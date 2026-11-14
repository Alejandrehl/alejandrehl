#!/usr/bin/env python3
"""Generates every SVG in assets/, in a dark and a light version.

Usage (from the repo root):  python3 scripts/art.py
Needs fonttools and brotli (pip install fonttools brotli).

Design rules, enforced here:
- The base state of every SVG (no animation, or prefers-reduced-motion) is a complete,
  legible frame. Animations only replay how it gets there.
- Text uses JetBrains Mono (OFL-1.1, scripts/fonts/), subset and embedded, so it renders
  the same on every platform. Symbols (arrows, checks, dots, the spinner) are drawn as
  paths because the subset has no glyphs for them.
- Every text colour must reach 4.5:1 (WCAG AA) against both background stops of its theme;
  the script stops if one does not.
"""
import base64, html, io, pathlib, sys
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONTS = ROOT / "scripts" / "fonts"
OUT = ROOT / "assets"
ADV = 0.6  # JetBrains Mono advance width, in em

THEMES = {
    "dark": dict(bg0="#13110f", bg1="#0b0a09", frame="#2a241f", rule="#201c19", grid="#211d1a",
                 text="#ece6de", dim="#a89a8d", faint="#958779", acc="#D97757", acct="#E08A6D",
                 ok="#7ee787", okf="#11261a", oks="#2f6b3f", box="#181411", boxs="#332b25",
                 boxt="#ddd4ca", wire="#4a3f37", ghost="#5a4e45"),
    "light": dict(bg0="#fffaf6", bg1="#f7f0e9", frame="#e6dbd1", rule="#ece3da", grid="#ede3d9",
                  text="#2b2420", dim="#6f6157", faint="#76685d", acc="#D97757", acct="#A9502F",
                  ok="#17783a", okf="#eaf7ee", oks="#7cc495", box="#ffffff", boxs="#e0d3c6",
                  boxt="#3a312b", wire="#cdbfb2", ghost="#b9aa9c"),
}
TEXT_KEYS = ("text", "dim", "faint", "acct", "ok", "boxt")


# ---------------------------------------------------------------- colour checks
def _lum(h):
    h = h.lstrip("#")
    def ch(c):
        c = int(c, 16) / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(h[i:i + 2]) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def blend(fg, bg, a):
    f, b = fg.lstrip("#"), bg.lstrip("#")
    mix = [round(int(f[i:i + 2], 16) * a + int(b[i:i + 2], 16) * (1 - a)) for i in (0, 2, 4)]
    return "#" + "".join(f"{v:02x}" for v in mix)


def check_contrast():
    bad = []
    for name, t in THEMES.items():
        # text that sits on a translucent highlight: (text, overlay colour, opacity, surface)
        for fg, ov, a, bg in ((t["dim"], t["ok"], .14, t["box"]), (t["dim"], t["acc"], .16, t["box"]),
                              (t["boxt"], t["acc"], .16, t["bg1"])):
            c = contrast(fg, blend(ov, bg, a))
            if c < 4.5:
                bad.append(f"{name}: {fg} on {ov}@{a} over {bg}: {c:.2f}")
    for name, t in THEMES.items():
        for k in TEXT_KEYS:
            for bg in ("bg0", "bg1", "box"):
                c = contrast(t[k], t[bg])
                if c < 4.5:
                    bad.append(f"{name}.{k} on {bg}: {c:.2f}")
        if contrast(t["ok"], t["okf"]) < 4.5:
            bad.append(f"{name}.ok on okf: {contrast(t['ok'], t['okf']):.2f}")
    if bad:
        sys.exit("contrast below 4.5:1 -> " + "; ".join(bad))


# ---------------------------------------------------------------- fonts
USED_TEXT = set()


def font_css():
    chars = "".join(sorted(USED_TEXT | set(" ")))
    rules = []
    for weight in (400, 700):
        f = TTFont(FONTS / f"jetbrains-mono-latin-{weight}-normal.woff2")
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = []  # no ligatures: what is written is what renders
        opts.hinting = False
        opts.name_IDs = [0, 1, 2, 3, 4, 5, 6]  # keep copyright and licence names
        s = subset.Subsetter(opts)
        s.populate(text=chars)
        s.subset(f)
        buf = io.BytesIO()
        f.flavor = "woff2"
        f.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        rules.append(f"@font-face{{font-family:'JBM';font-weight:{weight};"
                     f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "".join(rules)


# ---------------------------------------------------------------- primitives
def esc(s):
    return html.escape(s, quote=True)


def T(x, y, s, size, fill, weight=400, anchor="start", style="", cls="", extra="", m=None):
    """m: font size on narrow screens (below 600 px rendered width)."""
    USED_TEXT.update(s)
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    w = ' font-weight="700"' if weight == 700 else ""
    if m:
        cls = (cls + " mb").strip()
        style = (style + ";" if style else "") + f"--m:{m}px"
    c = f' class="{cls}"' if cls else ""
    st = f' style="{style}"' if style else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{w}{a}{c}{st}{extra}>{esc(s)}</text>'


def width(s, size):
    return len(s) * ADV * size


class Timeline:
    """One-shot sequences. Every keyframed element runs for the whole timeline from t=0 and
    holds its state through percentages. Short or delayed animations are skipped by WebKit
    and Blink when the SVG is an <img> (verified 14-11-2026), so none are used."""

    def __init__(self, total):
        self.total, self.rules = total, {}

    def add(self, frames):
        pct = lambda t: min(max(t / self.total * 100, 0), 100)
        pts = [(0.0, frames[0][1])] + [(pct(t), c) for t, c in frames] + [(100.0, frames[-1][1])]
        body = "".join(f"{p:.3f}%{{{c}}}" for p, c in pts)
        name = self.rules.setdefault(body, f"s{len(self.rules)}")
        return f"animation:{name} {self.total}s linear 0s 1 both"

    def css(self):
        return "".join(f"@keyframes {n}{{{b}}}" for b, n in self.rules.items())


TL = None  # the timeline of the SVG being built, or None for looping diagrams


def appear(t, dur=0.45):
    ease = "animation-timing-function:cubic-bezier(.2,.7,.2,1)"
    return TL.add([(t, f"opacity:0;transform:translateY(6px);{ease}"), (t + dur, "opacity:1;transform:none")])


def step_on(t):
    return TL.add([(t, "opacity:0"), (t + 0.02, "opacity:1")])


def step_off(t):
    return TL.add([(t, "opacity:1"), (t + 0.02, "opacity:0")])


def blink():
    return "animation:blink 1.06s steps(1) 0s infinite"


def dot(cx, cy, r, fill, style=""):
    st = f' style="{style}"' if style else ""
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{st}/>'


def check(cx, cy, s, color, w=2.4, style="", draw=None):
    # a tick inside an s x s box centred on (cx, cy)
    d = f"M{cx - s * .42:.1f} {cy + s * .02:.1f} L{cx - s * .12:.1f} {cy + s * .32:.1f} L{cx + s * .44:.1f} {cy - s * .3:.1f}"
    extra = ""
    if draw is not None:
        L = s * 1.4
        extra = (f' stroke-dasharray="{L:.1f}" '
                 f'style="{TL.add([(draw, f"stroke-dashoffset:{L:.1f}px"), (draw + .35, "stroke-dashoffset:0px")])}"')
    st = f' style="{style}"' if style and draw is None else ""
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" '
            f'stroke-linejoin="round"{extra}{st}/>')


