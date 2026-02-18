import type { ReactNode } from "react";
import { Link } from "react-router-dom";

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div>
      <nav style={{ padding: "16px", borderBottom: "1px solid #ccc" }}>
        <Link to="/invoices" style={{ marginRight: "16px" }}>
          Invoices
        </Link>
        <Link to="/invoices/new" style={{ marginRight: "16px" }}>
          New Invoice
        </Link>
        <Link to="/customers/new">New Customer</Link>
      </nav>
      <main style={{ padding: "16px" }}>
        {children}
      </main>
    </div>
  );
}