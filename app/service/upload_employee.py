import uuid
from fastapi import status, BackgroundTasks
from sqlalchemy.orm import Session
import re
from datetime import datetime
from app import enums
from app.enums import Comparer,FieldType,ConditionProperty,ContractType,Gender,RoleType
from app import schemas, models
from app.enums.emailTemplate import EmailTemplate
from app.crud.error import add_error
from app.external_services.emailService import simple_send

email_regex = r"^\S+@\S+\.\S+$"
cnss_regex = r"^\d{8}-\d{2}$"
phone_regex = r"^\d{8}$"

mandatory_fields = {
    "first_name": "First Name",
    "last_name": "Last Name",
    "email": "Email",
    "number": "Number",
    "gender": "Gender",
    "contract_type": "Contract Type",
    "employee_roles": "Roles",
}
optional_fields = {
    "birth_date": "Birthdate",
    "address": "Address",
    "phone_number": "Phone",
}
mandatory_with_condition = {
    "cnss_number": ("Cnss Number", lambda employee: isCdiOrCdd(employee))
}
unique_fields = {"email": models.Employee.email, "number": models.Employee.number}
possible_fields = {**mandatory_fields, **optional_fields, **mandatory_with_condition}
options = [
    schemas.MatchyOption(
        display_value=mandatory_fields["first_name"],
        value="first_name",
        mandatory=True,
        type=FieldType.string,
    ),
    schemas.MatchyOption(
        display_value=mandatory_fields["last_name"],
        value="last_name",
        mandatory=True,
        type=FieldType.string,
    ),
    schemas.MatchyOption(
        display_value=mandatory_fields["email"],
        value="email",
        mandatory=True,
        type=FieldType.string,
        conditions=[
            schemas.MatchyCondition(
                property=ConditionProperty.regex,
                comparer=Comparer.e,
                value=email_regex,
            )
        ],
    ),
    schemas.MatchyOption(
        display_value=mandatory_fields["number"],
        value="number",
        mandatory=True,
        type=FieldType.integer,
    ),
    schemas.MatchyOption(
        display_value=optional_fields["birth_date"],
        value="birth_date",
        mandatory=False,
        type=FieldType.string,
    ),
    schemas.MatchyOption(
        display_value=optional_fields["address"],
        value="address",
        mandatory=False,
        type=FieldType.string,
    ),
    schemas.MatchyOption(
        display_value=mandatory_with_condition["cnss_number"][0],
        value="cnss_number",
        mandatory=False,
        type=FieldType.string,
        conditions=[
            schemas.MatchyCondition(
                property=ConditionProperty.regex,
                comparer=Comparer.e,
                value=cnss_regex,
            )
        ],
    ),
    schemas.MatchyOption(
        display_value=mandatory_fields["contract_type"],
        value="contract_type",
        mandatory=True,
        type=FieldType.string,
        conditions=[
            schemas.MatchyCondition(
                property=ConditionProperty.value,
                comparer=Comparer._in,
                value=ContractType.getPossibleValues(),
            )
        ],
    ),
    schemas.MatchyOption(
        display_value=mandatory_fields["gender"],
        value="gender",
        mandatory=True,
        type=FieldType.string,
        conditions=[
            schemas.MatchyCondition(
                property=ConditionProperty.value,
                comparer=Comparer._in,
                value=Gender.getPossibleValues(),
            )
        ],
    ),
    schemas.MatchyOption(
        display_value=mandatory_fields["employee_roles"],
        value="employee_roles",
        mandatory=True,
        type=FieldType.string,
    ),
    schemas.MatchyOption(
        display_value=optional_fields["phone_number"],
        value="phone_number",
        mandatory=False,
        type=FieldType.string,
        conditions=[
            schemas.MatchyCondition(
                property=ConditionProperty.regex,
                comparer=Comparer.e,
                value=phone_regex,
            )
        ],
    ),
]


def is_regex_matched(pattern, field):
    return field if re.match(pattern, field) else None


