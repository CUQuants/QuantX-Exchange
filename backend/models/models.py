from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.database import Base
import enum

class OrderSide(enum.Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(enum.Enum):
    MARKET = "market"
    LIMIT = "limit"

class OrderStatus(enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    api_key = Column(String, unique=True, index=True)
    balance = Column(Float, default=1000.0)  # Starting balance
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="user")
    trades = relationship("Trade", back_populates="user")
    positions = relationship("Position", back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, default="CQAF")  # Only CQAF for now
    side = Column(Enum(OrderSide), nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=True)  # Null for market orders
    filled_quantity = Column(Integer, default=0)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    trades = relationship("Trade", back_populates="order")
    
    @property
    def remaining_quantity(self):
        return self.quantity - self.filled_quantity
    
    @property
    def is_fully_filled(self):
        return self.filled_quantity >= self.quantity

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    buy_order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    sell_order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Which user this trade affects
    symbol = Column(String, default="CQAF")
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    trade_value = Column(Float, nullable=False)  # quantity * price
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="trades")
    order = relationship("Order", back_populates="trades", foreign_keys=[buy_order_id])

class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, default="CQAF")
    quantity = Column(Integer, default=0)  # Can be negative for short positions
    average_price = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="positions")

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, default="CQAF")
    last_price = Column(Float, nullable=False)
    bid_price = Column(Float, nullable=True)
    ask_price = Column(Float, nullable=True)
    volume = Column(Integer, default=0)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())

class AttendanceRecord(Base):
    """Records actual meeting attendance for CQAF settlement"""
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_date = Column(DateTime, nullable=False)
    attendance_count = Column(Integer, nullable=False)
    meeting_type = Column(String, default="regular")  # regular, special, etc.
    notes = Column(String, nullable=True)
    is_settlement = Column(Boolean, default=False)  # If this is used for contract settlement
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

class ContractSpec(Base):
    """CQAF contract specifications"""
    __tablename__ = "contract_specs"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, default="CQAF")
    contract_size = Column(Integer, default=1)  # 1 contract = 1 attendance unit
    tick_size = Column(Float, default=0.1)  # Minimum price increment
    settlement_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    settlement_price = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())