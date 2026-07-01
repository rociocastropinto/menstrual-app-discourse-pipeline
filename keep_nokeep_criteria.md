# Manual Sentence-Level Curation Protocol

Corresponds to thesis Section 3.7 and Appendix E.

## What this step does

After BART filtering produced 392 relevant articles, each article was 
segmented into sentence fragments. Curation proceeded in two stages: 
article-level screening followed by sentence-level Keep/No Keep coding.

## Stage 1: Article-level inclusion

An article was retained for sentence-level review if it was centrally 
concerned with menstrual or period-tracking applications AND if data 
collection, privacy, sharing, selling, risk, or responsibility were 
central to the article narrative.

Articles were especially likely to be retained if they:
- Discussed several actors in menstrual-data governance (app companies, 
  users, advertisers, insurers, regulators, founders, or broader 
  technological and commercial systems)
- Clearly described reproductive or bodily data as commodified or at 
  risk of misuse

## Stage 2: Sentence-level Keep/No Keep

### Inclusion criterion (KEEP)

A sentence was kept if it met ALL of the following:

1. Contains an identifiable agent or patient involved in a data-related 
   action (sharing, collecting, selling, regulating, using, exposing)
2. The action is attributable to a specific actor category (corporate, 
   regulatory, user, technological system, expert/civil society)
3. The sentence contributes a responsibility frame, it does not merely 
   describe the app's features, market position, or download statistics 
   without implicating an actor in a data governance context

### Exclusion criterion (DO NOT KEEP)

A sentence was excluded if it was:
- Purely descriptive (app launch dates, feature lists, prices)
- A headline repetition within the article body
- A metadata artifact from the Nexis Uni export
- A sentence whose responsibility frame was fully captured by an 
  adjacent sentence already retained

The operational distinction:
- **KEEP** = directly constructs responsibility and privacy framing
- **DO NOT KEEP** = contextual / illustrative only

## Worked examples

The following examples are drawn from a single article to illustrate 
how the criterion was applied in practice:

| ID | Sentence (shortened) | Decision | Reason |
|---|---|---|---|
| 1 | "Half the world's population spend an average of..." | DO NOT KEEP | contextual / illustrative only |
| 2 | "That's why millions have started to diarise..." | KEEP | directly constructs responsibility and privacy framing |
| 18 | "She uses the app Period Log but didn't read its privacy..." | KEEP | directly constructs responsibility and privacy framing |
| 37 | "Clue is a period tracking app that wants to do things..." | DO NOT KEEP | contextual / illustrative only |
| 41 | "If people give data, then they should also see..." | KEEP | directly constructs responsibility and privacy framing |
| 50 | "While Tin takes privacy concerns seriously, she also..." | DO NOT KEEP | contextual / illustrative only |

## Saturation point

Manual review continued until theoretical saturation was reached — the 
point at which new fragments no longer provided novel actor-action 
relationships or framing patterns (Saunders et al., 2018). This 
approach is consistent with journalistic convergence patterns 
documented in high-attention news cycles (Boczkowski, 2010), where 
multiple outlets covering the same regulatory event produce overlapping 
rather than independently novel content.

This produced **2,673 sentences from 103 of the 392 articles**.

## Output

`sentences_keep_2673.xlsx` — not publicly available due to Nexis Uni 
licensing. See `data/README_data.md`.

## References

- Saunders, B. et al. (2018). Saturation in qualitative research. 
  *Quality & Quantity*, 52(4), 1893–1907.
- Boczkowski, P. J. (2010). *News at Work: Imitation in an Age of 
  Information Abundance*. University of Chicago Press.
