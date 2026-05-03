import ast
import re

with open('server/routes/room_routes.py', 'r', encoding='utf-8') as f:
    source = f.read()

tree = ast.parse(source)

exam_nodes = []
room_nodes = []

for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        is_exam_route = False
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                if hasattr(dec.func.value, 'id') and dec.func.value.id == 'router':
                    if hasattr(dec, 'args') and len(dec.args) > 0 and isinstance(dec.args[0], ast.Constant):
                        path = dec.args[0].value
                        if path.startswith('/{room_id}/exams'):
                            is_exam_route = True
                            # Remove the prefix
                            new_path = path.replace('/{room_id}/exams', '')
                            dec.args[0].value = new_path if new_path else '/'
        
        if is_exam_route:
            exam_nodes.append(node)
        else:
            room_nodes.append(node)
    else:
        room_nodes.append(node)

# Write exam_routes.py
generic_imports = """from fastapi import APIRouter, Depends, HTTPException, status, Header, UploadFile, File, Form, Request, Query, BackgroundTasks
from fastapi.responses import Response, StreamingResponse
import pymysql
import json
import csv
import io
import time
import asyncio
from typing import Optional, List

from server.database import get_db_connection
from server.auth import get_password_hash, verify_password, create_access_token, decode_token
from server.models import *
from server.main import check_rate_limit, upload_to_cloudinary, get_current_user, log_audit_action, grading_queue, trigger_socket_notify
from server.services.ai_service import _USE_GEMINI, _genai_client, _GEMINI_MODEL

"""

with open('server/routes/exam_routes.py', 'w', encoding='utf-8') as f:
    f.write(generic_imports)
    f.write('router = APIRouter(prefix="/api/rooms/{room_id}/exams", tags=["Exams"])\n\n')
    for node in exam_nodes:
        f.write(ast.unparse(node) + '\n\n')

new_tree = ast.Module(body=room_nodes, type_ignores=[])
with open('server/routes/room_routes.py', 'w', encoding='utf-8') as f:
    f.write(ast.unparse(new_tree))

print(f"Extracted {len(exam_nodes)} exam routes out of room_routes.py!")
