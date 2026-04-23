# Development setup (Windows)

How to run the backend and frontend locally on Windows.

## Prerequisites

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **Node.js 18+** (for frontend) — [nodejs.org](https://nodejs.org/)
- **Docker Desktop** (for PostgreSQL) — see “Install Docker” below.
- **PostgreSQL** (without Docker) — [postgresql.org](https://www.postgresql.org/download/windows/) or WSL; create DB `iwear_dev` and set `DATABASE_URL` in `backend\.env`.

## Install Docker (Windows)

Project ke liye PostgreSQL Docker se chalegi. Pehle Docker Desktop install karo:

```powershell
winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
```

- Install ke baad **PC restart** ya **Docker Desktop** open karo; first run par WSL 2 / Hyper-V setup ho sakta hai.
- Verify: nayi PowerShell window mein `docker --version` aur `docker compose version` chalao.

Agar winget nahi hai to: [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows/) se installer download karke install karo.

## Database (Docker)

From project root, use the PowerShell helper or Docker directly:

```powershell
# Start PostgreSQL (postgres:16-alpine, host port 5433, db iwear_dev)
.\backend\manage.ps1 start-db

# Stop
.\backend\manage.ps1 stop-db
```

Or: `docker compose up -d` / `docker compose down`.

## Backend (Flask)

1. **Create and activate a virtual environment** (from project root):

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. **Install dependencies** (project root has a single `requirements.txt`):

   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure environment**:

   - Copy `backend\.env.example` to `backend\.env`
   - `DATABASE_URL` in `.env.example` matches Docker: `postgresql://postgres:postgres@localhost:5432/iwear_dev`
   - Set `SECRET_KEY` and optionally `JWT_SECRET_KEY` for production-like config

4. **Run the backend** (from project root):

   ```powershell
   python backend/run.py
   ```

   API base: **http://127.0.0.1:5000**  
   Health check: **http://127.0.0.1:5000/api/health**

   Or from `backend/`:

   ```powershell
   cd backend
   python run.py
   ```

5. **Migrations** (with venv activated):

   First time only: start DB, then init and create initial migration:

   ```powershell
   .\backend\manage.ps1 start-db
   Copy-Item backend\.env.example backend\.env
   .\backend\manage.ps1 init
   .\backend\manage.ps1 migrate
   .\backend\manage.ps1 upgrade
   ```

   Later, after changing models: `.\backend\manage.ps1 migrate` then `.\backend\manage.ps1 upgrade`.  
   `.\backend\manage.ps1 seed` is a placeholder (no seed yet).

## Frontend

1. **Install dependencies** (from frontend directory, if present):

   ```powershell
   cd frontend
   npm install
   ```

2. **Run dev server** (e.g. Vite/React):

   ```powershell
   npm run dev
   ```

   Point the frontend API base URL to `http://127.0.0.1:5000` (or set in `.env` / env vars).

## Quick checklist

| Step              | Command / action                                          |
|-------------------|-----------------------------------------------------------|
| Install Docker    | `winget install -e --id Docker.DockerDesktop` (see above) |
| Backend venv      | `python -m venv venv` then activate                       |
| Backend deps      | `pip install -r requirements.txt`                        |
| Backend env       | Copy `backend\.env.example` → `backend\.env`              |
| Start DB          | `.\backend\manage.ps1 start-db`                           |
| Migrate (first)   | `.\backend\manage.ps1 upgrade` (venv active, from project root) |
| Run backend       | `python backend/run.py`                                   |
| Run frontend      | `cd frontend; npm install; npm run dev`                   |

## Notes

- Keep `backend\.env` out of version control (it is typically in `.gitignore`).
- For production, set `SECRET_KEY`, `JWT_SECRET_KEY`, and `DATABASE_URL` in the environment; avoid default secrets.
