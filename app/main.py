# app/main.py
from fastapi import FastAPI
from . import database
from .routers import users, items, bids # <-- IMPOR SEMUA ROUTER

# Inisialisasi Database
database.init_db()

app = FastAPI(
    title="BidHouse Auction API",
    description="A simple auction/bidding system built with FastAPI and SQLAlchemy."
)

# --- Registrasi Routers ---
app.include_router(users.router, prefix="/api") 
app.include_router(items.router, prefix="/api") 
app.include_router(bids.router, prefix="/api") 

@app.get("/")
def read_root():
    return {"message": "Welcome to BidHouse API. Go to /docs for the documentation."}