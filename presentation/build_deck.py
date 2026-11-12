"""Builds the 10-minute Kuverenga Lens presentation (PowerPoint) with speaker notes, native charts and the demo video.
Also writes preview.html (same layout) for checking the slides in a browser.
Run: python build_deck.py   (needs python-pptx)"""
import csv, html, os
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.dirname(HERE)
W, H = 13.333, 7.5
GREEN, GREEN2, SUN, CHALK, INK, INK2, TINT, LINE, WHITE = '1F4D3A', '2E6B52', 'F2B33D', 'FFF8E7', '1B1F1D', '4A4F4C', 'EEF5F1', 'D9E3DD', 'FFFFFF'
BLUE, ORANGE, GREY = '2A78D6', 'EB6834', 'A9A9A2'
FONT = 'Arial'

# ------------------------------------------------------------------ data
def load(name):
    with open(os.path.join(K, 'testing', name)) as f: return list(csv.DictReader(f))
v1, v2 = load('accuracy_results_v1.csv'), load('accuracy_results_v2.csv')
COND = [('1_good', 'Good photo'), ('2_angle', 'At an angle'), ('3_shake', 'Camera shake'), ('4_dim', 'Dim room'),
        ('5_glare', 'Window glare'), ('6_far', 'Back of class'), ('7_dusty', 'Dusty board')]
def acc(rows, c, pipe):
    v = [float(r['word_accuracy_pct']) for r in rows if r['condition'] == c and r['pipeline'] == pipe]
    return sum(v) / len(v)
RAWc = [acc(v2, c, 'raw photo') for c, _ in COND]
V1c = [acc(v1, c, 'with clean-up') for c, _ in COND]
V2c = [acc(v2, c, 'with clean-up') for c, _ in COND]
RAW, V1, V2 = sum(RAWc) / 7, sum(V1c) / 7, sum(V2c) / 7

# ------------------------------------------------------------------ slide spec helpers
def rect(x, y, w, h, fill, radius=0.0, line=None, dash=False): return dict(k='rect', x=x, y=y, w=w, h=h, fill=fill, r=radius, line=line, dash=dash)
def oval(x, y, d, fill): return dict(k='oval', x=x, y=y, w=d, h=d, fill=fill)
def img(path, x, y, w, h, crop_top=None): return dict(k='img', path=path, x=x, y=y, w=w, h=h)
def text(x, y, w, h, paras, size=16, color=INK, bold=False, align='l', anchor='t', font=FONT, spacing=1.1):
    """paras: str or list of paragraphs; a paragraph is str or list of runs (text, {bold, color, hl, size, italic})"""
    if isinstance(paras, str): paras = [paras]
    return dict(k='text', x=x, y=y, w=w, h=h, paras=paras, size=size, color=color, bold=bold, align=align, anchor=anchor, font=font, spacing=spacing)
def chart(kind, x, y, w, h, **kw): d = dict(k='chart', kind=kind, x=x, y=y, w=w, h=h); d.update(kw); return d
def video(path, poster, x, y, w, h): return dict(k='video', path=path, poster=poster, x=x, y=y, w=w, h=h)

def title(t, color=GREEN): return text(0.6, 0.42, 12.1, 0.85, t, size=34, color=color, bold=True, anchor='t')
def badge(x, y, n, d=0.52, fill=GREEN, fg=SUN): return [oval(x, y, d, fill), text(x, y, d, d, str(n), size=17, color=fg, bold=True, align='c', anchor='m')]
def icon_row(x, y, w, n, head, body, hsize=19, bsize=15, gap=0.75):
    return badge(x, y + 0.02, n) + [text(x + gap, y, w - gap, 0.42, head, size=hsize, bold=True, color=INK),
                                    text(x + gap, y + 0.42, w - gap, 0.8, body, size=bsize, color=INK2)]
def stat(x, y, w, value, label, vcolor=GREEN, fill=TINT, h=1.45, vsize=40):
    return [rect(x, y, w, h, fill, 0.12), text(x + 0.2, y + 0.12, w - 0.4, 0.75, value, size=vsize, bold=True, color=vcolor, spacing=1.0),
            text(x + 0.2, y + 0.86, w - 0.4, h - 0.9, label, size=14, color=INK2)]
def phone(path, x, y, h):
    w = h * 780 / 1688
    return [rect(x - 0.06, y - 0.06, w + 0.12, h + 0.12, '222222', 0.12), img(path, x, y, w, h)]
SS = lambda n: os.path.join(K, 'evidence', 'screenshots', n)
PH = dict(hl=True, color=INK)   # placeholders: dark text on yellow highlight

SLIDES = []
def slide(bg, elements, notes): SLIDES.append(dict(bg=bg, el=[e for e in flatten(elements)], notes=notes))
def flatten(items):
    for it in items:
        if isinstance(it, list): yield from flatten(it)
        else: yield it

