from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.sql import func

from backend.models.database import get_db
from backend.models.models import MarketData, Order, Trade, AttendanceRecord, OrderSide, OrderStatus

# Pydantic models
class MarketDataResponse(BaseModel):
    symbol: str
    last_price: float
    bid_price: Optional[float]
    ask_price: Optional[float]
    volume: int
    open_price: float
    high_price: float
    low_price: float
    timestamp: datetime
    change: float
    change_percent: float

class OrderBookEntry(BaseModel):
    price: float
    quantity: int
    orders: int

class OrderBookResponse(BaseModel):
    bids: List[OrderBookEntry]
    asks: List[OrderBookEntry]

class TradeResponse(BaseModel):
    price: float
    quantity: int
    timestamp: datetime
    side: OrderSide

    class Config:
        orm_mode = True

router = APIRouter(
    prefix="/market",
    tags=["market"],
)

def create_market_data_response(md: MarketData) -> MarketDataResponse:
    """Helper function to create MarketDataResponse from MarketData model."""
    change = md.last_price - md.open_price
    change_percent = (change / md.open_price) * 100 if md.open_price != 0 else 0
    return MarketDataResponse(
        symbol=md.symbol,
        last_price=md.last_price,
        bid_price=md.bid_price,
        ask_price=md.ask_price,
        volume=md.volume,
        open_price=md.open_price,
        high_price=md.high_price,
        low_price=md.low_price,
        timestamp=md.timestamp,
        change=change,
        change_percent=change_percent,
    )

@router.get("/data", response_model=List[MarketDataResponse], summary="Get All Market Data")
def get_all_market_data(db: Session = Depends(get_db)):
    """
    Retrieves market data for all available symbols.
    """
    market_data_list = db.query(MarketData).all()
    if not market_data_list:
        return []
    return [create_market_data_response(md) for md in market_data_list]

@router.get("/data/{symbol}", response_model=MarketDataResponse, summary="Get Market Data for a Symbol")
def get_market_data_for_symbol(symbol: str, db: Session = Depends(get_db)):
    """
    Retrieves detailed market data for a specific symbol.
    """
    market_data = db.query(MarketData).filter(MarketData.symbol == symbol.upper()).first()
    if not market_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Market data for symbol '{symbol}' not found")
    return create_market_data_response(market_data)

@router.get("/orderbook/{symbol}", response_model=OrderBookResponse, summary="Get Order Book for a Symbol")
def get_order_book(symbol: str, db: Session = Depends(get_db)):
    """
    Retrieves the order book for a specific symbol, showing current bids and asks.
    """
    active_statuses = [OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]
    
    bids_query = db.query(Order.price, func.sum(Order.quantity), func.count(Order.id)).\
        filter(Order.symbol == symbol.upper(), Order.side == OrderSide.BUY, Order.status.in_(active_statuses)).\
        group_by(Order.price).order_by(desc(Order.price)).all()

    asks_query = db.query(Order.price, func.sum(Order.quantity), func.count(Order.id)).\
        filter(Order.symbol == symbol.upper(), Order.side == OrderSide.SELL, Order.status.in_(active_statuses)).\
        group_by(Order.price).order_by(Order.price).all()

    bids = [OrderBookEntry(price=p, quantity=q, orders=c) for p, q, c in bids_query]
    asks = [OrderBookEntry(price=p, quantity=q, orders=c) for p, q, c in asks_query]
    
    return OrderBookResponse(bids=bids, asks=asks)

@router.get("/trades/{symbol}", response_model=List[TradeResponse], summary="Get Recent Trades for a Symbol")
def get_recent_trades(symbol: str, limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieves the most recent trades for a specific symbol.
    """
    trades = db.query(Trade).join(Order, Trade.order_id == Order.id)\
        .filter(Order.symbol == symbol.upper())\
        .order_by(desc(Trade.timestamp))\
        .limit(limit).all()
        
    if not trades:
        return []

    return trades