from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

async def send_otp_email(email_to: str, otp: str):
    message = MessageSchema(
        subject="Mã xác thực OTP - CMS",
        recipients=[email_to],
        body=f"Mã OTP của bạn là: {otp}. Mã này có hiệu lực trong 5 phút.",
        subtype=MessageType.plain
    )
    fm = FastMail(conf)
    await fm.send_message(message)