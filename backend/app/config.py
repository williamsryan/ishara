from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str 
    ALPACA_WS_URL: str

    DEBUG: bool = True
    APP_NAME: str = "Ishara Backend"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Yahoo Finance
    YAHOO_API_KEY: str = "your_yahoo_api_key_here" 

    # Alpaca
    ALPACA_API_KEY: str
    ALPACA_SECRET_KEY: str
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"
    ALPACA_STREAM_URL: str = "wss://stream.data.alpaca.markets/v2/iex"

    # General Settings
    DEBUG: bool = False

    class Config:
        env_file = ".env"

# Instantiate the settings object
settings = Settings()
