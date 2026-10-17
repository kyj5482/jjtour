"""Assemble jjtour/index.html from src/template.html + data files."""
import json, os

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
read = lambda p: open(os.path.join(here, p), encoding="utf-8").read()

html = read("template.html")
credits = json.load(open(os.path.join(root, "credits.json"), encoding="utf-8"))
html = html.replace("/*__CREDITS__*/", json.dumps(credits, ensure_ascii=False))
html = html.replace("/*__GEO__*/", read("geo.js"))
html = html.replace("/*__DAYS__*/", read("days.js"))
html = html.replace("/*__MEALS__*/", read("meals.js"))
html = html.replace("/*__TIPS__*/", read("tips.js"))
html = html.replace("/*__ENGLISH__*/", read("english.js"))
import base64
faces = []
for name, w in [("Regular",400),("SemiBold",600),("Bold",700),("ExtraBold",800)]:
    data = base64.b64encode(open(os.path.join(here, f"Pretendard-{name}.subset.woff2"),"rb").read()).decode()
    faces.append(f'@font-face{{font-family:"Pretendard";font-weight:{w};font-style:normal;font-display:swap;src:url(data:font/woff2;base64,{data}) format("woff2")}}')
html = html.replace("/*__FONTS__*/", "\n".join(faces))
open(os.path.join(root, "index.html"), "w", encoding="utf-8").write(html)
print("built", len(html), "bytes")
