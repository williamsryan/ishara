from fastapi import FastAPI
from app.routes import stocks, portfolio, charts

app = FastAPI(title="Ishara Backend", description="FastAPI Backend for Ishara")

# Include routers
app.include_router(stocks.router, prefix="/api/stocks", tags=["Stocks"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(charts.router, prefix="/api/charts", tags=["Charts"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Ishara Backend!"}
    