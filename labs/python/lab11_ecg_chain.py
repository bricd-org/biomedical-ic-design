"""Lab 11 -- ECG chain end to end (Open-BioAFE, Chapters 24 and 29).

An ECG goes through a behavioural front-end (input noise, baseline wander, the Table 11.1 range of
+-5 mV at the electrodes) and an N-bit converter, then a Pan-Tompkins QRS detector. The script
measures sensitivity (Se) and positive predictivity (PPV) against ADC bits and input noise, and
against electrode-motion noise at the signal-to-noise ratios of the Noise Stress Test.

    python lab11_ecg_chain.py                    # MIT-BIH 100 + NSTDB 'em' if wfdb works, else synthetic
    python lab11_ecg_chain.py --record 105 --seconds 600
    python lab11_ecg_chain.py --offline

Outputs go to labs/python/out/ (git-ignored).
"""
import argparse
import os
import sys

import numpy as np
from scipy import signal as sps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biosig  # noqa: E402

OUT = os.path.join(HERE, "out")
VFS = 5e-3                      # +-5 mV at the electrodes fills the converter (gain 100 into +-0.5 V)
BEATS = set("NLRBAaJSVrFejnE/fQ?")   # MIT-BIH beat annotation symbols


def pan_tompkins(x, fs):
    """Simplified Pan-Tompkins: 5-15 Hz band-pass, derivative, squaring, 150 ms moving-window
    integral, adaptive threshold, 200 ms refractory period. Returns R-peak times (s)."""
    sos = sps.butter(2, [5, 15], "band", fs=fs, output="sos")
    bp = sps.sosfilt(sos, x)
    d = np.convolve(bp, np.array([1, 2, 0, -2, -1]) * fs / 8, mode="same")
    w = int(0.15 * fs)
    mwi = np.convolve(d ** 2, np.ones(w) / w, mode="same")
    pk, _ = sps.find_peaks(mwi, distance=int(0.2 * fs))
    spki, npki = np.max(mwi[: int(2 * fs)]) * 0.5, np.mean(mwi[: int(2 * fs)]) * 0.5
    det = []
    for p in pk:
        if mwi[p] > npki + 0.25 * (spki - npki):
            det.append(p); spki = 0.125 * mwi[p] + 0.875 * spki
        else:
            npki = 0.125 * mwi[p] + 0.875 * npki
    h = int(0.075 * fs)                               # refine to the band-pass peak within +-75 ms
    r = [p - h + np.argmax(bp[max(p - h, 0): p + h]) for p in det]
    return np.array(r) / fs


def score(det, truth, tol=0.075):
    """Sensitivity and positive predictivity with a +-75 ms match window."""
    det = det[(det > truth.min() - 0.3) & (det < truth.max() + 0.3)]
    tp = sum(np.any(np.abs(det - t) < tol) for t in truth)
    fp = len(det) - sum(np.any(np.abs(truth - d) < tol) for d in det)
    return tp / len(truth), tp / max(tp + fp, 1)


def front_end(x, fs, noise, bits):
    """Add the front-end's noise and 200 µV of 0.3 Hz baseline wander, then quantise over +-VFS."""
    t = np.arange(len(x)) / fs
    return biosig.quantize(x + noise + 200e-6 * np.sin(2 * np.pi * 0.3 * t), bits, VFS)


