"""Write assets/figs/ch29_floorplan.svg (Open-BioAFE floorplan concept, core drawn to scale)."""
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "figs", "ch29_floorplan.svg")
INK, SEC, AMB, GRN = "#1D2A30", "#56656B", "#9A6212", "#1A7A4C"
o = []
a = o.append
a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 440" width="720" height="440" '
  'font-family="\'Libre Franklin\', \'Helvetica Neue\', Arial, sans-serif">')
a('  <title>Open-BioAFE floorplan concept: input pads and channel strips at one edge, shared analog in the middle, '
  'digital behind a guard ring at the opposite edge</title>')
a(f'  <text x="20" y="16" font-size="11.5" font-weight="700" fill="{INK}">Microvolts at one edge, clocks at the other (concept, core to scale)</text>')
# die, seal ring and core
a(f'  <rect x="20" y="26" width="490" height="380" rx="4" fill="#fff" stroke="{INK}" stroke-width="1.8"/>')
a(f'  <rect x="25" y="31" width="480" height="370" rx="3" fill="none" stroke="#B9C6C9" stroke-width="1"/>')
a(f'  <rect x="68" y="78" width="394" height="280" fill="#F7F9F9" stroke="{SEC}" stroke-width="0.8" stroke-dasharray="3 2"/>')

# channel strips
for i in range(8):
    x0 = 74 + 48 * i
    cx = x0 + 23
    a(f'  <g stroke="{INK}" stroke-width="0.9">')
    a(f'    <rect x="{x0}" y="82" width="46" height="14" fill="#DCE5E8"/>')
    a(f'    <rect x="{x0}" y="96" width="46" height="82" fill="#E4EEF8"/>')
    a(f'    <rect x="{x0}" y="178" width="46" height="44" fill="#D6E6F5"/>')
    a(f'    <rect x="{x0}" y="222" width="46" height="28" fill="#C6DAEF"/>')
    a('  </g>')
    # two 20 pF input capacitors
    a(f'  <g fill="#9DBBDD" stroke="#1F64A8" stroke-width="0.7">'
      f'<rect x="{x0 + 5}" y="102" width="16" height="16"/><rect x="{x0 + 25}" y="102" width="16" height="16"/></g>')
    a(f'  <text x="{cx}" y="140" font-size="9" font-weight="700" fill="{INK}" text-anchor="middle">CH{i + 1}</text>')
    a(f'  <text x="{cx}" y="154" font-size="7.5" fill="{SEC}" text-anchor="middle">LNA</text>')
    a(f'  <text x="{cx}" y="198" font-size="7.5" fill="{SEC}" text-anchor="middle">PGA</text>')
    a(f'  <text x="{cx}" y="208" font-size="7.5" fill="{SEC}" text-anchor="middle">filter</text>')
    a(f'  <text x="{cx}" y="240" font-size="8.5" fill="{INK}" text-anchor="middle">ΔΣ</text>')
    # input pads and their short traces
    for k, (dx, sgn) in enumerate(((5, "+"), (25, "−"))):
        px = x0 + dx
        a(f'  <path d="M{px + 8} 68 V82" stroke="{INK}" stroke-width="1"/>')
        a(f'  <rect x="{px}" y="38" width="16" height="30" rx="2" fill="#C98A1C" stroke="{AMB}" stroke-width="0.8"/>')
        a(f'  <text transform="translate({px + 11},53) rotate(-90)" font-size="7" font-weight="700" fill="#fff" '
          f'text-anchor="middle">IN{i + 1}{sgn}</text>')

# shared analog row
mids = [(74, 54, "RLD", "drive"), (132, 90, "MUX + SAR", "12 b"), (226, 64, "bandgap,", "bias"),
        (294, 56, "references", "and buffers"), (354, 50, "3 LDOs", ""), (408, 48, "bioZ", "source")]
for x, w, t1, t2 in mids:
    a(f'  <rect x="{x}" y="258" width="{w}" height="42" fill="#E4EEF8" stroke="{INK}" stroke-width="0.9"/>')
    a(f'  <text x="{x + w / 2}" y="{276 if t2 else 282}" font-size="8.5" font-weight="700" fill="{INK}" text-anchor="middle">{t1}</text>')
    if t2:
        a(f'  <text x="{x + w / 2}" y="289" font-size="7.5" fill="{SEC}" text-anchor="middle">{t2}</text>')