def arrow_r(x1, x2, y, color, w=1.6, head=5):
    return (f'<path d="M{x1:.1f} {y:.1f} H{x2 - 1:.1f}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'
            f'<path d="M{x2 - head:.1f} {y - head:.1f} L{x2:.1f} {y:.1f} L{x2 - head:.1f} {y + head:.1f}" fill="none" '
            f'stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def arrow_d(x, y1, y2, color, w=1.6, head=5):
    return (f'<path d="M{x:.1f} {y1:.1f} V{y2 - 1:.1f}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'
            f'<path d="M{x - head:.1f} {y2 - head:.1f} L{x:.1f} {y2:.1f} L{x + head:.1f} {y2 - head:.1f}" fill="none" '
            f'stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def asterisk(cx, cy, r, color, w=2.2, style="", cls=""):
    # the Claude Code spinner glyph, drawn: three strokes through the centre
    import math
    parts = []
    for i in range(6):
        a = math.radians(i * 60 + 90)
        x1, y1 = cx + math.cos(a) * r * .28, cy + math.sin(a) * r * .28
        x2, y2 = cx + math.cos(a) * r, cy + math.sin(a) * r
        parts.append(f"M{x1:.2f} {y1:.2f} L{x2:.2f} {y2:.2f}")
    st = f' style="{style}"' if style else ""
    c = f' class="{cls}"' if cls else ""
    return (f'<path d="{" ".join(parts)}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"{c}{st}/>')


def corner(x, y, color, s=11, w=1.6):
    # the "⎿" connector Claude Code draws under a tool call
    return f'<path d="M{x:.1f} {y - s:.1f} V{y:.1f} H{x + s:.1f}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'


def diamond(cx, cy, s, color, w=1.4):
    return (f'<path d="M{cx:.1f} {cy - s:.1f} L{cx + s:.1f} {cy:.1f} L{cx:.1f} {cy + s:.1f} L{cx - s:.1f} {cy:.1f} Z" '
            f'fill="none" stroke="{color}" stroke-width="{w}" stroke-linejoin="round"/>')


def flow_text(x, y, size, fill, parts, arrow_color):
    """Words joined by drawn arrows; each word is placed on its own, so a fallback font
    with a different advance width leaves a gap instead of an overlap."""
    out, cx = [], x
    for i, p in enumerate(parts):
        out.append(T(cx, y, p, size, fill))
        cx += width(p, size)
        if i < len(parts) - 1:
            a1 = cx + ADV * size * .7
            a2 = a1 + ADV * size * 1.5
            out.append(arrow_r(a1, a2, y - size * .32, arrow_color, w=1.4, head=size * .22))
            cx = a2 + ADV * size * .7
    return "".join(out)


def box(x, y, w, h, t, rx=10, fill=None, stroke=None, style="", dash=False, cls=""):
    d = ' stroke-dasharray="5 5"' if dash else ""
    st = f' style="{style}"' if style else ""
    c = f' class="{cls}"' if cls else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill or t["box"]}" '
            f'stroke="{stroke or t["boxs"]}" stroke-width="1.5"{d}{c}{st}/>')


def group(inner, style="", cls="", extra=""):
    st = f' style="{style}"' if style else ""
    c = f' class="{cls}"' if cls else ""
    return f"<g{c}{st}{extra}>{inner}</g>"


# ---------------------------------------------------------------- document
def doc(t, w, h, label, body, css="", grid=True):
    pat = (f'<pattern id="g" width="22" height="22" patternUnits="userSpaceOnUse">'
           f'<circle cx="11" cy="11" r="1.1" fill="{t["grid"]}"/></pattern>') if grid else ""
    gridrect = f'<rect x="9" y="9" width="{w - 18}" height="{h - 18}" rx="17" fill="url(#g)"/>' if grid else ""
    base_css = (
        f"text{{font-family:'JBM','SFMono-Regular',Menlo,Consolas,'Liberation Mono',monospace}}"
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
        ".spin{transform-box:fill-box;transform-origin:center;animation:spin 1.1s linear infinite}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
        ".nar{display:none}"
        "@media (max-width:600px){.minor,.wide{display:none}.nar{display:inline}.cap{font-size:20px}.mb{font-size:var(--m)}}"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(label)}">'
        f"<title>{esc(label)}</title>"
        f"<style>{FONT_CSS}{base_css}{css}{TL.css() if TL else ''}</style>"
        f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["bg0"]}"/>'
        f'<stop offset="1" stop-color="{t["bg1"]}"/></linearGradient>'
        f'<linearGradient id="glow" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["acc"]}"/>'
        f'<stop offset="1" stop-color="{t["acc"]}" stop-opacity="0"/></linearGradient>{pat}</defs>'
        f'<rect x="8" y="8" width="{w - 16}" height="{h - 16}" rx="18" fill="url(#bg)" stroke="{t["frame"]}" stroke-width="1.5"/>'
        f"{gridrect}"
        f'<rect x="26" y="8.75" width="{w - 52}" height="2.5" rx="1.25" fill="url(#glow)"/>'
        f"{body}</svg>\n"
    )


# ---------------------------------------------------------------- hero
HERO_LABEL = ("A Claude Code session: diagnose before you build, read the whole system from the database to the "
              "business outcome, plan reviewed, independent review passed, ship it. Beside it, a list of shipped work "
              "checks off: platform tooling, an agent workspace, mobile apps, a production ERP, and a side project.")
SHIPPED = ["platform tooling", "agent workspace", "mobile apps", "production ERP", "side project"]
# Narrow screens: hide the shipped pane and the title, and scale the terminal lines (bbox x 46..507,
# y 102..372) by 1.2 into the centre of the frame, so the main lines read at about 12 px on a phone.
HERO_MOBILE = ("@media (max-width:600px){.rp{display:none}"
               ".lp{transform:translate(108.2px,-36.4px) scale(1.2)}}")


def hero(t):
    global TL
    TL = Timeline(6.5)
    W, H = 880, 430
    fs, adv = 24, ADV * 24
    x0 = 46
    b = []
    # title bar
    b.append(dot(38, 40, 6, "#ff5f56") + dot(60, 40, 6, "#ffbd2e") + dot(82, 40, 6, "#27c93f"))
    title = "Claude Code  ~/alejandrehl"
    tx = 440 - width(title, 15) / 2 + 10
    b.append(group(asterisk(tx - 14, 40.5, 7, t["acc"], w=1.8) + T(tx, 46, title, 15, t["dim"]), cls="minor"))
    b.append(f'<line x1="24" y1="64" x2="856" y2="64" stroke="{t["rule"]}"/>')
    left_start = len(b)

    def typed(x, y, s, start, per):
        for i, ch in enumerate(s):
            if ch != " ":
                b.append(T(x + i * adv, y, ch, fs, t["text"], style=step_on(start + i * per)))
        return start + len(s) * per

    # L1  > diagnose before you build
    b.append(T(x0, 120, ">", fs, t["acct"], 700, style=appear(0.1, .2)))
    t_typed = typed(x0 + adv * 2, 120, "diagnose before you build", 0.25, 0.028)
    # L2  spinner "Reading the whole system..."  ->  "Read the whole system"
    y = 174
    t_read0, t_read1 = t_typed + 0.15, t_typed + 0.95
    spin = asterisk(x0 + 7, y - 8, 9, t["acc"], w=2.4, cls="spin")
    b.append(group(group(spin, style=step_off(t_read1)), style=step_on(t_read0), extra=' opacity="0"'))
    reading = T(x0 + adv * 2, y, "Reading the whole system...", fs, t["dim"])
    b.append(group(group(reading, style=step_off(t_read1)), style=step_on(t_read0), extra=' opacity="0"'))
    b.append(group(dot(x0 + 7, y - 8, 6.5, t["ok"]) + T(x0 + adv * 2, y, "Read the whole system", fs, t["text"]),
                   style=step_on(t_read1)))
    # L3   database -> services -> business outcome
    b.append(group(corner(x0 + 30, 207, t["faint"]) +
                   flow_text(x0 + 52, 212, 18, t["faint"], ["database", "services", "business outcome"], t["faint"]),
                   style=appear(t_read1 + 0.05)))
    # L4, L5
    t_plan, t_rev = t_read1 + 0.4, t_read1 + 0.75
    for yy, txt, tt in ((266, "Plan reviewed before execution", t_plan), (314, "Independent review passed", t_rev)):
        b.append(group(dot(x0 + 7, yy - 8, 6.5, t["ok"]) + T(x0 + adv * 2, yy, txt, fs, t["text"]), style=appear(tt)))
    # L6  > ship it, then the caret blinks
    t_ship = t_rev + 0.35
    b.append(T(x0, 366, ">", fs, t["acct"], 700, style=appear(t_ship, .2)))
    t_shipped = typed(x0 + adv * 2, 366, "ship it", t_ship + 0.1, 0.05)
    cx = x0 + adv * 2 + 8 * adv
    b.append(group(f'<rect x="{cx:.1f}" y="{366 - fs * .78:.1f}" width="{adv * .62:.1f}" height="{fs * .98:.1f}" rx="1.5" '
                   f'fill="{t["acc"]}" style="{blink()}"/>', style=step_on(t_shipped)))

    left = b[left_start:]
    del b[left_start:]
    b.append(group("".join(left), cls="lp"))
    # right pane: the work that shipped checks off, one by one
    rp = [f'<line x1="576" y1="84" x2="576" y2="372" stroke="{t["rule"]}"/>']
    px, pw, ph = 592, 250, 44
    pcx = px + pw / 2
    rp.append(T(pcx, 104, "shipped", 15, t["faint"], anchor="middle", style=appear(0.2)))
    tops = [118, 170, 222, 274, 326]
    hits = [t_shipped + 0.15 + i * 0.4 for i in range(len(SHIPPED))]
    for i, (top, lab) in enumerate(zip(tops, SHIPPED)):
        h = hits[i]
        flash = TL.add([(h, f"stroke:{t['boxs']}"), (h + .15, f"stroke:{t['acc']}"), (h + .55, f"stroke:{t['acc']}"),
                        (h + .9, f"stroke:{t['boxs']}")])
        rect = (f'<rect x="{px}" y="{top}" width="{pw}" height="{ph}" rx="11" fill="{t["box"]}" stroke="{t["boxs"]}" '
                f'stroke-width="1.5" style="{flash}"/>')
        icx, icy = px + 24, top + ph / 2
        pending = group(f'<circle cx="{icx}" cy="{icy}" r="6" fill="none" stroke="{t["ghost"]}" stroke-width="1.6"/>',
                        style=step_off(h), extra=' opacity="0"')
        label = T(px + 46, top + 29, lab, 19, t["boxt"],
                  style=TL.add([(h, f"fill:{t['dim']}"), (h + .3, f"fill:{t['boxt']}")]))
        rp.append(group(rect + pending + check(icx, icy, 15, t["ok"], w=2.6, draw=h + 0.05) + label,
                        style=appear(0.25 + i * 0.08)))
    b.append(group("".join(rp), cls="rp"))
    assert hits[-1] + 0.9 <= TL.total, "hero timeline too short"
    return doc(t, W, H, HERO_LABEL, "".join(b), HERO_MOBILE, grid=False)


