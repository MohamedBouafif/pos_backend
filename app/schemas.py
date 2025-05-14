from datetime import datetime, date
from pydantic import BaseModel
from app.enums import ContractType, Gender
from typing import List
from app.enums import RoleType




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
    # zeyed n3abeha puisque bch tit3aba par defaut fil base de donne
    # created_on = Column(DateTime, nullable=False, server_default=func.now())

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