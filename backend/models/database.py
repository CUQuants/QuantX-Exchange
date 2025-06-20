from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cu_quants_exchange.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def init_db():
    """Initialize database tables"""
    from models.models import User, Order, Trade, Position, MarketData, AttendanceRecord
    Base.metadata.create_all(bind=engine)
    
    # Create default admin user and initial market data
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            from werkzeug.security import generate_password_hash
            admin_user = User(
                username="admin",
                email="admin@cuquants.com",
                password_hash=generate_password_hash("admin123"),
                is_admin=True,
                balance=10000.0
            )
            db.add(admin_user)
            
        # Initialize market data for CQAF
        market_data = db.query(MarketData).filter(MarketData.symbol == "CQAF").first()
        if not market_data:
            initial_market_data = MarketData(
                symbol="CQAF",
                last_price=50.0,  # Starting price based on expected attendance
                bid_price=49.5,
                ask_price=50.5,
                volume=0,
                open_price=50.0,
                high_price=50.0,
                low_price=50.0
            )
            db.add(initial_market_data)
            
        db.commit()
        print("✅ Database initialized successfully")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        db.rollback()
    finally:
        db.close()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()