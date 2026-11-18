"""Write assets/figs/ch03_interface.svg: a cross-section of a gelled Ag/AgCl electrode on skin, with each layer
mapped to its element in the electrode-skin equivalent circuit (Chapter 3, Section 3.3)."""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "figs", "ch03_interface.svg")
INK, SEC, AMB, BLU, GRN, RED, RULE = "#1D2A30", "#56656B", "#9A6212", "#1F64A8", "#1A7A4C", "#B5473A", "#B9C6C9"
W, H = 720, 350
X0, X1 = 112, 420           # cross-section
EL0, EL1 = 176, 356         # electrode and gel
CX = 580                    # circuit axis
o = []
a = o.append


def text(x, y, t, size=9, col=SEC, anchor="start", bold=False, italic=False, extra=""):
    fw = ' font-weight="700"' if bold else ""
    fs = ' font-style="italic"' if italic else ""
    a(f'  <text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{fw}{fs}{extra}>{t}</text>')


def sym(x, y, base, sub, anchor="start"):
    text(x, y, f'{base}<tspan dy="3" font-size="9.5">{sub}</tspan>', 13, INK, anchor, italic=True)


def zig(x, y0, y1, w=6, n=6):
    """vertical resistor from y0 to y1 at x, 4 px leads"""
    step = (y1 - y0 - 8) / n
    d = f"M{x} {y0} v4 l{w / 2:g} {step / 2:g}"
    for k in range(n - 1):
        d += f" l{-w if k % 2 == 0 else w:g} {step:g}"
    d += f" l{w / 2:g} {step / 2:g} v4"
    return d


def cell(y):
    """vertical battery: long thin plate at y, short thick plate at y + 6"""
    a(f'  <path d="M{CX - 12} {y} H{CX + 12}" stroke="{INK}" stroke-width="2.4"/>')
    a(f'  <path d="M{CX - 7} {y + 6} H{CX + 7}" stroke="{INK}" stroke-width="4"/>')


def cap(x, y):
    a(f'  <path d="M{x - 10} {y} H{x + 10} M{x - 10} {y + 6} H{x + 10}" stroke="{INK}" stroke-width="2.4"/>')


def parallel(ytop, ybot, ycap):
    xl, xr = CX - 18, CX + 18
    a(f'  <path d="M{xl} {ytop} H{xr} M{xl} {ybot} H{xr} M{xr} {ytop} V{ycap} M{xr} {ycap + 6} V{ybot} '
      f'{zig(xl, ytop, ybot)}" stroke="{INK}" stroke-width="1.8" fill="none" stroke-linejoin="round"/>')
    cap(xr, ycap)
    for y in (ytop, ybot):
        a(f'  <circle cx="{CX}" cy="{y}" r="2.6" fill="{INK}"/>')


a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
  'font-family="\'Libre Franklin\', \'Helvetica Neue\', Arial, sans-serif">')
a('  <title>Cross-section of a gelled Ag/AgCl electrode on the skin, each layer mapped to its element of the '
  'electrode–skin equivalent circuit</title>')
a('  <defs>')
a(f'    <marker id="ia" viewBox="0 0 10 10" refX="10" refY="5" markerUnits="userSpaceOnUse" markerWidth="7" '
  f'markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{INK}"/></marker>')
a(f'    <clipPath id="cs"><rect x="{X0}" y="0" width="{X1 - X0}" height="{H}"/></clipPath>')
a('  </defs>')

# ---------------- skin (drawn first, bottom up) ----------------
a('  <g clip-path="url(#cs)">')
a(f'  <rect x="{X0}" y="232" width="{X1 - X0}" height="98" fill="#F9EDE9"/>')            # dermis
# living epidermis with a wavy lower edge (the rete ridges)
d = f"M{X0} 186 H{X1} V236"
x = X1
while x > X0:
    d += f" q-10 9 -20 0"
    x -= 20
d += " Z"
a(f'  <path d="{d}" fill="#F7E3D6"/>')
for r, y in enumerate((194, 206, 218)):
    for x in range(X0 + 8 + (8 if r % 2 else 0), X1, 16):
        a(f'  <ellipse cx="{x}" cy="{y}" rx="6.5" ry="3.6" fill="none" stroke="#E2C3B0" stroke-width="0.9"/>')
