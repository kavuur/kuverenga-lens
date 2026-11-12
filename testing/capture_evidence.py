"""Captures screenshots of every Kuverenga Lens screen and records a captioned demo video.
Needs the app served at http://127.0.0.1:8765/ and Playwright (Chromium)."""
import glob, os, sys, time, shutil
from playwright.sync_api import sync_playwright

K = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(K, 'evidence', 'screenshots')
VID = os.path.join(K, 'evidence', 'video')
PH = os.path.join(K, 'testing', 'photos')
URL = 'http://127.0.0.1:8765/'
exe = (sorted(glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome'))) or [None])[-1]
PHONE = dict(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)

CAPTION_JS = """(txt) => {
  let el = document.getElementById('demo-cap');
  if (!el) { el = document.createElement('div'); el.id = 'demo-cap';
    el.style.cssText = 'position:fixed;left:12px;right:12px;bottom:84px;z-index:99;background:rgba(27,31,29,.92);color:#fff;' +
      'font:700 17px/1.4 Verdana,sans-serif;padding:12px 14px;border-radius:14px;text-align:center;border:2px solid #F2B33D;transition:opacity .3s;pointer-events:none';
    document.body.appendChild(el); }
  el.style.opacity = txt ? 1 : 0; el.textContent = txt || '';
}"""

def highlight(pg, i):
    pg.evaluate("""(i) => { document.querySelectorAll('#reader .current').forEach(e => e.classList.remove('current'));
      const s = KL.state.sentences[i]; if (!s) return; s.el.classList.add('current');
      document.getElementById('reader').classList.remove('idle'); if (s.words[1]) s.words[1].el.classList.add('current');
      document.getElementById('btn-play').classList.add('playing'); }""", i)

def shoot(pg, name):
    pg.wait_for_timeout(350)
    pg.evaluate("document.getElementById('toast').classList.remove('show')"); pg.wait_for_timeout(250)
    pg.screenshot(path=os.path.join(SHOTS, name))
    print('shot', name)

def screenshots(b):
    ctx = b.new_context(device_scale_factor=2, **PHONE)
    pg = ctx.new_page(); pg.goto(URL); pg.wait_for_timeout(600)
    shoot(pg, '01_home_english.png')
    pg.click('.lang-switch [data-lang=sn]'); shoot(pg, '02_home_shona.png')
    pg.click('.lang-switch [data-lang=en]')
    pg.set_input_files('#camera-input', os.path.join(PH, 'english_5_glare.jpg'))
    pg.wait_for_selector('#screen-review.active'); pg.evaluate("document.getElementById('opt-contrast').value=0; document.getElementById('opt-contrast').dispatchEvent(new Event('input'))")
    shoot(pg, '03_review_before_flatten.png')
    pg.evaluate("document.getElementById('opt-contrast').value=75; document.getElementById('opt-contrast').dispatchEvent(new Event('input'))")
    shoot(pg, '04_review_cleaned.png')
    pg.click('#btn-convert'); pg.wait_for_selector('#screen-reader.active', timeout=120000)
    shoot(pg, '05_reader_opendyslexic.png')
    pg.click('#btn-syll'); shoot(pg, '06_reader_syllables_english.png'); pg.click('#btn-syll')
    pg.click('#btn-display'); shoot(pg, '07_display_panel.png')
    pg.click('#swatches [data-v=blue]'); pg.click('#btn-display'); pg.evaluate("window.scrollTo(0,0)"); shoot(pg, '08_display_blue_background.png'); pg.click('#btn-display')
    pg.click('#swatches [data-v=dark]'); pg.click('#btn-display'); pg.evaluate("window.scrollTo(0,0)"); shoot(pg, '09_reader_dark.png')
    pg.click('#swatches [data-v=cream]') if pg.is_visible('#swatches') else pg.evaluate("document.querySelector('#swatches [data-v=cream]').click()")
    highlight(pg, 1); shoot(pg, '10_reader_listening.png')
    pg.click('#btn-stop')
    pg.click('#btn-save'); pg.wait_for_timeout(300); shoot(pg, '11_note_saved.png')
    pg.click('#btn-edit'); shoot(pg, '12_fix_text.png'); pg.click('#btn-edit-cancel')
    # Shona board
    pg.evaluate("KL.show('home')")
    pg.set_input_files('#camera-input', os.path.join(PH, 'demo_shona.jpg'))
    pg.wait_for_selector('#screen-review.active'); pg.click('#btn-convert'); pg.wait_for_selector('#screen-reader.active', timeout=120000)
    pg.click('#btn-syll'); shoot(pg, '13_reader_shona_syllables.png')
    pg.evaluate("document.getElementById('opt-focus').click()"); highlight(pg, 1); shoot(pg, '14_focus_line_shona.png')
    pg.evaluate("document.getElementById('opt-focus').click()"); pg.click('#btn-stop'); pg.click('#btn-syll')
    pg.click('#btn-save'); pg.click('.tabbar [data-go=notes]'); shoot(pg, '15_my_notes.png')
    pg.click('.tabbar [data-go=help]'); shoot(pg, '16_help.png')
    pg.click('.tabbar [data-go=home]'); shoot(pg, '17_home_with_recent_notes.png')
    ctx.close()

def video(b):
    tmp = os.path.join(VID, '_raw'); os.makedirs(tmp, exist_ok=True)
    ctx = b.new_context(device_scale_factor=1, record_video_dir=tmp, record_video_size={'width': 390, 'height': 844}, **PHONE)
    pg = ctx.new_page(); pg.goto(URL); pg.wait_for_timeout(500)
    cap = lambda t, ms=2600: (pg.evaluate(CAPTION_JS, t), pg.wait_for_timeout(ms))
    cap('Kuverenga Lens: the chalkboard becomes a dyslexia-friendly reader', 3500)
    cap('Step 1 - SNAP: the learner photographs the board', 2600)
    pg.set_input_files('#camera-input', os.path.join(PH, 'english_5_glare.jpg'))
    pg.wait_for_selector('#screen-review.active')
    pg.evaluate("document.getElementById('opt-contrast').value=0; document.getElementById('opt-contrast').dispatchEvent(new Event('input'))")
    cap('Glare from the window makes part of the board hard to read', 3000)
    for v in range(0, 80, 5):
        pg.evaluate(f"document.getElementById('opt-contrast').value={v}; document.getElementById('opt-contrast').dispatchEvent(new Event('input'))")
        pg.wait_for_timeout(90)
    cap('Step 2 - CONVERT: the app removes the glare and turns chalk into dark text', 3200)
    pg.click('#btn-convert'); pg.wait_for_selector('#screen-reader.active', timeout=120000)
    cap('Step 3 - READ: clear OpenDyslexic letters, wide spacing, a calm background', 3400)
    for i in range(len(pg.evaluate("KL.state.sentences.map(s=>s.text)"))):
        highlight(pg, i); cap('Listen: the app reads aloud and highlights each sentence', 1500)
    pg.click('#btn-stop')
    pg.click('#btn-syll'); cap('Syllables: long words are split into small parts', 3000)
    pg.click('#btn-display'); cap('Display: the learner chooses font, size, spacing and colour', 1800)
    for c in ['blue', 'green', 'yellow', 'peach', 'dark', 'cream']:
        pg.click(f'#swatches [data-v={c}]'); pg.wait_for_timeout(450)
    pg.click('#btn-display'); pg.click('#btn-syll')
    pg.click('.lang-switch [data-lang=sn]'); pg.evaluate("KL.show('home')")
    cap('ChiShona: the whole app also works in Shona', 2600)
    pg.set_input_files('#camera-input', os.path.join(PH, 'demo_shona.jpg'))
    pg.wait_for_selector('#screen-review.active'); pg.wait_for_timeout(800)
    pg.click('#btn-convert'); pg.wait_for_selector('#screen-reader.active', timeout=120000)
    pg.click('#btn-syll'); cap('Shona syllables: ma·ngwa·na·ni, ku·chi·ko·ro', 3400)
    pg.click('#btn-save'); pg.wait_for_timeout(900)
    pg.click('.tabbar [data-go=notes]'); cap('Notes are saved on the phone and work without internet', 3000)
    pg.click('.lang-switch [data-lang=en]'); pg.click('.tabbar [data-go=home]')
    cap('Kuverenga Lens - Snap. Convert. Read.', 3000)
    path = pg.video.path(); ctx.close()
    dst = os.path.join(VID, 'kuverenga_lens_demo.webm'); shutil.move(path, dst); shutil.rmtree(tmp, ignore_errors=True)
    print('video', dst)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe)
    if 'video-only' not in sys.argv: screenshots(b)
    if 'shots-only' not in sys.argv: video(b)
    b.close()
