"""SP-01-T2 (NTT-46): rendering spike, hand-drawn SVG.

Throwaway code. Draws the same 7-note melody as NTT-45 by generating SVG
ourselves (no music libraries) to see how much work real notation takes.

    python spikes/svg/handdrawn_spike.py

Output: spikes/svg/out/handdrawn.svg and out/index.html
"""
import time
from pathlib import Path

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

# Same data as spikes/music21/render_spike.py (shaped like models.Note)
NOTES = [
    {"position": 1, "pitch": "C", "octave": 4, "duration": "quarter", "accidental": None, "is_rest": False},
    {"position": 2, "pitch": "E", "octave": 4, "duration": "quarter", "accidental": None, "is_rest": False},
    {"position": 3, "pitch": "G", "octave": 4, "duration": "half", "accidental": None, "is_rest": False},
    {"position": 4, "pitch": None, "octave": None, "duration": "quarter", "accidental": None, "is_rest": True},
    {"position": 5, "pitch": "F", "octave": 4, "duration": "eighth", "accidental": "sharp", "is_rest": False},
    {"position": 6, "pitch": "G", "octave": 4, "duration": "eighth", "accidental": None, "is_rest": False},
    {"position": 7, "pitch": "C", "octave": 5, "duration": "half", "accidental": None, "is_rest": False},
]

BEATS = {"whole": 4, "half": 2, "quarter": 1, "eighth": 0.5}
STEPS = "CDEFGAB"
GAP = 10                    # space between staff lines
TOP = 40                    # y of the top staff line (F5)
LEFT = 20
NOTE_X0 = 110               # first note x
SPACING = 55                # horizontal space per note (fixed, not proportional)
BEATS_PER_BAR = 4


def staff_step(pitch, octave):
    """Diatonic steps above E4 (the bottom line). E4=0, F4=1, G4=2, ... F5=8."""
    return (octave * 7 + STEPS.index(pitch)) - (4 * 7 + STEPS.index("E"))


def y_for(step):
    bottom = TOP + 4 * GAP
    return bottom - step * GAP / 2


def draw_note(n, x):
    parts = []
    step = staff_step(n["pitch"], n["octave"])
    y = y_for(step)

    # ledger lines below (C4 = step -2) and above (A5 = step 10)
    for s in range(-2, step - 1, -2) if step <= -2 else []:
        parts.append(f'<line x1="{x-11}" x2="{x+11}" y1="{y_for(s)}" y2="{y_for(s)}" stroke="#000" stroke-width="1.2"/>')
    for s in range(10, step + 1, 2) if step >= 10 else []:
        parts.append(f'<line x1="{x-11}" x2="{x+11}" y1="{y_for(s)}" y2="{y_for(s)}" stroke="#000" stroke-width="1.2"/>')

    # notehead: filled for quarter/eighth, hollow for half/whole
    filled = n["duration"] in ("quarter", "eighth")
    fill = "#000" if filled else "#fff"
    parts.append(f'<ellipse cx="{x}" cy="{y}" rx="6.5" ry="4.6" transform="rotate(-20 {x} {y})" '
                 f'fill="{fill}" stroke="#000" stroke-width="1.6"/>')

    # stem: up if below the middle line (B4 = step 4), down otherwise
    if n["duration"] != "whole":
        if step < 4:
            sx, y1, y2 = x + 6, y, y - 35
        else:
            sx, y1, y2 = x - 6, y, y + 35
        parts.append(f'<line x1="{sx}" x2="{sx}" y1="{y1}" y2="{y2}" stroke="#000" stroke-width="1.4"/>')
        # flag for eighth notes (no beaming: that needs knowledge of neighbouring notes)
        if n["duration"] == "eighth":
            d = 1 if step < 4 else -1
            parts.append(f'<path d="M{sx},{y2} q 12,{10*d} 8,{24*d}" fill="none" stroke="#000" stroke-width="2"/>')

    if n["accidental"] == "sharp":
        parts.append(f'<text x="{x-20}" y="{y+5}" font-size="16" font-family="serif">&#9839;</text>')
    elif n["accidental"] == "flat":
        parts.append(f'<text x="{x-18}" y="{y+5}" font-size="16" font-family="serif">&#9837;</text>')
    return parts


def draw_rest(n, x):
    # Quarter rest drawn as a simple zig-zag; other rest types not handled
    y = TOP + GAP
    return [f'<path d="M{x-3},{y} l6,7 l-5,6 l6,7 l-7,-2 l4,7" fill="none" stroke="#000" stroke-width="2.2"/>']


def render(notes):
    width = NOTE_X0 + SPACING * (len(notes) + 1)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="140" viewBox="0 0 {width} 140">',
             '<rect width="100%" height="100%" fill="#fff"/>']
    for i in range(5):
        y = TOP + i * GAP
        parts.append(f'<line x1="{LEFT}" x2="{width-20}" y1="{y}" y2="{y}" stroke="#000" stroke-width="1"/>')
    # clef and time signature: Unicode glyphs, look depends on the viewer's fonts
    parts.append(f'<text x="{LEFT+2}" y="{TOP+38}" font-size="58" font-family="serif">&#119070;</text>')
    parts.append(f'<text x="{LEFT+48}" y="{TOP+18}" font-size="22" font-weight="bold" font-family="serif">4</text>')
    parts.append(f'<text x="{LEFT+48}" y="{TOP+38}" font-size="22" font-weight="bold" font-family="serif">4</text>')

    x, beats = NOTE_X0, 0
    for n in sorted(notes, key=lambda n: n["position"]):
        parts += draw_rest(n, x) if n["is_rest"] else draw_note(n, x)
        beats += BEATS[n["duration"]]
        x += SPACING
        if beats % BEATS_PER_BAR == 0:
            bx = x - SPACING / 2
            parts.append(f'<line x1="{bx}" x2="{bx}" y1="{TOP}" y2="{TOP+4*GAP}" stroke="#000" stroke-width="1.2"/>')
    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    start = time.perf_counter()
    svg = render(NOTES)
    secs = time.perf_counter() - start
    (OUT / "handdrawn.svg").write_text(svg)

    verovio = Path(__file__).parent.parent / "music21" / "out" / "verovio.svg"
    compare = (f'<h2>Verovio (NTT-45)</h2><img src="../../music21/out/verovio.svg" style="max-width:100%">'
               if verovio.exists() else "<p>Run spikes/music21/render_spike.py to compare with Verovio.</p>")
    (OUT / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><title>NTT-46 spike</title>"
        "<body style='font-family:sans-serif;max-width:900px;margin:2rem auto'>"
        f"<h1>NTT-46 hand-drawn SVG</h1><p>Rendered in {secs*1000:.2f} ms. "
        f"Code: {sum(1 for _ in open(__file__))} lines.</p>"
        '<h2>Hand-drawn</h2><img src="handdrawn.svg">' + compare)
    print(f"Rendered in {secs*1000:.2f} ms -> {OUT / 'handdrawn.svg'}")
    print(f"Open {OUT / 'index.html'} to compare.")
