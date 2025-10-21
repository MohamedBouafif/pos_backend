from enum import Enum
#ay enum nheb netchek il values mte3ou nwali nheriti min hedha
class BasicEnum(str, Enum):
    @classmethod
    def getPossibleValues(cls):#Returns a list of all possible values in the enum
        return [val.value for val in cls]
    
    @classmethod
    def is_valid(cls, field):
        for val in cls:
            if field.strip().upper() == val.value.upper():
                return val
            
        return None
    

    #enums are not  instanciated we pass cls instead of self in function params