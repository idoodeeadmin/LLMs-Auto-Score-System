import fitz
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "docs_and_tests" / "LLMs_Auto_Score_Systems_Pro2_1-5.pdf"
OUT_DIR = ROOT / "docs_and_tests" / "screenshots" / "rendered_pages"
OUT_DIR.mkdir(parents=True, exist_ok=True)

doc = fitz.open(PDF_PATH)
print(f"Total pages in PDF: {len(doc)}")

# Find pages where บทที่ 4, บทที่ 5, and เอกสารอ้างอิง appear
ch4_pages = []
ch5_pages = []
ref_pages = []

for i, page in enumerate(doc):
    text = page.get_text()
    if "บทที่ 4" in text:
        ch4_pages.append(i + 1)
    if "บทที่ 5" in text:
        ch5_pages.append(i + 1)
    if "เอกสารอ้างอิง" in text and i > 50:
        ref_pages.append(i + 1)

print(f"Chapter 4 pages start around: {ch4_pages}")
print(f"Chapter 5 pages start around: {ch5_pages}")
print(f"References pages start around: {ref_pages}")

# Render preliminary pages (TOC, list of figures, list of tables)
print("Rendering preliminary pages (8-16)...")
for pno in range(7, 16):
    if pno < len(doc):
        page = doc[pno]
        pix = page.get_pixmap(dpi=150)
        img_path = OUT_DIR / f"page_{pno+1:03d}.png"
        pix.save(img_path)

# Render all pages from Chapter 4 to the end of the document
start_page = min(ch4_pages) if ch4_pages else 165
end_page = len(doc)

print(f"Rendering pages {start_page} to {end_page} to PNG...")
for pno in range(start_page - 1, end_page):
    page = doc[pno]
    pix = page.get_pixmap(dpi=150)
    img_path = OUT_DIR / f"page_{pno+1:03d}.png"
    pix.save(img_path)

print(f"All relevant pages rendered to {OUT_DIR}")

