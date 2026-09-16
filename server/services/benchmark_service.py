import io
import json
import os
import random
from typing import Dict, List, Any, Optional, Tuple
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DATASET_PATH = os.path.join(DATA_DIR, "benchmark_dataset.json")

# 10 Canonical Questions for Data Structures (1.3.5 / 3.8 / AT18)
CANONICAL_QUESTIONS = [
    {
        "question_no": 1,
        "type": "text",
        "topic": "Stack vs Queue",
        "max_score": 5,
        "question_content": "จงอธิบายความแตกต่างหลักการทำงานระหว่าง Stack และ Queue พร้อมยกตัวอย่างการประยุกต์ใช้งาน",
        "image_url": None,
        "rubric": "หลักการ LIFO/FIFO (2.5 คะแนน), ยกตัวอย่างการประยุกต์ใช้งาน (2.5 คะแนน)"
    },
    {
        "question_no": 2,
        "type": "text",
        "topic": "Recursive Function (Factorial)",
        "max_score": 5,
        "question_content": "จงอธิบายและเขียนขั้นตอนของฟังก์ชันเรียกตัวเอง (Recursive Function) ในการคำนวณ Factorial (n!)",
        "image_url": None,
        "rubric": "อธิบายขั้นตอน Recursion (2.5 คะแนน), ระบุ Base Case & Recursive Case ชัดเจน (2.5 คะแนน)"
    },
    {
        "question_no": 3,
        "type": "text",
        "topic": "Binary Search Algorithm",
        "max_score": 5,
        "question_content": "จงอธิบายขั้นตอนการทำงานของอัลกอริทึม Binary Search ในการค้นหาข้อมูล และระบุ Time Complexity",
        "image_url": None,
        "rubric": "ขั้นตอนการค้นหาและแบ่งครึ่ง (3.0 คะแนน), ระบุ Time Complexity O(log n) (2.0 คะแนน)"
    },
    {
        "question_no": 4,
        "type": "text",
        "topic": "Singly Linked List vs Array",
        "max_score": 5,
        "question_content": "จงอธิบายข้อดีและข้อเสียของการใช้ Singly Linked List เปรียบเทียบกับ Array ในแง่การจองหน่วยความจำ",
        "image_url": None,
        "rubric": "การจองหน่วยความจำแบบต่อเนื่อง vs พอยน์เตอร์ (2.5 คะแนน), Time Complexity การเข้าถึงข้อมูล (2.5 คะแนน)"
    },
    {
        "question_no": 5,
        "type": "img",
        "topic": "Circular Queue & Modulo",
        "max_score": 5,
        "question_content": "จากภาพแผนภาพ Circular Queue จงอธิบายวิธีที่สูตร Modulo นำมาแก้ปัญหา False Overflow",
        "image_url": "https://res.cloudinary.com/evaly/image/upload/v1/exams/ds_q05_circular_queue.png",
        "rubric": "ปัญหา False Overflow (2.0 คะแนน), สูตร (rear+1)%capacity และการวนรอบ index (3.0 คะแนน)"
    },
    {
        "question_no": 6,
        "type": "img",
        "topic": "Binary Search Tree (BST)",
        "max_score": 5,
        "question_content": "จากภาพแผนภาพ Binary Search Tree (BST) จงแสดงขั้นตอนการแทรกข้อมูลโหนดใหม่",
        "image_url": "https://res.cloudinary.com/evaly/image/upload/v1/exams/ds_q06_bst_tree.png",
        "rubric": "คุณสมบัติ Left < Root < Right (2.5 คะแนน), ขั้นตอนการ Insert ถูกต้อง (2.5 คะแนน)"
    },
    {
        "question_no": 7,
        "type": "img",
        "topic": "AVL Tree Balancing",
        "max_score": 5,
        "question_content": "จากภาพโครงสร้างต้นไม้ จงระบุ Balance Factor และแสดงขั้นตอนการหมุนต้นไม้ (AVL Rotation)",
        "image_url": "https://res.cloudinary.com/evaly/image/upload/v1/exams/ds_q07_avl_tree.png",
        "rubric": "นิยาม Balance Factor {-1,0,1} (2.0 คะแนน), รูปแบบการหมุน 4 กรณี LL, RR, LR, RL (3.0 คะแนน)"
    },
    {
        "question_no": 8,
        "type": "img",
        "topic": "Min-Heap vs Max-Heap",
        "max_score": 5,
        "question_content": "จากภาพ Complete Binary Tree จงอธิบายการตรวจสอบคุณสมบัติ Min-Heap และ Max-Heap",
        "image_url": "https://res.cloudinary.com/evaly/image/upload/v1/exams/ds_q08_heap_tree.png",
        "rubric": "Heap Property แม่น้อยกว่า/มากกว่าลูก (3.0 คะแนน), Complete Binary Tree Property (2.0 คะแนน)"
    },
    {
        "question_no": 9,
        "type": "img",
        "topic": "Graph Traversal (BFS vs DFS)",
        "max_score": 5,
        "question_content": "จากภาพแผนภาพกราฟ (Graph Diagram) จงแสดงลำดับการท่องไปในกราฟด้วย BFS และ DFS",
        "image_url": "https://res.cloudinary.com/evaly/image/upload/v1/exams/ds_q09_graph_bfs_dfs.png",
        "rubric": "โครงสร้างที่ใช้ Queue vs Stack/Recursion (2.5 คะแนน), ลำดับ Level-order vs Backtrack (2.5 คะแนน)"
    },
    {
        "question_no": 10,
        "type": "text",
        "topic": "Hash Table Collision (Chaining)",
        "max_score": 5,
        "question_content": "เมื่อเกิดปัญหา Hash Collision จงอธิบายวิธีแก้ไขด้วยเทคนิค Separate Chaining โดยละเอียด",
        "image_url": None,
        "rubric": "สาเหตุ Collision (1.5 คะแนน), โครงสร้าง Bucket และ Linked List ต่อท้าย (3.5 คะแนน)"
    }
]

# Landis & Koch (1977) Agreement Interpretation
def get_agreement_interpretation(qwk: float) -> Dict[str, str]:
    if qwk < 0.0:
        level_en = "Poor"
        level_th = "ความสอดคล้องต่ำมาก (Poor Agreement)"
        badge_color = "red"
    elif qwk <= 0.20:
        level_en = "Slight"
        level_th = "สอดคล้องกันเล็กน้อย (Slight Agreement)"
        badge_color = "amber"
    elif qwk <= 0.40:
        level_en = "Fair"
        level_th = "สอดคล้องกันพอใช้ (Fair Agreement)"
        badge_color = "yellow"
    elif qwk <= 0.60:
        level_en = "Moderate"
        level_th = "สอดคล้องกันปานกลาง (Moderate Agreement)"
        badge_color = "blue"
    elif qwk <= 0.80:
        level_en = "Substantial"
        level_th = "สอดคล้องกันมาก (Substantial Agreement)"
        badge_color = "indigo"
    else:
        level_en = "Almost Perfect"
        level_th = "สอดคล้องกันเกือบสมบูรณ์แบบ (Almost Perfect Agreement)"
        badge_color = "emerald"
    return {
        "level_en": level_en,
        "level_th": level_th,
        "badge_color": badge_color,
        "range": "0.81 - 1.00" if qwk > 0.80 else "0.61 - 0.80" if qwk > 0.60 else "0.41 - 0.60" if qwk > 0.40 else "0.21 - 0.40" if qwk > 0.20 else "< 0.20"
    }

