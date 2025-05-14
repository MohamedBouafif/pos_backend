from typing import List

from fastapi import BackgroundTasks, FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse
from pathlib import Path

from .config import settings

class EmailSchema(BaseModel):
    email: List[EmailStr]
   


conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = 465,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
    TEMPLATE_FOLDER = Path(__file__).parent / 'templates',
)






async def simple_send_account_activation(email: EmailSchema, body: dict ) -> JSONResponse:

    message = MessageSchema(
        subject="Création de compte - POS",
        recipients=email.email,
        template_body=body,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message, template_name = "account_activation.html")
    return JSONResponse(status_code=200, content={"message": "email has been sent"})    

async def simple_send_reset_password(email: EmailSchema, body: dict ) -> JSONResponse:

    message = MessageSchema(
        subject="Création de compte - POS",
        recipients=email.email,
        template_body=body,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message, template_name = "reset_password.html")
    return JSONResponse(status_code=200, content={"message": "email has been sent"})    