# ---------------------------------------------------------------- shared diagram bits
def caption(x, y, s, t, anchor="start"):
    return T(x, y, s, 15, t["faint"], anchor=anchor, cls="cap")


def cyc(name, frames):
    """Keyframes for a looping element: frames = [(percent, css)]."""
    return f"@keyframes {name}{{" + "".join(f"{p}%{{{c}}}" for p, c in frames) + "}"


# ---------------------------------------------------------------- 1. ephemeral environments
EPH_LABEL = ("Diagram: each merge request gets its own ephemeral environment on Cloud Run, Cloud SQL, and DNS; "
             "a time to live (TTL) runs down and the environment is torn down automatically.")


def ephemeral(t):
    global TL
    TL = None
    W, H, C = 880, 252, 9.0
    b, css = [], []
    b.append(caption(40, 46, "merge request", t))
    b.append(caption(232, 46, "ephemeral environment", t))
    b.append(caption(626, 46, "TTL", t))
    b.append(caption(738, 46, "cleanup", t))
    lanes = [(84, "feat/ui", "env-ui"), (142, "fix/api", "env-api"), (200, "feat/db", "env-db")]
    # static (reduced-motion) state of each lane: stage 0 = torn down, 1 = live half ttl, 2 = live full ttl
    static_stage = [0, 1, 2]
    css.append(cyc("ln", [(0, "opacity:0"), (3, "opacity:1"), (90, "opacity:1"), (96, "opacity:0"), (100, "opacity:0")]))
    css.append(cyc("ar", [(0, "opacity:0;transform:translateX(0)"), (5, "opacity:0;transform:translateX(0)"),
                          (7, "opacity:1"), (11, "opacity:1"), (13, "opacity:0;transform:translateX(30px)"),
                          (100, "opacity:0;transform:translateX(30px)")]))
    css.append(cyc("env", [(0, "opacity:0;transform:translateX(-8px)"), (12, "opacity:0;transform:translateX(-8px)"),
                           (16, "opacity:1;transform:none"), (90, "opacity:1"), (96, "opacity:0"), (100, "opacity:0")]))
    # torn down = colours fade to the faint text colour and a ghost outline (still 4.5:1), not to low opacity
    css.append(cyc("envn", [(0, f"fill:{t['text']}"), (61, f"fill:{t['text']}"), (64, f"fill:{t['faint']}"), (100, f"fill:{t['faint']}")]))
    css.append(cyc("envs", [(0, f"fill:{t['dim']}"), (61, f"fill:{t['dim']}"), (64, f"fill:{t['faint']}"), (100, f"fill:{t['faint']}")]))
    css.append(cyc("envb", [(0, f"stroke:{t['boxs']}"), (61, f"stroke:{t['boxs']}"), (64, f"stroke:{t['rule']}"), (100, f"stroke:{t['rule']}")]))
    css.append(cyc("st", [(0, f"fill:{t['acc']}"), (20, f"fill:{t['acc']}"), (22, f"fill:{t['ok']}"),
                          (60, f"fill:{t['ok']}"), (62, f"fill:{t['ghost']}"), (100, f"fill:{t['ghost']}")]))
    css.append(cyc("ttl", [(0, "transform:scaleX(0)"), (14, "transform:scaleX(0)"), (17, "transform:scaleX(1)"),
                           (21, "transform:scaleX(1)"), (60, "transform:scaleX(0)"), (100, "transform:scaleX(0)")]))
    css.append(cyc("dn", [(0, "opacity:0"), (61, "opacity:0"), (65, "opacity:1"), (90, "opacity:1"),
                          (96, "opacity:0"), (100, "opacity:0")]))
    for k, (yc, branch, env_name) in enumerate(lanes):
        delay = -k * 3.0 - 1.2  # negative: every lane is mid-cycle from the first frame
        st = static_stage[k]
        a = lambda nm, ease="linear": f"animation:{nm} {C}s {ease} {delay:.2f}s infinite both"
        lane = []
        # MR chip
        lane.append(box(36, yc - 19, 150, 38, t, rx=9))
        lane.append(T(52, yc + 7, branch, 18, t["boxt"], 700, m=24))
        # arrow + pulse
        lane.append(arrow_r(194, 222, yc, t["wire"], head=4.5))
        lane.append(f'<circle cx="190" cy="{yc}" r="4" fill="{t["acc"]}" opacity="0" style="{a("ar")}"/>')
        # env card
        env = [f'<rect x="232" y="{yc - 21}" width="380" height="42" rx="10" fill="{t["box"]}" '
               f'stroke="{t["boxs"] if st else t["rule"]}" stroke-width="1.5" style="{a("envb")}"/>',
               f'<circle cx="252" cy="{yc}" r="5" fill="{t["ok"] if st else t["ghost"]}" style="{a("st")}"/>',
               T(268, yc + 7, env_name, 18, t["text"] if st else t["faint"], 700, style=a("envn"), m=24),
               T(268 + width(env_name, 18) + 14, yc + 6, "Cloud Run · Cloud SQL · DNS", 15,
                 t["dim"] if st else t["faint"], style=a("envs"), cls="minor")]
        lane.append(group("".join(env), style=a("env")))
        # ttl bar
        frac = {0: 0, 1: .45, 2: .9}[st]
        lane.append(f'<rect x="626" y="{yc - 3}" width="92" height="6" rx="3" fill="{t["rule"]}" stroke="{t["boxs"]}" stroke-width="1"/>')
        lane.append(f'<rect x="626" y="{yc - 3}" width="92" height="6" rx="3" fill="{t["acct"]}" '
                    f'style="transform-box:fill-box;transform-origin:left center;transform:scaleX({frac});{a("ttl")}"/>')
        # torn down
        lane.append(group(check(746, yc, 16, t["ok"], w=2.4) + T(762, yc + 6, "torn down", 16, t["ok"], cls="minor"),
                          style=a("dn"), extra=f' opacity="{0 if st else 1}"'))
        b.append(group("".join(lane), style=a("ln"), extra=""))
    return doc(t, W, H, EPH_LABEL, "".join(b), "".join(css))