a(f'  <rect x="{X0}" y="160" width="{X1 - X0}" height="26" fill="#F5E6C8"/>')            # stratum corneum
for r, y in enumerate((162, 168, 174, 180)):
    for x in range(X0 - 11 + (11 if r % 2 else 0), X1, 22):
        a(f'  <rect x="{x}" y="{y}" width="21" height="4.6" rx="1.4" fill="none" stroke="#D9BE8C" stroke-width="0.8"/>')
# capillary loops
for xc in (166, 226):
    a(f'  <path d="M{xc - 12} 330 V266 C{xc - 12} 250 {xc + 12} 250 {xc + 12} 266 V330" fill="none" stroke="{RED}" '
      'stroke-width="2" stroke-opacity=".75"/>')
text(244, 304, "blood vessels", 7.5, RED)
# sweat gland and duct, opening into the gel
a('  <path d="M314 306 c-14 0 -14 12 0 12 c14 0 14 -12 0 -12 c-10 0 -10 8 0 8" fill="none" stroke="#5E8FBF" stroke-width="2.6"/>')
a('  <path d="M314 306 C306 286 322 270 314 250 C308 236 320 226 314 212 C310 200 318 194 314 186 '
  'C306 180 322 174 314 168 C310 165 314 162 314 160" fill="none" stroke="#5E8FBF" stroke-width="2.6"/>')
text(326, 262, "sweat duct: a", 7.5, "#3E6E9E")
text(326, 272, "parallel, lower-", 7.5, "#3E6E9E")
text(326, 282, "resistance path", 7.5, "#3E6E9E")
a('  </g>')
a(f'  <path d="M{X0} 330 q8 -5 16 0 t16 0 t16 0 t16 0 t16 0 t16 0 t16 0 t16 0 t16 0 t16 0 t16 0 t16 0 t16 0 t16 0 '
  f't16 0 t16 0 t16 0 t16 0 t20 0" fill="none" stroke="{RULE}" stroke-width="1"/>')
a(f'  <path d="M{X0} 160 H{X1} M{X0} 160 V330 M{X1} 160 V330" stroke="{RULE}" stroke-width="1" fill="none"/>')

# ---------------- electrode ----------------
for xa, xb in ((122, EL0), (EL1, 410)):                                            # foam ring with adhesive
    a(f'  <rect x="{xa}" y="52" width="{xb - xa}" height="108" fill="#EEF1F2" stroke="{RULE}" stroke-width="1"/>')
    a(f'  <path d="M{xa} 157 H{xb}" stroke="#C9B27A" stroke-width="3"/>')
    text((xa + xb) / 2, 112, "foam", 8, SEC, "middle")
    text((xa + xb) / 2, 150, "adhesive", 6.8, AMB, "middle")
a(f'  <rect x="{EL0}" y="86" width="{EL1 - EL0}" height="74" fill="#E4EEF8"/>')        # gel
a(f'  <rect x="{EL0}" y="86" width="{EL1 - EL0}" height="22" fill="#CFE0F1"/>')        # double-layer band
a(f'  <rect x="{EL0}" y="58" width="{EL1 - EL0}" height="18" fill="#C9D0D3" stroke="{INK}" stroke-width="1.2"/>')   # Ag
a(f'  <rect x="{EL0}" y="76" width="{EL1 - EL0}" height="10" fill="#8E979B" stroke="{INK}" stroke-width="1.2"/>')   # AgCl
a(f'  <rect x="252" y="30" width="28" height="28" rx="5" fill="#C9D0D3" stroke="{INK}" stroke-width="1.2"/>')      # snap
a(f'  <path d="M{X0} 36 H252" stroke="{INK}" stroke-width="2.4"/>')                                                 # lead wire
a(f'  <path d="M228 22 H140" stroke="{INK}" stroke-width="1.2" fill="none" marker-start="url(#ia)" marker-end="url(#ia)"/>')
text(184, 16, "electrons in the wire", 8, INK, "middle")
for x in range(EL0 + 9, EL1, 18):                                                  # double layer
    text(x, 94, "+", 8, INK, "middle")
    a(f'  <circle cx="{x}" cy="102" r="3.4" fill="#fff" stroke="{GRN}" stroke-width="1.1"/>')
    a(f'  <path d="M{x - 1.8} 102 H{x + 1.8}" stroke="{GRN}" stroke-width="1"/>')
