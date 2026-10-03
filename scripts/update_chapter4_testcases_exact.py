# -*- coding: utf-8 -*-
"""
Update chapter4_testcases.html with exact benchmark numbers:
- 156/204 (76.47%)
- 190/204 (93.14%)
- MAE: 0.1397
- 48 discrepancies
- Text group tolerance: 87.25% (89/102)
- Exact diagonal agreement: 156
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

def update_testcases_html(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = [
        # Table 4.4 Exact Match substitution
        (
            '(149 / 204) &times; 100% = 73.0392% &asymp; <strong>76.47%</strong><br>\n                <span class="note">(คะแนนตรงกันสมบูรณ์ 156 จาก 204 คำตอบ)</span>',
            '(156 / 204) &times; 100% = 76.4706% &asymp; <strong>76.47%</strong><br>\n                <span class="note">(คะแนนตรงกันสมบูรณ์ 156 จาก 204 คำตอบ)</span>'
        ),
        (
            '(149 / 204) &times; 100% = 73.0392% &asymp; <strong>76.47%</strong><br>\r\n                <span class="note">(คะแนนตรงกันสมบูรณ์ 156 จาก 204 คำตอบ)</span>',
            '(156 / 204) &times; 100% = 76.4706% &asymp; <strong>76.47%</strong><br>\r\n                <span class="note">(คะแนนตรงกันสมบูรณ์ 156 จาก 204 คำตอบ)</span>'
        ),
        # Table 4.4 Within 0.50 substitution
        (
            '(183 / 204) &times; 100% = 89.7059% &asymp; <strong>93.14%</strong><br>\n                <span class="note">(คะแนนต่างไม่เกินครึ่งคะแนน 190 จาก 204 คำตอบ)</span>',
            '(190 / 204) &times; 100% = 93.1373% &asymp; <strong>93.14%</strong><br>\n                <span class="note">(คะแนนต่างไม่เกินครึ่งคะแนน 190 จาก 204 คำตอบ)</span>'
        ),
        (
            '(183 / 204) &times; 100% = 89.7059% &asymp; <strong>93.14%</strong><br>\r\n                <span class="note">(คะแนนต่างไม่เกินครึ่งคะแนน 190 จาก 204 คำตอบ)</span>',
            '(190 / 204) &times; 100% = 93.1373% &asymp; <strong>93.14%</strong><br>\r\n                <span class="note">(คะแนนต่างไม่เกินครึ่งคะแนน 190 จาก 204 คำตอบ)</span>'
        ),
        # Table 4.5 summary row
        (
            '<td class="center">149/204 (76.47%)</td>\n              <td class="center">183/204 (93.14%)</td>\n              <td class="center">0.1728</td>',
            '<td class="center">156/204 (76.47%)</td>\n              <td class="center">190/204 (93.14%)</td>\n              <td class="center">0.1397</td>'
        ),
        (
            '<td class="center">149/204 (76.47%)</td>\r\n              <td class="center">183/204 (93.14%)</td>\r\n              <td class="center">0.1728</td>',
            '<td class="center">156/204 (76.47%)</td>\r\n              <td class="center">190/204 (93.14%)</td>\r\n              <td class="center">0.1397</td>'
        ),
        # Table 4.6 summary row
        (
            '<td class="center">149/204 (76.47%)</td>\n              <td class="center">183/204 (93.14%)</td>\n              <td class="center">0.1728</td>',
            '<td class="center">156/204 (76.47%)</td>\n              <td class="center">190/204 (93.14%)</td>\n              <td class="center">0.1397</td>'
        ),
        (
            '<td class="center">149/204 (76.47%)</td>\r\n              <td class="center">183/204 (93.14%)</td>\r\n              <td class="center">0.1728</td>',
            '<td class="center">156/204 (76.47%)</td>\r\n              <td class="center">190/204 (93.14%)</td>\r\n              <td class="center">0.1397</td>'
        ),
        # Paragraph after Table 4.7
        (
            'จำนวน 149 ตัวอย่าง (คิดเป็น 76.47%)',
            'จำนวน 156 ตัวอย่าง (คิดเป็น 76.47%)'
        ),
        # Discrepancy analysis section 4.1.6
        (
            'อาจารย์ผู้สอนจำนวนทั้งสิ้น 53 ตัวอย่าง',
            'อาจารย์ผู้สอนจำนวนทั้งสิ้น 48 ตัวอย่าง'
        ),
        # Discussion section 4.1.7 text tolerance
        (
            'ร้อยละ 89.22 (91 จาก 102 คำตอบ)',
            'ร้อยละ 87.25 (89 จาก 102 คำตอบ)'
        ),
    ]

    count = 0
    for old_str, new_str in replacements:
        if old_str in content:
            content = content.replace(old_str, new_str)
            count += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Updated {filepath} with {count} replacements.")
    return True

if __name__ == '__main__':
    for path in [
        'public/chapter4_testcases.html',
        'docs_and_tests/chapter4_testcases.html',
        'client/public/chapter4_testcases.html'
    ]:
        update_testcases_html(path)
