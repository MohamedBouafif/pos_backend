from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models


def get_error_message(error_message, error_keys = {}):
    for error_key in error_keys:
        if error_key in error_message:
            return error_keys[error_key] # ken yti7ou 7ajtin ya3tik 7aja kahaw (l7aja loula ili ta7et khw) 
    return "Something went wrong" 

def add_error(text, db: Session):
    try:
        db.add(models.Error(
            text = text
        ))
        db.commit()
    except Exception as  e :
        #alternative solution bech ken db tahet najem nil9a l mochkla
        raise HTTPException(status_code = 500,detail ="Something went wrong")

