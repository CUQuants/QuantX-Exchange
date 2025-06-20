import asyncio
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import json

from models.models import Order, Trade, Position, User, MarketData, OrderSide, OrderType, OrderStatus

class MatchingEngine:
    def __init__(self):
        self.buy_orders: List[Order] = []  # Sorted by price (highest first)
        self.sell_orders: List[Order] = []  # Sorted by price (lowest first)
        self.is_running = False
        self.connection_manager = None
        
    async def start(self, connection_manager):
        """Start the matching engine"""
        self.connection_manager = connection_manager
        self.is_running = True
        print("🔥 Matching Engine started for CQAF")
        
        # Start continuous matching loop
        asyncio.create_task(self._continuous_matching())
    
    async def stop(self):
        """Stop the matching engine"""
        self.is_running = False
        print("⏹️ Matching Engine stopped")
    
    async def add_order(self, order: Order, db: Session):
        """Add new order to the matching engine"""
        print(f"📝 New order: {order.side.value} {order.quantity} CQAF @ {order.price or 'MARKET'}")
        
        # Handle market orders immediately
        if order.order_type == OrderType.MARKET:
            await self._execute_market_order(order, db)
        else:
            # Add limit order to appropriate book
            if order.side == OrderSide.BUY:
                self.buy_orders.append(order)
                self.buy_orders.sort(key=lambda x: (-x.price, x.created_at))  # Highest price first
            else:
                self.sell_orders.append(order)
                self.sell_orders.sort(key=lambda x: (x.price, x.created_at))  # Lowest price first
            
            # Try to match immediately
            await self._match_orders(db)
    
    async def _continuous_matching(self):
        """Continuously check for matching opportunities"""
        while self.is_running:
            await asyncio.sleep(0.1)  # Check every 100ms
            # Continuous matching is handled when orders are added
    
    async def _execute_market_order(self, market_order: Order, db: Session):
        """Execute a market order against the best available prices"""
        remaining_quantity = market_order.quantity
        total_cost = 0.0
        
        if market_order.side == OrderSide.BUY:
            # Buy market order - match against sell orders (asks)
            available_sells = [order for order in self.sell_orders 
                             if order.status in [OrderStatus.PENDING, OrderStatus.PARTIAL]]
            available_sells.sort(key=lambda x: (x.price, x.created_at))
            
            for sell_order in available_sells:
                if remaining_quantity <= 0:
                    break
                
                trade_quantity = min(remaining_quantity, sell_order.remaining_quantity)
                trade_price = sell_order.price
                
                await self._execute_trade(market_order, sell_order, trade_quantity, trade_price, db)
                
                remaining_quantity -= trade_quantity
                total_cost += trade_quantity * trade_price
        
        else:
            # Sell market order - match against buy orders (bids)
            available_buys = [order for order in self.buy_orders 
                            if order.status in [OrderStatus.PENDING, OrderStatus.PARTIAL]]
            available_buys.sort(key=lambda x: (-x.price, x.created_at))
            
            for buy_order in available_buys:
                if remaining_quantity <= 0:
                    break
                
                trade_quantity = min(remaining_quantity, buy_order.remaining_quantity)
                trade_price = buy_order.price
                
                await self._execute_trade(buy_order, market_order, trade_quantity, trade_price, db)
                
                remaining_quantity -= trade_quantity
                total_cost += trade_quantity * trade_price
        
        # Update market order status
        if remaining_quantity == 0:
            market_order.status = OrderStatus.FILLED
        elif remaining_quantity < market_order.quantity:
            market_order.status = OrderStatus.PARTIAL
        
        market_order.filled_quantity = market_order.quantity - remaining_quantity
        db.commit()
        
        print(f"✅ Market order executed: {market_order.filled_quantity}/{market_order.quantity} filled")
    
    async def _match_orders(self, db: Session):
        """Match buy and sell orders"""
        trades_executed = 0
        
        while self.buy_orders and self.sell_orders:
            # Get best buy and sell orders
            best_buy = None
            best_sell = None
            
            # Find best active buy order
            for order in self.buy_orders:
                if order.status in [OrderStatus.PENDING, OrderStatus.PARTIAL]:
                    best_buy = order
                    break
            
            # Find best active sell order
            for order in self.sell_orders:
                if order.status in [OrderStatus.PENDING, OrderStatus.PARTIAL]:
                    best_sell = order
                    break
            
            if not best_buy or not best_sell:
                break
            
            # Check if orders can be matched
            if best_buy.price >= best_sell.price:
                # Determine trade price (use the order that was placed first)
                if best_buy.created_at < best_sell.created_at:
                    trade_price = best_buy.price
                else:
                    trade_price = best_sell.price
                
                # Determine trade quantity
                trade_quantity = min(best_buy.remaining_quantity, best_sell.remaining_quantity)
                
                # Execute the trade
                await self._execute_trade(best_buy, best_sell, trade_quantity, trade_price, db)
                trades_executed += 1
                
                # Remove filled orders from books
                if best_buy.is_fully_filled:
                    self.buy_orders.remove(best_buy)
                if best_sell.is_fully_filled:
                    self.sell_orders.remove(best_sell)
            else:
                # No more matches possible
                break
        
        if trades_executed > 0:
            print(f"🔄 Executed {trades_executed} trades")
    
    async def _execute_trade(self, buy_order: Order, sell_order: Order, 
                           quantity: int, price: float, db: Session):
        """Execute a trade between two orders"""
        trade_value = quantity * price
        
        print(f"💰 Trade executed: {quantity} CQAF @ ${price} (${trade_value})")
        
        # Update order fill quantities
        buy_order.filled_quantity += quantity
        sell_order.filled_quantity += quantity
        
        # Update order statuses
        if buy_order.is_fully_filled:
            buy_order.status = OrderStatus.FILLED
        else:
            buy_order.status = OrderStatus.PARTIAL
            
        if sell_order.is_fully_filled:
            sell_order.status = OrderStatus.FILLED
        else:
            sell_order.status = OrderStatus.PARTIAL
        
        # Create trade records for both users
        buy_trade = Trade(
            buy_order_id=buy_order.id,
            sell_order_id=sell_order.id,
            user_id=buy_order.user_id,
            symbol="CQAF",
            quantity=quantity,
            price=price,
            trade_value=trade_value
        )
        
        sell_trade = Trade(
            buy_order_id=buy_order.id,
            sell_order_id=sell_order.id,
            user_id=sell_order.user_id,
            symbol="CQAF",
            quantity=quantity,
            price=price,
            trade_value=trade_value
        )
        
        db.add(buy_trade)
        db.add(sell_trade)
        
        # Update user balances and positions
        await self._update_user_balance_and_position(buy_order.user_id, quantity, price, OrderSide.BUY, db)
        await self._update_user_balance_and_position(sell_order.user_id, quantity, price, OrderSide.SELL, db)
        
        # Update market data
        await self._update_market_data(price, quantity, db)
        
        db.commit()
        
        # Broadcast trade to connected clients
        await self._broadcast_trade({
            "type": "trade",
            "symbol": "CQAF",
            "price": price,
            "quantity": quantity,
            "value": trade_value,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _update_user_balance_and_position(self, user_id: int, quantity: int, 
                                              price: float, side: OrderSide, db: Session):
        """Update user's balance and position after a trade"""
        user = db.query(User).filter(User.id == user_id).first()
        position = db.query(Position).filter(
            Position.user_id == user_id,
            Position.symbol == "CQAF"
        ).first()
        
        if not position:
            position = Position(
                user_id=user_id,
                symbol="CQAF",
                quantity=0,
                average_price=0.0
            )
            db.add(position)
        
        trade_value = quantity * price
        
        if side == OrderSide.BUY:
            # Buyer: decrease balance, increase position
            user.balance -= trade_value
            
            # Update position with weighted average price
            if position.quantity > 0:
                total_cost = (position.quantity * position.average_price) + trade_value
                total_quantity = position.quantity + quantity
                position.average_price = total_cost / total_quantity
            else:
                position.average_price = price
            
            position.quantity += quantity
            
        else:
            # Seller: increase balance, decrease position
            user.balance += trade_value
            position.quantity -= quantity
            
            # Calculate realized P&L
            if position.average_price > 0:
                realized_pnl = (price - position.average_price) * quantity
                position.realized_pnl += realized_pnl
        
        # Update unrealized P&L (will be calculated with current market price)
        # This would be done in a separate process with live market data
    
    async def _update_market_data(self, price: float, volume: int, db: Session):
        """Update market data with new trade information"""
        market_data = db.query(MarketData).filter(MarketData.symbol == "CQAF").first()
        
        if market_data:
            market_data.last_price = price
            market_data.volume += volume
            market_data.high_price = max(market_data.high_price, price)
            market_data.low_price = min(market_data.low_price, price)
            market_data.timestamp = datetime.utcnow()
            
            # Update bid/ask based on current order book
            best_bid = max([order.price for order in self.buy_orders 
                           if order.status in [OrderStatus.PENDING, OrderStatus.PARTIAL]], default=None)
            best_ask = min([order.price for order in self.sell_orders 
                           if order.status in [OrderStatus.PENDING, OrderStatus.PARTIAL]], default=None)
            
            market_data.bid_price = best_bid
            market_data.ask_price = best_ask
        
        db.commit()
    
    async def _broadcast_trade(self, trade_data: dict):
        """Broadcast trade information to connected WebSocket clients"""
        if self.connection_manager:
            await self.connection_manager.broadcast(trade_data)
    
    def get_order_book_snapshot(self) -> Dict:
        """Get current order book snapshot"""
        active_buys = [order for order in self.buy_orders 
                      if order.status in [OrderStatus.PENDING, OrderStatus.PARTIAL]]
        active_sells = [order for order in self.sell_orders 
                       if order.status in [OrderStatus.PENDING, OrderStatus.PARTIAL]]
        
        return {
            "symbol": "CQAF",
            "bids": [(order.price, order.remaining_quantity) for order in active_buys[:10]],
            "asks": [(order.price, order.remaining_quantity) for order in active_sells[:10]],
            "timestamp": datetime.utcnow().isoformat()
        }