from sqlalchemy.orm import Session
from .import models, schemas, emailUtil

def get(db : Session, id : int):
    return db.query(models.Employee).filter(models.Employee.id == id).first()

def get_by_email(db : Session , email : str):
    return db.query(models.Employee).filter(models.Employee.email == email).first()

def get_all(db : Session, skip: int = 0, limit : int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()

async def add (db : Session, employee: schemas.EmployeeCreate):
    # fix me later when reading about security
    employee.password= employee.password + "notreallyhashed"
    employee_data  = employee.model_dump()
    employee_data.pop('confirm_password')
    roles = employee_data.pop('roles')
    db_employee = models.Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit() #tsajel change fi db commit vs flush
    db.refresh(db_employee)#fil moment hedha db 3tat id lil employee -> ki naaml refresh we get the id
    
    # adding employee roles 
    for role in roles:
        db_role = models.EmployeeRole(role = role, employee_id = db_employee.id)
        db.add(db_role)
        db.commit()
        db.refresh()

    # sending emails -> email service 
    await emailUtil.simple_send([employee_data.email])
    return schemas.EmployeeResponse(**db_employee.__dict__)