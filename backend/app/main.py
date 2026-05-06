from fastapi import FastAPI
from app.core.database import engine, Base
from app.api import auth

# Tự động tạo các bảng trong Database (sau này dự án lớn sẽ dùng Alembic để migrate)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CMS API")

# Gắn Router Auth vào ứng dụng
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Backend FastAPI is running!"}