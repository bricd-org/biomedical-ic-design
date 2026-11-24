"""sg13_flow.py -- SG13G2 simulations for Chapter 30 (the design flow), using the runner in sg13_char.py.

    python labs/spice/sg13_flow.py            # needs Docker and hpretl/iic-osic-tools:2026.10
    python labs/spice/sg13_flow.py --mc 400   # fewer Monte Carlo samples, for a quick check

Three checks on numbers this tutorial depends on:
  1. Simulator settings: the thick-oxide pseudo-resistor of Chapter 8 (one back-to-back pair of
     sg13_hv_pmos, W/L = 1/10 um, tt, 27 degC) with gmin from 1e-9 to 1e-18 S and abstol at 1e-12 A
     (the ngspice default), 1e-15 and 1e-18 A.
  2. Corners: the same pair at the five MOS corners (tt, ss, ff, sf, fs) and -20 ... 85 degC.
  3. Mismatch: Monte Carlo of the offset of two diode-connected 4/1 um sg13_lv_nmos at 1 uA each
     (the comparator's input pair, Chapter 16) with mos_tt_mismatch and mm_ok=1; and, without mismatch,
     gm and gds at that operating point, because a diode-connected device turns a threshold shift into
     a gate-voltage shift of only gm / (gm + gds) of it.
Results: figsrc/data/sg13_flow_gmin.csv, sg13_flow_corners.csv, sg13_flow_mc.csv, sg13_flow_gmgds.csv.
"""
import argparse, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sg13_char as ch

GMINS = [10.0 ** -k for k in range(9, 19)]
ABSTOLS = [1e-12, 1e-15, 1e-18]
CORNERS = ["tt", "ss", "ff", "sf", "fs"]
TEMPS = [-20, 0, 27, 37, 45, 85]
CORNER_OPT = (1e-18, 1e-18)        # gmin, abstol for the corner runs (checked by the sweep)


def pseudo(tag, corner="tt", temp=27, gmin=1e-15, abstol=1e-15):
    """One back-to-back pair of diode-connected thick-oxide PMOS, I versus V (as sg13_lna.py)."""
    return f"""* hv pseudo-resistor, {corner}, {temp} degC, gmin={gmin:g}, abstol={abstol:g}
.lib cornerMOShv.lib mos_{corner}
.temp {temp}
.option gmin={gmin:g} abstol={abstol:g}
Va a 0 0
XM0 a a m0 m0 sg13_hv_pmos w=1u l=10u ng=1 m=1
XM1 0 0 m0 m0 sg13_hv_pmos w=1u l=10u ng=1 m=1
.control
dc Va -0.6 0.6 5m
let ia = -i(Va)
wrdata /work/out/{tag}.txt ia
.endc
.end
"""


def mc(n):
    """Offset of two diode-connected 4/1 um NMOS at 1 uA each; mc_source draws new mismatch every run."""
    return f"""* offset Monte Carlo of a 4/1 um sg13_lv_nmos pair at 1 uA
.lib cornerMOSlv.lib mos_tt_mismatch
I1 0 g1 1u
XM1 g1 g1 0 0 sg13_lv_nmos w=4u l=1u ng=1 m=1 mm_ok=1
I2 0 g2 1u
XM2 g2 g2 0 0 sg13_lv_nmos w=4u l=1u ng=1 m=1 mm_ok=1
.control
set rndseed=11
let run = 0
dowhile run < {n}
  mc_source
  op
  let d = v(g1) - v(g2)
  echo "VOS $&d"
  let run = run + 1
end
.endc
.end
"""


DIODE = """* diode-connected 4/1 um sg13_lv_nmos at 1 uA, no mismatch: operating point
.lib cornerMOSlv.lib mos_tt
I1 0 g 1u
XM1 g g 0 0 sg13_lv_nmos w=4u l=1u ng=1 m=1
.control
op
let vg = v(g)
wrdata /work/out/flow_diode.txt vg
.endc
.end
"""

