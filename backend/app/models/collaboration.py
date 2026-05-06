from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from app.core.database import Base


class DocumentCollaboration(Base):
    __tablename__ = "document_collaborations"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Quyền hạn: 'viewer' (chỉ xem) hoặc 'editor' (được sửa)
    role = Column(String, nullable=False) 
    
    status = Column(String, default="pending", nullable=False)
    
    # Đảm bảo 1 user chỉ được mời 1 lần vào 1 bài viết
    __table_args__ = (UniqueConstraint('document_id', 'user_id', name='_document_user_uc'),)