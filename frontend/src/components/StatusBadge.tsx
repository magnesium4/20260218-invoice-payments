import type { InvoiceStatus } from "../api/types";

interface StatusBadgeProps {
  status: InvoiceStatus;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const colors: Record<InvoiceStatus, string> = {
    DRAFT: "#6b7280",
    PENDING: "#f59e0b",
    PAID: "#10b981",
    VOID: "#ef4444",
  };

  return (
    <span
      style={{
        padding: "4px 12px",
        borderRadius: "12px",
        fontSize: "12px",
        fontWeight: "600",
        backgroundColor: `${colors[status]}20`,
        color: colors[status],
        textTransform: "uppercase",
      }}
    >
      {status}
    </span>
  );
}