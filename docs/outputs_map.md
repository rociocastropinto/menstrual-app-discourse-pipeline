# Output Mapping: Scripts → Thesis Chapters

This file maps each pipeline output to the thesis section or figure it
supports.

## Corpus construction (Chapter 3)

| Script | Output | Thesis reference |
|---|---|---|
| `pipeline/00_scan_rtf.py` | Console count (3,980 RTF files) | Section 3.2, Table 3.1 |
| `pipeline/01_extract_metadata.py` | `corpus_metadata_final_v9.csv` | Section 3.4 |
| `pipeline/02_keyword_filter.py` | `corpus_final_procesado_v12.csv` | Section 3.4 |
| `pipeline/03_bart_classify.py` | `results_transformers_v12.csv` | Section 3.5, Table 3.2 |
| `pipeline/04_build_corpus.py` | `05_CORPUS_FINAL_TESIS.xlsx` (392 articles) | Section 3.5, Appendix F |

## Annotation (Chapter 3 / Appendix B, D)

| Script | Output | Thesis reference |
|---|---|---|
| `pipeline/05_annotate_sentences.py` | `06_annotated_2673.csv` (2,669 sentences) | Section 3.7 |
| `pipeline/06_annotate_iaa_subset.py` | `07_253_annotated.xlsx` | Section 3.7 |
| `pipeline/07_reclassify_other.py` | `07_253_annotated_v2.xlsx` | Section 3.7 |
| `iaa/01_sample_iaa.py` | `iaa_sample.xlsx` | Appendix C |
| `iaa/02_cohen_kappa.py` | `kappa_results.csv` | Table 3.6, Appendix D |

## Analysis and figures (Chapter 4)

| Script | Output | Thesis reference |
|---|---|---|
| `pipeline/08_chi_square_analysis.py` | `sentences_for_analysis.csv`, chi-square results | Section 4.2, Table 4.1 |
| `pipeline/09_make_figures.py` | `fig5_annual_distribution_responsibility.png` | Section 4.1, Figure 3 |
| `pipeline/09_make_figures.py` | `fig6_annual_trends_structural_vs_individualising.png` | Section 4.2, Figure 4 |
| `pipeline/09_make_figures.py` | `fig7_actor_distribution_by_period.png` | Section 4.2, Figure 5 |
| `pipeline/09_make_figures.py` | `fig8_responsibility_by_actor_full_corpus.png` | Section 4.3, Figure 6 |
| `pipeline/09_make_figures.py` | `fig9_heatmap_construction_actor.png` | Section 4.4, Figure 8 |
| `pipeline/09_make_figures.py` | `fig10_agent_backgrounding_by_period.png` | Section 4.4, Figure 9 |
| `pipeline/09_make_figures.py` | `fig11_actor_framing_clean.png` | Section 4.3, Figure 7 |

## Documentation

| File | Purpose |
|---|---|
| `prompts/annotation_prompt.txt` | Exact LLM prompt — Appendix B |
| `docs/codebook.md` | Full annotation scheme — Appendix G |
| `docs/keep_nokeep_criteria.md` | Sentence curation criteria — Appendix E |
| `data/README_data.md` | Data availability statement |
