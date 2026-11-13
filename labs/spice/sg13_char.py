"""sg13_char.py -- characterise IHP SG13G2 devices for Part II (and Lab 3) with ngspice in the
IIC-OSIC-TOOLS container, and write compact CSV files that the figure scripts read.

    python labs/spice/sg13_char.py            # needs Docker and hpretl/iic-osic-tools:2026.10

What it runs (tt corner, 27 degC):
  1. gm/ID sweeps of sg13_lv_nmos / sg13_lv_pmos, W = 10 um, L = 0.5, 1, 4 um, |VDS| = 0.6 V
  2. input-referred noise of both devices at |ID| = 1 uA for W/L = 10/1, 40/4, 100/10 um
  3. IC, IB versus VBE of the npn13G2 HBT (Nx = 1) at VCE = 0.6 V, and its input-referred
     voltage noise at IC = 1 uA
Results: figsrc/data/sg13_gmid.csv, sg13_noise.csv, sg13_hbt.csv, sg13_hbt_noise.csv.
"""
import os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "char")
OUT = os.path.join(WORK, "out")
DATA = os.path.normpath(os.path.join(HERE, "..", "..", "figsrc", "data"))
IMAGE = "hpretl/iic-osic-tools:2026.10"
SPICEINIT = """* load the SG13G2 compact models
osdi '/foss/pdks/ihp-sg13g2/libs.tech/ngspice/osdi/psp103.osdi'
osdi '/foss/pdks/ihp-sg13g2/libs.tech/ngspice/osdi/r3_cmc.osdi'
setcs sourcepath = ( $sourcepath /foss/pdks/ihp-sg13g2/libs.tech/ngspice/models )
"""
LENGTHS = [0.5, 1.0, 4.0]
NOISE_SIZES = [(10.0, 1.0), (40.0, 4.0), (100.0, 10.0)]
ID_NOISE = 1e-6


def mos(kind, w, l):
    return f"XM1 dd g 0 0 sg13_lv_{kind} w={w}u l={l}u ng=1 m=1"


def gmid_netlist(kind, w, l, tag):
    s = 1 if kind == "nmos" else -1
    return f"""* gm/ID sweep {kind} W={w}u L={l}u
.lib cornerMOSlv.lib mos_tt
Vd d 0 {0.6*s}
Vsense dd d 0
Vg g 0 0
{mos(kind, w, l)}
.control
dc Vg 0 {1.2*s} {0.002*s}
let id = {'-' if s > 0 else ''}i(Vsense)
let gm = abs(deriv(id))
wrdata /work/out/{tag}.txt id gm
.endc
.end
"""


def noise_netlist(kind, w, l, vgs, tag):
    s = 1 if kind == "nmos" else -1
    return f"""* noise {kind} W={w}u L={l}u at |ID| = {ID_NOISE}
.lib cornerMOSlv.lib mos_tt
Vd d 0 {0.6*s}
Vsense dd d 0
Vg g 0 dc {vgs} ac 1
{mos(kind, w, l)}
H1 out 0 Vsense 1
Rl out 0 1meg
.control
op
print i(Vsense)
noise v(out) Vg dec 10 0.1 1meg
setplot noise1
wrdata /work/out/{tag}.txt inoise_spectrum
.endc
.end
"""


HBT_NOISE = """* npn13G2 input-referred voltage noise at IC = 1 uA (base driven by a voltage source)
.lib cornerHBT.lib hbt_typ
Vc c 0 0.6
Vsense cc c 0
Vb b 0 dc VBEBIAS ac 1
XQ1 cc b 0 0 npn13G2 Nx=1
H1 out 0 Vsense 1
Rl out 0 1meg
.control
op
print i(Vsense)
noise v(out) Vb dec 10 0.1 1meg
setplot noise1
wrdata /work/out/hbt_noise.txt inoise_spectrum
.endc
.end
"""

HBT_NETLIST = """* npn13G2 IC, IB versus VBE
.lib cornerHBT.lib hbt_typ
Vc c 0 0.6
Vb b 0 0.7
XQ1 c b 0 0 npn13G2 Nx=1
.control
dc Vb 0.5 0.95 1m
let ic = -i(Vc)
let ib = -i(Vb)
wrdata /work/out/hbt.txt ic ib
.endc
.end
"""


