import type { ReactNode } from "react";
import { Link } from "react-router-dom";

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div>
      <nav className="app-nav">
        <Link to="/invoices" className="app-nav-link">
          Invoices
        </Link>
        <Link to="/invoices/new" className="app-nav-link">
          New Invoice
        </Link>
        <Link to="/customers/new" className="app-nav-link">
          New Customer
        </Link>
      </nav>
      <main style={{ padding: "16px" }}>
        {children}
      </main>
    </div>
  );
}