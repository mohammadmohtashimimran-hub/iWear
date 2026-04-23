# iWear – Vendor Setup & Handover Guide

This guide helps any e-commerce vendor run, customize, and hand over the system without code changes where possible.

---

## 1. How to run the system

### Option A: One command (full project in Docker)

**Prerequisite:** Docker Desktop installed and running.

From project root:

```powershell
python run.py
```

This starts the database and the app (Flask + built React) in Docker. Open **http://localhost:5000** in the browser. To stop: `Ctrl+C`, then `docker compose down` if needed.

**First-time seed (optional):** After the app is up, in another terminal:
```powershell
docker compose exec app flask seed
```
This creates roles, permissions, categories, brands, and a **default admin user** for the admin portal.

**Admin portal:** Open **http://localhost:5001/admin** (or 5000 if not using Docker port 5001).  
Default login (change in production): **admin@iwear.local** / **Admin123!**  
From the admin panel you can add products, manage orders, and open the storefront.

### Option B: Run backend and frontend separately (development)

### Prerequisites

- **Docker Desktop** (for PostgreSQL). Install:  
  `winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements`  
  After install, restart the PC or open Docker Desktop once.
- **Python 3.10+** with venv.
- **Node.js 18+** (for React frontend).

### Backend (Windows PowerShell, project root)

```powershell
# Virtual environment
.\venv\Scripts\Activate.ps1

# Start database (Docker)
.\backend\manage.ps1 start-db

# Apply migrations
cd backend
$env:FLASK_APP = "app.factory:app"
flask db upgrade

# Seed data (roles, permissions, order statuses, payment types, voucher types, store settings, CoA, eyewear, AI intents)
flask seed

# Run API server
cd ..
python backend\run.py
```

Backend runs at **http://127.0.0.1:5000**.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend runs at **http://127.0.0.1:3000** and proxies `/api` to the backend.

---

## 2. Environment variables (backend)

Create **backend/.env** (copy from **backend/.env.example** if present).

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes (production) | Flask secret; change in production. |
| `DATABASE_URL` | No (default) | PostgreSQL URL. Default: `postgresql://postgres:postgres@127.0.0.1:5433/iwear_dev`. |
| `JWT_SECRET_KEY` | No | JWT signing key; defaults to `SECRET_KEY`. |
| `JWT_ACCESS_TOKEN_EXPIRES` | No | Token lifetime in seconds; default 86400 (24h). |

Do not hardcode store name or currency in code; use **store settings** (below).

---

## 3. Store settings (no code change)

The system uses a **store_settings** table for branding and config. Use the API or seed to set:

| Key | Example | Description |
|-----|---------|-------------|
| `store_name` | My Store | Display name in header/title. |
| `store_logo_url` | https://... | Logo URL. |
| `currency_code` | PKR / USD | Currency for display. |
| `support_email` | support@... | Contact email. |
| `footer_text` | © 2026 ... | Footer content. |
| `meta_title` | My Store | Default page title. |
| `timezone` | Asia/Karachi | Timezone. |

- **GET** `/api/settings/` — returns all settings as JSON (public).
- **PUT** `/api/settings/` — update settings (send `{ "store_name": "New Name" }` etc.).  
  (Consider protecting PUT with auth in production.)

After deployment, change these via PUT or a small admin UI so the same codebase serves any vendor.

---

## 4. Adding a new role or permission

1. **Roles** and **permissions** are in the database (tables `roles`, `permissions`, `role_permissions`).
2. Seed creates: Super Admin, Admin, Finance Manager, Inventory Manager, Sales Staff, Viewer, and standard permissions (`inventory:write`, `finance:post`, etc.).
3. To add a new role: insert into `roles` (e.g. `name = 'Custom Role'`).  
4. To add a new permission: insert into `permissions` (`name`, `code`, `description`).  
5. To grant a permission to a role: insert into `role_permissions` (`role_id`, `permission_id`).

The backend checks permission codes (e.g. `inventory:write`, `finance:read`) on protected routes; no code change needed if you only add data.

---

## 5. Adding a payment type or order status

- **Payment types:** table `payment_types` (name, code, description). Seed creates Cash, COD, Card. Add rows for more types.
- **Order statuses:** table `order_statuses` (name, code, description). Seed creates Pending, Confirmed, Shipped, Delivered, Cancelled. Add rows as needed.

Codes (e.g. `cod`, `pending`) are used in the application; new codes can be used once the UI/API are extended to show or filter by them.

---

## 6. Architecture summary

- **Frontend:** React (Vite), port 3000, proxy `/api` to backend.
- **Backend:** Flask REST API, port 5000; JWT auth; RBAC via permissions.
- **Database:** PostgreSQL in Docker (port 5433 by default).

See **docs/week1/** and **docs/week2/** for architecture diagrams, ER design, and module structure.

---

## 7. Demo checklist (for handover)

1. Start DB: `.\backend\manage.ps1 start-db`
2. Backend: `flask db upgrade`, `flask seed`, `python backend\run.py`
3. Frontend: `cd frontend && npm install && npm run dev`
4. **Auth:** Register user → Login → GET `/api/auth/me`
5. **Catalog:** Open http://127.0.0.1:3000 → product list → product detail → add to cart
6. **Checkout:** Cart → Checkout → enter customer details → Place order (COD)
7. **Finance:** Login as user with `finance:post` → confirm COD for order → check trial balance / P&amp;L
8. **AI:** Login with `ai:query` → POST `/api/ai-assistant/query` with `{ "query": "sales today" }`

---

**Last updated:** After Week 3–9 implementation (auth, inventory, sales, finance, AI, React, vendor settings).
