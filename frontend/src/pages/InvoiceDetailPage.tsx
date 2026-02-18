import { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getInvoice, addPayment, postInvoice, voidInvoice, deleteInvoice } from "../api/invoices";
import { getCustomers } from "../api/customers";
import type { PaymentCreate } from "../api/types";
import StatusBadge from "../components/StatusBadge";
import { formatCurrency, formatDate } from "../utils/format";

export default function InvoiceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [paymentAmount, setPaymentAmount] = useState<string>("");
  const [paymentError, setPaymentError] = useState<string>("");
  const [actionError, setActionError] = useState<string>("");

  const invoiceId = Number(id);

  // Fetch invoice
  const { data: invoice, isLoading, error } = useQuery({
    queryKey: ["invoice", invoiceId],
    queryFn: () => getInvoice(invoiceId),
    enabled: !!invoiceId,
  });

  // Fetch customers for name lookup
  const { data: customers = [] } = useQuery({
    queryKey: ["customers"],
    queryFn: getCustomers,
  });

  // Payment mutation
  const paymentMutation = useMutation({
    mutationFn: (payload: PaymentCreate) => addPayment(invoiceId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invoice", invoiceId] });
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
      setPaymentAmount("");
      setPaymentError("");
    },
    onError: (err: any) => {
      setPaymentError(err.response?.data?.detail || err.message || "Failed to record payment");
    },
  });

  // Post invoice (DRAFT → PENDING)
  const postMutation = useMutation({
    mutationFn: () => postInvoice(invoiceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invoice", invoiceId] });
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
      setActionError("");
    },
    onError: (err: any) => {
      setActionError(err.response?.data?.detail || err.message || "Failed to post invoice");
    },
  });

  // Void invoice (PENDING → VOID)
  const voidMutation = useMutation({
    mutationFn: () => voidInvoice(invoiceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invoice", invoiceId] });
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
      setActionError("");
    },
    onError: (err: any) => {
      setActionError(err.response?.data?.detail || err.message || "Failed to cancel invoice");
    },
  });

  // Delete draft invoice (removed from DB)
  const deleteMutation = useMutation({
    mutationFn: () => deleteInvoice(invoiceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
      navigate("/invoices");
    },
    onError: (err: any) => {
      setActionError(err.response?.data?.detail || err.message || "Failed to delete invoice");
    },
  });

  const customerMap = new Map(customers.map((c) => [c.id, c.name]));
  const customerName = invoice ? customerMap.get(invoice.customer_id) : null;

  // Calculate totals
  const totalPaid =
    invoice?.payments.reduce((sum, p) => sum + parseFloat(p.amount), 0) || 0;
  const remainingBalance =
    invoice ? parseFloat(invoice.amount) - totalPaid : 0;
  const canAcceptPayment =
    invoice && invoice.status === "PENDING";

  const handlePaymentSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPaymentError("");

    const amount = parseFloat(paymentAmount);
    if (isNaN(amount) || amount <= 0) {
      setPaymentError("Payment amount must be positive");
      return;
    }

    if (amount > remainingBalance) {
      setPaymentError(`Payment amount exceeds remaining balance of ${formatCurrency(remainingBalance.toString(), invoice!.currency)}`);
      return;
    }

    paymentMutation.mutate({ amount: paymentAmount });
  };

  if (isLoading) {
    return (
      <div style={{ padding: "24px", maxWidth: "1000px", margin: "0 auto" }}>
        <div className="loading-state">
          <span className="loading-spinner" style={{ display: "block", margin: "0 auto 12px" }} />
          Loading invoice...
        </div>
      </div>
    );
  }
  if (error) {
    return (
      <div style={{ padding: "24px", maxWidth: "1000px", margin: "0 auto" }}>
        <div style={{ padding: "16px", backgroundColor: "#fee2e2", color: "#991b1b", borderRadius: "8px" }}>
          Error loading invoice
        </div>
      </div>
    );
  }
  if (!invoice) {
    return (
      <div style={{ padding: "24px", maxWidth: "1000px", margin: "0 auto" }}>
        <div className="empty-state">Invoice not found</div>
      </div>
    );
  }

  return (
    <div style={{ padding: "24px", maxWidth: "1000px", margin: "0 auto" }}>
      <Link to="/invoices" className="app-link" style={{ marginBottom: "16px", display: "inline-block" }}>
        ← Back to Invoices
      </Link>

      <div className="app-card" style={{ marginTop: "16px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "24px" }}>
          <div>
            <h1 className="page-title">Invoice #{invoice.id}</h1>
            <p style={{ margin: 0, color: "#6b7280" }}>Customer: {customerName || `Customer ${invoice.customer_id}`}</p>
          </div>
          <StatusBadge status={invoice.status} />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px", marginBottom: "24px" }}>
          <div>
            <h3 style={{ fontSize: "14px", fontWeight: "600", marginBottom: "8px", color: "#6b7280" }}>Amount</h3>
            <p style={{ fontSize: "24px", fontWeight: "700", margin: 0 }}>{formatCurrency(invoice.amount, invoice.currency)}</p>
          </div>
          <div>
            <h3 style={{ fontSize: "14px", fontWeight: "600", marginBottom: "8px", color: "#6b7280" }}>Remaining Balance</h3>
            <p style={{ fontSize: "24px", fontWeight: "700", margin: 0, color: remainingBalance > 0 ? "#ef4444" : "#10b981" }}>
              {formatCurrency(remainingBalance.toString(), invoice.currency)}
            </p>
          </div>
          <div>
            <h3 style={{ fontSize: "14px", fontWeight: "600", marginBottom: "8px", color: "#6b7280" }}>Issued</h3>
            <p style={{ margin: 0 }}>{formatDate(invoice.issued_at)}</p>
          </div>
          <div>
            <h3 style={{ fontSize: "14px", fontWeight: "600", marginBottom: "8px", color: "#6b7280" }}>Due</h3>
            <p style={{ margin: 0 }}>{formatDate(invoice.due_at)}</p>
          </div>
        </div>


        {/* Payment Form */}
        {canAcceptPayment && (
          <div style={{ borderTop: "1px solid #e5e7eb", paddingTop: "24px", marginTop: "24px" }}>
            <h2 style={{ fontSize: "18px", fontWeight: "600", marginBottom: "16px" }}>Record Payment</h2>
            <form onSubmit={handlePaymentSubmit}>
              <div style={{ display: "flex", gap: "50px", alignItems: "end" }}>
                <div style={{ width: "300px" }}>
                  <label style={{ display: "block", marginBottom: "4px", fontSize: "14px", fontWeight: "500" }}>
                    Amount ({invoice.currency})
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    max={remainingBalance}
                    value={paymentAmount}
                    onChange={(e) => setPaymentAmount(e.target.value)}
                    placeholder={`Max: ${formatCurrency(remainingBalance.toString(), invoice.currency)}`}
                    style={{
                      width: "100%",
                      padding: "8px 12px",
                      borderRadius: "6px",
                      border: "1px solid #d1d5db",
                      fontSize: "16px",
                    }}
                    required
                  />
                </div>
                <div style={{ display: "flex", alignItems: "end" }}>
                  <button
                    type="submit"
                    className="btn-success"
                    disabled={paymentMutation.isPending}
                  >
                    {paymentMutation.isPending ? "Recording..." : "Record Payment"}
                  </button>
                </div>
              </div>
              {paymentError && (
                <div style={{ marginTop: "8px", padding: "8px", backgroundColor: "#fee2e2", color: "#991b1b", borderRadius: "6px", fontSize: "14px" }}>
                  {paymentError}
                </div>
              )}
            </form>
          </div>
        )}
        

        {invoice.status === "DRAFT" && (
          <div style={{ marginTop: "24px", padding: "12px", backgroundColor: "#fef3c7", borderRadius: "6px", color: "#92400e" }}>
            Drafts cannot accept payments before being posted. Use &quot;Send for payment&quot; to post this invoice.
          </div>
        )}
        {!canAcceptPayment && invoice.status !== "DRAFT" && (
          <div style={{ marginTop: "24px", padding: "12px", backgroundColor: "#f3f4f6", borderRadius: "6px", color: "#6b7280" }}>
            This invoice cannot accept new payments (Status: {invoice.status})
          </div>
        )}

        {/* Action buttons: DRAFT = Send for payment / Delete draft; PENDING = Cancel invoice */}
        {(invoice.status === "DRAFT" || invoice.status === "PENDING") && (
          <div style={{ borderTop: "1px solid #e5e7eb", paddingTop: "24px", marginTop: "24px" }}>
            <div style={{ display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
              {invoice.status === "DRAFT" && (
                <>
                  <button
                    type="button"
                    className="btn-primary"
                    onClick={() => { setActionError(""); postMutation.mutate(); }}
                    disabled={postMutation.isPending}
                  >
                    {postMutation.isPending ? "Posting..." : "Send for payment"}
                  </button>
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() => {
                      if (window.confirm("Delete this draft invoice? This cannot be undone.")) {
                        setActionError("");
                        deleteMutation.mutate();
                      }
                    }}
                    disabled={deleteMutation.isPending}
                  >
                    {deleteMutation.isPending ? "Deleting..." : "Delete draft"}
                  </button>
                </>
              )}
              {invoice.status === "PENDING" && (
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => { setActionError(""); voidMutation.mutate(); }}
                  disabled={voidMutation.isPending}
                >
                  {voidMutation.isPending ? "Cancelling..." : "Cancel invoice"}
                </button>
              )}
            </div>
            {actionError && (
              <div style={{ marginTop: "12px", padding: "8px", backgroundColor: "#fee2e2", color: "#991b1b", borderRadius: "6px", fontSize: "14px" }}>
                {actionError}
              </div>
            )}
          </div>
        )}

        {/* Payments List */}
        <div style={{ borderTop: "1px solid #e5e7eb", paddingTop: "24px", marginTop: "24px" }}>
          <h2 style={{ fontSize: "18px", fontWeight: "600", marginBottom: "16px" }}>Payment History</h2>
          {invoice.payments.length === 0 ? (
            <p className="empty-state" style={{ margin: 0 }}>No payments recorded</p>
          ) : (
            <div className="app-table-wrapper" style={{ marginTop: "8px" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ backgroundColor: "#f9fafb" }}>
                  <th style={{ padding: "12px", textAlign: "left", fontWeight: "600", fontSize: "14px" }}>Date</th>
                  <th style={{ padding: "12px", textAlign: "right", fontWeight: "600", fontSize: "14px" }}>Amount</th>
                </tr>
              </thead>
              <tbody>
                {invoice.payments.map((payment) => (
                  <tr key={payment.id} style={{ borderTop: "1px solid #e5e7eb" }}>
                    <td style={{ padding: "12px" }}>{formatDate(payment.paid_at)}</td>
                    <td style={{ padding: "12px", textAlign: "right", fontWeight: "500" }}>
                      {formatCurrency(payment.amount, invoice.currency)}
                    </td>
                  </tr>
                ))}
                <tr style={{ borderTop: "2px solid #e5e7eb", fontWeight: "600" }}>
                  <td style={{ padding: "12px" }}>Total Paid</td>
                  <td style={{ padding: "12px", textAlign: "right" }}>{formatCurrency(totalPaid.toString(), invoice.currency)}</td>
                </tr>
              </tbody>
            </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}