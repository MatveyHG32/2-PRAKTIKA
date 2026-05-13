from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User


def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


def require_login(
    request: Request, db: Session = Depends(get_db)
) -> User:
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login required",
        )
    return user
