"""Lab 2 -- Electrodes and interference (Open-BioAFE, Chapters 3, 4 and 12).

A phasor model of Figure 4.1: mains -> body -> electrodes -> amplifier. It computes the body's
common-mode voltage, converts common mode into differential interference through the electrode
imbalance and the amplifier's common-mode input impedance Zcm, combines that with the amplifier's
own CMRR, adds a behavioural right-leg drive (RLD), and runs the 10 Vrms CMRR test of the ECG
standards. Every number should match Worked Examples 4.1-4.4 and Chapter 12.

    python lab2_electrodes_interference.py
    python lab2_electrodes_interference.py --f 60 --rld 40 --cmrr 110

Outputs go to labs/python/out/ (git-ignored).
"""
import argparse
import os
import sys

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biosig  # noqa: E402

OUT = os.path.join(HERE, "out")


def z_imbalance(f, r=51e3, c=47e-9):
    """The standards' imbalance network, r || c, in one lead."""
    return r / (1 + 1j * 2 * np.pi * f * r * c)


def v_dm(v_cm, dz, zcm, cmrr_db, rld_gain=0.0):
    """Worst-case differential interference (Vrms): the RLD divides the common mode at the
    electrodes by 1 + A; the imbalance term dZ/Zcm and the amplifier's 10^(-CMRR/20) add."""
    return v_cm / (1 + rld_gain) * (abs(dz) / zcm + 10 ** (-cmrr_db / 20))


def eff_cmrr_db(dz, zcm, cmrr_db, rld_gain=0.0):
    return -20 * np.log10(v_dm(1.0, dz, zcm, cmrr_db, rld_gain))


def zcm_needed(target_db, dz, cmrr_db, rld_gain=0.0):
    """Smallest Zcm that reaches target_db of effective CMRR (inf if the amplifier alone fails)."""
    room = 10 ** (-target_db / 20) * (1 + rld_gain) - 10 ** (-cmrr_db / 20)
    return abs(dz) / room if room > 0 else np.inf


