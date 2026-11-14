"""Write assets/figs/ch29_testchip.svg: the Open-BioAFE test chip concept with its test board.

Grid: every pair of blocks joined by an arrow is at least 32 px apart, so each arrow shows a real
shaft; check with  python tools/check_arrows.py assets/figs/ch29_testchip.svg
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "figs", "ch29_testchip.svg")
INK, SEC, AMB, BLU = "#1D2A30", "#56656B", "#9A6212", "#1F64A8"
C1, C2, C3 = (84, 206), (250, 336), (368, 508)          # columns (x0, x1)
R1, R2, R3, R4 = (60, 144), (176, 214), (246, 284), (316, 354)   # rows (y0, y1)
YM = 96                                                  # main signal line
o = []
a = o.append
a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 400" width="720" height="400" '
  'font-family="\'Libre Franklin\', \'Helvetica Neue\', Arial, sans-serif">')
a('  <title>The Open-BioAFE test chip concept: the chip, its test access and the test board</title>')
a('  <defs>')
for mid, col in (("ah", INK), ("aa", AMB)):
    a(f'    <marker id="{mid}" viewBox="0 0 10 10" refX="10" refY="5" markerUnits="userSpaceOnUse" '
      f'markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{col}"/></marker>')
a('  </defs>')

# die
a(f'  <rect x="52" y="24" width="488" height="368" rx="6" fill="#F7F9F9" stroke="{INK}" stroke-width="1.8"/>')
a(f'  <text x="64" y="44" font-size="10.5" font-weight="700" fill="{BLU}">OPEN-BIOAFE TEST CHIP · IHP SG13G2 (concept)</text>')


def box(c, r, fill, lines, dashed=False, stroke=INK):
    (x0, x1), (y0, y1) = c, r
    dash = ' stroke-dasharray="4 3"' if dashed else ""
    a(f'  <rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1.4"{dash}/>')
    cx = (x0 + x1) / 2
    n = len(lines)
    ytop = (y0 + y1) / 2 - 6.5 * (n - 1) + 3.5
    for k, (txt, bold) in enumerate(lines):
        col = (AMB if dashed else INK) if bold else (AMB if dashed else SEC)
        fs, fw = (10, ' font-weight="700"') if bold else (8.5, "")
        a(f'  <text x="{cx}" y="{ytop + 13 * k:.1f}" font-size="{fs}"{fw} fill="{col}" text-anchor="middle">{txt}</text>')


def arrow(d, col=INK, dashed=False, w=1.5):
    mk = "aa" if col == AMB else "ah"
    dash = ' stroke-dasharray="4 3"' if dashed else ""
    a(f'  <path d="{d}" stroke="{col}" stroke-width="{w}" fill="none"{dash} marker-end="url(#{mk})"/>')


# signal path
box(C1, R1, "#E4EEF8", [("8 channels", 1), ("chopped LNA, servo,", 0), ("boost, PGA, Gm-C filter", 0), ("(Ch 7–12)", 0)])
box(C2, R1, "#E4EEF8", [("8 × ΔΣ", 1), ("16 b, 500 S/s", 0), ("(Ch 20)", 0)])
(x0, x1), (y0, y1) = C3, R1
a(f'  <rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="3" fill="#FBF1DF" stroke="{INK}" stroke-width="1.4"/>')
for txt, y, bold in (("digital back end", 78, 1), ("decimators, features,", 92, 0), ("coding, SPI (Ch 23–27)", 104, 0)):
    fw = ' font-weight="700"' if bold else ""
    a(f'  <text x="{(x0 + x1) / 2}" y="{y}" font-size="{10 if bold else 8.5}"{fw} '
      f'fill="{INK if bold else SEC}" text-anchor="middle">{txt}</text>')
a(f'  <rect x="{x0 + 8}" y="113" width="{x1 - x0 - 16}" height="25" rx="2" fill="#fff" stroke="{AMB}" stroke-width="1.1" stroke-dasharray="4 3"/>')
a(f'  <text x="{(x0 + x1) / 2}" y="123.5" font-size="8.3" fill="{AMB}" text-anchor="middle">test modes: raw ΔΣ bit streams,</text>')
a(f'  <text x="{(x0 + x1) / 2}" y="134" font-size="8.3" fill="{AMB}" text-anchor="middle">raw SAR codes, no decimation</text>')
box(C2, R2, "#E4EEF8", [("MUX + SAR", 1), ("12 b, 16 kS/s", 0)])
box(C1, R3, "#E4EEF8", [("right-leg drive", 1), ("loop gain 100, 150 kΩ", 0)])
box(C1, R4, "#E4EEF8", [("bioZ source + I/Q", 1), ("51.2 kHz, cal. resistor", 0)])
box(C2, R4, "#F2F5F5", [("clock dividers", 1), ("1.024 MHz in", 0)])
box(C3, R4, "#F2F5F5", [("references, LDOs", 1), ("1 µF off chip at REF", 0)])
# test access (dashed)
box(C1, R2, "#fff", [("test-signal generator", 1), ("and lead-off currents", 0)], dashed=True, stroke=AMB)
box(C3, R3, "#fff", [("analog test MUX", 1), ("any LNA, PGA or filter output", 0)], dashed=True, stroke=AMB)

# pads
PAD = "#C98A1C"
pads = [(12, 66, 40, 60, ["IN1±", "…", "IN8±"]), (12, 254, 40, 22, ["RLD"]), (12, 324, 40, 22, ["BIOZ±"]),
        (540, 66, 40, 60, ["SPI", "+ DRDY", "CLKIN"]), (540, 248, 40, 16, ["TESTA"]), (540, 267, 40, 16, ["TESTB"]),
        (540, 324, 40, 22, ["REF"])]
for x, y, w, h, labs in pads:
    a(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{PAD}" stroke="{AMB}" stroke-width="1"/>')
    for k, t in enumerate(labs):
        yy = y + h / 2 + 3 + 12 * (k - (len(labs) - 1) / 2)
        a(f'  <text x="{x + w / 2}" y="{yy:.1f}" font-size="{8 if h < 20 else 8.5}" font-weight="700" fill="#fff" text-anchor="middle">{t}</text>')

# arrows: main chain, branch to the SAR, SAR to the back end
arrow(f"M52 {YM} H{C1[0]}")
arrow(f"M{C1[1]} {YM} H{C2[0]}")
arrow(f"M{C2[1]} {YM} H{C3[0]}")
arrow(f"M{C3[1]} {YM} H540")
YS = (R2[0] + R2[1]) / 2
arrow(f"M218 {YM} V{YS} H{C2[0]}")
a(f'  <circle cx="218" cy="{YM}" r="2.8" fill="{INK}"/>')
arrow(f"M{C2[1]} {YS} H438 V{R1[1]}")
arrow(f"M{C1[0]} {(R3[0] + R3[1]) / 2} H52")
arrow(f"M{C1[0]} {(R4[0] + R4[1]) / 2} H52")
a(f'  <path d="M{C3[1]} {(R4[0] + R4[1]) / 2} H540" stroke="{INK}" stroke-width="1.5"/>')
# test-access arrows
arrow(f"M145 {R2[0]} V{R1[1]}", AMB, True, 1.3)
YT = (R3[0] + R3[1]) / 2
arrow(f"M218 {YS} V{YT} H{C3[0]}", AMB, True, 1.3)
a(f'  <text x="{(C2[0] + C2[1]) / 2}" y="{YT - 6}" font-size="8.5" fill="{AMB}" text-anchor="middle">taps in every channel</text>')
arrow(f"M{C3[1]} 256 H540", AMB, True, 1.3)
arrow(f"M{C3[1]} 275 H540", AMB, True, 1.3)
a(f'  <text x="64" y="378" font-size="8.5" fill="{SEC}">blue: analog signal path · gold: digital · grey: support · dashed: test access, idle in normal use</text>')

# test board
a(f'  <rect x="616" y="60" width="96" height="294" rx="8" fill="{INK}"/>')
board = [("Test PCB", 84, 1), ("electrode simulator", 110, 2), ("51 kΩ ‖ 47 nF,", 122, 0), ("300 mV offset", 134, 0),
         ("precision DAC", 160, 2), ("plays MIT-BIH,", 172, 0), ("CHB-MIT records", 184, 0),
         ("CMRR fixture", 210, 2), ("common mode", 222, 0), ("through 200 pF", 234, 0),
         ("FPGA on SPI", 260, 2), ("raw streams, FFT", 272, 0), ("clean supplies", 298, 2), ("current per rail", 310, 0),
         ("(Chapter 22)", 336, 0)]
for t, y, kind in board:
    fs = 10.5 if kind == 1 else 8.8
    fw = ' font-weight="700"' if kind == 1 else ""
    col = "#fff" if kind else "#B9C6C9"
    a(f'  <text x="664" y="{y}" font-size="{fs}"{fw} fill="{col}" text-anchor="middle">{t}</text>')
arrow("M616 90 H580")
arrow("M580 104 H616")
arrow("M664 60 V14 H32 V66", INK, False, 1.3)
a(f'  <text x="350" y="10" font-size="8.5" fill="{SEC}" text-anchor="middle">simulated electrodes and recorded biosignals from the test board into IN1± … IN8±</text>')
a('</svg>')
open(OUT, "w").write("\n".join(o) + "\n")
print("wrote", OUT)
