import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs('public/answer-keys', exist_ok=True)

plt.rcParams['font.family'] = 'Leelawadee UI'
fig, ax = plt.subplots(figsize=(15, 11), dpi=300)
ax.set_facecolor('#ffffff')

# Shift tree right by 1.0 unit so node 5 does not touch text box
pos = {
    9:  (8.0, 5.2),
    5:  (5.0, 4.0),
    16: (11.0, 4.0),
    10: (8.2, 2.8),
    76: (13.2, 2.8),
    13: (9.2, 1.6),
    58: (11.7, 1.6),
    92: (14.7, 1.6),
    11: (8.0, 0.3),
    15: (10.2, 0.3),
    80: (13.6, 0.3),
    99: (15.6, 0.3)
}

edges = [
    (9, 5, 'L (5 < 9)'),
    (9, 16, 'R (16 > 9)'),
    (16, 10, 'L (10 < 16)'),
    (16, 76, 'R (76 > 16)'),
    (10, 13, 'R (13 > 10)'),
    (13, 11, 'L (11 < 13)'),
    (13, 15, 'R (15 > 13)'),
    (76, 58, 'L (58 < 76)'),
    (76, 92, 'R (92 > 76)'),
    (92, 80, 'L (80 < 92)'),
    (92, 99, 'R (99 > 92)')
]

# Draw edges
for u, v, lbl in edges:
    x1, y1 = pos[u]
    x2, y2 = pos[v]
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#1e293b', lw=2.8, shrinkA=22, shrinkB=22))
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    offset_x = -0.22 if x2 < x1 else 0.22
    ax.text(mx + offset_x, my, lbl, fontsize=9.5, fontweight='bold', color='#334155', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#f8fafc', edgecolor='#cbd5e1', lw=1.0))

# Draw nodes
for val, (x, y) in pos.items():
    if val in [11, 13, 15]:
        bg_col = '#eff6ff'
        edge_col = '#2563eb'
        text_col = '#1d4ed8'
    elif val == 58:
        bg_col = '#fef2f2'
        edge_col = '#ef4444'
        text_col = '#b91c1c'
    else:
        bg_col = '#f8fafc'
        edge_col = '#0f172a'
        text_col = '#0f172a'
        
    circle = patches.Circle((x, y), 0.36, facecolor=bg_col, edgecolor=edge_col, lw=3.0, zorder=4)
    ax.add_patch(circle)
    ax.text(x, y, str(val), fontsize=16, fontweight='bold', color=text_col, ha='center', va='center', zorder=5)

# Left Side Panel: Checkpoints & Guidance
guidance_text = (
    "เฉลยแนวคำตอบมาตรฐาน (Ground Truth Key)\n"
    "ข้อ 4: การสร้าง Binary Search Tree (12 โหนด)\n"
    "ข้อมูลนำเข้า: 9, 16, 10, 76, 5, 13, 58, 92, 11, 15, 80, 99\n"
    "คะแนนเต็ม: 1.00 คะแนน (ผิดกิ่งใดกิ่งหนึ่ง = 0.00 คะแนน)\n\n"
    "=========================================\n"
    "[จุดตรวจวิกฤตที่ AI ต้องตรวจอย่างละเอียด]:\n\n"
    "1. โหนด 15 (สำคัญที่สุด):\n"
    "   • ต้องต่อเป็นลูกขวาของโหนด 13 เท่านั้น (13 -> 15)\n"
    "   • ห้ามมีเส้นลากไปต่อใต้ 58 เด็ดขาด!\n"
    "   • หากเส้นเชื่อมลากไปชนโหนด 58 ให้คะแนน = 0.00 ทันที\n\n"
    "2. โหนด 58 เป็น Leaf Node:\n"
    "   • โหนด 58 ต้องไม่มีลูกหลานใดๆ ต่อลงมาทั้งสิ้น\n\n"
    "3. โหนด 11:\n"
    "   • ต้องต่อเป็นลูกซ้ายของโหนด 13 (13 -> 11)\n"
    "   • ห้ามต่อตรงกับโหนด 10 (10 -> 11 ผิด)\n\n"
    "4. ลำดับราก (Root) และลูกของ 9:\n"
    "   • รากต้องเป็น 9 (ซ้าย 5, ขวา 16)"
)

ax.text(0.5, 5.8, guidance_text, fontsize=10.5, fontweight='medium', color='#0f172a', va='top',
        bbox=dict(boxstyle='round,pad=0.8', facecolor='#f8fafc', edgecolor='#64748b', lw=1.8),
        linespacing=1.4)

ax.set_xlim(-0.5, 17.0)
ax.set_ylim(-0.5, 6.2)
ax.set_aspect('equal')
ax.axis('off')

out_path = 'public/answer-keys/q4_bst_ground_truth.png'
plt.tight_layout()
plt.savefig(out_path, bbox_inches='tight', dpi=300)
plt.close()
print('Successfully generated clean ground truth image!')
