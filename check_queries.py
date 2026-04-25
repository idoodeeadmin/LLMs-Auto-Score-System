import ast

with open('server/main.py', 'r', encoding='utf-8') as f:
    code = f.read()

tree = ast.parse(code)
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'execute':
        if node.args and isinstance(node.args[0], ast.Constant):
            query = node.args[0].value
            if isinstance(query, str) and '?' in query:
                # check if there's a ? that might be part of a string literal
                if "'?'" in query or '"?"' in query:
                    print('Found literal ?:', query)
                    found = True
if not found:
    print('No literal ? found in queries!')
