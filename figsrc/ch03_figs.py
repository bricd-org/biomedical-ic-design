"""ch03_figs.py -- Chapter 3 figures: electrode impedance, electrode noise, input loading and the
electrode offset. Electrode models come from labs/python/biosig.py."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

KINDS = [("wet Ag/AgCl", C1), ("dry", C2), ("implanted micro", C3)]
F = np.logspace(-1, 4, 400)


def impedance():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    for k, c in KINDS:
        z = bs.z_electrode(F, k)
        a1.loglog(F, np.abs(z), color=c, label=k)
        a2.semilogx(F, np.degrees(np.angle(z)), color=c)
    for a in (a1, a2):
        a.axvspan(0.5, 1000, color=BGPALE, lw=0, zorder=0)
    a1.text(3, 1.6e3, "ExG band", ha="center", fontsize=7, color=SLATE)
    a1.set_ylim(1e3, 1e10)
    a1.set_yticks([1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10])
    a1.set_yticklabels(["1k", "10k", "100k", "1M", "10M", "100M", "1G", "10G"])
    finish(a1, xlabel="Frequency (Hz)", ylabel="|Z| (Ω)", legend=True, loc="upper right")
    finish(a2, xlabel="Frequency (Hz)", ylabel="Phase (degrees)")
    a2.set_ylim(-90, 0)
    panel(a1, "a"); panel(a2, "b")
    savefig(fig, "ch03_impedance")


def noise():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    f = np.logspace(np.log10(0.5), 4, 300)
    for k, c in KINDS:
        en = np.sqrt(4 * bs.K_B * bs.T_BODY * np.real(bs.z_electrode(f, k)))
        a1.loglog(f, en * 1e9, color=c, label=k)
        cum = [bs.thermal_noise_rms(k, 0.5, fh, n=600) for fh in f[1:]]
        a2.semilogx(f[1:], np.array(cum) * 1e6, color=c)
    a2.axhline(bs.SPEC["noise_eeg_uVrms"], color=AMBER, ls="--", lw=1)
    a2.text(9e3, 1.6, "EEG-mode target\n(whole chain)", fontsize=7, color=AMBERDK, va="bottom", ha="right")
    a2.axvline(100, color=MUTED, lw=0.7, ls=":")
    finish(a1, xlabel="Frequency (Hz)", ylabel="Noise density (nV/√Hz)", legend=True, loc="lower left")
    finish(a2, xlabel="Upper band edge (Hz), lower edge 0.5 Hz", ylabel="Integrated noise (µVrms)")
    a2.set_ylim(0, 4)
    panel(a1, "a"); panel(a2, "b")
    savefig(fig, "ch03_noise")


def loading():
    fig, ax = plt.subplots(figsize=FULL)
    zin = np.logspace(5, 11, 300)
    for (k, c), f in zip(KINDS, (10.0, 10.0, 1000.0)):
        loss = bs.divider_loss(bs.z_electrode(f, k), zin) * 100
        ax.loglog(zin, loss, color=c, label=f"{k} at {f:g} Hz")
    ax.axhline(1, color=MUTED, lw=0.7, ls=":")
    ax.text(1.2e5, 1.15, "1 % loss", fontsize=7, color=MUTED, va="bottom")
    ax.axvline(2.5e6, color=AMBER, lw=1, ls="--")
    ax.text(2.7e6, 30, "2.5 MΩ: minimum in the\nECG standards", fontsize=7, color=AMBERDK, va="center")
    ax.set_ylim(1e-3, 100); ax.set_xlim(1e5, 1e11)
    ax.set_xticks([1e5, 1e6, 1e7, 1e8, 1e9, 1e10, 1e11])
    ax.set_xticklabels(["100k", "1M", "10M", "100M", "1G", "10G", "100G"])
    finish(ax, xlabel="Amplifier input impedance (Ω, resistive)", ylabel="Signal lost to the divider (%)",
           legend=True, loc="lower left")
    savefig(fig, "ch03_loading")


def offset_and_motion():
    fs = 250.0
    t, ecg, _ = bs.ecg(fs=fs, duration=10.0, hr=70)
    rng = np.random.default_rng(11)
    drift = 0.120 + 0.004 * np.sin(2 * np.pi * 0.05 * t) + 0.0015 * np.cumsum(rng.standard_normal(t.size)) / np.sqrt(fs)
    motion = 3e-3 * np.exp(-((t - 6.0) / 0.25) ** 2) * np.sin(2 * np.pi * 1.3 * (t - 6.0)) * 2
    resp = 0.3e-3 * np.sin(2 * np.pi * 0.25 * t)
    v = ecg + drift + motion + resp
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    a1.plot(t, v * 1e3, color=C1, lw=0.8)
    a1.set_ylim(0, 150)
    finish(a1, xlabel="Time (s)", ylabel="Electrode-pair voltage (mV)")
    a1.text(0.3, 130, "≈120 mV offset, ECG invisible\nat this scale", fontsize=7, color=GRAPHITE)
    panel(a1, "a")
    a2.plot(t, (v - 0.120) * 1e3, color=C1, lw=0.8)
    note(a2, (6.0, 5.5), "motion artefact", (7.2, 7.5))
    note(a2, (2.2, 3.6), "baseline wander", (0.3, 8.0), ha="left")
    finish(a2, xlabel="Time (s)", ylabel="After removing 120 mV (mV)")
    panel(a2, "b")
    savefig(fig, "ch03_offset")



def chemistry():
    """(a) Nernst: the Ag/AgCl half-cell potential against chloride activity, at 25 and 37 degC (E0 held at its
    25 degC value). (b) Butler-Volmer: overpotential against current density for a non-polarisable and a
    polarisable electrode (illustrative exchange current densities), with the 6 nA DC lead-off current over 1 cm^2."""
    F, R = 96485.0, 8.314
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    a = np.logspace(-3, 0.5, 100)
    for T, c, lab in ((298.15, C2, "25 °C"), (310.15, C1, "37 °C")):
        a1.semilogx(a, (0.2223 - R * T / F * np.log(a)) * 1e3, color=c, lw=1.6, label=lab)
    a1.annotate("", xy=(0.01, (0.2223 - R * 310.15 / F * np.log(0.01)) * 1e3), xytext=(0.1, (0.2223 - R * 310.15 / F * np.log(0.1)) * 1e3),
                arrowprops=dict(arrowstyle="<->", color=GRAPHITE, lw=0.8))
    a1.text(0.045, 338, "61 mV per decade\nat 37 °C", fontsize=6.6, ha="left")
    finish(a1, xlabel="Chloride activity in the gel", ylabel="Ag/AgCl half-cell potential (mV)", legend=True, loc="upper right")
    panel(a1, "a")
    J = np.logspace(-12, -3, 300)
    T = 310.15
    for i0, c, lab in ((1e-5, C1, "non-polarisable, i$_0$ = 10 µA/cm² (Ag/AgCl-like)"), (1e-9, C2, "polarisable, i$_0$ = 1 nA/cm² (platinum-like)")):
        eta = 2 * R * T / F * np.arcsinh(J / (2 * i0))
        a2.loglog(J * 1e9, eta * 1e3, color=c, lw=1.6, label=lab)
        e6 = 2 * R * T / F * np.arcsinh(6e-9 / (2 * i0)) * 1e3
        a2.plot([6], [e6], "o", color=AMBER, ms=4)
        a2.annotate(f"{e6:.3g} mV" if e6 >= 1 else f"{e6*1e3:.0f} µV", (6, e6), xytext=(9, e6 * 0.35), fontsize=6.6)
    a2.axvline(6, color=AMBERDK, ls=":", lw=0.8)
    a2.text(8, 1.0, "6 nA lead-off\nover 1 cm²", fontsize=6.3, color=AMBERDK)
    a2.text(1.2e-3, 120, "polarisable (platinum-like)\ni$_0$ = 1 nA/cm²", fontsize=6.3, color=C2)
    a2.text(6e5, 2e-4, "non-polarisable (Ag/AgCl-like)\ni$_0$ = 10 µA/cm²", fontsize=6.3, color=C1, ha="right")
    a2.set_ylim(1e-4, 1e3)
    finish(a2, xlabel="Current density (nA/cm²)", ylabel="Overpotential (mV)")
    panel(a2, "b")
    savefig(fig, "ch03_chemistry")


if __name__ == "__main__":
    chemistry()
    impedance()
    noise()
    loading()
    offset_and_motion()
