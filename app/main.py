from fastapi import FastAPI, Depends , HTTPException, status
from app import crud, schemas
from app import models, enums
from .database import SessionLocal, engine
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import update
import re



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
    # db_employee  = crud.get_by_email(db,email = employee_create.email)
    # if db_employee:
    #     raise HTTPException(status_code = 400 , detail = "Email already registered") 
    # HEDHY NA7EHA khater 3maltlha try catch  fil add function 
    return await crud.add(db, employee_create)


@app.patch("/employee",response_model = schemas.BaseOut)
def confirm_account(confirmAccountInput :schemas.ConfirmAccount, db : Session = Depends(get_db)):
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

email_regex = r'^\S+@\S+\.\S+$'
cnss_regex = r'^\d{8}-\d{2}$'
phone_number_regex = r'^\d{8}$'

mandatory_fields = {
    "first_name": "First Name",
    "last_name": "Last Name",
    "email": "Email",
    "number": "Number",
    "contract_type": "Contract Type",
    "gender": "Gender",
    "employee_roles": "Roles",
}
optional_fields = {
    "birth_date": "Birth Date",
    "address": "Address",
    "phone_number": "Phone Number",
}
mandatory_with_condition = {
    "cnss_number": ("Cnss Number", lambda employee: isCdiOrCdd(employee))
}#                      0               1(tekhou parametre)
possible_fields = {
    **optional_fields,
    **mandatory_fields,
    **mandatory_with_condition
}
unique_fields = {
    "email" : models.Employee.email,
    "number" : models.Employee.number
}

options = [
    schemas.MatchyOption(display_value=mandatory_fields["first_name"], value="first_name", mandatory=True, type=enums.FieldType.string),
    schemas.MatchyOption(display_value=mandatory_fields["last_name"], value="last_name", mandatory=True, type=enums.FieldType.string),
    schemas.MatchyOption(display_value=mandatory_fields["email"], value="email", mandatory=True, type=enums.FieldType.string, conditions=[
        schemas.MatchyCondition(property=enums.ConditionProperty.regex, comparer=enums.Comparer.e, value=email_regex),
    ]),
    schemas.MatchyOption(display_value=mandatory_fields["number"], value="number", mandatory=True, type=enums.FieldType.integer),
    schemas.MatchyOption(display_value=optional_fields["birth_date"], value="birth_date", mandatory=False, type=enums.FieldType.string),
    schemas.MatchyOption(display_value=optional_fields["address"], value="address", mandatory=False, type=enums.FieldType.string),
    schemas.MatchyOption(display_value=mandatory_with_condition["cnss_number"][0], value="cnss_number", mandatory=False, type=enums.FieldType.string, conditions=[
        schemas.MatchyCondition(property=enums.ConditionProperty.regex, comparer=enums.Comparer.e, value=cnss_regex)
    ]),
    schemas.MatchyOption(display_value=mandatory_fields["contract_type"], value="contract_type", mandatory=True, type=enums.FieldType.string, conditions=[
        schemas.MatchyCondition(property=enums.ConditionProperty.value, comparer=enums.Comparer._in, value=enums.ContractType.getPossibleValues())
    ]),
    schemas.MatchyOption(display_value=mandatory_fields["gender"], value="gender", mandatory=True, type=enums.FieldType.string, conditions=[
        schemas.MatchyCondition(property=enums.ConditionProperty.value, comparer=enums.Comparer._in, value=enums.Gender.getPossibleValues())
    ]),
    schemas.MatchyOption(display_value=mandatory_fields["employee_roles"], value="employee_roles", mandatory=True, type=enums.FieldType.string),
    schemas.MatchyOption(display_value=optional_fields["phone_number"], value="phone_number", mandatory=False, type=enums.FieldType.string, conditions=[
        schemas.MatchyCondition(property=enums.ConditionProperty.regex, comparer=enums.Comparer.e, value=phone_number_regex),
    ]),
]


def is_regex_matched(pattern,field):
    return field if re.match(pattern, field) else None # ken raj3et none check if its warning khaliha none else 9olou ysala7
def is_valid_email(field:str):
    return field if  is_regex_matched(email_regex,field) else None
