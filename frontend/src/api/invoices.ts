import { api } from "./client";
import type { Invoice, InvoiceCreate, InvoiceDraftUpdate, Payment, PaymentCreate, InvoiceStatus } from "./types";

export async function getAllInvoices(params?: {
  status?: InvoiceStatus;
  customer_id?: number;
  from?: string;
  to?: string;
}): Promise<Invoice[]> {
  const { data } = await api.get<Invoice[]>("/invoices", { params });
  return data;
}

export async function createInvoice(payload: InvoiceCreate): Promise<Invoice> {
  const { data } = await api.post<Invoice>("/invoices", payload);
  return data;
}

export async function getInvoice(id: number): Promise<Invoice> {
  const { data } = await api.get<Invoice>(`/invoices/${id}`);
  return data;
}

export async function updateInvoice(id: number, payload: InvoiceDraftUpdate): Promise<Invoice> {
  const { data } = await api.patch<Invoice>(`/invoices/${id}`, payload);
  return data;
}

export async function postInvoice(id: number): Promise<Invoice> {
  const { data } = await api.post<Invoice>(`/invoices/${id}/post`);
  return data;
}

export async function voidInvoice(id: number): Promise<Invoice> {
  const { data } = await api.post<Invoice>(`/invoices/${id}/void`);
  return data;
}

export async function deleteInvoice(id: number): Promise<void> {
  await api.delete(`/invoices/${id}`);
}

export async function addPayment(invoiceId: number, payload: PaymentCreate): Promise<Payment> {
  const { data } = await api.post<Payment>(`/invoices/${invoiceId}/payments`, payload);
  return data;
}