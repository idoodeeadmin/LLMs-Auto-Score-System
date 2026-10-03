# -*- coding: utf-8 -*-
import os

mathjax_config = """<script>
  window.MathJax = {
    tex: {
      inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
      displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
    }
  };
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>"""

for path in ['docs_and_tests/chapter4_testcases.html', 'public/chapter4_testcases.html']:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_script = '<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>'
    if old_script in content and 'window.MathJax' not in content:
        content = content.replace(old_script, mathjax_config)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated MathJax in {path}")

print("Done.")
