from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from datetime import datetime, timedelta
import jwt

from models.database import get_db
from models.models import User

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    api_key: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    balance: float
    is_admin: bool
    created_at: datetime

class AuthAPI:
    def __init__(self):
        self.router = APIRouter()
        self.security = HTTPBearer()
        self.SECRET_KEY = "cu-quants-exchange-secret-key-change-in-production"
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        # Register routes
        self.router.post("/register", response_model=UserResponse)(self.register)
        self.router.post("/login", response_model=Token)(self.login)
        self.router.get("/me", response_model=UserResponse)(self.get_current_user_info)
        self.router.post("/refresh-api-key")(self.refresh_api_key)

    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        return f"cqaf_{secrets.token_urlsafe(32)}"

    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    async def register(self, user_data: UserCreate, db: Session = Depends(get_db)):
        """Register a new user"""
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | 
            (User.email == user_data.email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Create new user
        hashed_password = generate_password_hash(user_data.password)
        api_key = self.generate_api_key()
        
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            api_key=api_key,
            balance=1000.0  # Starting balance for CQAF trading
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user

    async def login(self, login_data: UserLogin, db: Session = Depends(get_db)):
        """Authenticate user and return token"""
        user = db.query(User).filter(User.username == login_data.username).first()
        
        if not user or not check_password_hash(user.password_hash, login_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "api_key": user.api_key
        }

    async def get_current_user(self, 
                              credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
                              db: Session = Depends(get_db)) -> User:
        """Get current user from token or API key"""
        
        token = credentials.credentials
        
        # Try API key first
        if token.startswith("cqaf_"):
            user = db.query(User).filter(User.api_key == token).first()
            if user:
                return user
        
        # Try JWT token
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    async def get_current_user_info(self, current_user: User = Depends(get_current_user)):
        """Get current user information"""
        return current_user

    async def refresh_api_key(self, 
                             current_user: User = Depends(get_current_user),
                             db: Session = Depends(get_db)):
        """Generate a new API key for the user"""
        new_api_key = self.generate_api_key()
        current_user.api_key = new_api_key
        db.commit()
        
        return {"api_key": new_api_key, "message": "API key refreshed successfully"}