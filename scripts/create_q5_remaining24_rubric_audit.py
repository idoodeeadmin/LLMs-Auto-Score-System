from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ชุดข้อสอบใหม่" / "photo_clean_ชุดที่2"
OUTPUT = ROOT / "artifacts" / "q5-remaining24-rubric-audit"
HUMAN_SCORES = {
    147: "1.00", 148: "0.75", 149: "0.00", 150: "0.25",
    151: "0.00", 152: "1.00", 153: "0.00", 154: "1.00",
    155: "0.75", 156: "1.00", 157: "1.00", 158: "0.75",
    159: "1.00", 160: "0.00", 161: "0.25", 162: "0.00",
    163: "1.00", 164: "1.00", 165: "0.75", 166: "0.75",
    167: "0.00", 168: "1.00", 169: "0.75", 170: "1.00",
}


def font(size: int, bold: bool = False):
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)


def make_page(page: int, ids: list[int]) -> Path:
    width, height = 1640, 1580
    canvas = Image.new("RGB", (width, height), "#f8fafc")
    draw = ImageDraw.Draw(canvas)
    draw.text((50, 28), f"Question 5 — Remaining answers / manual rubric audit (page {page})", font=font(28, True), fill="#0f3d31")
    card_w, card_h = 740, 710
    for pos, sample_number in enumerate(ids):
        col, row = pos % 2, pos // 2
        x, y = 50 + col * 780, 90 + row * 740
        draw.rounded_rectangle((x, y, x + card_w, y + card_h), radius=12, fill="white", outline="#cbd5e1", width=2)
        image_no = sample_number - 136
        draw.text((x + 18, y + 16), f"DS-{sample_number} | Excel: {HUMAN_SCORES[sample_number]}", font=font(20, True), fill="#14532d")
        path = SOURCE / f"LINE_ALBUM_Photo2.1_260918_{image_no}.jpg"
        with Image.open(path) as image:
            image = image.convert("RGB")
            image.thumbnail((card_w - 36, card_h - 72), Image.Resampling.LANCZOS)
            canvas.paste(image, (x + (card_w - image.width) // 2, y + 56 + (card_h - 70 - image.height) // 2))
    output = OUTPUT / f"q5-remaining-page-{page}.jpg"
    canvas.save(output, "JPEG", quality=94, optimize=True)
    return output


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    sample_ids = list(HUMAN_SCORES)
    for page, start in enumerate(range(0, len(sample_ids), 4), 1):
        print(make_page(page, sample_ids[start:start + 4]))


if __name__ == "__main__":
    main()