ions = ((188, 118, 0), (198, 136, 1), (186, 150, 0), (342, 120, 1), (332, 138, 0), (344, 152, 1))
for x, y, na in ions:
    col = BLU if na else GRN
    a(f'  <circle cx="{x}" cy="{y}" r="4.6" fill="#fff" stroke="{col}" stroke-width="1.1"/>')
    a(f'  <path d="M{x - 2.4} {y} H{x + 2.4}{f" M{x} {y - 2.4} V{y + 2.4}" if na else ""}" stroke="{col}" stroke-width="1.1"/>')
a(f'  <rect x="210" y="114" width="112" height="32" rx="3" fill="#fff" fill-opacity=".75"/>')
text(266, 127, "Ag ⇌ Ag⁺ + e⁻", 9, INK, "middle")
text(266, 140, "Ag⁺ + Cl⁻ ⇌ AgCl", 9, INK, "middle")
text(266, 157, "Na⁺ and Cl⁻ ions in the gel", 7.5, SEC, "middle")

# ---------------- layer names (left) ----------------
for y, t in ((40, "lead wire, snap"), (71, "silver (Ag)"), (85, "silver chloride"), (101, "double layer"),
             (136, "electrolyte gel"), (171, "stratum corneum"), (182, "(dead, dry cells)"), (214, "living epidermis"),
             (276, "dermis and"), (287, "deeper tissue")):
    text(104, y, t, 8.5 if not t.startswith("(") else 7.5, INK if not t.startswith("(") else SEC, "end")

# ---------------- circuit (right) ----------------
a(f'  <circle cx="{CX}" cy="26" r="4.5" fill="#fff" stroke="{INK}" stroke-width="1.8"/>')
a(f'  <path d="M{CX} 30.5 V44 M{CX} 50 V62 M{CX} 110 V{110 + 0}" stroke="{INK}" stroke-width="1.8"/>')
cell(44)
parallel(62, 110, 83)
a(f'  <path d="{zig(CX, 110, 156)} M{CX} 156 V164 M{CX} 170 V180" stroke="{INK}" stroke-width="1.8" fill="none" '
  'stroke-linejoin="round"/>')
cell(164)
parallel(180, 230, 202)
a(f'  <path d="M{CX} 230 V246 {zig(CX, 246, 294)} M{CX} 294 V309.5" stroke="{INK}" stroke-width="1.8" fill="none" '
  'stroke-linejoin="round"/>')
a(f'  <circle cx="{CX}" cy="314" r="4.5" fill="#fff" stroke="{INK}" stroke-width="1.8"/>')
LX = CX + 32
text(LX, 30, "to the amplifier", 8.5, SEC)
sym(LX, 52, "E", "hc"); text(LX, 64, "half-cell potential", 8, SEC)
sym(LX, 88, "R", "d"); text(LX + 18, 88, "‖", 12, INK); sym(LX + 28, 88, "C", "d")
text(LX, 100, "charge transfer,", 8, SEC); text(LX, 110, "double layer", 8, SEC)
sym(LX, 138, "R", "s"); text(LX, 150, "gel", 8, SEC)
sym(LX, 172, "E", "se"); text(LX, 184, "skin potential", 8, SEC)
sym(LX, 208, "R", "e"); text(LX + 18, 208, "‖", 12, INK); sym(LX + 28, 208, "C", "e")
text(LX, 220, "stratum corneum", 8, SEC)
sym(LX, 274, "R", "u"); text(LX, 286, "dermis, tissue", 8, SEC)
text(LX, 318, "into the body", 8.5, SEC)

# ---------------- brackets and leaders ----------------
for (ya, yb), (ca, cb) in (((58, 108), (40, 112)), ((108, 160), (112, 158)), ((160, 236), (160, 232)), ((236, 330), (240, 300))):
    a(f'  <path d="M424 {ya + 2} h4 V{yb - 2} h-4" stroke="{RULE}" stroke-width="1.3" fill="none"/>')
    a(f'  <path d="M{CX - 30} {ca + 2} h-4 V{cb - 2} h4" stroke="{RULE}" stroke-width="1.3" fill="none"/>')
    a(f'  <path d="M432 {(ya + yb) / 2:g} L{CX - 38} {(ca + cb) / 2:g}" stroke="{RULE}" stroke-width="1" '
      'stroke-dasharray="4 3" fill="none"/>')
a('</svg>')
with open(OUT, "w") as f:
    f.write("\n".join(o) + "\n")
print("saved", os.path.abspath(OUT))
