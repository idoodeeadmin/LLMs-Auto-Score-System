import ast
import os
import glob

# Functions and variables to move
targets = {'get_image_bytes', 'trigger_socket_notify', 'check_rate_limit', 'log_audit_action', 'upload_to_cloudinary', 'get_current_user', 'generate_class_code', 'grading_queue'}

with open('server/main.py', 'r', encoding='utf-8') as f:
    source = f.read()

tree = ast.parse(source)

utils_nodes = []
main_nodes = []

for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in targets:
        utils_nodes.append(node)
    elif isinstance(node, ast.Assign):
        is_target = any(isinstance(t, ast.Name) and t.id in targets for t in node.targets)
        if is_target:
            utils_nodes.append(node)
        else:
            main_nodes.append(node)
    else:
        main_nodes.append(node)

# Create utils.py
utils_imports = """import os
import asyncio
import httpx
import time
import cloudinary
import cloudinary.uploader
import random
import string
import aiofiles
from fastapi import Header, HTTPException, Depends
from typing import Optional

from server.database import get_db_connection
from server.auth import decode_token

"""

with open('server/utils.py', 'w', encoding='utf-8') as f:
    f.write(utils_imports)
    for node in utils_nodes:
        f.write(ast.unparse(node) + '\n\n')

# Rewrite main.py
new_tree = ast.Module(body=main_nodes, type_ignores=[])
with open('server/main.py', 'w', encoding='utf-8') as f:
    # also add import in main.py for these utils
    f.write('from server.utils import grading_queue\n')
    f.write(ast.unparse(new_tree))

# Replace imports in all routes and services
files_to_check = glob.glob('server/routes/*.py') + ['server/services/ai_service.py']
for filepath in files_to_check:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple replace
    content = content.replace('from server.main import check_rate_limit', 'from server.utils import check_rate_limit')
    content = content.replace('from server.main import get_image_bytes', 'from server.utils import get_image_bytes')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed circular imports by moving utils to server.utils")
