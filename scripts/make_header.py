#!/usr/bin/env python3
"""Generate an animated SVG GitHub profile header (SMIL only, no JS, no external fonts)."""
import html
import math
import random
import sys

OUT = sys.argv[1]
W, H = 960, 200
random.seed(20261107)

NAME = "Deepratna Awale"
ROLES = [
    "Gen AI / ML Engineer",
    "Sr. Software Engineer @ Nasdaq",
    "Building Agents to catch Fraud & Money Laundering",
    "Maintainer of Open Wallpaper Engine, AutoExpress & SD Parsers",
]
FONT = "'Segoe UI', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
SPLINE = "0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1;0.42 0 0.58 1"

def f(v):
    return f"{v:.1f}"

# --- constellation nodes -----------------------------------------------------
nodes = []
for _ in range(58):
    x = random.uniform(-30, W + 30)
    y = random.uniform(-30, H + 30)
    # keep mesh thinner behind the name block
    if 10 < x < 420 and 50 < y < 150 and random.random() < 0.55:
        continue
    nodes.append({
        "x": x, "y": y,
        "ax": random.uniform(3, 9), "ay": random.uniform(3, 9),
        "dur": random.uniform(9, 18),
        "r": random.uniform(1.2, 2.4),
        "pulse": random.uniform(2.5, 5.0),
        "delay": random.uniform(0, 5),
    })

def drift_vals(base, amp):
    return ";".join(f(v) for v in (base, base + amp, base, base - amp, base))

def anim(attr, base, amp, dur):
    return (f'<animate attributeName="{attr}" values="{drift_vals(base, amp)}" '
            f'keyTimes="0;0.25;0.5;0.75;1" calcMode="spline" keySplines="{SPLINE}" '
            f'dur="{f(dur)}s" repeatCount="indefinite"/>')

edges = []
for i, a in enumerate(nodes):
    for j in range(i + 1, len(nodes)):
        b = nodes[j]
        d = math.hypot(a["x"] - b["x"], a["y"] - b["y"])
        if d < 150:
            edges.append((i, j, d))

parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{NAME} - Gen AI / ML Engineer">')
parts.append(f'''<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#010409"/>
  </linearGradient>
  <radialGradient id="glowL" cx="0.18" cy="0.5" r="0.55">
    <stop offset="0" stop-color="#8957e5" stop-opacity="0.22"/><stop offset="1" stop-color="#8957e5" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="glowR" cx="0.92" cy="0.5" r="0.35">
    <stop offset="0" stop-color="#1f6feb" stop-opacity="0.16"/><stop offset="1" stop-color="#1f6feb" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#bc8cff"/><stop offset="1" stop-color="#58a6ff"/>
  </linearGradient>
  <linearGradient id="term" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#21262d"/><stop offset="1" stop-color="#161b22"/>
  </linearGradient>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="2.2"/>
  </filter>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="#000" flood-opacity="0.6"/>
  </filter>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>''')
parts.append('<g clip-path="url(#frame)">')
parts.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
parts.append(f'<rect width="{W}" height="{H}" fill="url(#glowL)"><animate attributeName="opacity" values="0.7;1;0.7" dur="7s" repeatCount="indefinite"/></rect>')
parts.append(f'<rect width="{W}" height="{H}" fill="url(#glowR)"><animate attributeName="opacity" values="1;0.6;1" dur="9s" repeatCount="indefinite"/></rect>')

# two parallax layers: edges + nodes drift as a group, nodes pulse individually
layers = ([], [])
for idx, n in enumerate(nodes):
    layers[idx % 2].append(n)
