from enum import Enum

class AccountStatus(Enum):
    Active = "Active"
    Inactive = "Inactive" # email not confirmed
    # Blocked = "Blocked" cannot access the plateforme because he letf the company