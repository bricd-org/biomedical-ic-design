"""sg13_lna.py -- SG13G2 simulations for Chapter 8 (and Lab 4), using the runner in sg13_char.py.

    python labs/spice/sg13_lna.py

  1. MOS-bipolar pseudo-resistors: back-to-back pairs of diode-connected PMOS (W/L = 1/10 um, bulk
     tied to the shared source): one or four lv pairs and one hv (thick-oxide) pair, I versus V from
     -0.6 to +0.6 V at 27 and 85 degC.
  2. Gate capacitance of sg13_lv_nmos at |ID| = 1 uA for W/L = 10/1, 40/4, 100/10 um, from the AC gate
     current at 10 kHz.
Results: figsrc/data/sg13_pseudo.csv, sg13_cgg.csv.
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sg13_char as ch

def pseudo_netlist(temp, pairs, kind, tag):
    """`pairs` back-to-back pairs of diode-connected PMOS (W/L = 1/10 um) in series."""
    lib = "cornerMOSlv.lib mos_tt" if kind == "lv" else "cornerMOShv.lib mos_tt"
    lines, node = [], "a"
    for k in range(pairs):
        mid, nxt = f"m{k}", ("0" if k == pairs - 1 else f"n{k}")
        lines.append(f"XM{2*k} {node} {node} {mid} {mid} sg13_{kind}_pmos w=1u l=10u ng=1 m=1")
        lines.append(f"XM{2*k+1} {nxt} {nxt} {mid} {mid} sg13_{kind}_pmos w=1u l=10u ng=1 m=1")
        node = nxt
    body = "\n".join(lines)
    return f"""* pseudo-resistor: {pairs} pair(s) of diode-connected {kind} PMOS, {temp} degC
.lib {lib}
.temp {temp}
.option gmin=1e-15 abstol=1e-15
Va a 0 0
{body}
.control
dc Va -0.6 0.6 5m
let ia = -i(Va)
wrdata /work/out/{tag}.txt ia
.endc
.end
"""


PSEUDO_CASES = [(27, 1, "lv"), (85, 1, "lv"), (27, 4, "lv"), (85, 4, "lv"), (27, 1, "hv"), (37, 1, "hv"), (85, 1, "hv")]

CGG = """* gate capacitance of sg13_lv_nmos W={w}u L={l}u at 1 uA
.lib cornerMOSlv.lib mos_tt
Vd d 0 0.6
Vg g 0 dc {vgs} ac 1
XM1 d g 0 0 sg13_lv_nmos w={w}u l={l}u ng=1 m=1
.control
ac lin 1 10k 10k
let cgg = abs(imag(i(Vg)))/(2*pi*10e3)
wrdata /work/out/cgg_W{w:g}_L{l:g}.txt cgg
.endc
.end
"""


def main():
    vgs = {}
    for w, l in ch.NOISE_SIZES:
        vg, idd, gm = ch.load(f"gmid_nmos_W{w:g}_L{l:g}", 2)
        vgs[(w, l)] = float(np.interp(np.log(1e-6), np.log(np.maximum(np.abs(idd), 1e-18)), np.abs(vg)))
    nl = {f"pseudo_{k}{p}_{t}": pseudo_netlist(t, p, k, f"pseudo_{k}{p}_{t}") for t, p, k in PSEUDO_CASES}
    nl.update({f"cgg_W{w:g}_L{l:g}": CGG.format(w=w, l=l, vgs=vgs[(w, l)]) for w, l in ch.NOISE_SIZES})
    ch.run(nl)
    with open(os.path.join(ch.DATA, "sg13_pseudo.csv"), "w") as f:
        f.write("device,pairs,temp_C,V,I_A\n")
        for t, p, k in PSEUDO_CASES:
            v, i = ch.load(f"pseudo_{k}{p}_{t}", 1)
            for a, b in zip(v, i):
                f.write(f"{k},{p},{t},{a:.4f},{b:.6e}\n")
    with open(os.path.join(ch.DATA, "sg13_cgg.csv"), "w") as f:
        f.write("W_um,L_um,VGS_V,Cgg_F\n")
        for w, l in ch.NOISE_SIZES:
            _, c = ch.load(f"cgg_W{w:g}_L{l:g}", 1)
            f.write(f"{w:g},{l:g},{vgs[(w, l)]:.4f},{c[0]:.6e}\n")
    print("wrote", ch.DATA)


if __name__ == "__main__":
    main()
