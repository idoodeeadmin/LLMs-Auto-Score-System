import ast
import re
import os

with open('server/main.py', 'r', encoding='utf-8') as f:
    source = f.read()

tree = ast.parse(source)

ai_nodes = []
main_nodes = []
imports_to_add = []

target_names = {'grading_worker', 'score_with_gemini', '_fallback_score'}

for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name in target_names:
            ai_nodes.append(node)
        else:
            main_nodes.append(node)
    elif isinstance(node, ast.Assign):
        # check if it assigns to _USE_GEMINI or _genai_client
        is_ai_assign = False
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in {'_USE_GEMINI', '_genai_client'}:
                is_ai_assign = True
        
        if is_ai_assign:
            ai_nodes.append(node)
        else:
            main_nodes.append(node)
    else:
        main_nodes.append(node)

# We need to grab imports that ai_service might need, but we can hardcode them
ai_imports = """import os
import asyncio
import json
import httpx
import google.genai as genai
from google.genai import types

from server.database import get_db_connection
from server.main import get_image_bytes, trigger_socket_notify, grading_queue

"""

with open('server/services/ai_service.py', 'w', encoding='utf-8') as f:
    f.write(ai_imports)
    for node in ai_nodes:
        f.write(ast.unparse(node) + '\n\n')

# Rewrite main.py
new_tree = ast.Module(body=main_nodes, type_ignores=[])
with open('server/main.py', 'w', encoding='utf-8') as f:
    f.write("from server.services.ai_service import grading_worker\n")
    f.write(ast.unparse(new_tree))

print(f"Extracted {len(ai_nodes)} AI-related nodes to server/services/ai_service.py")
