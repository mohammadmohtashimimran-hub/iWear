# Week 2 – Backend Module Structure (iWear)

## Layout

```
backend/app/
├── __init__.py          # create_app(), blueprint registration
├── config.py
├── extensions.py        # db, migrate, bcrypt, jwt, cors
├── factory.py            # app instance for CLI
├── auth/                 # auth module (skeleton)
│   └── __init__.py
├── inventory/
│   └── __init__.py
├── sales/
│   └── __init__.py
├── finance/
│   └── __init__.py
├── ai_assistant/
│   └── __init__.py
├── services/            # business logic layer (skeleton)
│   └── __init__.py
├── utils/                # shared utilities (skeleton)
│   └── __init__.py
├── models/               # domain-split models
│   ├── __init__.py       # exports all models
│   ├── users.py          # User, Role, Permission, RolePermission, Session
│   ├── audit.py          # AuditLog
│   ├── catalog.py        # ProductCategory, ProductBrand, ProductType, Product, Stock
│   ├── inventory.py      # Supplier, Warehouse, ProductVariant, ProductImage, StockMovement, StockAdjustment, InventoryValuation
│   ├── eyewear.py        # FrameType, LensType, LensIndex, LensCoating, PrescriptionRecord, PrescriptionDetail
│   ├── sales.py          # Customer, CustomerAddress, Cart, CartItem, OrderStatus, Order, OrderItem, Return, ReturnItem
│   ├── finance.py        # PaymentType, Payment, VoucherType, ChartOfAccount, Voucher, VoucherEntry, JournalEntry, ExpenseCategory, Expense, PurchaseOrder, PurchaseOrderItem, SupplierPayment, SalesTransaction, TaxRecord
│   └── ai_reporting.py   # DailySalesSummary, MonthlyProfitSummary, InventoryValuationSummary, FinancialReportLog, ReportingIntent, IntentKeyword, PredefinedQuery, AssistantQueryLog
└── routes/
    ├── __init__.py
    ├── health.py         # GET /api/health
    ├── auth.py           # /api/auth (skeleton)
    ├── inventory.py      # /api/inventory (skeleton)
    ├── sales.py          # /api/sales (skeleton)
    ├── finance.py        # /api/finance (skeleton)
    └── ai_assistant.py   # /api/ai-assistant (skeleton)
```

## Design Notes

- **Models** are grouped by domain (users, catalog, inventory, eyewear, sales, finance, ai_reporting, audit). Flask-Migrate discovers them via `app.models` import in `create_app`.
- **Routes** are split by area; each blueprint has a placeholder route (e.g. GET `/api/auth/`) so the module is registered and testable. Full business logic is not implemented yet.
- **auth/**, **inventory/**, **sales/**, **finance/**, **ai_assistant/**, **services/**, **utils/** are package stubs for future logic (e.g. auth decorators, inventory service, voucher posting).
- **Health** endpoint remains at `GET /api/health`; new blueprints use prefixes `/api/auth`, `/api/inventory`, `/api/sales`, `/api/finance`, `/api/ai-assistant`.

## API Prefixes

| Blueprint     | URL prefix          |
|---------------|---------------------|
| health        | /api                |
| auth          | /api/auth           |
| inventory     | /api/inventory      |
| sales         | /api/sales          |
| finance       | /api/finance        |
| ai_assistant  | /api/ai-assistant   |
