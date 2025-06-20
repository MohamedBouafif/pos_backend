from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi import Depends

from app import models
from app.OAuth2 import  get_curr_employee
from app.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbDep = Annotated[Session, Depends(get_db)]
OAuthDep = Annotated[OAuth2PasswordRequestForm, Depends()]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
tokenDep = Annotated[str , Depends(oauth2_scheme)]


class PaginationParams:
    def __init__(self, page_size: int =10 , page_number: int = 1):
        self.page_size = page_size
        self.page_number = page_number

PaginationDep = Annotated[PaginationParams, Depends()]


def get_current_employee(db : DbDep ,token : tokenDep ):
    return get_curr_employee(db , token)
currentEmployee = Annotated[models.Employee, Depends(get_current_employee)]
