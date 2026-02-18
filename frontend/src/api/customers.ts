import { api } from "./client";
import type { Customer, Invoice, InvoiceStatus } from "./types";

export async function getCustomers(): Promise<Customer[]> {
  const { data } = await api.get<Customer[]>("/customers");
  return data;
}

export async function createCustomer(name: string): Promise<Customer> {
  const { data } = await api.post<Customer>("/customers", { name });
  return data;
}

export type CustomerInvoicesQuery = {
  status?: InvoiceStatus;
  from?: string;
  to?: string;
};

export async function getCustomerInvoices(customerId: number, q: CustomerInvoicesQuery): Promise<Invoice[]> {
  const { data } = await api.get<Invoice[]>(`/customers/${customerId}/invoices`, {
    params: q,
  });
  return data;
}