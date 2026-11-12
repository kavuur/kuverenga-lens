"""Builds the RISED 301 scientific report for Kuverenga Lens as a Word document.
Yellow-highlighted [square-bracket] text is for the student to complete.
Run: python build_report.py   (needs python-docx)"""
import csv, os
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'Kuverenga_Lens_RISED301_Report.docx')
GREEN = RGBColor(0x1F, 0x4D, 0x3A)

doc = Document()
sec = doc.sections[0]
sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
for side in ('left_margin', 'right_margin'): setattr(sec, side, Cm(2.5))
sec.top_margin = sec.bottom_margin = Cm(2.3)

# ---------- styles ----------
st = doc.styles['Normal']
st.font.name = 'Times New Roman'; st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
st.paragraph_format.line_spacing = 1.5
st.paragraph_format.space_after = Pt(6)
for name, size, before, after in (('Title', 26, 0, 6), ('Heading 1', 16, 18, 8), ('Heading 2', 13, 12, 4), ('Heading 3', 12, 10, 2)):
    s = doc.styles[name]
    s.font.name = 'Arial'; s.font.size = Pt(size); s.font.bold = True; s.font.color.rgb = GREEN
    rpr = s.element.get_or_add_rPr(); rf = rpr.find(qn('w:rFonts'))
    if rf is None: rf = OxmlElement('w:rFonts'); rpr.append(rf)
    for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'): rf.set(qn(a), 'Arial')
    s.paragraph_format.space_before = Pt(before); s.paragraph_format.space_after = Pt(after)
    s.paragraph_format.keep_with_next = True; s.paragraph_format.line_spacing = 1.15
cap = doc.styles['Caption']
cap.font.name = 'Arial'; cap.font.size = Pt(9.5); cap.font.italic = False; cap.font.bold = False
cap.font.color.rgb = RGBColor(0x33, 0x33, 0x33); cap.paragraph_format.space_after = Pt(10)

# ask Word to refresh the table of contents and figure lists when the file is opened
upd = OxmlElement('w:updateFields'); upd.set(qn('w:val'), 'true'); doc.settings.element.append(upd)

# ---------- helpers ----------
def runs(p, text):
    """Plain text with **bold** and [placeholder] (yellow highlight) support."""
    import re
    for part in re.split(r'(\*\*[^*]+\*\*|\[[^\]]+\])', text):
        if not part: continue
        if part.startswith('**'):
            r = p.add_run(part[2:-2]); r.bold = True
        elif part.startswith('[') and not part.startswith('[http'):
            r = p.add_run(part); r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        else:
            p.add_run(part)
    return p

def P(text, align=None, italic=False, size=None, after=None):
    p = doc.add_paragraph()
    runs(p, text)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if align is None else align
    if italic or size:
        for r in p.runs:
            if italic: r.italic = True
            if size: r.font.size = Pt(size)
    if after is not None: p.paragraph_format.space_after = Pt(after)
    return p

def H(text, level=1):
    return doc.add_heading(text, level)

def bullets(items, style='List Bullet'):
    for it in items:
        p = doc.add_paragraph(style=style); runs(p, it)
        p.paragraph_format.space_after = Pt(2)

def field(p, instr, placeholder=''):
    r = p.add_run(); fc = OxmlElement('w:fldChar'); fc.set(qn('w:fldCharType'), 'begin'); r._r.append(fc)
    r = p.add_run(); it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = instr; r._r.append(it)
    r = p.add_run(); fc = OxmlElement('w:fldChar'); fc.set(qn('w:fldCharType'), 'separate'); r._r.append(fc)
    p.add_run(placeholder)
    r = p.add_run(); fc = OxmlElement('w:fldChar'); fc.set(qn('w:fldCharType'), 'end'); r._r.append(fc)

counters = {'Figure': 0, 'Table': 0}
def caption(kind, text):
    counters[kind] += 1
    p = doc.add_paragraph(style='Caption')
    r = p.add_run(f'{kind} '); r.bold = True
    r_start = len(p.runs)
    field(p, f' SEQ {kind} \\* ARABIC ', str(counters[kind]))
    for r in p.runs[r_start:]: r.bold = True
    r = p.add_run(': '); r.bold = True
    p.add_run(text)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if kind == 'Figure' else WD_ALIGN_PARAGRAPH.LEFT
    if kind == 'Table': p.paragraph_format.keep_with_next = True
    return counters[kind]

def fig(path, text, width=15.5):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True; p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(os.path.join(K, path), width=Cm(width))
    return caption('Figure', text)

def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement('w:shd')
    sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), hex_fill); tcPr.append(sh)

def table(header, rows, widths, title=None, size=10):
    if title: caption('Table', title)
    t = doc.add_table(rows=1, cols=len(header)); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ''
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(size); r.font.color.rgb = RGBColor(255, 255, 255)
        shade(c, '1F4D3A')
    for k, row in enumerate(rows):
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ''
            para = cells[i].paragraphs[0]; runs(para, str(v))
            for r in para.runs: r.font.size = Pt(size)
            para.paragraph_format.line_spacing = 1.0; para.paragraph_format.space_after = Pt(0)
            if k % 2: shade(cells[i], 'F3F1EA')
    for row in t.rows:
        for i, w in enumerate(widths): row.cells[i].width = Cm(w)
        row.cells[0].paragraphs[0].paragraph_format.line_spacing = 1.0
    hdr = t.rows[0]._tr.get_or_add_trPr(); th = OxmlElement('w:tblHeader'); th.set(qn('w:val'), 'true'); hdr.append(th)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

def page_numbers(section):
    p = section.footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    field(p, ' PAGE ', '1')

# ---------- data ----------
def load(name):
    with open(os.path.join(K, 'testing', name)) as f: return list(csv.DictReader(f))
v1, v2 = load('accuracy_results_v1.csv'), load('accuracy_results_v2.csv')
COND = [('1_good', 'Good photo, straight on'), ('2_angle', 'Taken at an angle'), ('3_shake', 'Camera shake (blur)'),
        ('4_dim', 'Dim classroom'), ('5_glare', 'Window glare'), ('6_far', 'From the back of the class'), ('7_dusty', 'Dusty, poorly wiped board')]
def acc(rows, cond, pipe, lang=None):
    v = [float(r['word_accuracy_pct']) for r in rows if r['condition'] == cond and r['pipeline'] == pipe and (lang is None or r['language'] == lang)]
    return sum(v) / len(v)
def overall(rows, pipe): return sum(acc(rows, c, pipe) for c, _ in COND) / len(COND)
RAW, V1, V2 = overall(v2, 'raw photo'), overall(v1, 'with clean-up'), overall(v2, 'with clean-up')

# =====================================================================
# COVER
# =====================================================================
for _ in range(2): doc.add_paragraph()
for line, size, bold in (('UNIVERSITY OF ZIMBABWE', 16, True), ('FACULTY OF EDUCATION', 13, True),
                         ('Bachelor of Education (Honours)', 12, False),
                         ('RISED 301: Research & Innovation Skills', 12, True), ('Block 1 · Semester 2.1 · Innovation Project', 12, False)):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(line); r.bold = bold; r.font.size = Pt(size); p.paragraph_format.space_after = Pt(2)
doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(os.path.join(K, 'app/icons/logo-1024.png'), width=Cm(4.2))
p = doc.add_paragraph(style='Title'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run('Kuverenga Lens')
P('A phone application that turns the chalkboard into a personal, dyslexia-friendly reader in ChiShona and English', align=WD_ALIGN_PARAGRAPH.CENTER, italic=True, size=13)
doc.add_paragraph()
for label, val in (('Student name', '[Your full name]'), ('Registration number', '[R000000X]'), ('Programme', '[B.Ed (Hons) programme / subject area]'),
                   ('Lecturer', '[Lecturer name]'), ('Submission date', '13 November 2026')):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(0)
    r = p.add_run(label + ': '); r.bold = True; runs(p, val)
page_break()

# =====================================================================
# FRONT MATTER
# =====================================================================
H('Declaration', 1)
P('I, [Your full name], declare that this innovation project and report are my own work. All sources used have been acknowledged and referenced. This work has not been submitted for any other course or qualification.')
P('Signature: [__________]          Date: [__________]', align=WD_ALIGN_PARAGRAPH.LEFT)

H('Acknowledgements', 1)
P('I thank the following people and organisations for their help with this project:')
bullets([
    '[Lecturer name], RISED 301 lecturer, University of Zimbabwe, for guidance on research and innovation methods.',
    '[Head of school], [School name], for permission to carry out the needs assessment and the classroom trial.',
    '[Teacher name(s)], for completing the teacher questionnaire and letting me observe chalkboard lessons.',
    'The learners who answered the questionnaire and tested the app (names withheld), and their parents or guardians who gave consent.',
    '[Name of anyone who checked the ChiShona wording in the app], for checking the Shona translations.',
    'The open-source community: the Tesseract.js OCR engine (Apache 2.0 licence) and the OpenDyslexic font by Abbie Gonzalez (SIL Open Font Licence) are used in the app.',
])

H('Abstract', 1)
P('Learners with dyslexia in Zimbabwean classrooms are expected to read and copy notes from a chalkboard, often before the board is wiped. Chalk on a green board, small handwriting, glare and the pressure of time make this especially hard for them, and specialist assistive technology is expensive and rarely available. This project designed, built and tested **Kuverenga Lens** ("kuverenga" means "to read" in ChiShona). It is a free phone application that lets a learner photograph the board, converts the photo into clean digital text on the phone itself, and then displays that text in a dyslexia-friendly format (OpenDyslexic font, wide letter and line spacing, a choice of background colours and a syllable breaker) while reading it aloud. The app works in both ChiShona and English. It was built as an installable Progressive Web App, so it runs on ordinary Android phones and iPhones without the Google Play Store and works offline after the first download. An engineering design cycle was followed: needs assessment, design brief, prototype, testing and improvement. Fourteen simulated chalkboard photos covering seven classroom conditions were used to test text recognition. The first prototype scored an average word accuracy of '
  f'{V1:.1f}%, lower than sending the raw photo directly to the OCR engine ({RAW:.1f}%), because its contrast step damaged blurred and dusty writing. The second prototype replaced this step with background flattening and raised the average to {V2:.1f}%, with window glare improving from {acc(v2, "5_glare", "raw photo"):.0f}% to {acc(v2, "5_glare", "with clean-up"):.0f}%. The prototype cost an estimated US$135 to develop. It is free for learners, and schools can be offered a low-cost training and support plan. Further testing with real classroom photos and with learners is recommended.')
P('**Keywords:** dyslexia, assistive technology, optical character recognition, inclusive education, ChiShona, progressive web app, innovation')
page_break()

H('Table of Contents', 1)
p = doc.add_paragraph(); field(p, ' TOC \\o "1-2" \\h \\z \\u ', 'Right-click here and choose "Update Field" to show the table of contents.')
H('List of Figures', 2)
p = doc.add_paragraph(); field(p, ' TOC \\h \\z \\c "Figure" ', 'Right-click here and choose "Update Field".')
H('List of Tables', 2)
p = doc.add_paragraph(); field(p, ' TOC \\h \\z \\c "Table" ', 'Right-click here and choose "Update Field".')
page_break()

# =====================================================================
# 1 INTRODUCTION
# =====================================================================
H('1. Introduction', 1)
H('1.1 Background to the problem', 2)
P('In most Zimbabwean primary and secondary schools the chalkboard is still the main way that teachers share notes, sums, spellings and homework. Learners are expected to read what is written, often from several metres away, and to copy it into exercise books before the teacher wipes the board for the next part of the lesson. For most learners this is routine. For learners with dyslexia it is a daily barrier.')
P('Dyslexia is a specific learning difficulty that mainly affects accurate and fluent word reading and spelling (International Dyslexia Association, 2002; Lyon et al., 2003). It is not linked to intelligence. A learner with dyslexia may understand a topic well when it is explained aloud but still struggle to decode the written words, confuse letters such as b and d, lose their place between the board and the book, and copy slowly. The International Dyslexia Association estimates that as many as 15–20% of people show some symptoms of dyslexia (IDA, n.d.), so a typical class of 40 or more learners is likely to include several affected children, many of them never formally assessed.')
P('The physical setting makes the difficulty worse. Chalk on a green or black board gives limited contrast, glare from windows washes out parts of the board, old chalk dust leaves a grey haze, and learners at the back see small letters. Copying from the board also places a heavy load on working memory, because the learner must hold letters or words in mind while looking down to write. Specialist assistive technology such as reading pens, scanning software or tablets with paid apps is expensive and rarely available in public schools. However, many families now have access to at least one smartphone. This gap between a common classroom problem and a widely owned device is the starting point for this innovation.')

H('1.2 Statement of the problem', 2)
P('Learners with dyslexia and other reading difficulties cannot read and copy chalkboard notes accurately and quickly enough, and there is no affordable tool that turns those notes into an accessible format they can read and listen to in their own language. As a result they fall behind, miss content and lose confidence.')

H('1.3 Aim', 2)
P('To design, build and test a low-cost phone application that converts chalkboard notes into dyslexia-friendly text that can be read on screen and heard aloud, in both ChiShona and English.')

H('1.4 Objectives', 2)
bullets([
    'To carry out a needs assessment of the difficulties that learners with reading difficulties face when reading from the chalkboard.',
    'To write a design brief and product specifications for a suitable solution.',
    'To build a working prototype that runs on ordinary Android phones and iPhones without the Google Play Store and works offline.',
    'To measure how accurately the prototype converts chalkboard photos into text under common classroom conditions, and to improve it based on the results.',
    'To estimate the costs and propose a marketing and entrepreneurship plan for putting the innovation into schools.',
], style='List Number')

H('1.5 Research questions and hypothesis', 2)
bullets([
    'What difficulties do learners with reading difficulties experience when reading and copying from the chalkboard?',
    'Can a phone convert photographs of chalkboard writing into text accurately enough to be useful?',
    'Which image-processing steps improve recognition under poor conditions such as glare, blur and dust?',
    'Do learners find the dyslexia-friendly display and read-aloud helpful?',
])
P('**Hypothesis:** cleaning a chalkboard photo before text recognition (inverting the light-on-dark writing and removing uneven lighting) will give higher word accuracy than recognising the raw photo, especially in poor lighting.')

H('1.6 Scope and where the innovation will be implemented', 2)
P('The prototype will first be implemented at [School name], [Town/District], [Province], Zimbabwe, in [Grade/Form level] classes, where the needs assessment was carried out. It is designed for any classroom that uses a chalkboard or whiteboard. The first version covers printed and neat handwritten notes in English and ChiShona. Joined (cursive) handwriting, mathematical symbols and diagrams are outside the scope of this version.')

H('1.7 Definition of key terms', 2)
table(['Term', 'Meaning in this report'], [
    ['Dyslexia', 'A specific learning difficulty that mainly affects accurate and fluent word reading and spelling, not related to intelligence (IDA, 2002).'],
    ['Assistive technology', 'Any tool or device that helps a person with a disability or difficulty carry out a task they would otherwise find hard.'],
    ['Optical character recognition (OCR)', 'Software that finds letters and words in an image and turns them into editable digital text (Smith, 2007).'],
    ['Text-to-speech (TTS)', 'Software that reads digital text aloud with a synthetic voice.'],
    ['Progressive Web App (PWA)', 'A website that can be installed on a phone like an app, opens full-screen and keeps working offline.'],
    ['OpenDyslexic', 'A free typeface with heavier letter bottoms, designed to reduce letter rotation and confusion.'],
    ['Syllable', 'A unit of a word built around a vowel sound, e.g. ma-ngwa-na-ni.'],
    ['Word accuracy', 'The percentage of words on the board that the app reproduced correctly.'],
], [4.5, 11.5], 'Key terms used in this report')

# =====================================================================
# 2 LITERATURE REVIEW
# =====================================================================
H('2. Literature Review', 1)
H('2.1 Research', 2)
P('Research is a systematic process of collecting and analysing information to answer a question or solve a problem (Creswell & Creswell, 2018). It can be basic, adding to general knowledge, or applied, aimed at a practical problem. This project is applied research. It uses a needs assessment (questionnaires and observation) to understand the problem, and an experiment (controlled recognition tests) to evaluate the solution. Using both qualitative and quantitative evidence is known as a mixed-methods approach (Creswell & Creswell, 2018).')

H('2.2 Innovation', 2)
P('Schumpeter (1934) described innovation as "new combinations" of existing resources: new products, new methods of production, new markets, new sources of supply or new forms of organisation. The Oslo Manual defines an innovation as "a new or improved product or process (or combination thereof) that differs significantly from the unit\'s previous products or processes and that has been made available to potential users" (OECD/Eurostat, 2018, p. 20). Innovation therefore differs from invention: an invention is a new idea, while an innovation is an idea put into use. Drucker (1985) argues that innovation is a disciplined practice that starts from analysing needs and opportunities, including "incongruities" between what is and what ought to be. A child who understands a lesson but cannot read the board is one such incongruity.')
P('Kuverenga Lens is an incremental, combinational innovation. Phone cameras, OCR, dyslexia fonts and text-to-speech already exist separately. The new element is combining them into one free, offline, bilingual tool built around the chalkboard classroom and ChiShona.')

H('2.3 Product development, product design and the production process', 2)
P('**Product development** is the full set of activities that starts with seeing a market opportunity and ends with producing, selling and delivering a product (Ulrich & Eppinger, 2016). It usually moves through planning, concept development, system-level design, detail design, testing and refinement, and production ramp-up.')
P('**Product design** is the part of development that decides how the product will look, work and be used. It turns user needs into specifications. Design thinking (Brown, 2008) stresses empathy with users, quick prototypes and repeated testing. These ideas shaped this project: the needs assessment provides empathy, and the v1 → v2 improvement is an example of iterative testing.')
P('**Production process** means the steps and resources used to make a product. For software, the production process covers writing code, testing, packaging and distribution. Software has almost no cost per extra copy, so once the app is built it can be copied to many phones at very little cost.')
P('**Specifications** are measurable statements of what a product must do (for example, "works with no internet after the first download"). They let the designer test whether the design succeeded. The specifications for this project are given in Section 3.4.')

H('2.4 Dyslexia and reading from the board', 2)
P('Dyslexia is mainly a difficulty with phonological processing, that is, linking sounds to letters (Snowling, 2019). Common signs in class include slow and effortful reading, reversing or confusing letters, losing one\'s place, and poor spelling. Copying from a board is particularly demanding because it combines visual search, reading, short-term memory and handwriting in a timed task. Zimbabwe\'s education policies support inclusive education, and UNESCO (2020) stresses that inclusion requires adapting materials and methods so that every learner can take part. Sustainable Development Goal 4 calls for "inclusive and equitable quality education" for all (United Nations, 2015).')

H('2.5 Ways of making text easier to read', 2)
P('**Fonts.** OpenDyslexic gives letters heavier bottoms so they are less likely to appear rotated. The evidence is mixed. Rello and Baeza-Yates (2013) found that people with dyslexia read faster with sans-serif, monospaced and roman fonts, while Wery and Diliberto (2017) found that OpenDyslexic did not improve reading rate or accuracy for most pupils. For this reason, Kuverenga Lens makes OpenDyslexic the default, because many learners prefer it, but lets the learner switch to a plain sans-serif font (Verdana).')
P('**Spacing.** Zorzi et al. (2012) showed that extra-large letter spacing improved reading accuracy and speed for children with dyslexia by reducing "crowding" between letters. The British Dyslexia Association (2023) recommends generous line spacing (1.5 or more), left-aligned text and short lines. The app uses wide letter and word spacing and adjustable line spacing from 1.4 to 3.')
P('**Colour.** The British Dyslexia Association (2023) recommends off-white or pastel backgrounds instead of pure white, and allowing readers to choose. The app offers cream, blue, green, peach, yellow and dark backgrounds.')
P('**Listening.** A meta-analysis by Wood et al. (2018) found that text-to-speech and read-aloud tools have a small to moderate positive effect on reading comprehension for students with reading disabilities. Hearing the words while seeing them highlighted lets learners use their listening comprehension, which is often stronger than their decoding.')
P('**Syllables.** Breaking long words into syllables supports decoding. ChiShona is particularly suited to this, because almost all its syllables are "open", ending in a vowel (Fortune, 1955), e.g. ku-chi-ko-ro, mu-nda. A simple rule ("a syllable ends after each vowel") therefore splits Shona words accurately.')

H('2.6 Optical character recognition (OCR)', 2)
P('OCR converts images of text into digital text. Tesseract, first developed at Hewlett-Packard and later released as open source by Google, is one of the most widely used OCR engines (Smith, 2007). Its modern versions use a neural network (LSTM) to recognise whole lines of text. Tesseract.js is a version that runs inside a web browser using WebAssembly, so recognition happens on the phone without sending the image to a server. OCR works best on dark text on a light, evenly lit background, so photos of chalk on a dark board need pre-processing. Common steps are converting to greyscale, inverting, correcting uneven lighting, and thresholding to black and white, for example with the method of Otsu (1979).')

H('2.7 Installable web apps and offline use', 2)
P('A Progressive Web App (PWA) is a website that includes a "manifest" (name, icon, colours) and a "service worker" that stores the app on the device. Users can install it from the browser with "Add to Home screen". It then opens like a normal app and works offline. This avoids the cost, developer account and review process of the Google Play Store, and the app can be shared simply as a link or QR code. A PWA can also be packaged as an Android APK with free tools such as PWABuilder and shared directly.')

H('2.8 Gap in existing solutions', 2)
table(['Existing option', 'What it does', 'Limitation for Zimbabwean classrooms'], [
    ['General OCR apps (e.g. Google Lens)', 'Recognise and translate text from photos', 'Need data for many features, not designed for dyslexia, no Shona reading support or syllable breaker'],
    ['Paid dyslexia readers and reading pens', 'Scan and read printed text', 'Costly; designed for printed books, not chalkboards'],
    ['Teacher handouts', 'Teacher provides printed notes', 'Printing costs, extra teacher time, not always possible'],
    ['Peer copying / teacher assistant', 'Another learner or adult helps', 'Not always available; reduces independence'],
    ['**Kuverenga Lens (this project)**', 'Photo of board → clean text → dyslexia display + read-aloud', 'Free, offline, Shona + English, designed for chalkboards'],
], [4.2, 5.4, 6.4], 'Comparison of existing solutions with Kuverenga Lens')

# =====================================================================
# 3 METHODOLOGY
# =====================================================================
H('3. Methodology: Design and Production', 1)
H('3.1 Design approach', 2)
P('An engineering design cycle was followed (Figure 1). Research and needs assessment came first, followed by a design brief and specifications, idea generation, a first prototype, testing, improvement and retesting. Each test result was recorded so that design decisions are based on evidence. The full timeline is shown in Figure 2.')
fig('diagrams/diagram_process.png', 'Design process followed in developing Kuverenga Lens')
fig('charts/fig_timeline.png', 'Project timeline by week (planned)')

H('3.2 Needs assessment', 2)
P('**Participants and setting.** The needs assessment took place at [School name] with [number] learners from [Grade/Form] and [number] teachers. Learners were selected by [describe: e.g. teacher referral of learners who struggle with reading]. Learner codes (L1, L2 …) were used instead of names.')
P('**Instruments.** Two short questionnaires (Appendix A) were used: one for teachers and one for learners. These were combined with [number] lesson observations in which the time given for copying and the learners\' copying behaviour were noted.')
P('**Ethics.** Permission was obtained from the head of school. Parents or guardians gave consent, and learners agreed to take part. Participation was voluntary, and no photographs of learners\' faces are used without consent. All data are kept anonymous.')
P('**Analysis.** Responses were counted and converted to percentages using the spreadsheet *needs_assessment_template.xlsx*, which also draws the charts used in Section 4.1.')

H('3.3 Design brief', 2)
P('**Design brief:** Design and make a low-cost, easy-to-use phone application that allows learners with dyslexia and other reading difficulties to capture notes from the classroom chalkboard and read them in a format that suits them, both on screen and by listening. The app must work on the ordinary, low-cost phones that families already own, must not depend on the Google Play Store or a constant internet connection, must protect learners\' privacy, and must support both ChiShona and English.')
P('**Target users:** learners aged about 9–18 with dyslexia or reading difficulties (primary users); teachers and parents (secondary users).')
P('**Constraints:** very small budget; many learners share a family phone; limited mobile data; varied classroom lighting; school rules on phone use.')

H('3.4 Product specifications', 2)
table(['No.', 'Specification', 'How it is met / tested'], [
    ['S1', 'Captures the chalkboard with the phone camera or a saved photo', 'Camera button opens the rear camera; "Choose a photo" opens the gallery'],
    ['S2', 'Converts chalkboard photos to text with at least 90% word accuracy in good conditions', 'Accuracy test, Section 4.3'],
    ['S3', 'Works without the Google Play Store', 'Installable PWA; optional APK via PWABuilder'],
    ['S4', 'Works offline after the first download', 'Service worker stores the app, OCR engine and font (about 11 MB)'],
    ['S5', 'Dyslexia-friendly display: font choice, size, spacing, background colour', 'Display panel in the reader'],
    ['S6', 'Reads the text aloud and highlights the current sentence', 'Listen button using the phone\'s text-to-speech'],
    ['S7', 'Syllable breaker for ChiShona and English', 'Syllables button; rule-based splitter tested on sample words'],
    ['S8', 'All screens available in ChiShona and English', 'EN/SN switch at the top of every screen'],
    ['S9', 'Private: no photos or text leave the phone', 'All processing on the phone; notes in local storage'],
    ['S10', 'Simple: no more than three taps from photo to reading', 'Snap → Convert to text → Reader'],
    ['S11', 'Low cost: free for learners', 'Open-source tools; free hosting'],
], [1.2, 7.4, 7.4], 'Product specifications for Kuverenga Lens')

H('3.5 Materials and technologies', 2)
table(['Item', 'Purpose', 'Cost'], [
    ['Laptop with a web browser and text editor', 'Writing and testing the code', 'Already owned'],
    ['HTML, CSS and JavaScript', 'Building the screens and logic of the app', 'Free'],
    ['Tesseract.js 5.1.1 + English language model', 'On-phone optical character recognition', 'Free (Apache 2.0)'],
    ['OpenDyslexic font', 'Dyslexia-friendly typeface', 'Free (SIL OFL)'],
    ['Web Speech API', 'Text-to-speech using the phone\'s own voices', 'Free (built into browsers)'],
    ['Python + Playwright', 'Automated testing, screenshots and demo video', 'Free'],
    ['GitHub Pages', 'Free https hosting for installing the app', 'Free'],
    ['Android phone', 'Testing on a real device', 'See costing'],
], [5.8, 7.0, 3.2], 'Materials and technologies used')

H('3.6 Production process: how the app was built', 2)
P('The app was built in the following steps. The screens are shown in Figure 3, the architecture in Figure 4 and the three-step process in Figure 6.')
steps = [
    ('Step 1: Screen design.', 'Paper sketches of the three main steps (Snap, Convert, Read) were turned into simple screens with large buttons (at least 52 pixels high) and a bottom navigation bar for Home, Notes and Help. Colours were taken from the chalkboard (deep green) and chalk (cream), with a sunny yellow for the main reading action.'),
    ('Step 2: Logo and identity.', 'The logo shows a chalkboard tile with a reading lens that makes the letters "b" and "d" clear, the two letters most often confused by learners with dyslexia (Figure 5).'),
    ('Step 3: Capturing the board.', 'An HTML file input with the capture="environment" setting opens the rear camera on phones. The photo is scaled to at most 1,800 pixels to keep processing fast on low-cost phones. The app measures the average brightness; if the photo is dark, "Chalkboard mode" is switched on automatically.'),
    ('Step 4: Cleaning the image.', 'The photo is converted to grey, and the light-on-dark chalk is inverted to dark-on-light. In version 2, the uneven background (glare, shadows, dust) is estimated by shrinking and smoothing the image, then subtracted, leaving only the writing (Figure 8). An optional black-and-white mode uses Otsu\'s (1979) threshold.'),
    ('Step 5: Recognising the text.', 'The cleaned image is passed to Tesseract.js running on the phone. The engine files are stored inside the app, so no internet is needed after installation.'),
    ('Step 6: Tidying the text.', 'Lines with very low confidence or fewer than three letters (usually smudges) are removed. Lines that the board\'s edge split mid-sentence are joined. Words the engine is unsure about are kept but given a wavy underline so the learner knows to check them, and the "Fix text" screen allows corrections.'),
    ('Step 7: The dyslexia-friendly reader.', 'Text is shown in OpenDyslexic with wide spacing on a cream background. A Display panel changes font, size, line spacing, background colour, reading speed and a "focus line" that dims other sentences.'),
    ('Step 8: Syllable breaker.', 'For ChiShona, a syllable ends after each vowel (ma·ngwa·na·ni). For English, rules of thumb split between double consonants (win·ter), before a single consonant (ba·by) and before consonant + "le" (ta·ble). The app detects the text language automatically, and the learner can switch it.'),
    ('Step 9: Read-aloud.', 'The phone\'s built-in voices read one sentence at a time while the sentence is highlighted, and tapping a word reads that word alone, split into syllables when Syllables is on. For ChiShona, the app looks for a Shona voice, then for a closely related language (Swahili, Zulu, Xhosa).'),
    ('Step 10: Two languages.', 'Every label is stored in English and ChiShona, and the EN/SN switch changes the whole app instantly.'),
    ('Step 11: Notes and offline mode.', 'Notes are saved on the phone. A service worker stores every file of the app, including the 11 MB OCR engine, so it works offline. A web manifest gives the app its name, icon and colours when installed.'),
    ('Step 12: Testing and improvement.', 'An automated test ran 14 board photos through the app (Section 3.7). Version 1 performed poorly on blurred and dusty photos, so the image-cleaning step was redesigned (version 2) and the test was repeated.'),
    ('Step 13: Publishing.', 'The app folder is uploaded to GitHub Pages, which gives a free https link. Phones open the link and choose "Add to Home screen" (Android) or "Share › Add to Home Screen" (iPhone). An APK can also be generated with PWABuilder and shared by WhatsApp (Appendix C).'),
]
for head, body in steps: P(f'**{head}** {body}')
fig('diagrams/diagram_screens.png', 'Screen flow of the app (real screenshots of the prototype)')
fig('diagrams/diagram_arch.png', 'System architecture: every component runs on the phone')
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
p.add_run().add_picture(os.path.join(K, 'app/icons/icon-512.png'), width=Cm(3.5))
caption('Figure', 'Kuverenga Lens logo: a reading lens over the chalkboard making "b" and "d" clear')
fig('diagrams/diagram_how.png', 'How the app works: Snap, Convert, Read')

H('3.7 Testing method', 2)
P('**Recognition test.** No real photos were available at the building stage, so 14 test photos were generated by computer to simulate chalkboards: cream "chalk" handwriting on a textured green board with wipe marks. There were two boards (one in English, one in ChiShona), each under seven conditions: a good straight photo, an angled photo, camera shake, a dim classroom, window glare, a photo from the back of the class, and a dusty board. Each photo was processed in two ways: (a) the raw photo sent directly to the OCR engine, and (b) through the app\'s cleaning steps. The test ran automatically in a phone-sized web browser.')
P('**Measure.** Word accuracy = number of board words reproduced correctly ÷ number of words on the board × 100, ignoring capital letters and punctuation. Extra "junk" words produced from smudges were also counted.')
P('**Learner trial (planned).** [Number] learners will copy a short board passage in two ways: (1) by hand from the board and (2) using Kuverenga Lens. Time taken, words copied correctly and learner rating (1–5) will be recorded in the trial sheet of *needs_assessment_template.xlsx*.')

# =====================================================================
# 4 RESULTS
# =====================================================================
H('4. Results', 1)
H('4.1 Needs assessment results', 2)
P('[Enter your needs assessment results here. Use the spreadsheet needs_assessment_template.xlsx: type each learner\'s and teacher\'s answers in the data sheets, and the Summary sheet will count them and draw the charts. Copy the charts into this section with captions, and fill in Tables 5 and 6.]')
table(['Question (learners)', 'Never', 'Sometimes', 'Often', 'Always'], [
    ['Is it hard to read the words on the chalkboard?', '[ ]', '[ ]', '[ ]', '[ ]'],
    ['Do letters seem to move or swap (like b and d)?', '[ ]', '[ ]', '[ ]', '[ ]'],
    ['Does the teacher wipe the board before you finish copying?', '[ ]', '[ ]', '[ ]', '[ ]'],
    ['Do you lose your place when you look from the board to your book?', '[ ]', '[ ]', '[ ]', '[ ]'],
], [8.0, 2.0, 2.0, 2.0, 2.0], 'Learner questionnaire results (number of learners, n = [ ])')
table(['Question (teachers)', 'Result'], [
    ['Average number of learners per class who struggle to read from the board', '[ ]'],
    ['Teachers who say slow copying delays lessons (Often/Always)', '[ ] of [ ]'],
    ['Learners with access to a smartphone at home (own or family)', '[ ]%'],
    ['Teachers who would allow learners to photograph the board', '[ ] of [ ]'],
    ['Language(s) needed: English / ChiShona / Both', '[ ] / [ ] / [ ]'],
], [12.0, 4.0], 'Teacher questionnaire results (n = [ ])')
P('**Observation summary:** [e.g. average time the board stayed up before being wiped, behaviours observed such as copying letter by letter, asking neighbours, leaving notes unfinished].')

H('4.2 The working prototype', 2)
P('A complete working prototype was produced. It meets specifications S1 and S3–S11 as designed, and S2 was tested (Section 4.3). Figure 7 shows the main reading features.')
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
for f in ('05_reader_opendyslexic.png', '13_reader_shona_syllables.png', '07_display_panel.png', '09_reader_dark.png'):
    p.add_run().add_picture(os.path.join(K, 'evidence/screenshots', f), width=Cm(3.8)); p.add_run(' ')
caption('Figure', 'Reader screens: OpenDyslexic text, ChiShona syllables, the Display panel and the dark background')
fig('diagrams/diagram_pipeline.png', 'What the app does to a photo with window glare (real output of the prototype)')

H('4.3 Text recognition accuracy', 2)
rows = []
for c, name in COND:
    rows.append([name, f'{acc(v2, c, "raw photo"):.1f}', f'{acc(v1, c, "with clean-up"):.1f}', f'{acc(v2, c, "with clean-up"):.1f}'])
rows.append(['**Average (all 14 photos)**', f'**{RAW:.1f}**', f'**{V1:.1f}**', f'**{V2:.1f}**'])
table(['Condition', 'Raw photo (%)', 'Prototype v1 (%)', 'Prototype v2 (%)'], rows, [6.4, 3.2, 3.2, 3.2],
      'Average word accuracy by classroom condition (English and ChiShona boards combined)')
fig('charts/fig_accuracy_by_condition.png', 'Word accuracy by condition for the raw photo, prototype v1 and prototype v2')
fig('charts/fig_accuracy_overall.png', 'Average word accuracy across all 14 test photos', width=11)
P(f'Full results for every photo, including the text the app produced, are in Appendix B and in the files accuracy_results_v1.csv and accuracy_results_v2.csv. On a laptop browser each photo took between 0.1 and 0.5 seconds to recognise. Processing on low-cost phones is expected to be slower, and this should be measured in the classroom trial: [record time on your phone].')

H('4.4 Syllable breaker check', 2)
table(['Language', 'Words tested (output of the app)'], [
    ['ChiShona', 'Mwa·na, a·no·e·nda, ku·chi·ko·ro, ma·ngwa·na·ni, ku·bi·ka, sa·dza, mu·nda, we·chi·ba·ge, nzo·u, mhu·ri, zvi·nhu, svi·ka, bhu·ku, dzi·mba, nyi·ka'],
    ['English', 'wa·ter, sun·light, tea·cher, mo·ther, lit·tle, ta·ble, pock·et, win·ter, ba·by, o·pen, pho·to·syn·the·sis, re·mem·ber, yes·ter·day'],
], [3.0, 13.0], 'Syllable breaker output for sample words')
P('All 15 ChiShona words were split correctly. The English rules handled common patterns, but English spelling is irregular, so some words are not split perfectly. For example, "science" stays whole because the rules treat "ie" as one vowel sound.')

H('4.5 Learner trial results', 2)
P('[Enter results of the learner trial: time to copy, words correct, and learner ratings with and without the app. The trial sheet in needs_assessment_template.xlsx calculates averages and draws a comparison chart.]')

# =====================================================================
# 5 DISCUSSION
# =====================================================================
H('5. Discussion and Interpretation', 1)
H('5.1 What the results show', 2)
P(f'The hypothesis was only partly supported at first. The first version of the cleaning step (v1) was **worse** than doing nothing: its average accuracy was {V1:.1f}% against {RAW:.1f}% for the raw photo. The v1 step stretched the contrast strongly, and on blurred writing (camera shake, {acc(v1, "3_shake", "with clean-up"):.0f}%) and on the dusty board ({acc(v1, "7_dusty", "with clean-up"):.0f}%) this turned the faint grey edges of letters into noise. This was an important finding. It showed that more image processing is not always better, and that the design had to be tested, not assumed.')
P(f'Version 2 replaced the contrast stretch with **background flattening**: the app estimates the slowly changing background (glare, shadows, dust haze) and subtracts it. This raised the average to {V2:.1f}%, higher than the raw photo. The biggest gain was for window glare, where raw recognition was only {acc(v2, "5_glare", "raw photo"):.0f}% because the bright patch hid part of the board. Flattening removed the patch (Figure 8) and raised accuracy to {acc(v2, "5_glare", "with clean-up"):.0f}%. Glare is common in classrooms with large windows, so this matters in practice. The junk filter also removed most smudge "words" that the raw OCR produced.')
P('ChiShona boards were recognised as accurately as English boards, even though the OCR engine uses an English language model. This is likely because ChiShona is written with the same Latin letters and has a regular, phonetic spelling.')

H('5.2 Anomalies and unusual results', 2)
bullets([
    'In several photos the OCR read "take" as "fake", with high confidence, so the app did not mark it as doubtful. A wrong word in science notes could mislead a learner, which is why the "Fix text" step and teacher checking remain important.',
    'Prototype v1 scored 100% in good conditions but failed badly in poor conditions. Testing only in good conditions would have hidden this weakness.',
    'Shona with camera shake scored 93% in v2 against 100% for the raw photo, so flattening slightly hurt very blurred writing. The contrast slider lets the learner reduce flattening when needed.',
])

H('5.3 Limitations', 2)
bullets([
    '**Simulated photos.** The test photos were computer-generated using a neat handwriting-style font. Real teachers\' handwriting, especially joined writing, will be harder to read, so real accuracy is expected to be lower than these results.',
    '**Small test set.** 14 photos and about 300 words is a small sample. The v2 settings were chosen using the same photos, which may make the results look better than they would on new photos.',
    '**Shona voice.** Most phones do not yet have a ChiShona text-to-speech voice. The app falls back to a similar language, which does not sound fully natural.',
    '**Phone access and school rules.** Not every learner has a phone, and some schools ban phones in class. The innovation may need shared class phones or teacher-operated use.',
    '**Not a diagnosis.** The app supports reading. It does not diagnose dyslexia or replace specialist teaching.',
])

H('5.4 Future extensions', 2)
bullets([
    'Train or fine-tune the OCR on real Zimbabwean chalkboard handwriting, and add a ChiShona language model.',
    'Record a natural ChiShona voice for read-aloud (working with linguists at the University of Zimbabwe).',
    'Add support for maths symbols, diagrams and whiteboards.',
    'A teacher mode that shares typed notes from the teacher\'s phone to learners\' phones by QR code.',
    'Add other Zimbabwean languages such as isiNdebele, Tonga and Kalanga.',
])

# =====================================================================
# 6 COSTING, MARKETING, ENTREPRENEURSHIP
# =====================================================================
H('6. Costing, Marketing and Entrepreneurship', 1)
H('6.1 Costing', 2)
table(['Item', 'Cost (US$)', 'Notes'], [
    ['Internet data for development and testing', '20', 'Downloading tools and uploading the app'],
    ['Second-hand Android test phone', '60', 'For testing on a real low-cost device'],
    ['Printing report, poster and learner guides', '25', ''],
    ['Teacher demonstration session', '30', 'Transport and refreshments'],
    ['Web hosting (GitHub Pages)', '0', 'Free'],
    ['OCR engine, font, development tools', '0', 'Open source'],
    ['Developer time (estimated 60 hours)', '[0 / in kind]', 'Student\'s own time'],
    ['**Total cash cost**', '**135**', ''],
], [7.5, 2.5, 6.0], 'Estimated cost of developing the prototype [update with your real costs]')
fig('charts/fig_costs.png', 'Breakdown of the estimated development cost')
P('The cost of each extra user is almost zero, because copying an app costs nothing and the app runs on phones that families already have. The main running costs are keeping the app updated (estimated US$120 per year for data and maintenance) and training teachers.')

H('6.2 Business model and pricing', 2)
P('Kuverenga Lens will be **free for learners and parents**, because the families who most need it can least afford to pay. Income comes from a **school support plan** at US$30 per school per year, which includes a teacher training session, printed learner guides, help with installing the app on school or family phones, and updates. Additional funding will be sought from education NGOs, disability organisations and innovation competitions. At an estimated cost of US$10 per school per year plus US$255 in fixed yearly costs (development and upkeep), the plan breaks even at about 13 schools (Figure 12).')
fig('charts/fig_break_even.png', 'Break-even analysis for the school support plan (estimates)')

H('6.3 Marketing plan', 2)
table(['Element', 'Plan'], [
    ['Product', 'Free, offline, bilingual dyslexia-friendly reader for chalkboard notes; installs without the Play Store.'],
    ['Price', 'Free for learners; US$30/year school support plan; free for schools that cannot pay where sponsored.'],
    ['Place', 'Shared as a link, QR code or APK file (WhatsApp, Bluetooth); installed during school visits.'],
    ['Promotion', 'Demonstrations at school staff meetings and School Development Committee meetings; the RISED 301 innovation expo; teacher WhatsApp groups; Facebook page; short demo video; partnerships with inclusive education officers and dyslexia support groups.'],
], [3.2, 12.8], 'Marketing mix (4 Ps) for Kuverenga Lens')
table(['Strengths', 'Weaknesses'], [
    ['Free for learners; works offline; private; ChiShona support; no Play Store needed', 'Lower accuracy on joined handwriting; no natural Shona voice yet; needs a phone'],
], [8.0, 8.0], 'SWOT analysis')
t = doc.tables[-1]
r = t.add_row().cells; r[0].text = ''; r[1].text = ''
for i, h in enumerate(['Opportunities', 'Threats']):
    run = r[i].paragraphs[0].add_run(h); run.bold = True; run.font.size = Pt(10); run.font.color.rgb = RGBColor(255, 255, 255); shade(r[i], '1F4D3A')
r = t.add_row().cells
for i, v in enumerate(['Inclusive education policy; growing smartphone access; NGO funding; expansion to other languages and countries',
                       'School phone bans; competition from big-tech apps; unreliable electricity for charging']):
    r[i].text = ''; run = r[i].paragraphs[0].add_run(v); run.font.size = Pt(10)

H('6.4 Entrepreneurship', 2)
P('Entrepreneurship means seeing an opportunity and organising resources, and taking a risk, to create value (Drucker, 1985). This project is a **social enterprise**: its main goal is social impact (inclusion of learners with reading difficulties), with income used to keep the service running and growing. The plan is to (1) pilot at [School name], (2) collect evidence from the trial, (3) offer the support plan to neighbouring schools in [District], (4) seek partnership with the Ministry of Primary and Secondary Education\'s inclusive education officers and with NGOs, and (5) enter innovation competitions and university innovation hubs for seed funding. Future paid features for schools, such as a teacher dashboard, could add income while the learner app stays free.')

# =====================================================================
# 7 SIGNIFICANCE AND IMPACT
# =====================================================================
H('7. Significance and Impact of the Innovation', 1)
table(['Level', 'Impact'], [
    ['Myself', '[Personalise: e.g. I learnt how to carry out a needs assessment, design to a brief, write code, test and improve a product, and cost and market an innovation. As a future teacher I am now more aware of learners with dyslexia and of how to adapt my own board work.]'],
    ['Other people', 'Learners with dyslexia can read and hear board notes at their own pace, in their own language, and keep notes for revision, which builds independence and confidence. Teachers spend less time re-writing notes for individual learners. Parents can help with homework using the saved notes.'],
    ['Local community', 'Learners who were at risk of falling behind can take a full part in lessons. The app is free and offline, so it reaches families with little money for data. It also raises awareness of dyslexia, which is often mistaken for laziness or low ability.'],
    ['Zimbabwe', 'Supports inclusive education policy and the use of ChiShona in learning. It shows that Zimbabwean students can build useful educational technology with free tools, and it can be extended to other national languages.'],
    ['Global village', 'Contributes to SDG 4 (inclusive and equitable quality education) and SDG 10 (reduced inequalities). The approach suits any low-resource classroom that still uses a chalkboard, across Africa and beyond, and the code can be shared openly.'],
], [3.2, 12.8], 'Significance of Kuverenga Lens at different levels')

# =====================================================================
# 8 CONCLUSION
# =====================================================================
H('8. Conclusion and Recommendations', 1)
P(f'This project identified a real classroom need: learners with dyslexia struggle to read and copy chalkboard notes. In response it designed and built Kuverenga Lens, a working, free, offline, bilingual phone app that converts board photos into dyslexia-friendly text that can be read and heard. The app installs without the Google Play Store. Testing on 14 simulated board photos showed that careful image cleaning matters. The first design reduced accuracy to {V1:.1f}%, but the improved design reached {V2:.1f}%, above the {RAW:.1f}% achieved by the raw photo, and largely solved the problem of window glare. The objectives of building and testing the prototype were achieved. The remaining evidence on learner benefit will come from the classroom trial.')
P('**Recommendations:**')
bullets([
    'Pilot the app with learners at [School name], collecting real board photos and copying-time data.',
    'Teachers should write clearly in print rather than joined writing, leave notes on the board a little longer, and check the app\'s text for key words.',
    'Schools should allow supervised phone use for learners with reading difficulties as a reasonable accommodation.',
    'Researchers should develop a ChiShona OCR model and a natural ChiShona voice.',
])

# =====================================================================
# REFERENCES (APA 7th)
# =====================================================================
H('References', 1)
REFS = [
    'British Dyslexia Association. (2023). *Dyslexia style guide 2023: Creating dyslexia friendly content*. https://www.bdadyslexia.org.uk/advice/employers/creating-a-dyslexia-friendly-workplace/dyslexia-friendly-style-guide',
    'Brown, T. (2008). Design thinking. *Harvard Business Review, 86*(6), 84–92.',
    'Creswell, J. W., & Creswell, J. D. (2018). *Research design: Qualitative, quantitative, and mixed methods approaches* (5th ed.). SAGE.',
    'Drucker, P. F. (1985). *Innovation and entrepreneurship: Practice and principles*. Harper & Row.',
    'Fortune, G. (1955). *An analytical grammar of Shona*. Longmans, Green.',
    'International Dyslexia Association. (2002). *Definition of dyslexia*. https://dyslexiaida.org/definition-of-dyslexia/',
    'International Dyslexia Association. (n.d.). *Dyslexia basics*. https://dyslexiaida.org/dyslexia-basics/',
    'Lyon, G. R., Shaywitz, S. E., & Shaywitz, B. A. (2003). A definition of dyslexia. *Annals of Dyslexia, 53*, 1–14. https://doi.org/10.1007/s11881-003-0001-9',
    'OECD/Eurostat. (2018). *Oslo manual 2018: Guidelines for collecting, reporting and using data on innovation* (4th ed.). OECD Publishing. https://doi.org/10.1787/9789264304604-en',
    'Otsu, N. (1979). A threshold selection method from gray-level histograms. *IEEE Transactions on Systems, Man, and Cybernetics, 9*(1), 62–66. https://doi.org/10.1109/TSMC.1979.4310076',
    'Rello, L., & Baeza-Yates, R. (2013). Good fonts for dyslexia. In *Proceedings of the 15th International ACM SIGACCESS Conference on Computers and Accessibility* (Article 14). ACM. https://doi.org/10.1145/2513383.2513447',
    'Schumpeter, J. A. (1934). *The theory of economic development*. Harvard University Press.',
    'Smith, R. (2007). An overview of the Tesseract OCR engine. In *Ninth International Conference on Document Analysis and Recognition (ICDAR 2007)* (Vol. 2, pp. 629–633). IEEE. https://doi.org/10.1109/ICDAR.2007.4376991',
    'Snowling, M. J. (2019). *Dyslexia: A very short introduction*. Oxford University Press.',
    'Ulrich, K. T., & Eppinger, S. D. (2016). *Product design and development* (6th ed.). McGraw-Hill Education.',
    'UNESCO. (2020). *Global education monitoring report 2020: Inclusion and education: All means all*. UNESCO. https://doi.org/10.54676/JJNK6989',
    'United Nations. (2015). *Transforming our world: The 2030 agenda for sustainable development* (A/RES/70/1). https://sdgs.un.org/2030agenda',
    'Wery, J. J., & Diliberto, J. A. (2017). The effect of a specialized dyslexia font, OpenDyslexic, on reading rate and accuracy. *Annals of Dyslexia, 67*(2), 114–127. https://doi.org/10.1007/s11881-016-0127-1',
    'Wood, S. G., Moxley, J. H., Tighe, E. L., & Wagner, R. K. (2018). Does use of text-to-speech and related read-aloud tools improve reading comprehension for students with reading disabilities? A meta-analysis. *Journal of Learning Disabilities, 51*(1), 73–84. https://doi.org/10.1177/0022219416688170',
    'Zorzi, M., Barbiero, C., Facoetti, A., Lonciari, I., Carrozzi, M., Montico, M., Bravar, L., George, F., Pech-Georgel, C., & Ziegler, J. C. (2012). Extra-large letter spacing improves reading in dyslexia. *Proceedings of the National Academy of Sciences, 109*(28), 11455–11459. https://doi.org/10.1073/pnas.1205566109',
    '[Add local Zimbabwean sources, e.g. Ministry of Primary and Secondary Education inclusive education policy documents and articles on learning disabilities in Zimbabwe.]',
]
import re
for ref in REFS:
    p = doc.add_paragraph(); p.paragraph_format.left_indent = Cm(1.27); p.paragraph_format.first_line_indent = Cm(-1.27)
    p.paragraph_format.line_spacing = 1.15
    for part in re.split(r'(\*[^*]+\*|\[[^\]]+\])', ref):
        if not part: continue
        if part.startswith('*'): r = p.add_run(part[1:-1]); r.italic = True
        elif part.startswith('['): r = p.add_run(part); r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        else: p.add_run(part)

# =====================================================================
# APPENDICES
# =====================================================================
page_break()
H('Appendix A: Needs assessment questionnaires', 1)
H('A1. Learner questionnaire (read aloud to the learner if needed)', 2)
P('Learner code: ______   Grade/Form: ______   Age: ______   Date: ______', align=WD_ALIGN_PARAGRAPH.LEFT)
table(['No.', 'Question', 'Answer (tick one)'], [
    ['1', 'Is it hard to read the words on the chalkboard? / Zvakaoma here kuverenga mashoko ari pabhodhi?', 'Never / Sometimes / Often / Always'],
    ['2', 'Do letters seem to move or swap (like b and d)?', 'Never / Sometimes / Often / Always'],
    ['3', 'Does the teacher wipe the board before you finish copying?', 'Never / Sometimes / Often / Always'],
    ['4', 'Do you lose your place when you look from the board to your book?', 'Never / Sometimes / Often / Always'],
    ['5', 'Can you use a phone at home?', 'My own / Family phone / No'],
    ['6', 'Would it help to hear the board notes read aloud?', 'Yes / No / Not sure'],
    ['7', 'Which language do you prefer for reading?', 'English / ChiShona / Both'],
    ['8', 'Which background colour is easiest for you to read on? (show colour cards)', 'White / Cream / Blue / Green / Yellow'],
    ['9', 'After trying the app: how easy was it to read the notes? (1 = very hard, 5 = very easy)', '1  2  3  4  5'],
], [1.0, 9.5, 5.5])
H('A2. Teacher questionnaire', 2)
table(['No.', 'Question', 'Answer'], [
    ['1', 'How many learners in your class have difficulty reading from the chalkboard?', '______'],
    ['2', 'How often does slow copying from the board delay your lessons?', 'Never / Sometimes / Often / Always'],
    ['3', 'About how long do notes stay on the board before you wipe them?', '______ minutes'],
    ['4', 'What do you currently do to help learners who cannot copy in time?', '______'],
    ['5', 'About what share of your learners can use a smartphone at home?', 'None / A few / About half / Most'],
    ['6', 'Would you allow learners with reading difficulties to photograph the board?', 'Yes / No / With conditions'],
    ['7', 'Which language(s) should such an app support?', 'English / ChiShona / Both / Other'],
    ['8', 'Any suggestions for the app?', '______'],
], [1.0, 9.5, 5.5])
H('A3. Lesson observation sheet', 2)
table(['Lesson / date', 'Minutes notes stayed on board', 'Learners not finished when wiped', 'Behaviours observed'], [
    ['[ ]', '[ ]', '[ ]', '[ ]'], ['[ ]', '[ ]', '[ ]', '[ ]'], ['[ ]', '[ ]', '[ ]', '[ ]'],
], [3.5, 3.5, 3.5, 5.5])

H('Appendix B: Full recognition test results', 1)
rows = []
for r1, r2 in zip([r for r in v1 if r['pipeline'] == 'with clean-up'], [r for r in v2 if r['pipeline'] == 'with clean-up']):
    raw = next(x for x in v2 if x['photo'] == r2['photo'] and x['pipeline'] == 'raw photo')
    rows.append([r2['photo'].replace('.jpg', ''), raw['word_accuracy_pct'], r1['word_accuracy_pct'], r2['word_accuracy_pct'], r2['extra_junk_words']])
table(['Test photo', 'Raw (%)', 'v1 (%)', 'v2 (%)', 'Junk words (v2)'], rows, [6.0, 2.4, 2.4, 2.4, 2.8],
      'Word accuracy for each test photo', size=9)
P('Example of v2 output for the "window glare" photo: "' + next(r['ocr_text'] for r in v2 if r['photo'] == 'english_5_glare.jpg' and r['pipeline'] == 'with clean-up') + '"', italic=True, size=10)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
for f in ('english_1_good', 'english_2_angle', 'english_4_dim', 'shona_3_shake', 'shona_6_far', 'shona_7_dusty'):
    p.add_run().add_picture(os.path.join(K, 'testing/photos', f + '.jpg'), width=Cm(5.1)); p.add_run(' ')
caption('Figure', 'Examples of the simulated test photos (good, angle, dim, shake, far, dusty)')

H('Appendix C: How to install Kuverenga Lens without the Play Store', 1)
bullets([
    'Upload the contents of the app folder to a free GitHub Pages site (Settings › Pages › main branch). The app is then available at https://<username>.github.io/kuverenga-lens/.',
    'Android: open the link in Chrome and tap "Install on this phone" or ⋮ › Add to Home screen.',
    'iPhone: open the link in Safari, tap Share › Add to Home Screen.',
    'Open the app once while online. After that it works offline.',
    'Optional APK: paste the link into pwabuilder.com › Package for stores › Android, download the APK, and share it by WhatsApp. On the phone, allow "Install unknown apps" for the app used to open it.',
    'App link: [paste your GitHub Pages link here]    QR code: [insert QR code]',
], style='List Number')

H('Appendix D: Source code structure', 1)
table(['File', 'Lines', 'Purpose'], [
    ['index.html', '266', 'The six screens and bottom navigation'],
    ['js/app.js', '727', 'Photo loading, image cleaning, OCR, text tidying, reader, read-aloud, notes, two languages, install'],
    ['js/syllables.js', '91', 'Syllable breaker for ChiShona and English'],
    ['css/style.css', '251', 'Layout, colours, dyslexia-friendly reading area'],
    ['sw.js', '46', 'Service worker for offline use'],
    ['manifest.webmanifest', '—', 'App name, icons and colours for installation'],
    ['testing/run_accuracy_test.py', '—', 'Automated recognition test that produced Appendix B'],
], [4.6, 1.6, 9.8], 'Files that make up the app')

H('Appendix E: Authentic materials checklist', 1)
P('The rubric gives marks for authentic material showing what was done, when, where and how. Add the following to your file or display:')
bullets([
    '[Photos of your paper sketches of the screens]',
    '[Completed questionnaires (originals or scans)]',
    '[Photos of the app being tested in the classroom (with consent)]',
    '[Real photos of chalkboards taken with the app, and the text produced]',
    'Screenshots of every screen (folder evidence/screenshots) and the demo video (evidence/video/kuverenga_lens_demo.mp4)',
    'Test results v1 and v2 (testing/accuracy_results_v1.csv, accuracy_results_v2.csv)',
    '[Emails or letters requesting permission from the school]',
])

page_numbers(doc.sections[0])
doc.save(OUT)
print('saved', OUT, '| figures', counters['Figure'], '| tables', counters['Table'])
