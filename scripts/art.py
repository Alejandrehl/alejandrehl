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


def check_contrast():
    bad = []
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
              "checks off: ephemeral environments, a shared agent workspace, and change data capture over MCP.")
SHIPPED = ["ephemeral envs", "agent workspace", "CDC over MCP"]
# Narrow screens: hide the shipped pane and the status bar, and scale the terminal lines (bbox x 46..507,
# y 102..372) by 1.27 into the centre of the frame, so the main lines read at about 12 px on a phone.
HERO_MOBILE = ("@media (max-width:600px){.rp{display:none}"
               ".lp{transform:translate(88.8px,-44px) scale(1.27)}}")


def hero(t):
    global TL
    TL = Timeline(6.0)
    W, H = 880, 456
    fs, adv = 24, ADV * 24
    x0 = 46
    b = []
    # title bar
    b.append(dot(38, 40, 6, "#ff5f56") + dot(60, 40, 6, "#ffbd2e") + dot(82, 40, 6, "#27c93f"))
    title = "Claude Code  ~/alejandrehl"
    tx = 440 - width(title, 15) / 2 + 10
    b.append(asterisk(tx - 14, 40.5, 7, t["acc"], w=1.8))
    b.append(T(tx, 46, title, 15, t["dim"]))
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
    px, pw, ph = 592, 250, 52
    pcx = px + pw / 2
    rp.append(T(pcx, 128, "shipped", 15, t["faint"], anchor="middle", style=appear(0.2)))
    tops = [144, 216, 288]
    hits = [t_shipped + 0.15 + i * 0.5 for i in range(3)]
    for i, (top, lab) in enumerate(zip(tops, SHIPPED)):
        h = hits[i]
        flash = TL.add([(h, f"stroke:{t['boxs']}"), (h + .15, f"stroke:{t['acc']}"), (h + .55, f"stroke:{t['acc']}"),
                        (h + .9, f"stroke:{t['boxs']}")])
        rect = (f'<rect x="{px}" y="{top}" width="{pw}" height="{ph}" rx="11" fill="{t["box"]}" stroke="{t["boxs"]}" '
                f'stroke-width="1.5" style="{flash}"/>')
        icx, icy = px + 24, top + ph / 2
        pending = group(f'<circle cx="{icx}" cy="{icy}" r="6" fill="none" stroke="{t["ghost"]}" stroke-width="1.6"/>',
                        style=step_off(h), extra=' opacity="0"')
        label = T(px + 46, top + 33, lab, 20, t["boxt"],
                  style=TL.add([(h, f"fill:{t['dim']}"), (h + .3, f"fill:{t['boxt']}")]))
        rp.append(group(rect + pending + check(icx, icy, 15, t["ok"], w=2.6, draw=h + 0.05) + label,
                        style=appear(0.25 + i * 0.08)))
    b.append(group("".join(rp), cls="rp"))
    # status bar
    b.append(group(f'<line x1="24" y1="394" x2="856" y2="394" stroke="{t["rule"]}"/>' + diamond(48, 418, 5, t["faint"]) +
                   T(62, 423, "internal platforms · developer self-service · MCP servers in production", 15, t["faint"]),
                   cls="minor"))
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
    lanes = [(84, "128"), (142, "129"), (200, "130")]
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
    for k, (yc, n) in enumerate(lanes):
        delay = -k * 3.0 - 1.2  # negative: every lane is mid-cycle from the first frame
        st = static_stage[k]
        a = lambda nm, ease="linear": f"animation:{nm} {C}s {ease} {delay:.2f}s infinite both"
        lane = []
        # MR chip
        lane.append(box(36, yc - 19, 150, 38, t, rx=9))
        lane.append(T(52, yc + 7, f"MR !{n}", 18, t["boxt"], 700, m=24))
        # arrow + pulse
        lane.append(arrow_r(194, 222, yc, t["wire"], head=4.5))
        lane.append(f'<circle cx="190" cy="{yc}" r="4" fill="{t["acc"]}" opacity="0" style="{a("ar")}"/>')
        # env card
        env = [f'<rect x="232" y="{yc - 21}" width="380" height="42" rx="10" fill="{t["box"]}" '
               f'stroke="{t["boxs"] if st else t["rule"]}" stroke-width="1.5" style="{a("envb")}"/>',
               f'<circle cx="252" cy="{yc}" r="5" fill="{t["ok"] if st else t["ghost"]}" style="{a("st")}"/>',
               T(268, yc + 7, f"mr-{n}", 18, t["text"] if st else t["faint"], 700, style=a("envn"), m=24),
               T(268 + width(f"mr-{n}", 18) + 14, yc + 6, "Cloud Run · Cloud SQL · DNS", 15,
                 t["dim"] if st else t["faint"], style=a("envs"), cls="minor"),
               T(268 + width(f"mr-{n}", 24) + 16, yc + 6, "Cloud Run · SQL · DNS", 17,
                 t["dim"] if st else t["faint"], style=a("envs"), cls="nar")]
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
    b.append(caption(40, 46, "team", t))
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
    b.append(T(mx + 20 + width("CDC server", 18) + 10, my + 34, "MCP", 15, t["acct"], 700, cls="minor"))
    b.append(f'<line x1="{mx + 16}" y1="{my + 50}" x2="{mx + mw - 16}" y2="{my + 50}" stroke="{t["rule"]}"/>')
    # authz row
    b.append(check(mx + 30, my + 78, 14, t["ok"], w=2.4))
    b.append(T(mx + 46, my + 85, "authz per team", 16, t["dim"], m=20))
    b.append(f'<rect x="{mx + 14}" y="{my + 62}" width="{mw - 28}" height="30" rx="7" fill="{t["ok"]}" opacity="0" '
             f'style="animation:az {C}s linear 0s infinite both"/>')
    css.append(cyc("az", [(0, "opacity:0"), (11, "opacity:0"), (13, "opacity:.14"), (22, "opacity:.14"), (25, "opacity:0"), (100, "opacity:0")]))
    # audit log lines
    b.append(T(mx + 20, my + 121, "audit log", 15, t["faint"], m=19))
    for i in range(3):
        lx = mx + 20 + width("audit log", 15) + 12 + i * 34
        op = 1
        b.append(f'<rect class="minor" x="{lx:.1f}" y="{my + 110}" width="26" height="6" rx="3" fill="{t["wire"]}" '
                 f'style="animation:lg{i} {C}s ease-out 0s infinite both" opacity="{op}"/>')
        s0 = 22 + i * 4
        css.append(cyc(f"lg{i}", [(0, "opacity:0"), (s0, "opacity:0"), (s0 + 3, f"opacity:1;fill:{t['acc']}"),
                                  (s0 + 12, f"fill:{t['wire']}"), (92, "opacity:1"), (98, "opacity:0"), (100, "opacity:0")]))
    b.append(T(mx + 20, my + 140, "Python · FastAPI", 14, t["faint"], cls="minor"))
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
ARTS = {"hero": hero, "work-ephemeral": ephemeral, "work-agents": agents, "work-cdc": cdc, "cta": cta}
FONT_CSS = ""


LABELS = {"hero": HERO_LABEL, "work-ephemeral": EPH_LABEL, "work-agents": AGT_LABEL, "work-cdc": CDC_LABEL,
          "cta": CTA_LABEL}


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
