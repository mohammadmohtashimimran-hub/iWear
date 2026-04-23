# Chapter 4 — System Design

## 4.1 Architectural Overview

iWear is structured as a classical three-tier web application: a presentation tier (React 18 single-page application built with Vite), an application tier (Flask 3 with SQLAlchemy 2 and JWT-based RBAC) and a data tier (PostgreSQL 16 in production, SQLite in development, both managed by Alembic migrations). The decision to adopt a modular monolith — rather than a microservice mesh — was driven by the SME constraints discussed in the literature review: a single deployable artefact is dramatically easier to operate, monitor and reason about for a four-person team.

**Figure 4.1 — System Architecture (three-tier overview).** The rendered diagram is committed at `docs/architecture/system_architecture.drawio`. The diagram shows the customer and admin browsers connecting to the React SPA, the SPA exchanging JSON over HTTPS with the Flask blueprint layer, the blueprints calling into a service layer, the services persisting through SQLAlchemy to PostgreSQL, and a separate static-file route serving uploads. RBAC sits as a cross-cutting concern between the blueprints and the service layer.

```text
[Customer Browser]              [Admin Browser]
        \\                            //
         \\                          //
         [React SPA — Storefront + Admin]
                       │
                JSON (JWT in header)
                       │
        ┌──────────────┴──────────────┐
        │       Flask Blueprints      │
        │  auth · sales · inventory   │
        │  finance · ai · settings    │
        └──────────────┬──────────────┘
                       │  service layer (finance / inventory / ai)
                       │
                [SQLAlchemy ORM]
                       │
                 [PostgreSQL]
                       │
                  /uploads/
```

## 4.2 Subdomain Modules

Each Flask blueprint represents a single subdomain and lives in its own file under `backend/app/routes/`:

- **`auth_bp`** — `/api/auth/login`, `/api/auth/register`, `/api/auth/logout`, `/api/auth/me`. Issues JWTs and tracks active sessions.
- **`sales_bp`** — `/api/sales/products`, `/api/sales/carts`, `/api/sales/orders`, plus eyewear masters (`frame-types`, `lens-types`, `lens-indexes`, `lens-coatings`) and prescription endpoints. Around 850 lines of code, the largest module.
- **`inventory_bp`** — categories, brands, types, products (admin CRUD), variants, images, suppliers, warehouses, purchase orders and stock movements.
- **`finance_bp`** — chart of accounts, voucher types, vouchers and the trial balance / P&L reports.
- **`ai_assistant_bp`** — `POST /query`, `GET /intents`, `GET /history`. Calls the keyword matcher and runs predefined queries.
- **`settings_bp`** — store settings, countries and cities.
- **`health_bp`** — readiness probe and a smoke endpoint.

Each blueprint is registered explicitly in `backend/app/__init__.py:create_app`, which keeps wiring visible and makes route discovery trivial.

## 4.3 Service Layer

A thin service layer sits between the blueprints and the ORM. The point is to keep request handlers focused on HTTP concerns and to make business rules unit-testable without spinning up a Flask client.

- **`finance_service`** — `create_voucher`, `post_cod_sale`, `post_purchase`, `post_expense`. `create_voucher` enforces double-entry balance and assigns a voucher number before commit.
- **`inventory_service`** — `get_current_stock`, `get_low_stock_variants`. Encapsulates the difference between the legacy per-product `stock` table and the movement-based `stock_movements` table.
- **`ai_assistant_service`** — `normalize`, `detect_intent`, `run_predefined_query`, `format_response`. Implements the keyword matcher and the safe-query runner.

## 4.4 Data Model Overview

The database has approximately forty tables organised into seven groups: users & security, catalog & inventory, sales & e-commerce, eyewear domain, finance & accounting, settings & masters, and AI reporting. The full ERD is committed as a Mermaid diagram at `docs/architecture/database_erd.mmd` and as a text-based relation blueprint at `docs/week1/05_erd_relations.md`.

**Figure 4.2 — Entity Relationship Diagram (simplified)**

The ER diagram captures the seven subdomain groups and the relationships between them. Below is a simplified textual representation of the key entity clusters (the full Mermaid diagram is in the repository):