SWEEP = """* {src} sweep of the same device around its diode point
.lib cornerMOSlv.lib mos_tt
Vg g 0 {vg}
Vd d 0 {vg}
XM1 d g 0 0 sg13_lv_nmos w=4u l=1u ng=1 m=1
.control
dc {src} {lo} {hi} 0.0005
let id = -i(Vd)
wrdata /work/out/flow_{src}.txt id
.endc
.end
"""


def gm_gds():
    """gm and gds at the Monte Carlo pair's operating point (VDS = VGS, 1 uA)."""
    ch.run({"flow_diode": DIODE})
    vg = float(ch.load("flow_diode", 1)[1][0])
    ch.run({f"flow_{s}": SWEEP.format(src=s, vg=vg, lo=vg - 0.01, hi=vg + 0.01) for s in ("Vg", "Vd")})
    x, i = ch.load("flow_Vg", 1); k = len(x) // 2; gm, i0 = np.gradient(i, x)[k], i[k]
    x, i = ch.load("flow_Vd", 1); gds = np.gradient(i, x)[len(x) // 2]
    return vg, i0, gm, gds


def r_at(tag, v0=0.02):
    """Small-signal resistance dV/dI at v0, as figsrc/ch08_figs.py computes it."""
    v, i = ch.load(tag, 1)
    return float(np.gradient(v, i)[np.argmin(abs(v - v0))])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mc", type=int, default=4000, help="Monte Carlo samples")
    args = ap.parse_args()
    nl = {}
    for g in GMINS:
        for a in ABSTOLS:
            tag = f"flow_gmin_{g:.0e}_{a:.0e}"
            nl[tag] = pseudo(tag, gmin=g, abstol=a)
    for c in CORNERS:
        for t in TEMPS:
            tag = f"flow_corner_{c}_{t}"
            nl[tag] = pseudo(tag, corner=c, temp=t, gmin=CORNER_OPT[0], abstol=CORNER_OPT[1])
    nl["flow_mc"] = mc(args.mc)
    ch.run(nl)
    with open(os.path.join(ch.DATA, "sg13_flow_gmin.csv"), "w") as f:
        f.write("gmin_S,abstol_A,R_ohm\n")
        for g in GMINS:
            for a in ABSTOLS:
                f.write(f"{g:.0e},{a:.0e},{r_at(f'flow_gmin_{g:.0e}_{a:.0e}'):.4e}\n")
    with open(os.path.join(ch.DATA, "sg13_flow_corners.csv"), "w") as f:
        f.write("corner,temp_C,R_ohm\n")
        for c in CORNERS:
            for t in TEMPS:
                f.write(f"{c},{t},{r_at(f'flow_corner_{c}_{t}'):.4e}\n")
    log = open(os.path.join(ch.OUT, "flow_mc.log")).read()
    vos = [float(x) for x in re.findall(r"^VOS\s+(\S+)", log, re.M)]
    with open(os.path.join(ch.DATA, "sg13_flow_mc.csv"), "w") as f:
        f.write("run,vos_V\n")
        for k, v in enumerate(vos):
            f.write(f"{k},{v:.6e}\n")
    vg, i0, gm, gds = gm_gds()
    with open(os.path.join(ch.DATA, "sg13_flow_gmgds.csv"), "w") as f:
        f.write("VGS_V,ID_A,gm_S,gds_S\n")
        f.write(f"{vg:.5f},{i0:.5e},{gm:.5e},{gds:.5e}\n")
    print("Monte Carlo: %d samples, sigma %.3f mV" % (len(vos), np.std(vos, ddof=1) * 1e3))
    print("diode point: VGS %.4f V, gm/gds %.1f, gm/(gm+gds) %.3f" % (vg, gm / gds, gm / (gm + gds)))
    print("wrote", ch.DATA)


if __name__ == "__main__":
    main()
