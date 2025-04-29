from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import stocks, options, portfolio, charts, data_streams, tasks, watchlist, news, alpaca_stream
from app.database import init_db
from app.config import settings
from app.services.streaming_service import StreamingService
from contextlib import asynccontextmanager
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IsharaAPI")

# Streaming task handle
streaming_task = None

# Default tickers and subreddits
DEFAULT_TICKERS = [
    "PG", "ACHR", "LUNR", "RKLB", "SNOW",
    "RGTI", "QBTS", "QUBT", "MSTR", "PLTR", "PL", "KULR", "SPY", "QQQ"
]
DEFAULT_SUBREDDITS = ["stocks", "investing", "wallstreetbets"]

streaming_service = StreamingService(DEFAULT_TICKERS)

# Lifespan Context
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database and start streaming service
    logger.info("🚀 Starting Ishara Backend...")
    logger.info("🚀 Connecting to database...")
    init_db()  # Initialize database tables
    streaming_service.start()
    logger.info("🚀 Streaming service started.")
    yield
    # Shutdown: Stop streaming service
    logger.info("🛑 Shutting down Ishara Backend...")
    streaming_service.stop()

# Initialize FastAPI application
app = FastAPI(
    title="Ishara Backend",
    description="FastAPI backend for the Ishara platform, providing data analytics, portfolio management, and market insights.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
# app.include_router(data_streams.router, prefix="/api/streams", tags=["Streams"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["Stocks"])
app.include_router(options.router, prefix="/api", tags=["Options"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(charts.router, prefix="/api/charts", tags=["Charts"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["Watchlist"])
app.include_router(news.router, prefix="/api/news", tags=["News"])
app.include_router(alpaca_stream.router, prefix="/api/alpaca", tags=["Alpaca"])
