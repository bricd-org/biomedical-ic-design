"""lab4_lna.py -- Lab 4: the capacitive-feedback (Harrison) LNA in SG13G2, simulated with ngspice.

    python labs/spice/lab4_lna.py                 # operating point, AC, noise and an NEF sweep
    python labs/spice/lab4_lna.py --pr lv4        # four thin-oxide pseudo-resistor pairs instead of one thick-oxide pair

The amplifier is the single-ended Harrison topology of Chapter 8: C1 = 20 pF from the input to the
OTA's inverting input, C2 = 200 fF with a pseudo-resistor from the output back to it, the
non-inverting input at VREF, and CL = 2 pF. The OTA is an NMOS-input folded cascode (a telescopic
cascode cannot hold its output at the input common mode here: the large weak-inversion input pair
leaves its tail only ~50 mV below VREF). Its gain is well above 60 dB, so C1/C2 sets the gain.
Its input devices are 250/4 um (1000 um^2, Table B.5), thick-oxide by default: a thin-oxide pair
leaks 3-25 pA through its gate, more than the teraohm pseudo-resistor can carry, and the bias fails
(run --input lv to see it; Chapter 8, Section 8.5). The tail current is mirrored from IBIAS.
The cascode gates use ideal bias sources: replacing them with bias transistors is an exercise.
Needs Docker and hpretl/iic-osic-tools:2026.10 (see the set-up section of Chapter 31).
Outputs: labs/spice/char/out/lab4_*.txt and labs/spice/out/lab4_*.png (git-ignored).
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sg13_char as ch  # noqa: E402

PLOTS = os.path.join(HERE, "out")
K_B, T, Q = 1.380649e-23, 300.0, 1.602177e-19
UT = K_B * T / Q

VDD, VREF, VCN, VCP = 1.2, 0.65, 0.62, 0.45
C1, C2, CL = 20e-12, 200e-15, 2e-12
WIN, LIN = 250, 4          # input pair (um)


def pseudo(kind, a, b, tag):
    """Pseudo-resistor between nodes a and b: one thick-oxide pair (hv1) or four thin-oxide pairs (lv4)."""
    if kind == "hv1":
        return (f"XPR{tag}1 {a} {a} pm{tag}0 pm{tag}0 sg13_hv_pmos w=1u l=10u ng=1 m=1\n"
                f"XPR{tag}2 {b} {b} pm{tag}0 pm{tag}0 sg13_hv_pmos w=1u l=10u ng=1 m=1")
    lines, node = [], a
    for k in range(4):
        mid, nxt = f"pm{tag}{k}", (b if k == 3 else f"pn{tag}{k}")
        lines.append(f"XPR{tag}{2*k} {node} {node} {mid} {mid} sg13_lv_pmos w=1u l=10u ng=1 m=1")
        lines.append(f"XPR{tag}{2*k+1} {nxt} {nxt} {mid} {mid} sg13_lv_pmos w=1u l=10u ng=1 m=1")
        node = nxt
    return "\n".join(lines)


def ota(ibias, inp_kind="hv"):
    """Folded-cascode OTA with an NMOS input pair: inp = non-inverting, inn = inverting input, out.
    The folding PMOS sources and the NMOS mirror are long devices in strong inversion (inversion
    coefficient about 20 and 10), scaled with the bias current, so that their low gm/I and large area
    keep their thermal and flicker noise small when referred to the input."""
    k = ibias / 1e-6
    wp, wn = 10 * k, 4 * k
    return f"""* --- folded-cascode OTA, tail = {ibias*1e6:g} uA
Iref vdd nb {ibias}
XMB nb nb 0 0 sg13_lv_nmos w=10u l=4u ng=1 m=1
XMT tail nb 0 0 sg13_lv_nmos w=10u l=4u ng=1 m=1
Ibp bp 0 {ibias}
XMPB bp bp vdd vdd sg13_lv_pmos w={wp:g}u l=40u ng=1 m=1
XM1 f1 inp tail 0 sg13_{inp_kind}_nmos w={WIN}u l={LIN}u ng=1 m=1
XM2 f2 inn tail 0 sg13_{inp_kind}_nmos w={WIN}u l={LIN}u ng=1 m=1
XM5 f1 bp vdd vdd sg13_lv_pmos w={wp:g}u l=40u ng=1 m=1
XM6 f2 bp vdd vdd sg13_lv_pmos w={wp:g}u l=40u ng=1 m=1
XM7 c1 vcp f1 vdd sg13_lv_pmos w=20u l=1u ng=1 m=1
XM8 out vcp f2 vdd sg13_lv_pmos w=20u l=1u ng=1 m=1
XM11 c1 vcn y1 0 sg13_lv_nmos w=10u l=1u ng=1 m=1
XM12 out vcn y2 0 sg13_lv_nmos w=10u l=1u ng=1 m=1
XM9 y1 c1 0 0 sg13_lv_nmos w={wn:g}u l=64u ng=1 m=1
XM10 y2 c1 0 0 sg13_lv_nmos w={wn:g}u l=64u ng=1 m=1
Vcn vcn 0 {VCN}
Vcp vcp 0 {VCP}
"""


def lna(ibias, pr, tag, analysis, inp_kind="hv"):
    return f"""* Lab 4 LNA, tail {ibias*1e6:g} uA, pseudo-resistor {pr}, {inp_kind} input pair
