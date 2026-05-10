"""
calculate_kappa.py
------------------
Calculates Cohen's Kappa between your manual annotations and the LLM annotations
for all four dimensions, once you have filled in iaa_sample.xlsx.

Requires:
    - iaa_sample.xlsx  with Sheet 1 ("annotate_here") filled in columns E–H
    - sklearn, pandas, openpyxl

Usage:
    python calculate_kappa.py
"""

import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix
import warnings
warnings.filterwarnings("ignore")

# ── CONFIG ────────────────────────────────────────────────────────────────────
INPUT_XLSX = "iaa_sample.xlsx"
SHEET_HUMAN = "annotate_here"
SHEET_LLM   = "llm_labels_REVEAL_AFTER"
# ─────────────────────────────────────────────────────────────────────────────

DIMENSIONS = {
    "construction_type":      ("YOUR_construction_type",      "LLM_construction_type"),
    "actor_category":         ("YOUR_actor_category",          "LLM_actor_category"),
    "responsibility_direction":("YOUR_responsibility_direction","LLM_responsibility_direction"),
    "agent_suppressed":       ("YOUR_agent_suppressed",        "LLM_agent_suppressed"),
}

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
human_df = pd.read_excel(INPUT_XLSX, sheet_name=SHEET_HUMAN, header=1)  # row 2 is header (row 1 is instructions)
llm_df   = pd.read_excel(INPUT_XLSX, sheet_name=SHEET_LLM)

# Normalise
human_df.columns = human_df.columns.str.strip()
llm_df.columns   = llm_df.columns.str.strip()

# Merge on iaa_id
merged = human_df.merge(llm_df[["iaa_id"] + [c[1] for c in DIMENSIONS.values()]],
                        on="iaa_id", how="inner")

print(f"Sentences loaded: {len(merged)}")
print("=" * 60)

# ── KAPPA CALCULATION ─────────────────────────────────────────────────────────
results = {}

for dim, (human_col, llm_col) in DIMENSIONS.items():

    if human_col not in merged.columns:
        print(f"WARNING: '{human_col}' not found — skipping {dim}")
        continue
    if llm_col not in merged.columns:
        print(f"WARNING: '{llm_col}' not found — skipping {dim}")
        continue

    sub = merged[[human_col, llm_col]].dropna()
    sub[human_col] = sub[human_col].astype(str).str.strip().str.lower()
    sub[llm_col]   = sub[llm_col].astype(str).str.strip().str.lower()
    sub[human_col] = sub[human_col].str.replace("individualizing", "individualising")
    sub[llm_col]   = sub[llm_col].str.replace("individualizing", "individualising")



    # Remove rows where human left blank
    sub = sub[sub[human_col] != ""]
    sub = sub[sub[human_col] != "nan"]

    n = len(sub)
    if n < 2:
        print(f"{dim}: not enough annotations ({n})")
        continue

    try:
        kappa = cohen_kappa_score(sub[human_col], sub[llm_col])
    except Exception as e:
        print(f"{dim}: error — {e}")
        continue

    # Observed agreement
    agree = (sub[human_col] == sub[llm_col]).sum()
    p_o   = agree / n

    # Interpretation
    if kappa < 0.0:
        interp = "poor (below chance)"
    elif kappa < 0.20:
        interp = "slight"
    elif kappa < 0.40:
        interp = "fair"
    elif kappa < 0.60:
        interp = "moderate"
    elif kappa < 0.80:
        interp = "substantial ✓"
    else:
        interp = "near-perfect ✓✓"

    results[dim] = {
        "n": n,
        "observed_agreement": round(p_o, 3),
        "cohen_kappa": round(kappa, 3),
        "interpretation": interp,
    }

    print(f"\n── {dim} ──")
    print(f"   n annotated:          {n}")
    print(f"   Observed agreement:   {p_o:.1%}")
    print(f"   Cohen's Kappa (κ):    {kappa:.3f}")
    print(f"   Interpretation:       {interp}")

    # Confusion matrix
    labels = sorted(set(sub[human_col].tolist() + sub[llm_col].tolist()))
    cm = confusion_matrix(sub[human_col], sub[llm_col], labels=labels)
    cm_df = pd.DataFrame(cm, index=[f"H:{l}" for l in labels],
                              columns=[f"LLM:{l}" for l in labels])
    print(f"\n   Confusion matrix:")
    print(cm_df.to_string())

# ── SUMMARY TABLE ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SUMMARY TABLE (paste into thesis Table 3.4)")
print("=" * 60)
print(f"{'Dimension':<30} {'n':>5} {'P_o':>6} {'κ':>7}  Interpretation")
print("-" * 65)
for dim, r in results.items():
    print(f"{dim:<30} {r['n']:>5} {r['observed_agreement']:>6.3f} {r['cohen_kappa']:>7.3f}  {r['interpretation']}")

# ── EXPORT TO CSV ─────────────────────────────────────────────────────────────
if results:
    out_df = pd.DataFrame(results).T.reset_index()
    out_df.columns = ["dimension", "n", "observed_agreement", "cohen_kappa", "interpretation"]
    out_df.to_csv("kappa_results.csv", index=False)
    print("\nSaved: kappa_results.csv")