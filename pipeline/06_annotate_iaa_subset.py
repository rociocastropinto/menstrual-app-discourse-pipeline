"""
07_annotate_253.py
==================
Runs Step 2 responsibility analysis directly on sentences_keep_253.xlsx.
Skips Step 1 entirely — these sentences are already human-validated as relevant.

Uses GWDG Chat AI API with llama-3.3-70b-instruct.

REQUIREMENTS:
  pip install openai pandas tqdm openpyxl python-dotenv

.env file in same folder:
  GWDG_API_KEY=your-key-here

OUTPUT:
  07_253_annotated.xlsx  — full annotation ready for Chapter 4
  07_253_aggregated.csv  — year-by-year longitudinal summary
"""

import json
import os
import re
import time

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

load_dotenv()

# ── CONFIGURATION ──────────────────────────────────────────────────────────────

INPUT_FILE   = "sentences_keep_253.xlsx"
OUTPUT_FILE  = "07_253_annotated.xlsx"
OUTPUT_AGG   = "07_253_aggregated.csv"
CHECKPOINT   = "07_checkpoint.csv"

GWDG_BASE_URL = "https://chat-ai.academiccloud.de/v1"
MODEL         = "llama-3.3-70b-instruct"
TEMPERATURE   = 0.1
TOP_P         = 0.1
API_DELAY     = 5.0  # seconds between calls

# ── CLIENT ─────────────────────────────────────────────────────────────────────

def get_client():
    api_key = os.environ.get("GWDG_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GWDG_API_KEY not set. Add it to your .env file:\n"
            "GWDG_API_KEY=your-key-here"
        )
    return OpenAI(api_key=api_key, base_url=GWDG_BASE_URL)


