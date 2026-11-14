"""Write assets/figs/ch18_timing.svg: timing of the asynchronous SAR (one conversion, one period)."""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "figs", "ch18_timing.svg")
INK, SEC, AMB, BLU, GRN, RED = "#1D2A30", "#56656B", "#9A6212", "#1F64A8", "#1A7A4C", "#B5473A"
o = []
a = o.append
a('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 372" width="720" height="372" '
  'font-family="\'Libre Franklin\', \'Helvetica Neue\', Arial, sans-serif">')
a('  <title>Timing of the asynchronous SAR: a self-timed burst of fourteen decisions, then sleep</title>')
a(f'  <text x="10" y="16" font-size="11.5" font-weight="700" fill="{INK}">(a) One conversion: each decision triggers the next DAC step</text>')

# cycle boundaries: sampling, 7 fast cycles, 7 low-noise cycles
T0, TS = 130, 176
cyc = []
t = TS
for k in range(14):
    w, cmp_ = (26, 14) if k < 7 else (46, 32)
    cyc.append((t, t + 8, t + 8 + cmp_, t + w))      # start, compare starts, decision, end
    t += w
TEND = t
ROWS = {"sample": 52, "clk": 86, "ready": 118, "vx": 172, "done": 224}
H = 12
labels = [("sample", "sample"), ("clk", "comparator clock"), ("ready", "decision ready"),
          ("vx", "DAC residue vₓ"), ("done", "done, data out")]
for key, lab in labels:
    a(f'  <text x="120" y="{ROWS[key] + 4}" font-size="9.5" fill="{INK}" text-anchor="end">{lab}</text>')


def wave(y, segs, col=INK):
    """segs: list of (t_start, t_end) where the signal is high, between T0 and the end."""
    d = f"M{T0} {y}"
    for s, e in segs:
        d += f" H{s} V{y - H} H{e} V{y}"
    d += f" H{TEND + 20}"
    a(f'  <path d="{d}" stroke="{col}" stroke-width="1.5" fill="none"/>')


wave(ROWS["sample"], [(T0, TS)], BLU)
wave(ROWS["clk"], [(c[1], c[2]) for c in cyc], AMB)
wave(ROWS["ready"], [(c[2], c[2] + 4) for c in cyc], INK)
wave(ROWS["done"], [(TEND, TEND + 20)], GRN)

# residue: binary search with radix-1.8 weights; steps right after each decision
v, A, r = 0.62, 0.44, 1 / 1.8
y0, sc = ROWS["vx"], 56
a(f'  <path d="M{T0} {y0} H{TEND + 20}" stroke="#B9C6C9" stroke-width="0.8" stroke-dasharray="3 2"/>')
d = f"M{T0} {y0} L{TS} {y0 - v * sc:.1f}"
for k, c in enumerate(cyc):
    b = 1 if v > 0 else -1
    v -= b * A * r ** k
    d += f" H{c[2]} V{y0 - v * sc:.1f}"
d += f" H{TEND + 20}"
a(f'  <path d="{d}" stroke="{BLU}" stroke-width="1.5" fill="none"/>')
a(f'  <text x="{T0 + 4}" y="{y0 - 38}" font-size="8" fill="{BLU}">tracks −vᵢₙ</text>')
# the low-noise cycles magnified 25 times
v2, d2 = 0.62, ""
for k, c in enumerate(cyc):
    b = 1 if v2 > 0 else -1
    v2 -= b * A * r ** k
    if k == 6:
        d2 = f"M{c[2]} {y0 - 25 * v2 * sc:.1f}"
    elif k > 6:
        d2 += f" H{c[2]} V{y0 - 25 * v2 * sc:.1f}"
d2 += f" H{TEND + 20}"
a(f'  <path d="{d2}" stroke="#7FA7CF" stroke-width="1.2" fill="none" stroke-dasharray="4 2"/>')
a(f'  <text x="{cyc[9][0]}" y="{y0 + 30}" font-size="8" fill="#5C88B8">dashed: the same residue × 25</text>')

# phase brackets and notes
def brace(x0, x1, y, text, col=SEC):
    a(f'  <path d="M{x0} {y + 4} V{y} H{x1} V{y + 4}" stroke="{col}" stroke-width="1" fill="none"/>')
    a(f'  <text x="{(x0 + x1) / 2}" y="{y - 4}" font-size="8.8" fill="{col}" text-anchor="middle">{text}</text>')


brace(cyc[0][0], cyc[6][3], 34, "7 fast decisions: large residue, noise does not matter", AMB)
brace(cyc[7][0], cyc[13][3], 34, "7 low-noise decisions: residue near zero, integrate longer (Ch 16)", AMB)
a(f'  <path d="M{cyc[2][2] + 2} 120 C {cyc[2][2] + 10} 132, {cyc[3][0] - 4} 136, {cyc[3][0] + 2} 150" '
  f'stroke="{RED}" stroke-width="1" fill="none" marker-end="url(#ar)"/>')
a(f'  <defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
  f'<path d="M0 0 L10 5 L0 10 z" fill="{RED}"/></marker></defs>')
a(f'  <text x="{TS}" y="250" font-size="8.8" fill="{RED}">each ready switches the DAC; a delay cell waits for it to settle (clock low), then the next comparison starts (clock high)</text>')
a(f'  <text x="{TS}" y="264" font-size="8.8" fill="{SEC}">a watchdog timeout ends any decision that hangs near metastability, so the burst always finishes</text>')

# (b) one period
a(f'  <text x="10" y="292" font-size="11.5" font-weight="700" fill="{INK}">(b) One 62.5 µs period at 16 kS/s: burst, then sleep</text>')
yb, P0, P1 = 350, 130, 680
a(f'  <text x="120" y="{yb - 8}" font-size="9.5" fill="{INK}" text-anchor="end">supply current</text>')
d = (f"M{P0} {yb} V{yb - 34} H{P0 + 6} V{yb - 26} H{P0 + 26} V{yb - 3} H{P1} V{yb - 34} H{P1 + 6} V{yb - 26} H{P1 + 26} V{yb - 3} H{P1 + 30}")
a(f'  <path d="{d}" stroke="{INK}" stroke-width="1.5" fill="#E4EEF8"/>')
a(f'  <path d="M{P0} {yb} H{P1 + 30}" stroke="#B9C6C9" stroke-width="0.8"/>')
a(f'  <text x="{P0 + 32}" y="{yb - 28}" font-size="8.8" fill="{INK}">sample and 14 decisions: a few µs</text>')
a(f'  <text x="{(P0 + P1) / 2 + 40}" y="{yb - 10}" font-size="8.8" fill="{SEC}" text-anchor="middle">asleep: the dynamic comparator and logic draw only leakage, nanoamperes</text>')
a(f'  <text x="{P1 - 4}" y="{yb - 38}" font-size="8.8" fill="{INK}" text-anchor="end">next sample, next channel</text>')
for x, lab in ((P0, "0"), (P1, "62.5 µs")):
    a(f'  <path d="M{x} {yb} V{yb + 4}" stroke="{SEC}" stroke-width="0.8"/>')
    a(f'  <text x="{x}" y="{yb + 14}" font-size="8" fill="{SEC}" text-anchor="middle">{lab}</text>')
a(f'  <text x="710" y="16" font-size="8" fill="{SEC}" text-anchor="end">a timing sketch, not to scale</text>')
a('</svg>')
open(OUT, "w").write("\n".join(o) + "\n")
print("wrote", OUT)
