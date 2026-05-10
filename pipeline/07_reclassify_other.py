"""
07b_reclassify_other.py
Reruns Step 2 annotation only on sentences coded as actor_category = 'other'
in 07_253_annotated.xlsx, using the updated prompt with expert_civil_society.
Merges results back into the full annotated file.
"""

import json, os, re, time
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

load_dotenv()

INPUT_FILE  = "07_253_annotated.xlsx"
OUTPUT_FILE = "07_253_annotated_v2.xlsx"

GWDG_BASE_URL = "https://chat-ai.academiccloud.de/v1"
MODEL         = "llama-3.3-70b-instruct"
API_DELAY     = 5.0

def get_client():
    return OpenAI(
        api_key=os.environ.get("GWDG_API_KEY"),
        base_url=GWDG_BASE_URL
    )

def call_api(client, system, user, retries=3):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
                temperature=0.1,
                top_p=0.1,
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

SYSTEM = """You are an expert annotator in computational linguistics and
responsibility framing. You analyze sentences from English news articles about
menstrual tracking apps and data privacy. Respond ONLY with valid JSON."""

def prompt(sentence):
    return f"""Analyze this sentence from a news article about menstrual tracking apps.

Sentence: "{sentence}"

Classify these dimensions:

CONSTRUCTION TYPE:
  "active_transitive"   - Agent as subject acts on explicit object.
  "passive"             - Patient as subject; agent backgrounded or deleted.
  "nominalization"      - Verb appears as noun, suppressing agent and patient.
  "intransitive"        - No object; event presented as spontaneous.
  "other"               - Modal obligations, questions, reported speech, etc.

ACTOR CATEGORY (grammatical subject):
  "corporate"              - App companies, platforms, tech firms.
                             e.g. Flo, Clue, Google, "the company", "the app"
  "regulatory"             - Governments, courts, regulators, legislators.
                             e.g. ICO, FTC, "the regulator", "lawmakers"
  "user"                   - Individual users, women, consumers, patients.
                             e.g. "women", "users", "she", "the consumer"
  "technological_system"   - Algorithms, AI, data systems as autonomous agents.
                             e.g. "the algorithm", "the system", "the data"
  "expert_civil_society"   - Sources introduced by the journalist with a
                             professional credential, institutional affiliation,
                             or advocacy role. The expert status is assigned
                             by the article text, not assumed independently.
                             e.g. a source introduced as "cybersecurity expert",
                             "lead researcher", "privacy advocate", "founder of
                             [organization]", "campaigns director of [NGO]".
                             Also includes named advocacy groups, NGOs, and
                             media outlets cited as analytical sources.
  "suppressed"             - No grammatical subject present. Covers passive
                             without by-phrase, nominalization with no named
                             agent, impersonal constructions, abstract or
                             inanimate subjects where no human or institutional
                             actor is implied.
                             e.g. "the risk", "the problem", "concerns",
                             "that information", null subject.
  "other"                  - Genuine edge cases only. Use sparingly.

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

def main():
    print("Loading annotated file...")
    df = pd.read_excel(INPUT_FILE)

    # One row is a scraping artifact — remove it
    df = df[~df["sentence"].str.contains("Navigate Left", na=False)]

    # Separate other from clean
    mask_other = df["actor_category"] == "other"
    df_other   = df[mask_other].copy()
    df_clean   = df[~mask_other].copy()

    print(f"Sentences to reclassify: {len(df_other)}")
    print(f"Sentences to keep as-is: {len(df_clean)}")

    client = get_client()
    new_rows = []

    for _, row in tqdm(df_other.iterrows(), total=len(df_other), desc="Reclassifying"):
        sentence = str(row["sentence"]).strip()
        try:
            raw    = call_api(client, SYSTEM, prompt(sentence))
            result = parse_json(raw)
        except Exception as e:
            result = {
                "construction_type":        row["construction_type"],
                "grammatical_subject":      row["grammatical_subject"],
                "actor_category":           "other",
                "agent_foregrounded":       row["agent_foregrounded"],
                "agent_suppressed":         row["agent_suppressed"],
                "responsibility_direction": row["responsibility_direction"],
                "confidence":               0.0,
                "reasoning":                f"ERROR: {e}",
            }

        new_rows.append({
            "article_id":               row["article_id"],
            "date":                     row["date"],
            "publication":              row["publication"],
            "headline":                 row["headline"],
            "sentence_id_in_article":   row["sentence_id_in_article"],
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
        time.sleep(API_DELAY)

    # Merge and save
    df_reclassified = pd.DataFrame(new_rows)
    df_final = pd.concat([df_clean, df_reclassified], ignore_index=True)
    df_final = df_final.sort_values(["article_id", "sentence_id_in_article"])
    df_final.to_excel(OUTPUT_FILE, index=False)

    print(f"\nSaved: {OUTPUT_FILE}")
    print("\n--- Updated actor category distribution ---")
    print(df_final["actor_category"].value_counts().to_string())
    print("\n--- Updated construction type distribution ---")
    print(df_final["construction_type"].value_counts().to_string())

if __name__ == "__main__":
    main()