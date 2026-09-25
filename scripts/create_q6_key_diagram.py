import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "public" / "answer-keys"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = OUT_DIR / "q6-lcrs-binary-tree-answer-key.png"

# Use Tahoma for Thai support on Windows
plt.rcParams['font.family'] = ['Tahoma', 'Segoe UI', 'sans-serif']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), dpi=300)
fig.patch.set_facecolor('#0f172a')

# --- 1. General Tree (Original) ---
ax1.set_facecolor('#1e293b')
ax1.set_title("Question: General Tree (Original Tree)", fontsize=16, fontweight='bold', color='#38bdf8', pad=15)
ax1.set_xlim(-1, 9)
ax1.set_ylim(-1, 7)
ax1.axis('off')

# General tree node positions
gen_pos = {
    1: (4, 6),
    2: (1.5, 4),
    3: (4, 4),
    4: (6.5, 4),
    5: (0.5, 2),
    6: (1.5, 2),
    7: (2.5, 2),
    8: (5.5, 2),
    9: (6.5, 2),
    10: (7.5, 2)
}

gen_edges = [
    (1, 2), (1, 3), (1, 4),
    (2, 5), (2, 6), (2, 7),
    (4, 8), (4, 9), (4, 10)
]

for u, v in gen_edges:
    x1, y1 = gen_pos[u]
    x2, y2 = gen_pos[v]
    ax1.plot([x1, x2], [y1, y2], color='#94a3b8', linewidth=2.5, zorder=1)

for node, (x, y) in gen_pos.items():
    circle = plt.Circle((x, y), 0.35, color='#38bdf8', ec='#ffffff', linewidth=2, zorder=2)
    ax1.add_patch(circle)
    ax1.text(x, y, str(node), color='#0f172a', fontsize=14, fontweight='bold', ha='center', va='center', zorder=3)

ax1.text(4, 0.5, "Algorithm: Left-Child Right-Sibling (LCRS)\n• Left Child = First child of the node\n• Right Child = Next immediate sibling", 
         color='#cbd5e1', fontsize=13, ha='center', va='center',
         bbox=dict(boxstyle='round,pad=0.6', facecolor='#0f172a', edgecolor='#38bdf8', alpha=0.9))


# --- 2. Binary Tree (LCRS Representation) ---
ax2.set_facecolor('#1e293b')
ax2.set_title("Answer Key: Binary Tree (Left-Child Right-Sibling)", fontsize=16, fontweight='bold', color='#4ade80', pad=15)
ax2.set_xlim(-1, 9)
ax2.set_ylim(-1, 7)
ax2.axis('off')

bin_pos = {
    1: (3.5, 6.2),
    2: (2.2, 5.0),
    3: (4.0, 4.0),
    4: (5.2, 3.0),
    5: (1.0, 3.8),
    6: (1.8, 2.6),
    7: (2.6, 1.4),
    8: (4.4, 1.8),
    9: (5.4, 0.8),
    10: (6.4, -0.2)
}

left_edges = [(1, 2), (2, 5), (4, 8)]
right_edges = [(2, 3), (3, 4), (5, 6), (6, 7), (8, 9), (9, 10)]

for u, v in left_edges:
    x1, y1 = bin_pos[u]
    x2, y2 = bin_pos[v]
    ax2.plot([x1, x2], [y1, y2], color='#10b981', linewidth=3.5, zorder=1)

for u, v in right_edges:
    x1, y1 = bin_pos[u]
    x2, y2 = bin_pos[v]
    ax2.plot([x1, x2], [y1, y2], color='#f59e0b', linewidth=3.5, linestyle='-', zorder=1)

for node, (x, y) in bin_pos.items():
    bg_color = '#4ade80' if node in [1, 2, 5, 8] else '#fbbf24'
    circle = plt.Circle((x, y), 0.35, color=bg_color, ec='#ffffff', linewidth=2, zorder=2)
    ax2.add_patch(circle)
    ax2.text(x, y, str(node), color='#0f172a', fontsize=13, fontweight='bold', ha='center', va='center', zorder=3)

# Legend
legend_elements = [
    patches.Patch(facecolor='#10b981', edgecolor='#ffffff', label='Left Child = First child (1->2, 2->5, 4->8)'),
    patches.Patch(facecolor='#f59e0b', edgecolor='#ffffff', label='Right Child = Next sibling (2->3->4, 5->6->7, 8->9->10)')
]
ax2.legend(handles=legend_elements, loc='upper right', facecolor='#0f172a', edgecolor='#4ade80', fontsize=11, labelcolor='#ffffff')

plt.tight_layout()
plt.savefig(OUT_PATH, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print(f"Generated clean Q6 diagram at: {OUT_PATH}")
