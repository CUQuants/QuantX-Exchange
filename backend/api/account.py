from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.models.database import get_db
from backend.models.models import User, Position, Trade, Order, OrderStatus
from backend.api.auth import get_current_user
from pydantic import BaseModel

# Pydantic Models for API Responses
class AccountBalanceResponse(BaseModel):
    balance: float

class PositionResponse(BaseModel):
    symbol: str
    quantity: int
    average_price: float
    unrealized_pnl: float
    
    class Config:
        orm_mode = True

class TradeHistoryResponse(BaseModel):
    symbol: str
    quantity: int
    price: float
    trade_value: float
    created_at: str

    class Config:
        orm_mode = True

class OrderHistoryResponse(BaseModel):
    symbol: str
    side: str
    order_type: str
    quantity: int
    price: Optional[float]
    filled_quantity: int
    status: str
    created_at: str

    class Config:
        orm_mode = True


router = APIRouter(
    prefix="/account",
    tags=["account"],
    dependencies=[Depends(get_current_user)] # All endpoints require authentication
)

@router.get("/balance", response_model=AccountBalanceResponse, summary="Get Account Balance")
def get_account_balance(current_user: User = Depends(get_current_user)):
    """
    Retrieves the current trading balance for the authenticated user.
    """
    return AccountBalanceResponse(balance=current_user.balance)

@router.get("/positions", response_model=List[PositionResponse], summary="Get User Positions")
def get_user_positions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieves all current positions for the authenticated user.
    """
    positions = db.query(Position).filter(Position.user_id == current_user.id).all()
    return positions

@router.get("/trades", response_model=List[TradeHistoryResponse], summary="Get User Trade History")
def get_user_trade_history(limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieves the trade history for the authenticated user.
    """
    trades = db.query(Trade).filter(Trade.user_id == current_user.id).order_by(Trade.created_at.desc()).limit(limit).all()
    return trades

@router.get("/orders", response_model=List[OrderHistoryResponse], summary="Get User Order History")
def get_user_orders(status: Optional[OrderStatus] = None, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieves the order history for the authenticated user, with an option to filter by status.
    """
    query = db.query(Order).filter(Order.user_id == current_user.id)
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.order_by(Order.created_at.desc()).limit(limit).all()
    return orders 