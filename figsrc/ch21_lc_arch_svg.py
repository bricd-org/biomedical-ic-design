"""Write assets/figs/ch21_lc_arch.svg: how a level-crossing ADC works (block diagram and waveform)."""
import os

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "figs", "ch21_lc_arch.svg")
INK, SEC, AMB, BLU, GRN, RED = "#1D2A30", "#56656B", "#9A6212", "#1F64A8", "#1A7A4C", "#B5473A"
o = []
a = o.append
a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 410" width="720" height="410" '
  'font-family="\'Libre Franklin\', \'Helvetica Neue\', Arial, sans-serif">')
a('  <title>A level-crossing ADC: two comparators around a tracking DAC level, and the events it produces from a waveform</title>')
a('  <defs>')
for mid, col in (("la", INK), ("lk", AMB)):
    a(f'    <marker id="{mid}" viewBox="0 0 10 10" refX="10" refY="5" markerUnits="userSpaceOnUse" markerWidth="7" '
      f'markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{col}"/></marker>')
a('  </defs>')
a(f'  <text x="8" y="16" font-size="11.5" font-weight="700" fill="{INK}">(a) the converter: no sampling clock, only two comparators</text>')


def arrow(d, col=INK, w=1.5, dash=False):
    mk = "lk" if col == AMB else "la"
    ds = ' stroke-dasharray="4 3"' if dash else ""
    a(f'  <path d="{d}" stroke="{col}" stroke-width="{w}" fill="none"{ds} marker-end="url(#{mk})"/>')


# input and comparators
a(f'  <text x="8" y="90" font-size="12" font-style="italic" fill="{INK}">v(t)</text>')
a(f'  <path d="M34 86 H70 M70 48 V122 M70 48 H112 M70 122 H112" stroke="{INK}" stroke-width="1.5" fill="none"/>')
a(f'  <circle cx="70" cy="86" r="2.8" fill="{INK}"/>')
for y0 in (40, 98):
    a(f'  <path d="M112 {y0} L112 {y0 + 32} L152 {y0 + 16} Z" fill="#E4EEF8" stroke="{INK}" stroke-width="1.5"/>')
# references from the DAC (wires into the comparators' second inputs)
a(f'  <path d="M200 192 H90 V64 H112 M90 106 H112" stroke="{INK}" stroke-width="1.5" fill="none"/>')
a(f'  <circle cx="90" cy="106" r="2.6" fill="{INK}"/>')
a(f'  <text x="96" y="186" font-size="8.5" fill="{SEC}">v<tspan font-size="6.5" dy="2">DAC</tspan><tspan dy="-2"> ± δ</tspan></text>')
arrow("M152 56 H200")
arrow("M152 114 H200")
a(f'  <text x="176" y="50" font-size="9" fill="{GRN}" text-anchor="middle">up</text>')
a(f'  <text x="176" y="108" font-size="9" fill="{RED}" text-anchor="middle">down</text>')
a(f'  <text x="132" y="34" font-size="8.5" fill="{SEC}" text-anchor="middle">v &gt; v<tspan font-size="6.5" dy="2">DAC</tspan><tspan dy="-2"> + δ</tspan></text>')
a(f'  <text x="132" y="146" font-size="8.5" fill="{SEC}" text-anchor="middle">v &lt; v<tspan font-size="6.5" dy="2">DAC</tspan><tspan dy="-2"> − δ</tspan></text>')
# logic and DAC
a(f'  <rect x="200" y="38" width="108" height="94" rx="3" fill="#FBF1DF" stroke="{INK}" stroke-width="1.5"/>')
for t, y, b in (("asynchronous", 70, 1), ("logic", 84, 1), ("up/down counter", 102, 0), ("holds the level code", 115, 0)):
    fw = ' font-weight="700"' if b else ""
    a(f'  <text x="254" y="{y}" font-size="{10 if b else 8.5}"{fw} fill="{INK if b else SEC}" text-anchor="middle">{t}</text>')
a(f'  <rect x="200" y="172" width="108" height="40" rx="3" fill="#E4EEF8" stroke="{INK}" stroke-width="1.5"/>')
a(f'  <text x="254" y="189" font-size="10" font-weight="700" fill="{INK}" text-anchor="middle">DAC</text>')
a(f'  <text x="254" y="203" font-size="8.5" fill="{SEC}" text-anchor="middle">level ± δ</text>')
arrow("M254 132 V172")
# event register with timer clock
a(f'  <rect x="348" y="50" width="112" height="72" rx="3" fill="#FBF1DF" stroke="{INK}" stroke-width="1.5"/>')
for t, y, b in (("event register", 76, 1), ("direction bit", 94, 0), ("+ time stamp", 107, 0)):
    fw = ' font-weight="700"' if b else ""
    a(f'  <text x="404" y="{y}" font-size="{10 if b else 8.5}"{fw} fill="{INK if b else SEC}" text-anchor="middle">{t}</text>')
