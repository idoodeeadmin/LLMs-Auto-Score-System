from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ชุดข้อสอบใหม่" / "photo_clean_ชุดที่2"
OUTPUT = ROOT / "artifacts" / "q5-first10-rubric-audit"
ITEMS = [
    ("DS-137", 1, "0.50"), ("DS-138", 2, "0.75"),
    ("DS-139", 3, "0.00"), ("DS-140", 4, "0.00"),
    ("DS-141", 5, "1.00"), ("DS-142", 6, "0.75"),
    ("DS-143", 7, "0.00"), ("DS-144", 8, "0.00"),
    ("DS-145", 9, "1.00"), ("DS-146", 10, "0.00"),
]


def font(size: int, bold: bool = False):
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)


def make_page(page: int, entries: list[tuple[str, int, str]]) -> Path:
    width, height = 1640, 1580
    canvas = Image.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(canvas)
    draw.text((50, 28), f"Question 5 — First 10 answers / manual rubric audit (page {page})", font=font(28, True), fill="#0f3d31")
    card_w, card_h = 740, 710
    for pos, (sample_id, image_no, score) in enumerate(entries):
        col, row = pos % 2, pos // 2
        x, y = 50 + col * 780, 90 + row * 740
        draw.rounded_rectangle((x, y, x + card_w, y + card_h), radius=12, fill="white", outline="#cbd5e1", width=2)
        draw.text((x + 18, y + 16), f"{sample_id} | Excel: {score}", font=font(20, True), fill="#14532d")
        with Image.open(SOURCE / f"LINE_ALBUM_Photo2.1_260918_{image_no}.jpg") as image:
            image = image.convert("RGB")
            image.thumbnail((card_w - 36, card_h - 72), Image.Resampling.LANCZOS)
            canvas.paste(image, (x + (card_w - image.width) // 2, y + 56 + (card_h - 70 - image.height) // 2))
    path = OUTPUT / f"q5-first10-page-{page}.jpg"
    canvas.save(path, "JPEG", quality=94, optimize=True)
    return path


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for page, start in enumerate(range(0, len(ITEMS), 4), 1):
        print(make_page(page, ITEMS[start:start + 4]))


if __name__ == "__main__":
    main()
