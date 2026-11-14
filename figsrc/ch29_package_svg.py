"""Write assets/figs/ch29_package.svg: Open-BioAFE QFN-40 pinout concept (top view)."""
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "figs", "ch29_package.svg")
INK, SEC, AMB = "#1D2A30", "#56656B", "#9A6212"
COL = {"in": "#1F64A8", "ana": "#7FA7CF", "sup": "#8C9A9F", "dig": "#C98A1C"}
LEFT = ["IN5+", "IN5−", "IN6+", "IN6−", "IN7+", "IN7−", "IN8+", "IN8−", "SHLD", "VDD33"]          # 1-10, top->bottom
BOTTOM = ["VDDA", "VSSA", "REF", "TESTA", "TESTB", "VSSD", "VDDD", "RESETn", "CLKIN", "DRDY"]     # 11-20, left->right
RIGHT = ["MISO", "MOSI", "SCLK", "CSn", "VDDIO", "VSSIO", "VSSA", "VDDA", "BIOZ−", "BIOZ+"]       # 21-30, bottom->top
TOP = ["RLD", "SHLD", "IN1+", "IN1−", "IN2+", "IN2−", "IN3+", "IN3−", "IN4+", "IN4−"]            # 31-40, right->left


def group(n):
    if n.startswith("IN") or n in ("SHLD", "RLD"):
        return "in"
    if n.startswith("V"):
        return "sup"
    if n in ("REF", "TESTA", "TESTB") or n.startswith("BIOZ"):
        return "ana"
    return "dig"


X0, Y0, S = 110, 84, 280            # package outline, 6 mm -> 280 px
DW, DH = 93.0, 70.0                 # die, 2.0 x 1.5 mm
DX0, DY0 = 250 - DW / 2, 224 - DH / 2
EP0, EPS = 180, 140                 # exposed pad
off = [35 + 23.333 * k for k in range(10)]
FW = ' font-weight="700"'
o = []
a = o.append
a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 430" width="720" height="430" '
  'font-family="\'Libre Franklin\', \'Helvetica Neue\', Arial, sans-serif">')
a('  <title>Open-BioAFE package concept: QFN-40 pinout with the inputs on two adjacent sides and the digital pins in the opposite corner</title>')
a(f'  <text x="10" y="16" font-size="11.5" font-weight="700" fill="{INK}">Inputs round one corner, digital round the other (QFN-40 concept, top view)</text>')
a(f'  <rect x="{X0}" y="{Y0}" width="{S}" height="{S}" rx="6" fill="#2E3A40" stroke="{INK}" stroke-width="1.5"/>')
a(f'  <rect x="{EP0}" y="154" width="{EPS}" height="{EPS}" rx="2" fill="#56656B" opacity="0.65"/>')
a(f'  <rect x="{DX0}" y="{DY0}" width="{DW}" height="{DH}" fill="#B9C6C9" stroke="#fff" stroke-width="0.8"/>')
a(f'  <text x="250" y="222" font-size="8.5" font-weight="700" fill="{INK}" text-anchor="middle">die</text>')
a(f'  <text x="250" y="234" font-size="7.5" fill="{INK}" text-anchor="middle">2.0 × 1.5 mm</text>')
a(f'  <text x="{EP0 + EPS / 2}" y="286" font-size="7.5" fill="#fff" text-anchor="middle">exposed pad = VSSA</text>')
a(f'  <circle cx="{X0 + 14}" cy="{Y0 + 14}" r="4" fill="#fff"/>')

pins = []     # (number, name, pin centre, inward direction, die point)
for k, n in enumerate(LEFT):
    y = Y0 + off[k]
    pins.append((k + 1, n, (X0, y), "L", (DX0, 224 + (y - (Y0 + S / 2)) * DH / 210)))
for k, n in enumerate(BOTTOM):
    x = X0 + off[k]
    pins.append((k + 11, n, (x, Y0 + S), "B", (250 + (x - (X0 + S / 2)) * DW / 210, DY0 + DH)))
for k, n in enumerate(RIGHT):
    y = Y0 + S - off[k]
    pins.append((k + 21, n, (X0 + S, y), "R", (DX0 + DW, 224 + (y - (Y0 + S / 2)) * DH / 210)))
for k, n in enumerate(TOP):
    x = X0 + S - off[k]
    pins.append((k + 31, n, (x, Y0), "T", (250 + (x - (X0 + S / 2)) * DW / 210, DY0)))