# guard ring and digital
a(f'  <rect x="70" y="307" width="390" height="48" fill="none" stroke="{GRN}" stroke-width="2.4" stroke-dasharray="6 2"/>')
digs = [(76, 64, "clocks"), (144, 116, "decimators"), (264, 116, "features, coding"), (384, 70, "SPI, regs")]
for x, w, t in digs:
    a(f'  <rect x="{x}" y="313" width="{w}" height="36" fill="#FBF1DF" stroke="{AMB}" stroke-width="0.9"/>')
    a(f'  <text x="{x + w / 2}" y="334" font-size="8.5" font-weight="700" fill="{INK}" text-anchor="middle">{t}</text>')

# side pads
def side_pad(x, y, label, fill="#C98A1C"):
    a(f'  <rect x="{x}" y="{y - 9}" width="34" height="18" rx="2" fill="{fill}" stroke="{AMB}" stroke-width="0.8"/>')
    a(f'  <text x="{x + 17}" y="{y + 3}" font-size="7" font-weight="700" fill="#fff" text-anchor="middle">{label}</text>')

for y, lab in ((100, "RLD"), (126, "SHLD"), (152, "BIOZ+"), (200, "VDDA"), (226, "VSSA"), (276, "VDD33"), (330, "VDDD")):
    side_pad(29, y, lab, "#8C9A9F" if lab.startswith("V") else "#C98A1C")
for y, lab in ((100, "BIOZ−"), (152, "REF"), (200, "VDDA"), (226, "VSSA"), (264, "TESTA"), (290, "TESTB"), (330, "VSSD")):
    side_pad(467, y, lab, "#8C9A9F" if lab.startswith("V") else "#C98A1C")
# bottom pads
for j, lab in enumerate(("CLKIN", "RESETn", "CSn", "SCLK", "MOSI", "MISO", "DRDY", "VDDIO", "VSSIO")):
    px = 104 + 38 * j
    fill = "#8C9A9F" if lab.startswith("V") else "#C98A1C"
    a(f'  <rect x="{px}" y="364" width="16" height="30" rx="2" fill="{fill}" stroke="{AMB}" stroke-width="0.8"/>')
    a(f'  <text transform="translate({px + 11},379) rotate(-90)" font-size="6.5" font-weight="700" fill="#fff" '
      f'text-anchor="middle">{lab}</text>')

# annotations on the right, with brackets
def bracket(y0, y1):
    a(f'  <path d="M516 {y0} H521 V{y1} H516" stroke="{SEC}" stroke-width="1" fill="none"/>')

def note(y, lines, bold_first=True):
    for n, s in enumerate(lines):
        w = ' font-weight="700"' if (n == 0 and bold_first) else ''
        col = INK if (n == 0 and bold_first) else SEC
        a(f'  <text x="528" y="{y + 11 * n}" font-size="8.8"{w} fill="{col}">{s}</text>')

bracket(38, 68); note(50, ["16 input pads on one edge", "short, guarded traces (Ch 12)"])
bracket(82, 250)
a(f'  <text x="528" y="80" font-size="8.8" font-weight="700" fill="{INK}">8 channel strips, 0.2 × 0.7 mm</text>')
for y, s in ((92, "protection, 2 × 5 kΩ"), (113, "2 × 20 pF MIM input capacitors"), (150, "LNA, servo and boosting"),
             (203, "PGA, 4th-order Gm-C filter"), (239, "16-b incremental ΔΣ")):
    a(f'  <path d="M521 {y - 3} H525" stroke="{SEC}" stroke-width="1"/>')
    a(f'  <text x="{540 if y == 113 else 528}" y="{y}" font-size="8.5" fill="{SEC}">{s}</text>')
a('  <rect x="528" y="105" width="8" height="8" fill="#9DBBDD" stroke="#1F64A8" stroke-width="0.7"/>')
bracket(258, 300); note(276, ["shared analog, quiet", "SAR, references, LDOs, RLD"])
bracket(307, 355); note(322, ["guard ring, wide gap,", "own supply and substrate ties:", "clocks, decimators, features, SPI"])
bracket(364, 394); note(377, ["digital and supply pads", "on the far edge"])

a(f'  <text x="20" y="424" font-size="8.5" fill="{SEC}">Core about 1.6 × 1.06 mm ≈ 1.7 mm² (Section 29.3), drawn to scale: the eight strips take two thirds of it. '
  'Pad count and positions are illustrative.</text>')
a(f'  <text x="20" y="436" font-size="8.5" fill="{SEC}">blue: analog · gold: digital · green: guard ring · gold pads: signals · grey pads: supplies</text>')
a('</svg>')
open(OUT, "w").write("\n".join(o) + "\n")
print("wrote", OUT)
