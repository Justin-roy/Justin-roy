import json

from common import ACCENT, BAR_H, DIM, GREEN, INK, STATIC, esc, panel, write

with open("profile.json") as f:
    p = json.load(f)

LINE, PAD, CW = 21, 24, 7.8
head = f'{p["user"]}@{p["host"]}'
key_w = max(len(k) for k, _ in p["lines"]) + 2
widest = max(len(head), *(key_w + len(v) for _, v in p["lines"]))
W = int(PAD * 2 + widest * CW) + 10
rows = len(p["lines"]) + 4
H = BAR_H + PAD + rows * LINE + PAD - 4


def line(i, inner):
    y = BAR_H + PAD + 10 + i * LINE
    style = "" if STATIC else f' style="animation-delay:{0.15 + i * 0.08:.2f}s"'
    return f'<text class="l" x="{PAD}" y="{y}" font-size="13"{style}>{inner}</text>'


out = [
    line(0, f'<tspan fill="{GREEN}" font-weight="bold">{esc(p["user"])}</tspan><tspan fill="{INK}">@</tspan><tspan fill="{GREEN}" font-weight="bold">{esc(p["host"])}</tspan>'),
    line(1, f'<tspan fill="{DIM}">{"-" * len(head)}</tspan>'),
]
for i, (k, v) in enumerate(p["lines"]):
    out.append(line(i + 2, f'<tspan fill="{ACCENT}" font-weight="bold">{esc(k)}</tspan><tspan fill="{INK}" x="{PAD + key_w * CW}">{esc(v)}</tspan>'))

i = len(p["lines"]) + 3
y = BAR_H + PAD + i * LINE - 2
colors = ["#484f58", "#ff7b72", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"]
style = "" if STATIC else f' style="animation-delay:{0.15 + i * 0.08:.2f}s"'
out.append(f'<g class="l"{style}>' + "".join(
    f'<rect x="{PAD + j * 22}" y="{y}" width="20" height="12" fill="{c}"/>' for j, c in enumerate(colors)
) + "</g>")

css = "" if STATIC else ".l{opacity:0;animation:f .4s ease-out forwards}@keyframes f{to{opacity:1}}"
write("info-card.svg", panel(W, H, f"{head} — neofetch", "\n".join(out), css))
