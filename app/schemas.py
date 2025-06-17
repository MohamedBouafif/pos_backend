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

class BaseOut(OurBaseModel):
    detail : str
    status_code: int
class PagedResponse(BaseOut):
    page_number: int
    page_size: int
    total_pages:int
    total_records: int
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
class EmployeesResponse(PagedResponse):
    list : List[EmployeeResponse]
class EmployeeEdit(EmployeeCreate):
    actual_password : str | None = None
class ConfirmAccount(OurBaseModel):
    confirm_code: str

class ForgetPassword(OurBaseModel):
    email:str

class ResetPassword(OurBaseModel):
    reset_code: str
    password : str
    confirm_password:str

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
    
class ImportPossibleFields(OurBaseModel):
    possible_fields: List[MatchyOption] = []

class MatchyCell(OurBaseModel):
    value: str
    rowIndex: int
    colIndex: int

class MatchyUploadEntry(OurBaseModel):
    lines: List[Dict[str, MatchyCell]] # [ {cnss_number: {40, 1, 1}, {roles: {Admin, vendor, 1, 2}}, {emp 2}, {emp 3}] # enou emp lkol en tant que dict 3andhom nafs l keys
    forceUpload: Optional[bool] = False
class MatchyWrongCell(OurBaseModel):
    message: str
    rowIndex: int
    colIndex: int
class ImportResponse(BaseOut):
    errors:Optional[str] = None
    warnings: Optional[str] = None
    wrongCells:Optional[list[MatchyWrongCell]] = []


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