# ---------------------------------------------------------------- 2. AI-agent workspace
AGT_LABEL = ("Diagram: engineers on a platform team work from one shared Claude Code workspace with reusable "
             "agent skills, MCP servers, and CI quality gates.")


def person(cx, cy, color, w=1.7):
    return (f'<circle cx="{cx}" cy="{cy - 7}" r="6" fill="none" stroke="{color}" stroke-width="{w}"/>'
            f'<path d="M{cx - 11} {cy + 12} Q{cx - 11} {cy + 1} {cx} {cy + 1} Q{cx + 11} {cy + 1} {cx + 11} {cy + 12}" '
            f'fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>')


def agents(t):
    global TL
    TL = None
    W, H, C = 880, 252, 6.0
    b, css = [], []
    b.append(caption(40, 46, "team", t))
    b.append(caption(270, 46, "shared workspace", t))
    ys = [92, 142, 192]
    for y in ys:
        b.append(box(36, y - 20, 156, 40, t, rx=10))
        b.append(person(62, y - 1, t["dim"]))
        b.append(T(84, y + 7, "engineer", 17, t["boxt"], m=21))
    # workspace card: one shared Claude Code workspace with its three building blocks
    wx, wy, ww, wh = 270, 66, 574, 152
    b.append(box(wx, wy, ww, wh, t, rx=14))
    b.append(asterisk(wx + 28, wy + 30, 8, t["acc"], w=2.2, cls="spin"))
    b.append(T(wx + 46, wy + 37, "Claude Code", 18, t["text"], 700, m=24))
    b.append(T(wx + ww - 20, wy + 36, "used by the whole team", 15, t["faint"], anchor="end", cls="minor"))
    b.append(f'<line x1="{wx + 16}" y1="{wy + 54}" x2="{wx + ww - 16}" y2="{wy + 54}" stroke="{t["rule"]}"/>')
    tiles = ["agent skills", "MCP servers", "CI quality gates"]
    for i, label in enumerate(tiles):
        tx = wx + 16 + i * 186
        b.append(box(tx, wy + 72, 170, 60, t, rx=10, fill=t["bg1"]))
        b.append(f'<rect x="{tx}" y="{wy + 72}" width="170" height="60" rx="10" fill="{t["acc"]}" opacity="0" '
                 f'style="animation:row{i} {C}s linear 0s infinite both"/>')
        short = {"CI quality gates": "CI gates"}.get(label, label)
        if short == label:
            b.append(T(tx + 85, wy + 108, label, 16, t["boxt"], anchor="middle", m=20))
        else:
            b.append(T(tx + 85, wy + 108, label, 16, t["boxt"], anchor="middle", cls="wide"))
            b.append(T(tx + 85, wy + 109, short, 20, t["boxt"], anchor="middle", cls="nar"))
        css.append(cyc(f"row{i}", [(0, "opacity:0"), (30 + i * 16, "opacity:0"), (34 + i * 16, "opacity:.16"),
                                   (44 + i * 16, "opacity:.16"), (48 + i * 16, "opacity:0"), (100, "opacity:0")]))
    # wires team -> workspace; the pulses follow the curve where offset-path is supported
    for k, y in enumerate(ys):
        d = f"M194 {y} C230 {y} 236 142 268 142"
        b.append(f'<path d="{d}" fill="none" stroke="{t["wire"]}" stroke-width="1.5"/>')
        b.append(f'<circle r="4" fill="{t["acc"]}" opacity="0" class="mp" style="offset-path:path(\'{d}\');'
                 f'animation:in{k} {C}s ease-in-out 0s infinite both"/>')
        s0 = k * 7
        css.append(cyc(f"in{k}", [(0, "opacity:0;offset-distance:0%"), (s0, "opacity:0;offset-distance:0%"),
                                  (s0 + 2, "opacity:1"), (s0 + 14, "opacity:1"), (s0 + 16, "opacity:0;offset-distance:100%"),
                                  (100, "opacity:0;offset-distance:100%")]))
    css.append("@supports not (offset-path:path('M0 0')){.mp{display:none}}")
    return doc(t, W, H, AGT_LABEL, "".join(b), "".join(css))


# ---------------------------------------------------------------- 3. CDC over MCP
CDC_LABEL = ("Diagram: a team asks an MCP server for change data capture; the server checks the team's "
             "authorization, writes an audit entry, and enables CDC on PostgreSQL, whose change events then stream out.")


def cylinder(cx, top, w, h, t):
    rx, ry = w / 2, 9
    return (f'<path d="M{cx - rx} {top + ry} V{top + h - ry} A{rx} {ry} 0 0 0 {cx + rx} {top + h - ry} V{top + ry}" '
            f'fill="{t["box"]}" stroke="{t["boxs"]}" stroke-width="1.5"/>'
            f'<ellipse cx="{cx}" cy="{top + ry}" rx="{rx}" ry="{ry}" fill="{t["box"]}" stroke="{t["boxs"]}" stroke-width="1.5"/>'
            f'<path d="M{cx - rx} {top + h * .45} A{rx} {ry} 0 0 0 {cx + rx} {top + h * .45}" fill="none" stroke="{t["boxs"]}" stroke-width="1.2"/>')


def cdc(t):
    global TL
    TL = None
    W, H, C = 880, 252, 7.0
    b, css = [], []
    b.append(caption(232, 46, "MCP server", t))
    b.append(caption(520, 46, "PostgreSQL", t))
    b.append(caption(692, 46, "change stream", t))
    # team chip
    b.append(box(36, 112, 156, 44, t, rx=10))
    b.append(person(60, 133, t["dim"]))
    b.append(T(82, 141, "team", 18, t["boxt"], 700, m=24))
    b.append(arrow_r(196, 226, 134, t["wire"], head=4.5))
    b.append(f'<circle cx="196" cy="134" r="4" fill="{t["acc"]}" opacity="0" style="animation:req {C}s ease-in-out 0s infinite both"/>')
    css.append(cyc("req", [(0, "opacity:0;transform:translateX(0)"), (2, "opacity:1"), (9, "opacity:1"),
                           (11, "opacity:0;transform:translateX(28px)"), (100, "opacity:0;transform:translateX(28px)")]))
    # MCP server card
    mx, my, mw, mh = 232, 62, 240, 152
    b.append(box(mx, my, mw, mh, t, rx=14))
    b.append(T(mx + 20, my + 35, "CDC server", 18, t["text"], 700, m=22))
    b.append(f'<line x1="{mx + 16}" y1="{my + 50}" x2="{mx + mw - 16}" y2="{my + 50}" stroke="{t["rule"]}"/>')
    # authz row
    b.append(check(mx + 30, my + 78, 14, t["ok"], w=2.4))
    b.append(T(mx + 46, my + 85, "authz per team", 16, t["dim"], m=20))
    b.append(f'<rect x="{mx + 14}" y="{my + 62}" width="{mw - 28}" height="30" rx="7" fill="{t["ok"]}" opacity="0" '
             f'style="animation:az {C}s linear 0s infinite both"/>')
    css.append(cyc("az", [(0, "opacity:0"), (11, "opacity:0"), (13, "opacity:.14"), (22, "opacity:.14"), (25, "opacity:0"), (100, "opacity:0")]))
    # audit log lines
    b.append(T(mx + 20, my + 124, "audit log", 15, t["faint"], m=22))
    for i in range(3):
        lx = mx + 20 + width("audit log", 15) + 12 + i * 34
        op = 1
        b.append(f'<rect class="minor" x="{lx:.1f}" y="{my + 113}" width="26" height="6" rx="3" fill="{t["wire"]}" '
                 f'style="animation:lg{i} {C}s ease-out 0s infinite both" opacity="{op}"/>')
        s0 = 22 + i * 4
        css.append(cyc(f"lg{i}", [(0, "opacity:0"), (s0, "opacity:0"), (s0 + 3, f"opacity:1;fill:{t['acc']}"),
                                  (s0 + 12, f"fill:{t['wire']}"), (92, "opacity:1"), (98, "opacity:0"), (100, "opacity:0")]))
    # MCP -> PostgreSQL
    b.append(arrow_r(476, 514, 134, t["wire"], head=4.5))
    b.append(f'<circle cx="476" cy="134" r="4" fill="{t["acc"]}" opacity="0" style="animation:en {C}s ease-in-out 0s infinite both"/>')
    css.append(cyc("en", [(0, "opacity:0;transform:translateX(0)"), (28, "opacity:0;transform:translateX(0)"),
                          (30, "opacity:1"), (36, "opacity:1"), (38, "opacity:0;transform:translateX(36px)"),
                          (100, "opacity:0;transform:translateX(36px)")]))
    # PostgreSQL
    b.append(cylinder(578, 88, 116, 96, t))
    b.append(T(578, 161, "WAL", 15, t["faint"], anchor="middle", m=19))
    b.append(f'<circle cx="578" cy="124" r="6" fill="{t["ok"]}" style="animation:cdcon {C}s ease 0s infinite both"/>')
    css.append(cyc("cdcon", [(0, f"fill:{t['ghost']}"), (37, f"fill:{t['ghost']}"), (40, f"fill:{t['ok']}"),
                             (94, f"fill:{t['ok']}"), (98, f"fill:{t['ghost']}"), (100, f"fill:{t['ghost']}")]))
    # stream of change events
    sx1, sx2, sy = 654, 844, 134
    b.append(f'<line x1="{sx1}" y1="{sy}" x2="{sx2}" y2="{sy}" stroke="{t["rule"]}" stroke-width="22" stroke-linecap="round"/>')
    kinds = [("I", t["ok"]), ("U", t["acct"]), ("D", t["dim"]), ("U", t["acct"]), ("I", t["ok"])]
    css.append(cyc("ev", [(0, "opacity:0;transform:translateX(0)"), (6, "opacity:1"), (88, "opacity:1"),
                          (100, "opacity:0;transform:translateX(170px)")]))
    # events only flow while CDC is on (the same 40%..94% window as the WAL dot)
    css.append(cyc("evon", [(0, "opacity:0"), (38, "opacity:0"), (42, "opacity:1"), (92, "opacity:1"), (96, "opacity:0"), (100, "opacity:0")]))
    b.append(f'<g style="animation:evon {C}s linear 0s infinite both">')
    for i, (k, col) in enumerate(kinds):
        # static positions spread along the stream; the animation moves each one along it
        x = sx1 + 6
        static = 16 + i * 36
        b.append(f'<g style="animation:ev 3.5s linear {-i * 0.7:.2f}s infinite both" transform="translate({static} 0)">'
                 f'<rect x="{x}" y="{sy - 9}" width="22" height="18" rx="4" fill="{t["box"]}" stroke="{col}" stroke-width="1.5"/>'
                 + T(x + 11, sy + 5, k, 13, col, 700, anchor="middle") + "</g>")
    b.append("</g>")
    b.append(T(749, 182, "insert · update · delete", 14, t["faint"], anchor="middle", cls="minor"))
    return doc(t, W, H, CDC_LABEL, "".join(b), "".join(css))


