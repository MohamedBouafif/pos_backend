from fastapi import FastAPI, Depends , HTTPException, status
from app import crud, schemas
from app import models, enums
from .database import SessionLocal, engine
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import update



app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/change_password")
async def reset_password(email : str,db : Session = Depends(get_db)):
    if crud.get_by_email(db= db, email = email) == None:
        raise HTTPException(status_code = 400 , detail = "Email is not registered")
    return await crud.resetpassword(db = db,email=email)
        



@app.post("/employee/", response_model=schemas.EmployeeResponse)
async def create_user(employee_create: schemas.EmployeeCreate, db : Session = Depends(get_db)):
    if employee_create.password != employee_create.confirm_password:
        raise HTTPException(status_code=400, detail="Password must match!")
    db_employee  = crud.get_by_email(db,email = employee_create.email)
    if db_employee:
        raise HTTPException(status_code = 400 , detail = "Email already registered")
    return await crud.add(db, employee_create)


@app.patch("/employee",response_model = schemas.BaseOut)
def confir_account(confirmAccountInput :schemas.ConfirmAccount, db : Session = Depends(get_db)):
    confirmation_code = crud.get_confirmation_code(db,confirmAccountInput.confirm_code)
    if not confirmation_code:
        raise HTTPException(status_code=400, detail ="Token does not exists")
    if confirmation_code.status == enums.TokenStatus.Used:
        raise HTTPException(status_code= 400,  detail="Token already used")
    diff = datetime.now() - confirmation_code.created_on 
    if diff.total_seconds() > 60*60:
        raise HTTPException(status_code=400 , detail="Token expired")
    
    
    stmt1 = update(models.Employee).where(models.Employee.id == confirmation_code.employee_id).values(account_status=enums.AccountStatus.Active)
    db.execute(stmt1)

    stmt2 = update(models.AccountActivation).where(models.AccountActivation.id == confirmation_code.id).values(status=enums.TokenStatus.Used)
    db.execute(stmt2)
    db.commit()

    return schemas.BaseOut(
        detail="Account activated !",
        status_code= status.HTTP_200_OK
    )