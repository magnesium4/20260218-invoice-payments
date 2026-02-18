import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getAllInvoices } from "../api/invoices";
import { getCustomers } from "../api/customers";
import type { InvoiceStatus } from "../api/types";
import StatusBadge from "../components/StatusBadge";
import { formatCurrency, formatDate } from "../utils/format";

export default function InvoiceListPage() {
  const [statusFilter, setStatusFilter] = useState<InvoiceStatus | "">("");
  const [customerFilter, setCustomerFilter] = useState<number | "">("");
  const [fromDate, setFromDate] = useState<string>("");
  const [toDate, setToDate] = useState<string>("");

  // Fetch customers for dropdown
  const { data: customers = [] } = useQuery({
    queryKey: ["customers"],
    queryFn: getCustomers,
  });

  // Fetch invoices with filters
  const { data: invoices = [], isLoading, error } = useQuery({
    queryKey: ["invoices", statusFilter, customerFilter, fromDate, toDate],
    queryFn: () =>
      getAllInvoices({
        status: statusFilter || undefined,
        customer_id: customerFilter || undefined,
        from: fromDate || undefined,
        to: toDate || undefined,
      }),
  });

  const customerMap = new Map(customers.map((c) => [c.id, c.name]));

  return (
    <div style={{ padding: "24px", maxWidth: "1200px", margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <h1 className="page-title">Invoices</h1>
        <Link to="/invoices/new" className="btn-primary">
          + New Invoice
        </Link>
      </div>

      {/* Filters */}
      <div
        style={{
          display: "flex",
          gap: "16px",
          flexWrap: "wrap",
          marginBottom: "24px",
          padding: "16px",
          backgroundColor: "#f9fafb",
          borderRadius: "8px",
        }}
      >
        <div>
          <label style={{ display: "block", marginBottom: "4px", fontSize: "14px", fontWeight: "500" }}>
            Customer
          </label>
          <select
            value={customerFilter}
            onChange={(e) => setCustomerFilter(e.target.value === "" ? "" : Number(e.target.value))}
            style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #d1d5db", minWidth: "200px" }}
          >
            <option value="">All Customers</option>
            {customers.map((customer) => (
              <option key={customer.id} value={customer.id}>
                {customer.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "4px", fontSize: "14px", fontWeight: "500" }}>
            Status
          </label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as InvoiceStatus | "")}
            style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #d1d5db", minWidth: "150px" }}
          >
            <option value="">All Statuses</option>
            <option value="DRAFT">DRAFT</option>
            <option value="PENDING">PENDING</option>
            <option value="PAID">PAID</option>
            <option value="VOID">VOID</option>
          </select>
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "4px", fontSize: "14px", fontWeight: "500" }}>
            From Date
          </label>
          <input
            type="date"
            value={fromDate}
            max={toDate || undefined}
            onChange={(e) => {
              const next = e.target.value;
              setFromDate(next);
              if (next && toDate && next > toDate) setToDate(next);
            }}
            style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #d1d5db" }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "4px", fontSize: "14px", fontWeight: "500" }}>
            To Date
          </label>
          <input
            type="date"
            value={toDate}
            min={fromDate || undefined}
            onChange={(e) => {
              const next = e.target.value;
              setToDate(next);
              if (next && fromDate && next < fromDate) setFromDate(next);
            }}
            style={{ padding: "6px 12px", borderRadius: "6px", border: "1px solid #d1d5db" }}
          />
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div style={{ padding: "12px", backgroundColor: "#fee2e2", color: "#991b1b", borderRadius: "6px", marginBottom: "16px" }}>
          Error loading invoices: {(error as Error).message}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="loading-state">
          <span className="loading-spinner" style={{ display: "block", margin: "0 auto 12px" }} />
          Loading invoices...
        </div>
      )}

      {/* Invoice Table */}
      {!isLoading && !error && (
        <div className="app-table-wrapper">
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ backgroundColor: "#f3f4f6" }}>
                <th style={{ padding: "12px", textAlign: "left", fontWeight: "600", fontSize: "14px" }}>Customer</th>
                <th style={{ padding: "12px", textAlign: "right", fontWeight: "600", fontSize: "14px" }}>Amount</th>
                <th style={{ padding: "12px", textAlign: "left", fontWeight: "600", fontSize: "14px" }}>Status</th>
                <th style={{ padding: "12px", textAlign: "left", fontWeight: "600", fontSize: "14px" }}>Issued</th>
                <th style={{ padding: "12px", textAlign: "left", fontWeight: "600", fontSize: "14px" }}>Due</th>
                <th style={{ padding: "12px", textAlign: "center", fontWeight: "600", fontSize: "14px" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {invoices.length === 0 ? (
                <tr>
                  <td colSpan={6} className="empty-state">
                    No invoices found
                  </td>
                </tr>
              ) : (
                invoices.map((invoice) => (
                  <tr key={invoice.id} style={{ borderTop: "1px solid #e5e7eb" }}>
                    <td style={{ padding: "12px" }}>{customerMap.get(invoice.customer_id) || `Customer ${invoice.customer_id}`}</td>
                    <td style={{ padding: "12px", textAlign: "right", fontWeight: "500" }}>
                      {formatCurrency(invoice.amount, invoice.currency)}
                    </td>
                    <td style={{ padding: "12px" }}>
                      <StatusBadge status={invoice.status} />
                    </td>
                    <td style={{ padding: "12px" }}>{formatDate(invoice.issued_at)}</td>
                    <td style={{ padding: "12px" }}>{formatDate(invoice.due_at)}</td>
                    <td style={{ padding: "12px", textAlign: "center" }}>
                      <Link to={`/invoices/${invoice.id}`} className="app-link">
                        View
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}