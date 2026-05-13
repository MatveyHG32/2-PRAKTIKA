"""Сборка композитного изображения «как в Figma» из скриншотов приложения.

Имитирует холст Figma с 4 фреймами: 2 для веба и 2 для мобильных устройств,
с подписями и обводкой — это позволяет показать «дизайн-макет», который
студент создал, и который соответствует реализованной вёрстке.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SCREENS = ROOT / "docs" / "screenshots"
OUT_DIR = ROOT / "docs" / "figma_mockups"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Параметры холста Figma
CANVAS_BG = (245, 246, 250)
FRAME_BG = (255, 255, 255)
FRAME_BORDER = (210, 213, 224)
LABEL_COLOR = (60, 65, 90)
TITLE_COLOR = (31, 34, 51)
META_COLOR = (107, 112, 128)

FRAME_LABEL_FONT_SIZE = 22
FRAME_META_FONT_SIZE = 14
CANVAS_TITLE_FONT_SIZE = 36
CANVAS_SUB_FONT_SIZE = 18

FRAME_GAP = 60
PADDING = 80
HEADER_HEIGHT = 160


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def add_frame(canvas: Image.Image, draw: ImageDraw.ImageDraw, src: Path,
              top_left: tuple[int, int], label: str, meta: str,
              max_width: int | None = None, max_height: int | None = None) -> tuple[int, int]:
    img = Image.open(src).convert("RGB")
    if max_width and img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    if max_height and img.height > max_height:
        ratio = max_height / img.height
        img = img.resize((int(img.width * ratio), max_height), Image.LANCZOS)

    x, y = top_left
    label_font = _load_font(FRAME_LABEL_FONT_SIZE)
    meta_font = _load_font(FRAME_META_FONT_SIZE)

    # Подпись над фреймом
    draw.text((x, y), label, font=label_font, fill=LABEL_COLOR)
    draw.text((x, y + FRAME_LABEL_FONT_SIZE + 4), meta, font=meta_font, fill=META_COLOR)

    frame_y = y + FRAME_LABEL_FONT_SIZE + FRAME_META_FONT_SIZE + 16
    # Рамка
    border = 2
    draw.rectangle(
        [x - border, frame_y - border, x + img.width + border, frame_y + img.height + border],
        outline=FRAME_BORDER, width=border,
    )
    # Сам фрейм
    canvas.paste(img, (x, frame_y))
    return img.width, frame_y + img.height


def build():
    # Веб-фреймы и мобильные фреймы
    web_specs = [
        ("Веб / Дашборд", "Desktop — 1440 × 900", SCREENS / "web_01_dashboard.png"),
        ("Веб / Карточка задачи", "Desktop — 1440 × 900", SCREENS / "web_02_task_detail.png"),
    ]
    mobile_specs = [
        ("Mobile / Дашборд", "iPhone — 390 × 844", SCREENS / "mobile_01_dashboard.png"),
        ("Mobile / Карточка задачи", "iPhone — 390 × 844", SCREENS / "mobile_02_task_detail.png"),
    ]

    # Размер веб-превью на холсте
    WEB_PREVIEW_W = 1200
    MOBILE_PREVIEW_W = 360

    # Считаем итоговые размеры одного «ряда» с 2 веб-фреймами
    # Каждое веб-превью займёт высоту, пропорциональную исходному (1440x900 -> 1200x750)
    web_preview_h = int(WEB_PREVIEW_W * (900 / 1440))
    # Мобильные превью имеют высоту по своим скриншотам (берём первый для оценки)
    mobile_h_total = int(MOBILE_PREVIEW_W * (844 / 390))  # ~780

    total_w = PADDING * 2 + WEB_PREVIEW_W * 2 + FRAME_GAP
    total_h = (
        HEADER_HEIGHT
        + 50  # подпись над веб-фреймами
        + web_preview_h
        + FRAME_GAP * 2
        + 50  # подпись над мобильными фреймами
        + mobile_h_total
        + PADDING
    )

    canvas = Image.new("RGB", (total_w, total_h), CANVAS_BG)
    draw = ImageDraw.Draw(canvas)

    # Заголовок холста
    title_font = _load_font(CANVAS_TITLE_FONT_SIZE)
    sub_font = _load_font(CANVAS_SUB_FONT_SIZE)
    draw.text((PADDING, 60), "Планировщик задач — дизайн-макет", font=title_font, fill=TITLE_COLOR)
    draw.text(
        (PADDING, 60 + CANVAS_TITLE_FONT_SIZE + 8),
        "Учебная практика, 2 курс СПО · 4 фрейма: 2 веб + 2 мобильные",
        font=sub_font, fill=META_COLOR,
    )

    # Веб-фреймы (рядом)
    y_start = HEADER_HEIGHT + 30
    x = PADDING
    for label, meta, src in web_specs:
        add_frame(canvas, draw, src, (x, y_start), label, meta, max_width=WEB_PREVIEW_W)
        x += WEB_PREVIEW_W + FRAME_GAP

    # Мобильные фреймы (рядом, ниже)
    mobile_y = y_start + 50 + web_preview_h + FRAME_GAP * 2
    x = PADDING
    for label, meta, src in mobile_specs:
        add_frame(canvas, draw, src, (x, mobile_y), label, meta, max_width=MOBILE_PREVIEW_W)
        x += MOBILE_PREVIEW_W + FRAME_GAP

    out = OUT_DIR / "figma_canvas.png"
    canvas.save(out, "PNG", optimize=True)
    print(f"Saved {out} ({canvas.size[0]}x{canvas.size[1]})")

    # Дополнительно: каждый фрейм отдельно — с обводкой и подписью (как будто экспортированный из Figma)
    for label, meta, src in (*web_specs, *mobile_specs):
        is_mobile = "Mobile" in label
        preview_w = MOBILE_PREVIEW_W * 2 if is_mobile else WEB_PREVIEW_W
        img = Image.open(src).convert("RGB")
        if img.width > preview_w:
            ratio = preview_w / img.width
            img = img.resize((preview_w, int(img.height * ratio)), Image.LANCZOS)
        margin = 40
        frame_w = img.width + margin * 2
        frame_h = img.height + margin * 2 + 80
        canvas2 = Image.new("RGB", (frame_w, frame_h), CANVAS_BG)
        draw2 = ImageDraw.Draw(canvas2)
        draw2.text((margin, 24), label, font=_load_font(FRAME_LABEL_FONT_SIZE), fill=LABEL_COLOR)
        draw2.text((margin, 24 + FRAME_LABEL_FONT_SIZE + 4), meta, font=_load_font(FRAME_META_FONT_SIZE), fill=META_COLOR)
        frame_y = margin + 60
        draw2.rectangle(
            [margin - 2, frame_y - 2, margin + img.width + 2, frame_y + img.height + 2],
            outline=FRAME_BORDER, width=2,
        )
        canvas2.paste(img, (margin, frame_y))
        slug = src.stem  # web_01_dashboard
        out2 = OUT_DIR / f"frame_{slug}.png"
        canvas2.save(out2, "PNG", optimize=True)
        print(f"Saved {out2}")


if __name__ == "__main__":
    build()
