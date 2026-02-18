import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.api.routes import invoices, customers
from app.db.base import Base
from app.main import app


# Test database URL (use in-memory SQLite for speed, or separate test DB)
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[invoices.get_db] = override_get_db
    app.dependency_overrides[customers.get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_customer(db_session):
    """Create a sample customer for testing"""
    from app.db.models.customer import Customer
    customer = Customer(name="Test Customer")
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def sample_invoice(db_session, sample_customer):
    """Create a sample invoice for testing"""
    from app.db.models.invoice import Invoice, InvoiceStatus
    from datetime import datetime, timezone
    
    invoice = Invoice(
        customer_id=sample_customer.id,
        amount=1000.00,
        currency="USD",
        issued_at=datetime.now(timezone.utc),
        due_at=datetime.now(timezone.utc),
        status=InvoiceStatus.PENDING
    )
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)
    return invoice


@pytest.fixture
def sample_draft_invoice(db_session, sample_customer):
    """Create a DRAFT invoice for testing post endpoint"""
    from app.db.models.invoice import Invoice, InvoiceStatus
    from datetime import datetime, timezone
    
    invoice = Invoice(
        customer_id=sample_customer.id,
        amount=500.00,
        currency="EUR",
        issued_at=datetime.now(timezone.utc),
        due_at=datetime.now(timezone.utc),
        status=InvoiceStatus.DRAFT
    )
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)
    return invoice