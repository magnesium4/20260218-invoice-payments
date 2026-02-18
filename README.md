# Invoice & Payments

A full-stack application for managing **invoices** and **payments**: create invoices for customers, post them for payment, record full or partial payments, delete drafts, void pending invoices, or track them through to paid.

---

## What it does

- **Customers** — Create and list customers; associate invoices with a customer.
- **Invoices** — Create invoices (amount, currency, issued/due dates). Invoices move through statuses: **DRAFT** → **PENDING** → **PAID** or **VOID**.
- **Payments** — Record payments against a **PENDING** invoice. Partial payments are allowed; when the sum of payments equals the invoice amount, the invoice becomes **PAID**.
- **UI** — List invoices with filters (status, customer, date range), view invoice details and payment history, create invoices, record payments, post or delete drafts, and void pending invoices.

---

## Tech stack

| Layer    | Stack |
|----------|--------|
| Backend  | FastAPI, SQLAlchemy 2, PostgreSQL, Alembic |
| Frontend | React, TypeScript, Vite, React Query, React Router |
| DB       | PostgreSQL 16 (Docker) |

---

## Business assumptions and rules

### Invoice lifecycle

- **DRAFT** — Newly created; not yet sent for payment. Cannot accept payments. **DRAFT invoices can be deleted** (removed from the DB via `DELETE /invoices/{id}`).
- **PENDING** — “Sent for payment.” Accepts payments. Reached by **posting** a DRAFT (`POST /invoices/{id}/post`). **PENDING invoices can be voided** (status set to VOID); they are not deleted.
- **PAID** — Sum of payments equals invoice amount. No further payments allowed.
- **VOID** — Cancelled (status only; row remains). Only PENDING can be voided; PAID cannot be voided. No payments allowed.

Flow: create (DRAFT) → post (PENDING) → record payments until PAID, or **delete** a DRAFT or **void** a PENDING.

### Payments

- **Positive only** — Payment amount must be &gt; 0 (validated in API and schema).
- **No overpayment** — Sum of payments for an invoice cannot exceed the invoice amount. A payment that would exceed the remaining balance is rejected.
- **Only PENDING** — Payments can be recorded only for invoices in status **PENDING**. DRAFT, PAID, and VOID reject new payments.
- **Automatic PAID** — When the sum of all payments for an invoice equals (or exceeds) the invoice amount, the invoice status is set to **PAID** on that payment.
- **Concurrency** — Recording a payment uses a row-level lock on the invoice (`SELECT ... FOR UPDATE`) so concurrent payments for the same invoice are serialized and overpayment/race conditions are avoided.

### Currency and amounts

- **Currency** — Stored as a 3-character code (e.g. USD, EUR, GBP). The UI allows any 3-letter code; no exchange or multi-currency conversion.
- **Amounts** — Stored and handled as decimals. No rounding assumptions beyond normal decimal arithmetic; currency formatting in the UI is for display only.

### Customers and references

- **Customer required** — Every invoice has a required `customer_id` (FK to customers). Deleting customers is out of scope; referential integrity is assumed.
- **List and filter** — Invoices can be listed globally or per customer, with optional filters: `status`, `customer_id`, and `from`/`to` on `issued_at`.

### Delete, void, and post

- **Delete** — Only **DRAFT** invoices can be deleted (`DELETE /invoices/{id}`). The invoice and any related data are removed from the DB. PENDING/PAID/VOID cannot be deleted.
- **Void** — Only **PENDING** invoices can be voided. The invoice status is set to VOID; the row is kept. DRAFT invoices cannot be voided (use delete instead); PAID and already-VOID return an error.
- **Post** — Only a DRAFT invoice can be posted; posting sets status to PENDING.

---

## Project layout

```
├── backend/          # FastAPI app, services, models, migrations, tests
├── frontend/         # React app (Vite, TypeScript)
├── docker-compose.yml
├── seed-data.json
├── SETUP.md          # How to run locally
└── README.md
```

---

## Running the application

See **[SETUP.md](./SETUP.md)** for:

- Prerequisites (Docker, Python, Node)
- Starting PostgreSQL with Docker Compose
- Backend: venv, migrations, seed, running the API
- Frontend: env, install, dev server
- Running backend tests

Quick start: start the DB (`docker compose up -d`), run migrations and seed from `backend/`, start the API and then the frontend; open the app at the URL given by the frontend dev server (e.g. http://localhost:5173).
