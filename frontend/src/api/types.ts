export type InvoiceStatus = "DRAFT" | "PENDING" | "PAID" | "VOID";

export type Payment = {
  id: number;
  invoice_id: number;
  amount: string;     // backend returns Decimal/Numeric; treat as string
  paid_at: string;    // ISO timestamp
};

export type Invoice = {
  id: number;
  customer_id: number;
  amount: string;
  currency: string;
  issued_at: string;
  due_at: string;
  status: InvoiceStatus;
  payments: Payment[];
  // If you add it on backend, this becomes easy:
  // customer?: { id: number; name: string };
};

export type InvoiceCreate = {
  customer_id: number;
  amount: string;
  currency: string;
  issued_at: string;
  due_at: string;
  status?: InvoiceStatus;
};

export type PaymentCreate = {
  amount: string;
  paid_at?: string;
};

export type Customer = { id: number; name: string };