def run(netlists):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(WORK, ".spiceinit"), "w") as f:
        f.write(SPICEINIT)
    names = []
    for name, text in netlists.items():
        with open(os.path.join(WORK, name + ".cir"), "w") as f:
            f.write(text)
        names.append(name)
    loop = " ; ".join(f"ngspice -b {n}.cir > out/{n}.log 2>&1 < /dev/null" for n in names)
    cmd = ["docker", "run", "--rm", "-v", f"{WORK}:/work", "-w", "/work", "--entrypoint", "/bin/bash",
           IMAGE, "-lc", loop]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


def load(tag, ncol):
    a = np.loadtxt(os.path.join(OUT, tag + ".txt"))
    return [a[:, 0]] + [a[:, 2 * k + 1] for k in range(ncol)]


def main():
    os.makedirs(DATA, exist_ok=True)
    # pass 1: gm/ID sweeps (also used to find the noise bias) and the HBT
    nl = {f"gmid_{k}_W{w:g}_L{l:g}": gmid_netlist(k, w, l, f"gmid_{k}_W{w:g}_L{l:g}")
          for k in ("nmos", "pmos") for (w, l) in sorted(set([(10.0, L) for L in LENGTHS] + NOISE_SIZES))}
    nl["hbt"] = HBT_NETLIST
    run(nl)
    rows = []
    vgs_at = {}
    for k in ("nmos", "pmos"):
        for (w, l) in sorted(set([(10.0, L) for L in LENGTHS] + NOISE_SIZES)):
            vg, idd, gm = load(f"gmid_{k}_W{w:g}_L{l:g}", 2)
            idd = np.abs(idd)
            vg = np.abs(vg)
            vgs_at[(k, w, l)] = float(np.interp(np.log(ID_NOISE), np.log(np.maximum(idd, 1e-18)), vg))
            if (w, l) in [(10.0, L) for L in LENGTHS]:
                for a, b_, c in zip(vg, idd, gm):
                    rows.append((k, w, l, a, b_, c))
    with open(os.path.join(DATA, "sg13_gmid.csv"), "w") as f:
        f.write("device,W_um,L_um,VGS_V,ID_A,gm_S\n")
        for r in rows:
            f.write(f"{r[0]},{r[1]:g},{r[2]:g},{r[3]:.4f},{r[4]:.6e},{r[5]:.6e}\n")
    vb, ic, ib = load("hbt", 2)
    with open(os.path.join(DATA, "sg13_hbt.csv"), "w") as f:
        f.write("VBE_V,IC_A,IB_A\n")
        for a, b_, c in zip(vb, ic, ib):
            f.write(f"{a:.4f},{b_:.6e},{c:.6e}\n")
    # pass 2: noise at |ID| = 1 uA
    s = {"nmos": 1, "pmos": -1}
    nl = {f"noise_{k}_W{w:g}_L{l:g}": noise_netlist(k, w, l, s[k] * vgs_at[(k, w, l)], f"noise_{k}_W{w:g}_L{l:g}")
          for k in ("nmos", "pmos") for (w, l) in NOISE_SIZES}
    vbe1 = float(np.interp(np.log(1e-6), np.log(np.maximum(ic, 1e-18)), vb))
    nl["hbt_noise"] = HBT_NOISE.replace("VBEBIAS", f"{vbe1:.5f}")
    run(nl)
    fr, vn = load("hbt_noise", 1)
    with open(os.path.join(DATA, "sg13_hbt_noise.csv"), "w") as f:
        f.write("f_Hz,vn_V_per_rtHz\n")
        for a, b_ in zip(fr, vn):
            f.write(f"{a:.5g},{b_:.6e}\n")
    with open(os.path.join(DATA, "sg13_noise.csv"), "w") as f:
        f.write("device,W_um,L_um,VGS_V,f_Hz,vn_V_per_rtHz\n")
        for k in ("nmos", "pmos"):
            for (w, l) in NOISE_SIZES:
                fr, vn = load(f"noise_{k}_W{w:g}_L{l:g}", 1)
                for a, b_ in zip(fr, vn):
                    f.write(f"{k},{w:g},{l:g},{vgs_at[(k, w, l)]:.4f},{a:.5g},{b_:.6e}\n")
    print("wrote", DATA)


if __name__ == "__main__":
    sys.exit(main())
