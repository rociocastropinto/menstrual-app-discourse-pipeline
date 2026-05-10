"""
06_annotate_2673.py
====================
Simplified annotation pipeline for 2673 manually curated sentences.

- No Stanza, no Step 1 relevance filter
- Runs Step 2 (responsibility analysis) directly on all sentences
- Saves a checkpoint every 50 sentences → safe to interrupt and resume
- If interrupted: just run again, it picks up where it left off

SETUP:
  1. pip install openai pandas tqdm openpyxl python-dotenv
  2. Create a .env file in the same folder with:
         GWDG_API_KEY=your-key-here
  3. Make sure sentences_keep_2673.xlsx is in the same folder
  4. Run: python 06_annotate_2673.py

RESUME: if interrupted, just run again. It reads the checkpoint
        and skips already-annotated sentences automatically.
"""

import json
import os
import re
import time

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

# ── CONFIGURATION ──────────────────────────────────────────────────────────────

INPUT_FILE      = "sentences_keep_2673.xlsx"
OUTPUT_FILE     = "06_annotated_2673.csv"
CHECKPOINT_FILE = "06_checkpoint.csv"       # partial results, updated every 50 rows
LOG_FILE        = "06_errors.log"

GWDG_BASE_URL   = "https://chat-ai.academiccloud.de/v1"
MODEL           = "llama-3.3-70b-instruct"
TEMPERATURE     = 0.1
TOP_P           = 0.1
API_DELAY       = 10.0                       # seconds between calls (increased for rate limit)
CHECKPOINT_EVERY = 50                       # save progress every N sentences

# ── API CLIENT ─────────────────────────────────────────────────────────────────

def get_client():
    load_dotenv()
    api_key = os.environ.get("GWDG_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GWDG_API_KEY not set.\n"
            "Add it to a .env file: GWDG_API_KEY=your-key-here"
        )
    return OpenAI(api_key=api_key, base_url=GWDG_BASE_URL)


def call_api(client, system, user, retries=6):
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
                max_tokens=400,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            is_rate_limit = "429" in str(e)
            if attempt < retries - 1:
                # Rate limit: wait much longer (60s, 120s, 180s...)
                # Other errors: shorter wait
                wait = 60 * (attempt + 1) if is_rate_limit else 15 * (attempt + 1)
                tqdm.write(f"\n  {'Rate limit' if is_rate_limit else 'API error'} "
                           f"(attempt {attempt+1}): waiting {wait}s...")
                time.sleep(wait)
            else:
                raise e


def parse_json(raw):
    clean = re.sub(r"```json|```", "", raw).strip()
    return json.loads(clean)


# ── PROMPT ─────────────────────────────────────────────────────────────────────

SYSTEM = """You are an expert annotator in computational linguistics and
responsibility framing. You analyze sentences from English news articles about
menstrual tracking apps and data privacy. Your framework integrates Fillmore's
frame semantics, Construction Grammar, and Van Dijk's discourse theory.
Respond ONLY with valid JSON — no explanation, no markdown."""

def build_prompt(sentence):
    return f"""Analyze the responsibility framing in this sentence from a news article
about menstrual tracking apps and data privacy.

Sentence: "{sentence}"

CONSTRUCTION TYPE — how is the agent linguistically realized?

  "active_transitive"  — Agent as subject acts on explicit object.
                         e.g. "Flo sold user data to Facebook."

  "passive"            — Patient as subject; agent backgrounded or deleted.
                         e.g. "User data were sold to advertisers."

  "nominalization"     — Verb appears as noun, suppressing agent and patient.
                         e.g. "The sale of user data raised concerns."

  "intransitive"       — No object; event presented without agent.
                         e.g. "User data leaked."

  "other"              — Does not fit the above (e.g. questions, definitions,
                         purely descriptive statements with no responsibility frame).

ACTOR CATEGORY — classify the grammatical subject or main responsible party:

  "corporate"            — App companies, platforms, tech firms.
                           e.g. Flo, Clue, Google, "the company", "the app"

  "regulatory"           — Governments, courts, regulators, legislators, police.
                           e.g. ICO, FTC, NPCC, "lawmakers", "the court"

  "user"                 — Individual users, women, consumers, patients.
                           e.g. "women", "users", "the consumer"

  "technological_system" — Algorithms, AI, data systems as autonomous agents.
                           e.g. "the algorithm", "the system", "AI"

  "expert_civil_society" — Researchers, journalists, NGOs, advocacy groups.
                           e.g. "researchers", "Privacy International", "the report"

  "suppressed"           — No subject present (passive without by-phrase,
                           nominalization, impersonal construction).

  "other"                — Does not fit the above.

RESPONSIBILITY DIRECTION:
  "structural"       — blame/obligation pointed toward corporations or institutions
  "individualizing"  — blame/obligation pointed toward users or individuals
  "diffuse"          — spread across multiple actors
  "neutral"          — no clear direction (descriptive, contextual)

AGENT SUPPRESSED: true if the agent/responsible party is absent or hidden
                  false if the agent is explicitly named

Respond with ONLY this JSON object:
{{
  "construction_type": "...",
  "grammatical_subject": "exact subject phrase or null if absent",
  "actor_category": "...",
  "agent_suppressed": true or false,
  "responsibility_direction": "...",
  "confidence": 0.0 to 1.0,
  "reasoning": "one sentence max"
}}"""


