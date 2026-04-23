# Appendix A.3 — Individual Section: Member 3

**Name:** [Member 3 Name]
**Banner ID:** [Banner ID 3]
**Project area:** AI Business Insights Assistant

## A.3.1 Self-Reflection

My role on the iWear project was to design and implement the AI Business Insights Assistant — the natural-language query layer that lets a non-technical store owner ask questions like "sales today" or "best selling products" and receive a structured answer. My code lives in `backend/app/routes/ai_assistant.py`, `backend/app/services/ai_assistant_service.py`, the AI reporting tables in `backend/app/models/ai_reporting.py`, the seed function `seed_ai_intents` in `backend/app/seed.py` and the new front-end page `frontend/src/pages/admin/AdminAIInsights.jsx`.

The most valuable lesson I learned was that *safety beats sophistication* when an AI feature has to ship as part of a small team's prototype. My first instinct was to wire the assistant to a transformer model and let it generate SQL on the fly. After reading the recent natural-language-to-SQL literature (Zhong et al., 2017; Devlin et al., 2019) and discussing the risks with my supervisor, I redesigned the assistant around a curated set of `ReportingIntent` rows backed by predefined SQL templates that only accept whitelisted parameters. This is the architecture that ships. It is much more boring than a transformer model, but it has two properties that the team really needed: it is auditable (every query is logged in `assistant_query_logs` with the matched intent) and it cannot be tricked into running unsafe SQL because user text is never concatenated into the SQL string.

The skills I developed most were schema design for an extensible NLP layer, SQLAlchemy `text()` execution with parameter substitution, and React state management for a chat-style interface. I also learned a lot about the difference between *demonstrating* an AI feature and *engineering* one. A lot of academic AI demos quietly assume a clean dataset and a static prompt; a system that has to live in a retail back office cannot make either assumption.

My main strength during the project was reading the literature carefully and translating its lessons into concrete code. My main challenge was that I had limited React experience at the start of the semester and I had to ramp up quickly to deliver `AdminAIInsights.jsx`. The teamwork around this was great — Member 4 helped me wire the API client and Member 2 reviewed my JSX patterns.

If I were to start again, I would seed more intents earlier in the project — by the final iteration I expanded the seeded set from four to ten (Daily Sales, Monthly Profit, Best Selling Products, Low Stock, Top Customers, Pending Orders, Sales by Category, Average Order Value, New Customers This Month and Slow Moving Stock), which I am pleased with, but doing this in week three rather than week nine would have given the demos a much richer feel from the start.

## A.3.2 Critical Appraisal

The AI module meets FR-14 and FR-15 in Table 3.1, and it satisfies the safety property in NFR-3 (the SQL layer rejects any non-`SELECT` statement and only accepts a whitelisted set of substitution parameters). The unit tests in `backend/tests/test_ai_assistant.py` cover the matcher's positive paths, the no-match path, the safe execution path and the response formatter — six tests in total, more than any other module in the project. I am proud of this coverage because it makes the matcher's behaviour falsifiable: a future contributor cannot accidentally weaken the algorithm without breaking a test.

The clearest weakness of my work is the matcher itself. It is a keyword-overlap algorithm with a length-based scoring tie-breaker. It works well for the curated phrases in the seed but it cannot handle paraphrases that share no surface tokens with the keywords ("how much did we sell yesterday" does not match "sales today" because there is no overlap). The literature on natural-language-to-SQL (Zhong et al., 2017) shows that even relatively small transformer models can dramatically improve coverage. The reason I did not ship one is exactly the safety/sophistication trade-off I described above — but I am honest that the current matcher is the floor of what a real system should ship, not the ceiling. Future work should retain the safe-query backend and replace the matcher with a fine-tuned encoder model.

A second weakness is that the assistant has no concept of follow-up turns. Every query is independent. Real conversational analytics — "how about last month?", "and by category?" — would require a session state that the current architecture does not have. Adding it would require an `assistant_session` table and a session id on the query log, and the React chat panel would need to hold a session id in state. This is a clean extension that I would tackle next.

A third honest concern is that the matcher's tie-breaker (longest matching keyword wins) is brittle. A more rigorous approach would use TF-IDF over a small corpus of historical queries, or — once we have more usage data — a learned ranker. The current algorithm is good enough for a demo but it will need to evolve quickly under real user load.

Overall, my contribution is small in lines of code but high-leverage. The intent matching layer is the part of iWear that most clearly demonstrates an AI capability, and the safety properties I engineered into it should outlive the keyword matcher itself.
