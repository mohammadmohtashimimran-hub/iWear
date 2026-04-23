# Appendix B — Project Process Document

This appendix summarises the process artefacts of the project: the weekly development plan, the supervisor meeting notes and the version control workflow. It is intended to satisfy the *Project Process Document* requirement in `Final Report Guidelines.docx` ("This needs to be submitted as an Appendix of the final report.").

## B.1 Development Cadence

The project followed a nine-week iterative development plan loosely aligned with the *Weekly Development Plan (Client-Report Ready Version).docx* shipped in `Documentation/`. Each week followed roughly the same shape:

- Monday — supervisor sync, scope confirmation for the week.
- Tuesday/Wednesday — implementation work in subdomain branches.
- Thursday — integration and code review across the four subdomains.
- Friday — short demo and retrospective.

Key milestones:

- **Week 1** — business scope, draft architecture, ER diagrams committed under `docs/week1/`.
- **Week 2** — Dockerised PostgreSQL, Flask scaffold, Alembic migrations, enterprise schema rolled out (commit `37e8810`).
- **Weeks 3–4** — RBAC, JWT, finance posting, AI intent seeds.
- **Weeks 5–6** — Catalog admin, addon system, customer cart and checkout.
- **Week 7** — Initial UI styling, AI assistant route + service.
- **Week 8** — UI iteration round 1, manual scenario testing, draft report.
- **Week 9** *(this iteration)* — Backend hardening (filters, AI intents endpoint, logging, demo seeders), v2 design upgrade, AI Insights page, full final report assembly.

## B.2 Version Control Workflow

The team uses Git with a single shared remote and short-lived feature branches that fan into a main integration branch. The work in this iteration is on the branch `feature/eyewear-project-completion`. The branch naming convention is `feature/<scope>` for feature branches and `fix/<scope>` for bug-fix branches. Conventional commit messages (`feat:`, `fix:`, `docs:`, `test:`) are used.

The full commit log can be inspected with:

```bash
git log --oneline --decorate --graph
```

## B.3 Supervisor Meeting Notes (summary)

Substantive feedback from the supervisor over the project:

- **Architecture must be in the report.** Add a system architecture section with a draw.io/Visio-style diagram and a written explanation. *(Addressed in Chapter 4 and `docs/architecture/system_architecture.drawio`.)*
- **Algorithms must include flowcharts or pseudocode followed by an explanation.** *(Addressed in Chapter 5: order checkout flowchart, voucher posting pseudocode, AI intent flowchart, RBAC sequence diagram.)*
- **Code snippets must be brief and explained.** *(Addressed in Chapter 5 — every code snippet is followed by a paragraph stating what it does and why it matters.)*
- **Chapter 5 must contain results and discussion** with tables and explanatory paragraphs. *(Addressed in Chapter 7 — Tables 7.1, performance figures, scenarios.)*
- **Chapter 6 must contain conclusion and at least two paragraphs of future work.** *(Addressed in Chapter 8 — Section 8.2.1 covers ML-based AI and recommendation; Section 8.2.2 covers payments, notifications, multi-tenancy and observability.)*
- **Each student must include an individual section with name, Banner ID, self-reflection and critical appraisal.** *(Addressed in Appendix A.1–A.4.)*

## B.4 Tools and Conventions

| Tool / Convention | Purpose |
|---|---|
| Git + GitHub | Source control |
| Conventional Commits | Commit message style |
| pytest + pytest-flask | Backend test runner |
| Vite + ESLint | Frontend dev/build |
| Alembic | Database migrations |
| Mermaid | Flowcharts inside markdown |
| draw.io (XML) | Architecture diagram source |
| python-docx | Markdown → Word conversion (`Documentation/md_to_docx.py`) |

## B.5 Risk Log

| Risk | Mitigation | Outcome |
|---|---|---|
| Schema churn breaking earlier tests | Alembic migrations + explicit downgrades | No regressions in this iteration |
| AI assistant unsafe SQL | `SELECT`-only guard, whitelisted parameter substitution | Verified by inspection and unit tests |
| Cross-team merge conflicts | Subdomain blueprints, single shared `index.css` per design system | One conflict in this iteration, resolved cleanly |
| Front-end design quality | Layered v2 design system over existing classes | Storefront and admin both visibly improved |
| Final report scope creep | Word budget per chapter, structured outline | Report lands in the configured ~11,500-word target |

## B.6 Submission Checklist

- [ ] Real student names and Banner IDs filled into Appendix A and the front matter.
- [ ] Screenshots of the running storefront and AI Insights page inserted into Chapter 7.
- [ ] Word count verified to be ≈11,500.
- [ ] `iWear_Final_Report.docx` regenerated via `assemble_report.py` after every edit.
- [ ] Turnitin draft submission to check originality (<10%).
