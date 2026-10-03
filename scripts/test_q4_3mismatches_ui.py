import os
from playwright.sync_api import sync_playwright

url = "http://localhost:8080/audit_q4_mismatches.html"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 950})
    
    try:
        page.goto(url, wait_until='networkidle')
    except Exception:
        # Fallback to local file URL if localhost is down
        html_path = os.path.abspath('public/audit_q4_mismatches.html').replace('\\', '/')
        page.goto(f'file:///{html_path}', wait_until='networkidle')

    # Capture top section with deep dive
    page.screenshot(path='public/screenshots/q4_deepdive_section.png')
    print("Captured deep dive screenshot")

    # Click filter for remaining 3 mismatches
    page.click('button[data-filter="mismatch"]')
    page.wait_for_timeout(500)
    page.screenshot(path='public/screenshots/q4_3mismatches_filtered.png')
    print("Captured 3 mismatches filtered screenshot")

    # Scroll to first mismatch card (DS-111)
    card = page.locator('article[data-sid="DS-111"]')
    if card.count() > 0:
        card.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        page.screenshot(path='public/screenshots/q4_ds111_card.png')
        print("Captured DS-111 card screenshot")

    browser.close()
