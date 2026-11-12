"""Builds needs_assessment_template.xlsx: data-entry sheets for the questionnaires and learner trial,
with a Summary sheet that counts answers (formulas) and draws charts automatically."""
import os
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'needs_assessment_template.xlsx')
F = 'Arial'
HEAD = PatternFill('solid', fgColor='1F4D3A'); INPUT = PatternFill('solid', fgColor='FFF2A8'); EX = PatternFill('solid', fgColor='EDEDED')
thin = Side(style='thin', color='CFCFCF'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
N = 60   # rows available for responses (rows 4..63)
FIRST, LAST = 4, 3 + N

wb = Workbook()

def header(ws, cols, widths):
    for i, (c, w) in enumerate(zip(cols, widths), start=1):
        cell = ws.cell(row=2, column=i, value=c)
        cell.font = Font(name=F, bold=True, color='FFFFFF', size=10); cell.fill = HEAD
        cell.alignment = Alignment(wrap_text=True, vertical='center'); cell.border = BOX
        ws.column_dimensions[cell.column_letter].width = w
    ws.row_dimensions[2].height = 58
    ws.freeze_panes = 'A4'

def example(ws, values):
    for i, v in enumerate(values, start=1):
        c = ws.cell(row=3, column=i, value=v); c.fill = EX; c.font = Font(name=F, italic=True, color='666666', size=10); c.border = BOX
    ws.cell(row=3, column=1).comment = Comment('Example row showing the expected format. It is NOT counted in the Summary.', 'Kuverenga Lens')

def inputs(ws, ncols):
    for r in range(FIRST, LAST + 1):
        for c in range(1, ncols + 1):
            cell = ws.cell(row=r, column=c); cell.fill = INPUT; cell.border = BOX; cell.font = Font(name=F, size=10)

def dropdown(ws, col, options):
    dv = DataValidation(type='list', formula1='"' + ','.join(options) + '"', allow_blank=True)
    ws.add_data_validation(dv); dv.add(f'{col}{FIRST}:{col}{LAST}')

FREQ = ['Never', 'Sometimes', 'Often', 'Always']

# ---------------- Read me ----------------
ws = wb.active; ws.title = 'Read me'
lines = [
    ('Kuverenga Lens: needs assessment and trial workbook', True),
    ('', False),
    ('How to use', True),
    ('1. Type each learner\'s answers in the Learners sheet, one row per learner. Use codes (L1, L2 …), not names.', False),
    ('2. Type each teacher\'s answers in the Teachers sheet.', False),
    ('3. During the classroom trial, record times and scores in the Trial sheet.', False),
    ('4. The Summary sheet counts the answers and updates the charts automatically. Copy the charts into your report (section 4.1 and 4.5).', False),
    ('', False),
    ('Legend', True),
    ('Yellow cells = type your data here. Most have a drop-down list.', False),
    ('Grey italic row 3 = an example of the format. It is not counted. You may delete its contents.', False),
    ('White cells in Summary = formulas. Do not type over them.', False),
]
for i, (t, b) in enumerate(lines, start=1):
    c = ws.cell(row=i, column=1, value=t); c.font = Font(name=F, bold=b, size=14 if i == 1 else 11, color='1F4D3A' if b else '000000')
ws['A10'].fill = INPUT; ws['A11'].fill = EX
ws.column_dimensions['A'].width = 110

# ---------------- Learners ----------------
ws = wb.create_sheet('Learners')
ws['A1'] = 'Learner questionnaire responses'; ws['A1'].font = Font(name=F, bold=True, size=13, color='1F4D3A')
cols = ['Learner code', 'Grade / Form', 'Age', 'Q1 Hard to read the board?', 'Q2 Letters move or swap (b/d)?',
        'Q3 Board wiped before finished copying?', 'Q4 Lose place between board and book?', 'Q5 Phone at home',
        'Q6 Would hearing notes read aloud help?', 'Q7 Preferred language', 'Q8 Easiest background colour', 'Q9 Ease of reading with app (1-5)']
header(ws, cols, [11, 10, 7, 14, 14, 16, 16, 13, 15, 13, 14, 15])
example(ws, ['L0', 'Grade 6', 11, 'Often', 'Sometimes', 'Always', 'Often', 'Family phone', 'Yes', 'Both', 'Cream', 4])
inputs(ws, len(cols))
for col in 'DEFG': dropdown(ws, col, FREQ)
dropdown(ws, 'H', ['My own', 'Family phone', 'No'])
dropdown(ws, 'I', ['Yes', 'No', 'Not sure'])
dropdown(ws, 'J', ['English', 'ChiShona', 'Both'])
dropdown(ws, 'K', ['White', 'Cream', 'Blue', 'Green', 'Yellow'])
dv = DataValidation(type='whole', operator='between', formula1='1', formula2='5', allow_blank=True); ws.add_data_validation(dv); dv.add(f'L{FIRST}:L{LAST}')

# ---------------- Teachers ----------------
ws = wb.create_sheet('Teachers')
ws['A1'] = 'Teacher questionnaire responses'; ws['A1'].font = Font(name=F, bold=True, size=13, color='1F4D3A')
cols = ['Teacher code', 'Class taught', 'T1 Learners who struggle to read the board (number)', 'T2 Slow copying delays lessons?',
        'T3 Minutes notes stay on board', 'T4 What you do now to help', 'T5 Learners with smartphone at home',
        'T6 Allow photographing the board?', 'T7 Language(s) needed', 'T8 Suggestions']
header(ws, cols, [11, 11, 16, 15, 13, 28, 16, 16, 14, 30])
example(ws, ['T0', 'Form 1B', 6, 'Often', 15, 'Let them copy from a friend at break', 'About half', 'With conditions', 'Both', 'Make it work offline'])
inputs(ws, len(cols))
dropdown(ws, 'D', FREQ)
dropdown(ws, 'G', ['None', 'A few', 'About half', 'Most'])
dropdown(ws, 'H', ['Yes', 'No', 'With conditions'])
dropdown(ws, 'I', ['English', 'ChiShona', 'Both', 'Other'])

# ---------------- Trial ----------------
ws = wb.create_sheet('Trial')
ws['A1'] = 'Classroom trial: copying a board passage without and with Kuverenga Lens'; ws['A1'].font = Font(name=F, bold=True, size=13, color='1F4D3A')
cols = ['Learner code', 'Words in passage', 'WITHOUT app: minutes taken', 'WITHOUT app: words correct', 'WITH app: minutes taken',
        'WITH app: words correct', 'Learner rating of app (1-5)', 'Accuracy without (%)', 'Accuracy with (%)', 'Notes']
header(ws, cols, [11, 11, 14, 14, 14, 14, 13, 13, 13, 30])
example(ws, ['L0', 40, 9, 31, 5, 38, 4, '', '', 'Needed help to hold phone steady'])
inputs(ws, 7); 
for r in range(FIRST, LAST + 1):
    ws.cell(row=r, column=10).fill = INPUT; ws.cell(row=r, column=10).border = BOX
    for col, num in (('H', 'D'), ('I', 'F')):
        c = ws[f'{col}{r}']; c.value = f'=IF(OR(B{r}="",{num}{r}=""),"",{num}{r}/B{r})'; c.number_format = '0%'; c.border = BOX; c.font = Font(name=F, size=10)
for col, num in (('H', 'D'), ('I', 'F')):
    ws[f'{col}3'] = f'=IF(OR(B3="",{num}3=""),"",{num}3/B3)'; ws[f'{col}3'].number_format = '0%'

# ---------------- Summary ----------------
ws = wb.create_sheet('Summary')
ws['A1'] = 'Summary (updates automatically)'; ws['A1'].font = Font(name=F, bold=True, size=14, color='1F4D3A')
ws.column_dimensions['A'].width = 46
for c in 'BCDEF': ws.column_dimensions[c].width = 12

def hdr(row, labels):
    for i, l in enumerate(labels):
        c = ws.cell(row=row, column=1 + i, value=l); c.font = Font(name=F, bold=True, color='FFFFFF', size=10); c.fill = HEAD

L = f"Learners!$%s${FIRST}:$%s${LAST}"
ws['A3'] = 'Learners who answered'; ws['B3'] = f'=COUNTA(Learners!$A${FIRST}:$A${LAST})'
ws['A4'] = 'Teachers who answered'; ws['B4'] = f'=COUNTA(Teachers!$A${FIRST}:$A${LAST})'
for a in ('A3', 'A4', 'B3', 'B4'): ws[a].font = Font(name=F, bold=a.startswith('A'), size=11)

hdr(6, ['Learner question (number of learners)'] + FREQ)
qs = [('D', 'Q1 Hard to read the board'), ('E', 'Q2 Letters move or swap'), ('F', 'Q3 Board wiped before finished'), ('G', 'Q4 Lose place board → book')]
for i, (col, q) in enumerate(qs):
    r = 7 + i; ws.cell(row=r, column=1, value=q).font = Font(name=F, size=10)
    for j, f in enumerate(FREQ):
        ws.cell(row=r, column=2 + j, value=f'=COUNTIF({L % (col, col)},"{f}")').font = Font(name=F, size=10)

hdr(12, ['Learner question (%)', 'Often or Always'])
for i, (col, q) in enumerate(qs):
    r = 13 + i; ws.cell(row=r, column=1, value=q).font = Font(name=F, size=10)
    c = ws.cell(row=r, column=2, value=f'=IF($B$3=0,"",(D{7+i}+E{7+i})/$B$3)'); c.number_format = '0%'; c.font = Font(name=F, size=10)

def count_block(row, title, col, opts, sheet='Learners'):
    hdr(row, [title, 'Count'])
    for i, o in enumerate(opts):
        ws.cell(row=row + 1 + i, column=1, value=o).font = Font(name=F, size=10)
        ws.cell(row=row + 1 + i, column=2, value=f'=COUNTIF({sheet}!${col}${FIRST}:${col}${LAST},"{o}")').font = Font(name=F, size=10)
    return row + 1 + len(opts) + 1

r = 18
r = count_block(r, 'Q5 Phone at home', 'H', ['My own', 'Family phone', 'No'])
r = count_block(r, 'Q6 Would read-aloud help?', 'I', ['Yes', 'No', 'Not sure'])
r = count_block(r, 'Q7 Preferred language', 'J', ['English', 'ChiShona', 'Both'])
r = count_block(r, 'Q8 Easiest background colour', 'K', ['White', 'Cream', 'Blue', 'Green', 'Yellow'])
ws.cell(row=r, column=1, value='Q9 Average ease rating with app (1-5)').font = Font(name=F, bold=True, size=10)
c = ws.cell(row=r, column=2, value=f'=IFERROR(AVERAGE(Learners!$L${FIRST}:$L${LAST}),"")'); c.number_format = '0.0'
r += 2
hdr(r, ['Teachers', 'Value']); r += 1
tea = [('Average learners per class who struggle', f'=IFERROR(AVERAGE(Teachers!$C${FIRST}:$C${LAST}),"")', '0.0'),
       ('Say slow copying delays lessons Often/Always', f'=COUNTIF(Teachers!$D${FIRST}:$D${LAST},"Often")+COUNTIF(Teachers!$D${FIRST}:$D${LAST},"Always")', '0'),
       ('Average minutes notes stay on board', f'=IFERROR(AVERAGE(Teachers!$E${FIRST}:$E${LAST}),"")', '0.0'),
       ('Would allow photographing (Yes or With conditions)', f'=COUNTIF(Teachers!$H${FIRST}:$H${LAST},"Yes")+COUNTIF(Teachers!$H${FIRST}:$H${LAST},"With conditions")', '0')]
for label, fml, fmt in tea:
    ws.cell(row=r, column=1, value=label).font = Font(name=F, size=10); c = ws.cell(row=r, column=2, value=fml); c.number_format = fmt; r += 1
r += 1
trial_row = r
hdr(r, ['Trial (averages)', 'Without app', 'With app']); r += 1
for label, a, b, fmt in [('Minutes to copy the passage', 'C', 'E', '0.0'), ('Words correct', 'D', 'F', '0.0'), ('Accuracy', 'H', 'I', '0%')]:
    ws.cell(row=r, column=1, value=label).font = Font(name=F, size=10)
    for k, col in enumerate((a, b)):
        c = ws.cell(row=r, column=2 + k, value=f'=IFERROR(AVERAGE(Trial!${col}${FIRST}:${col}${LAST}),"")'); c.number_format = fmt
    r += 1
ws.cell(row=r, column=1, value='Average learner rating of app (1-5)').font = Font(name=F, size=10)
c = ws.cell(row=r, column=3, value=f'=IFERROR(AVERAGE(Trial!$G${FIRST}:$G${LAST}),"")'); c.number_format = '0.0'

# charts
ch = BarChart(); ch.type = 'bar'; ch.grouping = 'stacked'; ch.overlap = 100
ch.title = 'Learners: reading from the chalkboard'; ch.y_axis.title = 'Number of learners'
ch.add_data(Reference(ws, min_col=2, max_col=5, min_row=6, max_row=10), titles_from_data=True)
ch.set_categories(Reference(ws, min_col=1, min_row=7, max_row=10))
for s, colr in zip(ch.series, ['C9C9C2', '9CC3EE', '2A78D6', '1F4D3A']): s.graphicalProperties.solidFill = colr
ch.height, ch.width = 8, 16; ws.add_chart(ch, 'H3')

ch2 = BarChart(); ch2.title = 'Copying time: without vs with Kuverenga Lens (minutes)'
ch2.add_data(Reference(ws, min_col=2, max_col=3, min_row=trial_row, max_row=trial_row + 1), titles_from_data=True)
ch2.set_categories(Reference(ws, min_col=1, min_row=trial_row + 1, max_row=trial_row + 1))
ch2.series[0].graphicalProperties.solidFill = 'A9A9A2'; ch2.series[1].graphicalProperties.solidFill = '2A78D6'
ch2.height, ch2.width = 8, 16; ws.add_chart(ch2, 'H21')

ch3 = BarChart(); ch3.title = 'Learners: phone access at home'
ch3.add_data(Reference(ws, min_col=2, min_row=18, max_row=21), titles_from_data=True)
ch3.set_categories(Reference(ws, min_col=1, min_row=19, max_row=21)); ch3.legend = None
ch3.series[0].graphicalProperties.solidFill = '1F4D3A'
ch3.height, ch3.width = 7, 12; ws.add_chart(ch3, 'H39')

wb.move_sheet('Summary', offset=-3)
wb.save(OUT); print('saved', OUT)
