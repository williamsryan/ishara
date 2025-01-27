from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@db:5432/ishara_db"
    ALPACA_API_KEY: str
    ALPACA_SECRET_KEY: str
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"
    REDIS_URL: str = "redis://redis:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()
