# iWear – Testing Report

## Scope

- **Unit / integration tests:** Backend (Flask) with pytest; in-memory SQLite for isolation.
- **Manual / system:** Frontend flows and full stack via demo checklist.

## Automated Tests (backend/tests)

| Test | Description |
|------|-------------|
| test_health | GET /api/health returns 200 and status ok |
| test_settings_get | GET /api/settings/ returns 200 and a dict |
| test_register | POST /api/auth/register creates user (201 or 409) |
| test_login | POST /api/auth/login with valid credentials returns access_token |
| test_login_wrong_password | POST /api/auth/login with wrong password returns 401 |
| test_voucher_raises_when_unbalanced | create_voucher raises ValueError when debit != credit (or when type/account missing) |
| test_in_types_defined | IN_TYPES contains IN and PURCHASE for stock movement logic |

**Run:** From project root: `cd backend && python -m pytest tests/ -v`

## Integration (manual)

- **Order flow:** Create cart → add items → create order (COD) → confirm COD → voucher posted.
- **Stock:** Purchase order receive creates stock_movements; low-stock endpoint returns variants below threshold.
- **RBAC:** Endpoints protected by permission (e.g. inventory:write, finance:post) return 403 without permission.
- **AI:** POST /api/ai-assistant/query with "sales today" returns intent and table/summary when intents are seeded.

## Limitations

- No Selenium/browser tests; no load tests.
- Tests use SQLite; production uses PostgreSQL (migrations not run in test DB).

**Last updated:** After Week 8 implementation.
