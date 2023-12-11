from fastapi import APIRouter
from fastapi_mail import MessageSchema, ConnectionConfig, FastMail, MessageType
from app.config import MAIL_NAME, MAIL_PASSWORD

router = APIRouter(
    prefix="/mail",
    tags=["mail"]
)


async def send_registration_notification(email: str):
    message = MessageSchema(
        subject="Registration Notification",
        recipients=[email],
        body=f"Dear {email},\n\nThank you for registering with us!\n\nBest regards,\nTrello",
        subtype=MessageType.plain
    )
    await get_credential_and_send(message)


async def get_credential_and_send(message: MessageSchema):
    connection_config = ConnectionConfig(
        MAIL_USERNAME=MAIL_NAME,
        MAIL_PASSWORD=MAIL_PASSWORD,
        MAIL_FROM="rostovskii.1020@gmail.com",
        MAIL_PORT=587,
        MAIL_SERVER="smtp.gmail.com",
        MAIL_SSL_TLS=False,
        MAIL_STARTTLS=True,
        USE_CREDENTIALS=True,
        MAIL_DEBUG=0,
        MAIL_FROM_NAME="Trello",
        SUPPRESS_SEND=0,
        VALIDATE_CERTS=False,
        TIMEOUT=30,
    )
    fm = FastMail(connection_config)
    await fm.send_message(message)


@router.post("/send")
async def mail_send(email: str):
    await send_registration_notification(email)
    return "Message was sent"

