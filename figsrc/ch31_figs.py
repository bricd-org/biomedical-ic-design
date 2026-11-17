"""ch31_figs.py -- Chapter 31 figure: the capstone reference run, real ECG and EEG through the chopped LNA,
the PGA, decimation and a 16-bit quantiser, against the input passed through the designed 2 Hz servo response.
Data: figsrc/data/capstone.npz, copied from labs/spice/out/ after `.venv/bin/python labs/spice/capstone_chain.py`."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
from scipy import signal as sps

HERE = os.path.dirname(os.path.abspath(__file__))


def band(y, fs=500.0):
    return sps.sosfiltfilt(sps.butter(2, [3, 40], "band", fs=fs, output="sos"), y)


def capstone():
    d = np.load(os.path.join(HERE, "data", "capstone.npz"))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    for ax, t, y, r, sc, unit, snr, lab in ((a1, d["te"], d["ye"], d["re"], 1e3, "mV", float(d["snr_e"]), "a"),
                                            (a2, d["tg"], d["yg"], d["rg"], 1e6, "µV", float(d["snr_g"]), "b")):
        k = (t > 0.6) & (t < t[-1] - 0.3)
        ax.plot(t[k], band(r)[k] * sc, color=GRAPHITE, lw=2.2, alpha=0.35, label="input")
        ax.plot(t[k], band(y)[k] * sc, color=C1, lw=0.9, label="output ÷ gain")
        ax.text(0.98, 0.04, f"SNR {snr:.1f} dB", transform=ax.transAxes, ha="right", fontsize=7)
        finish(ax, xlabel="Time (s)", ylabel=f"Input-referred ({unit})", legend=(lab == "a"), loc="upper left")
        panel(ax, lab)
    a1.legend(loc="upper left", bbox_to_anchor=(0.255, 1.0), fontsize=6.3, handlelength=1.3)      # between the first two beats
    savefig(fig, "ch31_capstone")


if __name__ == "__main__":
    capstone()
