"""Converts README.md into a formatted Word document (Kuverenga_Lens_README.docx).
Handles the Markdown used in the README: headings, paragraphs, lists, tables, code blocks, **bold**, `code`, links."""
import os, re
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__)); K = os.path.dirname(HERE)
GREEN = RGBColor(0x1F, 0x4D, 0x3A)
doc = Document()
sec = doc.sections[0]; sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
sec.left_margin = sec.right_margin = Cm(2.3); sec.top_margin = sec.bottom_margin = Cm(2.0)
st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11); st.paragraph_format.space_after = Pt(6); st.paragraph_format.line_spacing = 1.2
for name, size in (('Title', 26), ('Heading 1', 16), ('Heading 2', 13)):
    s = doc.styles[name]; s.font.name = 'Arial'; s.font.size = Pt(size); s.font.bold = True; s.font.color.rgb = GREEN
    rpr = s.element.get_or_add_rPr(); rf = rpr.find(qn('w:rFonts'))
    if rf is None: rf = OxmlElement('w:rFonts'); rpr.append(rf)
    for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'): rf.set(qn(a), 'Arial')
    s.paragraph_format.space_before = Pt(14 if name != 'Title' else 0); s.paragraph_format.space_after = Pt(6); s.paragraph_format.keep_with_next = True

def shade(el_pr, fill):
    sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), fill); el_pr.append(sh)

def inline(p, text, size=None, color=None, bold=False):
    for part in re.split(r'(\*\*[^*]+\*\*|`[^`]+`|<https?://[^>]+>|\[[^\]]+\]\([^)]+\)|\*[^*]+\*)', text):
        if not part: continue
        if part.startswith('**'): r = p.add_run(part[2:-2]); r.bold = True
        elif part.startswith('`'):
            r = p.add_run(part[1:-1]); r.font.name = 'Consolas'; r.font.color.rgb = RGBColor(0x8A, 0x2B, 0x0B)
        elif part.startswith('<http'): r = p.add_run(part[1:-1]); r.font.color.rgb = RGBColor(0x1F, 0x5F, 0xBF); r.underline = True
        elif part.startswith('[') and '](' in part:
            label, url = re.match(r'\[([^\]]+)\]\(([^)]+)\)', part).groups(); r = p.add_run(label)
        elif part.startswith('*') and len(part) > 2: r = p.add_run(part[1:-1]); r.italic = True
        else: r = p.add_run(part)
        if size: r.font.size = Pt(size)
        if color: r.font.color.rgb = color
        if bold: r.bold = True

lines = open(os.path.join(K, 'README.md'), encoding='utf-8').read().split('\n')
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
p.add_run().add_picture(os.path.join(K, 'app/icons/icon-512.png'), width=Cm(2.6))
i = 0
while i < len(lines):
    ln = lines[i]
    if ln.startswith('# '):
        doc.add_paragraph(ln[2:], style='Title')
    elif ln.startswith('## '):
        doc.add_heading(ln[3:], 1)
    elif ln.startswith('```'):
        code = []; i += 1
        while i < len(lines) and not lines[i].startswith('```'): code.append(lines[i]); i += 1
        t = doc.add_table(rows=1, cols=1); c = t.rows[0].cells[0]; c.text = ''
        shade(c._tc.get_or_add_tcPr(), 'F2F2F2')
        for k, cl in enumerate(code):
            cp = c.paragraphs[0] if k == 0 else c.add_paragraph()
            r = cp.add_run(cl); r.font.name = 'Consolas'; r.font.size = Pt(9.5)
            cp.paragraph_format.space_after = Pt(0); cp.paragraph_format.line_spacing = 1.0
        doc.add_paragraph().paragraph_format.space_after = Pt(0)
    elif ln.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].startswith('|'):
            cells = [x.strip() for x in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r':?-{3,}:?', x) for x in cells): rows.append(cells)
            i += 1
        i -= 1
        t = doc.add_table(rows=0, cols=len(rows[0])); t.style = 'Table Grid'
        for ri, row in enumerate(rows):
            cells = t.add_row().cells
            for ci, v in enumerate(row):
                cells[ci].text = ''; cp = cells[ci].paragraphs[0]; cp.paragraph_format.space_after = Pt(0)
                if ri == 0:
                    inline(cp, v.replace('**', ''), size=10, color=RGBColor(255, 255, 255), bold=True); shade(cells[ci]._tc.get_or_add_tcPr(), '1F4D3A')
                else: inline(cp, v, size=10)
        widths = [Cm(5.2), Cm(11.2)] if len(rows[0]) == 2 else None
        if widths:
            for row in t.rows:
                for ci, w in enumerate(widths): row.cells[ci].width = w
        doc.add_paragraph().paragraph_format.space_after = Pt(0)
    elif re.match(r'^\d+\. ', ln):
        # numbers written out so every list restarts at 1 (Word's List Number style continues across lists)
        np_ = doc.add_paragraph(); np_.paragraph_format.left_indent = Cm(0.9); np_.paragraph_format.first_line_indent = Cm(-0.6)
        np_.paragraph_format.space_after = Pt(3)
        num, rest = re.match(r'^(\d+)\. (.*)', ln).groups(); r = np_.add_run(num + '.\t'); r.bold = True
        inline(np_, rest)
    elif ln.startswith('- '):
        inline(doc.add_paragraph(style='List Bullet'), ln[2:])
    elif ln.strip():
        inline(doc.add_paragraph(), ln)
    i += 1

out = os.path.join(K, 'Kuverenga_Lens_README.docx'); doc.save(out); print('saved', out)
