from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone
from typing import Union, Optional # Import Union and Optional for Python < 3.10 compatibility
from .db import Base

class Watch(Base):
    __tablename__ = "watches"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    origin: Mapped[str] = mapped_column(String(3), index=True)
    destination: Mapped[str] = mapped_column(String(3), index=True)
    departure_date: Mapped[Date] = mapped_column(Date, index=True)
    pax: Mapped[int] = mapped_column(Integer, default=1)
    cabin: Mapped[str] = mapped_column(String(16), default="ECONOMY")
    # FIX: Use Union or Optional for compatibility
    auto_book_price: Mapped[Union[float, None]] = mapped_column(Float, nullable=True)
    confirm_price: Mapped[Union[float, None]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    price_snapshots = relationship("PriceSnapshot", back_populates="watch", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="watch", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="watch", cascade="all, delete-orphan")

class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    watch_id: Mapped[int] = mapped_column(ForeignKey("watches.id"))
    provider: Mapped[str] = mapped_column(String(32))
    total: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3))
    raw: Mapped[Union[dict, None]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    watch = relationship("Watch", back_populates="price_snapshots")

class TypicalPrice(Base):
    __tablename__ = "typical_prices"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    origin: Mapped[str] = mapped_column(String(3), index=True)
    destination: Mapped[str] = mapped_column(String(3), index=True)
    departure_date: Mapped[Date] = mapped_column(Date, index=True)
    p10: Mapped[Union[float, None]] = mapped_column(Float, nullable=True)
    p25: Mapped[Union[float, None]] = mapped_column(Float, nullable=True)
    p50: Mapped[Union[float, None]] = mapped_column(Float, nullable=True)
    p75: Mapped[Union[float, None]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    watch_id: Mapped[int] = mapped_column(ForeignKey("watches.id"))
    kind: Mapped[str] = mapped_column(String(32))  # AUTO_BOOKED | NEED_CONFIRM | INFO
    message: Mapped[str] = mapped_column(Text)
    snapshot_id: Mapped[Union[int, None]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)

    watch = relationship("Watch", back_populates="alerts")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    watch_id: Mapped[int] = mapped_column(ForeignKey("watches.id"))
    provider: Mapped[str] = mapped_column(String(32), default="duffel")
    provider_order_id: Mapped[Union[str, None]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="created")  # created | booked | failed
    amount: Mapped[Union[float, None]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    hold_expires_at: Mapped[Union[datetime, None]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    watch = relationship("Watch", back_populates="orders")
