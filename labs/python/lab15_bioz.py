"""Lab 15 (Python part) -- Bioimpedance IQ readout (Open-BioAFE, Chapter 28).

A Cole tissue model, bipolar against tetrapolar measurement, digital IQ demodulation of a
noisy 50 kHz measurement in the time domain, and the error of square-wave excitation and
demodulation. The SG13G2 current source and square-wave demodulator follow in the Track B part.

    python lab15_bioz.py
    python lab15_bioz.py --i 50e-6 --vn 30e-9

Currents are rms, as the patient-current limits are. Outputs go to labs/python/out/ (git-ignored).
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biosig  # noqa: E402

OUT = os.path.join(HERE, "out")
R0, RINF, FC, ALPHA = 60.0, 30.0, 30e3, 0.7      # illustrative thoracic segment (Chapter 28)


def cole(f):
    return RINF + (R0 - RINF) / (1 + (1j * np.asarray(f, float) / FC) ** ALPHA)


def iq_measure(i_rms, vn, f_exc=50e3, fs=400e3, dur=10.0, bw=10.0, dz=None, seed=0):
    """Simulate V = I(t) * Z(t) + noise, sampled at fs, and demodulate it digitally.
    vn: white readout noise (V/sqrt(Hz)); bw: noise bandwidth of the boxcar low-pass (Hz).
    dz(t): optional impedance change (ohm, added to the real part). Returns (t_out, |Z| estimate)."""
    rng = np.random.default_rng(seed)
    n = int(dur * fs)
    t = np.arange(n) / fs
    z0 = cole(f_exc)
    zr = z0.real + (0.0 if dz is None else dz(t))
    ip = np.sqrt(2) * i_rms                                        # peak current
    v = ip * (zr * np.cos(2 * np.pi * f_exc * t) - z0.imag * np.sin(2 * np.pi * f_exc * t))
    v += vn * np.sqrt(fs / 2) * rng.standard_normal(n)
    i_ch = v * 2 * np.cos(2 * np.pi * f_exc * t)
    q_ch = -v * 2 * np.sin(2 * np.pi * f_exc * t)
    blk = int(fs / (2 * bw))                                       # boxcar: noise bandwidth 1/(2T) = bw
    m = n // blk
    i_o = i_ch[: m * blk].reshape(m, blk).mean(1)
    q_o = q_ch[: m * blk].reshape(m, blk).mean(1)
    return (np.arange(m) + 0.5) * blk / fs, np.hypot(i_o, q_o) / ip


def square_error(f_exc=50e3, k_max=199):
    """Square-wave excitation demodulated with a square-wave reference: harmonic k (odd) carries
    current 1/k and reference weight 1/k, so the reading is sum Z(kf)/k^2 normalised by pi^2/8."""
    k = np.arange(1, k_max + 1, 2)
    return np.sum(cole(k * f_exc) / k ** 2) / np.sum(1.0 / k ** 2)


def main():
    ap = argparse.ArgumentParser(description="Lab 15: bioimpedance IQ readout (Python part)")
    ap.add_argument("--i", type=float, default=None, help="one excitation current to test (A rms)")
    ap.add_argument("--vn", type=float, default=50e-9, help="readout noise (V/sqrt(Hz))")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    lines = []

    def say(s=""):
        print(s)
        lines.append(s)

    # 1. Cole model
    say(f"1. Cole model R0 {R0:g}, Rinf {RINF:g} Ohm, fc {FC/1e3:g} kHz, alpha {ALPHA:g}:")
    for f in (5e3, 50e3, 100e3, 500e3):
        z = cole(f)
        say(f"   {f/1e3:5.0f} kHz: |Z| {abs(z):5.1f} Ohm, phase {np.degrees(np.angle(z)):6.1f} deg")

    # 2. Bipolar against tetrapolar at 50 kHz
    z = cole(50e3)
    say("2. At 50 kHz, a bipolar measurement adds both electrodes:")
    for kind in ("wet Ag/AgCl", "dry"):
        ze = biosig.z_electrode(50e3, kind)
        say(f"   {kind:>12}: 2 Ze = {abs(2*ze):6.0f} Ohm -> bipolar reads {abs(z + 2*ze):6.0f} Ohm for {abs(z):.1f} Ohm of tissue")
    say("   tetrapolar: the voltage electrodes carry no current, so the tissue's 42 Ohm is read directly")

    # 3. Digital IQ: resolution against current (time-domain simulation)
    say(f"3. Digital IQ, 50 kHz, {args.vn*1e9:g} nV/rtHz, 10 Hz noise bandwidth: rms |Z| noise, simulated / v_n sqrt(B) / I")
    currents = (args.i,) if args.i else (10e-6, 50e-6, 500e-6)
    for i_rms in currents:
        _, zest = iq_measure(i_rms, args.vn, seed=1)
        say(f"   I = {i_rms*1e6:5.0f} µArms: {zest[2:].std()*1e3:6.2f} mOhm / {args.vn*np.sqrt(10)/i_rms*1e3:6.2f} mOhm")

    # 4. Square-wave excitation and demodulation
    zs = square_error()
    say(f"4. Square-wave excitation and reference at 50 kHz: reads {abs(zs):.2f} Ohm, {np.degrees(np.angle(zs)):.1f} deg "
        f"against {abs(z):.2f} Ohm, {np.degrees(np.angle(z)):.1f} deg "
        f"({(abs(zs)/abs(z)-1)*100:+.1f} %); noise folded from odd harmonics x{np.sqrt(np.pi**2/8):.2f}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
        f = np.logspace(2, 7, 400)
        zc = cole(f)
        a1.plot(zc.real, -zc.imag)
        for fm in (5e3, 50e3, 500e3):
            zm = cole(fm)
            a1.plot(zm.real, -zm.imag, "o"); a1.annotate(f"{fm/1e3:g} kHz", (zm.real, -zm.imag), fontsize=8)
        a1.set(xlabel="Re Z (Ω)", ylabel="−Im Z (Ω)", title="(a) Cole plot of the tissue", aspect="equal")

        def resp(t):
            return 0.5 * np.sin(2 * np.pi * 0.25 * t) + 0.1 * np.sin(2 * np.pi * 1.2 * t)
        for i_rms in (10e-6, 50e-6):
            to, zest = iq_measure(i_rms, args.vn, dur=8.0, dz=resp, seed=2)
            a2.plot(to[2:], (zest[2:] - abs(cole(50e3))) * 1e3, lw=0.8, label=f"{i_rms*1e6:.0f} µArms")
        a2.set(xlabel="time (s)", ylabel="ΔZ (mΩ)", title="(b) respiration 0.5 Ω + cardiac 0.1 Ω, recovered")
        a2.legend(fontsize=8)
        fig.savefig(os.path.join(OUT, "lab15_bioz.png"), dpi=130)
        say(f"\nwrote {os.path.join(OUT, 'lab15_bioz.png')}")
    except ImportError:
        pass
    with open(os.path.join(OUT, "lab15_summary.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
