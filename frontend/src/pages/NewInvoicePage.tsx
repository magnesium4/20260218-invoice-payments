import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { createInvoice } from "../api/invoices";
import { getCustomers } from "../api/customers";
import type { InvoiceCreate } from "../api/types";

export default function NewInvoicePage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<InvoiceCreate>({
    customer_id: 0,
    amount: "",
    currency: "USD",
    issued_at: new Date().toISOString().split("T")[0],
    due_at: "",
    status: "DRAFT",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const { data: customers = [], isLoading: customersLoading } = useQuery({
    queryKey: ["customers"],
    queryFn: getCustomers,
  });

  const createMutation = useMutation({
    mutationFn: createInvoice,
    onSuccess: (data) => {
      navigate(`/invoices/${data.id}`);
    },
    onError: (err: any) => {
      setErrors({ submit: err.response?.data?.detail || err.message || "Failed to create invoice" });
    },
  });

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.customer_id || formData.customer_id === 0) {
      newErrors.customer_id = "Customer is required";
    }
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      newErrors.amount = "Amount must be positive";
    }
    if (!formData.currency || formData.currency.length !== 3) {
      newErrors.currency = "Currency must be 3 characters (e.g., USD, CAD)";
    }
    if (!formData.issued_at) {
      newErrors.issued_at = "Issued date is required";
    }
    if (!formData.due_at) {
      newErrors.due_at = "Due date is required";
    }
    if (formData.issued_at && formData.due_at && formData.due_at < formData.issued_at) {
      newErrors.due_at = "Due date must be after issued date";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      createMutation.mutate({
        ...formData,
        issued_at: new Date(formData.issued_at).toISOString(),
        due_at: new Date(formData.due_at).toISOString(),
      });
    }
  };

  return (
    <div style={{ padding: "24px", maxWidth: "600px", margin: "0 auto" }}>
      <h1 style={{ marginBottom: "24px" }}>Create New Invoice</h1>

      <form onSubmit={handleSubmit} style={{ backgroundColor: "white", borderRadius: "8px", padding: "24px" }}>
        <div style={{ marginBottom: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
            <label style={{ fontWeight: "500" }}>
              Customer <span style={{ color: "red" }}>*</span>
            </label>
            <Link
              to="/customers/new"
              style={{
                fontSize: "14px",
                color: "#3b82f6",
                textDecoration: "none",
              }}
            >
              + New Customer
            </Link>
          </div>
          {customersLoading ? (
            <div>Loading customers...</div>
          ) : (
            <select
              value={formData.customer_id}
              onChange={(e) => setFormData({ ...formData, customer_id: Number(e.target.value) })}
              style={{
                width: "100%",
                padding: "8px 12px",
                borderRadius: "6px",
                border: errors.customer_id ? "1px solid #ef4444" : "1px solid #d1d5db",
              }}
              required
            >
              <option value={0}>Select a customer</option>
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.name}
                </option>
              ))}
            </select>
          )}
          {errors.customer_id && <div style={{ marginTop: "4px", color: "#ef4444", fontSize: "14px" }}>{errors.customer_id}</div>}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "16px", marginBottom: "20px" }}>
          <div>
            <label style={{ display: "block", marginBottom: "6px", fontWeight: "500" }}>
              Amount <span style={{ color: "red" }}>*</span>
            </label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              value={formData.amount}
              onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
              style={{
                width: "100%",
                padding: "8px 12px",
                borderRadius: "6px",
                border: errors.amount ? "1px solid #ef4444" : "1px solid #d1d5db",
              }}
              required
            />
            {errors.amount && <div style={{ marginTop: "4px", color: "#ef4444", fontSize: "14px" }}>{errors.amount}</div>}
          </div>

          <div>
            <label style={{ display: "block", marginBottom: "6px", fontWeight: "500" }}>
              Currency <span style={{ color: "red" }}>*</span>
            </label>
            <select
              value={formData.currency}
              onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
              style={{
                width: "100%",
                padding: "8px 12px",
                borderRadius: "6px",
                border: errors.currency ? "1px solid #ef4444" : "1px solid #d1d5db",
              }}
              required
            >
              <option value="USD">USD</option>
              <option value="CAD">CAD</option>
              <option value="EUR">EUR</option>
            </select>
            {errors.currency && <div style={{ marginTop: "4px", color: "#ef4444", fontSize: "14px" }}>{errors.currency}</div>}
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "20px" }}>
          <div>
            <label style={{ display: "block", marginBottom: "6px", fontWeight: "500" }}>
              Issued Date <span style={{ color: "red" }}>*</span>
            </label>
            <input
              type="date"
              value={formData.issued_at}
              onChange={(e) => setFormData({ ...formData, issued_at: e.target.value })}
              style={{
                width: "100%",
                padding: "8px 12px",
                borderRadius: "6px",
                border: errors.issued_at ? "1px solid #ef4444" : "1px solid #d1d5db",
              }}
              required
            />
            {errors.issued_at && <div style={{ marginTop: "4px", color: "#ef4444", fontSize: "14px" }}>{errors.issued_at}</div>}
          </div>

          <div>
            <label style={{ display: "block", marginBottom: "6px", fontWeight: "500" }}>
              Due Date <span style={{ color: "red" }}>*</span>
            </label>
            <input
              type="date"
              value={formData.due_at}
              onChange={(e) => setFormData({ ...formData, due_at: e.target.value })}
              style={{
                width: "100%",
                padding: "8px 12px",
                borderRadius: "6px",
                border: errors.due_at ? "1px solid #ef4444" : "1px solid #d1d5db",
              }}
              required
            />
            {errors.due_at && <div style={{ marginTop: "4px", color: "#ef4444", fontSize: "14px" }}>{errors.due_at}</div>}
          </div>
        </div>

        {errors.submit && (
          <div style={{ marginBottom: "20px", padding: "12px", backgroundColor: "#fee2e2", color: "#991b1b", borderRadius: "6px" }}>
            {errors.submit}
          </div>
        )}

        <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end" }}>
          <button
            type="button"
            onClick={() => navigate("/invoices")}
            style={{
              padding: "8px 24px",
              backgroundColor: "#f3f4f6",
              color: "#374151",
              border: "none",
              borderRadius: "6px",
              fontWeight: "500",
              cursor: "pointer",
            }}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={createMutation.isPending}
            style={{
              padding: "8px 24px",
              backgroundColor: "#3b82f6",
              color: "white",
              border: "none",
              borderRadius: "6px",
              fontWeight: "500",
              cursor: createMutation.isPending ? "not-allowed" : "pointer",
              opacity: createMutation.isPending ? 0.6 : 1,
            }}
          >
            {createMutation.isPending ? "Creating..." : "Create Invoice"}
          </button>
        </div>
      </form>
    </div>
  );
}