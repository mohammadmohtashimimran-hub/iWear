# Chapter 6 — Testing

## 6.1 Strategy

Testing was approached at three levels: automated unit/integration tests run with `pytest`, manual end-to-end scenarios that exercised the storefront and admin portal in a real browser, and visual regression checks during the v2 design upgrade. The goal was not exhaustive coverage but credible evidence that the major business invariants hold and that the customer journey works end to end.

The key invariants that the test suite is designed to protect are:

- Authentication produces a JWT and is rejected on bad credentials.
- Product filters and sorting produce the expected slices of the catalog.
- Voucher posting refuses to write unbalanced vouchers.
- The AI intent matcher chooses the correct intent for typical phrases and runs the associated SQL safely.
- Public health and settings endpoints respond.

## 6.2 Test Stack

The backend uses `pytest` 9 with `pytest-flask`. Tests live in `backend/tests/`. The fixtures in `tests/conftest.py` build a fresh in-memory SQLite database per test function so that no test pollutes another. The application is constructed via the `create_app` factory with a `TestConfig` that overrides the JWT secret and points SQLAlchemy at `sqlite:///:memory:`.

```python
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-jwt-secret"
    SECRET_KEY = "test-secret"

@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()
```

This pattern is enough to spin up the entire blueprint graph, the JWT manager, the bcrypt extension and all SQLAlchemy models inside one test process.

## 6.3 Automated Test Coverage

**Table 6.1 — Automated test coverage summary (after this iteration)**

| Test module | Tests | Focus |
|-------------|-------|-------|
| `test_health.py` | 2 | Health probe and settings GET |
| `test_auth.py` | 3 | Register, login, login with wrong password |
| `test_inventory.py` | 1 | Stock movement type constants |
| `test_finance.py` | 1 | `create_voucher` rejects unbalanced entries |
| `test_ai_assistant.py` *(new)* | 6 | `normalize`, intent matching for two intents, no-match path, predefined query execution, response formatting |
| `test_sales_filters.py` *(new)* | 5 | Active-only filter, price range, category, sort asc/desc, search substring |
| `test_cart_order_flow.py` *(new)* | 3 | Full cart-to-order pipeline (cart → add item → customer → place order → verify state), inactive-cart rejection, missing-id validation |

A typical run produces:

```
============================= test session starts =============================
collected 21 items
tests/test_ai_assistant.py ......                                       [ 28%]
tests/test_auth.py ...                                                  [ 42%]
tests/test_cart_order_flow.py ...                                       [ 57%]
tests/test_finance.py .                                                 [ 61%]
tests/test_health.py ..                                                 [ 71%]
tests/test_inventory.py .                                               [ 76%]
tests/test_sales_filters.py .....                                       [100%]
========================== 21 passed in 2.15s =========================
```

The new modules added in this iteration push the suite from 7 to 21 tests, tripling the count. Coverage now includes the AI intent algorithm, the public catalog filters and — crucially — the end-to-end cart-to-order pipeline that previously could only be tested manually. A `.github/workflows/ci.yml` GitHub Actions workflow runs the same `pytest` invocation alongside a `npm run build` of the frontend on every push, so any future regression in either tier is caught automatically.

## 6.4 Manual Acceptance Scenarios

The following scenarios were exercised manually against a running instance using the demo seed data. Each one is referenced in Chapter 7 as evidence that the corresponding requirement is satisfied.

1. **Browse the catalog and apply filters.** Open `/`, observe the hero, scroll into the catalog, change the category and the price range, observe the URL parameters update and the grid refresh.
2. **View product detail.** Click a frame, observe the gallery, switch images, expand the *Lens Options* addon, select an option, see the running total update.
3. **Add to cart and checkout (guest).** Add a configured frame, open the cart drawer, increase the quantity, click *Checkout*, fill in the address form, place a COD order, land on the order confirmation screen.
4. **Authenticated checkout.** Register a new account, log in, place an order, navigate to *My Orders* and confirm the new order is listed.
5. **Admin product CRUD.** Log in to the admin portal, create a new product, attach images, save, verify it appears in the storefront after a refresh.
6. **Admin AI insights.** Open *AI Insights*, click the *Daily Sales* suggestion, observe the chat panel render the summary and table for today's sales. Type "monthly profit" and confirm the assistant responds.
7. **Order status admin.** Open an order in the admin portal, change its status, refresh the storefront *My Orders* page and confirm the new status renders.
8. **RBAC denial.** With a non-admin user, attempt to call `/api/inventory/products` directly and confirm the response is 403.

## 6.5 Coverage Gaps and Mitigation

After the integration tests added in this iteration, the cart-to-order pipeline is covered automatically. The remaining coverage gaps are the prescription capture flow and React component testing. Both are mitigated by the manual scenarios above and by the unit tests that cover the underlying invariants in isolation. Adding React Testing Library coverage for the addon-selection state machine is listed as future work in Chapter 8.

## 6.6 Reproducing the Tests

From the project root:

```bash
cd backend
python -m pytest tests/ -v
```

The tests do not require Postgres, an internet connection or any external services — they run in under three seconds on a developer laptop and on CI runners.
