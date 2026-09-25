import sys
from pathlib import Path
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding='utf-8')

def create_bst_diagram():
    # Set equal aspect ratio so circles are perfectly round
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Coordinate system: x in [0, 10], y in [0, 8]
    nodes = {
        9:  (3.5, 7.0),
        5:  (1.5, 5.2),
        16: (6.5, 5.2),
        10: (4.5, 3.5),
        76: (8.2, 3.5),
        13: (5.5, 1.8),
        58: (7.2, 1.8),
        92: (9.2, 1.8),
        11: (4.7, 0.2),
        15: (6.3, 0.2),
        80: (8.4, 0.2),
        99: (10.0, 0.2),
    }
    
    edges = [
        (9, 5), (9, 16),
        (16, 10), (16, 76),
        (10, 13),
        (13, 11), (13, 15),
        (76, 58), (76, 92),
        (92, 80), (92, 99)
    ]
    
    # Draw edges
    for parent, child in edges:
        x1, y1 = nodes[parent]
        x2, y2 = nodes[child]
        ax.plot([x1, x2], [y1, y2], color='#475569', linewidth=2.8, zorder=1)
        
    # Draw node circles
    r = 0.42
    for val, (x, y) in nodes.items():
        is_root = (val == 9)
        face_col = '#1d4ed8' if is_root else '#3b82f6'
        circle = plt.Circle((x, y), r, facecolor=face_col, edgecolor='#1e3a8a', linewidth=2.2, zorder=2)
        ax.add_patch(circle)
        ax.text(x, y, str(val), color='white', weight='bold', fontsize=13, ha='center', va='center', zorder=3)
        
    # Labels for Root, Left, Right
    ax.text(3.5, 7.65, "Root (9)", fontsize=13, weight='bold', color='#1e3a8a', ha='center')
    ax.text(1.5, 5.85, "Left < 9", fontsize=11, color='#64748b', ha='center')
    ax.text(6.5, 5.85, "Right > 9", fontsize=11, color='#64748b', ha='center')
    
    # Title
    fig.suptitle("Answer Key: Binary Search Tree (Question 4)", fontsize=17, weight='bold', color='#0f172a', y=0.96)
    plt.figtext(0.5, 0.03, "Input sequence: 9, 16, 10, 76, 5, 13, 58, 92, 11, 15, 80, 99  |  Property: Left < Parent < Right",
                 ha='center', fontsize=11.5, color='#475569')
    
    ax.set_xlim(0.5, 10.8)
    ax.set_ylim(-0.6, 8.2)
    
    out_dir = Path('ชุดข้อสอบใหม่') / 'answer_keys'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / 'q4_bst_answer_key.png'
    plt.tight_layout()
    plt.savefig(out_file, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Generated perfect round BST answer key diagram: {out_file}")

if __name__ == '__main__':
    create_bst_diagram()