# ---------------------------------------------------------------- 4. mobile apps
MOB_LABEL = ("Two phones. NutriCoach: a meal photo is scanned and logged, and its protein, carbs, and fat rings fill. "
             "An art marketplace: a gallery of artworks scrolls and one is saved to favorites.")
ART_TILES = ["#D97757", "#E8C07D", "#7A9E87", "#2F4858", "#C9B8A8", "#8C5E58"]


def phone(x, y, w, h, t, clip_id):
    """Phone body and screen; returns (markup, screen x, screen y, screen w, clip definition)."""
    body = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="30" fill="{t["box"]}" stroke="{t["boxs"]}" stroke-width="1.5"/>'
            f'<rect x="{x + 7}" y="{y + 7}" width="{w - 14}" height="{h - 14}" rx="24" fill="{t["bg1"]}"/>'
            f'<rect x="{x + w / 2 - 24}" y="{y + 15}" width="48" height="13" rx="6.5" fill="{t["boxs"]}"/>')
    clip = (f'<clipPath id="{clip_id}"><rect x="{x + 7}" y="{y + 7}" width="{w - 14}" height="{h - 14}" rx="24"/></clipPath>')
    return body, clip


def ring(cx, cy, r, color, frac, t, name, C):
    circ = 2 * 3.14159 * r
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["rule"]}" stroke-width="5"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round" '
            f'stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ * (1 - frac):.1f}" transform="rotate(-90 {cx} {cy})" '
            f'style="animation:{name} {C}s ease-in-out 0s infinite both"/>',
            cyc(name, [(0, f"stroke-dashoffset:{circ:.1f}px"), (26, f"stroke-dashoffset:{circ:.1f}px"),
                       (36, f"stroke-dashoffset:{circ * (1 - frac):.1f}px"), (92, f"stroke-dashoffset:{circ * (1 - frac):.1f}px"),
                       (98, f"stroke-dashoffset:{circ:.1f}px"), (100, f"stroke-dashoffset:{circ:.1f}px")]))


