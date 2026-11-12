"""Renders poster.html to an A1 PDF and a PNG. Needs the project root served at http://127.0.0.1:8766/"""
import glob, os
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
exe = (sorted(glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome'))) or [None])[-1]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe)
    pg = b.new_page(viewport={'width': 2245, 'height': 3179})
    pg.goto('http://127.0.0.1:8766/poster/poster.html'); pg.wait_for_timeout(1500)
    over = pg.evaluate("[...document.querySelectorAll('main section')].reduce((m, e) => Math.max(m, e.getBoundingClientRect().bottom), 0) - document.querySelector('footer').getBoundingClientRect().top")
    print('overlap with footer (px, must be < 0):', round(over))
    pg.screenshot(path=os.path.join(HERE, 'Kuverenga_Lens_Poster.png'))
    pg.pdf(path=os.path.join(HERE, 'Kuverenga_Lens_Poster_A1.pdf'), width='594mm', height='841mm', print_background=True, scale=1, page_ranges='1')
    b.close()