def is_valid_email(field: str):
    return field if is_regex_matched(email_regex, field) else None


def is_positive_int(field: str):
    try:
        res = int(field)
    except Exception:
        return None
    return res if res >= 0 else None


def is_valid_date(field):
    try:
        obj = datetime.strptime(field, "%Y-%m-%d")
        return obj.isoformat()
    except Exception:
        return None


def isCdiOrCdd(employee):
    return employee["contract_type"].value in [ContractType.Cdd, ContractType.Cdi]


def is_valid_cnss_number(field):
    return field if is_regex_matched(cnss_regex, field) else None


def is_valid_phone_number(field):
    return field if is_regex_matched(phone_regex, field) else None


def are_roles_valid(field):
    res = []
    for role in field.split(","):
        val = RoleType.is_valid(role)
        if not val:
            return None
        res.append(val)
    return res


fields_check = {
    "email": (lambda field: is_valid_email(field), "Wrong email format"),
    "gender": (
        lambda field: Gender.is_valid(field),
        f"Possible values are : {Gender.getPossibleValues()}",
    ),
    "contract_type": (
        lambda field: ContractType.is_valid(field),
        f"Possible values are : {ContractType.getPossibleValues()}",
    ),
    "number": (
        lambda field: is_positive_int(field),
        "It should be an integer >=0",
    ),
    "birth_date": (
        lambda field: is_valid_date(field),
        "Dates format should be YYYY-MM-DD",
    ),
    "cnss_number": (
        lambda field: is_valid_cnss_number(field),
        "It should be {8 digits}-{2 digits} and it's mandatory for Cdi or Cdd ",
    ),
    "phone_number": (
        lambda field: is_valid_phone_number(field),
        "Phone number is not valid for tunisia, it should be of 8 digits",
    ),
    "employee_roles": (
        lambda field: are_roles_valid(field),
        f"Possible values are : {RoleType.getPossibleValues()}",
    ),
}


def is_field_mandatory(field, employee):
    return field in mandatory_fields or (field in mandatory_with_condition and mandatory_with_condition[field][1](employee))



def validate_employee_data(employee):
    errors = []
    warnings = []
    wrong_cells = []
    employee_to_add = {field: cell.value for field, cell in employee.items()}
    for field in possible_fields:
        if field not in employee:
            if is_field_mandatory(field, employee):
                errors.append(f"{possible_fields[field]} is mandatory but missing ")
            continue
        cell = employee[field]
        employee_to_add[field] = employee_to_add[field].strip()
        if employee_to_add[field] == "":
            if is_field_mandatory(field, employee):
                msg = f"{possible_fields[field][0]} is mandatory but missing "
                errors.append(msg)
                wrong_cells.append(schemas.MatchyWrongCell(message=msg,rowIndex=int(cell.rowIndex),colIndex=int(cell.colIndex)))
            else:
                employee_to_add[field] = None
        elif field in fields_check:
            converted_val = fields_check[field][0](employee_to_add[field])
            if converted_val is None:
                msg = fields_check[field][1]
                (errors if is_field_mandatory(field, employee) else warnings).append(msg)
                wrong_cells.append(schemas.MatchyWrongCell(message=msg,rowIndex=int(cell.rowIndex),colIndex=int(cell.colIndex)))
            else:
                employee_to_add[field] = converted_val
    return (errors, warnings, wrong_cells, employee_to_add)