arrow("M308 86 H348")
arrow("M404 16 V50", AMB)
a(f'  <text x="410" y="28" font-size="8.5" fill="{AMB}">timer clock</text>')
arrow("M460 86 H500")
a(f'  <text x="480" y="80" font-size="9" fill="{INK}" text-anchor="middle">events</text>')
notes = ["Nothing samples the input on a clock:", "a comparator fires when v(t) has moved", "by δ from the last level, the counter",
         "steps, and the DAC moves both thresholds.", "Each event is one bit plus a time stamp,", "so the data rate follows the signal's",
         "activity. The timer's resolution and", "the comparators' delay set the timing error."]
for k, t in enumerate(notes):
    a(f'  <text x="514" y="{56 + 13 * k}" font-size="9" fill="{SEC}">{t}</text>')

# (b) waveform with levels and events
a(f'  <text x="8" y="236" font-size="11.5" font-weight="700" fill="{INK}">(b) the events from one heartbeat</text>')
X0, X1, Y0, H = 70, 700, 400, 150          # plot area: baseline at Y0, height H
t = np.linspace(0, 1, 1200)
v = (0.12 * np.exp(-((t - 0.18) / 0.05) ** 2) + 1.0 * np.exp(-((t - 0.40) / 0.018) ** 2)
     - 0.22 * np.exp(-((t - 0.44) / 0.015) ** 2) + 0.28 * np.exp(-((t - 0.70) / 0.07) ** 2))
D = 0.125                                   # threshold, in units of the R-wave height
lev, ev, ref = [], [], 0.0
for ti, vi in zip(t, v):
    while vi >= ref + D:
        ref += D; ev.append((ti, 1))
    while vi <= ref - D:
        ref -= D; ev.append((ti, -1))
    lev.append(ref)
xs = lambda tt: X0 + (X1 - X0) * tt
ys = lambda vv: Y0 - 8 - (H - 8) * (vv + 0.25) / 1.3
for k in range(-1, 9):
    yy = ys(k * D)
    a(f'  <path d="M{X0} {yy:.1f} H{X1}" stroke="#E1E8E8" stroke-width="0.8"/>')
a(f'  <text x="{X0 - 6}" y="{ys(3 * D):.1f}" font-size="8.5" fill="{SEC}" text-anchor="end">levels</text>')
a(f'  <text x="{X0 - 6}" y="{ys(3 * D) + 11:.1f}" font-size="8.5" fill="{SEC}" text-anchor="end">δ apart</text>')
d = "M" + " L".join(f"{xs(tt):.1f} {ys(vv):.1f}" for tt, vv in zip(t[::4], v[::4]))
a(f'  <path d="{d}" stroke="{BLU}" stroke-width="1.6" fill="none"/>')
d = f"M{xs(0):.1f} {ys(lev[0]):.1f}"
for i in range(1, len(t)):
    if lev[i] != lev[i - 1]:
        d += f" H{xs(t[i]):.1f} V{ys(lev[i]):.1f}"
d += f" H{xs(1):.1f}"
a(f'  <path d="{d}" stroke="{AMB}" stroke-width="1.2" fill="none" stroke-dasharray="3 2"/>')
for tt, s in ev:
    x = xs(tt)
    col = GRN if s > 0 else RED
    a(f'  <circle cx="{x:.1f}" cy="{ys(lev[int(round(tt * 1199))]):.1f}" r="2.3" fill="{col}"/>')
a(f'  <text x="{X1}" y="{ys(1.0) - 4:.1f}" font-size="8.5" fill="{SEC}" text-anchor="end">'
  f'{len(ev)} events in one beat, none on the flat parts</text>')
a(f'  <text x="{xs(0.55):.1f}" y="{ys(0.75):.1f}" font-size="8.5" fill="{AMB}">tracked level</text>')
a(f'  <text x="{xs(0.47):.1f}" y="{ys(0.95):.1f}" font-size="8.5" fill="{GRN}">● up</text>')
a(f'  <text x="{xs(0.47):.1f}" y="{ys(0.95) + 11:.1f}" font-size="8.5" fill="{RED}">● down</text>')
a('</svg>')
open(OUT, "w").write("\n".join(o) + "\n")
print("wrote", OUT, len(ev), "events")
