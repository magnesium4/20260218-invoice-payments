# Take-Home Assignment — Invoice Status & Payments

## About This Exercise

At eCapital, we build fintech services using microservices and relational databases. This exercise asks you to design and implement a small full-stack application for managing invoices and payments — a simplified version of the kind of work our engineering team does every day.

There are no trick questions. We're looking for clean code, sound data modeling, and thoughtful decision-making.

---

## Goal

Build a full-stack **Invoice & Payments** application with a microservice-style backend API and a front-end UI.

- Use any **front-end framework** (React, Vue, Angular, etc.) or CSS library
- Implement the **backend API** with the framework of your choice and a **SQL database**
- We're evaluating: data modeling, API design, code organization, UI/UX, and documentation

---

## Domain

**Invoices** represent amounts owed by customers. **Payments** are applied against invoices and can be partial — an invoice becomes `PAID` only when the sum of its payments equals the invoice amount.

### Data Model (minimum)

**Customers**

| Field | Type |
|-------|------|
| id | integer / UUID |
| name | string |

**Invoices**

| Field | Type | Notes |
|-------|------|-------|
| id | integer / UUID | |
| customer_id | FK → customers | |
| amount | decimal | Total amount owed |
| currency | string | e.g. `USD`, `CAD` |
| issued_at | timestamp | |
| due_at | timestamp | |
| status | enum | `DRAFT`, `PENDING`, `PAID`, `VOID` |

**Payments**

| Field | Type | Notes |
|-------|------|-------|
| id | integer / UUID | |
| invoice_id | FK → invoices | |
| amount | decimal | Partial or full payment |
| paid_at | timestamp | |

You may add additional fields or tables as you see fit — just document your reasoning.

---

## Functional Requirements

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/invoices` | Create a new invoice |
| `GET` | `/invoices/{id}` | Get invoice details (including payments) |
| `POST` | `/invoices/{id}/payments` | Record a payment against an invoice |
| `GET` | `/customers/{id}/invoices` | List invoices for a customer |

The **list endpoint** should support query parameters for filtering:
- `status` — filter by invoice status
- `from` / `to` — filter by `issued_at` date range

### Business Rules

- A payment **must not** cause the total paid to exceed the invoice amount (no overpayment)
- A payment amount **must be positive**
- When `sum(payments) == invoice.amount`, the invoice status should transition to `PAID`
- A `VOID` or `PAID` invoice should not accept new payments

### Front-End UI

- List all invoices with: customer name, amount (currency-formatted), status, issued date, and due date
- View invoice details including a breakdown of payments
- Create a new invoice
- Record a payment against an invoice
- Filter invoices by status and/or customer
- Add validations as necessary

---

## Things We're Looking For

These aren't strict requirements — they're areas where you can demonstrate your thinking:

- **Data integrity:** How do you enforce invariants (no overpayment, no negative payments) at the database and/or application level?
- **Concurrency:** What happens if two payments arrive at the same time? How do you avoid double-counting? (Even a comment explaining your approach counts.)
- **Error handling:** Meaningful HTTP status codes and error responses
- **Input validation:** Both client-side and server-side
- **Testing:** A few well-chosen tests matter more than 100% coverage. Show us what you'd test first and why.
- **Code organization:** Modular, readable, and maintainable structure

---

## Technical Guidelines

- Your application doesn't have to read `seed-data.json` directly — use it to initialize your database via a SQL script or migration
- Structure your application and components in a modular, reusable way
- Commit code with useful, informative commit messages
- You can use any supporting libraries you'd like
- Styling is up to you — CSS, SCSS, Tailwind, Bootstrap, etc.
- You decide the best UI/UX — use your imagination
- While anything beyond the minimum requirements might impress us, make sure you complete the base requirements first and deliver on time

---

## Seed Data

See `seed-data.json` for sample customers, invoices, and payments to populate your database.

---

## Submission

1. Create a **public repo** on GitHub
2. Implement your solution and commit your work
3. Include a brief `SETUP.md` or section in your README explaining how to run the application locally
4. Reply to the email thread by the deadline provided, with a link to your repository

---

## Questions?

Please don't hesitate to reach out if anything is unclear. We'd rather you ask than guess.
