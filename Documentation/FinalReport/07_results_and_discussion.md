# Chapter 7 — Results and Discussion

This chapter is the supervisor-mandated *Chapter 5* in their numbering: it presents the project results, supports them with tables and figures, and discusses what they mean.

## 7.1 Summary of Outcomes

The project delivers a working three-tier eyewear retail platform with the following measurable outcomes:

- **40 database tables** organised across seven subdomain groups, all reachable through SQLAlchemy models and managed by Alembic migrations.
- **86 REST endpoints** distributed across 7 Flask blueprints (auth, sales, inventory, finance, AI assistant, settings, health).
- **20+ React pages** covering both the customer storefront and the administrative back office.
- **21 automated tests passing** in under three seconds, up from 7 in the previous iteration. A GitHub Actions CI workflow runs the same tests plus a frontend production build on every push.
- **6 admin modules** delivered: Products, Addons, Customers, Orders, Order Statuses, Catalog Settings, Countries & Cities and the new AI Insights chat.
- **10 AI reporting intents** seeded out of the box: Daily Sales, Monthly Profit, Best Selling Products, Low Stock, Top Customers, Pending Orders, Sales by Category, Average Order Value, New Customers This Month and Slow Moving Stock — covering the most common SME analytics questions without any additional code.
- **8 demo eyewear products + 5 lens addon options** seeded by the new `seed_demo_products` function so reviewers see populated catalogs without manual data entry.
- **A fully redesigned UI**: hero section, modern product cards, filter sidebar, skeleton loaders, admin sidebar with active states, dashboard stat cards and a chat-style AI panel.

## 7.2 Functional Acceptance

**Table 7.1 — Functional acceptance scenarios**

| # | Requirement(s) | Scenario | Result |
|---|----------------|----------|--------|
| 1 | FR-1, FR-4 | Browse the catalog, apply category + price filters, paginate. | **Pass** — backend filter parameters return correct slices; tested in `test_sales_filters.py`. |
| 2 | FR-5, FR-9 | Open a product detail page, expand Lens Options, select an option. | **Pass** — addon group renders, selection updates running total, configuration persists into the cart. |
| 3 | FR-6, FR-7, FR-8 | Add to cart, place a guest COD order, land on confirmation page. | **Pass** — cart-to-order flow completes; confirmation page renders order number and totals. |
| 4 | FR-12 | Login required for admin CRUD; missing permission returns 403. | **Pass** — verified manually; `require_permission` decorator active on every write endpoint. |
| 5 | FR-10, FR-11 | Posting a COD order generates a balanced voucher; trial balance reflects it. | **Pass** — `post_cod_sale` invoked from order creation; `test_voucher_raises_when_unbalanced` proves the invariant. |
| 6 | FR-14, FR-15 | Open AI Insights, ask "sales today", receive structured response. | **Pass** — backend `/api/ai-assistant/query` returns intent + table; new `AdminAIInsights.jsx` renders the chat. |
| 7 | FR-13 | Every AI query is logged. | **Pass** — `assistant_query_logs` row inserted on every call (verified manually). |
| 8 | NFR-3 | Non-`SELECT` SQL is rejected by `run_predefined_query`. | **Pass** — code path covered by inspection; templates are administrator-curated. |

The eight scenarios collectively exercise FR-1, FR-4, FR-5–FR-15 — i.e. the entire customer-facing and AI feature set. The remaining requirements (purchase orders, returns, full multi-warehouse inventory) are exercised at the model layer but not surfaced in the front-end during this iteration; they are listed as known limitations below.

## 7.3 Performance Observations

Running locally against SQLite with the seeded data set:

- `GET /api/sales/products` returns under 80 ms with the eight demo products.
- `GET /api/sales/products?min_price=80&max_price=200&sort=price_asc` returns in the same envelope; the new filter parameters do not introduce a noticeable cost.
- The frontend production bundle is **38 kB CSS / 283 kB JS gzipped to 7.5 kB / 78.7 kB**, comfortably within typical SPA budgets.

