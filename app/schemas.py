from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, Literal

class WatchCreate(BaseModel):
    origin: str = Field(min_length=3, max_length=3)
    destination: str = Field(min_length=3, max_length=3)
    departure_date: date
    pax: int = 1
    cabin: Literal["ECONOMY","PREMIUM_ECONOMY","BUSINESS","FIRST"] = "ECONOMY"
    auto_book_price: Optional[float] = None
    confirm_price: Optional[float] = None
    currency: str = "USD"

class WatchOut(WatchCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class TypicalOut(BaseModel):
    origin: str
    destination: str
    departure_date: date
    p10: float | None = None
    p25: float | None = None
    p50: float | None = None
    p75: float | None = None
    currency: str = "USD"

class TickResult(BaseModel):
    watch_id: int
    action: str  # NO_ACTION | AUTO_BOOKED | NEED_CONFIRM
    price: float
    currency: str
    typical: TypicalOut | None = None

class AlertOut(BaseModel):
    id: int
    watch_id: int
    kind: str
    message: str
    snapshot_id: int | None = None
    created_at: datetime

class ConfirmBookIn(BaseModel):
    alert_id: int