```text
SECURITY           CATALOG & INVENTORY        SALES & E-COMMERCE
─────────          ────────────────────        ──────────────────
users ──→ roles    products ──→ variants       customers ──→ orders
     ──→ perms          ──→ images                  ──→ carts
     ──→ audit          ──→ stock_movements         ──→ prescriptions
                   categories ──→ addons       carts ──→ cart_items
                   addons ──→ addon_options          ──→ cart_item_addons
                                               orders ──→ order_items
                                                     ──→ payments

EYEWEAR DOMAIN     FINANCE                    AI REPORTING
──────────────     ────────                    ────────────
frame_types        chart_of_accounts          reporting_intents
lens_types         vouchers ──→ entries          ──→ keywords
lens_indexes       voucher_types                 ──→ predefined_queries
lens_coatings                                 assistant_query_logs
prescription_records
  ──→ prescription_details (L/R eye: SPH, CYL, Axis, Add, PD)

SETTINGS
────────
countries ──→ cities
store_settings
order_statuses
payment_types
```

Key design choices include:

- **Movement-based inventory.** A `stock_movements` table records every IN/OUT event; the legacy per-product `stock` table is retained for compatibility but new code should compute current stock as a sum of movements.
- **Double-entry vouchers.** A `vouchers` table holds the header and a `voucher_entries` table holds the debit/credit lines. Validation lives in `finance_service.create_voucher`.
- **Eyewear domain tables.** `frame_types`, `lens_types`, `lens_indexes`, `lens_coatings`, `prescription_records` and `prescription_details` are first-class. A prescription belongs to a customer, has left- and right-eye details with sphere, cylinder, axis and PD values.
- **Flexible addons.** An `addons` group is bound to a product category, and each `addon_options` row is a selectable item with its own price. Cart items reference their selected addon options through the `cart_item_addons` junction table. This is how the storefront supports lens-option selection during the customer flow without exploding the variant catalog.
- **AI reporting tables.** `reporting_intents`, `intent_keywords`, `predefined_queries` and `assistant_query_logs` decouple the AI module from the rest of the schema and allow administrators to add new intents without code changes.

## 4.5 Authentication, Authorisation and Audit

Authentication uses JSON Web Tokens issued by Flask-JWT-Extended. The `users.id` is the JWT identity; a `user_lookup_loader` resolves the User on each authenticated request and exposes it through `get_current_user`. Authorisation is enforced by the `require_permission(code)` decorator defined in `backend/app/auth/decorators.py`. The decorator joins through the `roles` and `role_permissions` tables to check for the required permission code and returns 403 if missing. Default permissions are seeded by `seed.seed_permissions` and `seed.seed_role_permissions`. Audit data is captured in `audit_logs` (login/registration events) and `assistant_query_logs` (every AI assistant call).

## 4.6 Front-End Architecture

The React SPA is split between the storefront and the admin portal, sharing a single `AuthContext`, a thin API client (`src/api.js`) and a unified design system in `src/index.css`. Storefront routes live under `Layout` and admin routes live under `AdminLayout`, both wrapped in React Router v6 nested routes. Two design components from the v2 design upgrade — `Hero` (in `pages/ProductList.jsx`) and `AdminAIInsights` — illustrate the system's customer-facing and back-office surfaces.

A key design choice was to keep the API client centralised. Every backend interaction goes through one of the helpers exported from `src/api.js`, so cross-cutting concerns such as the `Authorization` header, error handling and base URL live in one place.

## 4.7 Deployment

The system is containerised with Docker. `docker-compose.yml` provisions a PostgreSQL 16 service. A multi-stage `Dockerfile` builds the React frontend and copies the dist into the Flask container under `frontend_dist/`, where Flask serves it from `/`. The `run.py` script offers a one-command launch for vendor handover. Migrations run via `flask db upgrade` and the `flask seed` command idempotently initialises the data set.

## 4.8 Design Trade-Offs

Several deliberate trade-offs shape the system. Server-side rendering was rejected because the SPA's interaction-heavy admin portal benefits more from React than from server templates. A microservice split was rejected because the operational overhead is unjustified at SME scale. ML-based AI was deferred because the predefined-query approach is auditable and safer for a prototype that will be reviewed academically. Each trade-off is revisited in Chapter 8 as a candidate for future work.
