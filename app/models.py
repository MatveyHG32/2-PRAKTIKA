from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Date,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Status(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks_owned = relationship(
        "Task", back_populates="owner", foreign_keys="Task.owner_id"
    )
    tasks_assigned = relationship(
        "Task", back_populates="assignee", foreign_keys="Task.assignee_id"
    )
    projects = relationship("Project", back_populates="owner")
    comments = relationship("Comment", back_populates="author")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(20), default="#6366F1")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="projects")
    tasks = relationship(
        "Task", back_populates="project", cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Enum(Priority), default=Priority.medium, nullable=False)
    status = Column(Enum(Status), default=Status.todo, nullable=False)
    due_date = Column(Date, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    owner = relationship(
        "User", back_populates="tasks_owned", foreign_keys=[owner_id]
    )
    assignee = relationship(
        "User", back_populates="tasks_assigned", foreign_keys=[assignee_id]
    )
    project = relationship("Project", back_populates="tasks")
    comments = relationship(
        "Comment", back_populates="task", cascade="all, delete-orphan"
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")