def is_positive_int(field: str):
    try:
        res = int(field)
    except:
        return None #not parsable to int 
    return res if res>= 0 else None
def is_valid_date(field):
    try:
        #FIXME: try to give the user the possibility to configure dates format
        # or try many format (not recommended) 12/01 -> 12 jan
        # 12/01 -> mm/dd -> 1 dec
        # user we3i bel format
        obj = datetime.strptime(field, '%Y-%m-%d')
        return obj.isoformat()
    except:
        return None # fchel enou yrodha date -> not parsable to int
    
def isCdiOrCdd(employee):
    return employee["contract_type"].value in [enums.ContractType.Cdi,enums.ContractType.Cdd]
def is_valid_cnss_number(field):
    return is_regex_matched(cnss_regex,field) if isCdiOrCdd(field) else None
def is_valid_phone_number(field):
    return field if is_regex_matched(phone_number_regex, field) else None
def are_roles_valid(field):
    # Admin,  venDor,  
    res = []
    for role_name in field.split(''):
        value = enums.RoleType.is_valid_enum_value(role_name)
        if not value:
            return None
        else:
            res.append(value)
    return res # [enums.RoleType.Admin, enums.RoleType.Vendor]

fields_check = {
    #field to validate : {function to validate , error message if not validated}
    "email" : {lambda field : is_valid_email(field), "Wrong Email Format !"},
    "gender" : {lambda field : enums.Gender.is_valid_enum_value(field), f"Possible values are : {enums.Gender.getPossibleValues()}"},
    "contract_type" : {lambda field : enums.ContractType.is_valid_enum_value(field), f"Possible values are : {enums.ContractType.getPossibleValues()}"},
    "number" : {lambda field : is_positive_int(field) , "It should be an integer >= 0"},
    "birth_date": {lambda field : is_valid_date(field) , "Dates fromat should be dd/mm/YYYY"},
    "cnss_number" : {lambda field : is_valid_cnss_number(field), "It should be {8 digits}-{2 digits} and it's Mandatory for Cdi and Cdd"},
    "phone_number" : {lambda field : is_valid_phone_number(field) , "Phone number is not valid for Tunisian, it should be of 8 digits"},
    "employee_roles" : {lambda field : are_roles_valid(field) , f"Possible values are :{enums.RoleType.getPossibleValues()}"}

}
def is_field_mandatory(employee,field):
    return field in mandatory_fields or (field in mandatory_with_condition and mandatory_with_condition[field][1](employee))


#employee wehed 
def validate_employee_data(employee):
    #employee = [{}] eg: [{cnss_number: {40, 1, 1}, {roles: {Admin, vendor, 1, 2}}, ....] ligne ta3 donne
    #employee = lista ta3 key values il key homa les fields wil values houma (value, rowIndex, colIndex)
    errors = []
    warnings = []
    wrong_cells = []  # bech nraj3ouhom ll matchy ylawanhom bel a7mer
    employee_to_add = { field: cell.value for field, cell in employee.items() } #lezem na7i il x wil y wnrodou dict aady -> {{field:value}, {field:value},....}

    for field in possible_fields:
        if field not in employee:
            if is_field_mandatory(employee, field):
                errors.append(f"{possible_fields[field]} is mandatory but missing")
            continue

        cell = employee[field]
        employee_to_add[field] = employee_to_add[field].strip() #ynajem ymedlik "   vendor         " fii 3odh "vendor"-> {{field:value}, {field:value},....}

        if employee_to_add[field] == '': #birth date optional = ""
            if is_field_mandatory(employee, field):
                msg = f"{possible_fields[field][0]} is mandatory but missing"
                errors.append(msg)
                wrong_cells.append(schemas.MatchyWrongCell(message=msg, rowIndex=cell.rowIndex, colIndex=cell.colIndex))
            else:
                employee_to_add[field] = None # f db tetsab null
        elif field in fields_check:
            converted_val = fields_check[field][0](employee_to_add[field])
            if converted_val is None: #if not convered_val khater ken je 3ana type bool => False valid value, int >= 0 converted_val = 0
                msg = fields_check[field][1]
                (errors if is_field_mandatory(employee, field) else warnings).append(msg)
                wrong_cells.append(schemas.MatchyWrongCell(message=msg, rowIndex=cell.rowIndex, colIndex=cell.colIndex))
            else:
                employee_to_add[field] = converted_val

    return (errors, warnings, wrong_cells, employee_to_add)

