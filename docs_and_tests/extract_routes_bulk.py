import ast
import re
import os

with open('server/main.py', 'r', encoding='utf-8') as f:
    source = f.read()

tree = ast.parse(source)

routes = {
    'room_routes': {'prefix': '/api/rooms', 'nodes': []},
    'notification_routes': {'prefix': '/api/notifications', 'nodes': []},
    'question_bank_routes': {'prefix': '/api/question-bank', 'nodes': []},
    'ai_routes': {'prefix': '/api/gemini', 'nodes': []},
    'system_routes': {'prefix': '/api/', 'nodes': []} # Catch-all for remaining api
}

main_nodes = []

for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        is_route = False
        target_group = None
        
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                if hasattr(dec.func.value, 'id') and dec.func.value.id == 'app':
                    if hasattr(dec, 'args') and len(dec.args) > 0 and isinstance(dec.args[0], ast.Constant):
                        path = dec.args[0].value
                        if path.startswith('/api/'):
                            is_route = True
                            
                            # Match prefix
                            if path.startswith('/api/rooms'): target_group = 'room_routes'
                            elif path.startswith('/api/notifications'): target_group = 'notification_routes'
                            elif path.startswith('/api/question-bank'): target_group = 'question_bank_routes'
                            elif path.startswith('/api/gemini'): target_group = 'ai_routes'
                            else: target_group = 'system_routes'
                            
                            # Rewrite decorator
                            dec.func.value.id = 'router'
                            if target_group != 'system_routes':
                                new_path = path.replace(routes[target_group]['prefix'], '')
                                dec.args[0].value = new_path if new_path else '/'
        
        if is_route:
            routes[target_group]['nodes'].append(node)
        else:
            main_nodes.append(node)
    else:
        main_nodes.append(node)

# Write to files
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

"""

for group_name, group_data in routes.items():
    if not group_data['nodes']:
        continue
    
    file_path = f'server/routes/{group_name}.py'
    prefix_val = group_data['prefix'] if group_name != 'system_routes' else ''
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(generic_imports)
        f.write(f'router = APIRouter(prefix="{prefix_val}", tags=["{group_name.replace("_", " ").title()}"])\n\n')
        
        for node in group_data['nodes']:
            f.write(ast.unparse(node) + '\n\n')
    print(f"Extracted {len(group_data['nodes'])} routes to {file_path}")

new_tree = ast.Module(body=main_nodes, type_ignores=[])
with open('server/main.py', 'w', encoding='utf-8') as f:
    f.write(ast.unparse(new_tree))

print("Finished extracting all routes!")
