from datetime import date, datetime, timedelta
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.database import get_db
from app.models import Task, Project, User, Status, Priority, Comment
from app.deps import get_current_user, require_login

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _compute_notif_count(db: Session, user: User) -> int:
    today = date.today()
    cnt = (
        db.query(Task)
        .filter(
            or_(Task.owner_id == user.id, Task.assignee_id == user.id),
            Task.due_date != None,
            Task.due_date <= today,
            Task.status != Status.done,
        )
        .count()
    )
    return cnt


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    tasks = (
        db.query(Task)
        .filter(or_(Task.owner_id == user.id, Task.assignee_id == user.id))
        .order_by(Task.due_date.is_(None), Task.due_date.asc(), Task.id.desc())
        .all()
    )
    projects = db.query(Project).filter(Project.owner_id == user.id).all()
    users = db.query(User).all()
    today = date.today()
    stats = {
        "total": len(tasks),
        "todo": sum(1 for t in tasks if t.status == Status.todo),
        "in_progress": sum(1 for t in tasks if t.status == Status.in_progress),
        "done": sum(1 for t in tasks if t.status == Status.done),
        "overdue": sum(
            1 for t in tasks
            if t.due_date and t.due_date < today and t.status != Status.done
        ),
    }
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "tasks": tasks,
            "projects": projects,
            "users": users,
            "stats": stats,
            "today": today,
            "active_page": "dashboard",
            "notif_count": _compute_notif_count(db, user),
        },
    )


@router.get("/tasks/{task_id}", response_class=HTMLResponse)
def task_detail(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_login),
):
    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            or_(Task.owner_id == user.id, Task.assignee_id == user.id),
        )
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    projects = db.query(Project).filter(Project.owner_id == user.id).all()
    users = db.query(User).all()
    return templates.TemplateResponse(
        "task_detail.html",
        {
            "request": request,
            "user": user,
            "task": task,
            "projects": projects,
            "users": users,
            "active_page": "dashboard",
            "notif_count": _compute_notif_count(db, user),
        },
    )


@router.get("/projects", response_class=HTMLResponse)
def projects_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_login),
):
    projects = db.query(Project).filter(Project.owner_id == user.id).all()
    project_data = []

    for p in projects:
        total = len(p.tasks)
        done = sum(1 for t in p.tasks if t.status == Status.done)
        preview = [t for t in p.tasks if t.status != Status.done][:3]
        if not preview:
            preview = p.tasks[:3]
        project_data.append(
            {
                "project": p,
                "total": total,
                "done": done,
                "preview_tasks": preview,
            }
        )

    return templates.TemplateResponse(
        "projects.html",
        {
            "request": request,
            "user": user,
            "project_data": project_data,
            "active_page": "projects",
            "notif_count": _compute_notif_count(db, user),
        },
    )


@router.get("/notifications", response_class=HTMLResponse)
def notifications_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_login),
):
    today = date.today()
    recent_cutoff = datetime.utcnow() - timedelta(days=7)

    my_tasks_q = db.query(Task).filter(
        or_(Task.owner_id == user.id, Task.assignee_id == user.id)
    )

    overdue_tasks = (
        my_tasks_q.filter(
            Task.due_date != None,
            Task.due_date < today,
            Task.status != Status.done,
        )
        .order_by(Task.due_date.asc())
        .all()
    )
    today_tasks = (
        my_tasks_q.filter(Task.due_date == today, Task.status != Status.done)
        .order_by(Task.id.desc())
        .all()
    )
    soon_tasks = (
        my_tasks_q.filter(
            Task.due_date != None,
            Task.due_date > today,
            Task.due_date <= today + timedelta(days=7),
            Task.status != Status.done,
        )
        .order_by(Task.due_date.asc())
        .all()
    )
    assigned_tasks = (
        db.query(Task)
        .filter(
            Task.assignee_id == user.id,
            Task.owner_id != user.id,
            Task.created_at >= recent_cutoff,
        )
        .order_by(desc(Task.created_at))
        .limit(5)
        .all()
    )
    recent_comments = (
        db.query(Comment)
        .join(Task, Comment.task_id == Task.id)
        .filter(
            or_(Task.owner_id == user.id, Task.assignee_id == user.id),
            Comment.author_id != user.id,
            Comment.created_at >= recent_cutoff,
        )
        .order_by(desc(Comment.created_at))
        .limit(5)
        .all()
    )

    notif_stats = {
        "overdue": len(overdue_tasks),
        "today": len(today_tasks),
        "soon": len(soon_tasks),
        "assigned": len(assigned_tasks),
        "comments": len(recent_comments),
    }
    notif_count = (
        notif_stats["overdue"]
        + notif_stats["today"]
        + notif_stats["assigned"]
        + notif_stats["comments"]
    )

    return templates.TemplateResponse(
        "notifications.html",
        {
            "request": request,
            "user": user,
            "overdue_tasks": overdue_tasks,
            "today_tasks": today_tasks,
            "soon_tasks": soon_tasks,
            "assigned_tasks": assigned_tasks,
            "recent_comments": recent_comments,
            "notif_stats": notif_stats,
            "notif_count": notif_count,
            "active_page": "notifications",
        },
    )
