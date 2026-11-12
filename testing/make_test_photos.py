"""Kuverenga Lens test set: simulated chalkboard photos under 7 classroom conditions.
Run: python make_test_photos.py <handwriting.ttf> <print.ttf>"""
import sys, random, json, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HAND, PRINT = sys.argv[1], sys.argv[2]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'photos')
TEXTS = {
    'english': ["Science: Plants", "Plants need water and sunlight", "to grow. The leaves make food",
                "for the plant. Roots take water", "from the soil."],
    'shona': ["Chishona: Rondedzero", "Mwana anoenda kuchikoro", "mangwanani. Amai vari kubika",
              "sadza. Baba vari kurima", "munda wechibage."],
}

def board(lines, font_path, size=66, seed=1, dust=0.0):
    rnd = random.Random(seed)
    W, H = 1600, 1000
    im = Image.new('RGB', (W, H), (36, 64, 52))
    px = im.load()
    for _ in range(120000):
        x, y = rnd.randrange(W), rnd.randrange(H); d = rnd.randint(-9, 9)
        r, g, b = px[x, y]; px[x, y] = (r + d, g + d, b + d)
    d = ImageDraw.Draw(im)
    for _ in range(10):  # faint old-chalk wipe marks
        x, y = rnd.randrange(W), rnd.randrange(H)
        d.ellipse([x, y, x + rnd.randint(150, 420), y + rnd.randint(40, 110)], fill=(44, 72, 60))
    im = im.filter(ImageFilter.GaussianBlur(6))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(font_path, size)
    y = 110
    for ln in lines:
        d.text((90 + rnd.randint(-10, 10), y), ln, font=f, fill=(234, 231, 218))
        y += 120
    if dust:
        layer = Image.new('L', (W, H), 0); ld = ImageDraw.Draw(layer)
        for _ in range(int(60 * dust)):
            x, y = rnd.randrange(W), rnd.randrange(H)
            ld.ellipse([x, y, x + rnd.randint(120, 380), y + rnd.randint(30, 90)], fill=int(70 * dust))
        layer = layer.filter(ImageFilter.GaussianBlur(18))
        im = Image.composite(Image.new('RGB', (W, H), (200, 205, 195)), im, layer)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(110, 74, 40), width=26)
    return im.filter(ImageFilter.GaussianBlur(0.7))

def perspective(im, k=0.12):
    W, H = im.size
    # map a trapezoid to the image (board photographed from the side)
    coeffs = find_coeffs([(0, 0), (W, int(H * k)), (W, int(H * (1 - k))), (0, H)],
                         [(0, 0), (W, 0), (W, H), (0, H)])
    return im.transform((W, H), Image.PERSPECTIVE, coeffs, Image.BICUBIC, fillcolor=(150, 140, 120))

def find_coeffs(pa, pb):
    import numpy as np
    m = []
    for p1, p2 in zip(pa, pb):
        m.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        m.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])
    A = np.array(m, dtype=float); B = np.array(pb).reshape(8)
    return np.linalg.solve(A, B).tolist()

def glare(im, strength=0.75):
    W, H = im.size
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    d.ellipse([W * 0.35, H * 0.05, W * 0.85, H * 0.75], fill=int(255 * strength))
    m = m.filter(ImageFilter.GaussianBlur(120))
    return Image.composite(Image.new('RGB', (W, H), (245, 245, 235)), im, m)

def far(im, scale=0.38):
    W, H = im.size
    small = im.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
    return small

CONDITIONS = {
    '1_good':   lambda im: im.rotate(1.0, resample=Image.BICUBIC, fillcolor=(150, 140, 120)),
    '2_angle':  lambda im: perspective(im, 0.12),
    '3_shake':  lambda im: im.filter(ImageFilter.GaussianBlur(3.2)),
    '4_dim':    lambda im: ImageEnhance.Contrast(ImageEnhance.Brightness(im).enhance(0.45)).enhance(0.6),
    '5_glare':  lambda im: glare(im, 0.8),
    '6_far':    lambda im: far(im, 0.38),
    '7_dusty':  None,  # handled in board() with chalk dust
}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for lang, lines in TEXTS.items():
        for cond, fn in CONDITIONS.items():
            im = board(lines, HAND, seed=hash((lang, cond)) % 1000, dust=1.0 if cond == '7_dusty' else 0)
            if fn: im = fn(im)
            name = f'{lang}_{cond}.jpg'
            im.convert('RGB').save(os.path.join(OUT, name), quality=85)
            manifest.append({'file': name, 'lang': lang, 'condition': cond, 'truth': ' '.join(lines)})
    # printed-style board used for the demo video
    for lang, lines in TEXTS.items():
        board(lines, PRINT, size=62, seed=7).rotate(1.0, resample=Image.BICUBIC, fillcolor=(150, 140, 120)) \
            .save(os.path.join(OUT, f'demo_{lang}.jpg'), quality=88)
    json.dump(manifest, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1)
    print(len(manifest), 'test photos written to', OUT)