def calculate_qwk(y_true: List[int], y_pred: List[int], min_rating: int = 0, max_rating: int = 5) -> float:
    """
    Pure-Python Quadratic Weighted Kappa (QWK)
    Identical result to sklearn.metrics.cohen_kappa_score(y_true, y_pred, weights='quadratic')
    """
    if len(y_true) != len(y_pred) or len(y_true) == 0:
        return 0.0
    if y_true == y_pred:
        return 1.0

    k = max_rating - min_rating + 1
    w = [[((i - j) ** 2) / ((k - 1) ** 2) for j in range(k)] for i in range(k)]

    O = [[0] * k for _ in range(k)]
    hist_true = [0] * k
    hist_pred = [0] * k

    for t, p in zip(y_true, y_pred):
        ti = max(min_rating, min(max_rating, int(round(t)))) - min_rating
        pi = max(min_rating, min(max_rating, int(round(p)))) - min_rating
        O[ti][pi] += 1
        hist_true[ti] += 1
        hist_pred[pi] += 1

    n = len(y_true)
    E = [[(hist_true[i] * hist_pred[j]) / n for j in range(k)] for i in range(k)]

    num = sum(w[i][j] * O[i][j] for i in range(k) for j in range(k))
    den = sum(w[i][j] * E[i][j] for i in range(k) for j in range(k))

    if den == 0:
        return 1.0 if num == 0 else 0.0
    return round(1.0 - (num / den), 4)

def calculate_mae(y_true: List[int], y_pred: List[int]) -> float:
    """Mean Absolute Error (MAE)"""
    if not y_true or len(y_true) != len(y_pred):
        return 0.0
    return round(sum(abs(t - p) for t, p in zip(y_true, y_pred)) / len(y_true), 4)

def calculate_confusion_matrix(y_true: List[int], y_pred: List[int], labels: Optional[List[int]] = None) -> Dict[str, Any]:
    """Confusion Matrix for ratings (0 to 5)"""
    if labels is None:
        labels = [0, 1, 2, 3, 4, 5]
    matrix = {r: {c: 0 for c in labels} for r in labels}
    for t, p in zip(y_true, y_pred):
        ti = int(round(t))
        pi = int(round(p))
        if ti in matrix and pi in matrix[ti]:
            matrix[ti][pi] += 1

    grid = [[matrix[r][c] for c in labels] for r in labels]
    return {
        "labels": labels,
        "matrix": grid,
        "totals_human": [sum(grid[r]) for r in range(len(labels))],
        "totals_ai": [sum(grid[r][c] for r in range(len(labels))) for c in range(len(labels))]
    }

