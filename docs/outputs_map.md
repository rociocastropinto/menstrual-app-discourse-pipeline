\# Output Mapping: Scripts → Thesis Chapters



This file maps each pipeline output to the thesis section or figure it

supports.



\## Corpus construction (Chapter 3)



| Script | Output | Thesis reference |

|---|---|---|

| `pipeline/00\_scan\_rtf.py` | Console count (3,980 RTF files) | Section 3.2, Table 3.1 |

| `pipeline/01\_extract\_metadata.py` | `corpus\_metadata\_final\_v9.csv` | Section 3.4 |

| `pipeline/02\_keyword\_filter.py` | `corpus\_final\_procesado\_v12.csv` | Section 3.4 |

| `pipeline/03\_bart\_classify.py` | `results\_transformers\_v12.csv` | Section 3.5, Table 3.2 |

| `pipeline/04\_build\_corpus.py` | `05\_CORPUS\_FINAL\_TESIS.xlsx` (392 articles) | Section 3.5, Appendix F |



\## Annotation (Chapter 3 / Appendix B, D)



| Script | Output | Thesis reference |

|---|---|---|

| `pipeline/05\_annotate\_sentences.py` | `06\_annotated\_2673.csv` (2,669 sentences) | Section 3.7 |

| `pipeline/06\_annotate\_iaa\_subset.py` | `07\_253\_annotated.xlsx` | Section 3.7 |

| `pipeline/07\_reclassify\_other.py` | `07\_253\_annotated\_v2.xlsx` | Section 3.7 |

| `iaa/01\_sample\_iaa.py` | `iaa\_sample.xlsx` | Appendix C |

| `iaa/02\_cohen\_kappa.py` | `kappa\_results.csv` | Table 3.6, Appendix D |



\## Analysis and figures (Chapter 4)



| Script | Output | Thesis reference |

|---|---|---|

| `pipeline/08\_chi\_square\_analysis.py` | `sentences\_for\_analysis.csv`, chi-square results | Section 4.2, Table 4.1 |

| `pipeline/09\_make\_figures.py` | `fig5\_annual\_distribution\_responsibility.png` | Section 4.1, Figure 3 |

| `pipeline/09\_make\_figures.py` | `fig6\_annual\_trends\_structural\_vs\_individualising.png` | Section 4.2, Figure 4 |

| `pipeline/09\_make\_figures.py` | `fig7\_actor\_distribution\_by\_period.png` | Section 4.2, Figure 5 |

| `pipeline/09\_make\_figures.py` | `fig8\_responsibility\_by\_actor\_full\_corpus.png` | Section 4.3, Figure 6 |

| `pipeline/09\_make\_figures.py` | `fig9\_heatmap\_construction\_actor.png` | Section 4.4, Figure 8 |

| `pipeline/09\_make\_figures.py` | `fig10\_agent\_backgrounding\_by\_period.png` | Section 4.4, Figure 9 |

| `pipeline/09\_make\_figures.py` | `fig11\_actor\_framing\_clean.png` | Section 4.3, Figure 7 |



\## Documentation



| File | Purpose |

|---|---|

| `prompts/annotation\_prompt.txt` | Exact LLM prompt — Appendix B |

| `docs/codebook.md` | Full annotation scheme — Appendix G |

| `docs/keep\_nokeep\_criteria.md` | Sentence curation criteria — Appendix E |

| `data/README\_data.md` | Data availability statement |

