# Menstrual App Discourse Pipeline

This repository accompanies the MA thesis **"Beyond Responsibilisation: Structural Accountability and Governance Diffusion in Menstrual-App News Coverage: A Longitudinal Computational Discourse Analysis (2015–2025)"**.

The thesis studies how responsibility for menstrual-data privacy is framed in English-language news coverage of menstrual-tracking apps between 2015 and 2025. It combines article-level corpus filtering, sentence-level manual curation, large language model annotation, and quantitative/discourse-analytic interpretation in order to examine how responsibility is distributed across actors, sentence structures, and time periods.

## What this repository contains

This repository provides the code, prompt materials, and reproducibility documentation for the computational pipeline used in the thesis. Because the raw news texts were collected through Nexis Uni and are subject to licensing restrictions, the repository may not include all original source texts. Where full-text redistribution is restricted, the repository instead documents the workflow, prompt design, annotation logic, and derived outputs used in the analysis.

## Pipeline overview

| Script | Description |
|--------|-------------|
| 00_scan_rtf.py | Diagnostic scan — confirms RTF file count |
| 01_extract_metadata.py | Extracts metadata, deduplicates, applies 200-word filter |
| 02_keyword_filter.py | Keyword pre-filter and echo chamber detection |
| 03_bart_classify.py | BART zero-shot classification (τ = 0.45) |
| 04_build_corpus.py | Final domain validation -> 392-article corpus |
| 05_annotate_sentences.py | LLM annotation of 2,673 sentences (canonical working annotation file) |
| 06_annotate_iaa_subset.py | LLM annotation of IAA subset used for comparison workflows |
| 07_reclassify_other.py | Reclassifies actor_category = other with updated prompt |
| 08_chi_square_analysis.py | Period assignment + chi-square test |
| 09_make_figures.py | Generates thesis figures |

## Corpus logic

The pipeline operates at two levels:

1. **Article level**: articles were collected, deduplicated, keyword-filtered, and then classified for domain relevance using BART zero-shot filtering.
2. **Sentence level**: articles in the final filtered corpus were segmented into sentence fragments. These fragments were then manually reviewed through a **Keep/No Keep** procedure in order to isolate responsibility-bearing discourse before LLM annotation.

A sentence was retained when it directly contributed to responsibility or privacy framing; contextual or illustrative-only material was excluded. The final analytical corpus reported in the thesis consists of **2,669 annotated sentences drawn from 103 articles**.

## Outputs and relation to the thesis

The repository supports the figures, tables, and methodological claims reported in the thesis, especially in:

- **Chapter 3**: pipeline design, annotation procedure, inter-annotator agreement
- **Chapter 4**: corpus statistics, period comparisons, chi-square analysis, figures
- **Appendix**: prompt design, technical environment, agreement matrices

If the repository includes generated figures, they correspond to the visualizations reproduced in the analysis chapter.

## Important note on counts

Some script outputs reflect intermediate working stages rather than the final counts reported in the submitted thesis. For example, canonical annotation files may retain pre-cleaning or pre-error-removal counts (e.g. 2,673), while the final reported analytical corpus may reflect the cleaned set used in interpretation (e.g. 2,669). The thesis should be treated as the authoritative source for final reported numbers.

## Data availability

Raw article texts obtained through Nexis Uni may not be redistributed through this repository because of licensing restrictions. Where this applies, the repository provides:

- metadata and workflow documentation
- prompt materials
- annotation schema
- code for filtering, annotation, and analysis
- derived results used in the thesis

## Reproducibility

To reproduce the pipeline as closely as possible:

1. Prepare the input article files in the expected format.
2. Run scripts in numerical order from `00_...` to `09_...`.
3. Apply the manual Keep/No Keep sentence curation step before sentence annotation.
4. Use the annotation prompt and inference settings documented in the thesis appendix.

## Environment

See `requirements.txt` for the software environment used in the project. The thesis appendix also documents the package versions used for the submitted analysis.

## Thesis reference

Castro Pinto, Rocio Alejandra. *Beyond Responsibilisation: Structural Accountability and Governance Diffusion in Menstrual-App News Coverage: A Longitudinal Computational Discourse Analysis (2015–2025).* MA Thesis, University of Göttingen, 2026.
