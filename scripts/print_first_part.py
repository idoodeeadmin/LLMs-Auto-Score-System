import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')
out = subprocess.check_output(['python', 'scripts/inspect_weird_cases.py'], text=True, encoding='utf-8')
print('\n'.join(out.splitlines()[:60]))
