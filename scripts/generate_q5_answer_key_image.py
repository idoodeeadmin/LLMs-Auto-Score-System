import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PUBLIC = ROOT / "public" / "answer-keys" / "q5-infix-prefix-postfix-answer-key.png"
OUTPUT_DATASET = ROOT / "ชุดข้อสอบใหม่" / "answer_keys" / "q5-infix-prefix-postfix-answer-key.png"

def font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/leelawdb.ttf" if bold else "C:/Windows/Fonts/leelawad.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()

def main():
    OUTPUT_PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_DATASET.parent.mkdir(parents=True, exist_ok=True)

    w, h = 1600, 950
    image = Image.new("RGB", (w, h), "#ffffff")
    draw = ImageDraw.Draw(image)

    f_title = font(26, True)
    f_sub = font(17)
    f_sec = font(21, True)
    f_step = font(16)
    f_code = font(18, True)
    f_ans = font(22, True)

    # Header Box
    draw.rounded_rectangle((40, 25, w - 40, 140), radius=12, fill="#f1f5f9", outline="#cbd5e1", width=2)
    draw.text((65, 38), "เฉลยแม่แบบมาตรฐาน (Model Answer Key): ข้อที่ 5", fill="#0f172a", font=f_title)
    draw.text((65, 78), "โจทย์: จงแสดงวิธีการหา Infix Expression ต่อไปนี้ให้เป็น Prefix และ Postfix Expression ด้วยมือ (คะแนนเต็ม 1.00)", fill="#334155", font=f_sub)
    draw.text((65, 104), "นิพจน์ต้นฉบับ: A + (B * (C - (D / (F * 2))))", fill="#1e40af", font=font(17, True))

    # Left Column: Prefix Expression (x: 40 -> 780)
    col1_left, col1_right = 40, 780
    draw.rounded_rectangle((col1_left, 160, col1_right, 840), radius=12, fill="#f8fafc", outline="#93c5fd", width=2)
    draw.rounded_rectangle((col1_left, 160, col1_right, 220), radius=12, fill="#dbeafe")
    draw.text((col1_left + 25, 175), "1. ฝั่ง Prefix Expression (คะแนนเต็ม 0.50)", fill="#1e3a8a", font=f_sec)

    prefix_steps = [
        ("ลำดับที่ 1 (วงเล็บในสุด):", "(F * 2)", "->", "* F 2"),
        ("ลำดับที่ 2:", "(D / (* F 2))", "->", "/ D * F 2"),
        ("ลำดับที่ 3:", "(C - (/ D * F 2))", "->", "- C / D * F 2"),
        ("ลำดับที่ 4:", "(B * (- C / D * F 2))", "->", "* B - C / D * F 2"),
        ("ลำดับที่ 5 (วงเล็บนอกสุด):", "A + (* B - C / D * F 2)", "->", "+ A * B - C / D * F 2"),
    ]

    y_cur = 240
    for label, inf, arr, pref in prefix_steps:
        draw.text((col1_left + 25, y_cur), label, fill="#475569", font=f_step)
        draw.text((col1_left + 40, y_cur + 26), f"{inf}  {arr}  {pref}", fill="#0f172a", font=f_code)
        y_cur += 75

    # Prefix Final Box
    draw.rounded_rectangle((col1_left + 20, 680, col1_right - 20, 810), radius=10, fill="#ecfdf5", outline="#10b981", width=2)
    draw.text((col1_left + 35, 695), "คำตอบสุดท้ายฝั่ง Prefix (0.50 คะแนน):", fill="#065f46", font=font(17, True))
    draw.text((col1_left + 35, 730), "+ A * B - C / D * F 2", fill="#047857", font=f_ans)
    draw.text((col1_left + 35, 770), "(ยอมรับการเขียนติดกัน: +A*B-C/D*F2)", fill="#059669", font=font(14))

    # Right Column: Postfix Expression (x: 820 -> 1560)
    col2_left, col2_right = 820, 1560
    draw.rounded_rectangle((col2_left, 160, col2_right, 840), radius=12, fill="#f8fafc", outline="#c4b5fd", width=2)
    draw.rounded_rectangle((col2_left, 160, col2_right, 220), radius=12, fill="#ede9fe")
    draw.text((col2_left + 25, 175), "2. ฝั่ง Postfix Expression (คะแนนเต็ม 0.50)", fill="#5b21b6", font=f_sec)

    postfix_steps = [
        ("ลำดับที่ 1 (วงเล็บในสุด):", "(F * 2)", "->", "F 2 *"),
        ("ลำดับที่ 2:", "(D / (F 2 *))", "->", "D F 2 * /"),
        ("ลำดับที่ 3:", "(C - (D F 2 * /))", "->", "C D F 2 * / -"),
        ("ลำดับที่ 4:", "(B * (C D F 2 * / -))", "->", "B C D F 2 * / - *"),
        ("ลำดับที่ 5 (วงเล็บนอกสุด):", "A + (B C D F 2 * / - *)", "->", "A B C D F 2 * / - * +"),
    ]

    y_cur = 240
    for label, inf, arr, post in postfix_steps:
        draw.text((col2_left + 25, y_cur), label, fill="#475569", font=f_step)
        draw.text((col2_left + 40, y_cur + 26), f"{inf}  {arr}  {post}", fill="#0f172a", font=f_code)
        y_cur += 75

    # Postfix Final Box
    draw.rounded_rectangle((col2_left + 20, 680, col2_right - 20, 810), radius=10, fill="#ecfdf5", outline="#10b981", width=2)
    draw.text((col2_left + 35, 695), "คำตอบสุดท้ายฝั่ง Postfix (0.50 คะแนน):", fill="#065f46", font=font(17, True))
    draw.text((col2_left + 35, 730), "A B C D F 2 * / - * +", fill="#047857", font=f_ans)
    draw.text((col2_left + 35, 770), "(ยอมรับการเขียนติดกัน: ABCDF2*/-*+)", fill="#059669", font=font(14))

    # Bottom Footer Note
    draw.text((45, 875), "เกณฑ์สรุป: ถูกทั้งสองฝั่งได้ 1.00 | ถูกฝั่งเดียวได้ 0.50 | มีความพยายามถูกทางแต่ผิดเล็กน้อยได้ 0.25 | ผิดทั้งหมดหรือไม่ทำได้ 0.00", fill="#64748b", font=font(16, True))

    image.save(OUTPUT_PUBLIC, "PNG", optimize=True)
    image.save(OUTPUT_DATASET, "PNG", optimize=True)
    print("Successfully generated Question 5 Answer Key template image with Leelawadee Thai font!")

if __name__ == "__main__":
    main()
