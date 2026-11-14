"""Lab 9 -- Delta-sigma by design (Open-BioAFE, Chapters 19 and 20).

Noise-transfer functions of first to third order, SQNR versus OSR (linear formula against a
1-bit simulation), the second-order incremental converter of the ECG/EEG channel, and its
cascade-of-integrators (CoI) decimator in integer arithmetic.

    python lab9_deltasigma.py
    python lab9_deltasigma.py --amp 0.3 --n 32768

Needs only NumPy/SciPy (biosig.synth_ntf / simulate_dsm replace python-deltasigma; if you have
python-deltasigma installed, compare synthesizeNTF(3, 128, 1, 1.5) with biosig.synth_ntf(3, 128)).
Outputs go to labs/python/out/ (git-ignored).
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biosig  # noqa: E402

OUT = os.path.join(HERE, "out")


def incremental2_sums(u_dc, m_cycles, a1=0.5, a2=0.25):
    """The incremental loop of biosig.incremental2, returning the integer CoI sums (s1, s2) and the
    largest |x1|, |x2| reached, so the decimator can be built bit-true and the swing checked."""
    u = np.atleast_1d(np.asarray(u_dc, float))
    x1 = np.zeros_like(u); x2 = np.zeros_like(u)
    s1 = np.zeros(u.shape, np.int64); s2 = np.zeros(u.shape, np.int64); run = np.zeros(u.shape, np.int64)
    sw1 = sw2 = 0.0
    for _ in range(m_cycles):
        v = np.where(x2 >= 0, 1, -1)
        s2 += run; run += v; s1 += v
        x2 = x2 + a2 * (x1 - v)
        x1 = x1 + a1 * (u - v)
        sw1 = max(sw1, np.abs(x1).max()); sw2 = max(sw2, np.abs(x2).max())
    return s1, s2, sw1, sw2


def coi_response_db(f, fs, m_cycles, a1=0.5):
    """Magnitude response (dB) of the CoI decimator: bit n of M is weighted 1 + a1*(M-1-n)."""
    n = np.arange(m_cycles)
    w = 1 + a1 * (m_cycles - 1 - n)
    w = w / w.sum()
    return 20 * np.log10(abs(np.sum(w * np.exp(-2j * np.pi * f / fs * n))))


def main():
    ap = argparse.ArgumentParser(description="Lab 9: delta-sigma by design")
    ap.add_argument("--amp", type=float, default=0.5, help="tone amplitude (full scale 1; 0.5 = -6 dBFS)")
    ap.add_argument("--n", type=int, default=65536, help="record length for the SQNR simulations")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    lines = []

    def say(s=""):
        print(s)
        lines.append(s)

    # 1. NTFs
    ntfs = {"MOD1 (1-z^-1)": biosig.ntf_pure(1), "MOD2 (1-z^-1)^2": biosig.ntf_pure(2),
            "MOD3, ||NTF|| = 1.5": biosig.synth_ntf(3, 128, 1.5),
            "MOD3, 1.5, optimised zeros": biosig.synth_ntf(3, 128, 1.5, opt_zeros=True)}
    f = np.linspace(1e-5, 0.5, 20000)
    fb = f[f <= 0.5 / 128]
    say("1. NTFs: max |NTF| and in-band noise power gain at OSR 128")
    for k, (b, a) in ntfs.items():
        h = biosig.ntf_response(b, a, f)
        g = np.trapz(biosig.ntf_response(b, a, fb) ** 2, fb) / 0.5
        say(f"   {k:>27}: max {h.max():5.2f}, in-band {10*np.log10(g):7.1f} dB")

    # 2. SQNR versus OSR: formula and 1-bit simulation
    n, amp = args.n, args.amp
    m = 17                                            # tone bin: in band down to OSR 256 at n = 65536
    u = amp * np.sin(2 * np.pi * m * np.arange(n) / n)
    rows = []
    say(f"2. SQNR at {20*np.log10(amp):.0f} dBFS: formula (1-bit, full scale) / simulation")
    for k, L in (("MOD1 (1-z^-1)", 1), ("MOD2 (1-z^-1)^2", 2), ("MOD3, ||NTF|| = 1.5", 3)):
        v, ok = biosig.simulate_dsm(u, *ntfs[k])
        sims = []
        for osr in (32, 64, 128, 256):
            sims.append(biosig.dsm_sqnr(v, m, osr) if ok and m < n / (2 * osr) - 2 else np.nan)
        form = [biosig.sqnr_os_db(1, osr, L) + 20 * np.log10(amp) for osr in (32, 64, 128, 256)]
        rows.append((k, form, sims, ok))
        say(f"   {k:>20}: " + "  ".join(f"OSR {o}: {fo:5.1f}/{s:5.1f}" for o, fo, s in zip((32, 64, 128, 256), form, sims))
            + ("" if ok else "  UNSTABLE"))

    # 3. Incremental second order (Worked Example 19.3, Chapter 20)
    ud = np.linspace(-0.8, 0.8, 8001)
    say("3. Incremental, second order, a1 = 0.5, a2 = 0.25, 8001 DC inputs over +-0.8 FS:")
    for mc in (256, 512, 1024):
        s1, s2, sw1, sw2 = incremental2_sums(ud, mc)
        est = (s1 + 0.5 * s2) / (0.5 * mc * (mc - 1) / 2)
        err = est - ud
        # bits as in Chapter 19: worst case, half an LSB over +-1 is 1/2^N; rms, LSB/sqrt(12) with LSB = 2/2^N
        say(f"   M = {mc:4d}: worst error {np.abs(err).max():.2e} -> {np.log2(1/np.abs(err).max()):4.1f} bits, "
            f"rms {np.log2(2/(np.sqrt(12)*err.std())):4.1f} bits; swing |x1| {sw1:.2f}, |x2| {sw2:.2f}")
    _, _, _, sw2_half = incremental2_sums(ud[::50], 1024, a2=0.5)
    say(f"   with a2 = 0.5 instead: identical codes, |x2| swing {sw2_half:.2f} (twice)")

    # 4. CoI decimator in integer arithmetic
    mc = 1024
    s1, s2, _, _ = incremental2_sums(ud, mc)
    d = 2 * s1 + s2                                   # integer numerator for a1 = 0.5: 2*(s1 + s2/2)
    full = mc * (mc - 1) // 2
    bits_s1 = int(np.ceil(np.log2(mc + 1))) + 1
    bits_s2 = int(np.ceil(np.log2(full + 1))) + 1
    bits_d = int(np.ceil(np.log2(np.abs(d).max() + 1))) + 1
    out16 = np.floor(d / full * 2 ** 15 + 0.5).astype(int)            # 16-bit output word
    err16 = out16 / 2 ** 15 - ud
    say(f"4. CoI decimator, M = {mc}: registers s1 {bits_s1} b, s2 {bits_s2} b, output sum {bits_d} b (signed); "
        f"rounded to 16 b: worst error {np.abs(err16).max()*2**15:.2f} LSB16")
    for fr in (50.0, 4000.0):
        say(f"   CoI response at {fr:g} Hz (fs 512 kHz): {coi_response_db(fr, 512e3, mc):6.1f} dB")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, (a1_, a2_) = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
        for k, (b, a) in ntfs.items():
            a1_.semilogx(f, 20 * np.log10(biosig.ntf_response(b, a, f)), label=k)
        a1_.axvline(0.5 / 128, color="k", ls=":", lw=0.8)
        a1_.set(xlabel="f / fs", ylabel="|NTF| (dB)", ylim=(-160, 15), title="(a) noise-transfer functions")
        a1_.legend(fontsize=8)
        for i, (k, form, sims, ok) in enumerate(rows):
            a2_.semilogx((32, 64, 128, 256), form, "--", color=f"C{i}")
            a2_.semilogx((32, 64, 128, 256), sims, "o-", color=f"C{i}", label=f"{k} (dashed: formula)")
        a2_.set(xlabel="OSR", ylabel="SQNR (dB)", title=f"(b) SQNR at {20*np.log10(amp):.0f} dBFS")
        a2_.legend(fontsize=8)
        fig.savefig(os.path.join(OUT, "lab9_deltasigma.png"), dpi=130)
        say(f"\nwrote {os.path.join(OUT, 'lab9_deltasigma.png')}")
    except ImportError:
        pass
    with open(os.path.join(OUT, "lab9_summary.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
