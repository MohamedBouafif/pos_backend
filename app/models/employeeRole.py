from sqlalchemy import Column, Integer, ForeignKey, Enum
from ..database import Base
from app.enums import RoleType

class EmployeeRole(Base):
    __tablename__ = "employee_roles"

    id = Column(Integer, primary_key = True, nullable = False)
    employee_id= Column(Integer, ForeignKey("employees.id"), nullable = False)  #it a one to many relationship (couple (employee_id , role_id) its the key)
    role = Column(Enum(RoleType), nullable = False)