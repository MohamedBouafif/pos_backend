from fastapi import FastAPI, Depends , HTTPException
from app import crud, schemas
from app import models
from .database import SessionLocal, engine
from sqlalchemy.orm import Session

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/employee/", response_model=schemas.EmployeeResponse)
async def create_user(employee_create: schemas.EmployeeCreate, db : Session = Depends(get_db)):
    if employee_create.password != employee_create.confirm_password:
        raise HTTPException(status_code=400, detail="Password must match!")
    db_employee  = crud.get_by_email(db,email = employee_create.email)
    if db_employee:
        raise HTTPException(status_code = 400 , detail = "Email already registered")
    return await crud.add(db, employee_create)
