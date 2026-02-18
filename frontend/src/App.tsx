import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import InvoiceListPage from "./pages/InvoiceListPage";
import InvoiceDetailPage from "./pages/InvoiceDetailPage";
import NewInvoicePage from "./pages/NewInvoicePage";
import NewCustomerPage from "./pages/NewCustomerPage";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/invoices" replace />} />
        <Route path="/invoices" element={<InvoiceListPage />} />
        <Route path="/invoices/new" element={<NewInvoicePage />} />
        <Route path="/invoices/:id" element={<InvoiceDetailPage />} />
        <Route path="/customers/new" element={<NewCustomerPage />} />
      </Routes>
    </Layout>
  );
}