for num, n, (px, py), side, (dx, dy) in pins:
    g = group(n)
    c = COL[g]
    # bond wire from the die edge to the inner end of the pin
    ix, iy = {"L": (px + 10, py), "R": (px - 10, py), "T": (px, py + 10), "B": (px, py - 10)}[side]
    a(f'  <path d="M{dx:.1f} {dy:.1f} L{ix:.1f} {iy:.1f}" stroke="{"#9DBBDD" if g == "in" else "#D9C9A0"}" stroke-width="0.8"/>')
    if side in "LR":
        a(f'  <rect x="{px - 8}" y="{py - 6}" width="18" height="12" fill="{c}" stroke="#fff" stroke-width="0.6"/>' if side == "L" else
          f'  <rect x="{px - 10}" y="{py - 6}" width="18" height="12" fill="{c}" stroke="#fff" stroke-width="0.6"/>')
        tx = px - 13 if side == "L" else px + 13
        a(f'  <text x="{tx}" y="{py + 3}" font-size="8.5" fill="{INK}" text-anchor="{"end" if side == "L" else "start"}"'
          f'{FW if g == "in" else ""}>{n}</text>')
        nx = px + 14 if side == "L" else px - 14
        a(f'  <text x="{nx}" y="{py + 2.5}" font-size="6.5" fill="#B9C6C9" text-anchor="{"start" if side == "L" else "end"}">{num}</text>')
    else:
        a(f'  <rect x="{px - 6}" y="{py - 8}" width="12" height="18" fill="{c}" stroke="#fff" stroke-width="0.6"/>' if side == "T" else
          f'  <rect x="{px - 6}" y="{py - 10}" width="12" height="18" fill="{c}" stroke="#fff" stroke-width="0.6"/>')
        ty = py - 13 if side == "T" else py + 13
        a(f'  <text transform="translate({px + 3},{ty}) rotate(-90)" font-size="8.5" fill="{INK}" '
          f'text-anchor="{"start" if side == "T" else "end"}"{FW if g == "in" else ""}>{n}</text>')
        ny = py + 18 if side == "T" else py - 13
        a(f'  <text x="{px}" y="{ny}" font-size="6.5" fill="#B9C6C9" text-anchor="middle">{num}</text>')

# corner arrows: where the cables go on the test board
a(f'  <path d="M96 70 L62 36" stroke="{COL["in"]}" stroke-width="2" fill="none"/>')
a(f'  <path d="M62 36 l11 2 l-9 9 z" fill="{COL["in"]}"/>')
a(f'  <text x="14" y="30" font-size="8.5" font-weight="700" fill="{COL["in"]}">to the electrode</text>')
a(f'  <text x="14" y="41" font-size="8.5" font-weight="700" fill="{COL["in"]}">connector</text>')
a(f'  <path d="M404 378 L438 412" stroke="{AMB}" stroke-width="2" fill="none"/>')
a(f'  <path d="M438 412 l-11 -2 l9 -9 z" fill="{AMB}"/>')
a(f'  <text x="444" y="420" font-size="8.5" font-weight="700" fill="{AMB}">to the FPGA or host</text>')

# notes and legend
NX = 480
a(f'  <text x="{NX}" y="96" font-size="10.5" font-weight="700" fill="{INK}">QFN-40, 6 × 6 mm, 0.5 mm pitch</text>')
for i, (g, lab) in enumerate((("in", "electrode inputs, shields, RLD (19)"), ("ana", "bioZ, reference, analog test (5)"),
                              ("sup", "supplies and grounds (9)"), ("dig", "SPI, clock, reset, DRDY (7)"))):
    y = 114 + 16 * i
    a(f'  <rect x="{NX}" y="{y - 8}" width="10" height="10" fill="{COL[g]}"/>')
    a(f'  <text x="{NX + 16}" y="{y + 1}" font-size="8.8" fill="{INK}">{lab}</text>')
notes = [
    ("Inputs wrap round the top-left corner,", True),
    ("one SHLD pin at each end of the group:", False),
    ("the driven shield of Chapter 12 guards", False),
    ("the traces on the board as well.", False),
    ("", False),
    ("SPI, clock and reset sit in the opposite", True),
    ("corner, with their own VDDIO and VSSIO.", False),
    ("", False),
    ("Analog supplies separate the groups;", True),
    ("the exposed pad is VSSA, and REF takes", False),
    ("1 µF to VSSA right at the pin.", False),
    ("", False),
    ("Concept only: the pin count follows the", True),
    ("test chip above; a product would drop", False),
    ("the TEST pins.", False),
]
y = 192
for s, b in notes:
    if s:
        a(f'  <text x="{NX}" y="{y}" font-size="8.8" fill="{INK if b else SEC}"{FW if b else ""}>{s}</text>')
    y += 12
a('</svg>')
open(OUT, "w").write("\n".join(o) + "\n")
print("wrote", OUT)
