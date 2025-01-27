from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@db:5432/ishara_db"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Yahoo Finance
    YAHOO_API_KEY: str = "your_yahoo_api_key_here" 

    # Alpaca
    ALPACA_API_KEY: str
    ALPACA_SECRET_KEY: str
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"

    # General Settings
    DEBUG: bool = False

    class Config:
        env_file = ".env"  # Specify where to load environment variables from

# Instantiate the settings object
settings = Settings()
