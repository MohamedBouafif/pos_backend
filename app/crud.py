from fastapi import HTTPException
from sqlalchemy.orm import Session
from .import models, schemas, emailUtil,enums
import uuid
def get(db : Session, id : int):
    return db.query(models.Employee).filter(models.Employee.id == id).first()
def get_all(db : Session, skip: int = 0, limit : int = 100):
    return db.query(models.Employee).offset(skip).limit(limit).all()
def add_error(text, db: Session):
    try:
        db.add(models.Error(
            text = text
        ))
        db.commit()
    except Exception as  e :
        #alternative solution bech ken db tahet najem nil9a l mochkla
        raise HTTPException(status_code = 500,detail ="Something went wrong")
def get_confirmation_code(db :Session , code:str):
    return db.query(models.AccountActivation).filter(models.AccountActivation.token == code).first()

error_keys = {
    "employee_roles_employee_id_fkey": "No Employee with this id",
    "employee_roles_pkey": "No Employee Role with this id",
    "ck_employees_cnss_number": "It should be {8 digits}-{2 digits} and it's Mandatory for Cdi and Cdd",
    "employees_email_key": "Email already used",
    "employees_pkey": "No employee with this id",
}
def get_error_message(error_message):
    for error_key in error_keys:
        if error_key in error_message:
            return error_keys[error_key] # ken yti7ou 7ajtin ya3tik 7aja kahaw (l7aja loula ili ta7et khw) 
        
        
    return "Something went wrong" # eyh ken something went wrong w customer kalamni chnaaml ? kifeh naarf lmochkla ili saret  ? 
                                  #-> tableau fil db fih el message ta3 el errors



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
async def add (db : Session, employee: schemas.EmployeeCreate):
    try:
        # fix me later when reading about security
        employee.password= employee.password + "notreallyhashed"

        employee_data  = employee.model_dump()
        employee_data.pop('confirm_password')
        roles = employee_data.pop('roles')
        email = employee_data['email']

        db_employee = models.Employee(**employee_data)
        db.add(db_employee) # its pending and nothing is insterted in the db
        #ki kenet autoflash  = true par default yaani izid fil session w toul yeflushi fil db 
        # 
        db.flush() #tsajel change fi db (traaja3 id)
        # adding employee roles 
        """for role in roles:
            db_role = models.EmployeeRole(role = role, employee_id = db_employee.id)
            db.add(db_role)
            db.commit()# we are doing so many commits ---> ala kol role naamlou f transaction 
            db.refresh(db_role)
        """
        db.add_all ([models.EmployeeRole(role = role, employee_id = db_employee.id) for role in roles])
        #manesthak chy mil roles ili bch yotsabou il db so no need to flash
        # add confirmation code to db
        activation_code = models.AccountActivation(employee_id = db_employee.id ,email = db_employee.email, status = enums.TokenStatus.Pending, token = uuid.uuid1())
        db.add(activation_code)
        #db.commit() idha ken mayhemekch fil lmail tab3ath wle hawka fil front twarih boutton send again
        
        # sending emails -> email service 
        await emailUtil.simple_send_account_activation(emailUtil.EmailSchema(email=[email]),{
            'code': activation_code.token,
            'name': employee_data['first_name'],
            'psw' : employee_data['password']
        })
        db.commit()
    except Exception as e:
        db.rollback()
        text = str(e)
        add_error(text,db)
        raise HTTPException(status_code = 500,detail =get_error_message(str(e)))

    return  schemas.EmployeeResponse.model_validate(db_employee)

#fix later 
# async def resetpassword(db : Session, email: str):
#    employee_db = get_by_email(db,email)

#    reset_password = models.ResetPassword(employee_id = employee_db.id, email= email,status = enums.TokenStatus.Pending, token = uuid.uuid1(), )
#    db.add(reset_password)
#    db.commit()
#    db.refresh(reset_password)
#    await emailUtil.simple_send_reset_password(emailUtil.EmailSchema(email = [email]),{
#        'code' : reset_password.token
#    })


    
    
