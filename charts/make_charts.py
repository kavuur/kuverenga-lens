"""Charts for the Kuverenga Lens report, poster and slides. Run: python make_charts.py"""
import csv, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
K = os.path.dirname(HERE)
INK, INK2, MUTED, GRID, SURF = '#1B1F1D', '#52514e', '#8a8a83', '#e6e3da', '#ffffff'
S1, S2, S3 = '#2a78d6', '#eb6834', '#1baf7a'          # validated categorical slots 1-3
BASE = '#a9a9a2'                                        # neutral baseline
BOARD, SUN = '#1F4D3A', '#F2B33D'

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 11, 'text.color': INK, 'axes.labelcolor': INK2,
    'axes.edgecolor': GRID, 'xtick.color': INK2, 'ytick.color': INK2, 'axes.spines.top': False,
    'axes.spines.right': False, 'axes.spines.left': False, 'axes.grid': True, 'grid.color': GRID,
    'grid.linewidth': 0.8, 'axes.axisbelow': True, 'figure.facecolor': SURF, 'axes.facecolor': SURF,
    'savefig.dpi': 200, 'savefig.bbox': 'tight', 'savefig.pad_inches': 0.25,
})

def title(ax, t, sub=None):
    ax.set_title(t, loc='left', fontsize=14, fontweight='bold', color=INK, pad=26 if sub else 10)
    if sub: ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=10, color=INK2, va='bottom')

def read(path):
    with open(path) as f: return list(csv.DictReader(f))

COND = [('1_good', 'Good photo'), ('2_angle', 'At an angle'), ('3_shake', 'Camera shake'), ('4_dim', 'Dim room'),
        ('5_glare', 'Window glare'), ('6_far', 'Back of class'), ('7_dusty', 'Dusty board')]

def mean_by(rows, pipeline):
    out = {}
    for c, _ in COND:
        v = [float(r['word_accuracy_pct']) for r in rows if r['condition'] == c and r['pipeline'] == pipeline]
        out[c] = sum(v) / len(v)
    return out

v1 = read(os.path.join(K, 'testing', 'accuracy_results_v1.csv'))
v2 = read(os.path.join(K, 'testing', 'accuracy_results_v2.csv'))
raw, c1, c2 = mean_by(v2, 'raw photo'), mean_by(v1, 'with clean-up'), mean_by(v2, 'with clean-up')

# ---- Figure: accuracy by condition (grouped horizontal bars) ----
fig, ax = plt.subplots(figsize=(9, 6.2))
labels = [n for _, n in COND][::-1]
keys = [c for c, _ in COND][::-1]
h = 0.25
for i, (series, color, name) in enumerate([(raw, BASE, 'Raw photo (no clean-up)'), (c1, S2, 'Prototype v1 clean-up'), (c2, S1, 'Prototype v2 clean-up')]):
    ys = [k + (1 - i) * (h + 0.02) for k in range(len(keys))]
    vals = [series[k] for k in keys]
    ax.barh(ys, vals, height=h, color=color, label=name, edgecolor=SURF, linewidth=1.5)
    if i == 2:
        for y, v in zip(ys, vals): ax.text(v + 1, y, f'{v:.0f}%', va='center', fontsize=9.5, color=INK, fontweight='bold')
    if i == 1:
        for y, v in zip(ys, vals):
            if v < 80: ax.text(v + 1, y, f'{v:.0f}%', va='center', fontsize=9, color=INK2)
ax.set_yticks(range(len(keys))); ax.set_yticklabels(labels, fontsize=11)
ax.set_xlim(0, 108); ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
ax.grid(axis='y', visible=False); ax.tick_params(axis='y', length=0)
ax.set_xlabel('Words read correctly (average of English and ChiShona boards)')
title(ax, 'Word accuracy by classroom condition', '14 simulated chalkboard photos, each read three ways')
ax.legend(loc='lower center', bbox_to_anchor=(0.45, -0.2), ncol=3, frameon=False, fontsize=10)
fig.savefig(os.path.join(HERE, 'fig_accuracy_by_condition.png')); plt.close(fig)

# ---- Figure: overall averages (stat-style bars) ----
def avg(d): return sum(d.values()) / len(d)
fig, ax = plt.subplots(figsize=(7, 3.4))
names = ['Raw photo', 'Prototype v1', 'Prototype v2']
vals = [avg(raw), avg(c1), avg(c2)]
cols = [BASE, S2, S1]
ax.barh(names[::-1], vals[::-1], color=cols[::-1], height=0.55, edgecolor=SURF, linewidth=1.5)
for i, v in enumerate(vals[::-1]): ax.text(v + 1, i, f'{v:.1f}%', va='center', fontweight='bold', fontsize=11)
ax.set_xlim(0, 110); ax.set_xticks([0, 50, 100]); ax.set_xticklabels(['0%', '50%', '100%'])
ax.grid(axis='y', visible=False); ax.tick_params(axis='y', length=0)
title(ax, 'Average word accuracy, all 14 test photos')
fig.savefig(os.path.join(HERE, 'fig_accuracy_overall.png')); plt.close(fig)

