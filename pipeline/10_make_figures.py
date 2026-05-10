"""
10_make_figures_labeled.py
--------------------------
Creates cleaner, thesis-ready figures from sentences_for_analysis.csv,
with small percentage labels added where useful.

Input:
    sentences_for_analysis.csv

Required columns:
    year
    period
    responsibility_direction
    actor_category
    construction_type

Optional:
    sentence_id
    article_id
    agent_suppressed
    confidence

Outputs:
    fig5_annual_distribution_responsibility.png / .pdf
    fig6_annual_trends_structural_vs_individualising.png / .pdf
    fig7_actor_distribution_by_period.png / .pdf
    fig8_responsibility_by_actor_full_corpus.png / .pdf
    fig9_heatmap_construction_actor.png / .pdf
    fig10_agent_backgrounding_by_period.png / .pdf
    fig11_actor_framing_clean.png / .pdf

Usage:
    python 10_make_figures_labeled.py
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False


# ── CONFIG ────────────────────────────────────────────────────────────────────

INPUT_CSV = "sentences_for_analysis.csv"
OUTPUT_DIR = "figures_labeled"

STRUCTURAL = "structural"
INDIVIDUALISING = "individualizing"   # keep z spelling from your dataset
NEUTRAL = "neutral"
DIFFUSE = "diffuse"

PERIOD_ORDER = [
    "pre-accountability (2015-2018)",
    "corporate accountability (2019-2022)",
    "governance and institutionalisation (2023-2025)",
]

RESPONSIBILITY_ORDER = [STRUCTURAL, NEUTRAL, DIFFUSE, INDIVIDUALISING]

ACTOR_ORDER = [
    "corporate",
    "regulatory",
    "user",
    "expert_civil_society",
    "technological_system",
    "suppressed",
    "other",
]

ACTOR_ORDER_MAIN = [
    "corporate",
    "user",
    "regulatory",
    "expert_civil_society",
]

CONSTRUCTION_ORDER = [
    "active_transitive",
    "passive",
    "nominalization",
    "intransitive",
    "other",
]

COLOR_MAP_RESP = {
    STRUCTURAL: "#4C78A8",
    NEUTRAL: "#B8B8B8",
    DIFFUSE: "#F2A541",
    INDIVIDUALISING: "#D95F5F",
}

COLOR_MAP_ACTOR = {
    "corporate": "#4C78A8",
    "regulatory": "#72B7B2",
    "user": "#D95F5F",
    "expert_civil_society": "#54A24B",
    "technological_system": "#B279A2",
    "suppressed": "#FF9DA6",
    "other": "#9D755D",
}


# ── HELPERS ───────────────────────────────────────────────────────────────────

def ensure_output_dir(path: str | Path) -> Path:
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out


def save_current_figure(outdir: Path, stem: str) -> None:
    png_path = outdir / f"{stem}.png"
    pdf_path = outdir / f"{stem}.pdf"
    plt.tight_layout()
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.savefig(pdf_path, bbox_inches="tight")
    print(f"Saved: {png_path}")
    print(f"Saved: {pdf_path}")
    plt.close()


def validate_columns(df: pd.DataFrame, required: list[str]) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns: {missing}\n"
            f"Available columns: {df.columns.tolist()}"
        )


def ordered_value_counts(series: pd.Series, order: list[str]) -> pd.Series:
    counts = series.value_counts()
    return counts.reindex(order, fill_value=0)


def ordered_crosstab(
    index: pd.Series,
    columns: pd.Series,
    index_order: list[str],
    col_order: list[str],
) -> pd.DataFrame:
    tab = pd.crosstab(index, columns)
    return tab.reindex(index=index_order, columns=col_order, fill_value=0)


def prettify_actor_label(label: str) -> str:
    mapping = {
        "corporate": "Corporate",
        "regulatory": "Regulatory",
        "user": "User",
        "expert_civil_society": "Expert/Civil Society",
        "technological_system": "Technological System",
        "suppressed": "Suppressed",
        "other": "Other",
    }
    return mapping.get(label, label)


def prettify_construction_label(label: str) -> str:
    mapping = {
        "active_transitive": "Active transitive",
        "passive": "Passive",
        "nominalization": "Nominalisation",
        "intransitive": "Intransitive",
        "other": "Other",
    }
    return mapping.get(label, label)


def pretty_period(label: str) -> str:
    mapping = {
        "pre-accountability (2015-2018)": "Period 1\n(2015–2018)",
        "corporate accountability (2019-2022)": "Period 2\n(2019–2022)",
        "governance and institutionalisation (2023-2025)": "Period 3\n(2023–2025)",
    }
    return mapping.get(label, label)


def add_bar_labels(ax, bars, decimals: int = 0, fontsize: int = 9, min_height: float = 0.0) -> None:
    for bar in bars:
        height = bar.get_height()
        if pd.isna(height) or height <= min_height:
            continue
        label = f"{height:.{decimals}f}%"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 1,
            label,
            ha="center",
            va="bottom",
            fontsize=fontsize,
        )


# ── LOAD ──────────────────────────────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    if not os.path.exists(INPUT_CSV):
        raise FileNotFoundError(
            f"{INPUT_CSV} not found.\n"
            f"Make sure it is in the same folder as this script."
        )
    df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    return df


# ── FIGURE 5 ──────────────────────────────────────────────────────────────────
# Annual distribution of annotated sentences by responsibility direction (counts)

def make_fig5(df: pd.DataFrame, outdir: Path) -> None:
    validate_columns(df, ["year", "responsibility_direction"])

    years = sorted([int(y) for y in df["year"].dropna().unique()])
    table = pd.crosstab(df["year"], df["responsibility_direction"])
    table = table.reindex(index=years, columns=RESPONSIBILITY_ORDER, fill_value=0)

    plt.figure(figsize=(10, 6))
    bottom = pd.Series([0] * len(table), index=table.index)

    for label in RESPONSIBILITY_ORDER:
        plt.bar(
            table.index.astype(str),
            table[label],
            bottom=bottom,
            label=label.replace("_", " ").title(),
            color=COLOR_MAP_RESP[label],
        )
        bottom += table[label]

    plt.xlabel("Year")
    plt.ylabel("Number of annotated sentences")
    plt.title("Annual distribution of annotated sentences by responsibility direction")
    plt.legend(title="Responsibility direction", frameon=False)
    save_current_figure(outdir, "fig5_annual_distribution_responsibility")


# ── FIGURE 6 ──────────────────────────────────────────────────────────────────
# Annual trends in structural vs individualising framing (% by year)

def make_fig6(df: pd.DataFrame, outdir: Path) -> None:
    validate_columns(df, ["year", "responsibility_direction"])

    years = sorted([int(y) for y in df["year"].dropna().unique()])
    year_counts = pd.crosstab(df["year"], df["responsibility_direction"]).reindex(
        index=years, fill_value=0
    )
    year_pct = year_counts.div(year_counts.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(10, 6))

    x = year_pct.index
    y1 = year_pct.get(STRUCTURAL, pd.Series(0, index=year_pct.index))
    y2 = year_pct.get(INDIVIDUALISING, pd.Series(0, index=year_pct.index))

    ax.plot(
        x,
        y1,
        marker="o",
        linewidth=2,
        label="Structural",
        color=COLOR_MAP_RESP[STRUCTURAL],
    )
    ax.plot(
        x,
        y2,
        marker="o",
        linewidth=2,
        label="Individualising",
        color=COLOR_MAP_RESP[INDIVIDUALISING],
    )

    # Labels for structural
    for i, v in enumerate(y1):
        ax.text(x.iloc[i] if hasattr(x, "iloc") else list(x)[i], v + 2, f"{v:.0f}%", ha="center", fontsize=9)

    # Labels for individualising, only if meaningful
    for i, v in enumerate(y2):
        if v > 2:
            ax.text(x.iloc[i] if hasattr(x, "iloc") else list(x)[i], v + 2, f"{v:.0f}%", ha="center", fontsize=9)

    ax.set_xlabel("Year")
    ax.set_ylabel("Percentage of sentences")
    ax.set_title("Annual trends in structural and individualising framing")
    ax.set_xticks(years)
    ax.set_ylim(0, 100)
    ax.legend(frameon=False)

    save_current_figure(outdir, "fig6_annual_trends_structural_vs_individualising")


# ── FIGURE 7 ──────────────────────────────────────────────────────────────────
# Actor category distribution by period (% of sentences in period)

def make_fig7(df: pd.DataFrame, outdir: Path) -> None:
    validate_columns(df, ["period", "actor_category"])

    table = ordered_crosstab(df["period"], df["actor_category"], PERIOD_ORDER, ACTOR_ORDER)
    pct = table.div(table.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(11, 6))
    bottom = pd.Series([0.0] * len(pct), index=pct.index)

    xlabels = [pretty_period(p) for p in pct.index]

    for actor in ACTOR_ORDER:
        bars = ax.bar(
            xlabels,
            pct[actor],
            bottom=bottom,
            label=prettify_actor_label(actor),
            color=COLOR_MAP_ACTOR[actor],
        )

        # Small labels inside meaningful segments
        for i, val in enumerate(pct[actor]):
            if val > 5:
                ax.text(
                    i,
                    bottom.iloc[i] + val / 2,
                    f"{val:.0f}%",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white",
                )

        bottom += pct[actor]

    ax.set_xlabel("Period")
    ax.set_ylabel("% of sentences in period")
    ax.set_title("Actor category distribution by period")
    ax.set_ylim(0, 100)
    ax.legend(
        title="Actor category",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        frameon=False,
    )

    save_current_figure(outdir, "fig7_actor_distribution_by_period")


# ── FIGURE 8 ──────────────────────────────────────────────────────────────────
# Responsibility direction by actor category (full corpus)

def make_fig8(df: pd.DataFrame, outdir: Path) -> None:
    validate_columns(df, ["actor_category", "responsibility_direction"])

    table = ordered_crosstab(
        df["actor_category"],
        df["responsibility_direction"],
        ACTOR_ORDER,
        RESPONSIBILITY_ORDER,
    )
    pct = table.div(table.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(11, 6))
    bottom = pd.Series([0.0] * len(pct), index=pct.index)
    xlabels = [prettify_actor_label(a) for a in pct.index]

    for label in RESPONSIBILITY_ORDER:
        bars = ax.bar(
            xlabels,
            pct[label],
            bottom=bottom,
            label=label.replace("_", " ").title(),
            color=COLOR_MAP_RESP[label],
        )

        # Optional small labels only for larger segments
        for i, val in enumerate(pct[label]):
            if val > 8:
                ax.text(
                    i,
                    bottom.iloc[i] + val / 2,
                    f"{val:.0f}%",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white",
                )

        bottom += pct[label]

    ax.set_xlabel("Actor category")
    ax.set_ylabel("% within actor category")
    ax.set_title("Responsibility direction by actor category (full corpus)")
    ax.set_xticklabels(xlabels, rotation=30, ha="right")
    ax.set_ylim(0, 100)
    ax.legend(
        title="Responsibility direction",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        frameon=False,
    )

    save_current_figure(outdir, "fig8_responsibility_by_actor_full_corpus")


# ── FIGURE 9 ──────────────────────────────────────────────────────────────────
# Heatmap: construction type × actor category (% within construction type)

def make_fig9_heatmap(df: pd.DataFrame, outdir: Path) -> None:
    validate_columns(df, ["construction_type", "actor_category"])

    use_actors = ACTOR_ORDER_MAIN
    subset = df[df["actor_category"].isin(use_actors)].copy()

    table = ordered_crosstab(
        subset["construction_type"],
        subset["actor_category"],
        CONSTRUCTION_ORDER,
        use_actors,
    )
    pct = table.div(table.sum(axis=1), axis=0) * 100

    pct.index = [prettify_construction_label(x) for x in pct.index]
    pct.columns = [prettify_actor_label(x) for x in pct.columns]

    plt.figure(figsize=(8, 5.5))

    if HAS_SEABORN:
        sns.heatmap(
            pct,
            annot=True,
            fmt=".0f",
            cmap="Blues",
            cbar_kws={"label": "% within construction type"},
        )
    else:
        im = plt.imshow(pct.values, aspect="auto", cmap="Blues")
        plt.colorbar(im, label="% within construction type")
        plt.xticks(range(len(pct.columns)), pct.columns, rotation=30, ha="right")
        plt.yticks(range(len(pct.index)), pct.index)
        for i in range(pct.shape[0]):
            for j in range(pct.shape[1]):
                plt.text(j, i, f"{pct.iloc[i, j]:.0f}", ha="center", va="center")

    plt.title("Construction type × actor category")
    plt.xlabel("Actor category")
    plt.ylabel("Construction type")
    save_current_figure(outdir, "fig9_heatmap_construction_actor")


# ── FIGURE 10 ─────────────────────────────────────────────────────────────────
# Agent-backgrounding constructions (passive + nominalisation) by period

def make_fig10(df: pd.DataFrame, outdir: Path) -> None:
    validate_columns(df, ["period", "construction_type"])

    bg_types = ["passive", "nominalization"]
    period_totals = ordered_value_counts(df["period"], PERIOD_ORDER)
    bg_counts = (
        df[df["construction_type"].isin(bg_types)]["period"]
        .value_counts()
        .reindex(PERIOD_ORDER, fill_value=0)
    )
    bg_pct = (bg_counts / period_totals) * 100

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        [pretty_period(p) for p in bg_pct.index],
        bg_pct.values,
        color="#8E6C8A",
        width=0.5,
    )

    ax.set_xlabel("Period")
    ax.set_ylabel("% of sentences")
    ax.set_title("Agent-backgrounding constructions by period\n(passive + nominalisation)")
    ax.set_ylim(0, max(20, bg_pct.max() * 1.25))
    add_bar_labels(ax, bars, decimals=1, fontsize=10, min_height=0.0)

    save_current_figure(outdir, "fig10_agent_backgrounding_by_period")


# ── FIGURE 11 ─────────────────────────────────────────────────────────────────
# Clean grouped bar chart: structural vs individualising framing by actor

def make_fig11_actor_framing_clean(df: pd.DataFrame, outdir: Path) -> None:
    validate_columns(df, ["actor_category", "responsibility_direction"])

    subset = df[df["responsibility_direction"].isin([STRUCTURAL, INDIVIDUALISING])].copy()

    table = pd.crosstab(subset["actor_category"], subset["responsibility_direction"])
    table = table.reindex(
        index=ACTOR_ORDER_MAIN,
        columns=[STRUCTURAL, INDIVIDUALISING],
        fill_value=0,
    )
    pct = table.div(table.sum(axis=1), axis=0) * 100

    labels = [prettify_actor_label(x) for x in pct.index]
    x = list(range(len(labels)))
    width = 0.34

    fig, ax = plt.subplots(figsize=(9, 5))
    bars1 = ax.bar(
        [i - width / 2 for i in x],
        pct[STRUCTURAL],
        width,
        label="Structural",
        color=COLOR_MAP_RESP[STRUCTURAL],
    )
    bars2 = ax.bar(
        [i + width / 2 for i in x],
        pct[INDIVIDUALISING],
        width,
        label="Individualising",
        color=COLOR_MAP_RESP[INDIVIDUALISING],
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("% within actor category")
    ax.set_xlabel("Actor category")
    ax.set_title("Structural vs individualising framing by actor")
    ax.set_ylim(0, 105)
    ax.legend(title="Responsibility direction", frameon=False)

    add_bar_labels(ax, bars1, decimals=0, fontsize=9, min_height=0.0)
    add_bar_labels(ax, bars2, decimals=0, fontsize=9, min_height=2.0)

    save_current_figure(outdir, "fig11_actor_framing_clean")


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main() -> None:
    outdir = ensure_output_dir(OUTPUT_DIR)
    df = load_data()

    print(f"Loaded {len(df)} rows from {INPUT_CSV}")
    print(f"Saving figures to: {outdir.resolve()}")

    make_fig5(df, outdir)
    make_fig6(df, outdir)
    make_fig7(df, outdir)
    make_fig8(df, outdir)
    make_fig9_heatmap(df, outdir)
    make_fig10(df, outdir)
    make_fig11_actor_framing_clean(df, outdir)

    print("\nAll figures generated successfully.")


if __name__ == "__main__":
    main()