# ================================================================== 1 Title
slide(GREEN, [
    img(os.path.join(K, 'app/icons/icon-512.png'), 0.85, 1.55, 3.3, 3.3),
    text(4.75, 1.45, 8.0, 1.1, [[('Kuverenga ', {}), ('Lens', {'color': SUN})]], size=60, color=CHALK, bold=True),
    text(4.75, 2.7, 7.9, 1.2, 'Turning the chalkboard into a personal, dyslexia-friendly reader, in ChiShona and English', size=24, color='DCE9E1'),
    rect(4.75, 4.15, 7.6, 0.62, GREEN2, 0.3),
    text(4.75, 4.15, 7.6, 0.62, 'SNAP   →   CONVERT   →   READ', size=20, color=SUN, bold=True, align='c', anchor='m'),
    text(0.85, 6.25, 11.8, 0.5, [[('[Student name]', PH), ('  ·  ', {}), ('[Reg. no.]', PH), ('  ·  RISED 301 Innovation Project  ·  Faculty of Education, University of Zimbabwe  ·  November 2026', {})]], size=14, color='BFD5C8'),
], """(about 30 seconds)
Good morning. My name is [name]. My innovation is called Kuverenga Lens. "Kuverenga" means "to read" in ChiShona.
Kuverenga Lens is a phone app that turns the chalkboard into a personal, dyslexia-friendly reader. It works in three steps: snap, convert and read.
In the next ten minutes I will explain the problem, show how I designed and built the app, what my tests found, and how it could reach schools.""")

# ================================================================== 2 Problem
slide(WHITE, [
    title('Copying from the chalkboard is a daily barrier'),
    icon_row(0.6, 1.7, 6.2, 1, 'Notes live on the board, then get wiped', 'Learners must read and copy before the teacher rubs the board for the next part of the lesson.'),
    icon_row(0.6, 3.05, 6.2, 2, 'Dyslexia makes this much harder', 'Letters such as b and d swap, learners lose their place between board and book, and copying is slow.'),
    icon_row(0.6, 4.4, 6.2, 3, 'Glare, dust and distance add to it', 'Chalk on a green board has low contrast; window glare and old chalk hide words.'),
    img(os.path.join(K, 'testing/photos/english_5_glare.jpg'), 7.3, 1.7, 5.4, 3.375),
    text(7.3, 5.12, 5.4, 0.3, 'A board with window glare (test photo)', size=11, color=INK2),
    stat(0.6, 5.65, 6.2, '15–20%', 'of people show some signs of dyslexia (IDA)', h=1.35, vsize=34),
], """(about 1 minute)
In our schools, the chalkboard is still the main way notes are shared. Learners must read and copy them before the board is wiped.
For a learner with dyslexia this is a daily struggle. Dyslexia is a specific difficulty with reading and spelling. It is not about intelligence. Letters like b and d swap, learners lose their place when they look from the board to their book, and they copy slowly.
The classroom makes it worse. Chalk on a green board has low contrast, glare from the windows washes out words, as in this photo, and learners at the back see small letters.
The International Dyslexia Association estimates that 15 to 20 percent of people show some signs of dyslexia, so there are several such learners in every class.""")

# ================================================================== 3 Needs assessment
slide(WHITE, [
    title('What learners and teachers told me'),
    stat(0.6, 1.65, 3.85, '[ ]%', 'of learners said the board is often or always hard to read', h=1.75, vsize=44),
    stat(4.75, 1.65, 3.85, '[ ] of [ ]', 'teachers said slow copying often or always delays lessons', h=1.75, vsize=44),
    stat(8.9, 1.65, 3.85, '[ ]%', 'of learners can use a phone at home (own or family)', h=1.75, vsize=44),
    rect(0.6, 3.75, 7.6, 3.15, WHITE, 0.12, line='9FB8AA', dash=True),
    text(0.6, 3.75, 7.6, 3.15, [[('[Paste the Summary chart from needs_assessment_template.xlsx here]', PH)]], size=15, color=INK2, align='c', anchor='m'),
    text(8.6, 3.85, 4.1, 0.4, 'How the data was collected', size=18, bold=True),
    text(8.6, 4.35, 4.1, 2.6, [
        [('Learner questionnaire: ', {'bold': True}), ('[n]', PH), (' learners', {})],
        [('Teacher questionnaire: ', {'bold': True}), ('[n]', PH), (' teachers', {})],
        [('Lesson observations: ', {'bold': True}), ('[n]', PH)],
        [('Where: ', {'bold': True}), ('[School name, District]', PH)],
        [('Ethics: ', {'bold': True}), ('head\'s permission, parent consent, learner codes, no names', {})],
    ], size=14, color=INK2, spacing=1.25),
], """(about 50 seconds)
Before designing anything, I carried out a needs assessment at [school name]. I used a short questionnaire with [n] learners and [n] teachers, and observed [n] lessons.
[Read out your three key numbers.]
[Describe one thing you observed, for example how long notes stayed on the board before being wiped.]
This confirmed the need: learners struggle to read and copy from the board, and many families have access to a phone.""")

