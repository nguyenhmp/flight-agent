from datetime import datetime, timedelta, timezone
import os
import random

# Real SDKs (uncomment after adding to requirements.txt and setting keys)
# from amadeus import Client as Amadeus
# from duffel_api import Duffel

AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
DUFFEL_ACCESS_TOKEN = os.getenv("DUFFEL_ACCESS_TOKEN")

def get_typical_price_amadeus(origin: str, destination: str, departure_date: str, currency: str = "USD"):
    """Return dict with p10/p25/p50/p75 for OD+date. Uses mock if no keys."""
    if not (AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET):
        # Mock typicals: generate a believable distribution
        base = random.randint(150, 500)
        return {"p10": base*0.6, "p25": base*0.8, "p50": base*1.0, "p75": base*1.2, "currency": currency}
    # amadeus = Amadeus(client_id=AMADEUS_CLIENT_ID, client_secret=AMADEUS_CLIENT_SECRET)
    # resp = amadeus.shopping.analytics.itinerary_price_metrics.get(
    #     originLocationCode=origin, destinationLocationCode=destination, departureDate=departure_date, currencyCode=currency
    # )
    # TODO: parse quartiles from resp
    # return {"p10": ..., "p25": ..., "p50": ..., "p75": ..., "currency": currency}
    raise NotImplementedError("Wire Amadeus SDK and parse response per your plan.")

def search_live_offers_duffel(origin: str, destination: str, departure_date: str, pax: int, cabin: str, currency: str = "USD"):
    """Return a list of offers: [{id, total, currency, raw}]. Uses mock if no token."""
    if not DUFFEL_ACCESS_TOKEN:
        # Mock 3 offers around a random center
        center = random.randint(120, 520)
        offers = []
        for i, delta in enumerate([-40, 0, 35]):
            total = max(60, center + delta + random.randint(-15, 15))
            offers.append({
                "id": f"mock_{i}",
                "total": float(total),
                "currency": currency,
                "raw": {"carrier": "XX", "flight": "XX123", "legs": 1}
            })
        return sorted(offers, key=lambda x: x["total"])
    # duffel = Duffel(access_token=DUFFEL_ACCESS_TOKEN)
    # offers = duffel.offers.list(...)
    # return [{"id": o.id, "total": float(o.total_amount), "currency": o.currency, "raw": o.to_dict()} for o in offers]
    raise NotImplementedError("Wire Duffel SDK search per your plan.")

def book_with_duffel(offer_id: str, passenger_info: dict, payment_info: dict, currency: str = "USD") -> dict:
    """Attempt a booking; returns {status, provider_order_id, amount, currency, hold_expires_at}.

    Uses mock if no token; in real use, re‑price the offer and issue order.
"""
    if not DUFFEL_ACCESS_TOKEN:
        # Simulate a hold with a future expiry
        hold_expires_at = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
        return {
            "status": "booked",
            "provider_order_id": f"mock_order_{offer_id}",
            "amount": 199.99,
            "currency": currency,
            "hold_expires_at": hold_expires_at
        }
    # duffel = Duffel(access_token=DUFFEL_ACCESS_TOKEN)
    # 1) re‑price / verify availability
    # 2) create order with passengers + payment
    # return parsed order data
    raise NotImplementedError("Wire Duffel SDK order per your plan.")
