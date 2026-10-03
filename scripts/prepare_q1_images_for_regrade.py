"""Prepare the 34 verified Q1 images for an image-only grading comparison.

The first 28 images were previously cleaned. The final six still matched their
scored originals, so this script removes only the teacher's score marks from
those six and keeps the student response intact.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageStat

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public" / "photo_q1_source_34"
OUTPUT = ROOT / "docs_and_tests" / "q1_image_cleaned"
OUTPUT.mkdir(parents=True, exist_ok=True)

# Rectangles are fractions of each image after orienting it for reading.
# They cover only the teacher's slash and numeral, away from student writing.
SCORE_BOXES = {
    29: (0.62, 0.65, 0.78, 0.94),
    30: (0.66, 0.55, 0.88, 0.93),
    31: (0.47, 0.30, 0.73, 0.55),
    32: (0.34, 0.56, 0.56, 0.91),
    34: (0.44, 0.57, 0.65, 0.95),
}

# For the remaining images the score overlaps the answer's general area.
# Remove only the distinctly blue teacher ink within a conservative region.
BLUE_SCORE_REGIONS = {
    33: (0.42, 0.69, 0.73, 1.00),
}

def remove_score(im: Image.Image, box: tuple[float, float, float, float]) -> Image.Image:
    w, h = im.size
    x0, y0, x1, y1 = (round(box[0]*w), round(box[1]*h), round(box[2]*w), round(box[3]*h))
    # Nearby unmarked paper supplies a neutral fill and soft border.
    sample = im.crop((max(0, x0 - int(.06*w)), max(0, y0 - int(.05*h)), x0, y1))
    color = tuple(round(v) for v in ImageStat.Stat(sample).median[:3])
    layer = Image.new("RGB", im.size, color)
    mask = Image.new("L", im.size, 0)
    draw = ImageDraw.Draw(mask)
    feather = max(12, round(min(w, h)*.009))
    draw.rectangle((x0+feather, y0+feather, x1-feather, y1-feather), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather))
    return Image.composite(layer, im, mask)

def remove_blue_score(im: Image.Image, box: tuple[float, float, float, float]) -> Image.Image:
    w, h = im.size
    x0, y0, x1, y1 = (round(box[0]*w), round(box[1]*h), round(box[2]*w), round(box[3]*h))
    roi = im.crop((x0, y0, x1, y1))
    mask = Image.new("L", roi.size, 0)
    src, dst = roi.load(), mask.load()
    for y in range(roi.height):
        for x in range(roi.width):
            r, g, b = src[x, y]
            if b > r + 12 and b > g + 7 and r < 190:
                dst[x, y] = 255
    mask = mask.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(4))
    # Neutral paper fill; the mask affects blue score strokes only.
    patch = roi.crop((0, max(0, roi.height - 100), min(100, roi.width), roi.height))
    color = tuple(round(v) for v in ImageStat.Stat(patch).median[:3])
    paper = Image.new("RGB", roi.size, color)
    roi = Image.composite(paper, roi, mask)
    im.paste(roi, (x0, y0))
    return im

files = sorted(SOURCE.glob("DS-*.jpg"))
assert len(files) == 34
for source in files:
    number = int(source.name[3:6])
    im = Image.open(source).convert("RGB")
    if number in (29, 30, 31, 32):
        im = im.rotate(90, expand=True)
    if number in SCORE_BOXES:
        im = remove_score(im, SCORE_BOXES[number])
    if number in BLUE_SCORE_REGIONS:
        im = remove_blue_score(im, BLUE_SCORE_REGIONS[number])
    im.save(OUTPUT / source.name, quality=94, subsampling=0)
print(f"Prepared {len(files)} Q1 images at {OUTPUT}")
