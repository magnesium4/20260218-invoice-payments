# Setup Guide — Invoice & Payments

This guide explains how to run the Invoice & Payments application locally (backend API, frontend UI, and database).

---

## Prerequisites

- **Docker Desktop** (or another way to run PostgreSQL 16)
- **Python 3.9+**
- **Node.js 18+** and **npm**

---

## Project structure

```
├── backend/          # FastAPI API (Python)
├── frontend/         # React + Vite UI (TypeScript)
├── docker-compose.yml
├── seed-data.json    # Sample data for seeding
└── SETUP.md
```

---

## 1. Database (PostgreSQL)

Start PostgreSQL with Docker Compose from the **project root**:

```bash
docker compose up -d
```

This starts PostgreSQL 16 with:

- **Host:** `localhost`
- **Port:** `5432`
- **Database:** `invoices_db`
- **User:** `postgres`
- **Password:** `postgres`

To stop: `docker compose down`

---

## 2. Backend API

### 2.1 Virtual environment and dependencies

From the **project root**:

```bash
cd backend
python -m venv .venv
```

Activate the venv:

- **macOS/Linux:** `source .venv/bin/activate`
- **Windows:** `.venv\Scripts\activate`

Then install dependencies:

```bash
pip install -r requirements.txt
```

### 2.2 Environment (optional)

The backend uses these defaults if you don’t set env vars:

- `DATABASE_URL` — defaults to  
  `postgresql+psycopg2://postgres:postgres@localhost:5432/invoices_db`

To override, create a `.env` file in the **project root** or in `backend/`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/invoices_db
```

### 2.3 Migrations

From the **backend** directory (with venv activated):

```bash
alembic upgrade head
```

### 2.4 Seed data (optional)

To load sample customers, invoices, and payments:

```bash
python -m app.db.seed_db
```

(Expects `seed-data.json` at the project root or the path you pass.)

### 2.5 Run the API server

From the **backend** directory:

```bash
uvicorn app.main:app --reload
```

- API: **http://localhost:8000**
- Docs: **http://localhost:8000/docs**

---

## 3. Frontend

### 3.1 Dependencies

From the **project root**:

```bash
cd frontend
npm install
```

### 3.2 Environment

The frontend calls the API using `VITE_API_BASE_URL`. Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

(If unset, the app may try to use a relative URL and fail for API calls.)

### 3.3 Run the dev server

From the **frontend** directory:

```bash
npm run dev
```

- App: **http://localhost:5173**

---

## 4. Run everything (quick reference)

**Terminal 1 — Database:**

```bash
docker compose up -d
```

**Terminal 2 — Backend:**

```bash
cd backend
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
alembic upgrade head
python -m app.db.seed_db    # optional
uvicorn app.main:app --reload
```

**Terminal 3 — Frontend:**

```bash
cd frontend
npm install
# Ensure frontend/.env has VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

Then open **http://localhost:5173** in your browser.

---

## 5. Backend tests

From the **backend** directory (venv activated):

```bash
pytest tests/ -v
```

Tests use an in-memory SQLite DB (`test.db` in the backend directory); no running PostgreSQL is required for tests.

---

## 6. Troubleshooting

| Issue | What to check |
|--------|----------------|
| **Database connection refused** | Ensure `docker compose up -d` is running and port 5432 is free. |
| **Frontend can’t reach API** | Set `VITE_API_BASE_URL=http://localhost:8000` in `frontend/.env` and restart `npm run dev`. |
| **Migrations fail** | Confirm `DATABASE_URL` matches your Postgres user, password, host, port, and database name. |
| **Port already in use** | Change the port for uvicorn (`--port 8001`) or Vite (e.g. in `vite.config.ts`), or stop the process using the port. |

---

## 7. Production build (frontend)

From the **frontend** directory:

```bash
npm run build
```

Output is in `frontend/dist/`. Serve it with any static file server; ensure the API base URL is correct for the environment (e.g. via `VITE_API_BASE_URL` at build time).
