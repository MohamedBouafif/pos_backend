from typing import List

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse
from pathlib import Path
from app.enums.emailTemplate import EmailTemplate

from ..config import settings

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



template_per_email = {
    EmailTemplate.ConfirmAccount : "account_activation.html",
    EmailTemplate.ResetPassword : "reset_password.html",
}
subject_per_mail = {
    EmailTemplate.ConfirmAccount: "Création de compte - POS",
    EmailTemplate.ResetPassword: "Réinitialiser le mot de passe - POS"
}


async def simple_send(email: EmailSchema, body: dict , type : EmailTemplate) -> JSONResponse:

    message = MessageSchema(
        subject=subject_per_mail[type],
        recipients=email.email,
        template_body=body,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message, template_name = template_per_email[type])
    return JSONResponse(status_code=200, content={"message": "email has been sent"})    

