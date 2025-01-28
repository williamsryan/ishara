from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Option
from app.schemas import OptionSchema

router = APIRouter()

@router.get("/options", response_model=list[OptionSchema])
def get_options(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Retrieve all options from the database.
    """
    options = db.query(Option).offset(skip).limit(limit).all()
    return options

@router.get("/options/{option_id}", response_model=OptionSchema)
def read_option(option_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific option by ID.
    """
    option = db.query(Option).filter(Option.id == option_id).first()
    if option is None:
        raise HTTPException(status_code=404, detail="Option not found")
    return option
    