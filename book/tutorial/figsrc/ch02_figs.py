"""ch02_figs.py -- Chapter 2 figures: action potential, ECG, EEG, EMG and spikes, and the master
amplitude-versus-bandwidth map. All signals come from labs/python/biosig.py."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "labs", "python"))
from bricdstyle import *
from matplotlib.patches import Rectangle
import biosig as bs


def action_potential():
    t, v = bs.hodgkin_huxley(t_end=12e-3)
    fig, ax = plt.subplots(figsize=FULL)
    ax.plot(t * 1e3, v * 1e3, color=C1)
    ax.axvspan(2, 3, color=GTINT, lw=0)
    ax.text(2.5, 45, "stimulus", ha="center", fontsize=7, color=GOLDDK)
    k = np.argmax(v)
    note(ax, (t[k] * 1e3, v[k] * 1e3), f"peak {v[k]*1e3:+.0f} mV", (t[k] * 1e3 + 1.6, 30))
    note(ax, (3.3, -20), "depolarisation\n(Na$^+$ in)", (0.4, 10), ha="left")
    note(ax, (4.6, -20), "repolarisation\n(K$^+$ out)", (6.2, 10))
    kmin = np.argmin(v[t > 4e-3]) + np.sum(t <= 4e-3)
    note(ax, (t[kmin] * 1e3, v[kmin] * 1e3), "after-hyperpolarisation", (8.0, -55))
    ax.axhline(-65, color=MUTED, lw=0.7, ls=":")
    ax.text(11.8, -63, "rest −65 mV", ha="right", fontsize=7, color=MUTED)
    ax.set_ylim(-85, 55)
    finish(ax, xlabel="Time (ms)", ylabel="Membrane potential (mV)")
    savefig(fig, "ch02_ap")


def ecg_figure():
    t, x, peaks = bs.ecg(fs=1000, duration=4.0, hr=72, hrv=0.03)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2, gridspec_kw=dict(width_ratios=[1.6, 1]))
    a1.plot(t, x * 1e3, color=C1, lw=1.1)
    finish(a1, xlabel="Time (s)", ylabel="Amplitude (mV)")
    panel(a1, "a")
    # one beat, annotated
    r = peaks[1]
    m = (t > r - 0.35) & (t < r + 0.5)
    tb = (t[m] - r) * 1e3
    a2.plot(tb, x[m] * 1e3, color=C1, lw=1.3)
    for name, (amp, mu, sig) in bs.ECG_WAVES.items():
        if name in ("Q", "S"):
            continue
        tt = mu * 1e3 * np.sqrt(60 / 72)
        y = np.interp(tt, tb, x[m] * 1e3)
        a2.text(tt, y + 0.08, "QRS" if name == "R" else name, ha="center", va="bottom", fontsize=7.5,
                color=GOLDDK, fontweight="bold")
    a2.annotate("", xy=(-30, -0.45), xytext=(30, -0.45), arrowprops=dict(arrowstyle="<->", lw=0.7, color=NAVY))
    a2.text(0, -0.5, "QRS ≈ 80 ms", ha="center", va="top", fontsize=7, color=NAVY)
    a2.set_ylim(-0.75, 1.3)
    finish(a2, xlabel="Time from R peak (ms)", ylabel="mV")
    panel(a2, "b")
    savefig(fig, "ch02_ecg")


def eeg_figure():
    fs = 256.0
    t, x = bs.eeg(fs=fs, duration=120.0)
    f, p = bs.psd(x, fs, seg_s=4.0)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    m = t < 4
    a1.plot(t[m], x[m] * 1e6, color=C1, lw=0.8)
    finish(a1, xlabel="Time (s)", ylabel="Amplitude (µV)")
    panel(a1, "a")
    cols = [BTINT, GTINT, "#DCEFE9", "#F3DEDA", "#E6E2F2"]
    for (name, (lo, hi)), c in zip(bs.EEG_BANDS.items(), cols):
        a2.axvspan(lo, hi, color=c, lw=0)
        a2.text(np.sqrt(lo * hi), 3e-10 if name != "gamma" else 3e-10, {"delta": "δ", "theta": "θ", "alpha": "α",
                "beta": "β", "gamma": "γ"}[name], ha="center", fontsize=9, color=NAVY)
    a2.loglog(f[1:], p[1:] * 1e12, color=C1, lw=1.1)
    a2.set_xlim(0.5, 100); a2.set_ylim(1e-3 * 1e0, 1e3)
    finish(a2, xlabel="Frequency (Hz)", ylabel="PSD (µV²/Hz)")
    for txt in a2.texts:
        txt.set_y(400)
    panel(a2, "b")
    savefig(fig, "ch02_eeg")


def emg_spike_figure():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    fs = 2000.0
    t, x = bs.emg(fs=fs, duration=4.0, peak=1e-3)
    w = int(0.1 * fs)
    env = np.sqrt(np.convolve(x ** 2, np.ones(w) / w, mode="same"))
    a1.plot(t, x * 1e3, color=C1, lw=0.5)
    a1.plot(t, env * 1e3, color=C2, lw=1.4, label="100 ms RMS envelope")
    finish(a1, xlabel="Time (s)", ylabel="Amplitude (mV)", legend=True, loc="lower right")
    panel(a1, "a")
    t2, s, times = bs.spikes(duration=0.5, rate=25, seed=7)
    m = (t2 > 0.10) & (t2 < 0.25)
    a2.plot((t2[m] - 0.10) * 1e3, s[m] * 1e6, color=C1, lw=0.6)
    finish(a2, xlabel="Time (ms)", ylabel="Amplitude (µV)")
    panel(a2, "b")
    savefig(fig, "ch02_emg_spikes")


def amplitude_bandwidth_map():
    fig, ax = plt.subplots(figsize=FULLTALL)
    cols = [C1, C3, C2, C5, NAVY, BROWN, C4]
    offs = {"ECG (surface)": (1.0, 1.25), "EEG (scalp)": (1.0, 1.35), "EMG (surface)": (1.2, 1.25),
            "EOG": (0.9, 0.62), "ECoG": (1.3, 1.25), "LFP (intracortical)": (0.9, 1.3),
            "Spikes (extracellular)": (1.1, 1.25)}
    for (name, ((a_lo, a_hi), (f_lo, f_hi), fs)), c in zip(bs.SIGNALS.items(), cols):
        ax.add_patch(Rectangle((f_lo, a_lo), f_hi - f_lo, a_hi - a_lo, facecolor=c, alpha=0.13,
                               edgecolor=c, lw=1.2))
        fx, fy = offs[name]
        ax.text(f_lo * fx, a_hi * fy, name, fontsize=7.2, color=c, fontweight="bold", va="bottom")
    # electrode offset and the noise target
    ax.add_patch(Rectangle((0.01, 0.1), 0.04, 0.2, facecolor=MUTED, alpha=0.2, edgecolor=MUTED, lw=1))
    ax.text(0.012, 0.42, "electrode DC offset\nup to ±300 mV", fontsize=7, color=SLATE, va="bottom")
    ax.axhline(bs.SPEC["noise_eeg_uVrms"] * 1e-6, color=GOLD, lw=1.0, ls="--")
    ax.text(0.012, 1.7e-6, "Open-BioAFE EEG-mode noise target 1.5 µVrms", fontsize=7, color=GOLDDK, va="bottom")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(0.01, 2e4); ax.set_ylim(5e-7, 2)
    ax.set_yticks([1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1])
    ax.set_yticklabels(["1 µV", "10 µV", "100 µV", "1 mV", "10 mV", "100 mV", "1 V"])
    ax.set_xticks([0.01, 0.1, 1, 10, 100, 1e3, 1e4])
    ax.set_xticklabels(["0.01", "0.1", "1", "10", "100", "1k", "10k"])
    finish(ax, xlabel="Frequency (Hz)", ylabel="Signal amplitude")
    savefig(fig, "ch02_map")


if __name__ == "__main__":
    action_potential()
    ecg_figure()
    eeg_figure()
    emg_spike_figure()
    amplitude_bandwidth_map()
