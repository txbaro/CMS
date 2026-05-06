from passlib.context import CryptContext
import jwt 
from datetime import datetime, timedelta, timezone
import random
import string
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    if len(password) > 71:
        password = password[:71]
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Đảm bảo tên biến ở đây là 'plain_password' giống như khai báo ở trên
    if len(plain_password) > 71:
        plain_password = plain_password[:71]
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Tạo chuỗi token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def generate_otp(length: int = 6):
    return ''.join(random.choices(string.digits, k=length))