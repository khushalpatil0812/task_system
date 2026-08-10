import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .database import get_db
from .models import User, Role

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/login")
SECRET = os.getenv("SECRET_KEY", "development-secret-change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
def hash_password(value: str): return pwd.hash(value)
def verify_password(value: str, hashed: str): return pwd.verify(value, hashed)
def create_token(user: User):
    expiry = datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")))
    return jwt.encode({"sub": str(user.id), "role": user.role.value, "exp": expiry}, SECRET, algorithm=ALGORITHM)
def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    try: user_id = int(jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub"))
    except (JWTError, TypeError, ValueError): raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.get(User, user_id)
    if not user: raise HTTPException(status_code=401, detail="User not found")
    return user
def admin_user(user: User = Depends(current_user)):
    if user.role != Role.admin: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
