"""Capture screenshots of the running app at desktop & mobile viewports.

Запуск:
    python scripts/capture_screens.py
Сохраняет PNG-файлы в docs/screenshots/.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8000"
OUT = Path(__file__).resolve().parent.parent / "docs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

DESKTOP = {"width": 1440, "height": 900}
MOBILE = {"width": 390, "height": 844, "device_scale_factor": 2, "is_mobile": True, "has_touch": True}


def login(page) -> None:
    page.goto(f"{BASE_URL}/login")
    page.fill('input[name="username"]', "matvey")
    page.fill('input[name="password"]', "matvey2026")
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")


def capture(page, path: str, out_name: str) -> None:
    page.goto(f"{BASE_URL}{path}")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(400)
    out = OUT / out_name
    page.screenshot(path=str(out), full_page=False)
    print(f"Saved {out}")


def main() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)

        # ---- Desktop ----
        ctx = browser.new_context(viewport=DESKTOP, locale="ru-RU")
        page = ctx.new_page()
        login(page)
        capture(page, "/", "web_01_dashboard.png")
        capture(page, "/tasks/2", "web_02_task_detail.png")
        capture(page, "/projects", "web_03_projects.png")
        capture(page, "/login", "web_04_login.png")
        ctx.close()

        # ---- Mobile ----
        ctx = browser.new_context(
            viewport={"width": MOBILE["width"], "height": MOBILE["height"]},
            device_scale_factor=MOBILE["device_scale_factor"],
            is_mobile=MOBILE["is_mobile"],
            has_touch=MOBILE["has_touch"],
            locale="ru-RU",
        )
        page = ctx.new_page()
        login(page)
        capture(page, "/", "mobile_01_dashboard.png")
        capture(page, "/tasks/2", "mobile_02_task_detail.png")
        capture(page, "/projects", "mobile_03_projects.png")
        capture(page, "/login", "mobile_04_login.png")
        ctx.close()

        browser.close()


if __name__ == "__main__":
    main()
