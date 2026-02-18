import json
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy import select

from app.db.session import SessionLocal
from app.db.models.customer import Customer
from app.db.models.invoice import Invoice, InvoiceStatus
from app.db.models.payment import Payment


def load_seed_data():
    """Load seed data from JSON file"""
    # Get the project root directory (go up from backend/app/db/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    seed_file = project_root / "seed-data.json"
    
    if not seed_file.exists():
        raise FileNotFoundError(f"Seed data file not found: {seed_file}")
    
    with open(seed_file, "r") as f:
        return json.load(f)


def seed_customers(db, customers_data):
    """Seed customers table"""
    print("Seeding customers...")
    for customer_data in customers_data:
        # Check if customer already exists
        existing = db.scalar(select(Customer).where(Customer.id == customer_data["id"]))
        if existing:
            print(f"  Customer {customer_data['id']} already exists, skipping...")
            continue
        
        customer = Customer(
            id=customer_data["id"],
            name=customer_data["name"]
        )
        db.add(customer)
    
    db.commit()

    # Reset the sequence to the max ID + 1
    if customers_data:
        max_id = max(c["id"] for c in customers_data)
        db.execute(sa.text(f"SELECT setval('customers_id_seq', {max_id}, true)"))
        db.commit()

    print(f"  ✓ Seeded {len(customers_data)} customers")


def seed_invoices(db, invoices_data):
    """Seed invoices table"""
    print("Seeding invoices...")
    for invoice_data in invoices_data:
        # Check if invoice already exists
        existing = db.scalar(select(Invoice).where(Invoice.id == invoice_data["id"]))
        if existing:
            print(f"  Invoice {invoice_data['id']} already exists, skipping...")
            continue
        
        # Parse datetime strings (ISO format)
        issued_at = datetime.fromisoformat(invoice_data["issued_at"].replace("Z", "+00:00"))
        due_at = datetime.fromisoformat(invoice_data["due_at"].replace("Z", "+00:00"))
        
        # Convert status string to enum
        status = InvoiceStatus[invoice_data["status"]]
        
        invoice = Invoice(
            id=invoice_data["id"],
            customer_id=invoice_data["customer_id"],
            amount=Decimal(str(invoice_data["amount"])),
            currency=invoice_data["currency"],
            issued_at=issued_at,
            due_at=due_at,
            status=status
        )
        db.add(invoice)
    
    db.commit()

    # Reset the sequence to the max ID + 1
    if invoices_data:
        max_id = max(i["id"] for i in invoices_data)
        db.execute(sa.text(f"SELECT setval('invoices_id_seq', {max_id}, true)"))
        db.commit()

    print(f"  ✓ Seeded {len(invoices_data)} invoices")


def seed_payments(db, payments_data):
    """Seed payments table"""
    print("Seeding payments...")
    for payment_data in payments_data:
        # Check if payment already exists
        existing = db.scalar(select(Payment).where(Payment.id == payment_data["id"]))
        if existing:
            print(f"  Payment {payment_data['id']} already exists, skipping...")
            continue
        
        # Parse datetime string (ISO format)
        paid_at = datetime.fromisoformat(payment_data["paid_at"].replace("Z", "+00:00"))
        
        payment = Payment(
            id=payment_data["id"],
            invoice_id=payment_data["invoice_id"],
            amount=Decimal(str(payment_data["amount"])),
            paid_at=paid_at
        )
        db.add(payment)
    
    db.commit()

    # Reset the sequence to the max ID + 1
    if payments_data:
        max_id = max(p["id"] for p in payments_data)
        db.execute(sa.text(f"SELECT setval('payments_id_seq', {max_id}, true)"))
        db.commit()

    print(f"  ✓ Seeded {len(payments_data)} payments")


def clear_all_data(db):
    """Clear all existing data (optional - use with caution!)"""
    print("Clearing existing data...")
    db.query(Payment).delete()
    db.query(Invoice).delete()
    db.query(Customer).delete()
    db.commit()
    print("  ✓ Cleared all data")


def main():
    """Main seeding function"""
    print("=" * 50)
    print("Starting database seeding...")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Load seed data
        seed_data = load_seed_data()
        
        # Optionally clear existing data (uncomment if you want to reset)
        # clear_all_data(db)
        
        # Seed in order: customers -> invoices -> payments
        seed_customers(db, seed_data["customers"])
        seed_invoices(db, seed_data["invoices"])
        seed_payments(db, seed_data["payments"])
        
        print("=" * 50)
        print("✓ Database seeding completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()