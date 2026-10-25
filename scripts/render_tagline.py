import json

from common import ACCENT, DIM, GREEN, INK, STATIC, esc, write

with open("profile.json") as f:
    p = json.load(f)

W, H = 850, 56
FS, CW = 15, 9.0
prompt = "$ echo"
text = p["tagline"]
px = (W - (len(prompt) + 1 + len(text)) * CW) / 2
tx = px + (len(prompt) + 1) * CW
y = H / 2 + 5
tw = len(text) * CW

body = [
    f'<text x="{px:.1f}" y="{y}" font-size="{FS}" textLength="{len(prompt) * CW:.1f}" lengthAdjust="spacingAndGlyphs">'
    f'<tspan fill="{GREEN}">$</tspan><tspan fill="{DIM}"> echo</tspan></text>'
]
line = f'<text x="{tx:.1f}" y="{y}" font-size="{FS}" fill="{INK}" textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs">{esc(text)}</text>'

if STATIC:
    body.append(line)
    body.append(f'<rect x="{tx + tw + 2:.1f}" y="{y - FS + 2}" width="{CW:.1f}" height="{FS + 2}" fill="{ACCENT}"/>')
else:
    steps = ";".join(f"{i * CW:.1f}" for i in range(len(text) + 1))
    dur = len(text) * 0.045
    body.append(
        f'<defs><clipPath id="t"><rect x="{tx:.1f}" y="0" width="0" height="{H}">'
        f'<animate attributeName="width" values="{steps}" calcMode="discrete" begin="0.6s" dur="{dur:.2f}s" fill="freeze"/>'
        f"</rect></clipPath></defs>"
    )
    body.append(f'<g clip-path="url(#t)">{line}</g>')
    xs = ";".join(f"{tx + i * CW + 2:.1f}" for i in range(len(text) + 1))
    body.append(
        f'<rect x="{tx + 2:.1f}" y="{y - FS + 2}" width="{CW:.1f}" height="{FS + 2}" fill="{ACCENT}">'
        f'<animate attributeName="x" values="{xs}" calcMode="discrete" begin="0.6s" dur="{dur:.2f}s" fill="freeze"/>'
        f'<animate attributeName="opacity" values="1;0;1" keyTimes="0;0.5;1" calcMode="discrete" begin="{0.6 + dur:.2f}s" dur="1s" repeatCount="indefinite"/>'
        f"</rect>"
    )

FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace"
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{esc(FONT)}">
{"".join(body)}
</svg>
'''
write("tagline.svg", svg)
