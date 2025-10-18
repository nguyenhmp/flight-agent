from pydantic import BaseModel
import os

class Settings(BaseModel):
    timezone: str = os.getenv("TIMEZONE", "America/Los_Angeles")
    amadeus_client_id: str | None = os.getenv("AMADEUS_CLIENT_ID")
    amadeus_client_secret: str | None = os.getenv("AMADEUS_CLIENT_SECRET")
    duffel_access_token: str | None = os.getenv("DUFFEL_ACCESS_TOKEN")

settings = Settings()