layer_cfg = [("18s", "0 0;7 -4;0 0;-6 5;0 0", 1.0), ("26s", "0 0;-5 6;0 0;6 -4;0 0", 0.8)]
for li, (lnodes, (ldur, lvals, lscale)) in enumerate(zip(layers, layer_cfg)):
    ledges = []
    for i, a in enumerate(lnodes):
        for j in range(i + 1, len(lnodes)):
            b = lnodes[j]
            d = math.hypot(a["x"] - b["x"], a["y"] - b["y"])
            if d < 175:
                ledges.append((a, b, d))
    parts.append(f'<g opacity="{lscale}">')
    parts.append(f'<animateTransform attributeName="transform" type="translate" values="{lvals}" keyTimes="0;0.25;0.5;0.75;1" calcMode="spline" keySplines="{SPLINE}" dur="{ldur}" repeatCount="indefinite"/>')
    parts.append('<g stroke="#8b949e" stroke-width="0.7">')
    for a, b, d in ledges:
        op = max(0.06, 0.34 * (1 - d / 175))
        parts.append(f'<line x1="{f(a["x"])}" y1="{f(a["y"])}" x2="{f(b["x"])}" y2="{f(b["y"])}" stroke-opacity="{op:.2f}"/>')
    parts.append('</g><g fill="#c9d1d9">')
    for n in lnodes:
        parts.append(
            f'<circle cx="{f(n["x"])}" cy="{f(n["y"])}" r="{f(n["r"])}">'
            f'<animate attributeName="opacity" values="0.35;1;0.35" dur="{f(n["pulse"])}s" begin="{f(n["delay"])}s" repeatCount="indefinite"/>'
            '</circle>')
    parts.append('</g>')
    # travelling signals along a few edges of this layer
    for k, (a, b, d) in enumerate(random.sample(ledges, min(5, len(ledges)))):
        if random.random() < 0.5:
            a, b = b, a
        dur = random.uniform(2.2, 4.0)
        begin = random.uniform(0, 8)
        color = "#bc8cff" if (k + li) % 2 else "#58a6ff"
        parts.append(
            f'<circle r="2.2" fill="{color}" filter="url(#soft)" opacity="0">'
            f'<animateMotion path="M{f(a["x"])} {f(a["y"])} L{f(b["x"])} {f(b["y"])}" dur="{f(dur)}s" begin="{f(begin)}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.15;0.85;1" dur="{f(dur)}s" begin="{f(begin)}s" repeatCount="indefinite"/>'
            '</circle>')
    parts.append('</g>')
    edges_total = globals().setdefault("edges_total", 0) + len(ledges)
    globals()["edges_total"] = edges_total

# --- name block --------------------------------------------------------------
name_x, name_y = 28, 98
parts.append('<g opacity="0">')
parts.append('<animate attributeName="opacity" from="0" to="1" dur="1.1s" begin="0.2s" fill="freeze"/>')
parts.append('<animateTransform attributeName="transform" type="translate" from="0 10" to="0 0" dur="1.1s" begin="0.2s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>')
parts.append(f'<text x="{name_x}" y="{name_y}" font-family="{FONT}" font-size="40" font-weight="600" fill="#e6edf3" letter-spacing="-0.5">{NAME}</text>')
# accent underline that draws itself
parts.append(f'<rect x="{name_x}" y="{name_y + 10}" width="0" height="2" rx="1" fill="url(#accent)">'
             '<animate attributeName="width" from="0" to="120" dur="0.9s" begin="0.9s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></rect>')
parts.append('</g>')

# --- typed roles ---------------------------------------------------------------
# One discrete (stepped) timeline per role covering the whole cycle:
# type char-by-char -> hold -> backspace char-by-char -> hidden until the cycle wraps.
role_x, role_y, role_fs = 28, 138, 18
TYPE_CH, ERASE_CH, HOLD_T, GAP_T = 0.045, 0.045, 3.2, 0.6
CUR_GAP, CUR_W, CUR_H = 7, 11, 2.5
slots = [TYPE_CH * len(r) + HOLD_T + ERASE_CH * len(r) + GAP_T for r in ROLES]
cycle = sum(slots)