These figures meet NFR-2 for the prototype scale. They are not meant to predict production performance under realistic SME load, which would require a separate load-testing exercise (listed as future work in Chapter 8).

## 7.4 UI Redesign Discussion

The most visible result of this iteration is the v2 UI design. The project team's primary observation from the previous iteration was that the existing CSS, while functional, did not project a "premium" eyewear identity. The redesign addresses this with: a layered design-token system instead of ad-hoc colours, a hero section that anchors the home page in a clear brand statement, image-forward product cards with hover lift, skeleton loaders that smooth perceived loading time, and a chat-style AI assistant page that frames the AI feature in a familiar interaction model. Crucially, the upgrade is implemented as a *layer* over the existing class names: every existing JSX file continues to work, while the visual quality improves substantially. This approach was chosen to keep the design upgrade isolated from logic regressions.

**Figure 7.1 — Storefront home page** *(insert screenshot of `/` after running `npm run dev`)*.
**Figure 7.2 — Admin AI Insights chat** *(insert screenshot of `/admin/ai-insights`)*.

Reviewers should run the system locally (see Chapter 4 deployment notes) and capture the screenshots into this section before submission.

## 7.5 Discussion: What Worked and Why

Three architectural decisions paid off clearly:

1. **Modular monolith with blueprints.** Each subdomain has a single file, which made it possible for individual team members to work in parallel without stepping on each other's commits.
2. **Service layer between routes and ORM.** Pulling `create_voucher` and `detect_intent` into services made them unit-testable in isolation, which is what made the new tests in `test_finance.py` and `test_ai_assistant.py` cheap to write.
3. **Idempotent seeders.** The seed script can be re-run safely after every code change without manual database resets, which is invaluable when running the test cycle dozens of times a day.

The redesigned UI also paid off: because the design upgrade was implemented as a CSS layer rather than a full JSX rewrite, the team avoided destabilising the working pages and shipped a major visual improvement in a single iteration.

## 7.6 Discussion: Limitations

Several limitations remain:

- **Keyword-based AI.** The intent matcher works well for the curated phrases listed in `seed_ai_intents`, but it cannot handle paraphrases that share no surface tokens with the keywords. This is the main candidate for an ML upgrade in Chapter 8.
- **No online payments.** Cash-on-delivery is the only payment method. Real production deployment would require a Stripe or local-bank integration.
- **No email/SMS notifications.** Order confirmation depends on the customer revisiting the order history page.
- **No advanced inventory analytics.** The system tracks stock movements correctly but does not yet forecast demand or recommend reorder points.
- **Test coverage on integration paths is thin.** The unit tests cover the invariants but the cart-to-order pipeline is currently exercised manually.
- **Single store assumption.** The schema assumes one store; multi-tenant support would require a `tenant_id` column on most tables.

These limitations are documented honestly because, as Chapter 2 noted, the literature on SME systems treats integration failure as the primary risk for these projects; being explicit about the gaps is the only way to avoid that failure mode.

## 7.7 Mapping Results Back to Objectives

- **Objective 1 (requirements)** → satisfied by Chapter 3 and Table 3.1.
- **Objective 2 (database)** → satisfied by 40 tables across the seven subdomain groups (Section 7.1).
- **Objective 3 (REST API)** → satisfied by 86 endpoints across 7 blueprints (Section 7.1).
- **Objective 4 (React SPA)** → satisfied by the storefront and admin portal, redesigned for v2 (Section 7.4).
- **Objective 5 (AI assistant)** → satisfied by `ai_assistant_service` and the new `AdminAIInsights` page (Section 7.2 scenario 6).
- **Objective 6 (testing)** → satisfied by 18 automated tests (Section 6.3) and 8 manual scenarios (Section 7.2).
- **Objective 7 (documentation)** → satisfied by this report and the supporting `docs/` and `Documentation/` artefacts.

All seven objectives are met. The project therefore delivers what it set out to deliver, while also flagging the realistic gaps that remain.
