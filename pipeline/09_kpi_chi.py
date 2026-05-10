"""
build_analysis_dataset.py
--------------------------
Joins 06_annotated_2673.csv with 05_CORPUS_FINAL_TESIS.xlsx to produce
a sentence-level dataset with year, period, and responsibility_direction.

Output columns:
    sentence_id (optional row number)
    article_id
    sentence
    year
    period
    responsibility_direction

Usage:
    python build_analysis_dataset.py

Edit the CONFIG section if your column names differ.
"""

import pandas as pd

# ── CONFIG ────────────────────────────────────────────────────────────────────
ANNOTATED_CSV   = "06_annotated_2673.csv"
METADATA_XLSX   = "05_CORPUS_FINAL_TESIS.xlsx"
OUTPUT_CSV      = "sentences_for_analysis.csv"

# Column name for date in your metadata file — change if different
DATE_COLUMN     = "date"

# Column name for article_id in metadata — change if different
ID_COLUMN       = "article_id"
# ─────────────────────────────────────────────────────────────────────────────

# ── LOAD ──────────────────────────────────────────────────────────────────────
print("Loading annotated sentences...")
ann = pd.read_csv(ANNOTATED_CSV)
ann.columns = ann.columns.str.strip()

print("Loading metadata...")
meta = pd.read_excel(METADATA_XLSX)
meta.columns = meta.columns.str.strip()

print(f"Annotated sentences: {len(ann)}")
print(f"Metadata articles:   {len(meta)}")
print(f"Metadata columns:    {meta.columns.tolist()}")

# ── EXTRACT YEAR ──────────────────────────────────────────────────────────────
if DATE_COLUMN not in meta.columns:
    raise ValueError(
        f"Column '{DATE_COLUMN}' not found in metadata. "
        f"Available columns: {meta.columns.tolist()}"
    )

meta["year"] = pd.to_datetime(meta[DATE_COLUMN], errors="coerce").dt.year
meta["year"] = meta["year"].astype("Int64")

# ── ASSIGN PERIOD ─────────────────────────────────────────────────────────────
def assign_period(year):
    if pd.isna(year):
        return "unknown"
    elif year <= 2018:
        return "pre-accountability (2015-2018)"
    elif year <= 2022:
        return "corporate accountability (2019-2022)"
    else:
        return "governance and institutionalisation (2023-2025)"

meta["period"] = meta["year"].apply(assign_period)

# ── MERGE ─────────────────────────────────────────────────────────────────────
# Keep only what we need from metadata
meta_slim = meta[[ID_COLUMN, "year", "period"]].drop_duplicates(subset=[ID_COLUMN])

merged = ann.merge(meta_slim, on=ID_COLUMN, how="left")

missing_year = merged["year"].isna().sum()
if missing_year > 0:
    print(f"WARNING: {missing_year} sentences could not be matched to a year.")

# ── BUILD OUTPUT ──────────────────────────────────────────────────────────────
merged.insert(0, "sentence_id", range(1, len(merged) + 1))

output_cols = [
    "sentence_id",
    "article_id",
    "sentence",
    "year",
    "period",
    "responsibility_direction",
]

# Add optional columns if you want them too
optional_cols = ["construction_type", "actor_category", "agent_suppressed", "confidence"]
for col in optional_cols:
    if col in merged.columns:
        output_cols.append(col)

result = merged[output_cols]

# ── CHI-SQUARE TEST: PERIOD × RESPONSIBILITY DIRECTION ───────────────────────
from scipy.stats import chi2_contingency

# keep only the two categories relevant to the hypothesis
chi_df = result[result["responsibility_direction"].isin(["structural", "individualizing"])].copy()

# build contingency table
contingency = pd.crosstab(
    chi_df["responsibility_direction"],
    chi_df["period"]
)

print("\nContingency table (responsibility_direction × period):")
print(contingency.to_string())

# run chi-square test
chi2, p, dof, expected = chi2_contingency(contingency)

print("\nChi-square test results:")
print(f"chi2 = {chi2:.4f}")
print(f"dof = {dof}")
print(f"p-value = {p:.6g}")

# optional: expected frequencies
expected_df = pd.DataFrame(
    expected,
    index=contingency.index,
    columns=contingency.columns
)

print("\nExpected frequencies:")
print(expected_df.round(2).to_string())

# ── SAVE ──────────────────────────────────────────────────────────────────────
result.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
print(f"\nSaved: {OUTPUT_CSV}")
print(f"Total sentences: {len(result)}")
print(f"\nYear distribution:")
print(result["year"].value_counts().sort_index().to_string())
print(f"\nPeriod distribution:")
print(result["period"].value_counts().to_string())
print(f"\nResponsibility direction distribution:")
print(result["responsibility_direction"].value_counts().to_string())