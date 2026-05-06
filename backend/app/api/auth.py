import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.models.otp import OTP # Đảm bảo đã import Model OTP
from app.schemas.user import UserCreate, UserResponse
from app.services.email_service import send_otp_email

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # 1. Kiểm tra xem email đã tồn tại chưa
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email này đã được đăng ký.")
    
    # 2. Băm mật khẩu
    hashed_password = get_password_hash(user_in.password)
    
    # 3. Tạo User mới và lưu vào DB
    new_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm), db: Session = Depends(get_db)):
    # 1. Tìm user trong DB
    # Lưu ý: OAuth2PasswordRequestForm mặc định gọi trường tài khoản là 'username', 
    # nhưng chúng ta quy ước người dùng sẽ nhập email vào trường đó.
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # 2. Kiểm tra mật khẩu
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Tạo JWT Token
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    # 1. Kiểm tra user có tồn tại không
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email không tồn tại")

    # 2. Tạo OTP 6 số
    otp_code = str(random.randint(100000, 999999))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    # 3. Lưu vào DB (hoặc update nếu đã có yêu cầu trước đó)
    db_otp = OTP(email=email, otp_code=otp_code, expires_at=expires_at)
    db.add(db_otp)
    db.commit()

    # 4. Gửi Email
    await send_otp_email(email, otp_code)
    
    return {"message": "Mã OTP đã được gửi vào email của bạn"}

# API 2: Xác thực OTP và đặt mật khẩu mới
@router.post("/reset-password")
def reset_password(email: str, otp: str, new_password: str, db: Session = Depends(get_db)):
    # 1. Kiểm tra OTP mới nhất
    db_otp = db.query(OTP).filter(OTP.email == email, OTP.otp_code == otp).order_by(OTP.id.desc()).first()
    
    if not db_otp or db_otp.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Mã OTP không hợp lệ hoặc đã hết hạn")

    # 2. Cập nhật mật khẩu mới cho User
    user = db.query(User).filter(User.email == email).first()
    user.hashed_password = get_password_hash(new_password)
    
    # 3. Xóa OTP sau khi dùng xong (tùy chọn)
    db.delete(db_otp)
    
    db.commit()
    return {"message": "Đặt lại mật khẩu thành công"}