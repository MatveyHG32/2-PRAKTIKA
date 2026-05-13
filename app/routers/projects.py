from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project, User
from app.deps import require_login

router = APIRouter(prefix="/projects")


@router.post("/new")
@router.post("/create")
def create_project(
    name: str = Form(...),
    description: str = Form(""),
    color: str = Form("#6366F1"),
    user: User = Depends(require_login),
    db: Session = Depends(get_db),
):
    project = Project(
        name=name,
        description=description,
        color=color,
        owner_id=user.id,
    )
    db.add(project)
    db.commit()
    return RedirectResponse(url="/projects", status_code=303)


@router.post("/{project_id}/delete")
def delete_project(
    project_id: int,
    user: User = Depends(require_login),
    db: Session = Depends(get_db),
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.owner_id == user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return RedirectResponse(url="/projects", status_code=303)
