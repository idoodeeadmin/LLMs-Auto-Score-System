import os
import sys
import pillow_heif
from PIL import Image

pillow_heif.register_heif_opener()
sys.stdout.reconfigure(encoding='utf-8')

cases_spec = [
    {
        'fname': 'case1_ds001.jpg',
        'src': 'ชุดข้อสอบใหม่/โจทย์textชุดที่1/IMG_2791.HEIC',
        'rot': Image.Transpose.ROTATE_90,
        'score_desc': 'คะแนน /2 ปากกาน้ำเงินด้านล่าง'
    },
    {
        'fname': 'case2_ds047.jpg',
        'src': 'ชุดข้อสอบใหม่/โจทย์textชุดที่2/IMG_2855.HEIC',
        'rot': None,
        'score_desc': 'คะแนน 2 ไฮไลต์สีส้มมุมขวาบน'
    },
    {
        'fname': 'case3_ds072.jpg',
        'src': 'ชุดข้อสอบใหม่/โจทย์textชุดที่3/IMG_2895.HEIC',
        'rot': None,
        'score_desc': 'คะแนน 0.5 ปากกาแดงมุมขวาล่าง'
    },
    {
        'fname': 'case4_ds104.jpg',
        'src': 'ชุดข้อสอบใหม่/photoชุดที่1/LINE_ALBUM_Photo1_260917_2.jpg',
        'rot': Image.Transpose.ROTATE_90,
        'score_desc': 'คะแนน 1 ปากกาแดงด้านล่างซ้าย'
    },
    {
        'fname': 'case5_ds154.jpg',
        'src': 'ชุดข้อสอบใหม่/photoชุดที่2/LINE_ALBUM_Photo2.1_260918_18.jpg',
        'rot': None,
        'score_desc': 'คะแนน 0.5 ปากกาแดงมุมขวาบน'
    },
    {
        'fname': 'case6_ds171.jpg',
        'src': 'ชุดข้อสอบใหม่/photoชุดที่3/LINE_ALBUM_Photo2.2_260918_1.jpg',
        'rot': Image.Transpose.ROTATE_270,
        'score_desc': 'คะแนน 0 วงกลมปากกาแดงด้านล่าง'
    }
]

dst_dirs = [
    'docs_and_tests/images/case_studies',
    'public/screenshots/case_studies',
    'public/images/case_studies'
]

for d in dst_dirs:
    os.makedirs(d, exist_ok=True)

for item in cases_spec:
    src_path = item['src']
    fname = item['fname']
    desc = item['score_desc']
    print(f"Processing {fname} from {src_path} ({desc})...")
    
    im = Image.open(src_path)
    if item['rot'] is not None:
        im = im.transpose(item['rot'])
        
    w, h = im.size
    max_dim = 1200
    if max(w, h) > max_dim:
        scale = max_dim / float(max(w, h))
        im_resized = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    else:
        im_resized = im.copy()
        
    for d in dst_dirs:
        out_p = os.path.join(d, fname)
        im_resized.save(out_p, quality=92, optimize=True)
        print(f"   -> Saved {out_p} ({im_resized.size})")

print("\nSuccessfully updated all 6 case study images with raw score-visible photos!")
