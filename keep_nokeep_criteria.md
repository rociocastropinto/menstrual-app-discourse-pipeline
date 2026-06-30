\# Manual Sentence-Level Curation Protocol



\## What this step does

After BART filtering produced 392 relevant articles, each article was segmented into sentence fragments. Each fragment was manually coded Keep/No Keep against the following inclusion criterion.



\## Inclusion criterion

A sentence was kept if it met ALL of the following:



1\. Contains an identifiable agent or patient involved in a 

&#x20;  data-related action (sharing, collecting, selling, regulating,

&#x20;  using, exposing)

2\. The action is attributable to a specific actor category 

&#x20;  (corporate, regulatory, user, technological system, 

&#x20;  expert/civil society)

3\. The sentence contributes a responsibility frame, it does not merely describe the app's features, market position, or download statistics without implicating an actor in a data governance context.

\## Exclusion criterion

A sentence was excluded if it was:

\- Purely descriptive (app launch dates, feature lists, prices)

\- A headline repetition within the article body

\- A metadata artifact from the Nexis Uni export

\- A sentence whose responsibility frame was fully captured by an adjacent sentence already retained


\## Saturation point

Manual review continued until theoretical saturation was reached 

- the point at which new fragments no longer provided novel actor-action relationships or framing patterns. 
- This produced 2,673 sentences from 103 of the 392 articles.



\## Output

sentences\_keep\_2673.xlsx — not publicly available due to 

Nexis Uni licensing. See data/README\_data.md.

