"""Visual layer for the demo site: fonts, colours, the "reads like" meter and manuscript cards.

Idea: an editor's proof. Paper text is set like a manuscript (Literata), flagged sentences get a
highlighter, and one meter runs from human (teal) to machine (violet). Colours carry meaning:
teal = reads like a real paper, violet = reads like an LLM. Nothing here changes any logic.
"""
from html import escape
import re

import streamlit as st

HUMAN = "#0E7C72"      # teal: reads like a real paper
MACHINE = "#9B3D8F"    # violet: reads like an LLM
MID = "#C98A1B"        # amber: borderline
INK = "#1E2A44"
MUTED = "#5B6780"
LINE = "#D6DEEA"
PAPER = "#FFFFFF"
MIST = "#EEF3F9"
HIGHLIGHT = "#FFE27A"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&family=Literata:opsz,wght@7..72,400;7..72,600&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"], button, input, textarea, select {{
  font-family: 'Figtree', system-ui, sans-serif;
}}
[data-testid="stAppViewContainer"] {{ background: #F7F9FC; }}
h1, h2, h3, h4 {{ font-family: 'Figtree', system-ui, sans-serif !important; color: {INK}; letter-spacing: -0.01em; }}
h2 {{ font-weight: 800 !important; }}
h3, h4 {{ font-weight: 700 !important; }}

/* step bar: the segmented control */
[data-testid="stSegmentedControl"] button, div[data-testid="stButtonGroup"] button {{
  font-weight: 600; min-height: 3rem;
}}
/* tabs */
button[data-baseweb="tab"] p {{ font-weight: 600; font-size: 1rem; }}
div[data-baseweb="tab-highlight"] {{ background-color: {HUMAN}; height: 3px; }}
/* expanders and bordered containers: quieter edges */
[data-testid="stExpander"] details {{ border-color: {LINE}; border-radius: 10px; background: {PAPER}; }}
[data-testid="stExpander"] summary p {{ font-weight: 600; }}
/* metrics */
[data-testid="stMetric"] {{ background: {PAPER}; border: 1px solid {LINE}; border-radius: 10px; padding: .8rem 1rem; }}
[data-testid="stMetricValue"] {{ font-weight: 800; color: {INK}; }}
/* primary buttons */
button[kind="primary"] {{ font-weight: 700; }}
/* highlighter for flagged sentences (Streamlit's orange background) */
span[style*="background-color"].st-emotion-cache-orange, .rw-hl {{ background: {HIGHLIGHT}; }}

/* ---- custom components ---- */
h1 {{ font-size: clamp(2rem, 4vw, 2.9rem) !important; font-weight: 800 !important; line-height: 1.05 !important; }}
.rw-lede {{ font-size: 1.15rem; color: {MUTED}; max-width: 62ch; margin: -.4rem 0 .6rem; line-height: 1.5; }}
.rw-course {{ font-size: .85rem; color: {MUTED}; font-weight: 600; margin-bottom: .5rem; }}

.rw-meter {{ background: {PAPER}; border: 1px solid {LINE}; border-radius: 14px; padding: 1rem 1.25rem .9rem; }}
.rw-meter .cap {{ font-size: .9rem; font-weight: 700; color: {INK}; margin-bottom: 2.4rem; }}
.rw-meter .track {{ position: relative; height: 12px; border-radius: 99px;
  background: linear-gradient(90deg, {HUMAN} 0%, {HUMAN} 30%, {MID} 50%, {MACHINE} 70%, {MACHINE} 100%); }}
.rw-meter .mark {{ position: absolute; top: 50%; transform: translate(-50%, -50%); }}
.rw-meter .dot {{ display: block; width: 18px; height: 18px; border-radius: 50%; border: 3px solid {PAPER};
  box-shadow: 0 0 0 1.5px {INK}; background: {INK}; }}
.rw-meter .ref .dot {{ width: 12px; height: 12px; background: {PAPER}; border: 2px solid {INK}; box-shadow: none; }}
.rw-meter .lab {{ position: absolute; left: 50%; transform: translateX(-50%); white-space: nowrap;
  font-size: .82rem; font-weight: 700; color: {INK}; }}
.rw-meter .up .lab {{ bottom: 24px; }}
.rw-meter .down .lab {{ top: 22px; font-weight: 500; color: {MUTED}; }}
.rw-meter .ends {{ display: flex; justify-content: space-between; margin-top: 2.3rem; font-size: .8rem; color: {MUTED}; }}
.rw-meter .ends b.h {{ color: {HUMAN}; }} .rw-meter .ends b.m {{ color: {MACHINE}; }}

.rw-paper {{ background: {PAPER}; border: 1px solid {LINE}; border-top: 4px solid var(--edge, {INK});
  border-radius: 6px; padding: .9rem 1.1rem 1rem; margin-bottom: .6rem; }}
.rw-paper .head {{ display: flex; justify-content: space-between; align-items: baseline; gap: .6rem; margin-bottom: .55rem; }}
.rw-paper .title {{ font-weight: 700; font-size: .95rem; color: {INK}; }}
.rw-paper .body {{ font-family: 'Literata', Georgia, serif; font-size: 1.02rem; line-height: 1.68; color: #22283A; }}

.rw-chip {{ display: inline-block; font-weight: 800; font-size: .85rem; padding: .12rem .55rem; border-radius: 99px;
  color: #fff; background: var(--c, {INK}); white-space: nowrap; }}

.rw-guide {{ display: flex; gap: .9rem; background: {MIST}; border-left: 4px solid {HUMAN}; border-radius: 0 10px 10px 0;
  padding: .8rem 1.1rem; margin: .3rem 0 1rem; }}
.rw-guide .ico {{ font-size: 1.4rem; line-height: 1; }}
.rw-guide b {{ color: {INK}; }}
.rw-guide ol {{ margin: .25rem 0 0 1.1rem; padding: 0; color: #2B3550; line-height: 1.55; }}

.rw-versions {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: .7rem; margin: .4rem 0 .6rem; }}
.rw-version {{ background: {PAPER}; border: 1px solid {LINE}; border-radius: 10px; padding: .75rem .9rem; }}
.rw-version .n {{ display: inline-flex; width: 1.6rem; height: 1.6rem; border-radius: 50%; align-items: center;
  justify-content: center; font-weight: 800; font-size: .85rem; color: #fff; background: var(--c, {INK}); margin-right: .45rem; }}
.rw-version .t {{ font-weight: 700; color: {INK}; }}
.rw-version p {{ margin: .4rem 0 0; font-size: .88rem; color: {MUTED}; line-height: 1.45; }}

.rw-meter .legend {{ display: none; margin: .9rem 0 0; padding: 0; list-style: none; font-size: .85rem; color: {INK}; }}
.rw-meter .legend li {{ display: flex; align-items: center; gap: .5rem; margin: .2rem 0; }}
.rw-meter .legend i {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; border: 2px solid {INK}; }}
@media (max-width: 640px) {{
  .rw-meter .lab {{ display: none; }}
  .rw-meter .cap {{ margin-bottom: 1rem; }}
  .rw-meter .ends {{ margin-top: 1rem; }}
  .rw-meter .ends span:nth-child(2) {{ display: none; }}
  .rw-meter .legend {{ display: block; }}
}}
</style>
"""


def style():
    st.html(CSS)


def tone(score):
    """Colour for a 0-100 AI-likeness score."""
    if score is None:
        return INK
    return HUMAN if score < 40 else MID if score < 60 else MACHINE


def chip(score, text=None):
    label = text or f"{score:.0f}"
    return f'<span class="rw-chip" style="--c:{tone(score)}">{escape(label)}</span>'


def meter(points, caption="Where each text sits on our detector's scale"):
    """points: list of (label, score, kind) where kind is 'up' (our versions) or 'down' (reference)."""
    marks = []
    for label, score, kind in points:
        if score is None:
            continue
        s = max(0.0, min(100.0, float(score)))
        cls = "mark up" if kind == "up" else "mark down ref"
        dot = f'style="background:{tone(s)}"' if kind == "up" else ""
        marks.append(f'<div class="{cls}" style="left:{s:.1f}%"><span class="dot" {dot}></span>'
                     f'<span class="lab">{escape(label)} · {s:.0f}</span></div>')
    legend = "".join(
        f'<li><i style="background:{tone(sc) if k == "up" else "#fff"}"></i>{escape(lb)} · {float(sc):.0f}</li>'
        for lb, sc, k in sorted([p for p in points if p[1] is not None], key=lambda p: p[1]))
    st.html(f'''<div class="rw-meter" role="img" aria-label="{escape(caption)}">
  <div class="cap">{escape(caption)}</div>
  <div class="track">{''.join(marks)}</div>
  <ul class="legend">{legend}</ul>
  <div class="ends"><span><b class="h">0 · reads like a real paper</b></span><span>40-60 borderline</span>
  <span><b class="m">100 · reads like an LLM</b></span></div>
</div>''')


def paper(title, text, score=None, edge=None):
    """A manuscript-style card for a paragraph of paper text."""
    c = edge or (tone(score) if score is not None else INK)
    sc = chip(score) if score is not None else ""
    st.html(f'''<div class="rw-paper" style="--edge:{c}">
  <div class="head"><span class="title">{escape(title)}</span>{sc}</div>
  <div class="body">{escape(text)}</div>
</div>''')


def md_lite(text):
    """Escape, then allow **bold** and *italic* from the guide copy."""
    t = escape(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)


def guide(title, steps, icon="🧭"):
    items = "".join(f"<li>{md_lite(s)}</li>" for s in steps)
    st.html(f'''<div class="rw-guide"><div class="ico" aria-hidden="true">{icon}</div>
  <div><b>{escape(title)}</b><ol>{items}</ol></div></div>''')


def versions(cards):
    """cards: list of (number, name, description, colour)."""
    html = "".join(f'''<div class="rw-version" style="--c:{c}"><span class="n">{n}</span><span class="t">{escape(name)}</span>
  <p>{escape(desc)}</p></div>''' for n, name, desc, c in cards)
    st.html(f'<div class="rw-versions">{html}</div>')


def hero(title, lede, course):
    st.html(f'<div class="rw-course">{escape(course)}</div>')
    st.title(title, anchor=False)
    st.html(f'<p class="rw-lede">{escape(lede)}</p>')