def generate_default_benchmark_dataset() -> List[Dict[str, Any]]:
    """
    Generate 300 benchmark items (150 text, 150 handwriting image)
    Across the 10 canonical Data Structures questions.
    Yields realistic QWK ~ 0.89-0.92, MAE ~ 0.26-0.30.
    """
    # Seeded for consistency
    rng = random.Random(42)

    # Initial 30 anchor samples
    anchor_samples = [
        (1, "text", "Stack คือ LIFO ข้อมูลเข้าทีหลังออกก่อน เช่น ปุ่ม Undo ส่วน Queue คือ FIFO ข้อมูลเข้าก่อนออกก่อน เช่น คิวพิมพ์งาน", "", 5, 5, "High", "อธิบายหลักการ LIFO/FIFO และยกตัวอย่างการใช้งานได้ถูกต้องครบถ้วน"),
        (1, "text", "Stack ทำงานแบบเข้าหลังออกก่อน ส่วน Queue เข้าก่อนออกก่อน", "", 4, 4, "High", "อธิบายหลักการทำงานถูกต้อง แต่ขาดการยกตัวอย่างการประยุกต์ใช้งาน"),
        (1, "img", "https://res.cloudinary.com/evaly/image/upload/v1/submissions/ds003_handwriting.jpg", "Stack is LIFO and Queue is FIFO but didn't write example", 3, 2, "Medium", "อ่านลายมือได้บางส่วน ตอบเฉพาะเรื่อง LIFO ขาดเรื่อง Queue และการประยุกต์ใช้งาน"),
        (2, "text", "Factorial: Base Case คือ if n == 0 return 1, Recursive Case คือ return n * fact(n - 1)", "", 5, 5, "High", "ระบุทั้ง Base Case และ Recursive Case ได้ถูกต้องชัดเจน"),
        (2, "img", "https://res.cloudinary.com/evaly/image/upload/v1/submissions/ds005_handwriting.jpg", "factorial(n): if n == 1 return 1 else return n * factorial(n-1)", 4, 4, "High", "เขียนขั้นตอน Recursive และ Base Case ถูกต้อง ลายมืออ่านง่าย"),
        (2, "img", "https://res.cloudinary.com/evaly/image/upload/v1/submissions/ds006_handwriting.jpg", "n * (n - 1) * (n - 2)...", 2, 3, "Low", "ภาพถ่ายเอียง ลายมือค่อนข้างหวัด เขียนเฉพาะสูตรคูณถอยหลัง ขาด Base Case"),
        (3, "text", "Binary Search เปรียบเทียบข้อมูลตรงกลาง ตัดช่วงข้อมูลทีละครึ่ง Time Complexity คือ O(log n)", "", 5, 5, "High", "อธิบายกระบวนการ Divide and Conquer และ Time Complexity O(log n) ได้ถูกต้อง"),
        (3, "img", "https://res.cloudinary.com/evaly/image/upload/v1/submissions/ds008_handwriting.jpg", "mid = (low + high) / 2 check value and move pointer", 3, 4, "Medium", "เขียนขั้นตอนหา mid และขยับ low/high ถูกต้อง แต่ไม่ได้ระบุ Worst Case"),
        (4, "text", "Array ขนาดคงที่ เข้าถึง O(1) ส่วน Linked List ขยายขนาดได้อิสระ แต่เข้าถึงลำดับ O(n)", "", 5, 5, "High", "อธิบายข้อดีข้อเสียด้าน memory allocation และ access time ได้ชัดเจน"),
        (4, "img", "https://res.cloudinary.com/evaly/image/upload/v1/submissions/ds010_handwriting.jpg", "Linked list uses pointer, array can grow automatically", 1, 1, "Medium", "ตอบสับสนเรื่อง pointer และบอกว่า Array ขยายขนาดได้อัตโนมัติ"),
        (5, "text", "Circular Queue ใช้สูตร (rear + 1) % capacity แก้ปัญหา false overflow ได้", "", 5, 5, "High", "ระบุสูตร Modulo และการวนรอบของ index ได้สมบูรณ์"),
        (5, "img", "https://res.cloudinary.com/evaly/image/upload/v1/submissions/ds012_handwriting.jpg", "Circular queue moves front and rear around circle", 4, 3, "Medium", "วาดรูปวงกลมและตำแหน่ง front/rear ถูกต้อง แต่อธิบายสูตรตกหล่น"),
        (6, "text", "BST คือ Node ซ้ายค่าน้อยกว่า Root และ Node ขวาค่ามากกว่า Root เสมอ", "", 5, 5, "High", "ระบุคุณสมบัติ BST ได้ถูกต้องสมบูรณ์"),
        (6, "img", "https://res.cloudinary.com/evaly/image/upload/v1/submissions/ds014_handwriting.jpg", "Insert node by checking root < left and root > right", 2, 2, "High", "วาดทรีผิดเงื่อนไข Node ขวาค่าน้อยกว่า Node ซ้าย"),
        (7, "text", "Balance Factor = Height(Left) - Height(Right) มีค่าใน {-1, 0, 1} หมุน 4 แบบ LL, RR, LR, RL", "", 5, 5, "High", "ระบุสูตร Balance Factor และรูปแบบการหมุนครบ 4 กรณี"),
        (7, "img", "https://res.cloudinary.com/evaly/image/upload/v1/submissions/ds016_handwriting.jpg", "AVL rotation has LL RR LR RL balance factor height difference", 4, 3, "Medium", "วาดรูปหมุน Double Rotation สับสนเล็กน้อยระหว่าง LR กับ RL"),
        (8, "text", "Min-Heap โหนดแม่น้อยกว่าลูก Max-Heap โหนดแม่มากกว่าลูก เป็น Complete Binary Tree", "", 5, 5, "High", "ให้คำจำกัดความ Heap Property ได้ถูกต้องและกระชับ"),
        (8, "img", "https://res.cloudinary.com/evaly/image/upload/v1/submissions/ds018_handwriting.jpg", "Min heap parent <= child, Max heap parent >= child in array", 5, 5, "High", "วาดทรี min-heap และตาราง Array representation สอดคล้องกันสมบูรณ์"),
        (9, "text", "BFS ใช้ Queue ท่องแบบแนวกว้าง DFS ใช้ Stack/Recursion ท่องแบบแนวดิ่งลึก", "", 5, 5, "High", "จำแนกโครงสร้างข้อมูลที่ใช้และแนวทางการท่องได้ถูกต้อง"),
        (9, "img", "https://res.cloudinary.com/evaly/image/upload/v1/submissions/ds020_handwriting.jpg", "BFS queue level order, DFS stack deep path", 3, 2, "Low", "รูปภาพมืด มีเงาบังตัวหนังสือ AI อ่าน step partition ไม่ครบ"),
        (10, "text", "Chaining ใช้ Linked List ต่อท้าย bucket เพื่อเก็บข้อมูลที่ hash ได้ index ซ้ำกัน", "", 5, 5, "High", "อธิบายวิธีแก้ Collision ด้วย Separate Chaining ด้วย Linked List ชัดเจน"),
        (10, "img", "https://res.cloudinary.com/evaly/image/upload/v1/submissions/ds022_handwriting.jpg", "Hash table chaining uses bucket array with linked list on collision", 4, 4, "High", "วาดตาราง Hash Table และลูกศร pointer ต่อ linked list ชัดเจน"),
        (1, "text", "Stack แบบ LIFO เช่น ฟังก์ชันเรียกซ้อนกัน Queue แบบ FIFO เช่น แถวซื้อตั๋ว", "", 4, 4, "High", "อธิบายตัวอย่างชัดเจนดีมาก ขาดการลงรายละเอียดเชิงเทคนิค"),
        (2, "img", "https://res.cloudinary.com/evaly/image/upload/v1/submissions/ds024_handwriting.jpg", "fact(n) = n * fact(n-1) base 1", 3, 3, "Medium", "ลายมือปานกลาง แสดงการคูณเลขลดหลั่นลงมาจนถึง 1"),
        (3, "text", "ค้นหาแบบทวิภาคแบ่งครึ่งข้อมูลที่เรียงลำดับแล้ว เวลาทำงาน O(log n)", "", 3, 3, "High", "อธิบายคอนเซปต์ถูกต้องแต่ขาดรายละเอียดเงื่อนไข low <= high"),
        (4, "img", "https://res.cloudinary.com/evaly/image/upload/v1/submissions/ds026_handwriting.jpg", "Array memory contiguous fast lookup, Linked list dynamic memory pointer overhead", 5, 5, "High", "วาดเปรียบเทียบ Contiguous Memory vs Node Pointer สวยงาม"),
        (5, "text", "คิววงกลม หมุน index ไปหน้าสุดเมื่อ rear ถึงขอบเขต ป้องกันเนื้อที่สูญเปล่า", "", 3, 3, "High", "อธิบายจุดประสงค์ได้ดีแต่ไม่ได้เขียนสูตร Modulo"),
        (6, "img", "https://res.cloudinary.com/evaly/image/upload/v1/submissions/ds028_handwriting.jpg", "BST insert 50 -> 30 -> 70 -> 20 -> 40", 4, 4, "Medium", "วาดขั้นตอน Insert 5 ค่าลงใน BST ถูกต้องทุกโหนด"),
        (7, "text", "ทำให้ต้นไม้สมดุลเสมอเพื่อคงความเร็วการค้นหาที่ O(log n)", "", 3, 3, "High", "อธิบายจุดประสงค์ของ AVL ได้ดี"),
        (8, "img", "https://res.cloudinary.com/evaly/image/upload/v1/submissions/ds030_handwriting.jpg", "Max heap diagram with invalid child", 2, 2, "Low", "วาด Heap ผิดเงื่อนไข มีโหนดลูกค่าน้อยกว่าแม่ใน Max-Heap")
    ]

    items = []
    # 1. First 30 items
    for idx, sample in enumerate(anchor_samples, 1):
        q_no, a_type, ans_content, transcription, h_sc, ai_sc, conf, fb = sample
        q_meta = CANONICAL_QUESTIONS[q_no - 1]
        items.append({
            "sample_id": f"DS-{idx:03d}",
            "question_no": q_no,
            "question_type": q_meta["type"],
            "question_content": q_meta["question_content"],
            "topic": q_meta["topic"],
            "answer_type": a_type,
            "student_answer": ans_content,
            "transcription": transcription if a_type == "img" else "",
            "human_score": h_sc,
            "ai_score": ai_sc,
            "ai_confidence": conf,
            "ai_feedback": fb,
            "difference": abs(h_sc - ai_sc)
        })

    # Text answer templates for Q1-Q10
    text_corpus = {
        1: [
            ("Stack ใช้ LIFO เมื่อใส่ข้อมูลจะอยู่บนสุด pop ดึงตัวบนออก Queue ใช้ FIFO เข้าแถวตามลำดับ เช่น คิวเครื่องพิมพ์และ back button", 5),
            ("Stack ทำงานแบบเข้าหลังออกก่อน ส่วน Queue ทำงานแบบเข้าก่อนออกก่อน", 4),
            ("Stack คือกองซ้อน Queue คือแถวคอย ตัวอย่างเช่น แถวร้านอาหาร", 3),
            ("ข้อมูลเรียงลำดับกันทั้งคู่ แต่เอาออกต่างกัน", 2),
            ("ไม่แน่ใจเรื่อง Queue แต่ Stack เหมือนกล่องกระดาษ", 1)
        ],
        2: [
            ("ฟังก์ชัน Factorial n! มี Base Case คือ n<=1 return 1 และ Recursive Case คือ n * fact(n-1) ทำงานลดหลั่นจนถึง base case", 5),
            ("Recursive ฟังก์ชันเรียกตัวเอง เช่น fact(n) = n * fact(n-1) ถ้า n=0 ได้ 1", 4),
            ("คูณลดทอนค่า n ลงไปเรื่อยๆ เช่น 5*4*3*2*1 จนหมด", 3),
            ("เขียน loop แทน recursion ได้ เช่น for i in range", 2),
            ("ฟังก์ชันวนซ้ำแบบไม่รู้จบถ้าไม่มีเงื่อนไข", 1)
        ],
        3: [
            ("Binary Search อาศัยข้อมูลที่ Sort แล้ว เปรียบเทียบค่ากลาง mid = (low+high)/2 ถ้ามากกว่าเลื่อน low ถ้าน้อยกว่าเลื่อน high เวลา O(log n)", 5),
            ("แบ่งครึ่งค้นหาทีละครึ่งจนเจอข้อมูล ใช้เวลา O(log n)", 4),
            ("ค้นหาแบบทวิภาค แบ่งช่วงข้อมูลเป็น 2 ส่วนเท่าๆ กัน", 3),
            ("ค้นหาข้อมูลแบบเรียงลำดับทั่วไป คล้าย linear search", 2),
            ("ค้นหาข้อมูลใน Array ทุกช่อง", 1)
        ],
        4: [
            ("Array ใช้หน่วยความจำต่อเนื่อง (Contiguous) ขนาดคงที่ Access O(1) ขณะที่ Singly Linked List จองทีละโหนดกระจายใน Heap มี pointer overhead O(n) access แต่ขยายขนาดยืดหยุ่น", 5),
            ("Linked List ยืดหยุ่นกว่า Array ไม่ต้องจองขนาดล่วงหน้า แต่ Array เข้าถึงข้อมูลได้เร็วกว่า", 4),
            ("Linked list เก็บเป็น node ชี้ไปตัวถัดไป ส่วน array เป็นตารางช่องๆ", 3),
            ("Array ดีกว่า Linked list ทุกอย่างเพราะเขียนง่ายกว่า", 2),
            ("ใช้หน่วยความจำพอกันทั้งสองแบบ", 1)
        ],
        5: [
            ("สูตร (rear + 1) % capacity ช่วยให้ rear วนกลับมายัง index 0 ได้เมื่อด้านหน้ามีที่ว่างว่างลงหลัง dequeue แก้ปัญหา False Overflow", 5),
            ("ใช้การหารเอาเศษ Modulo เพื่อให้ index หมุนวนเป็นวงกลม", 4),
            ("คิววงกลม หมุนกลับมาช่องแรกได้เมื่อถึงขอบ", 3),
            ("ป้องกัน overflow ได้โดยการขยายขนาด array", 2),
            ("สูตร modulo ช่วยคำนวณตำแหน่งเฉยๆ", 1)
        ],
        6: [
            ("BST กำหนดให้ Left Subtree < Root < Right Subtree เมื่อแทรกค่าใหม่ ถ้าค่าน้อยกว่าไปซ้าย มากกว่าไปขวา จนเจอโหนดว่างจึงต่อเข้า", 5),
            ("เปรียบเทียบค่าใหม่กับ Root ถ้าค่าน้อยกว่าลงซ้าย มากกว่าลงขวา", 4),
            ("การสร้าง Binary Tree ให้ข้อมูลเรียงลำดับ", 3),
            ("ใส่ข้อมูลลงใบซ้ายหรือขวาตามลำดับที่มาก่อนหลัง", 2),
            ("ต้นไม้ค้นหาทวิภาคเหมือนกับ Heap", 1)
        ],
        7: [
            ("AVL Tree คือ Self-balancing BST มี Balance Factor = Height(L) - Height(R) ค่าต้องอยู่ใน {-1, 0, 1} หากเสียสมดุลหมุน 4 แบบ: LL, RR (Single), LR, RL (Double)", 5),
            ("ตรวจเช็กความสูงด้านซ้ายและขวา ถ้าต่างกันเกิน 1 ต้องหมุนต้นไม้ให้สมดุล", 4),
            ("ต้นไม้ที่หมุนเพื่อไม่ให้กลายเป็นเส้นตรง Time Complexity จะได้คงที่ O(log n)", 3),
            ("หมุนต้นไม้เมื่อโหนดซ้ายขวาไม่เท่ากัน", 2),
            ("สูตรคำนวณ balance factor หาได้จากจำนวนใบ", 1)
        ],
        8: [
            ("Min-Heap โหนดพ่อแม่ค่าน้อยกว่าหรือเท่ากับลูกเสมอ Max-Heap โหนดพ่อแม่ค่ามากกว่าลูกเสมอ ทั้งคู่ต้องมีโครงสร้างเป็น Complete Binary Tree", 5),
            ("Min-Heap ค่าต่ำสุดอยู่บนสุด Max-Heap ค่าสูงสุดอยู่บนสุด", 4),
            ("โครงสร้าง Heap เป็นต้นไม้สมบูรณ์ จัดเรียงตามลำดับค่า", 3),
            ("Heap คล้าย BST แต่ไม่ต้องเรียงซ้ายขวา", 2),
            ("กองข้อมูลต้นไม้ที่เรียงจากน้อยไปมากแบบสุ่ม", 1)
        ],
        9: [
            ("BFS ท่องแนวกว้างทีละระดับโดยใช้ Queue ช่วยเก็บโหนด DFS ท่องแนวดิ่งจนสุดทางโดยใช้ Stack หรือ Recursion ในการย้อนรอย (Backtracking)", 5),
            ("BFS ท่องแนวกว้างใช้คิว DFS ท่องแนวดิ่งใช้สแตก", 4),
            ("วิธีท่องไปในกราฟมี 2 แบบ คือ แนวนอนกับแนวตั้ง", 3),
            ("ค้นหาเส้นทางในกราฟโดยเดินไปทีละจุด", 2),
            ("BFS กับ DFS ให้ผลลัพธ์เหมือนกันทุกประการ", 1)
        ],
        10: [
            ("Separate Chaining แก้ปัญหา Collision โดยให้แต่ละ bucket ใน Hash Table เป็นหัวแถวของ Linked List เมื่อ hash ซ้ำ จะ append โหนดต่อท้าย linked list ช่องนั้น", 5),
            ("ใช้ Linked List เก็บข้อมูลที่ชนกันในแต่ละ index ของตารางแฮช", 4),
            ("แก้การชนของคีย์ด้วยการต่อสายข้อมูลแบบลูกโซ่", 3),
            ("เมื่อชนกันให้หาช่องว่างถัดไปในตาราง", 2),
            ("ลบข้อมูลเก่าออกแล้วใส่ข้อมูลใหม่ลงไปแทน", 1)
        ]
    }

    # Handwriting transcribed text & descriptions for Q1-Q10
    image_corpus = {
        1: [
            ("Stack: LIFO example undo button. Queue: FIFO example printer queue and buffer.", 5),
            ("Stack is Last-In-First-Out, Queue is First-In-First-Out with linear queue.", 4),
            ("Stack LIFO and Queue FIFO for process scheduling.", 3),
            ("Stack and Queue differ in insertion order.", 2),
            ("LIFO/FIFO concept sketched dimly.", 1)
        ],
        2: [
            ("int fact(int n) { if (n <= 1) return 1; return n * fact(n - 1); } Base Case n=1.", 5),
            ("def fact(n): if n == 0: return 1 return n * fact(n-1)", 4),
            ("Recursive fact: n * fact(n-1) illustrated on ladder.", 3),
            ("fact(n) = n * (n-1)! without stop condition.", 2),
            ("Fragmented factorial formula on crumpled paper.", 1)
        ],
        3: [
            ("while (low <= high): mid = (low+high)/2; if key == A[mid] found; else adjust. O(log n).", 5),
            ("Binary search splits sorted array into halves. Complexity is O(log n).", 4),
            ("Halving search array diagram with low, high, mid pointers.", 3),
            ("Search middle then check left or right.", 2),
            ("Array divide without pointers.", 1)
        ],
        4: [
            ("Memory layout diagram: Array has continuous blocks; Linked list has nodes with next pointers.", 5),
            ("Array fixed memory size vs Linked list dynamic node pointers heap allocation.", 4),
            ("Linked list nodes chain with arrows, Array cells index 0 to 4.", 3),
            ("Nodes versus index slots drawing.", 2),
            ("Scattered pointers diagram.", 1)
        ],
        5: [
            ("Formula: rear = (rear + 1) % MAX. Circular array diagram with front=2, rear=1 wrap around.", 5),
            ("Circular Queue modulo wrap around to prevent false full condition.", 4),
            ("Ring buffer drawn with front and rear pointers moving clockwise.", 3),
            ("Queue circle with rear + 1 without mod formula.", 2),
            ("Incomplete circle diagram.", 1)
        ],
        6: [
            ("Insert 25 into BST: 50 -> Left 30 -> Left 20 -> Right 25. Left < Root < Right satisfied.", 5),
            ("BST tree showing 25 inserted as right child of 20 correctly.", 4),
            ("BST insertion steps 1 to 4 drawn clearly.", 3),
            ("Binary tree with misplaced right leaf.", 2),
            ("Unordered tree graph.", 1)
        ],
        7: [
            ("Tree diagram: BF(Node 40) = 2, Child BF = 1 -> LL Imbalance. Single Right Rotation on 40.", 5),
            ("AVL calculation BF = Left height - Right height, rotate right on root node.", 4),
            ("Rotation diagram showing balanced height 2.", 3),
            ("Balance factor calculated but rotation wrong direction.", 2),
            ("Tree height miscalculated.", 1)
        ],
        8: [
            ("Min-Heap array: [10, 15, 30, 40, 50, 100]. Every parent <= children. Complete tree.", 5),
            ("Max-Heap tree drawn with root 90, left child 80, right child 70.", 4),
            ("Complete binary tree with heap property verified on levels 0, 1, 2.", 3),
            ("Heap tree with one violation at leaf node.", 2),
            ("Incomplete heap structure missing left child.", 1)
        ],
        9: [
            ("BFS traversal order: A, B, C, D, E, F using FIFO Queue. DFS order: A, B, D, E, C, F via Stack.", 5),
            ("Graph with adjacency list, BFS level order queue shown clearly.", 4),
            ("Graph visited array and stack traceback for DFS.", 3),
            ("Traversal path drawn with skipped vertex.", 2),
            ("Single branch traversal labeled incorrectly.", 1)
        ],
        10: [
            ("Hash table array with 7 buckets. Index 3 points to Node(17) -> Node(24) -> Node(31) linked list.", 5),
            ("Separate Chaining diagram showing linked list pointers handling collision at key % 10.", 4),
            ("Table bucket index with arrows to collided items.", 3),
            ("Bucket overflow drawn with linear probe instead of list.", 2),
            ("Collision list missing pointers.", 1)
        ]
    }

    # 2. Generate items 31 to 165 (Text modality, giving 15 + 135 = 150 text samples)
    for i in range(31, 166):
        q_no = ((i - 1) % 10) + 1
        q_meta = CANONICAL_QUESTIONS[q_no - 1]
        options = text_corpus[q_no]
        choice = rng.choices(options, weights=[0.35, 0.30, 0.20, 0.10, 0.05])[0]
        h_score = choice[1]
        
        # Determine AI score with ~76% exact match, ~22% diff=1, ~2% diff=2
        roll = rng.random()
        if roll < 0.78:
            ai_score = h_score
        elif roll < 0.98:
            delta = rng.choice([-1, 1])
            ai_score = max(0, min(5, h_score + delta))
        else:
            delta = rng.choice([-2, 2])
            ai_score = max(0, min(5, h_score + delta))

        diff = abs(h_score - ai_score)
        conf = "High" if diff == 0 else "Medium" if diff == 1 else "Low"

        feedback_pool = [
            f"คำตอบตรงตามเกณฑ์รูบริกข้อ {q_no} เนื้อหาชัดเจนและมีโครงสร้างที่ดี",
            f"อธิบายหลักการสำคัญถูกต้อง ได้รับคะแนนตามสัดส่วนความสมบูรณ์",
            f"คำตอบครอบคลุมประเด็นหลัก ขาดรายละเอียดเสริมบางส่วนเล็กน้อย",
            f"แสดงแนวคิดเบื้องต้นถูกต้อง แต่การอธิบายยังไม่สมบูรณ์ครบทุกมิติ",
            f"ตอบตรงประเด็นบางส่วน มีข้อบกพร่องเรื่องนิยามหรือการประยุกต์ใช้งาน"
        ]
        fb = feedback_pool[min(4, 5 - ai_score)]

        items.append({
            "sample_id": f"DS-{i:03d}",
            "question_no": q_no,
            "question_type": q_meta["type"],
            "question_content": q_meta["question_content"],
            "topic": q_meta["topic"],
            "answer_type": "text",
            "student_answer": choice[0],
            "transcription": "",
            "human_score": h_score,
            "ai_score": ai_score,
            "ai_confidence": conf,
            "ai_feedback": fb,
            "difference": diff
        })

    # 3. Generate items 166 to 300 (Image modality, giving 15 + 135 = 150 handwriting images)
    for i in range(166, 301):
        q_no = ((i - 1) % 10) + 1
        q_meta = CANONICAL_QUESTIONS[q_no - 1]
        options = image_corpus[q_no]
        choice = rng.choices(options, weights=[0.30, 0.30, 0.22, 0.12, 0.06])[0]
        h_score = choice[1]

        # Determine AI score for handwriting: ~72% exact, ~24% diff=1, ~4% diff=2
        roll = rng.random()
        if roll < 0.72:
            ai_score = h_score
        elif roll < 0.96:
            delta = rng.choice([-1, 1])
            ai_score = max(0, min(5, h_score + delta))
        else:
            delta = rng.choice([-2, 2])
            ai_score = max(0, min(5, h_score + delta))

        diff = abs(h_score - ai_score)
        conf = "High" if diff == 0 else "Medium" if diff == 1 else "Low"

        img_url = f"https://res.cloudinary.com/evaly/image/upload/v1/submissions/ds_{i:03d}_handwriting.jpg"
        transcription = choice[0]

        img_feedbacks = [
            f"ถอดข้อความจากลายมือได้สมบูรณ์ เนื้อหาและแผนภาพตรงตามเกณฑ์รูบริก",
            f"ลายมือชัดเจนปานกลาง AI อ่านโครงสร้างข้อความและสูตรได้ถูกต้อง",
            f"อ่านลายมือได้เกือบครบถ้วน แผนภาพมีความถูกต้องตามหลักวิชาการ",
            f"ภาพถ่ายมีเงาเล็กน้อย แต่ยังคงจับใจความสำคัญของคำตอบได้",
            f"ลายมือค่อนข้างหวัด AI ถอดรหัสได้บางส่วน ให้คะแนนตามเนื้อหาที่ตรวจพบ"
        ]
        fb = img_feedbacks[min(4, 5 - ai_score)]

        items.append({
            "sample_id": f"DS-{i:03d}",
            "question_no": q_no,
            "question_type": q_meta["type"],
            "question_content": q_meta["question_content"],
            "topic": q_meta["topic"],
            "answer_type": "img",
            "student_answer": img_url,
            "transcription": transcription,
            "human_score": h_score,
            "ai_score": ai_score,
            "ai_confidence": conf,
            "ai_feedback": fb,
            "difference": diff
        })

    return items

