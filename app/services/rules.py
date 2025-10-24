from typing import Optional

def evaluate_rules(price: float, currency: str, auto_book_price: Optional[float], confirm_price: Optional[float], typical: Optional[dict]):
    """Return 'AUTO', 'CONFIRM', or 'NONE' based on thresholds and typicals (p25/p50)."""
    # Priority: explicit auto_book threshold
    if auto_book_price is not None and price <= auto_book_price:
        return "AUTO"
    # If typicals available, treat p25 as 'great deal', p50 as 'fair'
    if typical:
        p25 = typical.get("p25")
        p50 = typical.get("p50")
        if p25 and price <= p25 * 0.98:
            return "AUTO"
        if p50 and price <= p50:
            return "CONFIRM"
    # Explicit confirm threshold
    if confirm_price is not None and price <= confirm_price:
        return "CONFIRM"
    return "NONE"