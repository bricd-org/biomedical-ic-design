"""lab14_layout.py -- Lab 14: a common-centroid MIM capacitor array in SG13G2, with DRC and LVS (Chapter 30).

    python labs/spice/lab14_layout.py              # generate, DRC, LVS
    python labs/spice/lab14_layout.py --pitch 4.5  # another unit pitch (um)

Step 1 (KLayout, in the container): place minimum-size MIM capacitors (the PDK's `cmim` PCell,
1.14 x 1.14 um, about 1.95 fF) on a 6 x 6 grid: the inner 4 x 4 holds a 4-bit binary array in
common-centroid order (8 + 4 + 2 + 1 units and one termination unit), the outer ring is dummies.
Step 2: the PDK's KLayout DRC (run_drc.py), minimum rule set without the density rules, which
apply to the whole chip after metal fill, not to a block.
Step 3: the PDK's KLayout LVS (run_lvs.py) against a schematic netlist of the 36 capacitors.
By default the plates are left unrouted: routing them is the exercise. --route builds the reference
solution instead: TopMetal1 straps and a spine join every top plate; each bottom plate drops through a
Metal3-Metal5 via_stack placed in its Metal5 margin (outside the MIM) onto a Metal3 stub, which lands
on its net's Metal2 track under the row; Metal3 spines on the left join each net's tracks. LVS then
compares against six nets: top, bits 0-3 and the termination net that also takes the dummies.
Outputs go to labs/spice/char/l14/ (git-ignored).
Needs Docker and hpretl/iic-osic-tools:2026.10.
"""
import argparse
import glob
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sg13_char as ch  # noqa: E402

WORK = os.path.join(ch.WORK, "l14")
UNIT = 1.14          # um, minimum cmim width and length
# common-centroid assignment of the inner 4 x 4 (rows top to bottom): bit 3 = 8 units, bit 2 = 4,
# bit 1 = 2, bit 0 = 1, T = termination unit; every bit's units are point-symmetric about the centre
CC = [["3", "2", "3", "3"],
      ["2", "1", "0", "3"],
      ["3", "T", "1", "2"],
      ["3", "3", "2", "3"]]

GEN = r'''
import pya, json
p = json.load(open("/work/params.json"))
ly = pya.Layout()
ly.technology_name = "sg13g2"
top = ly.create_cell("cdac_cc")
lib = pya.Library.library_by_name("SG13_dev", "sg13g2")
unit = p["unit"]
pc = ly.create_cell("cmim", "SG13_dev", {"w": f"{unit}u", "l": f"{unit}u", "Calculate": "C"})
dbu = ly.dbu
pitch = p["pitch"]
for r in range(6):
    for c in range(6):
        top.insert(pya.CellInstArray(pc.cell_index(), pya.Trans(pya.Point(int(c * pitch / dbu), int(-r * pitch / dbu)))))
if p.get("route"):
    um = lambda v: int(round(v / dbu))
    def box(layer, x0, y0, x1, y1):
        top.shapes(ly.layer(*layer)).insert(pya.Box(um(min(x0, x1)), um(min(y0, y1)), um(max(x0, x1)), um(max(y0, y1))))
    def label(layer, x, y, t):
        top.shapes(ly.layer(*layer)).insert(pya.Text(t, pya.Trans(pya.Point(um(x), um(y)))))
    M2, M3, TM1 = (10, 0), (30, 0), (126, 0)
    v35 = ly.create_cell("via_stack", "SG13_dev", {"b_layer": "Metal3", "t_layer": "Metal5", "vn_columns": 1, "vn_rows": 1})
    v23 = ly.create_cell("via_stack", "SG13_dev", {"b_layer": "Metal2", "t_layer": "Metal3", "vn_columns": 1, "vn_rows": 1})
    def via(cell, x, y):                       # place a via_stack centred on (x, y)
        c = cell.dbbox().center()
        top.insert(pya.CellInstArray(cell.cell_index(), pya.Trans(pya.Point(um(x - c.x), um(y - c.y)))))
    nets = p["nets"]                           # 6 x 6 map of net names: b0..b3, T
    order = ["b0", "b1", "b2", "b3", "T"]
    W3, W2, TP = 0.3, 0.3, 0.55                # stub and track widths, track pitch
    x_right = 5 * pitch + 1.74
    spine_x = {n: -2.0 - 0.8 * k for k, n in enumerate(order)}
    track_y = {}
    for r in range(6):
        y_gap = -r * pitch - 0.6 - (pitch - 2.34) / 2
        for k, n in enumerate(order):
            track_y[(r, n)] = y_gap + (k - 2) * TP
    # top plate: one TopMetal1 strap per row, a spine on the right
    xs = 5 * pitch + 2.4
    for r in range(6):
        box(TM1, -0.25, -r * pitch - 0.25, xs + 1.64, -r * pitch + 1.39)
    box(TM1, xs, -5 * pitch - 0.25, xs + 1.64, 1.39)
    label((126, 25), xs + 0.82, 0.57, "top")
    # bottom plates: via in the Metal5 margin below the MIM, Metal3 stub down to the net's Metal2 track
    used = {n: [] for n in order}
    for r in range(6):
        for c in range(6):
            n = nets[r][c]
            x, y0 = c * pitch + 0.57, -r * pitch - 0.38
            via(v35, x, y0)
            ty = track_y[(r, n)]
            box(M3, x - W3 / 2, y0, x + W3 / 2, ty)
            via(v23, x, ty)
            used[n].append(r)
    for n in order:
        for r in sorted(set(used[n])):
            ty = track_y[(r, n)]
            box(M2, spine_x[n] - 0.3, ty - W2 / 2, x_right, ty + W2 / 2)
            via(v23, spine_x[n], ty)
        rows = sorted(set(used[n]))
        y_hi, y_lo = track_y[(rows[0], n)], track_y[(rows[-1], n)]
        box(M3, spine_x[n] - W3 / 2, y_lo - 0.3, spine_x[n] + W3 / 2, y_hi + 0.3)
        label((30, 25), spine_x[n], y_hi, n)
ly.write("/work/cdac_cc.gds")
print("cells placed:", 36, "routed:", bool(p.get("route")), "bbox um:", top.dbbox())
'''


