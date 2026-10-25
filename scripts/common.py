import os
from xml.sax.saxutils import escape

BG = "#0d1117"
BORDER = "#21262d"
BAR = "#161b22"
INK = "#c9d1d9"
DIM = "#8b949e"
ACCENT = "#58a6ff"
GREEN = "#3fb950"
LEVELS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace"
BAR_H = 30
STATIC = os.environ.get("STATIC") == "1"


def esc(s):
    return escape(str(s), {'"': "&quot;"})


def panel(width, height, title, body, style=""):
    dots = "".join(
        f'<circle cx="{18 + i * 16}" cy="{BAR_H / 2}" r="5" fill="{c}"/>'
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"])
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="{esc(FONT)}">
<style>{style}</style>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<path d="M0.5 {BAR_H} V10.5 a10 10 0 0 1 10 -10 H{width - 10.5} a10 10 0 0 1 10 10 V{BAR_H} Z" fill="{BAR}"/>
<line x1="0.5" y1="{BAR_H}" x2="{width - 0.5}" y2="{BAR_H}" stroke="{BORDER}"/>
{dots}
<text x="{width / 2}" y="{BAR_H / 2 + 4}" text-anchor="middle" font-size="12" fill="{DIM}">{esc(title)}</text>
{body}
</svg>
'''


def write(path, svg):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {path}")