def load(args):
    if not args.offline:
        try:
            import wfdb
            n = int(args.seconds * 360)
            rec = wfdb.rdrecord(args.record, pn_dir="mitdb", sampto=n)
            ann = wfdb.rdann(args.record, "atr", pn_dir="mitdb", sampto=n)
            x = rec.p_signal[:, 0] * 1e-3                                   # mV -> V
            truth = np.array([s for s, c in zip(ann.sample, ann.symbol) if c in BEATS]) / rec.fs
            em = wfdb.rdrecord("em", pn_dir="nstdb", sampto=n).p_signal[:, 0] * 1e-3
            return x, float(rec.fs), truth, em, f"MIT-BIH {args.record} ({args.seconds:g} s) + NSTDB em"
        except Exception as e:
            print(f"PhysioNet not available ({e.__class__.__name__}: {e}); using synthetic signals")
    fs = 500.0
    t, x, pk = biosig.ecg(fs=fs, duration=60.0, hr=75, hrv=0.05, seed=24)
    rng = np.random.default_rng(11)
    em = sps.sosfiltfilt(sps.butter(2, [1, 20], "band", fs=fs, output="sos"), rng.standard_normal(len(t)))
    em *= 1e-3 / em.std()                                                   # electrode-motion-like, 1-20 Hz
    return x, fs, pk[(pk > 2) & (pk < 58)], em, "synthetic ECG (60 s) + band-limited motion noise"


def main():
    ap = argparse.ArgumentParser(description="Lab 11: ECG chain end to end")
    ap.add_argument("--record", default="100")
    ap.add_argument("--seconds", type=float, default=300.0)
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    x, fs, truth, em, src = load(args)
    lines = []

    def say(s=""):
        print(s)
        lines.append(s)

    say(f"Source: {src}; {len(truth)} beats; converter range +-{VFS*1e3:g} mV")
    bits_list, noises = (3, 4, 5, 6, 8, 10, 12), (0.0, 50e-6, 100e-6, 200e-6)
    res = {}
    say("1. Se / PPV (%) against ADC bits and white input noise (mean of 3 noise seeds)")
    say("   noise    " + " ".join(f"{b:>11d} b" for b in bits_list))
    for nz in noises:
        row = []
        for b in bits_list:
            sc = [score(pan_tompkins(front_end(x, fs, nz * np.random.default_rng(s).standard_normal(len(x)), b), fs), truth)
                  for s in range(3)]
            row.append(np.mean(sc, axis=0) * 100)
        res[nz] = row
        say(f"   {nz*1e6:4.0f} µV " + " ".join(f"{se:5.1f}/{ppv:5.1f}" for se, ppv in row))

    # 2. Noise stress: electrode motion at fixed SNR (NSTDB definition: S from the QRS amplitude)
    idx = (truth * fs).astype(int)
    h = int(0.05 * fs)
    qrs_pp = np.median([np.ptp(x[max(i - h, 0): i + h]) for i in idx])
    s_pow = qrs_pp ** 2 / 8
    say(f"2. Electrode-motion noise at 12 bits (QRS p-p {qrs_pp*1e3:.2f} mV):")
    stress = []
    for snr in (24, 18, 12, 6, 0):
        nz = em[: len(x)] * np.sqrt(s_pow / 10 ** (snr / 10) / np.var(em[: len(x)]))
        se, ppv = score(pan_tompkins(front_end(x, fs, nz, 12), fs), truth)
        stress.append((snr, se * 100, ppv * 100))
        say(f"   SNR {snr:3d} dB: Se {se*100:5.1f} %, PPV {ppv*100:5.1f} %")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
        for nz, row in res.items():
            a1.plot(bits_list, [r[0] for r in row], "o-", label=f"{nz*1e6:.0f} µVrms")
        a1.set(xlabel="ADC bits (±5 mV range)", ylabel="sensitivity (%)", title="(a) QRS sensitivity", ylim=(0, 102))
        a1.legend(fontsize=8)
        s_ = np.array(stress)
        a2.plot(s_[:, 0], s_[:, 1], "o-", label="Se"); a2.plot(s_[:, 0], s_[:, 2], "s--", label="PPV")
        a2.set(xlabel="SNR (dB), electrode motion", ylabel="%", title="(b) noise stress at 12 bits", ylim=(0, 102))
        a2.invert_xaxis(); a2.legend(fontsize=8)
        fig.savefig(os.path.join(OUT, "lab11_ecg_chain.png"), dpi=130)
        say(f"\nwrote {os.path.join(OUT, 'lab11_ecg_chain.png')}")
    except ImportError:
        pass
    with open(os.path.join(OUT, "lab11_summary.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
