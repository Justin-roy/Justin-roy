import json
import re

TOTAL = 850


def aspect(path):
    with open(path, encoding="utf-8") as f:
        head = f.read(600)
    w = float(re.search(r'width="([\d.]+)"', head).group(1))
    h = float(re.search(r'height="([\d.]+)"', head).group(1))
    return w / h


with open("profile.json") as f:
    p = json.load(f)

a1, a2 = aspect("ascii-portrait.svg"), aspect("info-card.svg")
w1 = round(TOTAL * a1 / (a1 + a2))
w2 = TOTAL - w1
links = " &nbsp;·&nbsp; ".join(f'<a href="{u}">{n}</a>' for n, u in p["links"])

readme = f'''<div align="center">

<img src="./contrib-heatmap.svg" width="{TOTAL}" alt="Contribution heatmap"/>

<br>

<table>
<tr>
<td valign="top"><img src="./ascii-portrait.svg" width="{w1}" alt="ASCII portrait"/></td>
<td valign="top"><img src="./info-card.svg" width="{w2}" alt="About me"/></td>
</tr>
</table>

<br>

<h3>{p["tagline"].replace("&", "&amp;")}</h3>

{links}

</div>
'''
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
print(f"README.md: portrait {w1}px, card {w2}px")
