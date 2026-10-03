"""Make local, image/text review sheets for Q2 and Q3 without using an API."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs_and_tests' / 'q2_q3_review'
OUT.mkdir(parents=True, exist_ok=True)
wb = openpyxl.load_workbook(ROOT / 'ชุดข้อสอบใหม่' / 'ชุดข้อสอบ_dataset.xlsx', read_only=True, data_only=True)
ws = wb['ชุดข้อสอบ_dataset']
rows = {r[0]:r for r in ws.values if len(r)>5 and str(r[0]).startswith('DS-')}
font = ImageFont.truetype('C:/Windows/Fonts/tahoma.ttf', 24)
bold = ImageFont.truetype('C:/Windows/Fonts/tahomabd.ttf', 26)

def wrap(draw, text, width):
    result=[]
    for paragraph in str(text or '').splitlines():
        if not paragraph:
            result.append('');continue
        line=''
        for ch in paragraph:
            if draw.textlength(line+ch,font=font)>width and line:
                result.append(line);line=ch
            else: line+=ch
        result.append(line)
    return result

for q,start in [(2,35),(3,69)]:
    files=sorted((ROOT/'ชุดข้อสอบใหม่'/f'photo_clean_text{q}').glob('*.jpg'))
    assert len(files)==34
    for j in range(0,34,2):
        sheet=Image.new('RGB',(1660,1420),'white');d=ImageDraw.Draw(sheet)
        for k in range(2):
            i=j+k; path=files[i];sid=f'DS-{start+i:03d}';y=k*710
            d.rectangle((0,y,1660,y+44),fill='#dce8e9')
            d.text((20,y+7),f'{sid}  {path.name}',font=bold,fill='#0f2f3a')
            im=Image.open(path).convert('RGB');im=ImageOps.exif_transpose(im)
            if q==2 and path.stem in ('IMG_2792','IMG_2868','IMG_2869','IMG_2870') and im.height>im.width: im=im.rotate(90,expand=True)
            im.thumbnail((815,650))
            sheet.paste(im,(max(0,(820-im.width)//2),y+50+(650-im.height)//2))
            d.line((825,y+48,825,y+700),fill='#aac1c5',width=2)
            yy=y+58
            for line in wrap(d,rows[sid][5],790):
                d.text((845,yy),line,font=font,fill='#162e32'); yy+=34
                if yy>y+688: break
        sheet.save(OUT/f'q{q}_{j//2+1:02d}.jpg',quality=90)
print(f'Built 34 review sheets in {OUT}')