# ---- Figure: development cost breakdown ----
COSTS = [  # (item, USD) - estimates; edit to match real spending
    ('Internet data for development & testing', 20),
    ('Low-cost Android test phone (second-hand)', 60),
    ('Printing report, poster & learner guides', 25),
    ('Teacher demonstration session (transport, refreshments)', 30),
    ('Web hosting (GitHub Pages)', 0),
    ('OCR engine, font & tools (open source)', 0),
]
fig, ax = plt.subplots(figsize=(9, 3.9))
items = [c[0] for c in COSTS][::-1]; usd = [c[1] for c in COSTS][::-1]
ax.barh(items, usd, color=[S1 if u else GRID for u in usd], height=0.6, edgecolor=SURF, linewidth=1.5)
for i, u in enumerate(usd): ax.text(u + 1, i, f'${u}' if u else '$0 (free)', va='center', fontsize=10, fontweight='bold' if u else 'normal', color=INK if u else INK2)
ax.set_xlim(0, 75); ax.grid(axis='y', visible=False); ax.tick_params(axis='y', length=0)
ax.set_xlabel('US dollars (estimated)')
title(ax, f'Prototype development cost: ${sum(usd)} in total', 'Free, open-source tools keep the software itself at zero cost')
fig.savefig(os.path.join(HERE, 'fig_costs.png')); plt.close(fig)

# ---- Figure: break-even for the school support plan ----
fig, ax = plt.subplots(figsize=(8, 4.3))
schools = list(range(0, 21))
fixed, per_school_cost, fee = 135 + 120, 10, 30      # dev cost + yearly upkeep; cost & fee per school per year
cost = [fixed + per_school_cost * s for s in schools]
income = [fee * s for s in schools]
ax.plot(schools, cost, color=S2, linewidth=2, label='Yearly cost')
ax.plot(schools, income, color=S1, linewidth=2, label='Yearly income from schools')
be = fixed / (fee - per_school_cost)
ax.axvline(be, color=MUTED, linewidth=1, linestyle=(0, (4, 3)))
ax.text(be + 0.4, 120, f'Break-even ≈ {be:.0f} schools', color=INK2, fontsize=10)
ax.text(20.2, cost[-1], 'Cost', color=INK, va='center', fontsize=10); ax.text(20.2, income[-1], 'Income', color=INK, va='center', fontsize=10)
ax.set_xlim(0, 22); ax.set_ylim(0, 650); ax.set_xticks([0, 5, 10, 15, 20])
ax.set_xlabel('Schools using the support plan'); ax.set_ylabel('US dollars per year')
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f'${v:.0f}'))
title(ax, 'Break-even: free for learners, schools pay $30 a year for training and support', 'Estimates for planning')
ax.legend(loc='upper left', frameon=False, fontsize=10)
fig.savefig(os.path.join(HERE, 'fig_break_even.png')); plt.close(fig)

# ---- Figure: development timeline (Gantt, by week) ----
PHASES = [  # (phase, start week, length in weeks, colour)
    ('1. Needs assessment (questionnaires, observation)', 1, 2, S3),
    ('2. Define problem & write design brief', 2, 1, S3),
    ('3. Ideas & paper sketches of screens', 3, 1, S1),
    ('4. Build prototype v1 (camera, OCR, reader)', 3, 2, S1),
    ('5. Test v1 with 14 board photos', 5, 1, S2),
    ('6. Improve to v2 (glare fix, syllables, Shona)', 5, 1, S1),
    ('7. Retest v2, screenshots & demo video', 6, 1, S2),
    ('8. Trial with learners & teachers', 6, 2, S2),
    ('9. Report, poster & presentation', 7, 2, S3),
]
fig, ax = plt.subplots(figsize=(10, 4.6))
for i, (name, start, length, col) in enumerate(PHASES):
    y = len(PHASES) - 1 - i
    ax.add_patch(FancyBboxPatch((start - 0.5 + 0.06, y - 0.3), length - 0.12, 0.6, boxstyle='round,pad=0,rounding_size=0.12',
                                facecolor=col, edgecolor='none'))
ax.set_yticks(range(len(PHASES))); ax.set_yticklabels([p[0] for p in PHASES][::-1], fontsize=10)
ax.set_xlim(0.5, 8.5); ax.set_ylim(-0.7, len(PHASES) - 0.3)
ax.set_xticks(range(1, 9)); ax.set_xticklabels([f'Week {w}' for w in range(1, 9)], fontsize=9.5)
ax.xaxis.tick_top(); ax.grid(axis='y', visible=False); ax.tick_params(length=0)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=S3, label='Research & writing'), Patch(color=S1, label='Design & build'), Patch(color=S2, label='Testing')],
          loc='lower center', bbox_to_anchor=(0.4, -0.16), ncol=3, frameon=False, fontsize=10)
ax.set_title('Project timeline', loc='left', fontsize=14, fontweight='bold', pad=30)
fig.savefig(os.path.join(HERE, 'fig_timeline.png')); plt.close(fig)

print('charts saved in', HERE)
for c, n in COND: print(f'{n:15s} raw {raw[c]:5.1f}  v1 {c1[c]:5.1f}  v2 {c2[c]:5.1f}')
print(f"overall raw {avg(raw):.1f} v1 {avg(c1):.1f} v2 {avg(c2):.1f}")
