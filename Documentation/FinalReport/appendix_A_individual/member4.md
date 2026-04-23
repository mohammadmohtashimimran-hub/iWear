# Appendix A.4 — Individual Section: Member 4

**Name:** [Member 4 Name]
**Banner ID:** [Banner ID 4]
**Project area:** System Integration, Security & Architecture

## A.4.1 Self-Reflection

My role on the iWear project was to own the cross-cutting concerns: authentication and authorisation, the role-permission matrix, the finance module's double-entry posting, the system architecture diagram, the Docker deployment story and the integration glue that lets the four subdomains coexist in a single Flask application. Concretely, I am the author of `backend/app/auth/decorators.py`, the JWT setup in `backend/app/__init__.py`, `backend/app/services/finance_service.py`, `docker-compose.yml`, the multi-stage `Dockerfile`, the architecture artefacts under `docs/architecture/`, the Mermaid flowcharts and most of the seeders for roles, permissions and the chart of accounts.

The most valuable lesson I learned was that *every cross-cutting concern wants to be a single line of code at the call site*. The first version of my permission check was an inline `if user.has_permission(...)` block in each endpoint. It was correct, but it polluted every handler and was extremely easy to forget. After I refactored the check into the `require_permission(code)` decorator, the handlers got shorter, the security boundary became visible at a glance and the code reviews on later pull requests sped up significantly. The same principle applied to the JWT user lookup, which I moved into a `user_lookup_loader` so that handlers can simply call `get_current_user()` instead of decoding the token themselves. These are tiny refactors but they had a disproportionate effect on the overall maintainability of the system.

My main strength on the project was systems thinking — I enjoyed making sure that the four subdomains shared a consistent authentication, logging and configuration story rather than each inventing their own. My main challenge was scope discipline. Cross-cutting work is the kind of thing that always wants to expand: I had to talk myself out of building a full audit dashboard, a metrics exporter and an OAuth flow because none of them were on the critical path for the prototype. I now have a much sharper sense of when to say "not in this iteration".

The skills I developed most were Flask blueprint composition, decorator-based authorisation patterns, double-entry bookkeeping in code, Alembic migration squashing and Docker multi-stage builds. The literature I read for Chapter 2 helped me here: the SME literature on integration failure (OECD, 2021) gave me language for the trade-offs I was making, and the IFAC guidance on internal control was the reason I made `create_voucher` raise on imbalance instead of silently logging.

If I were to start the project again, I would set up CI from day one. For most of the project I left the test runner as a manual `pytest` invocation, and we paid for that several times when a refactor broke something that nobody noticed for a week. In the final iteration I added a `.github/workflows/ci.yml` GitHub Actions workflow that runs `pytest` and `npm run build` on every push, which closes that gap — but doing it earlier would have saved real debugging time.

## A.4.2 Critical Appraisal

My module meets FR-10, FR-11, FR-12, FR-13 and FR-16, plus the security and observability requirements in NFR-3 and NFR-6. The double-entry rule is enforced by `finance_service.create_voucher` and is exercised by `tests/test_finance.py::test_voucher_raises_when_unbalanced`. JWT and bcrypt are wired in the app factory. Every protected endpoint goes through `require_permission`. Audit data is captured for login and AI assistant queries. The Docker setup builds and runs cleanly.

The clearest remaining weakness in my work is observability. I added structured stdout logging in the app factory and a GitHub Actions CI workflow that runs `pytest` and `npm run build` on every push, but I did not invest in distributed tracing, request correlation ids or a metrics exporter. The literature on production SME systems consistently flags observability as a make-or-break property; my honest appraisal is that the prototype is operable for a single-developer install but not yet ready for an actual deployment.

A third area I would push further is the role-permission matrix. The current six roles and nine permissions are sufficient for the prototype, but a real optical chain would want finer-grained controls (per-store permissions, time-bound permissions, delegation). The schema supports this — it is just a matter of adding more permission codes — but I did not have time to design a UI for managing them.

Finally, the architecture diagram I shipped is committed as a draw.io XML file. I would normally export it to a PDF and an SVG so that reviewers do not need to install draw.io to view it. Member 2 generously offered to do this export as part of the report assembly, but a more robust workflow would generate the export automatically as part of the documentation build.

Overall, I am satisfied with the security, finance and integration story that ships in iWear. The decisions I made are visible in the code, defensible in the literature and easy for a future contributor to extend. The gaps I left are operational rather than architectural, and they are exactly the kind of gaps that a second sprint would close.
