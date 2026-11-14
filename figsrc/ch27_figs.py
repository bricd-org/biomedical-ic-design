"""ch27_figs.py -- Chapter 27 figure: data rate per mode for raw samples and for on-chip features, and the
radio power these rates cost against the energy per transmitted bit, compared with the analog front-end."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *

CH = 8
MODES = {   # name: (raw bits/s for 8 channels, feature bits/s for 8 channels)
    "ECG": (CH * 500 * 16, CH * 2 * 16 * 1.25 + 16),          # RR intervals (16 b per beat) + rhythm flags
    "EEG": (CH * 256 * 16, CH * 6 * 16 / 2.0),                # six band powers per 2 s window
    "EMG": (CH * 2000 * 12, CH * 4 * 16 * 5),                 # MAV, WL, ZC, SSC at 5 windows/s
    "Spikes (1 ch)": (30000 * 12, 30 * (32 + 16 * 12)),       # 30 spikes/s: time stamp + 16-sample snippet
}
AFE_W = CH * 10e-6


def fig():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    names = list(MODES)
    x = np.arange(len(names))
    raw = np.array([MODES[n][0] for n in names]); feat = np.array([MODES[n][1] for n in names])
    a1.bar(x - 0.2, raw / 1e3, 0.38, color=C4, label="raw samples")
    a1.bar(x + 0.2, feat / 1e3, 0.38, color=C1, label="on-chip features")
    a1.set_yscale("log"); a1.set_xticks(x); a1.set_xticklabels(names, fontsize=7)
    a1.set_ylim(0.01, 1e3)
    finish(a1, ylabel="Data rate (kb/s)", legend=True, loc="upper left")
    panel(a1, "a")
    e = np.logspace(-12, -7, 100)
    for n, c in (("EMG", C4), ("ECG", C2), ("EEG", C3)):
        a2.loglog(e * 1e9, MODES[n][0] * e * 1e6, color=c, label=f"{n}, raw")
        a2.loglog(e * 1e9, MODES[n][1] * e * 1e6, color=c, ls="--", lw=0.9, label=f"{n}, features")
    a2.axhline(AFE_W * 1e6, color=GRAPHITE, lw=1.2)
    a2.text(1.2e-3, AFE_W * 1e6 * 1.3, "analog front-end, 8 × 10 µW", fontsize=6.5, color=GRAPHITE)
    for v, lab in ((5e-9, "BLE-class\n~5 nJ/b"), (50e-12, "backscatter\n~50 pJ/b")):
        a2.axvline(v * 1e9, color=MUTED, ls=":", lw=0.8)
        a2.text(v * 1e9 * 1.15, 3e3, lab, fontsize=6.2, color=MUTED, va="top")
    a2.set_xlim(1e-3, 100); a2.set_ylim(1e-3, 1e4)
    finish(a2, xlabel="Radio energy per bit (nJ)", ylabel="Radio power (µW)", legend=True, loc="lower right")
    a2.legend(loc="lower right", fontsize=5.6, ncol=2)
    panel(a2, "b")
    savefig(fig, "ch27_soc")


if __name__ == "__main__":
    for n, (r, f) in MODES.items():
        print("%-14s raw %8.1f kb/s  features %7.3f kb/s  ratio %6.0f  radio@5nJ raw %7.1f uW feat %6.2f uW" % (n, r / 1e3, f / 1e3, r / f, r * 5e-9 * 1e6, f * 5e-9 * 1e6))
    fig()
