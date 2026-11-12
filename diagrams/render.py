"""Renders each figure in diagrams.html to a PNG. Needs the project root served at http://127.0.0.1:8766/"""
import glob, os
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
exe = (sorted(glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome'))) or [None])[-1]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe)
    pg = b.new_page(viewport={'width': 1700, 'height': 1200}, device_scale_factor=1.5)
    pg.goto('http://127.0.0.1:8766/diagrams/diagrams.html'); pg.wait_for_timeout(1200)
    for fid in ['fig-how', 'fig-arch', 'fig-process', 'fig-pipeline', 'fig-screens']:
        pg.locator('#' + fid).screenshot(path=os.path.join(HERE, fid.replace('fig-', 'diagram_') + '.png'))
        print('rendered', fid)
    b.close()
