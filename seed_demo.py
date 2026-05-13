"""Seed скрипт: создает демо-пользователей, проекты и задачи.

Запуск:  python seed_demo.py
"""
from datetime import date, timedelta

from app.database import Base, SessionLocal, engine
from app.models import User, Project, Task, Comment, Priority, Status
from app.security import hash_password


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("База уже заполнена, пропускаю seed.")
            return

        # Пользователи
        matvey = User(
            username="matvey",
            email="matvey@example.com",
            full_name="Магасумов Матвей",
            password_hash=hash_password("matvey2026"),
        )
        anna = User(
            username="anna",
            email="anna@example.com",
            full_name="Анна Иванова",
            password_hash=hash_password("anna2026"),
        )
        sergey = User(
            username="sergey",
            email="sergey@example.com",
            full_name="Сергей Петров",
            password_hash=hash_password("sergey2026"),
        )
        db.add_all([matvey, anna, sergey])
        db.commit()
        for u in (matvey, anna, sergey):
            db.refresh(u)

        # Проекты
        practice = Project(
            name="Учебная практика",
            description="Разработка веб-приложения «Планировщик задач»",
            color="#6366F1",
            owner_id=matvey.id,
        )
        course = Project(
            name="Курсовая работа",
            description="Подготовка курсовой по веб-разработке",
            color="#10B981",
            owner_id=matvey.id,
        )
        personal = Project(
            name="Личные дела",
            description="Бытовые задачи и личные планы",
            color="#F59E0B",
            owner_id=matvey.id,
        )
        db.add_all([practice, course, personal])
        db.commit()
        for p in (practice, course, personal):
            db.refresh(p)

        today = date.today()

        tasks = [
            Task(
                title="Сделать дизайн-макет в Figma",
                description="Подготовить 2 веб-фрейма и 2 мобильных фрейма для планировщика задач.",
                priority=Priority.high,
                status=Status.done,
                due_date=today - timedelta(days=2),
                owner_id=matvey.id,
                assignee_id=matvey.id,
                project_id=practice.id,
            ),
            Task(
                title="Сверстать главный экран дашборда",
                description="Реализовать карточный канбан с тремя колонками, чипами приоритета и адаптивом.",
                priority=Priority.high,
                status=Status.in_progress,
                due_date=today + timedelta(days=1),
                owner_id=matvey.id,
                assignee_id=matvey.id,
                project_id=practice.id,
            ),
            Task(
                title="Подключить SQLite и SQLAlchemy",
                description="Описать модели User, Project, Task, Comment и связи между ними.",
                priority=Priority.medium,
                status=Status.done,
                due_date=today - timedelta(days=1),
                owner_id=matvey.id,
                assignee_id=matvey.id,
                project_id=practice.id,
            ),
            Task(
                title="Написать отчёт по практике 1",
                description="Подготовить документ в Word по утверждённой структуре.",
                priority=Priority.medium,
                status=Status.todo,
                due_date=today + timedelta(days=4),
                owner_id=matvey.id,
                assignee_id=matvey.id,
                project_id=practice.id,
            ),
            Task(
                title="Назначить ревью Анне",
                description="Попросить однокурсницу проверить интерфейс перед сдачей.",
                priority=Priority.low,
                status=Status.todo,
                due_date=today + timedelta(days=3),
                owner_id=matvey.id,
                assignee_id=anna.id,
                project_id=practice.id,
            ),
            Task(
                title="Найти 10 источников для теоретической части",
                description="Книги, статьи, документация по FastAPI и проектированию интерфейсов.",
                priority=Priority.medium,
                status=Status.in_progress,
                due_date=today + timedelta(days=7),
                owner_id=matvey.id,
                assignee_id=matvey.id,
                project_id=course.id,
            ),
            Task(
                title="Купить продукты на неделю",
                description="Список: овощи, крупы, кофе.",
                priority=Priority.low,
                status=Status.todo,
                due_date=today,
                owner_id=matvey.id,
                assignee_id=matvey.id,
                project_id=personal.id,
            ),
            Task(
                title="Записаться к стоматологу",
                description="Профилактический осмотр.",
                priority=Priority.low,
                status=Status.done,
                due_date=today - timedelta(days=5),
                owner_id=matvey.id,
                assignee_id=matvey.id,
                project_id=personal.id,
            ),
            Task(
                title="Проверить вёрстку мобильной версии",
                description="Убедиться, что доска корректно отображается на iPhone SE и Android.",
                priority=Priority.high,
                status=Status.todo,
                due_date=today + timedelta(days=2),
                owner_id=matvey.id,
                assignee_id=sergey.id,
                project_id=practice.id,
            ),
        ]
        db.add_all(tasks)
        db.commit()
        for t in tasks:
            db.refresh(t)

        # Комментарии
        comments = [
            Comment(
                text="Поправил отступы и цвета — теперь выглядит аккуратнее.",
                task_id=tasks[1].id,
                author_id=matvey.id,
            ),
            Comment(
                text="Согласен, можно ещё добавить hover-состояния для карточек.",
                task_id=tasks[1].id,
                author_id=anna.id,
            ),
            Comment(
                text="Я возьму ревью на себя, посмотрю вечером.",
                task_id=tasks[4].id,
                author_id=anna.id,
            ),
        ]
        db.add_all(comments)
        db.commit()
        print("Демо-данные созданы.")
        print("Логин: matvey / Пароль: matvey2026")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
