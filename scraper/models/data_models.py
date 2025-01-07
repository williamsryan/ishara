from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FinancialData(BaseModel):
    source: str
    symbol: Optional[str]
    headline: str
    summary: Optional[str]
    sentiment: Optional[str]
    publish_date: datetime
    