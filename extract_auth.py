import ast
import re

with open('server/main.py', 'r', encoding='utf-8') as f:
    source = f.read()

tree = ast.parse(source)

auth_nodes = []
main_nodes = []

for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        is_auth_route = False
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                if hasattr(dec.func.value, 'id') and dec.func.value.id == 'app':
                    if hasattr(dec, 'args') and len(dec.args) > 0 and isinstance(dec.args[0], ast.Constant):
                        if dec.args[0].value.startswith('/api/auth'):
                            is_auth_route = True
                            dec.func.value.id = 'router'
                            dec.args[0].value = dec.args[0].value.replace('/api/auth', '')
                            if dec.args[0].value == '':
                                dec.args[0].value = '/'
        if is_auth_route:
            auth_nodes.append(node)
        else:
            main_nodes.append(node)
    else:
        main_nodes.append(node)

auth_code = [ast.unparse(node) for node in auth_nodes]

imports = """from fastapi import APIRouter, Depends, HTTPException, status, Header, UploadFile, File, Form, Request
import pymysql
import uuid
import smtplib
from datetime import datetime, timezone, timedelta
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from server.database import get_db_connection
from server.auth import get_password_hash, verify_password, create_access_token, decode_token
from server.models import *
from server.main import check_rate_limit, upload_to_cloudinary, get_current_user, log_audit_action

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

"""

with open('server/routes/auth_routes.py', 'w', encoding='utf-8') as f:
    f.write(imports)
    for code in auth_code:
        f.write(code + '\n\n')

new_tree = ast.Module(body=main_nodes, type_ignores=[])
with open('server/main.py', 'w', encoding='utf-8') as f:
    f.write(ast.unparse(new_tree))

print(f"Extracted {len(auth_nodes)} auth routes to auth_routes.py")
