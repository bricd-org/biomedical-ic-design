"""Write assets/figs/ch12_leadoff.svg: DC and AC lead-off detection (Chapter 12)."""
import os

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "figs", "ch12_leadoff.svg")
INK, SEC, AMB, BLU, GRN, RED = "#1D2A30", "#56656B", "#9A6212", "#1F64A8", "#1A7A4C", "#B5473A"
o = []
a = o.append
a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 350" width="720" height="350" '
  'font-family="\'Libre Franklin\', \'Helvetica Neue\', Arial, sans-serif">')
a('  <title>Lead-off detection: a DC current with a rail detector, and an AC current above the band measured as an impedance</title>')
a('  <defs>')
for mid, col in (("oa", INK), ("ok", AMB)):
    a(f'    <marker id="{mid}" viewBox="0 0 10 10" refX="10" refY="5" markerUnits="userSpaceOnUse" markerWidth="7" '
      f'markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{col}"/></marker>')
a('  </defs>')


def arrow(d, col=INK, w=1.5):
    a(f'  <path d="{d}" stroke="{col}" stroke-width="{w}" fill="none" marker-end="url(#{"ok" if col == AMB else "oa"})"/>')


def text(x, y, t, size=9, col=SEC, anchor="start", bold=False, italic=False):
    fw = ' font-weight="700"' if bold else ""
    fs = ' font-style="italic"' if italic else ""
    a(f'  <text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{fw}{fs}>{t}</text>')


def electrodes(ytop, ybot, yp, yn):
    a(f'  <rect x="10" y="{ytop}" width="54" height="{ybot - ytop}" rx="14" fill="#FBF1DF" stroke="{INK}" stroke-width="1.5"/>')
    text(37, (ytop + ybot) / 2 + 4, "body", 10.5, INK, "middle", True)
    for y in (yp, yn):
        a(f'  <path d="M64 {y} H96 M124 {y} H190" stroke="{INK}" stroke-width="1.5" fill="none"/>')
        a(f'  <rect x="96" y="{y - 7}" width="28" height="14" rx="2" fill="#fff" stroke="{INK}" stroke-width="1.4"/>')
        text(110, y - 11, "Z<tspan font-size=\"6.5\" dy=\"2\">e</tspan>", 9, SEC, "middle", italic=True)
        a(f'  <circle cx="190" cy="{y}" r="2.6" fill="{INK}"/>')
    text(178, yp - 6, "IN+", 8.5, INK, "end", True)
    text(178, yn + 13, "IN−", 8.5, INK, "end", True)


def lna(y0, y1, lines):
    a(f'  <rect x="250" y="{y0}" width="80" height="{y1 - y0}" rx="3" fill="#E4EEF8" stroke="{INK}" stroke-width="1.5"/>')
    ym = (y0 + y1) / 2 - 6.5 * (len(lines) - 1) + 3
    for k, (t, b) in enumerate(lines):
        text(290, ym + 13 * k, t, 10 if b else 8.5, INK if b else SEC, "middle", bool(b))


def source(cx, cy, col, label, up=False, ac=False):
    a(f'  <circle cx="{cx}" cy="{cy}" r="10" fill="#fff" stroke="{col}" stroke-width="1.6"/>')
    if ac:
        a(f'  <path d="M{cx - 6} {cy} q3 -6 6 0 t6 0" stroke="{col}" stroke-width="1.5" fill="none"/>')
    else:
        a(f'  <path d="M{cx} {cy + (5 if up else -5)} V{cy + (-5 if up else 5)}" stroke="{col}" stroke-width="1.5" '
          f'marker-end="url(#ok)"/>')
    text(cx + 15, cy + 3, label, 9, col)


