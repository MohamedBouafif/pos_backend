from enum import Enum

class RoleType(Enum):
    ADMIN = "ADMIN"
    InventoryManager = "InventoryManager"
    Superuser = "Superuser"
    Vendor = "Vendor"