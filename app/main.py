from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date, datetime, timezone
from typing import List, Optional

from .db import Base, engine, get_db
from . import models
from .schemas import WatchCreate, WatchOut, TickResult, AlertOut, ConfirmBookIn, TypicalOut
from .services.providers import get_typical_price_amadeus, search_live_offers_duffel, book_with_duffel
from .services.rules import evaluate_rules

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Flight Agent Starter", version="0.1.0")

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/watch", response_model=WatchOut)
def create_watch(payload: WatchCreate, db: Session = Depends(get_db)):
    w = models.Watch(
        origin=payload.origin.upper(),
        destination=payload.destination.upper(),
        departure_date=payload.departure_date,
        pax=payload.pax,
        cabin=payload.cabin,
        auto_book_price=payload.auto_book_price,
        confirm_price=payload.confirm_price,
        currency=payload.currency,
    )
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


@app.get("/watch", response_model=List[WatchOut])
def list_watches(db: Session = Depends(get_db)):
    return db.query(models.Watch).order_by(models.Watch.id.desc()).all()


@app.post("/tick", response_model=List[TickResult])
def run_tick(db: Session = Depends(get_db)):
    results: list[TickResult] = []
    watches = db.query(models.Watch).all()

    for w in watches:
        # 1) typical price
        tp_dict = get_typical_price_amadeus(w.origin, w.destination, w.departure_date.isoformat(), w.currency)
        # upsert local cache (simplified)
        tp = db.query(models.TypicalPrice).filter_by(origin=w.origin, destination=w.destination, departure_date=w.departure_date).first()
        if not tp:
            tp = models.TypicalPrice(origin=w.origin, destination=w.destination, departure_date=w.departure_date, currency=w.currency)
            db.add(tp)
        tp.p10 = tp_dict.get("p10")
        tp.p25 = tp_dict.get("p25")
        tp.p50 = tp_dict.get("p50")
        tp.p75 = tp_dict.get("p75")
        tp.currency = w.currency
        tp.updated_at = datetime.now(timezone.utc)

        # 2) live offers
        offers = search_live_offers_duffel(w.origin, w.destination, w.departure_date.isoformat(), w.pax, w.cabin, w.currency)
        if not offers:
            continue
        best = offers[0]

        snap = models.PriceSnapshot(watch_id=w.id, provider="duffel", total=best["total"], currency=best["currency"], raw=best["raw"])
        db.add(snap)
        db.flush()  # so we get snap.id

        # 3) rules
        action = evaluate_rules(best["total"], w.currency, w.auto_book_price, w.confirm_price, tp_dict)

        if action == "AUTO":
            # attempt booking
            order_info = book_with_duffel(best["id"], passenger_info={"type": "adult"}, payment_info={"test": True}, currency=w.currency)
            order = models.Order(
                watch_id=w.id,
                provider_order_id=order_info.get("provider_order_id"),
                status=order_info.get("status", "created"),
                amount=order_info.get("amount"),
                currency=order_info.get("currency", w.currency),
                hold_expires_at=order_info.get("hold_expires_at"),
            )
            db.add(order)
            msg = f"Auto‑booked at {best['total']} {w.currency} (vs median {tp_dict.get('p50')}). Order {order.provider_order_id}."
            alert = models.Alert(watch_id=w.id, kind="AUTO_BOOKED", message=msg, snapshot_id=snap.id)
            db.add(alert)

        elif action == "CONFIRM":
            msg = f"Price {best['total']} {w.currency} meets confirm threshold (vs median {tp_dict.get('p50')}). Offer {best['id']}."
            alert = models.Alert(watch_id=w.id, kind="NEED_CONFIRM", message=msg, snapshot_id=snap.id)
            db.add(alert)

        results.append(TickResult(
            watch_id=w.id,
            action="AUTO_BOOKED" if action=="AUTO" else ("NEED_CONFIRM" if action=="CONFIRM" else "NO_ACTION"),
            price=best["total"],
            currency=w.currency,
            typical=TypicalOut(
                origin=w.origin, destination=w.destination, departure_date=w.departure_date,
                p10=tp_dict.get("p10"), p25=tp_dict.get("p25"), p50=tp_dict.get("p50"), p75=tp_dict.get("p75"), currency=w.currency
            )
        ))

    db.commit()
    return results


@app.get("/alerts", response_model=List[AlertOut])
def list_alerts(watch_id: Optional[int] = Query(default=None), db: Session = Depends(get_db)):
    q = db.query(models.Alert)
    if watch_id is not None:
        q = q.filter(models.Alert.watch_id == watch_id)
    return q.order_by(models.Alert.id.desc()).all()


@app.post("/book/confirm", response_model=AlertOut)
def confirm_book(payload: ConfirmBookIn, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter_by(id=payload.alert_id).first()
    if not alert or alert.kind != "NEED_CONFIRM" or alert.resolved:
        raise HTTPException(status_code=404, detail="Confirmable alert not found.")
    watch = db.query(models.Watch).filter_by(id=alert.watch_id).first()
    if not watch:
        raise HTTPException(status_code=404, detail="Watch not found.")

    # In real flow you’d re‑price here and pass real passenger/payment info
    order_info = book_with_duffel(offer_id="from_alert_snapshot", passenger_info={"type": "adult"}, payment_info={"test": True}, currency=watch.currency)
    order = models.Order(
        watch_id=watch.id,
        provider_order_id=order_info.get("provider_order_id"),
        status=order_info.get("status", "created"),
        amount=order_info.get("amount"),
        currency=order_info.get("currency", watch.currency),
        hold_expires_at=order_info.get("hold_expires_at"),
    )
    db.add(order)
    alert.resolved = True
    db.commit()
    db.refresh(alert)
    return alert
