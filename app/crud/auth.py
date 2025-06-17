import uuid
from sqlalchemy import update
from sqlalchemy.orm import Session

from app import enums, models 
#confirmation code
def get_confirmation_code(db :Session , code:str):
    return db.query(models.AccountActivation).filter(models.AccountActivation.token == code).first()

def add_confirmation_code(db : Session, id : int,email:str):
    activation_code = models.AccountActivation(employee_id = id ,email = email, status = enums.TokenStatus.Pending, token = uuid.uuid1())
    db.add(activation_code)
    return activation_code

def edit_confirmation_code(db : Session , id : int,new_data : dict):
    stmt1 = update(models.AccountActivation).where(models.AccountActivation.id == id).values(new_data)
    db.execute(stmt1)

#reset code
def get_reset_code(db :Session , code:str):
    return db.query(models.ResetPassword).filter(models.ResetPassword.token == code).first()

def add_reset_code(db : Session, db_employee : models.Employee):
    reset_code = models.ResetPassword(employee_id = db_employee.id ,email = db_employee.email, status = enums.TokenStatus.Pending, token = uuid.uuid1())
    db.add(reset_code)
    return reset_code

def edit_reset_code(db : Session , id : int,new_data : dict):
    stmt1 = update(models.ResetPassword).where(models.ResetPassword.id == id).values(new_data)
    db.execute(stmt1)