# ── CHECKPOINT HELPERS ─────────────────────────────────────────────────────────

def load_checkpoint():
    """Returns set of already-annotated sentence indices."""
    if not os.path.exists(CHECKPOINT_FILE):
        return pd.DataFrame(), set()
    df = pd.read_csv(CHECKPOINT_FILE, encoding="utf-8-sig")
    done = set(df["_input_index"].tolist()) if "_input_index" in df.columns else set()
    return df, done


def save_checkpoint(rows):
    df = pd.DataFrame(rows)
    df.to_csv(CHECKPOINT_FILE, index=False, encoding="utf-8-sig")


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("06_annotate_2673.py — Responsibility Annotation")
    print(f"Model : {MODEL} @ GWDG Chat AI")
    print("=" * 60)

    # Load input
    print(f"\nLoading {INPUT_FILE}...")
    try:
        df_input = pd.read_excel(INPUT_FILE)
    except FileNotFoundError:
        print(f"ERROR: {INPUT_FILE} not found.")
        return

    print(f"  Loaded {len(df_input)} sentences.")

    # Identify sentence column
    if "sentence" not in df_input.columns:
        print(f"ERROR: no 'sentence' column found. Columns: {df_input.columns.tolist()}")
        return

    # Load checkpoint (resume support)
    checkpoint_rows, done_indices = load_checkpoint()
    if done_indices:
        print(f"  Resuming from checkpoint: {len(done_indices)} already done.")

    client = get_client()

    # Annotate
    results = checkpoint_rows.to_dict("records") if not checkpoint_rows.empty else []
    errors  = []
    new_since_checkpoint = 0

    remaining = df_input[~df_input.index.isin(done_indices)]
    print(f"\n  Sentences to annotate: {len(remaining)}")
    print(f"  Estimated time: ~{len(remaining) * API_DELAY / 60:.0f}–{len(remaining) * 1.5 / 60:.0f} min\n")

    for idx, row in tqdm(remaining.iterrows(), total=len(remaining), desc="Annotating"):
        sentence = str(row.get("sentence", "")).strip()
        if not sentence:
            continue

        try:
            raw    = call_api(client, SYSTEM, build_prompt(sentence))
            result = parse_json(raw)
        except Exception as e:
            errors.append({"_input_index": idx, "sentence": sentence, "error": str(e)})
            tqdm.write(f"  ERROR row {idx}: {e}")
            continue

        results.append({
            "_input_index":             idx,
            "article_id":               row.get("article_id", ""),
            "sentence":                 sentence,
            "construction_type":        result.get("construction_type"),
            "grammatical_subject":      result.get("grammatical_subject"),
            "actor_category":           result.get("actor_category"),
            "agent_suppressed":         result.get("agent_suppressed"),
            "responsibility_direction": result.get("responsibility_direction"),
            "confidence":               result.get("confidence"),
            "reasoning":                result.get("reasoning"),
        })

        new_since_checkpoint += 1
        time.sleep(API_DELAY)

        # Save checkpoint every N sentences
        if new_since_checkpoint >= CHECKPOINT_EVERY:
            save_checkpoint(results)
            new_since_checkpoint = 0
            tqdm.write(f"  [checkpoint saved — {len(results)} total]")

    # Final save
    df_out = pd.DataFrame(results)

    # Drop internal index column from final output
    if "_input_index" in df_out.columns:
        df_out = df_out.drop(columns=["_input_index"])

    df_out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    if errors:
        pd.DataFrame(errors).to_csv(LOG_FILE, index=False)

    # Clean up checkpoint if complete
    if len(errors) == 0 and os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
        print("\n  Checkpoint file removed (run complete).")

    # Summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Annotated : {len(df_out)}")
    print(f"Errors    : {len(errors)}")

    if len(df_out) > 0:
        print("\n--- Construction types ---")
        print(df_out["construction_type"].value_counts().to_string())
        print("\n--- Actor categories ---")
        print(df_out["actor_category"].value_counts().to_string())
        print("\n--- Responsibility direction ---")
        print(df_out["responsibility_direction"].value_counts().to_string())
        sup = df_out["agent_suppressed"]
        print(f"\nAgent suppression rate: {sup.mean():.2%}")
        print(f"Mean confidence       : {df_out['confidence'].mean():.2f}")

    print(f"\nOutput saved: {OUTPUT_FILE}")
    if errors:
        print(f"Errors logged: {LOG_FILE}")
    print("\nNext step: run inter-annotator agreement on a 100-sentence sample.")


if __name__ == "__main__":
    main()