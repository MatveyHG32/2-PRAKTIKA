"""Task Planner — учебное веб-приложение на FastAPI + SQLite.

Запуск в режиме разработки:
    uvicorn main:app --reload
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.database import Base, engine
from app.routers import auth, pages, projects, tasks

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Планировщик задач",
    description="Учебный проект (2 курс СПО) — планировщик задач на FastAPI + SQLite.",
    version="1.0.0",
)

app.add_middleware(
    SessionMiddleware, secret_key="task-planner-secret-please-change-me"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(projects.router)


@app.get("/healthz")
def healthcheck():
    return {"status": "ok"}
