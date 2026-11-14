"""Generates assets/hero-dark.svg and assets/hero-light.svg. Frame 0 must be fully legible.

Usage (from the repo root): python3 scripts/hero.py assets
"""
import sys, pathlib
OUT = pathlib.Path(sys.argv[1])
MONO = "'SFMono-Regular','JetBrains Mono',Consolas,Menlo,monospace"
THEMES = {
    "dark":  dict(bg0="#12100e", bg1="#0a0a0a", stroke="#26211d", rule="#1e1a17", title="#958779",
                  text="#e8e2da", dim="#a89a8d", faint="#958779", ok="#7ee787", box="#171310",
                  boxs="#2e2722", boxt="#d9d0c6", arrow="#6e6259", status="#958779", prod="#12261a", prods="#2f6b3f"),
    "light": dict(bg0="#fffaf6", bg1="#f6efe8", stroke="#e6dbd1", rule="#ece3da", title="#76685d",
                  text="#2b2420", dim="#6f6157", faint="#76685d", ok="#1a7f37", box="#ffffff",
                  boxs="#e3d6ca", boxt="#3a312b", arrow="#b3a497", status="#76685d", prod="#eaf7ee", prods="#7cc495"),
}
ACCENT = "#D97757"

def svg(t):
    steps = [("merge request", False), ("ephemeral env", False), ("review · tests", False), ("production", True)]
    boxes = []
    x, w, h, y0, gap = 600, 236, 40, 96, 18
    for i, (label, prod) in enumerate(steps):
        y = y0 + i * (h + gap)
        fill, st, col = (t["prod"], t["prods"], t["ok"]) if prod else (t["box"], t["boxs"], t["boxt"])
        mark = "✓ " if prod else ""
        boxes.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{st}" stroke-width="1.5"/>'
                     f'<text x="{x + w / 2}" y="{y + 26}" text-anchor="middle" fill="{col}" font-size="15"{" font-weight=\"700\"" if prod else ""}>{mark}{label}</text>')
        if i < len(steps) - 1:
            ay = y + h
            boxes.append(f'<path d="M{x + w / 2} {ay + 3} V{ay + gap - 4}" stroke="{t["arrow"]}" stroke-width="1.6"/>'
                         f'<path d="M{x + w / 2 - 5} {ay + gap - 9} L{x + w / 2} {ay + gap - 3} L{x + w / 2 + 5} {ay + gap - 9}" fill="none" stroke="{t["arrow"]}" stroke-width="1.6"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 360" width="880" height="360" role="img" aria-label="Alejandro in Claude Code: diagnose before you build, plan reviewed, independent review passed, ship it. Beside it, a merge request moving through its own ephemeral environment and review to production.">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["bg0"]}"/><stop offset="1" stop-color="{t["bg1"]}"/></linearGradient>
    <linearGradient id="glow" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{ACCENT}"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></linearGradient>
  </defs>
  <rect x="8" y="8" width="864" height="344" rx="16" fill="url(#bg)" stroke="{t["stroke"]}" stroke-width="1.5"/>
  <rect x="24" y="8.75" width="832" height="2.5" rx="1.25" fill="url(#glow)"/>
  <circle cx="40" cy="42" r="6.5" fill="#ff5f56"/><circle cx="62" cy="42" r="6.5" fill="#ffbd2e"/><circle cx="84" cy="42" r="6.5" fill="#27c93f"/>
  <text x="440" y="47" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{t["title"]}">✳ claude code — ~/alejandro</text>
  <line x1="24" y1="66" x2="856" y2="66" stroke="{t["rule"]}" stroke-width="1"/>
  <line x1="568" y1="82" x2="568" y2="314" stroke="{t["rule"]}" stroke-width="1"/>
  <g font-family="{MONO}" font-size="17.5">
    <text x="36" y="112" fill="{t["text"]}"><tspan fill="{ACCENT}" font-weight="700">› </tspan>diagnose before you build.</text>
    <text x="36" y="148" fill="{t["dim"]}"><tspan fill="{ACCENT}" font-weight="700">✻ </tspan>reading the whole system …</text>
    <text x="58" y="176" fill="{t["faint"]}" font-size="15">database → services → business outcome</text>
    <text x="36" y="212" fill="{t["ok"]}"><tspan font-weight="700">✓ </tspan>plan reviewed before execution</text>
    <text x="36" y="242" fill="{t["ok"]}"><tspan font-weight="700">✓ </tspan>independent review passed</text>
    <text x="36" y="282" fill="{t["text"]}"><tspan fill="{ACCENT}" font-weight="700">› </tspan>ship it. <tspan fill="{ACCENT}">▌<animate attributeName="opacity" begin="0s" dur="1.05s" values="1;1;0;0" keyTimes="0;0.5;0.5;1" repeatCount="indefinite"/></tspan></text>
  </g>
  <g font-family="{MONO}">
    <text x="718" y="86" text-anchor="middle" fill="{t["faint"]}" font-size="12.5">one environment per merge request</text>
    {"".join(boxes)}
  </g>
  <line x1="24" y1="322" x2="856" y2="322" stroke="{t["rule"]}" stroke-width="1"/>
  <g font-family="{MONO}" font-size="12.5">
    <text x="36" y="341" fill="{t["status"]}">◇ internal platforms · developer self-service · AI agents in production</text>
    <text x="844" y="341" text-anchor="end" fill="{t["title"]}"><tspan fill="{ACCENT}">✻</tspan> claude code</text>
  </g>
</svg>
'''

for name, t in THEMES.items():
    (OUT / f"hero-{name}.svg").write_text(svg(t), encoding="utf-8")
print("ok")
