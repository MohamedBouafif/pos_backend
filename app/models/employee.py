from sqlalchemy import Column, Integer, String, Enum, DateTime, CheckConstraint, ForeignKey, Date, func
from ..database import Base
from app.enums import Gender, ContractType, AccountStatus

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=True)
    number = Column(Integer, nullable=False)
    birth_date = Column(Date, nullable=True)
    address = Column(String, nullable=True)
    cnss_number = Column(String, nullable=True)
    contract_type = Column(Enum(ContractType), nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    account_status = Column(Enum(AccountStatus), nullable=False, default=AccountStatus.Inactive)
    phone_number = Column(String, nullable=True)
    created_on = Column(DateTime, nullable=False, server_default=func.now())

    