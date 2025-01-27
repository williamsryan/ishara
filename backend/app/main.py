from fastapi import FastAPI
from app.routes import stocks, portfolio, charts, data_streams
from app.database import init_db
from app.config import settings

app = FastAPI(
    title="Ishara Backend",
    description="FastAPI backend for Ishara platform.",
    version="1.0.0",
)

@app.on_event("startup")
def on_startup():
    """
    Tasks to perform when the app starts.
    """
    print(f"🚀 Connecting to database: {settings.DATABASE_URL}")
    init_db()  # Initialize the database

# Include routers
app.include_router(data_streams.router, prefix="/api", tags=["Data Streams"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["Stocks"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(charts.router, prefix="/api/charts", tags=["Charts"])
