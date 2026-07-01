# Data Availability

## What is not shareable

Full raw article texts cannot be redistributed because they were sourced
from Nexis Uni (LexisNexis Academic) under institutional subscription, which
prohibits public redistribution of licensed content. This applies to:

- Raw RTF exports (3,980 files)
- `corpus_metadata_final_v9.csv` (contains article body text)
- `05_CORPUS_FINAL_TESIS.xlsx` (392 articles, full text)
- `sentences_keep_2673.xlsx` (curated sentences, full text)
- `06_annotated_2673.csv` (annotated sentences, includes sentence text)

GWDG API keys (`.env`) are also excluded; see `.env.example` for the
required format.

## What is included instead

- All processing scripts (`pipeline/`, `iaa/`)
- The exact LLM annotation prompt (`prompts/annotation_prompt.txt`)
- The full annotation codebook (`docs/codebook.md`)
- The sentence curation criteria (`docs/keep_nokeep_criteria.md`)
- Inter-annotator agreement results and confusion matrices (thesis
  Appendix D; raw kappa script output reproducible via `iaa/02_cohen_kappa.py`
  once a labeled sample is available)
- Output-to-chapter mapping (`docs/outputs_map.md`)

## How to reproduce the full pipeline

1. Obtain a Nexis Uni institutional subscription
2. Run the Boolean search string documented in thesis Section 3.2
3. Download RTF exports and place them in a local folder
4. Obtain a GWDG Chat AI API key (kisski.gwdg.de)
5. Copy `.env.example` to `.env` and add your key
6. Run scripts in `pipeline/` in numerical order (00 through 09)
7. Run `iaa/01_sample_iaa.py` then `iaa/02_cohen_kappa.py` for the IAA
   subset, using a second human annotator following `docs/codebook.md`

## Corpus statistics (for reference, no underlying text included)

- Raw RTF files: 3,980
- After deduplication and 200-word filter: 1,497
- After BART filtering (τ=0.45): 392 articles
- After manual sentence curation: 2,673 sentences (from 103 of 392 articles)
- Successfully annotated: 2,669 sentences
