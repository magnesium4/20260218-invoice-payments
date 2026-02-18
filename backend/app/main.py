from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import invoices, customers

app = FastAPI(
    title="Invoice & Payments API",
    description="API for managing invoices and payments",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(invoices.router)
app.include_router(customers.router)


@app.get("/")
def root():
    return {"message": "Invoice & Payments API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}