parts.append(f'<g font-family="{FONT}" font-size="{role_fs}" fill="#bc8cff" font-weight="500">')
begin = 0.0
for i, role in enumerate(ROLES):
    n = len(role)
    width = round(role_fs * 0.53 * n)
    # timeline: (time, chars visible)
    tl = [(k * TYPE_CH, k) for k in range(1, n + 1)]
    t_hold_end = n * TYPE_CH + HOLD_T
    tl += [(t_hold_end + (n - k) * ERASE_CH, k) for k in range(n - 1, -1, -1)]
    t_erase_end = tl[-1][0]
    times = [t for t, _ in tl]
    w_vals = [f(width * k / n + (6 if k == n else 2)) for _, k in tl]
    x_vals = [f(role_x + width * k / n + CUR_GAP) for _, k in tl]
    kt = ";".join(f"{k:.5f}" for k in [0.0] + [t / cycle for t in times] + [1.0])
    wv = ";".join(["0"] + w_vals + ["0"])
    xv = ";".join([f(role_x + CUR_GAP)] + x_vals + [f(role_x + CUR_GAP)])
    parts.append(f'<clipPath id="clip{i}">')
    parts.append(
        f'<rect x="{role_x - 2}" y="{role_y - role_fs}" width="0" height="{role_fs + 8}">'
        f'<animate attributeName="width" values="{wv}" keyTimes="{kt}" calcMode="discrete" '
        f'dur="{f(cycle)}s" begin="{f(begin)}s" repeatCount="indefinite"/>'
        '</rect>')
    parts.append('</clipPath>')
    parts.append(f'<text x="{role_x}" y="{role_y}" textLength="{width}" lengthAdjust="spacing" clip-path="url(#clip{i})">{html.escape(role)}</text>')
    # underscore cursor: visible from first keystroke until the last backspace, follows the head
    t_on = TYPE_CH * 0.5 / cycle
    t_off = (t_erase_end + ERASE_CH) / cycle
    parts.append(
        f'<rect x="{f(role_x + CUR_GAP)}" y="{role_y + 1}" width="{CUR_W}" height="{CUR_H}" rx="1" fill="#58a6ff" opacity="0">'
        f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;{t_on:.5f};{t_off:.5f};1" calcMode="discrete" '
        f'dur="{f(cycle)}s" begin="{f(begin)}s" repeatCount="indefinite"/>'
        f'<animate attributeName="x" values="{xv}" keyTimes="{kt}" calcMode="discrete" '
        f'dur="{f(cycle)}s" begin="{f(begin)}s" repeatCount="indefinite"/>'
        '</rect>')
    begin += slots[i]
parts.append('</g>')

# --- terminal icon -----------------------------------------------------------
tx, ty, tw, th = 846, 58, 84, 84
parts.append('<g filter="url(#shadow)">')
parts.append(f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" dur="5s" repeatCount="indefinite" calcMode="spline" keySplines="0.42 0 0.58 1;0.42 0 0.58 1"/>')
parts.append(f'<g transform="rotate(-8 {tx + tw/2} {ty + th/2})">')
parts.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="18" fill="url(#term)" stroke="#30363d" stroke-width="1"/>')
parts.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="18" fill="none" stroke="url(#accent)" stroke-width="1.2" opacity="0.35">'
             '<animate attributeName="opacity" values="0.2;0.7;0.2" dur="3.5s" repeatCount="indefinite"/></rect>')
for k, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
    parts.append(f'<circle cx="{tx + 16 + k * 10}" cy="{ty + 16}" r="3" fill="{c}"/>')
# prompt chevron and underscore cursor
px, py = tx + 20, ty + 56
parts.append(f'<path d="M{px} {py - 18} l12 9 l-12 9" fill="none" stroke="#e6edf3" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
parts.append(f'<rect x="{px + 20}" y="{py - 3}" width="18" height="4" rx="2" fill="#58a6ff">'
             '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/></rect>')
parts.append('</g></g>')

parts.append('</g>')  # frame clip
parts.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="#30363d"/>')
parts.append('</svg>')

svg = "\n".join(parts)
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(svg)
print(f"wrote {OUT}: {len(svg)/1024:.1f} KB, {len(nodes)} nodes, {edges_total} edges")