# ================================================================== 4 Aim & brief
slide(WHITE, [
    title('Aim: a free reading lens on every learner\'s phone'),
    rect(0.6, 1.6, 5.9, 5.2, GREEN, 0.15),
    text(0.95, 1.85, 5.2, 0.45, 'Aim', size=20, bold=True, color=SUN),
    text(0.95, 2.35, 5.2, 1.7, 'Design, build and test a free phone app that turns chalkboard notes into dyslexia-friendly text that learners can read and hear, in ChiShona and English.', size=17, color=CHALK, spacing=1.2),
    text(0.95, 4.15, 5.2, 0.45, 'Hypothesis', size=20, bold=True, color=SUN),
    text(0.95, 4.65, 5.2, 1.9, 'Cleaning the photo (inverting the chalk and removing glare) before text recognition gives higher word accuracy than using the raw photo.', size=17, color=CHALK, spacing=1.2),
    text(6.95, 1.6, 5.8, 0.45, 'Design brief: it must…', size=20, bold=True, color=GREEN),
] + [
    [rect(6.95 + (i % 2) * 2.95, 2.25 + (i // 2) * 1.55, 2.8, 1.38, TINT, 0.12),
     text(7.15 + (i % 2) * 2.95, 2.37 + (i // 2) * 1.55, 2.5, 0.45, h_, size=15, bold=True, color=GREEN),
     text(7.15 + (i % 2) * 2.95, 2.82 + (i // 2) * 1.55, 2.45, 0.75, b_, size=13, color=INK2)]
    for i, (h_, b_) in enumerate([('Run on cheap phones', 'Android or iPhone, small download'), ('Work offline', 'No data needed in class'),
                                  ('Skip the Play Store', 'Install from a link or APK'), ('Stay private', 'Photos never leave the phone'),
                                  ('Speak two languages', 'ChiShona and English'), ('Be simple', 'Three taps from board to reading')])
], """(about 40 seconds)
So my aim was to design, build and test a free phone app that turns chalkboard notes into dyslexia-friendly text that learners can read and hear, in ChiShona and English.
My hypothesis was that cleaning the photo before text recognition would give higher accuracy than using the raw photo.
The design brief set six requirements: it must run on cheap phones, work offline, avoid the Play Store, keep learners' photos private, support both languages, and be simple, with three taps from board to reading.""")

# ================================================================== 5 Solution
cards = [('1', 'SNAP', 'Point the phone at the board and take a picture. A dark chalkboard is detected automatically.', '01_home_english.png'),
         ('2', 'CONVERT', 'The app turns chalk into dark text, removes glare, then reads the letters on the phone.', '04_review_cleaned.png'),
         ('3', 'READ', 'Clear dyslexia-friendly text that is read aloud, with syllables and colours.', '05_reader_opendyslexic.png')]
els = [title('The solution: Snap. Convert. Read.')]
for i, (n, h_, b_, shot) in enumerate(cards):
    x = 0.6 + i * 4.15
    els += [rect(x, 1.55, 3.9, 5.35, TINT, 0.15)] + phone(SS(shot), x + 0.3, 1.85, 4.75) + badge(x + 2.65, 1.85, n) + [
        text(x + 2.65, 2.5, 1.2, 0.45, h_, size=15, bold=True, color=GREEN),
        text(x + 2.65, 2.95, 1.15, 3.7, b_, size=12, color=INK2, spacing=1.2)]
slide(WHITE, els, """(about 50 seconds)
Here is how it works.
Step one, SNAP: the learner points the phone at the board and takes a picture. The app notices that it is a dark chalkboard.
Step two, CONVERT: the app cleans the photo. It turns the light chalk into dark letters, removes glare, and then a text-recognition engine reads the letters. This all happens on the phone, with no internet.
Step three, READ: the learner sees the notes in a dyslexia-friendly style and can listen to them.""")

# ================================================================== 6 Innovative
els = [title('Designed for dyslexia, and for ChiShona')]
els += phone(SS('13_reader_shona_syllables.png'), 0.75, 1.6, 5.2) + phone(SS('07_display_panel.png'), 3.45, 1.6, 5.2)
feats = [('OpenDyslexic font', 'Heavy letter bottoms so b and d do not flip; a plain font is also offered'),
         ('Wide spacing and calm colours', 'Double line spacing; cream, blue, green, peach, yellow or dark backgrounds'),
         ('Syllable breaker', 'ChiShona: a syllable ends after each vowel, ma·ngwa·na·ni. English rules too'),
         ('Listen and follow', 'Reads aloud and highlights each sentence; tap a word to hear it'),
         ('Dual language', 'Every screen in ChiShona and English, with automatic text-language detection')]
for i, (h_, b_) in enumerate(feats):
    els += icon_row(6.35, 1.6 + i * 1.06, 6.4, i + 1, h_, b_, hsize=17, bsize=13)
slide(WHITE, els, """(about 50 seconds)
What makes it innovative is how it combines these tools for dyslexia and for our language.
The OpenDyslexic font has heavier bottoms on the letters, so b and d are less likely to flip. Research on this font is mixed, so the learner can also switch to a plain font.
The text has wide spacing and the learner chooses a calm background colour. Research by Zorzi and colleagues found that extra letter spacing helps children with dyslexia read.
The syllable breaker splits long words. ChiShona suits this well because almost every syllable ends in a vowel: ma-ngwa-na-ni.
The app reads aloud and highlights each sentence, and the whole app works in ChiShona and English.""")

# ================================================================== 7 How it was built
slide(WHITE, [
    title('How it was built: everything runs on the phone'),
    img(os.path.join(K, 'diagrams/diagram_arch.png'), (W - 9.7) / 2, 1.4, 9.7, 9.7 * 1161 / 2400),
    rect(0.6, 6.25, 12.1, 0.75, TINT, 0.12),
    text(0.85, 6.25, 11.6, 0.75, [[('Free, open-source tools: ', {'bold': True, 'color': GREEN}), ('HTML, CSS and JavaScript (installable web app)  ·  Tesseract.js OCR  ·  OpenDyslexic font  ·  phone text-to-speech  ·  Python tests', {})]], size=15, color=INK, anchor='m'),
], """(about 40 seconds)
I built the app with free tools: HTML, CSS and JavaScript.
It is an installable web app, a Progressive Web App. Every part runs inside the phone: the image cleaning, the Tesseract text-recognition engine, the dyslexia reader and the read-aloud.
A service worker stores the whole app on the phone, about 11 megabytes, so after the first visit it works offline. It is installed from a free web link with "Add to Home screen", so it does not need the Google Play Store. An APK file can also be made and shared on WhatsApp.""")

# ================================================================== 8 Results
slide(WHITE, [
    title('Testing exposed a flaw, and version 2 fixed it'),
    chart('acc', 0.5, 1.4, 8.1, 5.6),
    stat(9.0, 1.55, 3.75, f'{RAW:.1f}%', 'Raw photo, no clean-up', vcolor='6E6E68', h=1.6),
    stat(9.0, 3.35, 3.75, f'{V1:.1f}%', 'Prototype v1: strong contrast step', vcolor='C2410C', h=1.6),
    stat(9.0, 5.15, 3.75, f'{V2:.1f}%', 'Prototype v2: glare flattening', vcolor=BLUE, h=1.6),
], f"""(about 1 minute)
To test it, I made 14 board photos, one English and one ChiShona board under seven classroom conditions: a good photo, an angle, camera shake, a dim room, window glare, the back of the class and a dusty board. The test ran automatically and counted how many words came out correctly.
The first version surprised me. It scored only {V1:.0f} percent on average, worse than doing nothing ({RAW:.0f} percent). Its strong contrast step destroyed blurred and dusty writing: blur fell to {V1c[2]:.0f} percent and dust to {V1c[6]:.0f} percent.
So I redesigned it. Version 2 scored {V2:.1f} percent, and window glare went from {RAWc[4]:.0f} to {V2c[4]:.0f} percent. This supports my hypothesis, but only for the improved design.""")

# ================================================================== 9 Why v2 works / discussion
slide(WHITE, [
    title('Why version 2 works, and what still limits it'),
    img(os.path.join(K, 'diagrams/diagram_pipeline.png'), 0.6, 1.4, 12.1, 12.1 * 746 / 2400),
] + [
    [rect(0.6 + i * 4.15, 5.3, 3.9, 1.65, TINT, 0.12), text(0.8 + i * 4.15, 5.4, 3.5, 0.4, h_, size=16, bold=True, color=c_),
     text(0.8 + i * 4.15, 5.82, 3.55, 1.1, b_, size=13, color=INK2, spacing=1.15)]
    for i, (h_, b_, c_) in enumerate([
        ('v1 problem', 'Stretching contrast turned faint, blurred letter edges into noise.', 'C2410C'),
        ('v2 fix', 'Estimate the uneven background (glare, dust) and subtract it, keeping the letters.', BLUE),
        ('Limits', 'Simulated photos; joined handwriting is harder; few phones have a Shona voice.', GREEN)])
], """(about 45 seconds)
This shows a real run of the app on the glare photo. When the chalk is inverted, the glare becomes a dark cloud. Version 2 estimates that uneven background and removes it, and the letters come out clean.
The lesson for me was that more processing is not always better, and that a design must be tested under poor conditions, not only good ones.
There are limits. My photos were simulated, and real joined handwriting will be harder. The engine misread "take" as "fake", so the learner can correct words on the Fix text screen. Most phones also lack a ChiShona voice, so the app uses the closest available voice.""")

# ================================================================== 10 Demo
els = [title('Demo: from board to reading in seconds')]
vh = 5.55; vw = vh * 780 / 1688
els += [rect(0.95 - 0.07, 1.45 - 0.07, vw + 0.14, vh + 0.14, '222222', 0.12),
        video(os.path.join(K, 'evidence/video/kuverenga_lens_demo.mp4'), os.path.join(HERE, 'video_poster.png'), 0.95, 1.45, vw, vh)]
els += [text(4.0, 1.5, 8.7, 0.45, 'Watch for', size=20, bold=True, color=GREEN)]
watch = [('Glare removed', 'the contrast slider flattens the bright patch'), ('Read-aloud', 'each sentence is highlighted as it is read'),
         ('Syllables and colours', 'chosen by the learner'), ('ChiShona', 'the whole app switches language')]
for i, (h_, b_) in enumerate(watch):
    els += badge(4.0, 2.1 + i * 0.78, i + 1, d=0.46) + [text(4.65, 2.13 + i * 0.78, 8.0, 0.45, [[(h_ + ': ', {'bold': True, 'color': INK}), (b_, {})]], size=15, color=INK2)]
els += [rect(4.0, 5.35, 8.7, 1.6, GREEN, 0.12),
        text(4.3, 5.45, 8.2, 0.45, 'Install with no Play Store', size=17, bold=True, color=SUN),
        text(4.3, 5.92, 8.2, 0.95, 'Open the link → tap "Add to Home screen" → the app works offline. An APK file can also be shared by WhatsApp.', size=15, color=CHALK)]
slide(WHITE, els, """(about 1 minute; the video is 48 seconds; click it to play)
Let me show you the app working.
[Play the video.] Here the learner photographs a board with glare. Moving the slider flattens the glare. Convert to text, and the notes appear in the dyslexia-friendly reader. The app reads each sentence aloud and highlights it. Syllables and background colours are chosen by the learner. And the whole app switches to ChiShona.
To install it, there is no Play Store: open the link, tap "Add to Home screen", and it works offline.""")

# ================================================================== 11 Cost & enterprise
slide(WHITE, [
    title('$135 to build. Free for learners.'),
    chart('cost', 0.5, 1.4, 7.0, 4.3),
    text(0.6, 5.85, 6.9, 1.0, 'Estimated prototype costs. The software tools and hosting are free and open source.', size=13, color=INK2),
    rect(7.9, 1.55, 4.85, 3.35, GREEN, 0.15),
    text(8.2, 1.75, 4.3, 0.45, 'Social enterprise model', size=19, bold=True, color=SUN),
    text(8.2, 2.25, 4.3, 2.55, [[('Free', {'bold': True, 'color': WHITE}), (' for learners and parents', {})],
                                 [('$30 a year', {'bold': True, 'color': WHITE}), (' per school for training, guides and support', {})],
                                 [('Grants', {'bold': True, 'color': WHITE}), (' from education NGOs and innovation competitions', {})]], size=15, color='DCE9E1', spacing=1.3),
    stat(7.9, 5.15, 2.3, '≈13', 'schools to break even', h=1.75, vsize=36),
    stat(10.45, 5.15, 2.3, '$0', 'cost per extra learner', h=1.75, vsize=36),
], """(about 45 seconds)
The prototype cost about 135 US dollars, mainly for a second-hand test phone, data, printing and a teacher demonstration. The tools and hosting are free.
Because copying an app costs almost nothing, Kuverenga Lens will be free for learners. It is a social enterprise: schools can pay 30 dollars a year for teacher training, printed guides and support, and I will seek grants from NGOs. At those estimates it breaks even at about 13 schools.
Marketing will be through demonstrations at staff and SDC meetings, teacher WhatsApp groups and the innovation expo. The pilot will be at [school name].""")

# ================================================================== 12 Significance
lv = [('Myself', 'Research, design, coding, testing and enterprise skills; I am more aware of learners with dyslexia as a teacher.'),
      ('Learners', 'Read and hear board notes at their own pace, in their own language, and keep notes for revision.'),
      ('Community', 'Free and offline, so it reaches families with little money for data; raises awareness of dyslexia.'),
      ('Zimbabwe', 'Supports inclusive education and ChiShona in technology; can extend to other national languages.'),
      ('Global village', 'Contributes to SDG 4 and SDG 10; works in any chalkboard classroom.')]
els = [title('Significance: from me to the global village')]
for i, (h_, b_) in enumerate(lv):
    x = 0.6 + i * 2.46
    els += [rect(x, 1.6, 2.3, 4.6, TINT if i % 2 == 0 else 'F7F3E6', 0.15)] + badge(x + 0.25, 1.85, i + 1, d=0.6) + [
        text(x + 0.25, 2.65, 1.9, 0.75, h_, size=18, bold=True, color=GREEN),
        text(x + 0.25, 3.4, 1.85, 2.7, b_, size=14, color=INK2, spacing=1.2)]
els += [text(0.6, 6.4, 12.1, 0.5, [[('Where: ', {'bold': True, 'color': GREEN}), ('pilot at ', {}), ('[School name, District, Province]', PH), (', then nearby schools.', {})]], size=15, color=INK2)]
slide(WHITE, els, """(about 40 seconds)
The innovation matters at every level.
For me, I learnt research, design, coding, testing and costing, and I am more aware of dyslexia as a future teacher.
For learners, they can read and hear notes at their own pace, in their own language.
For the community, it is free and offline, so it reaches families with little data, and it raises awareness that dyslexia is not laziness.
For Zimbabwe, it supports inclusive education and puts ChiShona into technology.
For the global village, it contributes to Sustainable Development Goal 4, inclusive and quality education for all, and it works in any chalkboard classroom.""")

# ================================================================== 13 Conclusion
slide(GREEN, [
    text(0.6, 0.42, 12.1, 0.85, 'Conclusion and next steps', size=34, color=CHALK, bold=True),
    text(0.6, 1.55, 6.6, 0.45, 'What this project showed', size=19, bold=True, color=SUN),
    text(0.6, 2.05, 6.6, 3.6, [
        'A free, offline, bilingual phone app can turn chalkboard notes into dyslexia-friendly text that learners can read and hear.',
        f'Testing mattered: v1 failed in poor conditions; v2 reached {V2:.1f}% word accuracy and solved window glare.',
        'No Play Store is needed: install from a link or share the APK.'], size=16, color='DCE9E1', spacing=1.25),
    text(7.6, 1.55, 5.1, 0.45, 'Next steps', size=19, bold=True, color=SUN),
    text(7.6, 2.05, 5.1, 2.6, ['Classroom trial with learners and real board photos', 'Train the OCR on Zimbabwean handwriting', 'Record a natural ChiShona voice', 'Offer the school plan to nearby schools'], size=16, color='DCE9E1', spacing=1.25),
    rect(7.6, 4.85, 1.8, 1.8, WHITE, 0.1),
    text(7.6, 4.85, 1.8, 1.8, [[('[QR code]', PH)]], size=13, color=INK, align='c', anchor='m'),
    text(9.65, 4.95, 3.1, 1.6, [[('Scan to try it', {'bold': True, 'color': CHALK})], [('[app link]', PH)]], size=15, color='DCE9E1', spacing=1.3),
    text(0.6, 6.15, 6.6, 0.8, [[('Thank you  ·  Mazvita', {})]], size=30, color=SUN, bold=True),
], """(about 30 seconds)
To conclude: a free, offline, bilingual phone app can turn chalkboard notes into text that learners with dyslexia can read and hear. Testing was essential. My first design failed in poor conditions, and the improved version reached about 99 percent word accuracy on my test photos.
My next steps are a classroom trial with real learners and boards, training the text recognition on Zimbabwean handwriting, a natural ChiShona voice, and offering the school plan to nearby schools.
Thank you. Mazvita. I welcome your questions.""")

# ================================================================== PPTX writer
def rgb(h): return RGBColor.from_string(h)

def set_run(run, txt, size, color, bold, opts, font):
    run.text = txt
    f = run.font; f.size = Pt(opts.get('size', size)); f.bold = opts.get('bold', bold); f.name = font
    f.italic = opts.get('italic', False); f.color.rgb = rgb(opts.get('color', color))
    if opts.get('hl'):
        # schema order inside a:rPr is ln, fill, effect, highlight, ... latin: place highlight right after the fill
        rPr = run._r.get_or_add_rPr()
        hl = etree.Element(qn('a:highlight')); c = etree.SubElement(hl, qn('a:srgbClr')); c.set('val', 'FFF200')
        rPr.find(qn('a:solidFill')).addnext(hl)

def build_pptx(path):
    prs = Presentation(); prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    blank = prs.slide_layouts[6]
    for n, s in enumerate(SLIDES, 1):
        sl = prs.slides.add_slide(blank)
        sl.background.fill.solid(); sl.background.fill.fore_color.rgb = rgb(s['bg'])
        for i, e in enumerate(s['el']):
            x, y, w, h = Inches(e['x']), Inches(e['y']), Inches(e['w']), Inches(e['h'])
            if e['k'] in ('rect', 'oval'):
                shp = sl.shapes.add_shape(MSO_SHAPE.OVAL if e['k'] == 'oval' else (MSO_SHAPE.ROUNDED_RECTANGLE if e.get('r') else MSO_SHAPE.RECTANGLE), x, y, w, h)
                if e['k'] == 'rect' and e.get('r'): shp.adjustments[0] = min(0.5, e['r'] / min(e['w'], e['h']))
                shp.fill.solid(); shp.fill.fore_color.rgb = rgb(e['fill'])
                if e.get('line'):
                    shp.line.color.rgb = rgb(e['line']); shp.line.width = Pt(1.5)
                    if e.get('dash'):
                        from pptx.enum.dml import MSO_LINE_DASH_STYLE; shp.line.dash_style = MSO_LINE_DASH_STYLE.DASH
                else: shp.line.fill.background()
                shp.shadow.inherit = False
                shp.name = f'{e["k"]}-{n}-{i}'
            elif e['k'] == 'img':
                pic = sl.shapes.add_picture(e['path'], x, y, w, h); pic.name = f'image-{n}-{i}'
            elif e['k'] == 'video':
                mv = sl.shapes.add_movie(e['path'], x, y, w, h, poster_frame_image=e['poster'], mime_type='video/mp4'); mv.name = 'Demo video'
            elif e['k'] == 'text':
                tb = sl.shapes.add_textbox(x, y, w, h); tb.name = f'text-{n}-{i}'
                tf = tb.text_frame; tf.word_wrap = True
                tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
                tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[e['anchor']]
                for pi, para in enumerate(e['paras']):
                    p = tf.paragraphs[0] if pi == 0 else tf.add_paragraph()
                    p.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}[e['align']]
                    p.line_spacing = e['spacing']
                    if pi: p.space_before = Pt(e['size'] * 0.45)
                    runs_ = [(para, {})] if isinstance(para, str) else para
                    for t_, o_ in runs_: set_run(p.add_run(), t_, e['size'], e['color'], e['bold'], o_, e['font'])
            elif e['k'] == 'chart':
                add_chart(sl, e, x, y, w, h)
        sl.notes_slide.notes_text_frame.text = s['notes']
    prs.save(path)

def style_axis_text(ax, size=11, color=INK2):
    ax.tick_labels.font.size = Pt(size); ax.tick_labels.font.color.rgb = rgb(color); ax.tick_labels.font.name = FONT

def add_chart(sl, e, x, y, w, h):
    if e['kind'] == 'acc':
        cd = CategoryChartData(); cats = [n for _, n in COND][::-1]; cd.categories = cats
        cd.add_series('Raw photo', [round(v, 1) for v in RAWc[::-1]])
        cd.add_series('Prototype v1', [round(v, 1) for v in V1c[::-1]])
        cd.add_series('Prototype v2', [round(v, 1) for v in V2c[::-1]])
        ch = sl.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, x, y, w, h, cd).chart
        colors = [GREY, ORANGE, BLUE]
        ch.has_title = True; ch.chart_title.text_frame.text = 'Word accuracy by classroom condition (%)'
        tp = ch.chart_title.text_frame.paragraphs[0]; tp.runs[0].font.size = Pt(15); tp.runs[0].font.bold = True; tp.runs[0].font.color.rgb = rgb(INK); tp.runs[0].font.name = FONT
        ch.has_legend = True; ch.legend.position = XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(12); ch.legend.font.color.rgb = rgb(INK2); ch.legend.font.name = FONT
        plot = ch.plots[0]; plot.gap_width = 55; plot.overlap = -8
        for s_, c_ in zip(plot.series, colors):
            s_.format.fill.solid(); s_.format.fill.fore_color.rgb = rgb(c_); s_.invert_if_negative = False
        s2 = plot.series[2]; s2.data_labels.show_value = True; s2.data_labels.number_format = '0"%"'; s2.data_labels.number_format_is_linked = False
        s2.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END; s2.data_labels.font.size = Pt(10); s2.data_labels.font.bold = True; s2.data_labels.font.color.rgb = rgb(INK)
        va = ch.value_axis; va.maximum_scale = 110; va.minimum_scale = 0; va.major_unit = 25; va.has_major_gridlines = True
        va.major_gridlines.format.line.color.rgb = rgb('E6E3DA'); va.format.line.fill.background(); va.tick_labels.number_format = '0"%"'; va.tick_labels.number_format_is_linked = False
        style_axis_text(va, 11); style_axis_text(ch.category_axis, 12, INK); ch.category_axis.format.line.color.rgb = rgb('CFCFCF')
    else:
        items = [('Second-hand test phone', 60), ('Teacher demonstration', 30), ('Printing', 25), ('Internet data', 20), ('Hosting (GitHub Pages)', 0), ('OCR, font, tools', 0)][::-1]
        cd = CategoryChartData(); cd.categories = [a for a, _ in items]; cd.add_series('US$', [b for _, b in items])
        ch = sl.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, x, y, w, h, cd).chart
        ch.has_title = True; ch.chart_title.text_frame.text = 'Estimated prototype cost (US$)'
        tp = ch.chart_title.text_frame.paragraphs[0]; tp.runs[0].font.size = Pt(15); tp.runs[0].font.bold = True; tp.runs[0].font.color.rgb = rgb(INK); tp.runs[0].font.name = FONT
        ch.has_legend = False
        plot = ch.plots[0]; plot.gap_width = 60
        s_ = plot.series[0]; s_.format.fill.solid(); s_.format.fill.fore_color.rgb = rgb(GREEN); s_.invert_if_negative = False
        s_.data_labels.show_value = True; s_.data_labels.number_format = '"$"0'; s_.data_labels.number_format_is_linked = False
        s_.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END; s_.data_labels.font.size = Pt(11); s_.data_labels.font.bold = True; s_.data_labels.font.color.rgb = rgb(INK)
        va = ch.value_axis; va.maximum_scale = 70; va.minimum_scale = 0; va.major_unit = 10; va.has_major_gridlines = True
        va.major_gridlines.format.line.color.rgb = rgb('E6E3DA'); va.format.line.fill.background(); va.visible = False
        style_axis_text(ch.category_axis, 12, INK); ch.category_axis.format.line.color.rgb = rgb('CFCFCF')

# ================================================================== HTML preview (same geometry, Arial-metric font)
def build_preview(path, font_dir):
    PX = 96
    out = ['<!doctype html><html><head><meta charset="utf-8"><style>',
           f'@font-face{{font-family:"Arial";src:url("file://{font_dir}/LiberationSans-Regular.ttf")}}',
           f'@font-face{{font-family:"Arial";font-weight:700;src:url("file://{font_dir}/LiberationSans-Bold.ttf")}}',
           'body{margin:0;background:#888}.s{position:relative;width:%dpx;height:%dpx;overflow:hidden;margin:0 0 20px}' % (W * PX, H * PX),
           '.e{position:absolute;box-sizing:border-box}.t{display:flex;flex-direction:column;overflow:visible;font-family:Arial}',
           '.t p{margin:0}.hl{background:#FFF200}.chart{background:#fff;border:2px dashed #2a78d6}</style></head><body>']
    for n, s in enumerate(SLIDES, 1):
        out.append(f'<div class="s" id="s{n}" style="background:#{s["bg"]}">')
        for e in s['el']:
            pos = f'left:{e["x"]*PX}px;top:{e["y"]*PX}px;width:{e["w"]*PX}px;height:{e["h"]*PX}px'
            if e['k'] == 'rect':
                br = f'border-radius:{e["r"]*PX}px;' if e.get('r') else ''
                bd = f'border:2px {"dashed" if e.get("dash") else "solid"} #{e["line"]};' if e.get('line') else ''
                out.append(f'<div class="e" style="{pos};background:#{e["fill"]};{br}{bd}"></div>')
            elif e['k'] == 'oval':
                out.append(f'<div class="e" style="{pos};background:#{e["fill"]};border-radius:50%"></div>')
            elif e['k'] in ('img', 'video'):
                src = e['poster'] if e['k'] == 'video' else e['path']
                out.append(f'<img class="e" src="file://{src}" style="{pos};object-fit:fill">')
            elif e['k'] == 'chart':
                pic = os.path.join(K, 'charts', 'fig_accuracy_by_condition.png' if e['kind'] == 'acc' else 'fig_costs.png')
                out.append(f'<div class="e chart" style="{pos}"><img src="file://{pic}" style="width:100%;height:100%;object-fit:contain"></div>')
            elif e['k'] == 'text':
                jc = {'t': 'flex-start', 'm': 'center', 'b': 'flex-end'}[e['anchor']]
                ta = {'l': 'left', 'c': 'center', 'r': 'right'}[e['align']]
                ps = []
                for pi, para in enumerate(e['paras']):
                    runs_ = [(para, {})] if isinstance(para, str) else para
                    inner = ''.join(f'<span class="{"hl" if o.get("hl") else ""}" style="color:#{o.get("color", e["color"])};font-weight:{700 if o.get("bold", e["bold"]) else 400};font-size:{o.get("size", e["size"])}pt">{html.escape(t)}</span>' for t, o in runs_)
                    mt = f'margin-top:{e["size"]*0.45}pt;' if pi else ''
                    ps.append(f'<p style="{mt}line-height:{1.2*e["spacing"]};text-align:{ta}">{inner}</p>')
                out.append(f'<div class="e t" data-text="1" style="{pos};justify-content:{jc}">{"".join(ps)}</div>')
        out.append('</div>')
    out.append('</body></html>')
    open(path, 'w').write('\n'.join(out))

if __name__ == '__main__':
    import sys
    out = os.path.join(HERE, 'Kuverenga_Lens_Presentation.pptx')
    build_pptx(out); print('saved', out, '|', len(SLIDES), 'slides')
    if len(sys.argv) > 1:
        build_preview(os.path.join(sys.argv[1], 'preview.html'), sys.argv[2]); print('preview written')
