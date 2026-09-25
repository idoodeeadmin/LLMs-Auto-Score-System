from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ชุดข้อสอบใหม่" / "photoชุดที่2"
OUTPUT = ROOT / "artifacts" / "q5-original-score-audit"
ITEMS = [
    ("DS-138", 2, "0.75"), ("DS-142", 6, "0.75"),
    ("DS-148", 12, "0.75"), ("DS-155", 19, "0.75"),
    ("DS-158", 22, "0.75"), ("DS-165", 29, "0.75"),
    ("DS-166", 30, "0.75"), ("DS-169", 33, "0.75"),
]


def get_font(size: int, bold: bool = False):
    filename = "segoeuib.ttf" if bold else "segoeui.ttf"
    path = Path("C:/Windows/Fonts") / filename
    return ImageFont.truetype(path, size) if path.exists() else ImageFont.load_default()


def make_sheet(page: int, entries: list[tuple[str, int, str]]) -> Path:
    width, height = 1640, 1580
    sheet = Image.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(sheet)
    draw.text((50, 28), f"Question 5 — Original images / score audit (page {page})", font=get_font(28, True), fill="#0f3d31")
    card_w, card_h = 740, 710
    for position, (sample_id, student_index, score) in enumerate(entries):
        col, row = position % 2, position // 2
        x, y = 50 + col * 780, 90 + row * 740
        draw.rounded_rectangle((x, y, x + card_w, y + card_h), radius=12, fill="white", outline="#cbd5e1", width=2)
        draw.text((x + 18, y + 16), f"{sample_id} | Excel score: {score}", font=get_font(20, True), fill="#14532d")
        image_path = SOURCE / f"LINE_ALBUM_Photo2.1_260918_{student_index}.jpg"
        with Image.open(image_path) as source:
            source = source.convert("RGB")
            source.thumbnail((card_w - 36, card_h - 72), Image.Resampling.LANCZOS)
            px = x + (card_w - source.width) // 2
            py = y + 56 + (card_h - 70 - source.height) // 2
            sheet.paste(source, (px, py))
    path = OUTPUT / f"q5-original-scores-page-{page}.jpg"
    sheet.save(path, "JPEG", quality=94, optimize=True)
    return path


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for page, start in enumerate(range(0, len(ITEMS), 4), start=1):
        print(make_sheet(page, ITEMS[start:start + 4]))


if __name__ == "__main__":
    main()
