from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import or_

from app.core.database import get_db
from app.models.document import Document
from app.models.user import User
from app.models.collaboration import DocumentCollaboration
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentInvite
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/documents", tags=["Documents"])

# 1. TẠO BÀI VIẾT
@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(doc_in: DocumentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_doc = Document(title=doc_in.title, content=doc_in.content, owner_id=current_user.id)
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

# 2. MỜI NGƯỜI DÙNG
@router.post("/{doc_id}/invite")
def invite_user_to_document(doc_id: int, invite_data: DocumentInvite, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết")
    if document.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Chỉ chủ bài viết mới được cấp quyền")
    
    invited_user = db.query(User).filter(User.email == invite_data.email).first()
    if not invited_user:
        raise HTTPException(status_code=404, detail="Người dùng được mời không tồn tại")
    if invited_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Bạn không thể tự mời chính mình")
    if invite_data.role not in ["viewer", "editor"]:
        raise HTTPException(status_code=400, detail="Quyền không hợp lệ")

    existing_collab = db.query(DocumentCollaboration).filter(
        DocumentCollaboration.document_id == doc_id,
        DocumentCollaboration.user_id == invited_user.id
    ).first()

    if existing_collab:
        existing_collab.role = invite_data.role
        msg = f"Đã cập nhật quyền của {invite_data.email} thành {invite_data.role}"
    else:
        new_collab = DocumentCollaboration(document_id=doc_id, user_id=invited_user.id, role=invite_data.role)
        db.add(new_collab)
        msg = f"Đã mời {invite_data.email} tham gia với quyền {invite_data.role}"
    
    db.commit()
    return {"message": msg}

# 3. LẤY DANH SÁCH BÀI VIẾT (Của mình + Được mời)
@router.get("/", response_model=List[DocumentResponse])
def get_documents(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    collab_doc_ids = db.query(DocumentCollaboration.document_id).filter(DocumentCollaboration.user_id == current_user.id).all()
    collab_ids = [item[0] for item in collab_doc_ids]
    
    if not collab_ids:
        documents = db.query(Document).filter(Document.owner_id == current_user.id).offset(skip).limit(limit).all()
    else:
        documents = db.query(Document).filter(
            or_(Document.owner_id == current_user.id, Document.id.in_(collab_ids))
        ).offset(skip).limit(limit).all()
        
    return documents

# 4. LẤY CHI TIẾT 1 BÀI VIẾT
@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết")
    
    is_owner = document.owner_id == current_user.id

    is_collaborator = db.query(DocumentCollaboration).filter(
        DocumentCollaboration.document_id == doc_id,
        DocumentCollaboration.user_id == current_user.id,
        DocumentCollaboration.status == "accepted",
    ).first()

    if not is_owner and not is_collaborator:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem bài viết này")
    return document

# 5. CẬP NHẬT BÀI VIẾT
@router.put("/{doc_id}", response_model=DocumentResponse)
def update_document(doc_id: int, doc_in: DocumentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết")
    
    is_owner = document.owner_id == current_user.id
    collab = db.query(DocumentCollaboration).filter(
        DocumentCollaboration.document_id == doc_id,
        DocumentCollaboration.user_id == current_user.id,
        DocumentCollaboration.status == "accepted",
    ).first()

    can_edit = is_owner or (collab and collab.role == "editor")
    if not can_edit:
        raise HTTPException(status_code=403, detail="Bạn chỉ có quyền xem, không có quyền sửa bài viết này")

    document.title = doc_in.title
    document.content = doc_in.content
    db.commit()
    db.refresh(document)
    return document

# 6. XÓA BÀI VIẾT
@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết")
    
    if document.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Chỉ chủ bài viết mới được quyền xóa")

    db.delete(document)
    db.commit()
    return None

@router.post("/{doc_id}/accept")
def accept_invitation(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Tìm lời mời dành cho User này đang ở trạng thái 'pending'
    collab = db.query(DocumentCollaboration).filter(
        DocumentCollaboration.document_id == doc_id,
        DocumentCollaboration.user_id == current_user.id,
        DocumentCollaboration.status == "pending"
    ).first()

    if not collab:
        raise HTTPException(status_code=404, detail="Không tìm thấy lời mời nào đang chờ xử lý")

    # Đổi trạng thái thành 'accepted'
    collab.status = "accepted"
    db.commit()
    return {"message": "Bạn đã chấp nhận lời mời tham gia bài viết"}

@router.post("/{doc_id}/decline")
def decline_invitation(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    collab = db.query(DocumentCollaboration).filter(
        DocumentCollaboration.document_id == doc_id,
        DocumentCollaboration.user_id == current_user.id,
        DocumentCollaboration.status == "pending"
    ).first()

    if not collab:
        raise HTTPException(status_code=404, detail="Không tìm thấy lời mời")

    # Xóa luôn lời mời khỏi DB hoặc đổi status thành 'declined'
    db.delete(collab)
    db.commit()
    return {"message": "Bạn đã từ chối lời mời"}