XREF = r'''
import pya
lvs = pya.LayoutVsSchematic()
lvs.read("/work/lvs/cdac_cc.lvsdb")
x = lvs.xref()
for cp in x.each_circuit_pair():
    dev = [str(d.status()) for d in x.each_device_pair(cp)]
    net = [str(n.status()) for n in x.each_net_pair(cp)]
    print("XREF circuit", cp.status(), "devices", len(dev), "matched", sum(s.startswith("Match") for s in dev),
          "nets", len(net), "exact", sum(s == "Match" for s in net), "ambiguous", sum(s == "MatchWithWarning" for s in net))
'''


def main():
    ap = argparse.ArgumentParser(description="Lab 14: MIM array layout, DRC and LVS")
    ap.add_argument("--pitch", type=float, default=5.0, help="unit pitch (um)")
    ap.add_argument("--route", action="store_true", help="build and check the routed reference solution")
    args = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    import shutil
    for d in ("drc", "lvs"):                     # results of earlier runs
        shutil.rmtree(os.path.join(WORK, d), ignore_errors=True)
    import json
    nets = [["T"] * 6 if r in (0, 5) else ["T"] + [("T" if x == "T" else "b" + x) for x in CC[r - 1]] + ["T"]
            for r in range(6)]
    json.dump({"unit": UNIT, "pitch": args.pitch, "route": args.route, "nets": nets},
              open(os.path.join(WORK, "params.json"), "w"))
    open(os.path.join(WORK, "gen.py"), "w").write(GEN)
    open(os.path.join(WORK, "xref.py"), "w").write(XREF)
    # schematic: 36 unconnected capacitors (each with its own two nets, as in the unrouted layout)
    lines = [".SUBCKT cdac_cc top b0 b1 b2 b3 T" if args.route else ".SUBCKT cdac_cc"]
    for k in range(36):
        t, b = ("top", nets[k // 6][k % 6]) if args.route else (f"t{k}", f"b{k}")
        lines.append(f"C{k} {t} {b} cap_cmim w={UNIT}u l={UNIT}u A={UNIT**2:.4f}p P={4*UNIT:.2f}u m=1")
    lines.append(".ENDS")
    open(os.path.join(WORK, "cdac_cc.cdl"), "w").write("\n".join(lines) + "\n")
    tech = "/foss/pdks/ihp-sg13g2/libs.tech/klayout/tech"
    script = (f"klayout -zz -r gen.py 2>&1 | grep -v registered ; "
              f"python3 {tech}/drc/run_drc.py --path=cdac_cc.gds --topcell=cdac_cc --run_dir=drc --min_drc --no_density > drc.log 2>&1 ; "
              f"python3 {tech}/lvs/run_lvs.py --layout=cdac_cc.gds --netlist=cdac_cc.cdl --topcell=cdac_cc --run_dir=lvs > lvs.log 2>&1 ; "
              f"grep -E 'Passed|Failed|Violated' drc.log ; klayout -zz -r xref.py 2>&1 | grep XREF")
    out = subprocess.run(["docker", "run", "--rm", "-v", f"{WORK}:/work", "-w", "/work", "--entrypoint", "/bin/bash",
                          ch.IMAGE, "-lc", script], capture_output=True, text=True).stdout
    print("\n".join(l for l in out.splitlines() if "INFO]" not in l and "PATH" not in l))
    # count DRC markers in the result databases
    n_drc = 0
    for f in glob.glob(os.path.join(WORK, "drc", "*.lyrdb")):
        n_drc += len(re.findall(r"<item>", open(f).read()))
    print(f"\nDRC: {n_drc} violations (cdac_cc.gds, minimum rule set, no density rules)")
    m = re.search(r"XREF circuit (\S+) devices (\d+) matched (\d+) nets (\d+) exact (\d+) ambiguous (\d+)", out)
    if m:
        st, nd, md, nn, ex, amb = m.groups()
        print(f"LVS: circuit {st}; {md} of {nd} devices paired; {nn} nets, {ex} exact, {amb} ambiguous")
        if int(amb) and not args.route:
            print("     (unrouted plates are interchangeable, so the runner reports a failed comparison;"
                  " route and label the plates and it resolves)")
    print("Unit:", f"{UNIT} x {UNIT} um, {UNIT**2*1.5:.2f} fF; array of 36 units at {args.pitch} um pitch")
    print("Common-centroid map for the routing (D = dummy, T = termination unit, digits = bit):")
    for r in range(6):
        row = ["D"] * 6 if r in (0, 5) else ["D"] + CC[r - 1] + ["D"]
        print("   " + " ".join(row))


if __name__ == "__main__":
    main()
