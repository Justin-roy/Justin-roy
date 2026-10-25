import json
import re
from urllib.parse import quote

TOTAL = 840
BADGES = {
    "LinkedIn": ("0A66C2", "linkedin"),
    "LeetCode": ("FFA116", "leetcode"),
    "Email": ("EA4335", "gmail"),
    "Portfolio": ("000000", "vercel"),
    "GitHub": ("181717", "github"),
}


def aspect(path):
    with open(path, encoding="utf-8") as f:
        head = f.read(600)
    w = float(re.search(r'width="([\d.]+)"', head).group(1))
    h = float(re.search(r'height="([\d.]+)"', head).group(1))
    return w / h


def badge(name, url):
    color, logo = BADGES.get(name, ("30363d", ""))
    src = f"https://img.shields.io/badge/{quote(name)}-{color}?style=for-the-badge" + (f"&logo={logo}&logoColor=white" if logo else "")
    return f'<a href="{url}"><img src="{src}" alt="{name}"/></a>'


with open("profile.json") as f:
    p = json.load(f)

a1, a2 = aspect("ascii-portrait.svg"), aspect("info-card.svg")
w1 = round(TOTAL * a1 / (a1 + a2))
w2 = TOTAL - w1
links = "\n".join(badge(n, u) for n, u in p["links"])
stack = ""
if p.get("icons"):
    stack = f'''
<img src="https://skillicons.dev/icons?i={",".join(p["icons"])}&theme=dark&perline=12" alt="Tech stack"/>

<br><br>
'''

readme = f'''<div align="center">

<img src="./contrib-heatmap.svg" width="850" alt="Contribution heatmap"/>

<img src="./ascii-portrait.svg" width="{w1}" alt="ASCII portrait"/>
<img src="./info-card.svg" width="{w2}" alt="About me"/>

<img src="./tagline.svg" width="850" alt="{p["tagline"].replace("&", "&amp;")}"/>
{stack}
{links}

</div>
'''
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
print(f"README.md: portrait {w1}px, card {w2}px")
