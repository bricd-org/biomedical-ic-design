"""ch04_figs.py -- Chapter 4 figures: common-mode to differential conversion, effective CMRR,
mains interference on EEG, and patient-current limits. Models from labs/python/biosig.py."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

F_MAINS = 50.0
VCM_GND = bs.body_cm_voltage(z_ground=bs.z_electrode(F_MAINS, "wet Ag/AgCl"))   # ~9 mV rms


def cm_to_dm():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    dz = np.logspace(2, 6.3, 200)
    for zcm, c in zip((10e6, 100e6, 1e9, 10e9), (C4, C2, C1, C3)):
        vdm = [bs.cm_to_dm(VCM_GND, d, 0.0, zcm) for d in dz]
        lab = f"{zcm/1e9:g} GΩ" if zcm >= 1e9 else f"{zcm/1e6:g} MΩ"
        a1.loglog(dz / 1e3, np.array(vdm) * 1e6, color=c, label=r"$Z_\mathrm{cm}$ = " + lab)
    a1.axhline(bs.SPEC["noise_eeg_uVrms"], color=GOLD, ls="--", lw=1)
    a1.text(0.12, 1.75, "1.5 µV", fontsize=7, color=GOLDDK, va="bottom")
    a1.axvline(40.7, color=MUTED, lw=0.7, ls=":")
    a1.text(45, 2e-3, "51 kΩ‖47 nF\nat 50 Hz", fontsize=6.5, color=MUTED)
    a1.set_ylim(1e-3, 1e3)
    finish(a1, xlabel="Electrode impedance imbalance |ΔZ| (kΩ)",
           ylabel="Mains on the signal (µVrms)", legend=True, loc="upper left")
    panel(a1, "a")
    # effective CMRR: intrinsic CMRR combined with the imbalance term dZ/Zcm
    zcm = np.logspace(7, 11, 200)
    dzt = 40.7e3
    for cmrr_db, c in zip((80, 100, 120), (C2, C1, C3)):
        inv = 10 ** (-cmrr_db / 20) + dzt / zcm
        a2.semilogx(zcm, -20 * np.log10(inv), color=c, label=f"amplifier CMRR {cmrr_db} dB")
    a2.axhline(89.0, color=GOLD, ls="--", lw=1)
    a2.text(1.2e7, 90.2, "89 dB (ECG CMRR test)", fontsize=7, color=GOLDDK, va="bottom")
    a2.set_ylim(40, 125)
    a2.set_xticks([1e7, 1e8, 1e9, 1e10, 1e11]); a2.set_xticklabels(["10M", "100M", "1G", "10G", "100G"])
    finish(a2, xlabel=r"Common-mode input impedance $Z_\mathrm{cm}$ (Ω)", ylabel="Effective CMRR (dB)",
           legend=True, loc="lower right")
    panel(a2, "b")
    savefig(fig, "ch04_cmdm")


def mains_on_eeg():
    fs = 1000.0
    t, eeg = bs.eeg(fs=fs, duration=2.0, seed=5)
    dz = bs.z_electrode(F_MAINS, "wet Ag/AgCl") - bs.ELECTRODES["wet Ag/AgCl"]["Rs"]
    fig, axs = plt.subplots(1, 2, figsize=FULL2, sharey=True)
    for a, zcm, letter in zip(axs, (10e6, 1e9), "ab"):
        vdm = bs.cm_to_dm(VCM_GND, dz, 0.0, zcm)
        x = eeg + np.sqrt(2) * vdm * np.sin(2 * np.pi * F_MAINS * t)
        a.plot(t, x * 1e6, color=C1, lw=0.6)
        lab = f"{zcm/1e9:g} GΩ" if zcm >= 1e9 else f"{zcm/1e6:g} MΩ"
        a.set_title(r"$Z_\mathrm{cm}$ = " + lab + f": {vdm*1e6:.2g} µVrms of mains", fontsize=8)
        finish(a, xlabel="Time (s)", ylabel="EEG + interference (µV)" if letter == "a" else None)
        panel(a, letter)
    savefig(fig, "ch04_mains_eeg")


def current_limits():
    f = np.logspace(0, 6, 300)
    fig, ax = plt.subplots(figsize=FULL)
    for part, c in (("BF", C1), ("CF", C4)):
        ax.loglog(f, bs.patient_current_limit(f, part) * 1e6, color=c, label=f"type {part}, normal condition")
        ax.loglog(f, bs.patient_current_limit(f, part, single_fault=True) * 1e6, color=c, ls="--", lw=1,
                  label=f"type {part}, single fault")
    ax.plot(50e3, 50, "o", color=NAVY, ms=4.5)
    ax.annotate("example bioimpedance\nexcitation: 50 µA at 50 kHz", xy=(50e3, 50), xytext=(1.2e3, 2.2e3),
                fontsize=7, color=NAVY, arrowprops=dict(arrowstyle="-|>", lw=0.7, color=NAVY, mutation_scale=7))
    ax.axhline(bs.PATIENT_LIMIT_DC * 1e6, xmax=0.06, color=MUTED, lw=2.5)
    ax.text(1.3, 7, "d.c. limit 10 µA", fontsize=7, color=MUTED, va="top")
    ax.set_xlim(1, 1e6); ax.set_ylim(1, 2e4)
    ax.set_xticks([1, 10, 100, 1e3, 1e4, 1e5, 1e6]); ax.set_xticklabels(["1", "10", "100", "1k", "10k", "100k", "1M"])
    finish(ax, xlabel="Frequency (Hz)", ylabel="Allowed patient current (µA rms)", legend=True, loc="upper left")
    savefig(fig, "ch04_limits")


if __name__ == "__main__":
    cm_to_dm()
    mains_on_eeg()
    current_limits()
