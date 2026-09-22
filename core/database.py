"""FinGuard AI - Multi-User SQLite Database Models, Password Hashing & Session Management"""

import os
import hashlib
import secrets
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "finguard_v2.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def hash_password(password: str) -> str:
    """Secure password hashing using SHA-256 with salt."""
    salt = "finguard_salt_"
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against stored hash."""
    return hash_password(password) == hashed_password


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    debts = relationship("Debt", back_populates="user", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    type = Column(String(20), nullable=False)  # "Income" or "Expense"
    category = Column(String(50), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String(255), default="")
    account = Column(String(50), default="Primary Checking")
    is_recurring = Column(Boolean, default=False)
    is_anomaly = Column(Boolean, default=False)
    anomaly_reason = Column(String(255), default="")

    user = relationship("User", back_populates="transactions")


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    category = Column(String(50), nullable=False)
    monthly_limit = Column(Float, nullable=False)
    alert_threshold_pct = Column(Float, default=85.0)

    user = relationship("User", back_populates="budgets")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(100), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    target_date = Column(DateTime, nullable=False)
    category = Column(String(50), default="Savings")

    user = relationship("User", back_populates="goals")


class Debt(Base):
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(100), nullable=False)
    principal = Column(Float, nullable=False)
    outstanding_balance = Column(Float, nullable=False)
    interest_rate_pct = Column(Float, nullable=False)
    monthly_emi = Column(Float, nullable=False)
    remaining_months = Column(Integer, default=12)

    user = relationship("User", back_populates="debts")


class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    symbol = Column(String(30), nullable=False)  # e.g. "TCS.NS"
    name = Column(String(100), nullable=False)
    asset_type = Column(String(50), default="Equity")  # Equity, Mutual Fund, Gold
    quantity = Column(Float, nullable=False)
    buy_price = Column(Float, nullable=False)
    current_price = Column(Float, default=0.0)

    user = relationship("User", back_populates="investments")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    billing_cycle = Column(String(20), default="Monthly")  # Monthly, Annual
    category = Column(String(50), default="Entertainment")
    next_billing_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="subscriptions")


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(150), nullable=False)
    due_date = Column(DateTime, nullable=False)
    amount = Column(Float, default=0.0)
    category = Column(String(50), default="Bill")
    frequency = Column(String(30), default="One-Time")
    is_completed = Column(Boolean, default=False)

    user = relationship("User", back_populates="reminders")


def init_db():
    """Initializes SQLite database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Context provider for DB sessions."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass
