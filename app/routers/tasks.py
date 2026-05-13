from datetime import date
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task, Comment, User, Project, Priority, Status
from app.deps import require_login

router = APIRouter(prefix="/tasks")


def _parse_optional_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _parse_optional_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


@router.post("/create")
def create_task(
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("medium"),
    status: str = Form("todo"),
    due_date: str = Form(""),
    project_id: str = Form(""),
    assignee_id: str = Form(""),
    user: User = Depends(require_login),
    db: Session = Depends(get_db),
):
    task = Task(
        title=title,
        description=description,
        priority=Priority(priority),
        status=Status(status),
        due_date=_parse_optional_date(due_date),
        project_id=_parse_optional_int(project_id),
        assignee_id=_parse_optional_int(assignee_id),
        owner_id=user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return RedirectResponse(url=f"/tasks/{task.id}", status_code=303)


@router.post("/{task_id}/update")
def update_task(
    task_id: int,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("medium"),
    status: str = Form("todo"),
    due_date: str = Form(""),
    project_id: str = Form(""),
    assignee_id: str = Form(""),
    user: User = Depends(require_login),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task or (task.owner_id != user.id and task.assignee_id != user.id):
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = title
    task.description = description
    task.priority = Priority(priority)
    task.status = Status(status)
    task.due_date = _parse_optional_date(due_date)
    task.project_id = _parse_optional_int(project_id)
    task.assignee_id = _parse_optional_int(assignee_id)
    db.commit()
    return RedirectResponse(url=f"/tasks/{task_id}", status_code=303)


@router.post("/{task_id}/status")
def change_status(
    task_id: int,
    status: str = Form(...),
    user: User = Depends(require_login),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task or (task.owner_id != user.id and task.assignee_id != user.id):
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = Status(status)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@router.post("/{task_id}/delete")
def delete_task(
    task_id: int,
    user: User = Depends(require_login),
    db: Session = Depends(get_db),
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.owner_id == user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@router.post("/{task_id}/comments")
def add_comment(
    task_id: int,
    text: str = Form(...),
    user: User = Depends(require_login),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    comment = Comment(text=text, task_id=task_id, author_id=user.id)
    db.add(comment)
    db.commit()
    return RedirectResponse(url=f"/tasks/{task_id}", status_code=303)
