import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createCustomer } from "../api/customers";

export default function NewCustomerPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [name, setName] = useState<string>("");
  const [error, setError] = useState<string>("");

  const createMutation = useMutation({
    mutationFn: createCustomer,
    onSuccess: () => {
      // Invalidate customers query to refresh the list
      queryClient.invalidateQueries({ queryKey: ["customers"] });
      navigate("/invoices/new");
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || err.message || "Failed to create customer");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!name.trim()) {
      setError("Customer name is required");
      return;
    }

    if (name.length > 255) {
      setError("Customer name must be 255 characters or less");
      return;
    }

    createMutation.mutate(name.trim());
  };

  return (
    <div style={{ padding: "24px", maxWidth: "600px", margin: "0 auto" }}>
      <h1 className="page-title" style={{ marginBottom: "24px" }}>Create New Customer</h1>

      <form onSubmit={handleSubmit} className="app-card">
        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "6px", fontWeight: "500" }}>
            Customer Name <span style={{ color: "red" }}>*</span>
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter customer name"
            maxLength={255}
            style={{
              width: "100%",
              padding: "8px 12px",
              borderRadius: "6px",
              border: error ? "1px solid #ef4444" : "1px solid #d1d5db",
              fontSize: "16px",
            }}
            required
            autoFocus
          />
          {error && <div style={{ marginTop: "4px", color: "#ef4444", fontSize: "14px" }}>{error}</div>}
        </div>

        <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end" }}>
          <button type="button" className="btn-ghost" onClick={() => navigate("/invoices/new")}>
            Cancel
          </button>
          <button type="submit" className="btn-primary" disabled={createMutation.isPending}>
            {createMutation.isPending ? "Creating..." : "Create Customer"}
          </button>
        </div>
      </form>
    </div>
  );
}