def mobile_apps(t):
    global TL
    TL = None
    W, H, C = 880, 404, 8.0
    b, css, defs = [], [], []
    pw, ph, py = 176, 334, 22
    # ---- NutriCoach
    x = 172
    body, clip = phone(x, py, pw, ph, t, "scrA")
    defs.append(clip)
    b.append(body)
    X, w_ = x + 14, pw - 28
    scr = [T(X + 4, py + 54, "NutriCoach", 14, t["text"], 700, cls="minor"), dot(X + w_ - 8, py + 49, 6, t["acc"])]
    # meal photo card with a plate, and the scan line that reads it
    cy = py + 116
    scr.append(f'<rect x="{X}" y="{py + 68}" width="{w_}" height="96" rx="14" fill="{t["box"]}" stroke="{t["boxs"]}" stroke-width="1.2"/>')
    scr.append(f'<circle cx="{X + w_ / 2}" cy="{cy}" r="33" fill="{t["bg0"]}" stroke="{t["boxs"]}" stroke-width="1.5"/>')
    scr.append(f'<circle cx="{X + w_ / 2 - 11}" cy="{cy - 7}" r="12" fill="#7A9E87"/>'
               f'<circle cx="{X + w_ / 2 + 12}" cy="{cy + 3}" r="10" fill="{t["acc"]}"/>'
               f'<rect x="{X + w_ / 2 - 8}" y="{cy + 9}" width="20" height="9" rx="4.5" fill="#E8C07D"/>')
    scr.append(f'<rect x="{X + 6}" y="{py + 72}" width="{w_ - 12}" height="2.5" rx="1.25" fill="{t["acc"]}" opacity="0" '
               f'style="animation:scan {C}s linear 0s infinite both"/>')
    css.append(cyc("scan", [(0, "opacity:0;transform:translateY(0)"), (4, "opacity:0;transform:translateY(0)"),
                            (6, "opacity:.95"), (22, "opacity:.95;transform:translateY(86px)"),
                            (24, "opacity:0;transform:translateY(86px)"), (100, "opacity:0;transform:translateY(86px)")]))
    # macro rings
    for i, (lab, col, frac) in enumerate((("P", t["acc"], .82), ("C", "#7A9E87", .64), ("F", "#E8C07D", .48))):
        rx_ = X + 24 + i * 50
        r_svg, r_css = ring(rx_, py + 196, 16, col, frac, t, f"rg{i}", C)
        scr.append(r_svg)
        css.append(r_css)
        scr.append(T(rx_, py + 233, lab, 12, t["dim"], 700, anchor="middle", cls="minor"))
    # coach replies
    css.append(cyc("b1", [(0, "opacity:0;transform:translateY(6px)"), (36, "opacity:0;transform:translateY(6px)"),
                          (40, "opacity:1;transform:none"), (92, "opacity:1;transform:none"), (97, "opacity:0"), (100, "opacity:0")]))
    css.append(cyc("b2", [(0, "opacity:0;transform:translateY(6px)"), (46, "opacity:0;transform:translateY(6px)"),
                          (50, "opacity:1;transform:none"), (92, "opacity:1;transform:none"), (97, "opacity:0"), (100, "opacity:0")]))
    scr.append(group(f'<rect x="{X}" y="{py + 248}" width="{w_ - 18}" height="30" rx="12" fill="{t["okf"]}" stroke="{t["oks"]}" stroke-width="1.2"/>'
                     + check(X + 16, py + 263, 11, t["ok"], w=2) + T(X + 28, py + 268, "Lunch logged", 12, t["ok"], 700, cls="minor"),
                     style=f"animation:b1 {C}s ease-out 0s infinite both"))
    scr.append(group(f'<rect x="{X}" y="{py + 286}" width="{w_}" height="30" rx="12" fill="{t["box"]}" stroke="{t["boxs"]}" stroke-width="1.2"/>'
                     + T(X + 12, py + 306, "Protein on track", 12, t["boxt"], cls="minor"),
                     style=f"animation:b2 {C}s ease-out 0s infinite both"))
    b.append(group("".join(scr), extra=' clip-path="url(#scrA)"'))
    b.append(T(x + pw / 2, 382, "NutriCoach", 17, t["text"], 700, anchor="middle", m=24))
    # ---- art marketplace
    x = 532
    body, clip = phone(x, py, pw, ph, t, "scrB")
    defs.append(clip)
    b.append(body)
    X = x + 14
    scr = [T(X + 4, py + 54, "Discover", 14, t["text"], 700, cls="minor"),
           f'<circle cx="{X + w_ - 10}" cy="{py + 49}" r="6" fill="none" stroke="{t["dim"]}" stroke-width="1.6"/>'
           f'<path d="M{X + w_ - 5.5} {py + 53.5} l4 4" stroke="{t["dim"]}" stroke-width="1.6" stroke-linecap="round"/>']
    tw, th, gx, gy = (w_ - 8) / 2, 86, 8, 8
    tiles = []
    for r in range(6):
        for c in range(2):
            k = (r % 3) * 2 + c
            tx, ty = X + c * (tw + gx), py + 68 + r * (th + gy)
            bg, fg, fg2 = ART_TILES[k % 6], ART_TILES[(k + 2) % 6], ART_TILES[(k + 4) % 6]
            shape = [f'<circle cx="{tx + tw * .62:.1f}" cy="{ty + th * .4:.1f}" r="{tw * .26:.1f}" fill="{fg}"/>',
                     f'<rect x="{tx + 10:.1f}" y="{ty + th * .55:.1f}" width="{tw - 20:.1f}" height="{th * .18:.1f}" rx="4" fill="{fg2}"/>',
                     f'<path d="M{tx:.1f} {ty + th:.1f} L{tx + tw * .5:.1f} {ty + th * .45:.1f} L{tx + tw:.1f} {ty + th:.1f} Z" fill="{fg}"/>'][k % 3]
            tiles.append(f'<rect x="{tx:.1f}" y="{ty:.1f}" width="{tw:.1f}" height="{th}" rx="10" fill="{bg}"/>' + shape)
            if r % 3 == 0 and c == 1:
                hx, hy = tx + tw - 16, ty + 16
                tiles.append(f'<path d="M{hx} {hy + 5} c-6 -5 -9 -8 -9 -11 a4.5 4.5 0 0 1 9 -1.5 a4.5 4.5 0 0 1 9 1.5 c0 3 -3 6 -9 11 Z" '
                             f'fill="#ffffff" style="transform-box:fill-box;transform-origin:center;animation:hrt {C}s ease-out 0s infinite both"/>')
    css.append(cyc("hrt", [(0, "transform:scale(1)"), (40, "transform:scale(1)"), (44, "transform:scale(1.45)"),
                           (50, "transform:scale(1)"), (100, "transform:scale(1)")]))
    period = 3 * (th + gy)
    defs.append(f'<clipPath id="grid"><rect x="{X}" y="{py + 66}" width="{w_}" height="{ph - 73}"/></clipPath>')
    scr.append(f'<g clip-path="url(#grid)"><g style="animation:gal {C * 1.5}s linear 0s infinite both">' + "".join(tiles) + "</g></g>")
    css.append(cyc("gal", [(0, "transform:translateY(0)"), (100, f"transform:translateY(-{period}px)")]))
    b.append(group("".join(scr), extra=' clip-path="url(#scrB)"'))
    b.append(T(x + pw / 2, 382, "art marketplace", 17, t["text"], 700, anchor="middle", m=24))
    # callouts pointing at what each screen is doing (wide screens only)
    def callout(x_text, y, label, x_line0, x_line1, anchor):
        return group(T(x_text, y + 5, label, 14, t["dim"], anchor=anchor) +
                     f'<line x1="{x_line0}" y1="{y}" x2="{x_line1}" y2="{y}" stroke="{t["wire"]}" stroke-width="1.2" stroke-dasharray="2 4"/>' +
                     dot(x_line1, y, 2.5, t["acc"]), cls="minor")
    for y, lab in ((py + 116, "meal photo"), (py + 196, "macros"), (py + 284, "coach chat")):
        b.append(callout(150, y, lab, 156, 196, "end"))
    for y, lab in ((py + 116, "gallery"), (py + 196, "favorites")):
        b.append(callout(730, y, lab, 722, 692, "start"))
    return doc(t, W, H, MOB_LABEL, "<defs>" + "".join(defs) + "</defs>" + "".join(b), "".join(css))


# ---------------------------------------------------------------- 5. ERP
ERP_LABEL = ("Diagram: an ERP dashboard for a distribution company, with modules for sales, inventory, customers, "
             "suppliers, payments, commissions, and dispatch; sales charts grow, documents arrive, and a pending sales "
             "order turns paid. A coverage-gate badge shows it is covered by tests.")
ERP_MODULES = ["Sales", "Inventory", "Customers", "Suppliers", "Payments", "Commissions", "Dispatch"]


