"""Saves each stage of the app's image clean-up for the glare photo (for the report figure)."""
import base64, glob, os
from playwright.sync_api import sync_playwright
K = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
exe = (sorted(glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome'))) or [None])[-1]
src = 'data:image/jpeg;base64,' + base64.b64encode(open(os.path.join(K, 'testing/photos/english_5_glare.jpg'), 'rb').read()).decode()
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe); pg = b.new_page(); pg.goto('http://127.0.0.1:8765/')
    out = pg.evaluate("""async (src) => {
      const img = await new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = src; });
      const c = document.createElement('canvas'); c.width = img.width; c.height = img.height; c.getContext('2d').drawImage(img,0,0);
      const a = KL.cleanImage(c, {board:true, contrast:0, bw:false}).toDataURL('image/png');
      const f = KL.cleanImage(c, {board:true, contrast:75, bw:false});
      const w = await KL.getWorker(); const {data} = await w.recognize(f, {}, {text:true, blocks:true});
      return {a, f: f.toDataURL('image/png'), text: KL.joinLines(KL.linesFromOcr(data).map(l=>l.map(w=>w.text)))};
    }""", src)
    for k, n in (('a', '2_inverted.png'), ('f', '3_flattened.png')):
        open(os.path.join(K, 'diagrams/pipeline', n), 'wb').write(base64.b64decode(out[k].split(',')[1]))
    open(os.path.join(K, 'diagrams/pipeline', '4_text.txt'), 'w').write(out['text'])
    b.close()
import shutil; shutil.copy(os.path.join(K, 'testing/photos/english_5_glare.jpg'), os.path.join(K, 'diagrams/pipeline/1_photo.jpg'))
print(out['text'])
