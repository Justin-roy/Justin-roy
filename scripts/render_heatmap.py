import datetime as dt
import json
import os

from common import ACCENT, BAR_H, DIM, GREEN, INK, LEVELS, STATIC, esc, panel, write

W, H = 850, 236
CELL, STEP = 11, 15
X0, Y0 = 46, 96

data = None
if os.path.exists("data/contributions.json"):
    with open("data/contributions.json") as f:
        data = json.load(f)

if data:
    user = data["user"]
    days = data["days"]
else:
    user = os.environ.get("GITHUB_USERNAME", "you")
    today = dt.date.today()
    days = [{"date": (today - dt.timedelta(days=364 - i)).isoformat(), "level": 0, "count": 0} for i in range(365)]

first = dt.date.fromisoformat(days[0]["date"])
offset = (first.weekday() + 1) % 7

cells, months, last_month = [], [], None
for i, d in enumerate(days):
    idx = i + offset
    col, row = divmod(idx, 7)
    x, y = X0 + col * STEP, Y0 + row * STEP
    date = dt.date.fromisoformat(d["date"])
    if (row == 0 or i == 0) and date.month != last_month:
        if i == 0 or col < 52:
            months.append(f'<text x="{x}" y="{Y0 - 8}" font-size="10" fill="{DIM}">{date.strftime("%b")}</text>')
        last_month = date.month
    style = "" if STATIC else f' style="animation-delay:{(col + row) * 0.012:.3f}s"'
    cells.append(
        f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{LEVELS[d["level"]]}"{style}>'
        f'<title>{d["count"]} on {d["date"]}</title></rect>'
    )

if len(months) > 1:
    xs = [float(m.split('x="')[1].split('"')[0]) for m in months[:2]]
    if xs[1] - xs[0] < 3 * STEP:
        months.pop(0)

weekdays = "".join(
    f'<text x="{X0 - 8}" y="{Y0 + r * STEP + 9}" font-size="10" fill="{DIM}" text-anchor="end">{n}</text>'
    for r, n in [(1, "Mon"), (3, "Wed"), (5, "Fri")]
)

lx = W - 26 - 5 * STEP - 30
legend = f'<text x="{lx - 6}" y="{H - 21}" font-size="10" fill="{DIM}" text-anchor="end">Less</text>'
legend += "".join(
    f'<rect x="{lx + i * STEP}" y="{H - 30}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>' for i, c in enumerate(LEVELS)
)
legend += f'<text x="{lx + 5 * STEP + 2}" y="{H - 21}" font-size="10" fill="{DIM}">More</text>'

if data:
    counts = [d["count"] for d in days]
    total = sum(counts)
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    tail = counts[:-1] if counts[-1] == 0 else counts
    current = 0
    for c in reversed(tail):
        if not c:
            break
        current += 1
    best = max(days, key=lambda d: d["count"])
    parts = [
        (f"{total:,}", "contributions"),
        (f"{longest}d", "longest streak"),
        (f"{current}d", "current streak"),
        (f"{best['count']}", f"best day ({best['date']})"),
    ]
    footer = "".join(
        f'<tspan fill="{INK}" font-weight="bold">{esc(v)}</tspan><tspan fill="{DIM}"> {esc(k)}</tspan>'
        + ('<tspan fill="#30363d">   |   </tspan>' if i < len(parts) - 1 else "")
        for i, (v, k) in enumerate(parts)
    )
else:
    footer = f'<tspan fill="{DIM}">Waiting for the first sync. Run the "heatmap" workflow in the Actions tab.</tspan>'

body = f'''<text x="22" y="{BAR_H + 26}" font-size="13"><tspan fill="{GREEN}">{esc(user)}@github</tspan><tspan fill="{DIM}">:~$ </tspan><tspan fill="{INK}">contributions --last-year</tspan></text>
{"".join(months)}{weekdays}
{"".join(cells)}
<text x="22" y="{H - 21}" font-size="11">{footer}</text>
{legend}'''

style = "" if STATIC else ".c{opacity:0;animation:f .35s ease-out forwards}@keyframes f{to{opacity:1}}"
write("contrib-heatmap.svg", panel(W, H, f"{user} — activity", body, style))