def validate_employees_data_and_upload(employees: list,force_upload: bool,background_tasks: BackgroundTasks,db: Session):
    try:
        errors = []
        warnings = []
        wrong_cells = []
        employees_to_add = []
        roles_per_email = {}
        for line, employee in enumerate(employees):
            emp_errors, emp_warnings, emp_wrong_cells, emp = validate_employee_data(employee)
            if emp_errors:
                msg = ("\n").join(emp_errors)
                errors.append(f"\nLine {line+1}:\n{msg}")
            if emp_warnings:
                msg = ("\n").join(emp_warnings)
                warnings.append(f"\nLine {line+1}:\n{msg}")
            if emp_wrong_cells:
                wrong_cells.extend(emp_wrong_cells)
            roles_per_email[emp.get("email")] = emp.pop("employee_roles")
            employees_to_add.append(models.Employee(**emp))
        for field in unique_fields:
            values = set()
            for line, employee in enumerate(employees):
                cell = employee.get(field)
                val = cell.value.strip()
                if val == "":
                    continue
                if val in values:
                    msg = f"{possible_fields[field]} should be unique but this value exists more than one time in the file"
                    (errors if is_field_mandatory(field, employee) else warnings).append(msg)
                    wrong_cells.append(schemas.MatchyWrongCell(message=msg,rowIndex=int(cell.rowIndex),colIndex=int(cell.colIndex)))
                else:
                    values.add(val)
            duplicated_vals = (db.query(models.Employee).filter(unique_fields[field].in_(values)).all())
            duplicated_vals = {str(val[0]) for val in duplicated_vals}
            if duplicated_vals:
                msg = f"{possible_fields[field]} should be unique {(', ').join([str(val[0]) for val in  duplicated_vals])} already exist in database"
                (errors if is_field_mandatory(field, employee) else warnings).append(msg)
                for emp in employees:
                    cell = emp.get(field)
                    val = cell.value.strip()
                    if val in duplicated_vals:
                        wrong_cells.append(schemas.MatchyWrongCell(message=f"{possible_fields[field]} should be unique. {val} already exist in database",rowIndex=cell.rowIndex,colIndex=cell.colIndex))
                wrong_cells.append(schemas.MatchyWrongCell(message=msg,rowIndex=int(cell.rowIndex),colIndex=int(cell.colIndex)))
        if errors or (warnings and not force_upload):
            return schemas.ImportResponse(errors=("\n").join(errors),warnings=("\n").join(warnings),wrongCells=wrong_cells,detail="Somthing went wrong",status_code=400)
        db.add_all(employees_to_add)
        db.flush()
        db.bulk_save_objects([models.EmployeeRole(employee_id=empl.id, role=role)for empl in employees_to_add for role in roles_per_email[empl.email]])
        tokens_to_add = []
        email_data = []
        for emp in employees_to_add:
            new_token = models.AccountActivation(employee_id = emp.id ,email = emp.email, status = enums.TokenStatus.Pending, token = uuid.uuid1())

            tokens_to_add.append(new_token)
            email_data.append(schemas.MailData(
                    emails=[emp.email],
                    body={"name": f"{emp.first_name} {emp.last_name}","token": new_token.token,},
                    subject="Confirm Account",
                    template=EmailTemplate.ConfirmAccount,
                )
            )
        db.bulk_save_objects(tokens_to_add)
        for email_datum in email_data:
            background_tasks.add_task(simple_send, email_datum)
        db.commit()
    except Exception as error:
        return schemas.BaseOut(status_code=400, detail=str(error))
    return schemas.ImportResponse(detail="File uploaded successfully", status_code=201)


def get_possible_fields():
    return schemas.ImportPossibleFields(possible_fields=options)


def upload(entry: schemas.MatchyUploadEntry,background_tasks: BackgroundTasks,db: Session,):
    employees = entry.lines
    if not employees:
        return schemas.BaseOut(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    missing_mandatory_fields = set(mandatory_fields.keys()) - employees[0].keys()
    if missing_mandatory_fields:
        return schemas.BaseOut(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Missing mandatory fields : {(', ').join(mandatory_fields[field] for field in missing_mandatory_fields)}")
    try:
        return validate_employees_data_and_upload(employees=employees,force_upload=entry.force_upload,db=db,background_tasks=background_tasks)
    except Exception as error:
        db.rollback()
        add_error(str(error), db)
        return schemas.BaseOut(status_code=400, detail=str(error))