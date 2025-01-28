from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import stocks, options, portfolio, charts, data_streams, tasks
from app.database import init_db
from app.config import settings
from app.services.streaming_service import start_streaming
from contextlib import asynccontextmanager
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IsharaAPI")

# Initialize FastAPI application
app = FastAPI(
    title="Ishara Backend",
    description="FastAPI backend for the Ishara platform, providing data analytics, portfolio management, and market insights.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Streaming task handle
streaming_task = None

# Default tickers and subreddits
DEFAULT_TICKERS = [
    "PG", "ACHR", "LUNR", "RKLB", "SNOW",
    "RGTI", "QBTS", "QUBT", "MSTR", "PLTR", "PL", "KULR", "SPY", "QQQ"
]
DEFAULT_SUBREDDITS = ["stocks", "investing", "wallstreetbets"]

@app.on_event("startup")
async def on_startup():
    """
    Tasks to perform when the application starts.
    """
    global streaming_task
    logger.info("🚀 Starting Ishara Backend...")
    logger.info("🚀 Connecting to database...")
    init_db()  # Initialize the database

    # Start the streaming service as an asyncio task
    # logger.info("🚀 Starting streaming service...")
    # streaming_task = asyncio.create_task(start_streaming(DEFAULT_TICKERS))
    # logger.info("🚀 Streaming service started.")

@app.on_event("shutdown")
async def on_shutdown():
    """
    Tasks to perform when the application shuts down.
    """
    global streaming_task
    logger.info("🛑 Shutting down Ishara Backend...")

    # Stop the streaming task gracefully
    if streaming_task:
        logger.info("🛑 Stopping streaming service...")
        streaming_task.cancel()
        try:
            await streaming_task
            logger.info("🛑 Streaming service stopped.")
        except asyncio.CancelledError:
            logger.info("🛑 Streaming service canceled.")

# Include API routes
# app.include_router(data_streams.router, prefix="/api/streams", tags=["Streams"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(stocks.router, prefix="/api", tags=["Stocks"])
app.include_router(options.router, prefix="/api", tags=["Options"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(charts.router, prefix="/api/charts", tags=["Charts"])
