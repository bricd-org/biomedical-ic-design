"""lab10_scds.py -- Lab 10: the second-order delta-sigma loop of Lab 9 with switched-capacitor integrators.

    python labs/spice/lab10_scds.py             # ideal-model reference plus two OTA gains
    python labs/spice/lab10_scds.py --n 8192    # longer records

The loop is the CIFB structure of Figure 20.1 run free (not reset), so its spectrum can be compared
with the ideal model: x1 += a1 (u - v), x2 += a2 (x1 - v), v = sign(x2), with a1 = Cs1/Ci1 =
1.1 pF / 2.2 pF = 0.5 and a2 = Cs2/Ci2 = 0.25 pF / 1 pF = 0.25. Each integrator is the
parasitic-insensitive circuit of Figure 20.2 with SG13G2 transmission-gate switches on two
non-overlapping 512 kHz phases (single-ended, with a +-0.25 V range standing for the chip's
+-0.5 V differential so that the integrators fit a 1.2 V supply); the DAC connects the input side of each sampling capacitor to
VCM +- VREF in phase 2. The OTAs are behavioural (one pole, gain A0, unity-gain bandwidth GBW) so
that their effect can be swept, and the 1-bit quantiser is latched at the end of phase 1.
Input: a coherent tone at -6 dBFS; the in-band SQNR at OSR 128 is compared with the ideal
difference equations run on the same input. ngspice simulates no device noise in a transient,
so kT/C noise is not included (add it in Python: Chapter 20, Worked Example 20.1).
Needs Docker and hpretl/iic-osic-tools:2026.10.
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "python"))
import biosig  # noqa: E402
import sg13_char as ch  # noqa: E402

PLOTS = os.path.join(HERE, "out")
FCLK, VCM, VREF = 512e3, 0.6, 0.25   # single-ended: +-0.25 V stands for the chip's +-0.5 V differential
A1, A2 = 0.5, 0.25
OSR, M_TONE, AMP = 128, 11, 0.5


def netlist(a0_db, gbw, n, tag):
    tc = 1 / FCLK
    a0 = 10 ** (a0_db / 20)
    fin = M_TONE * FCLK / n
    tw = tc / 2 - 40e-9
    return f"""* Lab 10 SC delta-sigma, A0 = {a0_db} dB, GBW = {gbw/1e6:g} MHz
