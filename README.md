| Script | Description |

|--------|-------------|

| `00\_scan\_rtf.py` | Diagnostic scan — confirms RTF file count |

| `01\_extract\_metadata.py` | Extracts metadata, deduplicates, applies 200-word filter |

| `02\_keyword\_filter.py` | Keyword pre-filter and echo chamber detection |

| `03\_bart\_classify.py` | BART zero-shot classification (τ=0.45) |

| `04\_build\_corpus.py` | Final domain validation → 392-article corpus |

| `05\_annotate\_sentences.py` | LLM annotation of 2,673 sentences (canonical) |

| `06\_annotate\_iaa\_subset.py` | LLM annotation of 253-sentence IAA subset |

| `07\_reclassify\_other.py` | Reclassifies actor\_category=other with updated prompt |

| `08\_chi\_square\_analysis.py` | Period assignment + chi-square test |

| `09\_make\_figures.py` | Generates all thesis figures |

