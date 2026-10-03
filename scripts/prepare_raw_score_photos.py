from PIL import Image

# Case 4 raw with teacher's red score
im4 = Image.open('ชุดข้อสอบใหม่/photoชุดที่1/LINE_ALBUM_Photo1_260917_2.jpg')
im4_rot = im4.rotate(90, expand=True)
im4_rot.save('public/screenshots/case_studies/raw_score_case4.jpg', quality=95)

# Case 5 raw with teacher's red score
im5 = Image.open('ชุดข้อสอบใหม่/photoชุดที่2/LINE_ALBUM_Photo2.1_260918_18.jpg')
im5.save('public/screenshots/case_studies/raw_score_case5.jpg', quality=95)

# Case 6 raw with teacher's red score
im6 = Image.open('ชุดข้อสอบใหม่/photoชุดที่3/LINE_ALBUM_Photo2.2_260918_1.jpg')
im6_rot = im6.rotate(270, expand=True)
im6_rot.save('public/screenshots/case_studies/raw_score_case6.jpg', quality=95)

print('Saved raw_score_case4, 5, 6')
