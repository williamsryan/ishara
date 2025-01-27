from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str  # Ensure this field is explicitly defined
    ALPACA_WS_URL: str

    # Optional: Other environment variables for your app
    DEBUG: bool = False
    APP_NAME: str = "Ishara Backend"
    
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