.lib cornerMOSlv.lib mos_tt
.subckt tg a b c cb
XN a c b 0 sg13_lv_nmos w=2u l=0.13u ng=1 m=1
XP a cb b vdd sg13_lv_pmos w=4u l=0.13u ng=1 m=1
.ends
.subckt ota inm out a0=1e3 gbw=5e6
* one-pole inverting amplifier referred to VCM, output clamped to the rails
B1 n1 0 v = -a0 * (v(inm) - {VCM})
R1 n1 n2 1k
C1 n2 0 {{a0 / (6.2832 * gbw * 1e3)}}
B2 out 0 v = max(min({VCM} + v(n2), 1.15), 0.05)
.ends
Vdd vdd 0 1.2
Vcm vcm 0 {VCM}
Vp1 p1 0 pulse(0 1.2 20n 2n 2n {tw} {tc})
Vp2 p2 0 pulse(0 1.2 {tc/2 + 20e-9} 2n 2n {tw} {tc})
Bp1n p1n 0 v = 1.2 - v(p1)
Bp2n p2n 0 v = 1.2 - v(p2)
* quantiser: latch sign(x2) at the end of phase 1 and hold it
Vlat lat 0 pulse(0 1.2 {tc/2 - 15e-9} 1n 1n 5n {tc})
.model swl sw vt=0.6 vh=0.05 ron=100 roff=1e14
Bq qin 0 v = v(x2) > {VCM} ? 1 : -1
Slat qin q lat 0 swl
Cq q 0 1p
Bdac dac 0 v = {VCM} + {VREF} * (v(q) > 0 ? 1 : -1)
* input
Vu u 0 dc {VCM} sin({VCM} {AMP * VREF} {fin})
* integrator 1: Cs1 samples u in phase 1, connects to the DAC level in phase 2
X11 u a1 p1 p1n tg
X12 a1 dac p2 p2n tg
Cs1 a1 b1 1.1p
X13 b1 vcm p1 p1n tg
X14 b1 g1 p2 p2n tg
Ci1 g1 x1 2.2p
XO1 g1 x1 ota a0={a0} gbw={gbw}
* integrator 2: Cs2 samples x1 in phase 1, connects to the DAC level in phase 2
X21 x1 a2 p1 p1n tg
X22 a2 dac p2 p2n tg
Cs2 a2 b2 0.25p
X23 b2 vcm p1 p1n tg
X24 b2 g2 p2 p2n tg
Ci2 g2 x2 1p
XO2 g2 x2 ota a0={a0} gbw={gbw}
.ic v(x1)={VCM} v(x2)={VCM} v(q)=1
.control
tran 20n {(n + 8) * tc} 0 40n
wrdata /work/out/{tag}.txt v(q) v(x1) v(x2)
.endc
.end
"""


def ideal_bits(n):
    tc = 1 / FCLK
    fin = M_TONE * FCLK / n
    k = np.arange(n + 8)
    u = AMP * np.sin(2 * np.pi * fin * (k * tc + 20e-9))   # input as sampled at the start of phase 1
    x1 = x2 = 0.0
    v, s1, s2 = np.empty(len(k)), np.empty(len(k)), np.empty(len(k))
    for i, ui in enumerate(u):
        v[i] = 1.0 if x2 > 0 else -1.0
        x2 = x2 + A2 * (x1 - v[i])
        x1 = x1 + A1 * (ui - v[i])
        s1[i], s2[i] = x1, x2
    return v[8:], s1[8:] * VREF, s2[8:] * VREF


def bits_from(tag, n):
    tc = 1 / FCLK
    t, q, x1, x2 = ch.load(tag, 3)
    tk = (np.arange(n) + 8) * tc + 0.75 * tc            # the latched bit, in the middle of phase 2
    return np.sign(np.interp(tk, t, q)), np.interp(tk, t, x1) - VCM, np.interp(tk, t, x2) - VCM


def main():
    ap = argparse.ArgumentParser(description="Lab 10: switched-capacitor delta-sigma loop")
    ap.add_argument("--n", type=int, default=4096)
    ap.add_argument("--parse-only", action="store_true", help="analyse the outputs of the last run")
    args = ap.parse_args()
    n = args.n
    cases = [(60, 5e6), (40, 5e6), (60, 0.5e6)]
    nl = {f"lab10_{a}dB_{g/1e6:g}MHz": netlist(a, g, n, f"lab10_{a}dB_{g/1e6:g}MHz") for a, g in cases}
    if not args.parse_only:
        from concurrent.futures import ThreadPoolExecutor      # one container per case, in parallel
        with ThreadPoolExecutor(len(nl)) as ex:
            list(ex.map(lambda kv: ch.run({kv[0]: kv[1]}), nl.items()))
    vi, i1, i2 = ideal_bits(n)
    p999 = lambda x: np.percentile(np.abs(x), 99.9)
    print(f"Second-order loop, a1 = {A1}, a2 = {A2}, tone at -6 dBFS (bin {M_TONE} of {n}), OSR {OSR}:")
    print(f"   ideal difference equations      : SQNR {biosig.dsm_sqnr(vi, M_TONE, OSR):5.1f} dB; "
          f"swing (99.9 %) |x1| {p999(i1[200:]):.2f} V, |x2| {p999(i2[200:]):.2f} V")
    rows = {}
    for a, g in cases:
        tag = f"lab10_{a}dB_{g/1e6:g}MHz"
        v, x1, x2 = bits_from(tag, n)
        sq = biosig.dsm_sqnr(v, M_TONE, OSR)
        rows[tag] = (v, sq)
        clipped = np.nonzero((np.abs(x1) > 0.54) | (np.abs(x2) > 0.54))[0]
        start = int(clipped.max()) + 1 if len(clipped) else 0
        print(f"   SC loop, A0 = {a} dB, GBW = {g/1e6:3g} MHz: SQNR {sq:5.1f} dB; "
              f"swing after start-up (99.9 %) |x1| {p999(x1[200:]):.2f} V, |x2| {p999(x2[200:]):.2f} V; "
              f"integrators clip only in the first {start} cycles")
    os.makedirs(PLOTS, exist_ok=True)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 4.2), constrained_layout=True)
        f = np.fft.rfftfreq(n, 1 / FCLK)
        for lab, v in [("ideal", vi)] + [(k.replace("lab10_", "SC, "), rows[k][0]) for k in rows]:
            p = np.abs(np.fft.rfft(v * np.hanning(n) ** 2)) ** 2
            ax.semilogx(f[1:], 10 * np.log10(p[1:] / p.max() + 1e-20), lw=0.6, label=lab)
        ax.axvline(FCLK / (2 * OSR), color="k", ls=":", lw=0.8)
        ax.set(xlabel="frequency (Hz)", ylabel="dBFS", ylim=(-160, 5), title="Switched-capacitor loop against the ideal model")
        ax.legend(fontsize=8)
        fig.savefig(os.path.join(PLOTS, "lab10_scds.png"), dpi=130)
        print("wrote", os.path.join(PLOTS, "lab10_scds.png"))
    except ImportError:
        pass


if __name__ == "__main__":
    main()
