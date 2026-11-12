"""Runs every test photo through Kuverenga Lens in a headless phone browser, twice:
   A) raw photo straight into the OCR engine, B) the app clean-up step first (invert chalkboard, flatten uneven light).
Word accuracy = matched words / words on the board (difflib alignment, case and punctuation ignored).
Needs: the app served at http://127.0.0.1:8765/ and Playwright."""
import csv, difflib, glob, json, os, re, sys, time
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
PHOTOS = os.path.join(HERE, 'photos')
exe = (sorted(glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome'))) or [None])[-1]

def words(s): return re.findall(r"[a-z0-9']+", s.lower())
def accuracy(truth, got):
    t, g = words(truth), words(got)
    m = difflib.SequenceMatcher(a=t, b=g, autojunk=False)
    hits = sum(b.size for b in m.get_matching_blocks())
    extra = max(0, len(g) - hits)
    return 100 * hits / len(t), extra

JS = """async ([src, clean]) => {
  const img = await new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = src; });
  const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
  c.getContext('2d').drawImage(img, 0, 0);
  const w = await KL.getWorker();
  const input = clean ? KL.cleanImage(c, {board: KL.meanLuma(c) < 120, contrast: 75, bw: false}) : c;
  const t0 = performance.now();
  const {data} = await w.recognize(input, {}, {text: true, blocks: true});
  const ms = performance.now() - t0;
  const text = clean ? KL.joinLines(KL.linesFromOcr(data).map(l => l.map(w => w.text))) : data.text;
  return {text, ms};
}"""

rows = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe)
    pg = b.new_page(viewport={'width': 412, 'height': 915})
    pg.goto('http://127.0.0.1:8765/')
    for item in json.load(open(os.path.join(PHOTOS, 'manifest.json'))):
        src = 'http://127.0.0.1:8765/../testing/photos/' + item['file']
        import base64
        data = 'data:image/jpeg;base64,' + base64.b64encode(open(os.path.join(PHOTOS, item['file']), 'rb').read()).decode()
        for clean in (False, True):
            r = pg.evaluate(JS, [data, clean])
            acc, extra = accuracy(item['truth'], r['text'])
            rows.append({'photo': item['file'], 'language': item['lang'], 'condition': item['condition'],
                         'pipeline': 'with clean-up' if clean else 'raw photo', 'word_accuracy_pct': round(acc, 1),
                         'extra_junk_words': extra, 'seconds': round(r['ms'] / 1000, 2),
                         'ocr_text': r['text'].replace('\n', ' / ').strip()})
            print(f"{item['file']:28s} {'clean' if clean else 'raw  '} {acc:5.1f}%  junk={extra}  {r['ms']/1000:.2f}s")
    b.close()

out = os.path.join(HERE, 'accuracy_results.csv')
with open(out, 'w', newline='') as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
print('saved', out)
