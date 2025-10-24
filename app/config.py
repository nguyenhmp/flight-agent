from pydantic import BaseModel
import os
from typing import Optional

class Settings(BaseModel):
    timezone: str = os.getenv("TIMEZONE", "America/Los_Angeles")
    amadeus_client_id: Optional[str] = os.getenv("AMADEUS_CLIENT_ID")
    amadeus_client_secret: Optional[str] = os.getenv("AMADEUS_CLIENT_SECRET")
    duffel_access_token: Optional[str] = os.getenv("DUFFEL_ACCESS_TOKEN")

settings = Settings()