from fastapi import FastAPI
from app.routes import stocks, portfolio, charts, data_streams
from app.database import init_db
from app.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IsharaAPI")

# Initialize FastAPI application
app = FastAPI(
    title="Ishara Backend",
    description="FastAPI backend for the Ishara platform, providing data analytics, portfolio management, and market insights.",
    version="1.0.0",
)

@app.on_event("startup")
def on_startup():
    """
    Tasks to perform when the application starts.
    """
    logger.info("🚀 Starting Ishara Backend...")
    logger.info(f"🚀 Connecting to database: {settings.DATABASE_URL}")
    init_db()  # Initialize the database

@app.on_event("shutdown")
def on_shutdown():
    """
    Tasks to perform when the application shuts down.
    """
    logger.info("🛑 Shutting down Ishara Backend...")

# Include API routes
app.include_router(data_streams.router, prefix="/api/stream", tags=["Data Streams"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["Stocks"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(charts.router, prefix="/api/charts", tags=["Charts"])
