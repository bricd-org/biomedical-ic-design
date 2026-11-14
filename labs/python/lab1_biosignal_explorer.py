"""Lab 1 -- Biosignal explorer (Open-BioAFE, Chapter 2).

Load one ECG, one EEG and one EMG recording, plot the traces and their spectra, measure the
amplitude and the power bandwidth of each, and write your own version of Table 2.1.

    python lab1_biosignal_explorer.py                  # PhysioNet if wfdb is installed, else synthetic
    python lab1_biosignal_explorer.py --offline        # synthetic signals from biosig.py only
    python lab1_biosignal_explorer.py --chbmit chb01_03.edf --ninapro S1_E1_A1.mat

Sources
  ECG  MIT-BIH Arrhythmia Database, record 100, lead MLII, 360 S/s (streamed from PhysioNet by wfdb)
  EEG  CHB-MIT Scalp EEG Database, an EDF file such as chb01/chb01_03.edf (~40 MB), 256 S/s;
       give a local path with --chbmit, or let wfdb stream chb01_03.edf from PhysioNet
  EMG  NinaPro (DB2 or similar): download a subject's .mat file after registering and pass it
       with --ninapro; the 'emg' array is read, 2 kS/s
Any source that cannot be loaded falls back to the synthetic signal of biosig.py, and the table
says which one was used. Outputs go to labs/python/out/ (git-ignored).
"""
import argparse
import os
import sys

import numpy as np
from scipy import signal as sps

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import biosig  # noqa: E402

OUT = os.path.join(HERE, "out")
UNIT = {"uv": 1e-6, "µv": 1e-6, "mv": 1e-3, "v": 1.0}


def _wfdb():
    try:
        import wfdb
        return wfdb
    except ImportError:
        return None


def _scale(units):
    return UNIT.get(str(units).strip().lower(), 1.0)


def load_ecg(seconds, offline):
    wfdb = None if offline else _wfdb()
    if wfdb is not None:
        try:
            rec = wfdb.rdrecord("100", pn_dir="mitdb", sampto=int(seconds * 360))
            k = rec.sig_name.index("MLII") if "MLII" in rec.sig_name else 0
            x = rec.p_signal[:, k] * _scale(rec.units[k])
            return x, float(rec.fs), "MIT-BIH 100, MLII"
        except Exception as e:  # network down, PhysioNet moved, ...
            print(f"  ECG: PhysioNet failed ({e.__class__.__name__}: {e}); using synthetic")
    _, x, _ = biosig.ecg(fs=500.0, duration=seconds)
    return x, 500.0, "synthetic (biosig.ecg)"


def load_eeg(seconds, offline, path):
    wfdb = None if offline else _wfdb()
    if wfdb is not None:
        try:
            if path:
                rec = wfdb.rdrecord(path)
            else:
                rec = wfdb.rdrecord("chb01_03.edf", pn_dir="chbmit/1.0.0/chb01")
            k = rec.sig_name.index("FP1-F7") if "FP1-F7" in rec.sig_name else 0
            n = int(seconds * rec.fs)
            start = int(60 * rec.fs)                      # skip the first minute (settling)
            x = rec.p_signal[start:start + n, k] * _scale(rec.units[k])
            return x, float(rec.fs), f"CHB-MIT {os.path.basename(path or 'chb01_03.edf')}, {rec.sig_name[k]}"
        except Exception as e:
            print(f"  EEG: EDF load failed ({e.__class__.__name__}: {e}); using synthetic")
    _, x = biosig.eeg(fs=256.0, duration=seconds)
    return x, 256.0, "synthetic (biosig.eeg)"


def load_emg(seconds, path, scale):
    if path:
        try:
            from scipy.io import loadmat
            m = loadmat(path)
            fs = float(np.squeeze(m.get("frequency", 2000.0)))
            x = np.asarray(m["emg"], float)[: int(seconds * fs), 0] * scale
            return x, fs, f"NinaPro {os.path.basename(path)}, ch 1"
        except Exception as e:
            print(f"  EMG: NinaPro load failed ({e.__class__.__name__}: {e}); using synthetic")
    _, x = biosig.emg(fs=2000.0, duration=min(seconds, 4.0))
    return x, 2000.0, "synthetic (biosig.emg)"


