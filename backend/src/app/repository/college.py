from sqlalchemy.orm import Session
from app.models.college import College


def get_all_colleges(db: Session) -> list[College]:
    return db.query(College).order_by(College.name).all()


def get_college(db: Session, college_id: int) -> College | None:
    return db.query(College).filter(College.id == college_id).first()