def eng(x, unit):
    for div, p in ((1e9, "G"), (1e6, "M"), (1e3, "k"), (1, ""), (1e-3, "m"), (1e-6, "µ"), (1e-9, "n")):
        if abs(x) >= div:
            return f"{x/div:.3g} {p}{unit}"
    return f"{x:.3g} {unit}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--f", type=float, default=50.0, help="mains frequency (Hz)")
    ap.add_argument("--vmains", type=float, default=230.0, help="mains voltage (Vrms)")
    ap.add_argument("--cmrr", type=float, default=100.0, help="amplifier's own CMRR (dB)")
    ap.add_argument("--rld", type=float, default=100.0, help="right-leg-drive loop gain at f")
    ap.add_argument("--target", type=float, default=90.0, help="effective CMRR target (dB)")
    args = ap.parse_args()
    f, A = args.f, args.rld
    os.makedirs(OUT, exist_ok=True)
    out = []

    def say(s=""):
        print(s)
        out.append(s)

    # 1. The body's common mode (Worked Example 4.1)
    z_gnd = biosig.z_electrode(f, "wet Ag/AgCl")             # 1 kOhm + 51 kOhm || 47 nF
    v_float = biosig.body_cm_voltage(args.vmains, f)
    v_cm = biosig.body_cm_voltage(args.vmains, f, z_ground=z_gnd)
    say(f"1. Body common mode at {f:g} Hz: floating {v_float:.2f} Vrms; "
        f"with a wet ground electrode ({eng(abs(z_gnd), 'Ohm')}) {eng(v_cm, 'Vrms')}; "
        f"with an RLD of loop gain {A:g}: {eng(v_cm/(1+A), 'Vrms')}")

    # 2. Common mode to differential through the imbalance (Worked Example 4.2)
    dz = z_imbalance(f)
    z1 = 1e3                                                 # matched part of both electrodes
    say(f"2. Imbalance 51 kOhm || 47 nF = {eng(abs(dz), 'Ohm')} at {f:g} Hz; "
        f"Vdm for {eng(v_cm, 'Vrms')} of common mode:")
    for zcm in (10e6, 100e6, 1e9, 10e9):
        vd = biosig.cm_to_dm(v_cm, z1, z1 + dz, zcm)
        say(f"     Zcm = {eng(zcm, 'Ohm'):>9}: {eng(vd, 'Vrms'):>12}"
            f"   ({vd/1.5e-6:.2g} x the 1.5 µVrms noise target)")

    # 3. The effective CMRR and the Zcm it needs (Worked Example 4.4)
    say(f"3. Zcm for {args.target:g} dB effective CMRR with an amplifier of:")
    for c in (90.5, 100.0, 120.0):
        say(f"     {c:5.1f} dB: {eng(zcm_needed(args.target, dz, c), 'Ohm'):>9} without RLD,"
            f" {eng(zcm_needed(args.target, dz, c, A), 'Ohm'):>9} with loop gain {A:g}")

    # 4. The CMRR test of the ECG standards (Worked Example 4.3, Chapter 12)
    v_test, limit = 10.0, 1e-3
    zb, cb, _ = biosig.cmrr_test_zcm(f, v_test, limit)
    say(f"4. CMRR test, {v_test:g} Vrms, limit {limit*1e3:g} mVpp: required CMRR "
        f"{biosig.required_cmrr_db(v_test, limit):.1f} dB; imbalance alone needs "
        f"Zcm >= {eng(zb, 'Ohm')} ({cb*1e12:.2f} pF) without RLD, {eng(zb/(1+A), 'Ohm')} with loop gain {A:g}")
    for name, zcm in (("chopped, unboosted", 6.25e6), ("boosted", 200e6)):
        for a in (0.0, 10.0, A):
            r = 2 * np.sqrt(2) * v_dm(v_test, dz, zcm, args.cmrr, a)
            verdict = f"pass, {20*np.log10(limit/r):.0f} dB margin" if r < limit else "FAIL"
            say(f"     {name:>18} front-end ({eng(zcm, 'Ohm')}), RLD gain {a:>4g}: "
                f"{r*1e3:7.3f} mVpp  {verdict}")

    # 5. Shields: grounded versus driven (Chapter 4 pitfall, Chapter 12)
    c_shield, z_amp = 100e-12, 2e9                          # 1 m of lead; amplifier's own Zcm
    for name, c_eff in (("grounded shield", c_shield), ("driven shield, 1 % error", 0.01 * c_shield)):
        zs = 1 / (2 * np.pi * f * c_eff)
        zcm = 1 / (1 / zs + 1 / z_amp)
        say(f"5. {name:>24}: Zcm {eng(zcm, 'Ohm'):>9}, Vdm {eng(biosig.cm_to_dm(v_cm, z1, z1 + dz, zcm), 'Vrms')}")

    # Figure: (a) Vdm vs imbalance for four Zcm, (b) effective CMRR vs Zcm, with and without RLD
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    dzs = np.logspace(2, 6, 200)
    for zcm in (10e6, 100e6, 1e9, 10e9):
        a1.loglog(dzs, v_cm * dzs / zcm * 1e6, label=f"Zcm = {eng(zcm, 'Ω')}")
    a1.axvline(abs(dz), color="k", ls=":", lw=0.8)
    a1.axhline(1.5, color="C3", ls="--", lw=0.8, label="1.5 µVrms noise target")
    a1.set(xlabel="electrode imbalance |ΔZ| (Ω)", ylabel="mains on the signal (µVrms)",
           title=f"(a) {eng(v_cm, 'Vrms')} common mode, no RLD")
    a1.legend(fontsize=8)
    zcms = np.logspace(6, 11, 200)
    for c in (80.0, 100.0, 120.0):
        a2.semilogx(zcms, eff_cmrr_db(dz, zcms, c), label=f"amp {c:g} dB")
    a2.semilogx(zcms, eff_cmrr_db(dz, zcms, args.cmrr, A), "k--", label=f"amp {args.cmrr:g} dB + RLD {A:g}")
    a2.axhline(args.target, color="C3", ls=":", lw=0.8)
    a2.set(xlabel="common-mode input impedance Zcm (Ω)", ylabel="effective CMRR (dB)",
           title="(b) the input impedance sets the rejection", ylim=(40, 170))
    a2.legend(fontsize=8)
    png = os.path.join(OUT, "lab2_interference.png")
    fig.savefig(png, dpi=130)
    txt = os.path.join(OUT, "lab2_summary.txt")
    with open(txt, "w") as fh:
        fh.write("\n".join(out) + "\n")
    print(f"\nwrote {png}\nwrote {txt}")


if __name__ == "__main__":
    main()
