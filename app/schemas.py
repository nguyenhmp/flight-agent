from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, Literal # Import Optional for compatibility

class WatchCreate(BaseModel):
    origin: str = Field(min_length=3, max_length=3)
    destination: str = Field(min_length=3, max_length=3)
    departure_date: date
    pax: int = 1
    cabin: Literal["ECONOMY","PREMIUM_ECONOMY","BUSINESS","FIRST"] = "ECONOMY"
    auto_book_price: Optional[float] = None # Fixed: float | None -> Optional[float]
    confirm_price: Optional[float] = None    # Fixed: float | None -> Optional[float]
    currency: str = "USD"

class WatchOut(WatchCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class TypicalOut(BaseModel):
    origin: str
    destination: str
    departure_date: date
    p10: Optional[float] = None # Fixed: float | None -> Optional[float]
    p25: Optional[float] = None # Fixed: float | None -> Optional[float]
    p50: Optional[float] = None # Fixed: float | None -> Optional[float]
    p75: Optional[float] = None # Fixed: float | None -> Optional[float]
    currency: str = "USD"

class TickResult(BaseModel):
    watch_id: int
    action: str  # NO_ACTION | AUTO_BOOKED | NEED_CONFIRM
    price: float
    currency: str
    typical: Optional[TypicalOut] = None # Fixed: TypicalOut | None -> Optional[TypicalOut]

class AlertOut(BaseModel):
    id: int
    watch_id: int
    kind: str
    message: str
    snapshot_id: Optional[int] = None # Fixed: int | None -> Optional[int]
    created_at: datetime

class ConfirmBookIn(BaseModel):
    alert_id: int