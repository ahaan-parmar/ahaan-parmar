"""Build assets/langs.svg: an animated donut of the languages across my own (non-fork) repos."""
import json, math, os, urllib.request

USER = "ahaan-parmar"
HIDE = {"TypeScript", "HTML", "CSS", "Jupyter Notebook"}
TOP = 6
COLORS = {  # GitHub linguist colours
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Go": "#00ADD8",
    "C": "#555555", "C++": "#f34b7d", "Java": "#b07219", "Rust": "#dea584", "Shell": "#89e051",
    "PowerShell": "#012456", "PHP": "#4F5D95", "Ruby": "#701516", "Dockerfile": "#384d54",
    "HCL": "#844FBA", "Kotlin": "#A97BFF", "Swift": "#F05138", "C#": "#178600", "Lua": "#000080",
    "Assembly": "#6E4C13", "Solidity": "#AA6746", "Dart": "#00B4AB", "Vue": "#41b883",
}


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


totals = {}
for repo in get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner"):
    if repo["fork"]:
        continue
    for lang, n in get(repo["languages_url"]).items():
        if lang not in HIDE:
            totals[lang] = totals.get(lang, 0) + n

langs = sorted(totals.items(), key=lambda kv: -kv[1])[:TOP]
total = sum(n for _, n in langs)
langs = [(name, n / total) for name, n in langs]
langs = [(name, s) for name, s in langs if s >= 0.003]
total = sum(s for _, s in langs)
langs = [(name, s / total) for name, s in langs]

W, H = 300, 195
CX, CY, R, SW = W / 2, 98, 66, 20
CIRC = 2 * math.pi * R
GAP = 3 if len(langs) > 1 else 0
PER = 2.4                     # seconds each language stays in the centre
CYCLE = PER * len(langs)
DRAW = 0.5                    # seconds to draw each slice

segs, labels, css = [], [], []
start = 0.0
for i, (name, share) in enumerate(langs):
    col = COLORS.get(name, "#a6adc8")
    seg = max(share * CIRC - GAP, 0.5)
    t = 0.2 + i * DRAW * 0.6
    segs.append(
        f'<circle class="s s{i}" cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="{col}" stroke-width="{SW}" '
        f'stroke-dasharray="0 {CIRC:.2f}" stroke-dashoffset="{-start:.2f}" transform="rotate(-90 {CX} {CY})">'
        f'<animate attributeName="stroke-dasharray" from="0 {CIRC:.2f}" to="{seg:.2f} {CIRC:.2f}" '
        f'begin="{t:.2f}s" dur="{DRAW}s" fill="freeze" calcMode="spline" keySplines=".25 .1 .25 1"/></circle>')
    start += share * CIRC
    delay = 1.4 + i * PER
    labels.append(
        f'<g class="c" style="animation-delay:{delay:.2f}s">'
        f'<text x="{CX}" y="{CY + 4}" class="pct" fill="{col}">{(f"{share * 100:.0f}" if share >= .1 else f"{share * 100:.1f}")}%</text>'
        f'<text x="{CX}" y="{CY + 24}" class="nm">{name}</text></g>')
    css.append(f".s{i}{{animation:pop {CYCLE}s {delay:.2f}s infinite}}")

on = PER / CYCLE * 100
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Most used languages: {", ".join(f"{n} {s * 100:.0f}%" for n, s in langs)}">
  <title>Most used languages</title>
  <style>
    text{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,'Helvetica Neue',Arial,sans-serif;text-anchor:middle}}
    .pct{{font-size:26px;font-weight:700}}
    .nm{{font-size:13px;font-weight:500;fill:#a6adc8}}
    .c{{opacity:0;animation:cyc {CYCLE}s infinite}}
    @keyframes cyc{{0%{{opacity:0}}{on * .1:.2f}%{{opacity:1}}{on * .9:.2f}%{{opacity:1}}{on:.2f}%,100%{{opacity:0}}}}
    @keyframes pop{{0%,{on:.2f}%,100%{{stroke-width:{SW}px}}{on * .1:.2f}%,{on * .9:.2f}%{{stroke-width:{SW + 8}px}}}}
    {"".join(css)}
  </style>
  <rect width="{W}" height="{H}" rx="4.5" fill="#1e1e2e"/>
  <circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="#313244" stroke-width="{SW}"/>
  {"".join(segs)}
  {"".join(labels)}
</svg>
'''
out = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "langs.svg")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    f.write(svg)
print("wrote", os.path.normpath(out), langs)