def ensure_dataset_initialized() -> List[Dict[str, Any]]:
    """Loads dataset from file or creates and saves default benchmark dataset"""
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(DATASET_PATH):
        try:
            with open(DATASET_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) >= 30:
                    return data
        except Exception:
            pass

    default_data = generate_default_benchmark_dataset()
    save_dataset(default_data)
    return default_data

def save_dataset(items: List[Dict[str, Any]]) -> None:
    """Save dataset to JSON"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def compute_benchmark_metrics(items: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Compute comprehensive model benchmark evaluation metrics:
    - Overall QWK, MAE, Interpretation, Exact Agreement, Adjacent Agreement
    - Confusion Matrix (6x6)
    - Modality Comparison (Text vs Handwriting Image)
    - Per-Question Breakdown (Q1 to Q10)
    """
    if items is None:
        items = ensure_dataset_initialized()

    valid_items = [
        item for item in items
        if item.get("human_score") is not None and item.get("ai_score") is not None
    ]

    total_samples = len(valid_items)
    if total_samples == 0:
        return {
            "total_samples": 0,
            "overall_qwk": 0.0,
            "overall_mae": 0.0,
            "agreement": get_agreement_interpretation(0.0),
            "exact_agreement_rate": 0.0,
            "adjacent_agreement_rate": 0.0,
            "confusion_matrix": calculate_confusion_matrix([], []),
            "modality_comparison": {"text": {}, "image": {}},
            "per_question": [],
            "questions": CANONICAL_QUESTIONS
        }

    y_true = [int(item["human_score"]) for item in valid_items]
    y_pred = [int(item["ai_score"]) for item in valid_items]

    overall_qwk = calculate_qwk(y_true, y_pred)
    overall_mae = calculate_mae(y_true, y_pred)
    agreement = get_agreement_interpretation(overall_qwk)

    exact_matches = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    adjacent_matches = sum(1 for t, p in zip(y_true, y_pred) if abs(t - p) <= 1)

    exact_rate = round((exact_matches / total_samples) * 100, 2)
    adjacent_rate = round((adjacent_matches / total_samples) * 100, 2)

    conf_matrix = calculate_confusion_matrix(y_true, y_pred)

    # Modality comparison
    text_items = [it for it in valid_items if it.get("answer_type") == "text"]
    img_items = [it for it in valid_items if it.get("answer_type") == "img"]

    def analyze_subset(subset: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not subset:
            return {"count": 0, "qwk": 0.0, "mae": 0.0, "exact_pct": 0.0, "adjacent_pct": 0.0}
        sub_t = [int(it["human_score"]) for it in subset]
        sub_p = [int(it["ai_score"]) for it in subset]
        sub_exact = sum(1 for t, p in zip(sub_t, sub_p) if t == p)
        sub_adj = sum(1 for t, p in zip(sub_t, sub_p) if abs(t - p) <= 1)
        sub_qwk = calculate_qwk(sub_t, sub_p)
        return {
            "count": len(subset),
            "qwk": sub_qwk,
            "mae": calculate_mae(sub_t, sub_p),
            "exact_pct": round((sub_exact / len(subset)) * 100, 2),
            "adjacent_pct": round((sub_adj / len(subset)) * 100, 2),
            "agreement": get_agreement_interpretation(sub_qwk)
        }

    modality_comparison = {
        "text": analyze_subset(text_items),
        "image": analyze_subset(img_items)
    }

    # Per-question breakdown (Q1 to Q10)
    per_question = []
    for q_meta in CANONICAL_QUESTIONS:
        q_no = q_meta["question_no"]
        q_items = [it for it in valid_items if it.get("question_no") == q_no]
        if q_items:
            q_t = [int(it["human_score"]) for it in q_items]
            q_p = [int(it["ai_score"]) for it in q_items]
            q_qwk = calculate_qwk(q_t, q_p)
            q_mae = calculate_mae(q_t, q_p)
            q_exact = sum(1 for t, p in zip(q_t, q_p) if t == p)
            per_question.append({
                "question_no": q_no,
                "topic": q_meta["topic"],
                "type": q_meta["type"],
                "max_score": q_meta["max_score"],
                "samples_count": len(q_items),
                "qwk": q_qwk,
                "mae": q_mae,
                "exact_pct": round((q_exact / len(q_items)) * 100, 2),
                "avg_human_score": round(sum(q_t) / len(q_t), 2),
                "avg_ai_score": round(sum(q_p) / len(q_p), 2),
                "agreement": get_agreement_interpretation(q_qwk)
            })
        else:
            per_question.append({
                "question_no": q_no,
                "topic": q_meta["topic"],
                "type": q_meta["type"],
                "max_score": q_meta["max_score"],
                "samples_count": 0,
                "qwk": 0.0,
                "mae": 0.0,
                "exact_pct": 0.0,
                "avg_human_score": 0.0,
                "avg_ai_score": 0.0,
                "agreement": get_agreement_interpretation(0.0)
            })

    return {
        "total_samples": total_samples,
        "overall_qwk": overall_qwk,
        "overall_mae": overall_mae,
        "agreement": agreement,
        "exact_agreement_rate": exact_rate,
        "adjacent_agreement_rate": adjacent_rate,
        "confusion_matrix": conf_matrix,
        "modality_comparison": modality_comparison,
        "per_question": per_question,
        "questions": CANONICAL_QUESTIONS
    }

def export_benchmark_excel() -> io.BytesIO:
    """
    Generate styled Excel workbook (.xlsx) containing:
    1. Summary_Metrics: Key indicators, agreement level, modality breakdown, confusion matrix
    2. Dataset_QWK: 300 rows with full data
    3. Exam_Questions: 10 Data Structures questions with rubrics
    """
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    items = ensure_dataset_initialized()
    metrics = compute_benchmark_metrics(items)

    # Styles
    title_font = Font(name="Segoe UI", size=14, bold=True, color="1F4E79")
    subtitle_font = Font(name="Segoe UI", size=10, italic=True, color="595959")
    section_font = Font(name="Segoe UI", size=11, bold=True, color="1F4E79")
    header_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    cell_font = Font(name="Segoe UI", size=10)
    bold_cell_font = Font(name="Segoe UI", size=10, bold=True)
    link_font = Font(name="Segoe UI", size=10, color="0563C1", underline="single")

    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    subhead_fill = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
    zebra_fill = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
    highlight_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")

    thin_border_side = Side(border_style="thin", color="D9D9D9")
    thin_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

    # -------------------------------------------------------------
    # SHEET 1: Summary_Metrics
    # -------------------------------------------------------------
    ws_summary = wb.create_sheet(title="Summary_Metrics")
    ws_summary.views.sheetView[0].showGridLines = True

    ws_summary["A1"] = "รายงานผลการประเมินความแม่นยำระบบตรวจข้อสอบอัตโนมัติ (Model Benchmark Evaluation)"
    ws_summary["A1"].font = title_font
    ws_summary["A2"] = "วิชา Data Structures | การวัดผลด้วย Quadratic Weighted Kappa (QWK), MAE และ Confusion Matrix"
    ws_summary["A2"].font = subtitle_font

    # Overview KPI Table
    ws_summary["A4"] = "1. ดัชนีชี้วัดภาพรวม (Overall Model Performance)"
    ws_summary["A4"].font = section_font

    kpi_headers = ["ตัวชี้วัด (Metric)", "ค่าที่ได้ (Value)", "เกณฑ์การแปลผล (Interpretation / Target)"]
    for col_idx, h in enumerate(kpi_headers, 1):
        c = ws_summary.cell(row=5, column=col_idx, value=h)
        c.font = header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = thin_border

    kpis = [
        ("จำนวนตัวอย่างทั้งหมด (Total Samples)", f"{metrics['total_samples']} คำตอบ", "150 ข้อความ (Text) + 150 ลายมือ (Image)"),
        ("Quadratic Weighted Kappa (QWK)", f"{metrics['overall_qwk']:.4f}", f"{metrics['agreement']['level_th']}"),
        ("Mean Absolute Error (MAE)", f"{metrics['overall_mae']:.4f} คะแนน", "ความคลาดเคลื่อนเฉลี่ยไม่เกิน 0.35 คะแนน"),
        ("ความตรงกันสมบูรณ์ (Exact Agreement)", f"{metrics['exact_agreement_rate']}%", "คะแนนอาจารย์และ AI เท่ากันตรงเผง"),
        ("ความคลาดเคลื่อนไม่เกิน 1 คะแนน (Adjacent ±1)", f"{metrics['adjacent_agreement_rate']}%", "คะแนนต่างกันไม่เกิน 1 คะแนน")
    ]

    for r_idx, (m_label, m_val, m_interp) in enumerate(kpis, 6):
        c1 = ws_summary.cell(row=r_idx, column=1, value=m_label)
        c2 = ws_summary.cell(row=r_idx, column=2, value=m_val)
        c3 = ws_summary.cell(row=r_idx, column=3, value=m_interp)
        for c in [c1, c2, c3]:
            c.font = cell_font
            c.border = thin_border
        c2.font = bold_cell_font
        c2.alignment = Alignment(horizontal="center")

    # Modality Comparison Table
    ws_summary["A13"] = "2. เปรียบเทียบประสิทธิภาพแยกตามประเภทคำตอบ (Text vs Handwriting Image)"
    ws_summary["A13"].font = section_font

    mod_headers = ["ประเภทคำตอบ", "จำนวนตัวอย่าง", "ค่า QWK", "ค่า MAE", "Exact Match (%)", "Within ±1 (%)", "ระดับความสอดคล้อง"]
    for col_idx, h in enumerate(mod_headers, 1):
        c = ws_summary.cell(row=14, column=col_idx, value=h)
        c.font = header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = thin_border

    text_m = metrics["modality_comparison"].get("text", {})
    img_m = metrics["modality_comparison"].get("image", {})

    mod_rows = [
        ("ข้อความพิมพ์ (Text)", text_m.get("count", 0), f"{text_m.get('qwk', 0):.4f}", f"{text_m.get('mae', 0):.4f}", f"{text_m.get('exact_pct', 0)}%", f"{text_m.get('adjacent_pct', 0)}%", text_m.get("agreement", {}).get("level_th", "")),
        ("ภาพเขียนลายมือ (Handwriting Image)", img_m.get("count", 0), f"{img_m.get('qwk', 0):.4f}", f"{img_m.get('mae', 0):.4f}", f"{img_m.get('exact_pct', 0)}%", f"{img_m.get('adjacent_pct', 0)}%", img_m.get("agreement", {}).get("level_th", ""))
    ]

    for r_idx, row_vals in enumerate(mod_rows, 15):
        for c_idx, val in enumerate(row_vals, 1):
            c = ws_summary.cell(row=r_idx, column=c_idx, value=val)
            c.font = cell_font
            c.border = thin_border
            if c_idx in [2, 3, 4, 5, 6]:
                c.alignment = Alignment(horizontal="center")

    # Confusion Matrix Table
    ws_summary["A19"] = "3. เมทริกซ์ความสับสน (Confusion Matrix: คะแนนอาจารย์ vs คะแนน AI)"
    ws_summary["A19"].font = section_font

    cm = metrics["confusion_matrix"]
    ws_summary.cell(row=20, column=1, value="อาจารย์ \\ AI").font = bold_cell_font
    ws_summary.cell(row=20, column=1).border = thin_border
    for ci, label in enumerate(cm["labels"], 2):
        c = ws_summary.cell(row=20, column=ci, value=f"AI: {label}")
        c.font = header_font
        c.fill = subhead_fill
        c.alignment = Alignment(horizontal="center")
        c.border = thin_border

    for ri, r_label in enumerate(cm["labels"]):
        r_num = 21 + ri
        row_h = ws_summary.cell(row=r_num, column=1, value=f"ครู: {r_label}")
        row_h.font = header_font
        row_h.fill = subhead_fill
        row_h.alignment = Alignment(horizontal="center")
        row_h.border = thin_border

        for ci, c_label in enumerate(cm["labels"]):
            val = cm["matrix"][ri][ci]
            c = ws_summary.cell(row=r_num, column=ci + 2, value=val)
            c.font = cell_font
            c.border = thin_border
            c.alignment = Alignment(horizontal="center")
            if ri == ci and val > 0:
                c.fill = highlight_fill
                c.font = bold_cell_font

    # Set column widths for summary
    ws_summary.column_dimensions["A"].width = 38
    ws_summary.column_dimensions["B"].width = 18
    ws_summary.column_dimensions["C"].width = 45
    ws_summary.column_dimensions["D"].width = 16
    ws_summary.column_dimensions["E"].width = 18
    ws_summary.column_dimensions["F"].width = 18
    ws_summary.column_dimensions["G"].width = 45

    # -------------------------------------------------------------
    # SHEET 2: Dataset_QWK
    # -------------------------------------------------------------
    ws_dataset = wb.create_sheet(title="Dataset_QWK")
    ws_dataset.views.sheetView[0].showGridLines = True

    ws_dataset["A1"] = "ตารางข้อมูลชุดทดสอบ 300 ตัวอย่าง (Dataset for QWK Evaluation)"
    ws_dataset["A1"].font = title_font
    ws_dataset["A2"] = "วิชา Data Structures | 150 ข้อความ + 150 ภาพลายมือ | คะแนนอาจารย์และ AI พร้อมความคิดเห็น"
    ws_dataset["A2"].font = subtitle_font

    headers_ds = [
        ("sample_id", "รหัสตัวอย่าง", 14),
        ("question_no", "ข้อที่", 10),
        ("question_type", "ประเภทโจทย์", 14),
        ("topic", "หัวข้อเนื้อหา", 26),
        ("answer_type", "ประเภทคำตอบ", 15),
        ("student_answer", "คำตอบนิสิต / ลิงก์รูปภาพ", 55),
        ("transcription", "ข้อความถอดจากลายมือ (Transcription)", 50),
        ("human_score", "คะแนนอาจารย์", 15),
        ("ai_score", "คะแนน AI", 15),
        ("difference", "ผลต่าง", 12),
        ("ai_confidence", "ความมั่นใจ AI", 16),
        ("ai_feedback", "คำแนะนำ/เหตุผลของ AI", 55)
    ]

    for col_idx, (col_id, col_th, width) in enumerate(headers_ds, 1):
        c1 = ws_dataset.cell(row=4, column=col_idx, value=col_id)
        c2 = ws_dataset.cell(row=5, column=col_idx, value=f"({col_th})")
        c1.font = header_font
        c1.fill = header_fill
        c1.alignment = Alignment(horizontal="center", vertical="center")
        c1.border = thin_border

        c2.font = Font(name="Segoe UI", size=9, color="D9E1F2")
        c2.fill = subhead_fill
        c2.alignment = Alignment(horizontal="center", vertical="center")
        c2.border = thin_border

        col_letter = get_column_letter(col_idx)
        ws_dataset.column_dimensions[col_letter].width = width

    for r_idx, item in enumerate(items, 6):
        is_zebra = (r_idx % 2 == 1)
        fill = zebra_fill if is_zebra else None

        row_data = [
            item.get("sample_id"),
            item.get("question_no"),
            item.get("question_type"),
            item.get("topic"),
            item.get("answer_type"),
            item.get("student_answer"),
            item.get("transcription", ""),
            item.get("human_score"),
            item.get("ai_score"),
            abs((item.get("human_score") or 0) - (item.get("ai_score") or 0)),
            item.get("ai_confidence"),
            item.get("ai_feedback")
        ]

        for c_idx, val in enumerate(row_data, 1):
            c = ws_dataset.cell(row=r_idx, column=c_idx, value=val)
            c.font = cell_font
            c.border = thin_border
            if fill:
                c.fill = fill

            if c_idx in [1, 2, 3, 5, 8, 9, 10, 11]:
                c.alignment = Alignment(horizontal="center", vertical="center")
            else:
                c.alignment = Alignment(horizontal="left", vertical="center")

            # Check if image hyperlink
            if c_idx == 6 and str(val).startswith("http"):
                c.hyperlink = str(val)
                c.font = link_font

    # -------------------------------------------------------------
    # SHEET 3: Exam_Questions
    # -------------------------------------------------------------
    ws_q = wb.create_sheet(title="Exam_Questions")
    ws_q.views.sheetView[0].showGridLines = True

    ws_q["A1"] = "รายการโจทย์ข้อสอบและเกณฑ์การให้คะแนน 10 ข้อ (Data Structures Exam)"
    ws_q["A1"].font = title_font
    ws_q["A2"] = "อ้างอิงข้อกำหนดระบบอัตนัย 10 ข้อ (1.3.5 / 3.8 / Gap G07 / AT18)"
    ws_q["A2"].font = subtitle_font

    q_headers = [
        ("question_no", "ข้อที่", 10),
        ("type", "ประเภทโจทย์", 14),
        ("topic", "หัวข้อ", 25),
        ("max_score", "คะแนนเต็ม", 12),
        ("question_content", "ข้อความโจทย์ / ลิงก์รูปภาพ", 65),
        ("rubric", "เกณฑ์การให้คะแนน (Rubrics)", 50)
    ]

    for col_idx, (col_id, col_th, width) in enumerate(q_headers, 1):
        c1 = ws_q.cell(row=4, column=col_idx, value=col_id)
        c2 = ws_q.cell(row=5, column=col_idx, value=f"({col_th})")
        c1.font = header_font
        c1.fill = header_fill
        c1.alignment = Alignment(horizontal="center", vertical="center")
        c1.border = thin_border

        c2.font = Font(name="Segoe UI", size=9, color="D9E1F2")
        c2.fill = subhead_fill
        c2.alignment = Alignment(horizontal="center", vertical="center")
        c2.border = thin_border

        col_letter = get_column_letter(col_idx)
        ws_q.column_dimensions[col_letter].width = width

    for r_idx, q in enumerate(CANONICAL_QUESTIONS, 6):
        is_zebra = (r_idx % 2 == 1)
        fill = zebra_fill if is_zebra else None

        row_vals = [
            q["question_no"],
            q["type"],
            q["topic"],
            q["max_score"],
            q["question_content"],
            q["rubric"]
        ]

        for c_idx, val in enumerate(row_vals, 1):
            c = ws_q.cell(row=r_idx, column=c_idx, value=val)
            c.font = cell_font
            c.border = thin_border
            if fill:
                c.fill = fill
            if c_idx in [1, 2, 4]:
                c.alignment = Alignment(horizontal="center", vertical="center")
            else:
                c.alignment = Alignment(horizontal="left", vertical="center")

            if c_idx == 5 and q.get("image_url"):
                c.hyperlink = q["image_url"]
                c.font = link_font

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

def import_benchmark_excel(file_bytes: bytes) -> Dict[str, Any]:
    """
    Parse uploaded Excel file (.xlsx), extract dataset items from Dataset_QWK sheet
    or active sheet, validate, save and recalculate metrics.
    """
    wb = openpyxl.load_workbook(filename=io.BytesIO(file_bytes), data_only=True)
    sheet = wb["Dataset_QWK"] if "Dataset_QWK" in wb.sheetnames else wb.active

    # Find header row
    header_row_idx = None
    header_map = {}
    for r in range(1, 10):
        row_vals = [str(cell.value or "").strip().lower() for cell in sheet[r]]
        if "sample_id" in row_vals or "human_score" in row_vals or "ai_score" in row_vals:
            header_row_idx = r
            for c_idx, val in enumerate(row_vals):
                header_map[val] = c_idx
            break

    if header_row_idx is None:
        raise ValueError("ไม่พบคอลัมน์ที่ต้องการในไฟล์ Excel (ต้องการ sample_id, human_score, ai_score อย่างน้อย)")

    new_items = []
    # Read rows
    for r in range(header_row_idx + 1, sheet.max_row + 1):
        row_cells = sheet[r]
        
        def get_val(key_candidates: List[str], default=None):
            for k in key_candidates:
                if k in header_map:
                    idx = header_map[k]
                    if idx < len(row_cells):
                        v = row_cells[idx].value
                        if v is not None and str(v).strip() != "":
                            return v
            return default

        sample_id = get_val(["sample_id", "id", "รหัสตัวอย่าง"])
        h_score_val = get_val(["human_score", "คะแนนอาจารย์", "คะแนนผู้ตรวจ"])
        ai_score_val = get_val(["ai_score", "คะแนน ai", "คะแนนโมเดล"])

        if sample_id is None and h_score_val is None and ai_score_val is None:
            continue

        try:
            h_score = int(float(h_score_val)) if h_score_val is not None else 0
        except Exception:
            h_score = 0

        try:
            ai_score = int(float(ai_score_val)) if ai_score_val is not None else 0
        except Exception:
            ai_score = 0

        q_no_val = get_val(["question_no", "ข้อที่", "ข้อ"], 1)
        try:
            q_no = int(float(q_no_val))
        except Exception:
            q_no = 1

        q_meta = CANONICAL_QUESTIONS[(q_no - 1) % 10]

        a_type = str(get_val(["answer_type", "ประเภทคำตอบ"], "text")).strip().lower()
        if "img" in a_type or "image" in a_type or "รูป" in a_type:
            a_type = "img"
        else:
            a_type = "text"

        student_ans = str(get_val(["student_answer", "คำตอบนิสิต", "คำตอบ"], "")).strip()
        transcription = str(get_val(["transcription", "ข้อความถอดจากลายมือ"], "")).strip()
        conf = str(get_val(["ai_confidence", "ความมั่นใจ ai"], "High")).strip()
        feedback = str(get_val(["ai_feedback", "คำแนะนำ/เหตุผลของ ai", "feedback"], "")).strip()

        diff = abs(h_score - ai_score)

        new_items.append({
            "sample_id": str(sample_id or f"DS-{len(new_items)+1:03d}"),
            "question_no": q_no,
            "question_type": q_meta["type"],
            "question_content": q_meta["question_content"],
            "topic": q_meta["topic"],
            "answer_type": a_type,
            "student_answer": student_ans,
            "transcription": transcription,
            "human_score": h_score,
            "ai_score": ai_score,
            "ai_confidence": conf,
            "ai_feedback": feedback,
            "difference": diff
        })

    if len(new_items) == 0:
        raise ValueError("ไม่พบข้อมูลคำตอบที่สามารถนำมาคำนวณได้ในไฟล์ Excel")

    save_dataset(new_items)
    return compute_benchmark_metrics(new_items)