def erp(t):
    global TL
    TL = None
    W, H, C = 880, 324, 14.0
    b, css = [], []
    b.append(box(36, 32, 808, 262, t, rx=14))
    for i in range(3):
        b.append(dot(58 + i * 15, 52, 4, t["boxs"]))
    b.append(T(110, 57, "dashboard", 13, t["faint"], cls="minor"))
    b.append(group(f'<rect x="676" y="41" width="152" height="24" rx="12" fill="{t["okf"]}" stroke="{t["oks"]}" stroke-width="1.2"/>'
                   + check(694, 53, 11, t["ok"], w=2) + T(708, 58, "coverage gate", 13, t["ok"], 700), cls="minor"))
    b.append(f'<line x1="37" y1="74" x2="843" y2="74" stroke="{t["rule"]}"/>')
    b.append(f'<line x1="196" y1="74" x2="196" y2="293" stroke="{t["rule"]}"/>')
    # sidebar with a moving active state
    for i, m in enumerate(ERP_MODULES):
        y = 100 + i * 27
        b.append(f'<rect x="54" y="{y - 10}" width="12" height="12" rx="3.5" fill="{t["ghost"]}"/>')
        b.append(T(76, y + 1, m, 14, t["dim"], cls="minor"))
    css.append(cyc("act", [(p * 100 / 7, f"transform:translateY({i * 27}px)") for i, p in enumerate(range(7))] +
                   [(100, "transform:translateY(0px)")]))
    b.append(f'<rect class="minor" x="46" y="87" width="140" height="24" rx="7" fill="{t["acc"]}" opacity=".16" '
             f'style="animation:act {C}s steps(1) 0s infinite both"/>')
    # KPI cards with growing bars
    for k, lab in enumerate(("sales", "stock", "dispatch")):
        cx = 212 + k * 212
        b.append(box(cx, 88, 192, 84, t, rx=12, fill=t["bg1"]))
        b.append(T(cx + 14, 110, lab, 13, t["dim"], 700, m=22))
        hs = [(14, 22, 18, 28, 24, 34, 40), (30, 26, 32, 24, 28, 22, 26), (10, 18, 16, 26, 30, 28, 38)][k]
        for j, hgt in enumerate(hs):
            bx = cx + 14 + j * 24
            col = t["acc"] if j == 6 else t["wire"]
            b.append(f'<rect x="{bx}" y="{160 - hgt}" width="16" height="{hgt}" rx="3" fill="{col}" '
                     f'style="transform-box:fill-box;transform-origin:bottom;animation:bar{k} {C / 2}s ease-out {-j * .08:.2f}s infinite both"/>')
        css.append(cyc(f"bar{k}", [(0, "transform:scaleY(.15)"), (12 + k * 6, "transform:scaleY(.15)"), (26 + k * 6, "transform:scaleY(1)"),
                                   (92, "transform:scaleY(1)"), (100, "transform:scaleY(.15)")]))
    # documents table
    b.append(T(224, 198, "document", 12, t["faint"], cls="minor"))
    b.append(T(424, 198, "customer", 12, t["faint"], cls="minor"))
    b.append(T(708, 198, "status", 12, t["faint"], cls="minor"))
    rows = [("Sales order", 150, "paid"), ("Delivery note", 120, "shipped"), ("Sales order", 170, "pending")]
    for i, (doc_, bw, stt) in enumerate(rows):
        y = 222 + i * 26
        css.append(cyc(f"row{i}", [(0, "opacity:0;transform:translateY(-6px)"), (8 + i * 6, "opacity:0;transform:translateY(-6px)"),
                                   (12 + i * 6, "opacity:1;transform:none"), (94, "opacity:1;transform:none"), (98, "opacity:0"), (100, "opacity:0")]))
        cells = [f'<line x1="212" y1="{y - 18}" x2="828" y2="{y - 18}" stroke="{t["rule"]}"/>',
                 T(224, y, doc_, 14, t["boxt"], m=20),
                 f'<rect class="minor" x="424" y="{y - 9}" width="{bw}" height="8" rx="4" fill="{t["rule"]}"/>']
        chip = {"paid": (t["okf"], t["oks"], t["ok"]), "shipped": (t["box"], t["acc"], t["acct"]),
                "pending": (t["bg1"], t["boxs"], t["dim"])}
        def chip_svg(kind):
            f_, s_, c_ = chip[kind]
            return (f'<rect x="700" y="{y - 14}" width="112" height="20" rx="10" fill="{f_}" stroke="{s_}" stroke-width="1.2"/>'
                    + T(756, y + 1, kind, 12, c_, 700, anchor="middle", m=18))
        if i == 0:
            # this sales note arrives pending and turns paid
            css.append(cyc("pend", [(0, "opacity:1"), (40, "opacity:1"), (43, "opacity:0"), (100, "opacity:0")]))
            css.append(cyc("paid", [(0, "opacity:0"), (40, "opacity:0"), (43, "opacity:1"), (100, "opacity:1")]))
            cells.append(group(chip_svg("pending"), style=f"animation:pend {C}s linear 0s infinite both", extra=' opacity="0"'))
            cells.append(group(chip_svg("paid"), style=f"animation:paid {C}s linear 0s infinite both"))
        else:
            cells.append(chip_svg(stt))
        b.append(group("".join(cells), style=f"animation:row{i} {C}s ease-out 0s infinite both"))
    return doc(t, W, H, ERP_LABEL, "".join(b), "".join(css))


# ---------------------------------------------------------------- 6. micodigopostal.fun
STOPS = [("Arica", "1000000", "Región de Arica y Parinacota", -18.5377),
         ("Santiago", "8320000", "Región Metropolitana", -33.4541),
         ("Puerto Montt", "5480000", "Región de los Lagos", -41.4892),
         ("Punta Arenas", "6200000", "Región de Magallanes y Antártica Chilena", -53.6415)]
POS_LABEL = ("micodigopostal.fun: a search box looks up Arica, Santiago, Puerto Montt, and Punta Arenas in turn; a "
             "slot-machine counter rolls to each city's base postal code (1000000, 8320000, 5480000, 6200000) while a pin "
             "hops down Chile, drawn sideways from north to south.")


def postal(t):
    global TL
    TL = None
    W, H, C = 880, 300, 12.0
    seg = C / len(STOPS)
    pct = lambda s_: round(min(max(s_ / C * 100, 0), 100), 3)
    b, css, defs = [], [], []
    b.append(caption(40, 44, "city", t))
    b.append(caption(468, 44, "postal code", t))
    # search field with the commune of each stop
    b.append(box(36, 58, 392, 58, t, rx=12))
    b.append(f'<circle cx="62" cy="84" r="8" fill="none" stroke="{t["dim"]}" stroke-width="2"/>'
             f'<path d="M68 90 l6 6" stroke="{t["dim"]}" stroke-width="2" stroke-linecap="round"/>')
    for k, (name, code, region, lat) in enumerate(STOPS):
        a0, a1 = k * seg, (k + 1) * seg
        frames = [(0, "opacity:0"), (pct(a0), "opacity:0"), (pct(a0 + .25), "opacity:1"), (pct(a1 - .15), "opacity:1"),
                  (pct(a1), "opacity:0"), (100, "opacity:0")]
        if k == len(STOPS) - 1:
            # fade out before the first stop fades back in at the loop seam, so the names never overlap
            frames = [(0, "opacity:0"), (pct(a0), "opacity:0"), (pct(a0 + .25), "opacity:1"), (pct(a1 - .5), "opacity:1"),
                      (pct(a1 - .25), "opacity:0"), (100, "opacity:0")]
        if k == 0:
            frames = [(0, "opacity:1"), (pct(a1 - .15), "opacity:1"), (pct(a1), "opacity:0"), (pct(C - .25), "opacity:0"), (100, "opacity:1")]
        css.append(cyc(f"nm{k}", frames))
        base = 1 if name == "Santiago" else 0
        b.append(T(88, 95, name, 24, t["text"], 700, style=f"animation:nm{k} {C}s linear 0s infinite both", extra=f' opacity="{base}"', m=34))
        land = a0 + 1.35
        out0 = a1 - (.5 if k == len(STOPS) - 1 else .15)
        rframes = [(0, "opacity:0"), (pct(land), "opacity:0"), (pct(land + .25), "opacity:1"), (pct(out0), "opacity:1"),
                   (pct(out0 + (.25 if k == len(STOPS) - 1 else .15)), "opacity:0"), (100, "opacity:0")]
        css.append(cyc(f"rg{k}", rframes))
        b.append(T(468, 154, region, 15, t["dim"], style=f"animation:rg{k} {C}s linear 0s infinite both", extra=f' opacity="{base}"', cls="minor"))
    b.append(arrow_r(436, 458, 87, t["wire"], head=4.5))
    # odometer: each column is a strip 0..19 that rolls a full turn to the next digit
    cw, gap, oy, oh, step = 46, 8, 58, 60, 60
    defs.append(f'<clipPath id="odo"><rect x="468" y="{oy}" width="{7 * cw + 6 * gap}" height="{oh}" rx="10"/></clipPath>')
    santiago = STOPS[1][1]
    strips = []
    for c in range(7):
        x = 468 + c * (cw + gap)
        b.append(f'<rect x="{x}" y="{oy}" width="{cw}" height="{oh}" rx="10" fill="{t["box"]}" stroke="{t["boxs"]}" stroke-width="1.5"/>')
        # the strip (digits 0..10*(n+1)-1) only ever moves forward: stop k lands on copy k+1 of its digit; the one jump back to
        # copy 0 happens at the loop restart, which is instantaneous
        n = len(STOPS)
        digits = "".join(T(x + cw / 2, oy + 45 + j * step, str(j % 10), 40, t["text"], 700, anchor="middle")
                         for j in range(10 * (n + 1)))
        d = [int(code[c]) for _, code, _, _ in STOPS]
        pos = [d[-1]] + [d[k] + 10 * (k + 1) for k in range(n)]
        frames = [(0, f"transform:translateY(-{pos[0] * step}px)")]
        for k in range(n):
            s0 = k * seg + .2 + c * .07
            frames += [(pct(s0), f"transform:translateY(-{pos[k] * step}px);animation-timing-function:cubic-bezier(.25,.8,.25,1)"),
                       (pct(s0 + 1.0), f"transform:translateY(-{pos[k + 1] * step}px)")]
        frames.append((100, f"transform:translateY(-{pos[-1] * step}px)"))
        css.append(cyc(f"od{c}", frames))
        strips.append(f'<g transform="translate(0 -{int(santiago[c]) * step})" style="animation:od{c} {C}s linear 0s infinite both">{digits}</g>')
        b.append(f'<line x1="{x + 6}" y1="{oy + oh / 2}" x2="{x + cw - 6}" y2="{oy + oh / 2}" stroke="{t["rule"]}" stroke-width="1" opacity=".5"/>')
    b.append(f'<g clip-path="url(#odo)">{"".join(strips)}</g>')
    # confetti on each landing
    bits = [(-26, -18, t["acc"]), (18, -24, "#7A9E87"), (40, -6, "#E8C07D"), (-40, 2, "#7A9E87"), (6, -30, t["acc"]), (30, 14, t["acc"])]
    for i, (dx, dy, col) in enumerate(bits):
        frames = [(0, "opacity:0;transform:translate(0,0)")]
        for k in range(len(STOPS)):
            l0 = k * seg + 1.25
            frames += [(pct(l0), "opacity:0;transform:translate(0,0)"), (pct(l0 + .1), "opacity:1;transform:translate(0,0)"),
                       (pct(l0 + .7), f"opacity:0;transform:translate({dx}px,{dy}px)")]
        frames.append((100, f"opacity:0;transform:translate({dx}px,{dy}px)"))
        css.append(cyc(f"cf{i}", frames))
        b.append(f'<rect x="{652 + i * 4}" y="{oy - 2}" width="6" height="6" rx="1.5" fill="{col}" opacity="0" '
                 f'style="animation:cf{i} {C}s ease-out 0s infinite both"/>')
    # Chile, sideways: north on the left, south on the right
    x0, x1, sy = 60, 820, 222
    lat0, lat1 = STOPS[0][3], STOPS[-1][3]
    xs = [x0 + (lat - lat0) / (lat1 - lat0) * (x1 - x0) for *_, lat in STOPS]
    wave = " ".join(f"L{x0 + i * 38} {sy - 6 - (3 if i % 2 else 0)}" for i in range(1, 21))
    trk = []
    trk.append(f'<path d="M{x0} {sy - 6} {wave} L{x1} {sy + 6} L{x0} {sy + 6} Z" fill="{t["rule"]}" stroke="{t["boxs"]}" stroke-width="1.2" stroke-linejoin="round"/>')
    trk.append(T(440, 280, "Chile, sideways: north to south", 15, t["faint"], anchor="middle", cls="cap"))
    for k, ((name, *_), x) in enumerate(zip(STOPS, xs)):
        trk.append(dot(x, sy, 4, t["ghost"]))
        anchor = "start" if k == 0 else "end" if k == len(STOPS) - 1 else "middle"
        lx = x - 8 if k == 0 else x + 8 if k == len(STOPS) - 1 else x
        trk.append(T(lx, sy + 28, name, 13, t["dim"], anchor=anchor, m=20))
    # the pin hops from stop to stop
    frames = [(0, f"transform:translate({xs[-1] - xs[1]:.1f}px,0px)")]
    for k, x in enumerate(xs):
        s0 = k * seg + .1
        prev = xs[k - 1]
        mid = (prev + x) / 2
        frames += [(pct(s0), f"transform:translate({prev - xs[1]:.1f}px,0px)"),
                   (pct(s0 + .5), f"transform:translate({mid - xs[1]:.1f}px,-26px)"),
                   (pct(s0 + 1.0), f"transform:translate({x - xs[1]:.1f}px,0px)"),
                   (pct(s0 + 1.1), f"transform:translate({x - xs[1]:.1f}px,-5px)"),
                   (pct(s0 + 1.2), f"transform:translate({x - xs[1]:.1f}px,0px)")]
    frames.append((100, f"transform:translate({xs[-1] - xs[1]:.1f}px,0px)"))
    css.append(cyc("pin", frames))
    px = xs[1]
    trk.append(f'<g style="animation:pin {C}s ease-in-out 0s infinite both">'
             f'<path d="M{px:.1f} {sy - 4} C{px - 4:.1f} {sy - 12} {px - 12:.1f} {sy - 18} {px - 12:.1f} {sy - 27} '
             f'a12 12 0 0 1 24 0 C{px + 12:.1f} {sy - 18} {px + 4:.1f} {sy - 12} {px:.1f} {sy - 4} Z" fill="{t["acc"]}"/>'
             f'<circle cx="{px:.1f}" cy="{sy - 27}" r="4.5" fill="{t["box"]}"/></g>')
    # on phones the region line is hidden, so the track moves up to close the gap
    b.append(group("".join(trk), cls="trk"))
    css.append("@media (max-width:600px){.trk{transform:translateY(-34px)}}")
    return doc(t, W, H, POS_LABEL, "<defs>" + "".join(defs) + "</defs>" + "".join(b), "".join(css))


