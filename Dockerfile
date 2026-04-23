# Stage 1: Build React frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend + serve frontend
FROM python:3.11-slim
WORKDIR /app

# Install deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Backend code
COPY backend/ ./backend/

# Frontend build from stage 1
COPY --from=frontend-build /app/dist ./backend/frontend_dist/

WORKDIR /app/backend

ENV FLASK_APP=app.factory:app
ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1

# Migrate then start server (no external script = no Windows CRLF issue)
CMD ["sh", "-c", "flask db upgrade && exec gunicorn -w 1 -b 0.0.0.0:5000 --timeout 120 app.factory:app"]