.lib cornerMOSlv.lib mos_tt
.lib cornerMOShv.lib mos_tt
.option gmin=1e-15 abstol=1e-15
Vdd vdd 0 {VDD}
Vref inp 0 {VREF}
Vin in 0 dc {VREF} ac 1
C1 in inn {C1}
C2 out inn {C2}
CL out 0 {CL}
{pseudo(pr, 'out', 'inn', 'f')}
{ota(ibias, inp_kind)}
.control
{analysis}
.endc
.end
"""


def an_op(tag):
    return f"""op
print v(inn) v(out) v(tail) v(f1) v(f2) v(c1) v(y1) v(y2) v(bp) v(nb)
print i(Vdd)
"""


def an_ac(tag):
    return f"""ac dec 20 1m 10meg
let g = vdb(out)
let ph = 180/pi*cph(v(out))
wrdata /work/out/{tag}.txt g ph
"""


def an_noise(tag):
    return f"""noise v(out) Vin dec 20 10m 10meg
setplot noise1
wrdata /work/out/{tag}.txt onoise_spectrum inoise_spectrum
"""


def main():
    ap = argparse.ArgumentParser(description="Lab 4: the Harrison LNA in SG13G2")
    ap.add_argument("--pr", choices=["hv1", "lv4"], default="hv1")
    ap.add_argument("--input", choices=["hv", "lv"], default="hv",
                    help="thick-oxide (hv) or thin-oxide (lv) input pair; lv shows the gate-leakage failure")
    ap.add_argument("--oponly", action="store_true")
    args = ap.parse_args()
    biases = (0.5e-6, 1e-6, 2e-6, 4e-6)
    nl = {f"lab4_op_{b*1e6:g}": lna(b, args.pr, "", an_op(""), args.input) for b in biases}
    if not args.oponly:
        for b in biases:
            nl[f"lab4_ac_{b*1e6:g}"] = lna(b, args.pr, "", an_ac(f"lab4_ac_{b*1e6:g}"), args.input)
            nl[f"lab4_noise_{b*1e6:g}"] = lna(b, args.pr, "", an_noise(f"lab4_noise_{b*1e6:g}"), args.input)
    ch.run(nl)
    for b in biases:
        log = open(os.path.join(ch.OUT, f"lab4_op_{b*1e6:g}.log")).read()
        vals = {k: float(v) for k, v in
                __import__("re").findall(r"^(v\(\w+\)|i\(vdd\)) = ([-+0-9.eE]+)", log, __import__("re").M)}
        print(f"tail {b*1e6:4g} uA: " + "  ".join(f"{k}={v:.3f}" for k, v in vals.items() if k.startswith("v")))
    if args.oponly:
        return

    os.makedirs(PLOTS, exist_ok=True)
    rows = []
    for b in biases:
        f, g, ph = ch.load(f"lab4_ac_{b*1e6:g}", 2)
        fn, on, inn = ch.load(f"lab4_noise_{b*1e6:g}", 2)
        am = g.max()
        band = f[g >= am - 3]
        fl, fh = band.min(), band.max()
        a_lin = 10 ** (am / 20)
        sel = (fn >= 0.5) & (fn <= 100)
        v_eeg = np.sqrt(np.trapz(on[sel] ** 2, fn[sel])) / a_lin
        v_tot = np.sqrt(np.trapz(on ** 2, fn)) / a_lin          # all of the output noise, referred to the input
        itot = b                                                # OTA supply current = tail current
        nef = v_tot * np.sqrt(2 * itot / (np.pi * UT * 4 * K_B * T * fh))
        th = (fn > 2e3) & (fn < 5e3)
        rows.append((b, am, fl, fh, v_eeg, v_tot, nef, np.median(inn[th])))
    print("\n tail   A_M      f_L        f_H     noise 0.5-100 Hz   total noise   NEF   white floor")
    for b, am, fl, fh, ve, vt, nef, wf in rows:
        print(f" {b*1e6:4g} uA {am:5.1f} dB {fl:8.3g} Hz {fh/1e3:6.1f} kHz {ve*1e6:8.2f} µVrms {vt*1e6:9.2f} µVrms "
              f"{nef:5.2f} {wf*1e9:6.1f} nV/rtHz")
    with open(os.path.join(PLOTS, "lab4_summary.txt"), "w") as fh_:
        for r in rows:
            fh_.write(" ".join(f"{x:.6g}" for x in r) + "\n")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
        for b in biases:
            f, g, _ = ch.load(f"lab4_ac_{b*1e6:g}", 2)
            a1.semilogx(f, g, label=f"{b*1e6:g} µA")
            fn, on, inn = ch.load(f"lab4_noise_{b*1e6:g}", 2)
            a2.loglog(fn, inn * 1e9, label=f"{b*1e6:g} µA")
        a1.set(xlabel="frequency (Hz)", ylabel="gain (dB)", title=f"(a) closed-loop gain, pseudo-resistor {args.pr}")
        a2.set(xlabel="frequency (Hz)", ylabel="input noise (nV/√Hz)", title="(b) input-referred noise", ylim=(5, 1e4))
        a1.legend(fontsize=8); a2.legend(fontsize=8)
        fig.savefig(os.path.join(PLOTS, "lab4_lna.png"), dpi=130)
        print("wrote", os.path.join(PLOTS, "lab4_lna.png"))
    except ImportError:
        pass


if __name__ == "__main__":
    main()