# ---------------- (a) DC lead-off ----------------
text(8, 16, "(a) DC lead-off: a few nanoamperes and a rail detector", 11.5, INK, bold=True)
YP, YN = 74, 136
electrodes(44, 166, YP, YN)
source(190, 38, AMB, "6 nA from the supply")
a(f'  <path d="M190 48 V{YP}" stroke="{AMB}" stroke-width="1.4"/>')
source(190, 168, AMB, "6 nA to ground")
a(f'  <path d="M190 {YN} V158" stroke="{AMB}" stroke-width="1.4"/>')
arrow(f"M190 {YP} H250")
arrow(f"M190 {YN} H250")
lna(54, 156, [("chopped LNA", 1), ("+ DC servo", 1), ("(Chapter 10)", 0)])
arrow("M330 80 H370")
text(374, 84, "signal", 9, INK)
arrow("M330 130 H370")
text(374, 127, "flag: servo output", 9, RED)
text(374, 139, "or comparator at a rail", 9, RED)
text(10, 180, "current returns through the RL electrode", 8.5, SEC)
# inset: v(IN+) when the contact is lost
X0, X1, Yb, Yt = 530, 708, 150, 46
a(f'  <path d="M{X0} {Yb} H{X1} M{X0} {Yb} V{Yt}" stroke="#B9C6C9" stroke-width="1"/>')
yrail = Yt + 10
a(f'  <path d="M{X0} {yrail} H{X1}" stroke="#B9C6C9" stroke-width="0.8" stroke-dasharray="3 2"/>')
text(X1, yrail - 4, "rail", 8, SEC, "end")
yth = yrail + 26
a(f'  <path d="M{X0} {yth} H{X1}" stroke="{RED}" stroke-width="0.9" stroke-dasharray="4 3"/>')
text(X0 + 4, yth - 4, "flag threshold", 8, RED)
t = np.linspace(0, 1, 200)
tl = 0.55
v = np.where(t < tl, 0.06, 0.06 + 0.94 * (1 - np.exp(-(t - tl) / 0.12)))
pts = " L".join(f"{X0 + (X1 - X0) * ti:.1f} {Yb - 6 - (Yb - 6 - yrail) * vi:.1f}" for ti, vi in zip(t, v))
a(f'  <path d="M{pts}" stroke="{BLU}" stroke-width="1.6" fill="none"/>')
a(f'  <path d="M{X0 + (X1 - X0) * tl:.1f} {Yb} V{Yb - 18}" stroke="{SEC}" stroke-width="0.8" stroke-dasharray="2 2"/>')
text(X0 + 4, Yb - 13, "6 nA × 1 MΩ = 6 mV", 8, BLU)
text(X0 + (X1 - X0) * tl + 4, Yb + 12, "contact lost", 8, SEC)
text(X0, Yt - 4, "v(IN+): drifts to the rail in milliseconds", 8.5, INK)

# ---------------- (b) AC lead-off ----------------
a(f'  <path d="M8 196 H712" stroke="#E1E8E8" stroke-width="1.2"/>')
text(8, 216, "(b) AC lead-off: a small current above the band, measured as an impedance", 11.5, INK, bold=True)
YP, YN = 252, 316
electrodes(228, 340, YP, YN)
source(190, 284, AMB, "", ac=True)
a(f'  <path d="M190 {YP} V274 M190 294 V{YN}" stroke="{AMB}" stroke-width="1.4"/>')
text(176, 281, "I<tspan font-size=\"6.5\" dy=\"2\">AC</tspan>", 9, AMB, "end", italic=True)
text(176, 294, "above the band", 8, AMB, "end")
arrow(f"M190 {YP} H250")
arrow(f"M190 {YN} H250")
lna(236, 332, [("LNA", 1), ("the same", 0), ("channel", 0)])
a(f'  <path d="M330 284 H360" stroke="{INK}" stroke-width="1.5"/>')
a(f'  <circle cx="360" cy="284" r="2.6" fill="{INK}"/>')
arrow("M360 284 V250 H400")
arrow("M360 284 V318 H400")
for y0, l1, l2 in ((234, "low-pass, decimate", "signal band only"), (302, "demodulate at f", "voltage → |Z<tspan font-size=\"6.5\" dy=\"2\">e</tspan><tspan dy=\"-2\">|, phase</tspan>")):
    a(f'  <rect x="400" y="{y0}" width="132" height="32" rx="3" fill="#FBF1DF" stroke="{INK}" stroke-width="1.4"/>')
    text(466, y0 + 14, l1 + ("<tspan font-size=\"6.5\" dy=\"2\">AC</tspan>" if "demod" in l1 else ""), 9.5, INK, "middle", True)
    text(466, y0 + 26, l2, 8.5, SEC, "middle")
arrow("M532 250 H564")
arrow("M532 318 H564")
text(568, 254, "ECG, EEG", 9, INK)
text(568, 314, "impedance of every", 9, INK)
text(568, 326, "electrode, continuously", 9, INK)
text(568, 338, "(I/Q readout, Chapter 28)", 8.5, SEC)
text(568, 280, "keep the injected current inside", 8.5, AMB)
text(568, 292, "the patient-current limit (Chapter 4)", 8.5, AMB)
a('</svg>')
open(OUT, "w").write("\n".join(o) + "\n")
print("wrote", OUT)
