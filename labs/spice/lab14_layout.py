"""lab14_layout.py -- Lab 14: a common-centroid MIM capacitor array in SG13G2, with DRC and LVS (Chapter 30).

    python labs/spice/lab14_layout.py              # generate, DRC, LVS
    python labs/spice/lab14_layout.py --pitch 4.5  # another unit pitch (um)

Step 1 (KLayout, in the container): place minimum-size MIM capacitors (the PDK's `cmim` PCell,
1.14 x 1.14 um, about 1.95 fF) on a 6 x 6 grid: the inner 4 x 4 holds a 4-bit binary array in
common-centroid order (8 + 4 + 2 + 1 units and one termination unit), the outer ring is dummies.
Step 2: the PDK's KLayout DRC (run_drc.py), minimum rule set without the density rules, which
apply to the whole chip after metal fill, not to a block.
Step 3: the PDK's KLayout LVS (run_lvs.py) against a schematic netlist of the 36 capacitors.
The plates are left unrouted: routing the common top plate and the bit bottom plates, and
re-running DRC and LVS, is the exercise. Outputs go to labs/spice/char/l14/ (git-ignored).
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
ly.write("/work/cdac_cc.gds")
print("cells placed:", 36, "bbox um:", top.dbbox())
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
    args = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    import shutil
    for d in ("drc", "lvs"):                     # results of earlier runs
        shutil.rmtree(os.path.join(WORK, d), ignore_errors=True)
    import json
    json.dump({"unit": UNIT, "pitch": args.pitch}, open(os.path.join(WORK, "params.json"), "w"))
    open(os.path.join(WORK, "gen.py"), "w").write(GEN)
    open(os.path.join(WORK, "xref.py"), "w").write(XREF)
    # schematic: 36 unconnected capacitors (each with its own two nets, as in the unrouted layout)
    lines = [".SUBCKT cdac_cc"]
    for k in range(36):
        lines.append(f"C{k} t{k} b{k} cap_cmim w={UNIT}u l={UNIT}u A={UNIT**2:.4f}p P={4*UNIT:.2f}u m=1")
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
        if int(amb):
            print("     (unrouted plates are interchangeable, so the runner reports a failed comparison;"
                  " route and label the plates and it resolves)")
    print("Unit:", f"{UNIT} x {UNIT} um, {UNIT**2*1.5:.2f} fF; array of 36 units at {args.pitch} um pitch")
    print("Common-centroid map for the routing (D = dummy, T = termination unit, digits = bit):")
    for r in range(6):
        row = ["D"] * 6 if r in (0, 5) else ["D"] + CC[r - 1] + ["D"]
        print("   " + " ".join(row))


if __name__ == "__main__":
    main()
