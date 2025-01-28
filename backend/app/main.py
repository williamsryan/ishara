from fastapi import FastAPI
from app.routes import stocks, options, portfolio, charts, data_streams, tasks
from app.database import init_db
from app.config import settings
from app.services.streaming_service import start_streaming
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

# Streaming task handle
streaming_task = None

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
    # symbols = ["AAPL", "MSFT", "GOOGL"]  # Define symbols to stream
    # streaming_task = asyncio.create_task(start_streaming(symbols))
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
app.include_router(data_streams.router, prefix="/api/streams", tags=["Streams"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(stocks.router, prefix="/api", tags=["Stocks"])
app.include_router(options.router, prefix="/api", tags=["Options"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(charts.router, prefix="/api/charts", tags=["Charts"])
