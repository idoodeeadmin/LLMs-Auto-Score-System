# -*- coding: utf-8 -*-
"""
Redirect wrapper: builds the Chapter 4 Word Document using the official full script
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_full_chapter4_thesis_docx import generate_thesis_word_document

if __name__ == "__main__":
    generate_thesis_word_document()
