import os
import re

files_to_update = [
    "client/pages/Home.tsx",
    "client/components/Navbar.tsx",
    "client/pages/Index.tsx"
]

replacements = {
    r'\bbg-slate-50\b(?! dark:)': 'bg-slate-50 dark:bg-slate-900',
    r'\bbg-white\b(?!/)(?! dark:)': 'bg-white dark:bg-slate-800',
    r'\btext-slate-900\b(?! dark:)': 'text-slate-900 dark:text-white',
    r'\btext-slate-800\b(?! dark:)': 'text-slate-800 dark:text-slate-200',
    r'\btext-slate-700\b(?! dark:)': 'text-slate-700 dark:text-slate-300',
    r'\btext-slate-600\b(?! dark:)': 'text-slate-600 dark:text-slate-400',
    r'\btext-slate-500\b(?! dark:)': 'text-slate-500 dark:text-slate-400',
    r'\bborder-slate-100\b(?! dark:)': 'border-slate-100 dark:border-slate-700',
    r'\bborder-slate-200\b(?! dark:)': 'border-slate-200 dark:border-slate-700',
    r'\bborder-gray-100\b(?! dark:)': 'border-gray-100 dark:border-slate-800',
    r'\bhover:bg-slate-50\b(?! dark:)': 'hover:bg-slate-50 dark:hover:bg-slate-700/50',
    r'\bhover:bg-slate-100\b(?! dark:)': 'hover:bg-slate-100 dark:hover:bg-slate-700',
    r'\bhover:bg-gray-50\b(?! dark:)': 'hover:bg-gray-50 dark:hover:bg-slate-700/50',
    r'\bhover:bg-gray-100\b(?! dark:)': 'hover:bg-gray-100 dark:hover:bg-slate-700',
    r'\bbg-gray-50\b(?! dark:)': 'bg-gray-50 dark:bg-slate-900',
    r'\btext-gray-900\b(?! dark:)': 'text-gray-900 dark:text-white',
    r'\btext-gray-800\b(?! dark:)': 'text-gray-800 dark:text-slate-200',
    r'\btext-gray-600\b(?! dark:)': 'text-gray-600 dark:text-slate-400',
    r'\btext-gray-500\b(?! dark:)': 'text-gray-500 dark:text-slate-400',
    r'\btext-gray-400\b(?! dark:)': 'text-gray-400 dark:text-slate-500',
    r'\bbg-blue-50\b(?! dark:)': 'bg-blue-50 dark:bg-blue-900/30',
    r'\bhover:bg-blue-100\b(?! dark:)': 'hover:bg-blue-100 dark:hover:bg-blue-800/40',
    r'\bhover:bg-blue-50\b(?! dark:)': 'hover:bg-blue-50 dark:hover:bg-blue-900/40',
}

for filepath in files_to_update:
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original_content = content
    for pattern, repl in replacements.items():
        content = re.sub(pattern, repl, content)
        
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
    else:
        print(f"No changes in {filepath}")
