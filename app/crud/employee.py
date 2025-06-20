from fastapi import HTTPException
from sqlalchemy import func, update
from sqlalchemy.orm import Session

from app.OAuth2 import get_password_hash
from app.crud.auth import add_confirmation_code
from app.dependencies import  PaginationParams
from app.enums.emailTemplate import EmailTemplate
from ..external_services import emailService
from ..import models, schemas, enums


error_keys = {
    "employee_roles_employee_id_fkey": "No Employee with this id",
    "employee_roles_pkey": "No Employee Role with this id",
    "ck_employees_cnss_number": "It should be {8 digits}-{2 digits} and it's Mandatory for Cdi and Cdd",
    "employees_email_key": "Email already used",
    "employees_pkey": "No employee with this id",
}
#employee
def get_employee(db : Session, id : int,):
    return db.query(models.Employee).filter(models.Employee.id == id).first()
def get_all(db : Session, skip: int = 0, limit : int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()

def sudo_edit_employee(db : Session, id:int, new_data :dict ):
    stmt1 = update(models.Employee).where(models.Employee.id == id).values(new_data)
    db.execute(stmt1)


def div_ceil(nominator,denominator):
    full_pages = nominator // denominator
    additional_page = 1 if nominator % denominator > 0 else 0
    return full_pages + additional_page

def get_employees(db: Session, pagination_param: PaginationParams, name_substr: str):
    query = db.query(models.Employee)

    if name_substr:
        query = query.filter(func.lower(func.concat(models.Employee.first_name, ' ', models.Employee.last_name)).contains(func.lower(name_substr)))
    
    total_records = query.count()
    total_pages = div_ceil(total_records, pagination_param.page_size)
    employees = query.limit(pagination_param.page_size).offset((pagination_param.page_number-1)*pagination_param.page_size).all()
    
    return (employees, total_records, total_pages)


#in this function there is no partial success which means that if i encounter an exception 
# that can prevent from adding employee role (or other data to db) i must stop all the process
# rollback , session, flush 

# we call the models atomic 
"""session : to93ed t7adher fil data mte3ha il kol  fi transaction ba3d it will make changes in
    the db f dharba barka ( update, delete ,insert) w ki mataamlch commit maytsajlouch fil db
    the session object register il transaction operations bil session.add() ama maytzed chy fil db (yo93dou in memeory fil python level) 
    wki nbadel haja fil object ili bch nzidou ba3d man3ayet lil session.add zeda yitbadl (it will keep track of changes).
    ki n3aytou l session.flush() wa9tha il operations (insert,delete, update) 
    ili tsajlou fil transaction il kol bch YOUSLOU LIL DB w yO93DOU PENDING 
    lin naamlou session.commit() wa9tha il transcation will be commited
        ----> perfermance : we need to commit once bech mano93odch 

    ken naaml commit manajmch naaml roll_back() wki naaml commit rahou taaml flush wahadha wahadha
    ki naaml flash w naaml roll back yitnaha mil db


    ama ken hachti bil id taa haja 9bal manzidha lil db lezem nistaaml flush (eg employee bch nzidou roles donc hachti bil id mte3ou wihtout commiting the employee )
    in the db  ----> use flash EG : a = model() , session.add(a) -> a.id = null , session.flush() ---> a.id is not null
"""
async def add_employee (db : Session, employee: schemas.EmployeeCreate):
    employee.password = get_password_hash(employee.password)
    employee_data  = employee.model_dump()
    employee_data.pop('confirm_password')
    roles = employee_data.pop('roles')
    email = employee_data['email'] 
    #add employee
    db_employee = models.Employee(**employee_data)
    db.add(db_employee) 
    db.flush() 
    
    #add employee roles
    db.add_all ([models.EmployeeRole(role = role, employee_id = db_employee.id) for role in roles])
    
    # add confirmation code to db
    activation_code = add_confirmation_code(db = db , id = db_employee.id , email = db_employee.email)  
    #send confirmation account mail 
    await emailService.simple_send(emailService.EmailSchema(email=[email]),{
        'code': activation_code.token,
        'name': employee_data['first_name'],
        'psw' : employee_data['password']
    },EmailTemplate.ConfirmAccount)
    db.commit()
    return  db_employee

async def edit_employee(db: Session, id: int, entry: schemas.EmployeeEdit):
    query = db.query(models.Employee).filter(models.Employee.id == id)
    employee_in_db = query.first()

    if not employee_in_db:
        raise HTTPException(status_code=400, detail="Employee not found")
    
    fields_to_update = entry.model_dump()
    for field in ["email", "password", "confirm_password", "roles", "actual_password"]:
        fields_to_update.pop(field)
    
    # manage roles after reading about relationships (manage access role)

    # if edited email
    if employee_in_db.email != entry.email:
        if not entry.actual_password or get_password_hash(entry.password) != employee_in_db.password:
            raise HTTPException(status_code=400, detail="Current Password missing or incorrect. It's mandatory to set a new email")
        
        fields_to_update[models.Employee.email] = entry.email
        fields_to_update[models.Employee.account_status] = enums.AccountStatus.Inactive

    # if edited psw
    if entry.password and get_password_hash(entry.password) != employee_in_db.password:
        if entry.password != entry.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords must match")
        
        if not entry.actual_password or get_password_hash(entry.actual_password) != employee_in_db.password:
            raise HTTPException(status_code=400, detail="Current Password missing or incorrect. It's mandatory to set a new password")
        
        fields_to_update[models.Employee.password] = get_password_hash(entry.password)

    query.update(fields_to_update, synchronize_session=False)

    if models.Employee.email in fields_to_update:
        activation_code = add_confirmation_code(db, employee_in_db.id, fields_to_update[models.Employee.email])
    
        # send confirmation email
        await emailService.simple_send([employee_in_db.email], {
                'name': employee_in_db.first_name,
                'code': activation_code.token,
            }, enums.EmailTemplate.ConfirmAccount,
        )
    
    db.commit()