# iWear – Evaluation (MSc Project)

## Objectives vs deliverables

| Objective | Deliverable | Status |
|-----------|-------------|--------|
| Inventory management (products, stock, low-stock) | Inventory APIs, stock_movements, low_stock_threshold, GET /api/inventory/low-stock | Done |
| E-commerce with eyewear customization (frame, lens, prescription), COD | Sales APIs, prescription, cart, order (COD), React product/cart/checkout | Done |
| AI Business Insights (natural language) | Intent detection, predefined queries, POST /api/ai-assistant/query, logging | Done |
| Finance / voucher-based accounting | Chart of accounts, vouchers, double-entry, trial balance, P&L, COD posting | Done |
| Secure access (RBAC) | Login, JWT, permissions, require_permission on endpoints | Done |
| Generic / vendor-ready | store_settings, seed data, VENDOR_SETUP.md | Done |

## Security

- **Auth:** bcrypt password hashing; JWT access tokens; session table for logout.
- **RBAC:** Role–permission mapping; decorator `require_permission(code)` on protected routes.
- **Evaluation:** Unauthorized access (no token or wrong permission) returns 401/403; automated tests cover login and wrong password.

## Financial accuracy

- **Double-entry:** create_voucher enforces total debit = total credit; test_voucher_raises_when_unbalanced validates ValueError.
- **Reports:** Trial balance and P&L use voucher_entries and chart_of_accounts.

## AI reporting

- **Intent:** Keyword-based match against intent_keywords; returns reporting_intent.
- **Execution:** Predefined SQL with safe params (e.g. {{today}}); read-only; result as summary + table.
- **Logging:** assistant_query_logs stores raw_query, interpreted_intent_id, response_status.

## Reliability

- **Stack:** Flask + PostgreSQL + React; Docker for DB.
- **Tests:** 7 pytest tests (health, settings, auth, finance validation, inventory constants).

## Handover

- **VENDOR_SETUP.md:** How to run, env vars, store settings, roles/permissions, demo checklist.
- **TESTING_REPORT.md:** What was tested and how to run tests.

**Last updated:** After Week 9 (evaluation and handover).
