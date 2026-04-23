# iWear - AI Enabled Eyewear ERP System

Enterprise-level eyewear inventory, e-commerce and finance management system.

## Quickstart (one command)

From the project root:

```bash
python dev.py
```

This will:

1. Create a Python virtualenv under `backend/.venv` and install `requirements.txt`.
2. Run `flask db upgrade` (SQLite, no Postgres needed).
3. Seed demo data — 8 products, multiple colour variants per product, placeholder images, Frame Glass / Lens Options / Sight / UV Tint addon groups, and the default admin user.
4. Install `frontend/node_modules`.
5. Start the Flask API on `http://localhost:5000` and the Vite dev server on `http://localhost:3000`.
6. Open `http://localhost:3000` in your browser.

Press `Ctrl-C` to stop both servers.

**Default admin credentials** (change in production):

- email: `admin@iwear.local`
- password: `Admin123!`

**Useful flags:**

```bash
python dev.py --setup-only   # install + migrate + seed, do not start servers
python dev.py --reset        # wipe and re-seed demo data before starting
```

The `--reset` flag is useful when you've been experimenting and want a clean catalogue back. It calls the `flask reset-demo` CLI command under the hood.

## Tech Stack

| Layer    | Technology                                      |
| -------- | ----------------------------------------------- |
| Frontend | React 18, React Router v6, Vite 5               |
| Backend  | Flask 3, Flask-SQLAlchemy, Flask-JWT-Extended     |
| Database | SQLite (local dev) / PostgreSQL (production)      |
| Auth     | JWT tokens, bcrypt password hashing               |
| Migrations | Alembic via Flask-Migrate                       |

---

## Prerequisites

- **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)
- **Node.js 18+** and **npm** — [nodejs.org](https://nodejs.org/)
- **Docker Desktop** *(optional, for PostgreSQL / production)* — [docker.com](https://www.docker.com/)

---

## Project Structure

```
EStore/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── config.py            # Environment-based config
│   │   ├── extensions.py        # Flask extensions (db, jwt, bcrypt, cors, migrate)
│   │   ├── seed.py              # Seed data (roles, permissions, admin user, etc.)
│   │   ├── models/              # SQLAlchemy models
│   │   ├── routes/              # API blueprints (auth, inventory, sales, finance, settings)
│   │   └── services/            # Business logic
│   ├── migrations/              # Alembic migration scripts
│   ├── uploads/                 # Uploaded product images
│   ├── instance/                # SQLite database file (auto-created)
│   ├── run.py                   # Backend entry point
│   ├── .env                     # Environment variables (local)
│   └── .env.example             # Template for .env
├── frontend/
│   ├── src/
│   │   ├── main.jsx             # React entry point
│   │   ├── App.jsx              # Routes & app shell
│   │   ├── api.js               # API client (fetch wrapper)
│   │   ├── AuthContext.jsx       # Auth state provider
│   │   ├── pages/               # Page components (Login, Cart, Checkout, etc.)
│   │   └── components/          # Reusable UI components
│   ├── package.json
│   └── vite.config.js           # Vite config with API proxy to port 5000
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Production Docker image
├── docker-compose.yml           # Docker Compose (DB + app)
└── run.py                       # One-command Docker launcher
```

---

## Quick Start (Local Development)

### 1. Clone the repository

```bash
git clone <repository-url>
cd EStore
```

### 2. Set up the backend

```bash
# Create a Python virtual environment
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# macOS / Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configure environment variables

The backend ships with a SQLite config by default. To customise, edit `backend/.env`:

```bash
# backend/.env — omit DATABASE_URL for default SQLite (backend/instance/iwear_dev.db)
SECRET_KEY=dev-secret-change-in-production-32b
JWT_SECRET_KEY=dev-secret-change-in-production-32b
```

For PostgreSQL, update `DATABASE_URL`:

```bash
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5433/iwear_dev
```

### 4. Initialise the database & run migrations

```bash
cd backend

# Run all migrations to create/update tables
flask db upgrade

# Seed roles, permissions, order statuses, admin user, and master data
flask seed

cd ..
```

### 5. Start the backend server

```bash
python backend/run.py
```

The API will be available at **http://localhost:5000**.

### 6. Set up and start the frontend

Open a **new terminal**:

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start the Vite dev server
npm run dev
```

The web app will be available at **http://localhost:3000**.

Vite proxies `/api` and `/uploads` requests to the Flask backend automatically.

---

## Default Admin Credentials

After running `flask seed`, a default admin account is created:

| Field    | Value                |
| -------- | -------------------- |
| Email    | admin@iwear.local    |
| Password | Admin123!            |

> Change these credentials in production by setting `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables before seeding.

---

## Common Commands Reference

### Backend

| Command                      | Description                                  |
| ---------------------------- | -------------------------------------------- |
| `pip install -r requirements.txt` | Install all Python dependencies         |
| `flask db upgrade`           | Apply all pending database migrations        |
| `flask db migrate -m "msg"`  | Auto-generate a new migration                |
| `flask db downgrade`         | Revert the last migration                    |
| `flask seed`                 | Seed master data (roles, statuses, admin, etc.) |
| `python backend/run.py`     | Start Flask dev server (port 5000)           |
| `pytest`                     | Run the test suite                           |

### Frontend

| Command            | Description                          |
| ------------------ | ------------------------------------ |
| `npm install`      | Install Node.js dependencies          |
| `npm run dev`      | Start Vite dev server (port 3000)     |
| `npm run build`    | Build for production                  |
| `npm run preview`  | Preview the production build locally  |

### Docker (Production)

| Command                           | Description                          |
| --------------------------------- | ------------------------------------ |
| `python run.py`                   | Start everything via Docker Compose  |
| `docker compose up --build`       | Build and start containers           |
| `docker compose down`             | Stop and remove containers           |
| `docker compose logs -f`          | Follow container logs                |

---

## API Endpoints Overview

All API routes are prefixed with `/api`.

| Endpoint                | Method | Description                |
| ----------------------- | ------ | -------------------------- |
| `/api/health`           | GET    | Health check               |
| `/api/auth/register`    | POST   | Register a new user        |
| `/api/auth/login`       | POST   | Login and get JWT token    |
| `/api/auth/me`          | GET    | Get current user profile   |
| `/api/products`         | GET    | List products              |
| `/api/products/<id>`    | GET    | Product detail             |
| `/api/cart`             | GET    | View cart                  |
| `/api/orders`           | POST   | Place an order             |
| `/api/orders`           | GET    | Order history              |
| `/api/settings/...`     | GET    | Store settings & locations |
| `/api/admin/...`        | *      | Admin management endpoints |

---

## Environment Variables

| Variable                    | Default                                      | Description                  |
| --------------------------- | -------------------------------------------- | ---------------------------- |
| `DATABASE_URL`              | SQLite at `backend/instance/iwear_dev.db` (absolute path in config) | Omit or set for Postgres     |
| `SECRET_KEY`                | `dev-secret-change-in-production-32b`        | Flask secret key             |
| `JWT_SECRET_KEY`            | same as SECRET_KEY                           | JWT signing secret           |
| `JWT_ACCESS_TOKEN_EXPIRES`  | `86400` (24 hours)                           | Token expiry in seconds      |
| `ADMIN_EMAIL`               | `admin@iwear.local`                          | Default admin email (seed)   |
| `ADMIN_PASSWORD`            | `Admin123!`                                  | Default admin password (seed)|

---

## Testing

```bash
cd backend
pytest
```

Tests use an in-memory SQLite database by default so they don't affect your development data.
# iWear
