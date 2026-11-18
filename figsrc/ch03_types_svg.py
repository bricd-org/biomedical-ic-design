"""Write assets/figs/ch03_types.svg: six biopotential electrodes in cross-section (Chapter 3)."""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "figs", "ch03_types.svg")
INK, SEC, AMB, BLU, RED, RULE = "#1D2A30", "#56656B", "#9A6212", "#1F64A8", "#B5473A", "#B9C6C9"
METAL, GEL, FOAM, HAIR = "#C9D0D3", "#E4EEF8", "#EEF1F2", "#5B4636"
PW, PH = 232, 160
o = []
a = o.append


def text(x, y, t, size=9, col=SEC, anchor="start", bold=False):
    fw = ' font-weight="700"' if bold else ""
    a(f'  <text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{fw}>{t}</text>')


def rect(x, y, w, h, fill, stroke="none", sw=1, rx=0):
    a(f'  <rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def skin(px, ys, ye, muscle=None):
    """layered skin across the sketch, from the surface ys down to ye; optional muscle from y=muscle"""
    x0, w = px + 10, PW - 20
    rect(x0, ys + 18, w, ye - ys - 18, "#F9EDE9")
    rect(x0, ys + 6, w, 12, "#F7E3D6")
    rect(x0, ys, w, 6, "#F5E6C8")
    for x in range(int(x0) + 4, int(x0 + w) - 8, 14):
        a(f'  <ellipse cx="{x + 4}" cy="{ys + 12}" rx="5" ry="2.8" fill="none" stroke="#E2C3B0" stroke-width="0.8"/>')
    if muscle:
        rect(x0, muscle, w, ye - muscle, "#F1D2CC")
        for y in range(int(muscle) + 5, int(ye), 6):
            a(f'  <path d="M{x0} {y} H{x0 + w}" stroke="#E0B0A8" stroke-width="0.8"/>')
    a(f'  <path d="M{x0} {ys} H{x0 + w}" stroke="#D9BE8C" stroke-width="1"/>')


def lead(d):
    a(f'  <path d="{d}" stroke="{INK}" stroke-width="2" fill="none" stroke-linejoin="round"/>')


def panel(k, title, notes):
    px, py = 4 + (k % 3) * (PW + 6), 4 + (k // 3) * (PH + 8)
    rect(px, py, PW, PH, "#FCFDFD", "#E1E7E9", 1, 5)
    text(px + 10, py + 18, f"({'abcdef'[k]}) {title}", 10.5, INK, bold=True)
    for j, t in enumerate(notes):
        text(px + 10, py + 138 + 12 * j, t, 8.3, SEC)
    return px, py


a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 340" width="720" height="340" '
  'font-family="\'Libre Franklin\', \'Helvetica Neue\', Arial, sans-serif">')
a('  <title>Six biopotential electrodes in cross-section: metal plate, disposable Ag/AgCl, floating, dry pins, '
  'needle and microelectrode array</title>')

# (a) metal plate with paste, strapped on
px, py = panel(0, "Metal plate", ("Paste under a reusable metal plate,", "strapped to a limb: the oldest ECG lead."))
ys = py + 98
skin(px, ys, py + 124)
rect(px + 60, ys - 6, 112, 6, GEL)
rect(px + 66, ys - 15, 100, 9, METAL, INK, 1.1, 1)
for s in (1, -1):
    xe, xp = (px + 14, px + 66) if s == 1 else (px + PW - 14, px + 166)
    a(f'  <path d="M{xe} {ys} Q{(xe + xp) / 2} {ys - 22} {xp} {ys - 18}" stroke="#C9A86A" stroke-width="5" fill="none" stroke-linecap="round"/>')
lead(f"M{px + 116} {ys - 15} V{py + 44} H{px + PW - 12}")
text(px + 176, ys - 1, "paste", 7.5, BLU)
text(px + 24, ys - 22, "strap", 7.5, AMB)

# (b) disposable foam Ag/AgCl
px, py = panel(1, "Disposable Ag/AgCl", ("Snap, Ag/AgCl disc, gel sponge, foam", "and adhesive: the clinical standard."))
ys = py + 98
skin(px, ys, py + 124)
rect(px + 40, ys - 26, 152, 26, FOAM, RULE, 1, 2)
rect(px + 86, ys - 20, 60, 20, GEL, RULE, 0.8)
rect(px + 86, ys - 26, 60, 6, METAL, INK, 1)
rect(px + 86, ys - 22, 60, 2, "#8E979B")
for xa, xb in ((px + 40, px + 86), (px + 146, px + 192)):
    a(f'  <path d="M{xa} {ys - 1.2} H{xb}" stroke="#C9A86A" stroke-width="2.4"/>')
rect(px + 106, ys - 42, 20, 16, METAL, INK, 1, 4)
lead(f"M{px + 106} {ys - 36} H{px + 14}")
text(px + 116, ys - 6, "gel", 7.5, BLU, "middle")
text(px + 63, ys - 9, "foam", 7.5, SEC, "middle")
text(px + 132, ys - 32, "snap", 7.5, SEC)
text(px + 150, ys - 29, "Ag/AgCl", 7.5, SEC)

# (c) floating, recessed electrode
px, py = panel(2, "Floating (recessed)", ("The disc sits back in a gel-filled cup,", "off the skin: less motion artefact."))
ys = py + 98
skin(px, ys, py + 124)
a(f'  <path d="M{px + 64} {ys} V{ys - 46} H{px + 168} V{ys} H{px + 152} V{ys - 36} H{px + 80} V{ys} Z" fill="#DDE3E5" stroke="{INK}" stroke-width="1"/>')
rect(px + 80, ys - 36, 72, 36, GEL)
rect(px + 86, ys - 36, 60, 6, METAL, INK, 1)
for xa, xb in ((px + 64, px + 80), (px + 152, px + 168)):
    a(f'  <path d="M{xa} {ys - 1.2} H{xb}" stroke="#C9A86A" stroke-width="2.4"/>')
lead(f"M{px + 116} {ys - 46} V{py + 34} H{px + PW - 12}")
text(px + 116, ys - 12, "gel", 7.5, BLU, "middle")
text(px + 172, ys - 30, "metal disc", 7.5, SEC)
text(px + 172, ys - 20, "held off", 7.5, SEC)
text(px + 172, ys - 10, "the skin", 7.5, SEC)

# (d) dry pins through hair
px, py = panel(3, "Dry pins", ("Pins part the hair to reach the skin:", "no gel, but high, unstable impedance."))
ys = py + 102
skin(px, ys, py + 124)
for j, (x, h, c) in enumerate(((px + 50, 40, 8), (px + 76, 46, -6), (px + 98, 30, 6), (px + 124, 44, -8), (px + 150, 34, 7),
                               (px + 178, 46, -5), (px + 196, 30, 6))):
    a(f'  <path d="M{x} {ys} q{c} {-h / 2} {c / 2} {-h}" stroke="{HAIR}" stroke-width="1.1" fill="none"/>')
rect(px + 56, py + 46, 120, 12, METAL, INK, 1, 2)
for j in range(7):
    x = px + 64 + 17.3 * j
    a(f'  <path d="M{x - 2.6:g} {py + 58} V{ys - 3} Q{x:g} {ys + 1} {x + 2.6:g} {ys - 3} V{py + 58} Z" fill="#A9B2B6" stroke="{INK}" stroke-width="0.8"/>')
lead(f"M{px + 116} {py + 46} V{py + 34} H{px + PW - 12}")
text(px + 214, ys - 26, "hair", 7.5, HAIR, "end")

# (e) needle into muscle
px, py = panel(4, "Needle", ("Through the skin into the muscle, for", "EMG: no stratum corneum in the path."))
ys = py + 52
skin(px, ys, py + 124, muscle=py + 84)
a(f'  <path d="M{px + 72} {py + 31} L{px + 151} {py + 106} L{px + 76} {py + 27} Z" fill="#8E979B" stroke="{INK}" stroke-width="0.8" stroke-linejoin="round"/>')
rect(px + 48, py + 22, 28, 12, "#DCC9A0", INK, 1, 3)
a(f'  <circle cx="{px + 146}" cy="{py + 101}" r="3" fill="{AMB}"/>')
lead(f"M{px + 48} {py + 28} H{px + 14}")
text(px + 214, py + 118, "muscle", 7.5, RED, "end")
text(px + 158, py + 98, "recording site", 7.5, AMB)

# (f) microelectrode array in cortex
px, py = panel(5, "Microelectrode array", ("Implanted shanks, sites tens of µm", "across: capacitive, hundreds of kΩ at 1 kHz."))
yt = py + 70
rect(px + 10, yt, PW - 20, py + 124 - yt, "#F3DDD8")
a(f'  <path d="M{px + 10} {yt} H{px + PW - 10}" stroke="#D9A9A0" stroke-width="1.2"/>')
for x, y in ((px + 30, py + 92), (px + 44, py + 112), (px + 88, py + 86), (px + 118, py + 116), (px + 152, py + 90),
             (px + 186, py + 108), (px + 200, py + 84)):
    a(f'  <path d="M{x} {y - 4} L{x + 4} {y + 3} L{x - 4} {y + 3} Z" fill="{RED}" fill-opacity=".45"/>')
for j in range(6):
    x = px + 70 + 19 * j
    a(f'  <path d="M{x - 3} {py + 58} L{x + 3} {py + 58} L{x} {py + 112} Z" fill="#B7BEC2" stroke="{INK}" stroke-width="0.7" stroke-linejoin="round"/>')
    a(f'  <circle cx="{x}" cy="{py + 104}" r="2" fill="{AMB}"/>')
rect(px + 60, py + 46, 114, 12, "#B7BEC2", INK, 1, 2)
a(f'  <path d="M{px + 174} {py + 52} C{px + 196} {py + 52} {px + 196} {py + 36} {px + PW - 12} {py + 36}" stroke="#C9A86A" stroke-width="3" fill="none"/>')
text(px + 18, yt + 12, "cortex", 7.5, RED)
text(px + 186, py + 62, "flex cable", 7.5, AMB)
a('</svg>')
with open(OUT, "w") as f:
    f.write("\n".join(o) + "\n")
print("saved", os.path.abspath(OUT))
