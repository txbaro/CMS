from pydantic import BaseModel, EmailStr, ConfigDict

# Dữ liệu Frontend gửi lên khi tạo tài khoản
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

# Dữ liệu Backend trả về (không bao giờ trả về password)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)