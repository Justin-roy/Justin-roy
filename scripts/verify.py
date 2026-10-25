import re
import sys
import xml.etree.ElementTree as ET

NS = "{http://www.w3.org/2000/svg}"
errors = []

for path in ["contrib-heatmap.svg", "ascii-portrait.svg", "info-card.svg"]:
    raw = open(path, encoding="utf-8").read()
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        errors.append(f"{path}: invalid XML ({e})")
        continue
    if "<script" in raw.lower():
        errors.append(f"{path}: contains <script>")
    if re.search(r'(href|src)\s*=\s*"(https?:)?//|url\(\s*[\'"]?https?:|@import', raw):
        errors.append(f"{path}: external reference")
    W, H = float(root.get("width")), float(root.get("height"))
    for el in root.iter():
        tag = el.tag.replace(NS, "")
        if tag == "rect" and el.get("x") is not None:
            x, y = float(el.get("x")), float(el.get("y"))
            w, h = float(el.get("width")), float(el.get("height"))
            if x < 0 or y < 0 or x + max(w, 0) > W + 0.01 or y + h > H + 0.01:
                if not any(a.get("attributeName") == "width" for a in el):
                    errors.append(f"{path}: rect at ({x},{y}) {w}x{h} exceeds {W}x{H}")
        if tag == "text":
            x, y = float(el.get("x", 0)), float(el.get("y", 0))
            tl = el.get("textLength")
            if tl and x + float(tl) > W:
                errors.append(f"{path}: text run at x={x} ends past {W}")
            if x < 0 or x > W or y < 0 or y > H:
                errors.append(f"{path}: text at ({x},{y}) outside {W}x{H}")
        if tag == "animate":
            to = el.get("to")
            if to and float(to) > W:
                errors.append(f"{path}: animation width {to} exceeds panel")
    print(f"ok {path} ({W:.0f}x{H:.0f})")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("all checks passed")
