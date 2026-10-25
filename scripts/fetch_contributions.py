import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

user = os.environ.get("GITHUB_USERNAME") or (sys.argv[1] if len(sys.argv) > 1 else None)
if not user:
    sys.exit("set GITHUB_USERNAME or pass a username")

r = requests.get(
    f"https://github.com/users/{user}/contributions",
    headers={"User-Agent": "profile-heatmap"},
    timeout=30,
)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")

tips = {}
for tip in soup.find_all("tool-tip"):
    m = re.match(r"\s*(\d+|No)\s+contribution", tip.get_text())
    if tip.get("for") and m:
        tips[tip["for"]] = 0 if m.group(1) == "No" else int(m.group(1))

days = []
for td in soup.select("td[data-date]"):
    days.append({
        "date": td["data-date"],
        "level": int(td.get("data-level", 0)),
        "count": tips.get(td.get("id"), 0),
    })
days.sort(key=lambda d: d["date"])
if not days:
    sys.exit("no contribution cells found; GitHub markup may have changed")

os.makedirs("data", exist_ok=True)
with open("data/contributions.json", "w") as f:
    json.dump({"user": user, "days": days}, f)
print(f"{len(days)} days, {sum(d['count'] for d in days)} contributions")