def call_api(client, system, user, retries=3):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
                temperature=TEMPERATURE,
                top_p=TOP_P,
                max_tokens=500,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt < retries - 1:
                wait = 60 * (attempt + 1)
                print(f"\n  Error attempt {attempt+1}: {e}. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise e


def parse_json(raw):
    clean = re.sub(r"```json|```", "", raw).strip()
    result = json.loads(clean)
    if not isinstance(result, dict):
        raise ValueError(f"Expected dict, got {type(result)}")
    return result


# ── STEP 2 PROMPT ──────────────────────────────────────────────────────────────

SYSTEM = """You are an expert annotator in computational linguistics and
responsibility framing. You analyze sentences from English news articles about
menstrual tracking apps and data privacy. Respond ONLY with valid JSON."""

def prompt(sentence):
    return f"""Analyze this sentence from a news article about menstrual tracking apps.

Sentence: "{sentence}"

Classify these dimensions:

CONSTRUCTION TYPE:
  "active_transitive"   - Agent as subject acts on explicit object.
                          e.g. "Flo sold user data to Facebook."
  "passive"             - Patient as subject; agent backgrounded or deleted.
                          e.g. "User data were sold to advertisers."
  "nominalization"      - Verb appears as noun, suppressing agent and patient.
                          e.g. "The sale of user data raised concerns."
  "intransitive"        - No object; event presented as spontaneous.
                          e.g. "User data leaked."
  "other"               - Modal obligations, questions, reported speech, etc.

ACTOR CATEGORY (grammatical subject):
  "corporate"           - App companies, platforms, tech firms.
                          e.g. Flo, Clue, Google, "the company", "the app"
  "regulatory"          - Governments, courts, regulators, legislators.
                          e.g. ICO, FTC, "the regulator", "lawmakers"
  "user"                - Individual users, women, consumers, patients.
                          e.g. "women", "users", "she", "the consumer"
  "technological_system"- Algorithms, AI, data systems as autonomous agents.
                          e.g. "the algorithm", "the system", "the data"
  "suppressed"          - No subject present (passive without by-phrase,
                          nominalization, impersonal construction).
  "other"               - Does not fit the above.

RESPONSIBILITY DIRECTION:
  "individualizing"     - Blame pointed toward users / individuals.
  "structural"          - Blame pointed toward corporations / institutions.
  "diffuse"             - Spread across multiple actors or the system.
  "neutral"             - No clear responsibility direction.

Respond in JSON:
{{
  "construction_type": "...",
  "grammatical_subject": "..." or null,
  "actor_category": "...",
  "agent_foregrounded": true or false,
  "agent_suppressed": true or false,
  "responsibility_direction": "...",
  "confidence": 0.0 to 1.0,
  "reasoning": "one sentence"
}}"""


# ── LONGITUDINAL AGGREGATION ───────────────────────────────────────────────────

def aggregate_by_year(df):
    df["year"] = pd.to_datetime(df["date"], errors="coerce").dt.year
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)

    agg = df.groupby("year").agg(
        total_sentences        = ("sentence", "count"),
        agent_suppressed_n     = ("agent_suppressed",
                                  lambda x: (x == True).sum()),
        corporate_n            = ("actor_category",
                                  lambda x: (x == "corporate").sum()),
        regulatory_n           = ("actor_category",
                                  lambda x: (x == "regulatory").sum()),
        user_n                 = ("actor_category",
                                  lambda x: (x == "user").sum()),
        tech_system_n          = ("actor_category",
                                  lambda x: (x == "technological_system").sum()),
        suppressed_n           = ("actor_category",
                                  lambda x: (x == "suppressed").sum()),
        individualizing_n      = ("responsibility_direction",
                                  lambda x: (x == "individualizing").sum()),
        structural_n           = ("responsibility_direction",
                                  lambda x: (x == "structural").sum()),
        diffuse_n              = ("responsibility_direction",
                                  lambda x: (x == "diffuse").sum()),
        active_transitive_n    = ("construction_type",
                                  lambda x: (x == "active_transitive").sum()),
        passive_n              = ("construction_type",
                                  lambda x: (x == "passive").sum()),
        nominalization_n       = ("construction_type",
                                  lambda x: (x == "nominalization").sum()),
        intransitive_n         = ("construction_type",
                                  lambda x: (x == "intransitive").sum()),
        mean_confidence        = ("confidence", "mean"),
    ).reset_index()

    n = agg["total_sentences"]
    agg["agent_suppression_rate"] = (agg["agent_suppressed_n"] / n).round(3)
    agg["corporate_share"]        = (agg["corporate_n"] / n).round(3)
    agg["regulatory_share"]       = (agg["regulatory_n"] / n).round(3)
    agg["user_share"]             = (agg["user_n"] / n).round(3)
    agg["individualizing_rate"]   = (agg["individualizing_n"] / n).round(3)
    agg["structural_rate"]        = (agg["structural_n"] / n).round(3)
    agg["passive_rate"]           = (agg["passive_n"] / n).round(3)
    agg["nominalization_rate"]    = (agg["nominalization_n"] / n).round(3)

    return agg


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Script 07 — Step 2 Annotation on 253 Validated Sentences")
    print(f"Model: {MODEL} @ GWDG Chat AI")
    print("=" * 60)

    # Load input
    print(f"\nLoading {INPUT_FILE}...")
    df = pd.read_excel(INPUT_FILE)
    print(f"Loaded {len(df)} sentences from {df['article_id'].nunique()} articles.")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")

    client = get_client()

    # Resume from checkpoint if exists
    if os.path.exists(CHECKPOINT):
        done_df = pd.read_csv(CHECKPOINT)
        done_sentences = set(done_df["sentence"].tolist())
        remaining = df[~df["sentence"].isin(done_sentences)].copy()
        results = done_df.to_dict("records")
        print(f"\nResuming from checkpoint: {len(done_df)} done, {len(remaining)} remaining.")
    else:
        remaining = df.copy()
        results = []
        print(f"\nStarting fresh: {len(remaining)} sentences to annotate.")

    print(f"Estimated time: ~{len(remaining) * API_DELAY / 60:.1f} minutes\n")

    # Annotate
    for _, row in tqdm(remaining.iterrows(), total=len(remaining), desc="Annotating"):
        sentence = str(row["sentence"]).strip()
        if not sentence:
            continue

        try:
            raw    = call_api(client, SYSTEM, prompt(sentence))
            result = parse_json(raw)
        except Exception as e:
            result = {
                "construction_type":        "ERROR",
                "grammatical_subject":      None,
                "actor_category":           "ERROR",
                "agent_foregrounded":       None,
                "agent_suppressed":         None,
                "responsibility_direction": "ERROR",
                "confidence":               0.0,
                "reasoning":                str(e),
            }

        results.append({
            "article_id":               row["article_id"],
            "date":                     row["date"],
            "publication":              row.get("publication", ""),
            "headline":                 row.get("headline", ""),
            "sentence_id_in_article":   row.get("sentence_id_in_article", ""),
            "sentence":                 sentence,
            "construction_type":        result.get("construction_type"),
            "grammatical_subject":      result.get("grammatical_subject"),
            "actor_category":           result.get("actor_category"),
            "agent_foregrounded":       result.get("agent_foregrounded"),
            "agent_suppressed":         result.get("agent_suppressed"),
            "responsibility_direction": result.get("responsibility_direction"),
            "confidence":               result.get("confidence"),
            "reasoning":                result.get("reasoning"),
        })

        # Save checkpoint every 25 sentences
        if len(results) % 25 == 0:
            pd.DataFrame(results).to_csv(CHECKPOINT, index=False, encoding="utf-8-sig")

        time.sleep(API_DELAY)

    # Save final output
    df_results = pd.DataFrame(results)

    # Remove error rows for aggregation
    df_clean = df_results[df_results["construction_type"] != "ERROR"].copy()

    df_results.to_excel(OUTPUT_FILE, index=False)
    print(f"\nFull annotation saved: {OUTPUT_FILE}")

    # Summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total annotated:      {len(df_clean)}")
    errors = len(df_results) - len(df_clean)
    if errors:
        print(f"Errors:               {errors}")

    print("\n--- Construction type ---")
    print(df_clean["construction_type"].value_counts().to_string())

    print("\n--- Actor category ---")
    print(df_clean["actor_category"].value_counts().to_string())

    print("\n--- Responsibility direction ---")
    print(df_clean["responsibility_direction"].value_counts().to_string())

    supp = df_clean["agent_suppressed"].mean()
    print(f"\nAgent suppression rate: {supp:.2%}")

    # Longitudinal aggregation
    df_agg = aggregate_by_year(df_clean.copy())
    df_agg.to_csv(OUTPUT_AGG, index=False)
    print(f"\nLongitudinal aggregation saved: {OUTPUT_AGG}")
    print("\n--- Year-by-year ---")
    cols = ["year", "total_sentences", "agent_suppression_rate",
            "corporate_share", "user_share", "structural_rate", "individualizing_rate"]
    print(df_agg[cols].to_string(index=False))

    # Clean up checkpoint
    if os.path.exists(CHECKPOINT):
        os.remove(CHECKPOINT)
        print("\nCheckpoint file removed.")

    print(f"\nDone. Use {OUTPUT_FILE} and {OUTPUT_AGG} for Chapter 4.")


if __name__ == "__main__":
    main()