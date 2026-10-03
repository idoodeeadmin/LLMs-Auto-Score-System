import json

with open('public/audit_q4_data.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

items_json_str = json.dumps(items, ensure_ascii=False)

html_content = f'''<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>เจาะลึกข้อ 4: การตรวจภาพวาด BST เทียบภาพเฉลยมาตรฐาน (Visual Ground Truth Key) - LLMs Auto-Score System</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Sarabun:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #090d16;
      --card-bg: #111827;
      --card-border: #1f293d;
      --card-hover: #1e293b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --primary: #3b82f6;
      --primary-light: #60a5fa;
      --emerald: #10b981;
      --amber: #f59e0b;
      --rose: #f43f5e;
      --purple: #a855f7;
      --cyan: #06b6d4;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background: var(--bg);
      color: var(--text-main);
      font-family: 'Sarabun', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      line-height: 1.6;
    }}

    /* Top Navigation */
    .nav-bar {{
      background: rgba(17, 24, 39, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--card-border);
      position: sticky;
      top: 0;
      z-index: 50;
      padding: 12px 24px;
    }}

    .nav-inner {{
      max-width: 1400px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }}

    .nav-brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .badge-q4 {{
      background: linear-gradient(135deg, #2563eb, #7c3aed);
      color: #fff;
      font-size: 12px;
      font-weight: 800;
      padding: 4px 10px;
      border-radius: 9999px;
      letter-spacing: 0.5px;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }}

    .nav-title {{
      font-size: 16px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .nav-links {{
      display: flex;
      gap: 10px;
    }}

    .btn-link {{
      background: #1e293b;
      color: #cbd5e1;
      text-decoration: none;
      font-size: 13.5px;
      font-weight: 600;
      padding: 7px 14px;
      border-radius: 8px;
      border: 1px solid #334155;
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .btn-link:hover {{
      background: #334155;
      color: #fff;
      border-color: #475569;
    }}

    /* Header Banner */
    .hero-section {{
      max-width: 1400px;
      margin: 28px auto 0;
      padding: 0 24px;
    }}

    .hero-card {{
      background: radial-gradient(circle at 10% 20%, rgba(37, 99, 235, 0.15) 0%, rgba(15, 23, 42, 0.6) 90%), #111827;
      border: 1px solid rgba(59, 130, 246, 0.3);
      border-radius: 16px;
      padding: 28px 32px;
      position: relative;
      overflow: hidden;
    }}

    .hero-title {{
      font-size: 24px;
      font-weight: 800;
      color: #fff;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
    }}

    .hero-subtitle {{
      color: var(--text-muted);
      font-size: 15px;
      max-width: 1050px;
      margin-bottom: 20px;
    }}

    /* Visual Key Callout Banner */
    .visual-key-banner {{
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 182, 212, 0.1) 100%);
      border: 1.5px solid rgba(16, 185, 129, 0.4);
      border-radius: 12px;
      padding: 16px 20px;
      margin-bottom: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }}

    .vk-info {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}

    .vk-icon {{
      background: rgba(16, 185, 129, 0.2);
      border: 1px solid rgba(16, 185, 129, 0.4);
      color: #10b981;
      width: 44px;
      height: 44px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      flex-shrink: 0;
    }}

    .vk-text h4 {{
      font-size: 15.5px;
      font-weight: 700;
      color: #a7f3d0;
      margin-bottom: 3px;
    }}

    .vk-text p {{
      font-size: 13.5px;
      color: #cbd5e1;
    }}

    .btn-view-key {{
      background: linear-gradient(135deg, #10b981, #059669);
      color: #fff;
      font-weight: 700;
      font-size: 13.5px;
      padding: 9px 18px;
      border-radius: 8px;
      border: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }}

    .btn-view-key:hover {{
      transform: translateY(-1px);
      box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
    }}

    .rubric-box {{
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 14px 18px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px;
      font-size: 13px;
    }}

    .rubric-pill {{
      background: #1e293b;
      color: #93c5fd;
      border: 1px solid #3b82f640;
      padding: 3px 10px;
      border-radius: 6px;
      font-family: 'Plus Jakarta Sans', monospace;
      font-size: 12px;
      font-weight: 600;
    }}

    /* Stats Grid */
    .stats-grid {{
      max-width: 1400px;
      margin: 20px auto 0;
      padding: 0 24px;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }}

    @media (max-width: 992px) {{
      .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}

    .stat-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      position: relative;
    }}

    .stat-card.highlight {{
      border-color: rgba(16, 185, 129, 0.5);
      background: linear-gradient(180deg, rgba(16, 185, 129, 0.08) 0%, rgba(17, 24, 39, 1) 100%);
    }}

    .stat-card.clickable {{
      cursor: pointer;
      transition: all 0.2s;
    }}

    .stat-card.clickable:hover {{
      border-color: var(--amber);
      transform: translateY(-2px);
      box-shadow: 0 8px 20px -4px rgba(245, 158, 11, 0.2);
    }}

    .stat-label {{
      font-size: 12.5px;
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }}

    .stat-value {{
      font-size: 28px;
      font-weight: 800;
      font-family: 'Plus Jakarta Sans', sans-serif;
      margin-bottom: 4px;
    }}

    .stat-desc {{
      font-size: 12.5px;
      color: var(--text-dim);
    }}

    /* 3 Mismatches Deep Dive Card */
    .deep-dive-section {{
      max-width: 1400px;
      margin: 24px auto 0;
      padding: 0 24px;
    }}

    .deep-dive-box {{
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
      border: 1.5px solid rgba(245, 158, 11, 0.4);
      border-radius: 14px;
      padding: 20px 24px;
      box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
    }}

    .dd-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      border-bottom: 1px solid rgba(245, 158, 11, 0.2);
      padding-bottom: 12px;
      flex-wrap: wrap;
      gap: 12px;
    }}

    .dd-title {{
      font-size: 17px;
      font-weight: 800;
      color: #fbbf24;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .dd-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
    }}

    @media (max-width: 1024px) {{
      .dd-grid {{ grid-template-columns: 1fr; }}
    }}

    .dd-card {{
      background: rgba(17, 24, 39, 0.9);
      border: 1px solid #334155;
      border-radius: 10px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .dd-card:hover {{
      border-color: #f59e0b;
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(245, 158, 11, 0.2);
    }}

    .dd-card-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .dd-sid {{
      font-family: 'Plus Jakarta Sans', monospace;
      font-size: 16px;
      font-weight: 800;
      color: #fff;
      background: #1e293b;
      padding: 3px 8px;
      border-radius: 6px;
    }}

    .dd-badge {{
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
    }}

    .dd-scores {{
      display: flex;
      gap: 10px;
      font-size: 13px;
      font-weight: 700;
      background: #0f172a;
      padding: 8px 12px;
      border-radius: 6px;
      border: 1px solid #1e293b;
    }}

    .dd-verdict {{
      font-size: 13.5px;
      color: #e2e8f0;
      line-height: 1.5;
    }}

    .dd-verdict strong {{
      color: #fbbf24;
    }}

    /* Filter & Search Bar */
    .controls-bar {{
      max-width: 1400px;
      margin: 24px auto 0;
      padding: 0 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }}

    .filter-group {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .filter-btn {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      font-size: 13.5px;
      font-weight: 600;
      padding: 8px 16px;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .filter-btn:hover {{
      background: var(--card-hover);
      color: #fff;
    }}

    .filter-btn.active {{
      background: var(--primary);
      color: #fff;
      border-color: var(--primary);
      box-shadow: 0 0 12px rgba(59, 130, 246, 0.4);
    }}

    .filter-btn.warning.active {{
      background: #f59e0b;
      border-color: #f59e0b;
      color: #78350f;
      box-shadow: 0 0 12px rgba(245, 158, 11, 0.5);
    }}

    .filter-btn.success.active {{
      background: #10b981;
      border-color: #10b981;
      color: #064e3b;
      box-shadow: 0 0 12px rgba(16, 185, 129, 0.5);
    }}

    .search-input {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      color: #fff;
      font-size: 14px;
      padding: 8px 16px;
      border-radius: 8px;
      outline: none;
      width: 260px;
      transition: border-color 0.2s;
    }}

    .search-input:focus {{
      border-color: var(--primary);
    }}

    /* Main Grid for Cards */
    .main-grid {{
      max-width: 1400px;
      margin: 20px auto 60px;
      padding: 0 24px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}

    .item-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      overflow: hidden;
      transition: border-color 0.2s, box-shadow 0.2s;
    }}

    .item-card:hover {{
      border-color: #334155;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }}

    .item-header {{
      background: rgba(15, 23, 42, 0.7);
      border-bottom: 1px solid var(--card-border);
      padding: 14px 22px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }}

    .student-badge-group {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .sid-pill {{
      font-size: 18px;
      font-weight: 800;
      font-family: 'Plus Jakarta Sans', monospace;
      color: #fff;
      background: #1e293b;
      padding: 4px 12px;
      border-radius: 8px;
      border: 1px solid #334155;
    }}

    .category-tag {{
      font-size: 12px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 6px;
    }}

    .score-comparison-pills {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }}

    .score-pill {{
      padding: 5px 12px;
      border-radius: 6px;
      font-size: 13.5px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .score-human {{ background: #1e293b; color: #94a3b8; border: 1px solid #334155; }}
    .score-ai {{ background: #1e3a8a; color: #60a5fa; border: 1px solid #2563eb; }}
    
    .score-diff {{
      font-size: 13px;
      font-weight: 800;
      padding: 5px 10px;
      border-radius: 6px;
    }}
    .diff-positive {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }}
    .diff-negative {{ background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }}

    /* Card Body */
    .item-body {{
      display: grid;
      grid-template-columns: 380px 1fr;
      gap: 20px;
      padding: 20px;
    }}

    @media (max-width: 992px) {{
      .item-body {{ grid-template-columns: 1fr; }}
    }}

    /* Left: Image Viewer Column */
    .image-viewer-col {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .img-toggle-tabs {{
      display: flex;
      background: #0f172a;
      border-radius: 8px;
      padding: 3px;
      border: 1px solid #1e293b;
    }}

    .img-tab-btn {{
      flex: 1;
      background: transparent;
      border: none;
      color: #94a3b8;
      font-size: 12.5px;
      font-weight: 600;
      padding: 6px 10px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s;
      text-align: center;
    }}

    .img-tab-btn.active {{
      background: #1e293b;
      color: #fff;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}

    .img-display-frame {{
      background: #000;
      border: 1px solid var(--card-border);
      border-radius: 10px;
      position: relative;
      overflow: hidden;
      aspect-ratio: 4 / 3;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }}

    .img-display-frame img {{
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
      transition: transform 0.2s;
    }}

    .img-display-frame:hover img {{
      transform: scale(1.02);
    }}

    .zoom-hint {{
      position: absolute;
      bottom: 8px;
      right: 8px;
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid #334155;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11px;
      color: #cbd5e1;
      display: flex;
      align-items: center;
      gap: 4px;
    }}

    /* Right: Analysis & Feedback Column */
    .analysis-col {{
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}

    /* New Regrade Result Banner inside Card */
    .regrade-success-box {{
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(6, 182, 212, 0.08) 100%);
      border: 1.5px solid rgba(16, 185, 129, 0.4);
      border-radius: 10px;
      padding: 12px 16px;
      display: flex;
      align-items: flex-start;
      gap: 12px;
    }}

    .regrade-success-box .badge-res {{
      background: #10b981;
      color: #042f2e;
      font-weight: 800;
      font-size: 12px;
      padding: 3px 8px;
      border-radius: 6px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      flex-shrink: 0;
    }}

    .cause-callout {{
      background: rgba(30, 41, 59, 0.5);
      border-left: 4px solid var(--amber);
      border-radius: 0 8px 8px 0;
      padding: 12px 16px;
    }}

    .cause-title {{
      font-size: 13px;
      font-weight: 700;
      color: var(--amber);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .cause-text {{
      font-size: 14px;
      color: #e2e8f0;
      line-height: 1.5;
    }}

    .feedback-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }}

    @media (max-width: 768px) {{
      .feedback-grid {{ grid-template-columns: 1fr; }}
    }}

    .fb-box {{
      background: #0f172a;
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      font-size: 13.5px;
      line-height: 1.5;
    }}

    .fb-header {{
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .fb-header.teacher {{ color: var(--primary-light); }}
    .fb-header.student {{ color: var(--emerald); }}

    /* Modal / Lightbox */
    .modal-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.9);
      backdrop-filter: blur(8px);
      z-index: 100;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }}

    .modal-overlay.active {{ display: flex; }}

    .modal-content {{
      background: #111827;
      border: 1px solid #334155;
      border-radius: 14px;
      max-width: 92vw;
      max-height: 92vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
    }}

    .modal-bar {{
      background: #1e293b;
      padding: 12px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #334155;
    }}

    .modal-img-container {{
      padding: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #000;
      overflow: auto;
    }}

    .modal-img {{
      max-width: 86vw;
      max-height: 80vh;
      object-fit: contain;
    }}

    .btn-close {{
      background: #334155;
      color: #fff;
      border: none;
      padding: 6px 14px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
    }}
  </style>
</head>
<body>

  <!-- Top Navigation -->
  <nav class="nav-bar">
    <div class="nav-inner">
      <div class="nav-brand">
        <span class="badge-q4">QUESTION 4 AUDIT</span>
        <div class="nav-title">เจาะลึกข้อสอบภาพวาด BST + การทดลองส่งตรวจใหม่ด้วยภาพเฉลย</div>
      </div>
      <div class="nav-links">
        <button class="btn-link" style="background:#10b98120; color:#10b981; border-color:#10b98150; cursor:pointer;" onclick="openModal('answer-keys/q4_bst_ground_truth.png', 'ภาพแนวคำตอบมาตรฐานที่สร้างขึ้น (Ground Truth Visual Key)')">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
          ดูภาพเฉลยมาตรฐาน
        </button>
        <a href="audit_gallery_53.html" class="btn-link">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16M4 12h16M4 18h7"/></svg>
          ดูครบทุกข้อที่ไม่ตรง
        </a>
        <a href="chapter4_testcases.html" class="btn-link">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          กลับหน้าบทที่ 4
        </a>
      </div>
    </div>
  </nav>

  <!-- Hero Banner -->
  <section class="hero-section">
    <div class="hero-card">
      <div class="hero-title">
        <span>🌳 ข้อสอบข้อที่ 4: การสร้าง Binary Search Tree (12 โหนด)</span>
      </div>
      <p class="hero-subtitle">
        โจทย์ให้สร้าง Binary Search Tree จากลำดับตัวเลข 12 ค่า: <code>9, 16, 10, 76, 5, 13, 58, 92, 11, 15, 80, 99</code> 
        โดยกำหนดคะแนนเต็ม 1.00 คะแนน (เกณฑ์ Binary: ถูกต้องครบถ้วนได้ 1.00 หรือผิดหลักการได้ 0.00) จากจำนวนผู้สอบทั้งหมด 34 คน
      </p>

      <!-- Visual Key Innovation Banner -->
      <div class="visual-key-banner">
        <div class="vk-info">
          <div class="vk-icon">🎯</div>
          <div class="vk-text">
            <h4>ผลการทดลองส่งตรวจใหม่ด้วย "ภาพแนวคำตอบมาตรฐาน (Visual Ground Truth Key)"</h4>
            <p>เมื่อแนบภาพเฉลยมาตรฐานที่สร้างเองเข้าสู่โมเดล VLM ความแม่นยำพุ่งขึ้นจาก <strong>79.41% (27/34)</strong> เป็น <strong style="color:#34d399; font-size:16px;">91.18% (31/34)</strong>! และแก้ปัญหา AI มองข้ามเส้นเชื่อมของ DS-114 ได้สำเร็จ 100%</p>
          </div>
        </div>
        <button class="btn-view-key" onclick="openModal('answer-keys/q4_bst_ground_truth.png', 'ภาพแนวคำตอบมาตรฐานที่สร้างขึ้น (Ground Truth Visual Key)')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
          เปิดดูภาพเฉลยที่แนบตรวจ
        </button>
      </div>

      <div class="rubric-box">
        <span style="font-weight:700; color:#cbd5e1;">โครงสร้างเฉลยมาตรฐาน (Key Structure):</span>
        <span class="rubric-pill">Root = 9 (ซ้าย 5, ขวา 16)</span>
        <span class="rubric-pill">ใต้ 16: ซ้าย 10, ขวา 76</span>
        <span class="rubric-pill">ใต้ 10: ขวา 13</span>
        <span class="rubric-pill">ใต้ 13: ซ้าย 11, ขวา 15 (ห้ามต่อใต้ 58)</span>
        <span class="rubric-pill">ใต้ 76: ซ้าย 58 (Leaf Node), ขวา 92</span>
        <span class="rubric-pill">ใต้ 92: ซ้าย 80, ขวา 99</span>
      </div>
    </div>
  </section>

  <!-- Stats Grid -->
  <section class="stats-grid">
    <div class="stat-card">
      <span class="stat-label">ตรวจแบบเดิม (Text Rubric)</span>
      <span class="stat-value" style="color:var(--text-muted);">27 / 34</span>
      <span class="stat-desc">ความสอดคล้อง 79.41% (ไม่ตรง 7 ข้อ)</span>
    </div>

    <div class="stat-card highlight">
      <span class="stat-label" style="color:#34d399;">ตรวจใหม่ด้วยภาพเฉลย (Visual Key)</span>
      <span class="stat-value" style="color:#10b981;">31 / 34</span>
      <span class="stat-desc" style="color:#a7f3d0; font-weight:600;">ความสอดคล้อง 91.18% (ไม่ตรงเหลือเพียง 3 ข้อ!)</span>
    </div>

    <div class="stat-card">
      <span class="stat-label">แก้ปัญหา AI Hallucination</span>
      <span class="stat-value" style="color:var(--cyan);">DS-114 ✅</span>
      <span class="stat-desc">เดิม AI ให้ 1 -> ตรวจใหม่ให้ 0 ตรงอาจารย์</span>
    </div>

    <div class="stat-card clickable" onclick="applyFilter('mismatch')" title="คลิกเพื่อกรองดูเฉพาะ 3 ข้อที่ยังไม่ตรง">
      <span class="stat-label">ข้อที่ไม่ตรงที่ยังเหลือ (คลิกดู)</span>
      <span class="stat-value" style="color:var(--amber);">3 ข้อ 👉</span>
      <span class="stat-desc">DS-111 (ลายมือทับ), DS-121 (คะแนนเศษ), DS-122 (กิ่งผิด)</span>
    </div>
  </section>

  <!-- Deep Dive 3 Remaining Mismatches Section -->
  <section class="deep-dive-section" id="deepDiveSection">
    <div class="deep-dive-box">
      <div class="dd-header">
        <div class="dd-title">
          <span>🔍 ผ่าประเด็น 3 ข้อที่ยังตรวจไม่ตรง: ใครถูก ใครผิด? (Remaining 3 Mismatches)</span>
        </div>
        <span style="font-size:12.5px; color:#cbd5e1;">(คลิกที่การ์ดเพื่อเลื่อนไปดูภาพคำตอบจริงและคำอธิบายโดยละเอียด)</span>
      </div>

      <div class="dd-grid">
        <!-- DS-111 -->
        <div class="dd-card" onclick="focusCard('DS-111')">
          <div class="dd-card-top">
            <span class="dd-sid">DS-111</span>
            <span class="dd-badge" style="background:#fbbf2420; color:#fbbf24; border:1px solid #fbbf2440;">ลายมือ/ตารางซ้อนทับ</span>
          </div>
          <div class="dd-scores">
            <span style="color:#94a3b8;">ครู: <strong style="color:#fff;">1.00</strong></span>
            <span style="color:#60a5fa;">AI: <strong style="color:#fff;">0.00</strong></span>
            <span style="color:#f59e0b;">(Confidence: Medium)</span>
          </div>
          <div class="dd-verdict">
            <strong>คำวินิจฉัย:</strong> นิสิตวาดโครงสร้าง Complete Tree Skeleton (มีวงกลม <code>-</code> เปล่าทั้งสองข้างเพื่อเตรียมทำข้อ 5 Array) ทำให้มีเส้นตารางทับซ้อน AI สับสนเส้นเชื่อม 80 กับ 58 จึงตัดคะแนน <strong>แต่ AI มีระบบ Safety Net ออกคำเตือนให้อาจารย์ตรวจซ้ำด้วยตนเอง</strong>
          </div>
        </div>

        <!-- DS-121 -->
        <div class="dd-card" onclick="focusCard('DS-121')">
          <div class="dd-card-top">
            <span class="dd-sid">DS-121</span>
            <span class="dd-badge" style="background:#c084fc20; color:#c084fc; border:1px solid #c084fc40;">Human Score Anomaly</span>
          </div>
          <div class="dd-scores">
            <span style="color:#94a3b8;">ครู: <strong style="color:#fff;">0.25</strong></span>
            <span style="color:#60a5fa;">AI: <strong style="color:#fff;">1.00</strong></span>
            <span style="color:#a855f7;">(คะแนนเศษจากเต็ม 1.0)</span>
          </div>
          <div class="dd-verdict">
            <strong>คำวินิจฉัย:</strong> เกณฑ์ข้อสอบเป็นแบบ <strong>Binary (0 หรือ 1)</strong> แต่อาจารย์ให้คะแนนเศษ <strong>0.25</strong> (คาดว่าหักคะแนนรอยร่างวงกลมเกินด้านล่าง) ในขณะที่ AI ยึดตาม Rubric ว่าโหนดจริงทั้ง 12 โหนดถูกต้องตามหลัก BST จึงให้คะแนนเต็ม 1.00
          </div>
        </div>

        <!-- DS-122 -->
        <div class="dd-card" onclick="focusCard('DS-122')">
          <div class="dd-card-top">
            <span class="dd-sid">DS-122</span>
            <span class="dd-badge" style="background:#ef444420; color:#f87171; border:1px solid #ef444440;">AI ถูกต้อง 100% / ครูตรวจหลุด</span>
          </div>
          <div class="dd-scores">
            <span style="color:#94a3b8;">ครู: <strong style="color:#fff;">1.00</strong></span>
            <span style="color:#60a5fa;">AI: <strong style="color:#fff;">0.00</strong></span>
            <span style="color:#34d399;">(AI ตรวจจับเส้นเชื่อมเป๊ะ)</span>
          </div>
          <div class="dd-verdict">
            <strong>คำวินิจฉัย:</strong> <strong>นิสิตทำผิดอย่างชัดเจน!</strong> กิ่ง 76 ไม่มี 58 แต่นำ 58 ไปต่อเป็นลูกขวาของ 13 และเอา 15 ไปต่อใต้ 58 (ผิด BST รุนแรง: 58 &lt; 16 เป็นเท็จ!) <strong>AI ตรวจถูกที่ให้ 0.00 แต่อาจารย์ดูกวาดตาเร็วๆ แล้วให้ 1.00 หลุดไป</strong>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Controls & Filters -->
  <div class="controls-bar">
    <div class="filter-group">
      <button class="filter-btn active" data-filter="all" onclick="applyFilter('all')">ทั้งหมด (7 กรณีศึกษา)</button>
      <button class="filter-btn warning" data-filter="mismatch" onclick="applyFilter('mismatch')">⚠️ เฉพาะ 3 ข้อที่ยังไม่ตรง</button>
      <button class="filter-btn success" data-filter="matched" onclick="applyFilter('matched')">🎯 ตรงแล้วหลังตรวจใหม่ (4)</button>
      <button class="filter-btn" data-filter="ai-lower" onclick="applyFilter('ai-lower')">AI เข้มงวดกว่าอาจารย์ (4)</button>
      <button class="filter-btn" data-filter="ai-higher" onclick="applyFilter('ai-higher')">AI สูงกว่าอาจารย์ (3)</button>
    </div>
    <input type="text" id="searchInput" class="search-input" placeholder="ค้นหารหัส เช่น DS-114..." oninput="handleSearch()">
  </div>

  <!-- Cards Main Container -->
  <main class="main-grid" id="mismatchGrid">
    <!-- Rendered dynamically -->
  </main>

  <!-- Modal Lightbox -->
  <div class="modal-overlay" id="lightboxModal" onclick="closeModal()">
    <div class="modal-content" onclick="event.stopPropagation()">
      <div class="modal-bar">
        <span id="modalTitle" style="font-weight:700; color:#fff;">ภาพถ่ายกระดาษคำตอบ</span>
        <button class="btn-close" onclick="closeModal()">ปิด (Esc)</button>
      </div>
      <div class="modal-img-container">
        <img id="modalImg" class="modal-img" src="" alt="Enlarged view">
      </div>
    </div>
  </div>

  <script>
    const ITEMS = {items_json_str};
    let currentFilter = 'all';
    let searchQuery = '';

    function renderCards() {{
      const grid = document.getElementById('mismatchGrid');
      const filtered = ITEMS.filter(item => {{
        let matchesFilter = true;
        if (currentFilter === 'mismatch') matchesFilter = !item.regrade_match;
        else if (currentFilter === 'matched') matchesFilter = item.regrade_match;
        else if (currentFilter !== 'all') matchesFilter = (item.type === currentFilter);

        const matchesSearch = item.sid.toLowerCase().includes(searchQuery.toLowerCase()) ||
                              item.analysis.toLowerCase().includes(searchQuery.toLowerCase()) ||
                              item.cause.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesFilter && matchesSearch;
      }});

      if (filtered.length === 0) {{
        grid.innerHTML = '<div style="text-align:center; padding:60px 20px; color:#64748b;">ไม่พบข้อมูลที่ตรงกับเงื่อนไข</div>';
        return;
      }}

      grid.innerHTML = filtered.map(item => {{
        const diffClass = item.diff > 0 ? 'diff-positive' : 'diff-negative';
        const diffText = item.diff > 0 ? `+${{item.diff.toFixed(2)}}` : item.diff.toFixed(2);
        
        const regradeStatus = item.regrade_match 
          ? `<div class="regrade-success-box">
               <span class="badge-res">🎯 ตรวจใหม่ด้วยภาพเฉลย</span>
               <div>
                 <div style="font-size:13.5px; font-weight:700; color:#34d399;">
                   AI ปรับคะแนนใหม่เป็น: ${{item.regrade_ai_score.toFixed(2)}} คะแนน (ตรงกับอาจารย์ผู้สอนแล้ว 100%!)
                 </div>
                 <div style="font-size:12.5px; color:#cbd5e1; margin-top:2px;">
                   ${{item.regrade_teacher_fb}}
                 </div>
               </div>
             </div>`
          : `<div class="regrade-success-box" style="border-color:#f59e0b50; background:rgba(245,158,11,0.08);">
               <span class="badge-res" style="background:#f59e0b; color:#78350f;">⚠️ ตรวจใหม่ด้วยภาพเฉลย</span>
               <div>
                 <div style="font-size:13.5px; font-weight:700; color:#fbbf24;">
                   AI คะแนนใหม่: ${{item.regrade_ai_score.toFixed(2)}} (มนุษย์: ${{item.human_score.toFixed(2)}})
                 </div>
                 <div style="font-size:12.5px; color:#cbd5e1; margin-top:2px;">
                   ${{item.regrade_teacher_fb}}
                 </div>
               </div>
             </div>`;

        return `
          <article class="item-card" id="card-${{item.sid}}" data-sid="${{item.sid}}">
            <header class="item-header">
              <div class="student-badge-group">
                <span class="sid-pill">${{item.sid}}</span>
                <span class="category-tag" style="background:${{item.badge_color}}20; color:${{item.badge_color}}; border:1px solid ${{item.badge_color}}40;">
                  ${{item.category}}
                </span>
                <span style="font-size:12.5px; color:#64748b;">(ความมั่นใจ AI เดิม: <strong>${{item.confidence}}</strong>)</span>
              </div>

              <div class="score-comparison-pills">
                <div class="score-pill score-human">
                  <span>อาจารย์ผู้สอน:</span>
                  <span style="color:#fff; font-size:15px;">${{item.human_score.toFixed(2)}}</span>
                </div>
                <div class="score-pill score-ai">
                  <span>AI เดิม:</span>
                  <span style="color:#fff; font-size:15px;">${{item.ai_score.toFixed(2)}}</span>
                </div>
                <span class="score-diff ${{diffClass}}">ผลต่างเดิม ${{diffText}} pt</span>
              </div>
            </header>

            <div class="item-body">
              <!-- Left: Image Viewer with Toggle -->
              <div class="image-viewer-col">
                <div class="img-toggle-tabs">
                  <button class="img-tab-btn active" id="btn-raw-${{item.sid}}" onclick="switchImg('${{item.sid}}', 'raw')">
                    📷 ภาพถ่ายดิบ (รอยตรวจอาจารย์)
                  </button>
                  <button class="img-tab-btn" id="btn-clean-${{item.sid}}" onclick="switchImg('${{item.sid}}', 'clean')">
                    ✨ ภาพสะอาด (ที่ AI ใช้ตรวจ)
                  </button>
                </div>
                
                <div class="img-display-frame" onclick="openModal(document.getElementById('img-${{item.sid}}').src, '${{item.sid}} - กระดาษคำตอบ')">
                  <img id="img-${{item.sid}}" src="${{item.raw_img}}" alt="Student Answer Sheet">
                  <div class="zoom-hint">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
                    คลิกเพื่อซูมดูรูปใหญ่
                  </div>
                </div>
              </div>

              <!-- Right: Analysis & Feedback -->
              <div class="analysis-col">
                <!-- Regrade Result with Visual Key -->
                ${{regradeStatus}}

                <!-- Diagnostic Root Cause -->
                <div class="cause-callout">
                  <div class="cause-title">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
                    สาเหตุเชิงลึกเดิม (Diagnostic Root Cause): <strong>${{item.cause}}</strong>
                  </div>
                  <p class="cause-text">${{item.analysis}}</p>
                </div>

                <!-- Feedbacks Grid -->
                <div class="feedback-grid">
                  <div class="fb-box teacher">
                    <div class="fb-header teacher">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
                      คำอธิบายเดิม [สำหรับผู้สอน]
                    </div>
                    <p style="color:#cbd5e1;">${{item.teacher_feedback}}</p>
                  </div>

                  <div class="fb-box student">
                    <div class="fb-header student">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
                      คำแนะนำเชิงพัฒนา [สำหรับนักเรียน]
                    </div>
                    <p style="color:#cbd5e1;">${{item.student_feedback}}</p>
                  </div>
                </div>
              </div>
            </div>
          </article>
        `;
      }}).join('');
    }}

    function switchImg(sid, type) {{
      const imgElem = document.getElementById(`img-${{sid}}`);
      const btnRaw = document.getElementById(`btn-raw-${{sid}}`);
      const btnClean = document.getElementById(`btn-clean-${{sid}}`);
      
      const item = ITEMS.find(x => x.sid === sid);
      if (!item) return;

      if (type === 'clean') {{
        imgElem.src = item.clean_img;
        btnClean.classList.add('active');
        btnRaw.classList.remove('active');
      }} else {{
        imgElem.src = item.raw_img;
        btnRaw.classList.add('active');
        btnClean.classList.remove('active');
      }}
    }}

    function applyFilter(filter) {{
      currentFilter = filter;
      document.querySelectorAll('.filter-btn').forEach(btn => {{
        btn.classList.toggle('active', btn.getAttribute('data-filter') === filter);
      }});
      renderCards();
    }}

    function handleSearch() {{
      searchQuery = document.getElementById('searchInput').value;
      renderCards();
    }}

    function openModal(imgSrc, title) {{
      document.getElementById('modalImg').src = imgSrc;
      document.getElementById('modalTitle').innerText = title;
      document.getElementById('lightboxModal').classList.add('active');
    }}

    function closeModal() {{
      document.getElementById('lightboxModal').classList.remove('active');
    }}

    document.addEventListener('keydown', (e) => {{
      if (e.key === 'Escape') closeModal();
    }});

    function focusCard(sid) {{
      applyFilter('all');
      setTimeout(() => {{
        const card = document.querySelector(`.item-card[data-sid="${{sid}}"]`);
        if (card) {{
          card.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
          card.style.outline = '3px solid #f59e0b';
          card.style.boxShadow = '0 0 25px rgba(245, 158, 11, 0.6)';
          setTimeout(() => {{
            card.style.outline = '';
            card.style.boxShadow = '';
          }}, 3000);
        }}
      }}, 100);
    }}

    // Initialize
    renderCards();
  </script>
</body>
</html>
'''

with open('public/audit_q4_mismatches.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Generated public/audit_q4_mismatches.html with Visual Key comparison successfully!")
