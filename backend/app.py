from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
from datetime import datetime
from typing import List, Optional
import uvicorn

from models.database import init_db, get_db
from models.models import User, Order, Trade, Position, MarketData
from api.auth import router as auth_router
from api.market_data import router as market_data_router
from api.account import router as account_router
from api.trading import router as trading_router, MatchingEngineSingleton, engine_singleton as trading_engine_singleton
from matching_engine.engine import MatchingEngine
from websocket_manager import ConnectionManager

# Global instances
connection_manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    print("🚀 CU Quants Exchange started!")
    print("📊 Trading CQAF (CU Quants Attendance Futures)")
    
    # Start matching engine
    matching_engine_instance = MatchingEngine()
    
    # Set up singleton for trading API
    global trading_engine_singleton
    trading_engine_singleton = MatchingEngineSingleton(matching_engine_instance)
    
    # Pass connection manager to the engine
    asyncio.create_task(matching_engine_instance.start(connection_manager))
    
    yield
    
    # Shutdown
    print("💤 Exchange shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="CU Quants Exchange",
    description="Trading platform for CQAF (CU Quants Attendance Futures)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize API routers
auth_api = AuthAPI()
trading_api = TradingAPI(matching_engine_instance)
market_data_api = MarketDataAPI()

# Include API routes
app.include_router(auth_router, prefix="/api")
app.include_router(market_data_router, prefix="/api")
app.include_router(account_router, prefix="/api")
app.include_router(trading_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Welcome to CU Quants Exchange",
        "symbol": "CQAF",
        "description": "CU Quants Attendance Futures",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "matching_engine": "running",
        "connections": len(connection_manager.active_connections)
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, symbol: str = "CQAF"):
    await connection_manager.connect(websocket)
    try:
        while True:
            # The server will push updates; this loop keeps the connection open.
            # In a more advanced implementation, this could handle client messages
            # for subscriptions to different channels (e.g., trades, orderbook).
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )