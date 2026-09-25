from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public" / "answer-keys" / "q5-array-bst-answer-key.png"
VALUES = {0: "9", 1: "5", 2: "16", 5: "10", 6: "76", 12: "13", 13: "58", 14: "92", 25: "11", 26: "15", 29: "80", 30: "99"}


def font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def draw_row(draw, start, end, y, cell_w, x):
    title_font = font(18, True)
    body_font = font(19, True)
    small_font = font(13)
    for index in range(start, end + 1):
        left = x + (index - start) * cell_w
        is_value = index in VALUES
        draw.rounded_rectangle((left, y, left + cell_w, y + 50), radius=5, fill="#e8f3ee" if is_value else "#f8fafc", outline="#80a69a" if is_value else "#cbd5e1", width=2)
        label = str(index)
        label_box = draw.textbbox((0, 0), label, font=small_font)
        draw.text((left + (cell_w - (label_box[2] - label_box[0])) / 2, y - 21), label, fill="#475569", font=small_font)
        value = VALUES.get(index, "—")
        value_box = draw.textbbox((0, 0), value, font=body_font)
        draw.text((left + (cell_w - (value_box[2] - value_box[0])) / 2, y + 14), value, fill="#14532d" if is_value else "#94a3b8", font=body_font)
    draw.text((x, y - 52), f"Array index {start}–{end}", fill="#0f3d31", font=title_font)


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1500, 690), "#ffffff")
    draw = ImageDraw.Draw(image)
    title = font(30, True)
    subtitle = font(18)
    note = font(16)
    draw.text((60, 42), "Model Answer: Binary Tree in a 1D Array", fill="#0f3d31", font=title)
    draw.text((60, 90), "Zero-based indexing  |  Left child = 2i + 1  |  Right child = 2i + 2", fill="#475569", font=subtitle)
    draw.rounded_rectangle((60, 130, 1440, 161), radius=8, fill="#ecfdf5")
    draw.text((78, 137), "Filled cells show tree nodes. All remaining cells are intentionally blank.", fill="#166534", font=note)

    draw_row(draw, 0, 19, 245, 66, 90)
    draw_row(draw, 20, 30, 440, 88, 260)

    draw.rounded_rectangle((60, 565, 1440, 635), radius=10, fill="#f8fafc", outline="#cbd5e1")
    draw.text((84, 582), "Expected values: 0=9, 1=5, 2=16, 5=10, 6=76, 12=13, 13=58, 14=92, 25=11, 26=15, 29=80, 30=99", fill="#334155", font=note)
    draw.text((84, 607), "One-based indexing is also accepted when every position is shifted consistently by +1.", fill="#475569", font=note)
    image.save(OUTPUT, "PNG", optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    main()
