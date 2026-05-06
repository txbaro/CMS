from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=True) # Lưu trữ nội dung văn bản (định dạng HTML hoặc JSON của Tiptap)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Khóa ngoại trỏ đến User
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Quan hệ (Relationship) giúp SQLAlchemy lấy dữ liệu dễ dàng hơn
    owner = relationship("User")