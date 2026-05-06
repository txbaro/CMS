from fastapi import FastAPI
from app.core.database import engine, Base
from app.api import auth, documents
from app.models.user import User
from app.models.otp import OTP
from app.models.document import Document

app = FastAPI(title="CMS API")

# Gắn Router Auth vào ứng dụng
app.include_router(auth.router)
app.include_router(documents.router)

@app.get("/")
async def root():
    return {"message": "Backend FastAPI is running!"}