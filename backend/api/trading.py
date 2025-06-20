from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from models.database import get_db
from models.models import User, Order, OrderSide, OrderType, OrderStatus
from api.auth import get_current_user
from matching_engine.engine import MatchingEngine

# Pydantic Models
class CreateOrderRequest(BaseModel):
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: Optional[float] = None  # Price is optional for market orders

class OrderResponse(BaseModel):
    id: int
    status: str
    
    class Config:
        orm_mode = True

class CancelOrderResponse(BaseModel):
    order_id: int
    status: str

# This is a bit of a workaround to allow passing the matching engine
# instance to the router, as FastAPI dependencies are typically singletons
# or created per request.
class MatchingEngineSingleton:
    def __init__(self, engine: MatchingEngine):
        self.engine = engine

engine_singleton = None

def get_matching_engine() -> MatchingEngine:
    if engine_singleton is None:
        raise RuntimeError("Matching engine is not initialized.")
    return engine_singleton.engine

router = APIRouter(
    prefix="/trading",
    tags=["trading"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, summary="Create a New Order")
async def create_order(
    order_req: CreateOrderRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    matching_engine: MatchingEngine = Depends(get_matching_engine)
):
    """
    Creates a new order. For LIMIT orders, a price must be specified.
    """
    if order_req.order_type == OrderType.LIMIT and order_req.price is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Price is required for LIMIT orders.")

    if order_req.quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be positive.")

    # Balance check
    if order_req.side == OrderSide.BUY:
        cost = order_req.quantity * order_req.price if order_req.order_type == OrderType.LIMIT else 0
        if current_user.balance < cost:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance.")
    
    new_order = Order(
        user_id=current_user.id,
        symbol=order_req.symbol.upper(),
        side=order_req.side,
        order_type=order_req.order_type,
        quantity=order_req.quantity,
        price=order_req.price,
        status=OrderStatus.PENDING
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Add order to matching engine
    await matching_engine.add_order(new_order, db)
    db.refresh(new_order) # Refresh to get status updates from matching engine

    return new_order

@router.delete("/orders/{order_id}", response_model=CancelOrderResponse, summary="Cancel an Order")
def cancel_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Cancels an open order.
    """
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    cancellable_statuses = [OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED, OrderStatus.PENDING]
    if order.status not in cancellable_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Order is in '{order.status.value}' state and cannot be canceled.")

    order.status = OrderStatus.CANCELLED
    db.commit()

    return CancelOrderResponse(order_id=order_id, status="canceled")