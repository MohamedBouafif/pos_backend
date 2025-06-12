from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.OAuth2 import ACCESS_TOKEN_EXPIRE_MINUTES,create_access_token,authenticate_employee
from app.dependencies import DbDep
from app.schemas import Token


app = APIRouter(
    tags=["Authentification"],
)


@app.post("/token")
async def login_for_access_token(
    db : DbDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    employee = authenticate_employee(db, form_data.email, form_data.password)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": employee.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
