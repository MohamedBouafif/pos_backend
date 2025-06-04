from datetime import datetime, date
from pydantic import BaseModel
from app.enums import ContractType, Gender
from typing import Dict, List, Optional
from app.enums import RoleType
from app.enums.matchyComparer import Comparer
from app.enums.matchyConditionProperty import ConditionProperty
from app.enums.matchyFieldType import FieldType

class OurBaseModel(BaseModel):
    class Config:
        orm_mode = True

class EmployeeBase(OurBaseModel):
    first_name :str
    last_name :str
    email :str
    roles : List[RoleType]
    number : int
    birth_date : date | None = None
    address : str  | None = None
    cnss_number : str  | None = None
    contract_type : ContractType
    gender : Gender
    phone_number : str | None = None

class EmployeeCreate(EmployeeBase):
    password :str | None = None
    confirm_password : str | None = None
class EmployeeResponse(EmployeeBase):
    id : int
    created_on : datetime

class ConfirmAccount(OurBaseModel):
    confirm_code: str

class BaseOut(OurBaseModel):
    detail : str
    status_code: int
 
class MatchyCondition(OurBaseModel):
    property : ConditionProperty
    comparer : Optional[Comparer] = None
    value: int| float | str |List[str]
    custom_fail_message: Optional[str] = None

class MatchyOption(OurBaseModel):
    display_value : str #displayed to user
    value : Optional[str] = None #name of the variable in the db
    mendatory : Optional[bool] = False #true if not nullable
    type : FieldType
    conditions: Optional[List[MatchyCondition]] = []

class MatchyCell(OurBaseModel):
    value: str
    rowIndex: int
    colIndex: int

class MatchyUploadEntry(OurBaseModel):
    lines: List[Dict[str, MatchyCell]] # [ {cnss_number: {40, 1, 1}, {roles: {Admin, vendor, 1, 2}}, {emp 2}, {emp 3}] # enou emp lkol en tant que dict 3andhom nafs l keys

class MatchyWrongCell(OurBaseModel):
    message: str
    rowIndex: int
    colIndex: int
class ImportResponse(OurBaseModel):
    errors:str 
    warnings: str
    wrongCells:list[MatchyWrongCell]