# ---------------------------------------------------------------- footer
CTA_LABEL = "A Claude Code prompt reads: let's build something that has to work in production."


def cta(t):
    global TL
    TL = Timeline(3.0)
    W, H = 880, 136

    def prompt(lines, fs, x, ys, start, per):
        adv, out, k = ADV * fs, [T(x, ys[0], ">", fs, t["acct"], 700)], 0
        for line, y in zip(lines, ys):
            for i, ch in enumerate(line):
                if ch != " ":
                    out.append(T(x + adv * 2 + i * adv, y, ch, fs, t["text"], style=step_on(start + k * per)))
                k += 1
        end = start + k * per
        cx = x + adv * 2 + (len(lines[-1]) + 1) * adv
        out.append(group(f'<rect x="{cx:.1f}" y="{ys[-1] - fs * .78:.1f}" width="{adv * .62:.1f}" height="{fs * .98:.1f}" '
                         f'rx="1.5" fill="{t["acc"]}" style="{blink()}"/>', style=step_on(end)))
        return "".join(out), end

    # wide: one line; narrow: the same words on two larger lines
    wide, e1 = prompt(["let's build something that has to work in production"], 21, 52, [76], 0.4, 0.03)
    nar, e2 = prompt(["let's build something that", "has to work in production"], 30, 52, [62, 100], 0.4, 0.03)
    b = [group(box(28, 36, 824, 64, t, rx=14) + wide, cls="wide"),
         group(box(28, 24, 824, 94, t, rx=14) + nar, cls="nar")]
    assert max(e1, e2) < TL.total
    return doc(t, W, H, CTA_LABEL, "".join(b), grid=False)


# ---------------------------------------------------------------- build
ARTS = {"hero": hero, "work-ephemeral": ephemeral, "work-agents": agents, "work-cdc": cdc, "work-mobile": mobile_apps,
        "work-erp": erp, "work-postal": postal, "cta": cta}
FONT_CSS = ""


LABELS = {"hero": HERO_LABEL, "work-ephemeral": EPH_LABEL, "work-agents": AGT_LABEL, "work-cdc": CDC_LABEL,
          "work-mobile": MOB_LABEL, "work-erp": ERP_LABEL, "work-postal": POS_LABEL, "cta": CTA_LABEL}


def check_readme():
    """Every <picture> in README.md must use the dark and light file of one art and carry its label as alt."""
    import re
    md = (ROOT / "README.md").read_text(encoding="utf-8")
    bad = []
    for name, label in LABELS.items():
        m = re.search(rf'<picture>\s*<source media="\(prefers-color-scheme: dark\)" srcset="\./assets/{name}-dark\.svg">\s*'
                      rf'<source media="\(prefers-color-scheme: light\)" srcset="\./assets/{name}-light\.svg">\s*'
                      rf'<img src="\./assets/{name}-light\.svg"[^>]*alt="([^"]*)"', md)
        if not m:
            bad.append(f"{name}: no <picture> with both themes")
        elif html.unescape(m.group(1)) != label:
            bad.append(f"{name}: alt differs from the SVG label")
    if bad:
        sys.exit("README check failed -> " + "; ".join(bad))


def main():
    global FONT_CSS
    check_contrast()
    # first pass collects the characters, second pass embeds the subset font
    for fn in ARTS.values():
        for t in THEMES.values():
            fn(t)
    FONT_CSS = font_css()
    OUT.mkdir(exist_ok=True)
    for name, fn in ARTS.items():
        for theme, t in THEMES.items():
            (OUT / f"{name}-{theme}.svg").write_text(fn(t), encoding="utf-8")
    check_readme()
    print("ok:", ", ".join(f"{n}-{{dark,light}}.svg" for n in ARTS), "· README alts match")


if __name__ == "__main__":
    main()
