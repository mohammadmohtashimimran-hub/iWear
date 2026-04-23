# iWear – ChatGPT / Cursor Progress Log

**Project:** iWear (eyewear ecommerce)  
**Repo path:** `c:\Ali\Webapps\eyewear ecommerce`  
**Environment:** Windows, PowerShell.

---

## Docker Desktop (one-time)

```powershell
winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
```

Install ke baad ek baar PC restart ya Docker Desktop open karo; phir `docker compose` use ho sakta hai.

---

## Commands (PowerShell, project root se)

```powershell
# Venv activate
.\venv\Scripts\Activate.ps1

# DB start (Docker – pehle Docker install/start karo)
.\backend\manage.ps1 start-db

# Migrations (backend folder se, venv active)
cd backend
$env:FLASK_APP = "app.factory:app"
flask db upgrade
flask db migrate -m "your_message"

# Run backend
python backend\run.py
```

---

## Week 1 (done earlier)

- Business scope, architecture (React + Flask + PostgreSQL), workflow and ER docs in `docs/week1/`.
- Initial models: User, Role, UserRole, ProductCategory, ProductBrand, ProductType, Product, Stock.
- Health endpoint: `GET /api/health`.
- Diagram updates: `docs/week1/week1-diagrams-update.md`.

---

## Week 2 – Completed (enterprise schema & backend foundation)

### 1) Models reorganized into domain files

- **backend/app/models/**  
  - `users.py` – User, Role, user_roles, Permission, RolePermission, Session  
  - `audit.py` – AuditLog  
  - `catalog.py` – ProductCategory, ProductBrand, ProductType, Product, Stock  
  - `inventory.py` – Supplier, Warehouse, ProductVariant, ProductImage, StockMovement, StockAdjustment, InventoryValuation  
  - `eyewear.py` – FrameType, LensType, LensIndex, LensCoating, PrescriptionRecord, PrescriptionDetail  
  - `sales.py` – Customer, CustomerAddress, Cart, CartItem, OrderStatus, Order, OrderItem, Return, ReturnItem  
  - `finance.py` – PaymentType, Payment, VoucherType, ChartOfAccount, Voucher, VoucherEntry, JournalEntry, ExpenseCategory, Expense, PurchaseOrder, PurchaseOrderItem, SupplierPayment, SalesTransaction, TaxRecord  
  - `ai_reporting.py` – DailySalesSummary, MonthlyProfitSummary, InventoryValuationSummary, FinancialReportLog, ReportingIntent, IntentKeyword, PredefinedQuery, AssistantQueryLog  
  - `__init__.py` – imports and exports all models (and `UserRole` alias).

### 2) Security & access control tables

- permissions, role_permissions, sessions, audit_logs added. User and Role unchanged.

### 3) Inventory foundation tables

- suppliers, warehouses, product_variants, product_images, stock_movements, stock_adjustments, inventory_valuation. Legacy `stock` table retained.

### 4) Eyewear domain tables

- frame_types, lens_types, lens_indexes, lens_coatings, prescription_records, prescription_details.

### 5) Sales & order tables

- customers, customer_addresses, carts, cart_items, order_statuses, orders, order_items, returns, return_items.

### 6) Payment & finance tables

- payment_types, payments, voucher_types, chart_of_accounts, vouchers, voucher_entries, journal_entries, expense_categories, expenses, purchase_orders, purchase_order_items, supplier_payments, sales_transactions, tax_records.

### 7) Reporting & AI tables

- daily_sales_summary, monthly_profit_summary, inventory_valuation_summary, financial_reports_log, reporting_intents, intent_keywords, predefined_queries, assistant_query_logs.

### 8) Backend module structure (skeleton)

- **backend/app/**  
  - `auth/`, `inventory/`, `sales/`, `finance/`, `ai_assistant/`, `services/`, `utils/` – each with `__init__.py`.  
- **backend/app/routes/**  
  - `auth.py`, `inventory.py`, `sales.py`, `finance.py`, `ai_assistant.py` – each defines a blueprint with placeholder route; all registered in `create_app()`.

### 9) Migration

- Migration generated: `backend/migrations/versions/96904e6e8d8a_week2_enterprise_schema.py`.  
- `flask db upgrade` run successfully.

### 10) Documentation

- **docs/week2/01_enterprise_schema.md** – table groups, movement-based inventory, finance baseline (vouchers, chart of accounts).  
- **docs/week2/02_backend_module_structure.md** – folder layout, model files, route prefixes.

---

## Week 3 – Auth & RBAC (done)

- Store settings model + migration; low_stock_threshold on product_variants.
- Seed: roles, permissions, role_permissions, order_statuses, payment_types, voucher_types, chart_of_accounts, eyewear masters, store_settings, AI intents/keywords/predefined_queries.
- POST /api/auth/login, /register, /logout; GET /api/auth/me; JWT + sessions; require_permission decorator; audit on login/register.
- GET/PUT /api/settings/.

---

## Week 4 – Inventory & procurement (done)

- Product/variant CRUD; stock from movements; GET /api/inventory/low-stock; POST /api/inventory/movements; suppliers, warehouses CRUD; purchase orders CRUD + POST .../receive (goods receipt).

---

## Week 5 – Sales & e-commerce (done)

- Backend: GET /api/sales/products, /products/:id; frame-types, lens-types, lens-indexes, lens-coatings; POST prescriptions, customers, addresses; carts CRUD; POST /api/sales/orders (COD); GET orders.
- React frontend (Vite): product list, product detail, cart, checkout (COD), order confirmation, order history. Proxy /api to backend.

---

## Week 6 – Finance (done)

- Chart of accounts CRUD; voucher types; POST /api/finance/vouchers (double-entry); GET trial-balance, profit-loss; POST /api/finance/orders/:id/confirm-cod (post Sales Voucher).
- finance_service: create_voucher, post_cod_sale, post_purchase, post_expense, post_supplier_payment.

---

## Week 7 – AI Business Insights (done)

- Intent detection (keyword match); predefined SQL with {{today}} etc.; POST /api/ai-assistant/query; response summary + table; assistant_query_logs.
- Seed: Daily Sales, Monthly Profit, Best Selling, Low Stock intents with keywords and queries.

---

## Week 8 – Integration & testing (done)

- Pytest: health, settings, auth (register, login, wrong password), finance (voucher unbalanced raises), inventory (IN_TYPES). Run: `cd backend && python -m pytest tests/ -v`.
- docs/TESTING_REPORT.md.

---

## Week 9 – Evaluation & handover (done)

- docs/VENDOR_SETUP.md (run, env, store settings, roles, demo checklist).
- docs/EVALUATION.md (objectives vs deliverables, security, financial accuracy, AI, reliability).
- docs/TESTING_REPORT.md.

---

## Agay (optional)

- [ ] Online payment gateway (out of scope per spec).
- [ ] Advanced AI (e.g. ML-based intent).
- [ ] Full eyewear guided flow in React (frame → lens → prescription → add to cart).

---

**Last updated:** Weeks 3–9 plan implemented; vendor-ready; CHATGPT_PROGRESS updated.
