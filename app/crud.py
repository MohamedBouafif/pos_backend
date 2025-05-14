from sqlalchemy.orm import Session
from .import models, schemas, emailUtil,enums
import uuid
def get(db : Session, id : int):
    return db.query(models.Employee).filter(models.Employee.id == id).first()

def get_by_email(db : Session , email : str):
    return db.query(models.Employee).filter(models.Employee.email == email).first()

def get_all(db : Session, skip: int = 0, limit : int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()

def get_confirmation_code(db :Session , code:str):
    return db.query(models.AccountActivation).filter(models.AccountActivation.token == code).first()

async def add (db : Session, employee: schemas.EmployeeCreate):
    # fix me later when reading about security
    employee.password= employee.password + "notreallyhashed"

    employee_data  = employee.model_dump()
    employee_data.pop('confirm_password')
    roles = employee_data.pop('roles')
    email = employee_data['email']

    db_employee = models.Employee(**employee_data)
    db.add(db_employee)
    db.commit() #tsajel change fi db commit vs flush
    db.refresh(db_employee)#fil moment hedha db 3tat id lil employee -> ki naaml refresh we get the id
    
    # adding employee roles 
    for role in roles:
        db_role = models.EmployeeRole(role = role, employee_id = db_employee.id)
        db.add(db_role)
        db.commit()
        db.refresh(db_role)

    # add confirmation code to db
    activation_code = models.AccountActivation(employee_id = db_employee.id ,email = db_employee.email, status = enums.TokenStatus.Pending, token = uuid.uuid1())
    db.add(activation_code)
    db.commit()
    db.refresh(activation_code)
     
    # sending emails -> email service 
    await emailUtil.simple_send_account_activation(emailUtil.EmailSchema(email=[email]),{
        'code': activation_code.token,
        'name': employee_data['first_name'],
        'psw' : employee_data['password']
    })

    return  schemas.EmployeeResponse.model_validate(db_employee)


#hehdi chakchouka ketebha ena bech nab3th reset password AMA TEKHDDDDDDDDDDM 
async def resetpassword(db : Session, email: str):
   employee_db = get_by_email(db,email)

   reset_password = models.ResetPassword(employee_id = employee_db.id, email= email,status = enums.TokenStatus.Pending, token = uuid.uuid1(), )
   db.add(reset_password)
   db.commit()
   db.refresh(reset_password)
   await emailUtil.simple_send_reset_password(emailUtil.EmailSchema(email = [email]),{
       'code' : reset_password.token
   })


    
    
