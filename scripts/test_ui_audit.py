import os
from playwright.sync_api import sync_playwright

html_path = os.path.abspath('public/audit_q4_mismatches.html').replace('\\', '/')
file_url = f'file:///{html_path}'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.goto(file_url, wait_until='networkidle')
    
    # 1. Switch to clean image tab
    page.click('#btn-clean-DS-107')
    page.wait_for_timeout(400)
    
    # 2. Click image to trigger modal
    page.click('#img-DS-107')
    page.wait_for_timeout(400)
    
    # 3. Close modal
    page.click('.btn-close')
    page.wait_for_timeout(400)
    
    # 4. Click filter button for ai-lower
    page.click('button[data-filter="ai-lower"]')
    page.wait_for_timeout(400)
    page.screenshot(path='public/screenshots/q4_filter_test.png')
    
    # 5. Type into search input
    page.fill('#searchInput', 'DS-113')
    page.wait_for_timeout(400)
    page.screenshot(path='public/screenshots/q4_search_test.png')
    
    print('Testing completed successfully!')
    browser.close()
