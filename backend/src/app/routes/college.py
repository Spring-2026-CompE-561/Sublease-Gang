from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repository.college import get_all_colleges, get_college
from app.repository.exceptions import ResourceNotFoundError
from app.schemas.college import CollegeRead

router = APIRouter(prefix="/colleges", tags=["colleges"])


@router.get("/", response_model=list[CollegeRead])
def list_colleges(db: Session = Depends(get_db)):
    return get_all_colleges(db)


@router.get("/{college_id}", response_model=CollegeRead)
def get_college_by_id(college_id: int, db: Session = Depends(get_db)):
    college = get_college(db, college_id)
    if college is None:
        raise ResourceNotFoundError("College not found")
    return college