def measure(x, fs, f_hp):
    """High-pass at the signal's lower band edge (removes baseline and electrode drift), then
    amplitude (robust peak-to-peak, RMS) and the 2.5-97.5 % power bandwidth."""
    sos = sps.butter(2, f_hp, "highpass", fs=fs, output="sos")
    y = sps.sosfiltfilt(sos, x - np.median(x))
    a = biosig.amplitude_stats(y)
    f, p = biosig.psd(y, fs)
    keep = f >= f_hp
    lo, hi = biosig.band_edges(f[keep], p[keep])
    return y, f, p, a, (lo, hi)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--offline", action="store_true", help="use the synthetic signals only")
    ap.add_argument("--chbmit", help="local CHB-MIT .edf file")
    ap.add_argument("--ninapro", help="local NinaPro .mat file")
    ap.add_argument("--ninapro-scale", type=float, default=1.0, help="factor to volts for the .mat data")
    ap.add_argument("--seconds", type=float, default=10.0)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    if _wfdb() is None and not args.offline:
        print("wfdb is not installed (pip install wfdb): ECG and EEG fall back to synthetic signals")

    sets = [
        ("ECG (surface)", *load_ecg(args.seconds, args.offline)),
        ("EEG (scalp)", *load_eeg(args.seconds, args.offline, args.chbmit)),
        ("EMG (surface)", *load_emg(args.seconds, args.ninapro, args.ninapro_scale)),
    ]

    fig, axs = plt.subplots(len(sets), 2, figsize=(11, 8), constrained_layout=True)
    rows = []
    for i, (name, x, fs, src) in enumerate(sets):
        (a_lo, a_hi), (f_lo, f_hi), _ = biosig.SIGNALS[name]
        f_hp = max(f_lo, 0.5) if name.startswith("EEG") else f_lo
        y, f, p, a, (b_lo, b_hi) = measure(x, fs, f_hp)
        rows.append((name, src, fs, a["pp"], a["rms"], b_lo, b_hi, a_lo, a_hi, f_lo, f_hi))

        t = np.arange(len(y)) / fs
        show = t < min(5.0, t[-1])
        axs[i, 0].plot(t[show], y[show] * 1e6, lw=0.6)
        axs[i, 0].set(xlabel="time (s)", ylabel="µV", title=f"{name}: {src}")
        axs[i, 1].loglog(f[1:], p[1:] * 1e12, lw=0.8)
        for fb in (b_lo, b_hi):
            axs[i, 1].axvline(fb, color="C3", ls="--", lw=0.8)
        axs[i, 1].set(xlabel="frequency (Hz)", ylabel="µV²/Hz",
                      title=f"Welch PSD, 95 % of power in {b_lo:.2g}–{b_hi:.3g} Hz")
    png = os.path.join(OUT, "lab1_explorer.png")
    fig.savefig(png, dpi=130)

    head = ("| Signal | Source | fs (S/s) | measured p-p | measured RMS | 95 % power band (Hz) "
            "| Table 2.1 amplitude | Table 2.1 band (Hz) |")
    lines = [head, "|" + "---|" * 8]
    for (name, src, fs, pp, rms, b_lo, b_hi, a_lo, a_hi, f_lo, f_hi) in rows:
        lines.append(f"| {name} | {src} | {fs:.0f} | {pp*1e6:.0f} µV | {rms*1e6:.1f} µV "
                     f"| {b_lo:.2g}–{b_hi:.3g} | {a_lo*1e6:.0f}–{a_hi*1e6:.0f} µV | {f_lo:g}–{f_hi:g} |")
    table = "\n".join(lines)
    md = os.path.join(OUT, "lab1_table.md")
    with open(md, "w") as fh:
        fh.write(table + "\n")
    print(table)
    print(f"\nwrote {png}\nwrote {md}")


if __name__ == "__main__":
    main()