#many employees: batch add to reduce time consumption
def validate_employees_data_and_upload(employees:list , force_upload: bool , db : Session = Depends(get_db)):
    errors = []
    warnings =[]
    wrong_cells = []
    employees_to_add = [] #bch nistaamlou fil batch add  bch nsob kol chy fard mara fil db

    #adding errors, warnings , wrong_cells and the employee that we are going to add
    for line, employee in enumerate(employees):
        emp_errors, emp_warnings , emp_wrong_cells, emp = validate_employee_data(employee)
        if emp_errors:
            msg = ('\n').join(emp_errors) #returns a single string binet kol element mil list fama il joinig character 
            errors.append(f"\nLine {line + 1}: \n {msg}")
        if emp_warnings:
            msg = ('\n').join(emp_warnings)
            warnings.append(f"\nLine {line + 1}: \n {msg}")
            # tajouti fil le5er ta3 il liste il value puisque il msg wala string ma3adch lista (sinon nnista3mlou extend) : 
            # numero ligne : 
            # msg 
        if emp_wrong_cells:
            wrong_cells.extend(emp_wrong_cells)
            #bch najoutiw fil filsta ta3 il wrong cells lista ta3 cells puisque emp_wrong_cells is a list
        employees_to_add.append(emp)
    
    
    for field in unique_fields:
        values = set()
        for line ,employee in enumerate(employees): #employee = [{fields: value, rowIndex,colIndex}]
                                                    #                       hedha kolou objet ena nekteb fih haka: MatchyCell
            cell = employee.get(field)
            val = cell.value.strip()
            if val == '':#if it is mandatory , email and number where already checked in the fields check
                continue

            if val in values:#mahomch unique f b3adhhom
                    msg = f"{possible_fields[field]} should be unique. but this value exists more than one time in the file"
                    (errors if is_field_mandatory(employee, field) else warnings).append(msg)
                    wrong_cells.append(schemas.MatchyWrongCell(message=msg, rowIndex=cell.rowIndex, colIndex=cell.colIndex))
            else:
                values.add(val)
            duplicated_vals = db.query(models.Employee).filter(unique_fields[field].in_(values)).all()#nchouf famechi emails fil db ymatchiw il emails ili fil csv
            if duplicated_vals :
                msg  = f"{possible_fields[field]} should be unique . {(', ').join(duplicated_vals)} already exist  in database"
                (errors if is_field_mandatory(employee, field) else warnings).append(msg)
                wrong_cells.append(schemas.MatchyWrongCell(message=msg, rowIndex=cell.rowIndex, colIndex=cell.colIndex))
    
    #mouhema inik t7otha lehna : manraja3ch il errors partiellement
    if errors or (warnings and not force_upload):
        return schemas.ImportResponse(
            errors = ('\n').join(errors),
            warnings = ('\n').join(warnings),
            wrongCells=wrong_cells
        )
@app.post("/employees/import")
def importEmployees():
    pass

@app.get("/employees/possibleImportFields")
def getPossibleFields(db : Session = Depends(get_db)):
    return schemas.ImportPossibleFields(
        possible_fields=options,
    )

@app.post("employees/csv")
def upload(entry:schemas.MatchyUploadEntry, db:Session = Depends(get_db)):
    employees = entry.lines
    if not employees: #front lezmou yjeri ili fama au moins ligne
        raise HTTPException(status_code=400, detail = "Nothig to do , Empty file !")
    header_fields = employees[0].keys()
    missing_mendatory_fields = set(mandatory_fields.keys()) - employees[0].keys()
    if missing_mendatory_fields:
        raise HTTPException(
            status_code = 400, 
            detail= f"missing mendatory fields: {(', ').join([display  for field,display in missing_mendatory_fields.items()])}"
        )