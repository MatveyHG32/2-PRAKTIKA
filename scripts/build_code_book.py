"""Сборка одностраничного HTML-«листинга кода» проекта для видео-обзора."""
from pathlib import Path
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, TextLexer
from pygments.formatters import HtmlFormatter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "code_book.html"

# Какие файлы и в каком порядке показывать.
FILES = [
    ("main.py",                                  "Точка входа: создание FastAPI-приложения, middleware и подключение роутеров"),
    ("requirements.txt",                         "Зависимости проекта"),
    ("seed_demo.py",                             "Скрипт заливки демонстрационных данных в SQLite"),
    ("app/database.py",                          "Настройка SQLAlchemy и сессии БД"),
    ("app/models.py",                            "ORM-модели: User, Project, Task, Comment + Enum-ы"),
    ("app/security.py",                          "Хеширование паролей через bcrypt"),
    ("app/deps.py",                              "Зависимости FastAPI: получение текущего пользователя"),
    ("app/routers/auth.py",                      "Регистрация, вход, выход (сессии Starlette)"),
    ("app/routers/pages.py",                     "GET-страницы: дашборд, задача, проекты"),
    ("app/routers/tasks.py",                     "CRUD задач и комментариев"),
    ("app/routers/projects.py",                  "CRUD проектов"),
    ("templates/base.html",                      "Базовый шаблон Jinja2 со «шапкой» сайта"),
    ("templates/login.html",                     "Страница входа"),
    ("templates/dashboard.html",                 "Дашборд с канбан-доской и модалкой создания задачи"),
    ("templates/task_detail.html",               "Страница карточки задачи + комментарии"),
    ("templates/projects.html",                  "Страница проектов с прогресс-барами"),
    ("static/js/app.js",                         "Минимальный JS для модальных окон"),
]

CSS_OVERRIDES = """
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: 'Segoe UI', 'Inter', system-ui, sans-serif;
    background: #0f1115;
    color: #e6e8eb;
}
.container { max-width: 1100px; margin: 0 auto; padding: 40px 24px 80px; }
header.proj {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    color: #fff;
    padding: 56px 24px;
    text-align: center;
}
header.proj h1 { margin: 0; font-size: 36px; }
header.proj p { margin: 12px 0 0; font-size: 18px; opacity: .9; }
section.file { margin-top: 56px; }
section.file h2 {
    color: #e6e8eb;
    font-size: 22px;
    border-bottom: 2px solid #6366f1;
    padding-bottom: 8px;
    margin-bottom: 4px;
    font-family: 'JetBrains Mono', 'Consolas', monospace;
}
section.file .desc {
    color: #9aa3b0;
    font-size: 14px;
    margin-bottom: 16px;
}
.highlight {
    background: #1c1f26 !important;
    border-radius: 10px;
    padding: 16px 18px;
    overflow-x: auto;
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 13px;
    line-height: 1.55;
}
.highlight pre { margin: 0; }
.linenos { color: #5b6473; padding-right: 14px; user-select: none; }
.toc {
    background: #1c1f26;
    padding: 18px 22px;
    border-radius: 10px;
    margin-top: 32px;
}
.toc h2 { margin: 0 0 10px; font-size: 18px; }
.toc ol { padding-left: 20px; margin: 0; }
.toc li { padding: 4px 0; }
.toc a { color: #8b8df1; text-decoration: none; }
.toc a:hover { color: #c4c5ff; }
"""

HEADER = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Планировщик задач — листинг кода</title>
<style>
{pygments_css}
{overrides}
</style>
</head>
<body>
<header class="proj">
    <h1>Планировщик задач — листинг кода</h1>
    <p>FastAPI + SQLite + Jinja2 + чистый CSS&nbsp;·&nbsp;Магасумов М. М.&nbsp;·&nbsp;ИСП(спо)-209-1</p>
</header>
<div class="container">
<div class="toc">
<h2>Содержание</h2>
<ol>
{toc_items}
</ol>
</div>
"""

FILE_BLOCK = """
<section class="file" id="{anchor}">
    <h2>{path}</h2>
    <div class="desc">{desc}</div>
    {body}
</section>
"""

FOOTER = "</div></body></html>"


def main():
    formatter = HtmlFormatter(style="monokai", linenos="table", cssclass="highlight")
    pygments_css = formatter.get_style_defs(".highlight")

    toc_items = []
    for path, desc in FILES:
        anchor = path.replace("/", "_").replace(".", "_")
        toc_items.append(f'<li><a href="#{anchor}">{path}</a> — <em>{desc}</em></li>')

    blocks = []
    for path, desc in FILES:
        anchor = path.replace("/", "_").replace(".", "_")
        full_path = ROOT / path
        if not full_path.exists():
            print(f"[skip] {path} — нет на диске")
            continue
        code = full_path.read_text(encoding="utf-8", errors="replace")
        try:
            lexer = get_lexer_for_filename(path, code, stripnl=False)
        except Exception:
            lexer = TextLexer(stripnl=False)
        body = highlight(code, lexer, formatter)
        blocks.append(FILE_BLOCK.format(
            anchor=anchor, path=path, desc=desc, body=body))

    html = HEADER.format(
        pygments_css=pygments_css,
        overrides=CSS_OVERRIDES,
        toc_items="\n".join(toc_items),
    ) + "\n".join(blocks) + FOOTER

    OUT.write_text(html, encoding="utf-8")
    print(f"Saved {OUT}  ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
