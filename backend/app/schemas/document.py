from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# Dữ liệu Frontend gửi lên khi tạo/sửa bài viết
class DocumentCreate(BaseModel):
    title: str
    content: Optional[str] = None

# Dữ liệu Backend trả về cho Frontend
class DocumentResponse(BaseModel):
    id: int
    title: str
    content: Optional[str]
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentInvite(BaseModel):
    email: str  # Mời qua email cho dễ
    role: str   # 'viewer' hoặc 'editor'