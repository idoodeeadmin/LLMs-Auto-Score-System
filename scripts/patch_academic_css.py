# -*- coding: utf-8 -*-
import os

css_addition = """
  /* --- Academic Thesis Styling for Section 4.1 --- */
  #model-evaluation table {
    width: 100%;
    table-layout: auto !important;
    border-collapse: collapse;
    margin: 10px 0 18px;
    font-size: 16.5px;
    line-height: 1.3;
    background: #fff;
  }
  #model-evaluation th {
    background: #f3f4f6 !important;
    color: #111;
    font-weight: 700;
    border: 1px solid #333 !important;
    padding: 6px 8px;
    vertical-align: middle;
  }
  #model-evaluation td {
    background: #fff !important;
    color: #111;
    border: 1px solid #333 !important;
    padding: 6px 8px;
    vertical-align: top;
  }
  #model-evaluation td:first-child {
    background: #fff !important;
    font-weight: normal;
  }
  #model-evaluation tr[style*="font-weight: bold"] td,
  #model-evaluation tr[style*="font-weight:bold"] td {
    background: #f9fafb !important;
    font-weight: 700;
  }
  #model-evaluation .example-table {
    margin: 10px 0 20px;
    table-layout: fixed !important;
  }
  #model-evaluation .example-table th {
    background: #f9fafb !important;
    width: 24% !important;
    text-align: left;
    font-weight: 700;
    vertical-align: top;
    border: 1px solid #333 !important;
  }
  #model-evaluation .example-table td {
    background: #fff !important;
    width: 76% !important;
    text-align: left;
    vertical-align: top;
    white-space: normal;
    word-break: break-word;
    border: 1px solid #333 !important;
  }
  #model-evaluation .figure {
    margin: 12px auto 14px;
    text-align: center;
  }
  #model-evaluation .figure img {
    display: block;
    margin: 0 auto 6px;
    border: 1px solid #aaa;
    border-radius: 2px;
    max-width: 90%;
    object-fit: contain;
    background: #fff;
  }
  #model-evaluation .caption {
    font-size: 15.5px;
    color: #222;
    margin-top: 4px;
    text-align: center;
    font-style: italic;
  }
  #table-4-4 td {
    vertical-align: middle;
  }
  #table-4-4 .note {
    font-size: 14px;
    color: #555;
    margin: 2px 0 0;
  }
"""

for p in ['docs_and_tests/chapter4_testcases.html', 'public/chapter4_testcases.html']:
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()

    # Place css before </style>
    if 'Academic Thesis Styling for Section 4.1' not in content:
        content = content.replace('</style>', css_addition + '\n</style>')
        with open(p, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched academic CSS in {p}")
    else:
        print(f"CSS already in {p}")

print("Done.")
