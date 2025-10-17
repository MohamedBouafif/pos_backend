from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm


from app import enums, models, schemas
from app.OAuth2 import ACCESS_TOKEN_EXPIRE_MINUTES,create_access_token,authenticate_employee, get_employee_by_email, get_password_hash
from app.crud.employee import edit_employee, sudo_edit_employee
from app.crud.error import add_error, get_error_message
from app.dependencies import DbDep, OAuthDep
from app.enums.emailTemplate import EmailTemplate
from app.external_services.emailService import EmailSchema, simple_send
from app.schemas import Token, ForgetPassword
from app.crud import auth

app = APIRouter(
    tags=["Authentification"],
)


@app.post("/auth/login",response_model = schemas.Token)
async def login_for_access_token(db : DbDep,form_data: OAuthDep):
    try:
        employee = authenticate_employee(db, form_data.username, form_data.password)
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
    except Exception as e:
        db.rollback()
        text = str(e)
        add_error(text,db)
        raise HTTPException(status_code = 500,detail =get_error_message(str(e)))
    
    return Token(status_code=status.HTTP_200_OK ,access_token=access_token, token_type="bearer")

@app.patch("/auth/confirm_account",response_model = schemas.BaseOut)
def confirm_account(confirmAccountInput :schemas.ConfirmAccount, db : DbDep):
    try:
        confirmation_code = auth.get_confirmation_code(db,confirmAccountInput.confirm_code)
        if not confirmation_code:
            raise HTTPException(status_code=400, detail ="Token does not exists")
        if confirmation_code.status == enums.TokenStatus.Used:
            raise HTTPException(status_code= 400,  detail="Token already used")
        diff = datetime.now() - confirmation_code.created_on 
        if diff.total_seconds() > 60*60:
            raise HTTPException(status_code=400 , detail="Token expired")
        
        #update account status
        sudo_edit_employee(db,confirmation_code.employee_id,{models.Employee.account_status : enums.AccountStatus.Active} )
        
        #update token status
        auth.edit_confirmation_code(db , confirmation_code.id, {models.AccountActivation.status : enums.TokenStatus.Used})
        
        db.commit()
    except Exception as e:
        db.rollback()
        text = str(e)
        add_error(text,db)
        raise HTTPException(status_code = 500,detail =get_error_message(str(e)))
    
    return schemas.BaseOut(
            detail="Account activated !",
            status_code= status.HTTP_200_OK
        )
    

@app.post("/auth/forgot_password", response_model = schemas.BaseOut)
async def forgot_password(entry : schemas.ForgetPassword, db :DbDep):
    employee = get_employee_by_email(db , entry.email)
    if not employee:
        return schemas.BaseOut(
            detail = "No Account with this email",
            status = status.HTTP_404_NOT_FOUND
        )
    try:
        reset_code = auth.add_reset_code(db , employee)
        db.flush()
        await simple_send(EmailSchema(email=[employee.email]),{
            'code': reset_code.token,
        },EmailTemplate.ResetPassword)
        
        db.commit()

    except Exception as e:
        db.rollback()
        text = str(e)
        add_error(text,db)
        raise HTTPException(status_code = 500,detail =get_error_message(str(e)))
    return schemas.BaseOut(
            detail = "email Sent !",
            status = status.HTTP_200_OK
        )
        

@app.patch("/auth/reset_password",response_model = schemas.BaseOut)
def reset_password(resetPasswordInput : schemas.ResetPassword, db : DbDep):
    try:
        reset_code = auth.get_reset_code(db,resetPasswordInput.reset_code)
        if not reset_code:
            raise HTTPException(status_code=400, detail ="Token does not exists")
        if reset_code.status == enums.TokenStatus.Used:
            raise HTTPException(status_code= 400,  detail="Token already used")
        diff = datetime.now() - reset_code.created_on 
        if diff.total_seconds() > 60*60:
            raise HTTPException(status_code=400 , detail="Token expired")
        
        if resetPasswordInput.password != resetPasswordInput.confirm_password:
            raise HTTPException(status_code=400 , detail="Passwords do not match !")
      

        edit_employee(db,reset_code.employee_id, {models.Employee.password : get_password_hash(resetPasswordInput)})
        
        auth.edit_reset_code(db , reset_code.id, {models.AccountActivation.status : enums.TokenStatus.Used})
        
        db.commit()
    except Exception as e:
        db.rollback()
        text = str(e)
        add_error(text,db)
        raise HTTPException(status_code = 500,detail =get_error_message(str(e)))
    
    return schemas.BaseOut(
            detail="Password reset successufully !",
            status_code= status.HTTP_200_OK
        )
    