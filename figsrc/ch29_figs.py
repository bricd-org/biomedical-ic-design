"""ch29_figs.py -- Chapter 29 figure: the EEG-mode noise budget of one Open-BioAFE channel with wet and dry
electrodes, and the power per channel by block in ECG/EEG and EMG modes. Numbers from Chapters 3-27."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *

NOISE = [  # (source, wet uVrms, dry uVrms), input-referred over 0.5-100 Hz
    ("electrodes (Ch 3)", 0.34, 1.20),
    ("chopped LNA incl. servo (Ch 10)", 0.36, 0.36),
    ("input resistors 2 × 5 kΩ (Ch 12)", 0.13, 0.13),
    ("filter kT/C after gain (Ch 11)", 0.05, 0.05),
    ("PGA (Ch 11)", 0.02, 0.02),
    ("ΔΣ ADC, 16 b (Ch 20)", 0.006, 0.006),
]
POWER = [  # (block, uW in ECG/EEG mode, uW in EMG mode)
    ("LNA OTA, 2 µA (Ch 6–8)", 2.4, 2.4),
    ("ΔΣ ADC (Ch 20)", 1.9, 0.0),
    ("PGA (Ch 11)", 0.6, 0.6),
    ("shared: RLD, bias, LDOs (÷8)", 0.6, 0.6),
    ("DC servo, 3.3 V (Ch 10)", 0.33, 0.33),
    ("choppers and ripple loop (Ch 9)", 0.3, 0.3),
    ("impedance boosting (Ch 10)", 0.3, 0.3),
    ("features and decimation (Ch 27)", 0.3, 0.3),
    ("Gm-C filter (Ch 11)", 0.05, 0.05),
    ("SAR share (Ch 18)", 0.0, 0.023),
]


def totals():
    wet = np.sqrt(sum(w ** 2 for _, w, _ in NOISE)); dry = np.sqrt(sum(d ** 2 for _, _, d in NOISE))
    pe = sum(p for _, p, _ in POWER); pm = sum(p for _, _, p in POWER)
    return wet, dry, pe, pm


def fig():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    cols = [C4, C1, C2, C5, C3, GRAPHITE]
    for j, (lab_e, idx) in enumerate((("wet", 1), ("dry", 2))):
        left = 0.0
        for k, row in enumerate(NOISE):
            p = row[idx] ** 2
            a1.barh([j], [p], left=left, color=cols[k], height=0.5, label=row[0] if j == 0 else None)
            left += p
        a1.text(left + 0.03, j, f"{np.sqrt(left):.2f} µVrms", va="center", fontsize=7)
    a1.axvline(1.5 ** 2, color=AMBER, ls="--", lw=0.9)
    a1.text(1.5 ** 2 + 0.03, 0.55, "1.5 µVrms\ntarget", fontsize=6.5, color=AMBERDK)
    a1.set_yticks([0, 1]); a1.set_yticklabels(["wet", "dry"])
    a1.set_xlim(0, 3.0); a1.set_ylim(-0.5, 2.6)
    finish(a1, xlabel="Noise power, 0.5–100 Hz (µV²)", legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=5.4)
    panel(a1, "a")
    cols2 = [C1, C4, C2, GRAPHITE, C3, C5, AMBER, MUTED, PALE, BROWN]
    for j, idx in enumerate((1, 2)):
        left = 0.0
        for k, row in enumerate(POWER):
            a2.barh([j], [row[idx]], left=left, color=cols2[k], height=0.5, label=row[0] if j == 0 else None)
            left += row[idx]
        a2.text(left + 0.1, j, f"{left:.1f} µW", va="center", fontsize=7)
    a2.axvline(10, color=AMBER, ls="--", lw=0.9)
    a2.text(9.9, 1.45, "10 µW", fontsize=6.5, color=AMBERDK, ha="right")
    a2.set_yticks([0, 1]); a2.set_yticklabels(["ECG/EEG", "EMG"])
    a2.set_xlim(0, 12); a2.set_ylim(-0.5, 3.2)
    finish(a2, xlabel="Power per channel (µW)", legend=True, loc="upper right")
    a2.legend(loc="upper right", fontsize=5.0, ncol=2)
    panel(a2, "b")
    savefig(fig, "ch29_budgets")


# Gain plan (Table 11.1) and converters (Chapters 13-20): largest signal (V peak at the electrodes),
# LNA and PGA gain, converter bits; the converters' full scale is 0.5 V peak (+-0.5 V differential).
MODES = [("ECG", 4e-3, 100, 1, 16, C1), ("EEG", 300e-6, 100, 8, 16, C3), ("EMG", 5e-3, 10, 8, 12, C4)]
VFS = 0.5


def level_diagram():
    """Signal peak and noise at every node of the chain, in dBV, for the three modes; the EEG noise
    accumulates the input-referred contributions of the NOISE table (wet electrodes)."""
    nodes = ["electrodes", "LNA out", "PGA out", "filter out", "converter"]
    x = np.arange(len(nodes))
    db = lambda v: 20 * np.log10(v)
    fig, ax = plt.subplots(figsize=(6.3, 3.4))
    for name, vpk, g1, g2, nb, c in MODES:
        sig = [vpk, vpk * g1, vpk * g1 * g2, vpk * g1 * g2, vpk * g1 * g2]
        ax.plot(x, db(np.array(sig)), "o-", color=c, lw=1.4, ms=3.5, label=f"{name}: largest signal (peak)")
        lsb = 2 * VFS / 2 ** nb
        ax.plot([x[-1] - 0.25, x[-1] + 0.25], [db(lsb / np.sqrt(12))] * 2, color=c, lw=2.2)
    # EEG noise: electrode + LNA + input resistors at the input, then PGA and filter added after gain
    nz = dict((k.split(" (")[0], w) for k, w, _ in NOISE)
    g1, g2 = 100, 8
    n_in = np.sqrt(0.34 ** 2 + 0.36 ** 2 + 0.13 ** 2) * 1e-6
    n_lna = n_in * g1
    n_pga = np.sqrt(n_in ** 2 + (0.02e-6) ** 2) * g1 * g2
    n_flt = np.sqrt(n_in ** 2 + (0.02e-6) ** 2 + (0.05e-6) ** 2) * g1 * g2
    noise = [n_in, n_lna, n_pga, n_flt, n_flt]
    ax.plot(x, db(np.array(noise)), "s--", color=C3, lw=1.1, ms=3, label="EEG: noise, 0.5–100 Hz, wet electrodes (rms)")
    ax.axhline(db(VFS), color=AMBER, ls="--", lw=0.9)
    ax.text(0.05, db(VFS) + 2, "converter full scale, 0.5 V peak (ECG and EMG both reach 0.4 V)", fontsize=6.8, color=AMBERDK)
    ax.text(x[-1] + 0.3, db(2 * VFS / 2 ** 16 / np.sqrt(12)), "16-b ΔΣ\nquantisation", fontsize=6.3, va="center", color=C3)
    ax.text(x[-1] + 0.3, db(2 * VFS / 2 ** 12 / np.sqrt(12)), "12-b SAR\nquantisation", fontsize=6.3, va="center", color=C4)
    # annotate the EEG margins at the converter
    s_eeg = 300e-6 * 800
    ax.annotate("", xy=(x[-1] - 0.05, db(VFS)), xytext=(x[-1] - 0.05, db(s_eeg)),
                arrowprops=dict(arrowstyle="<->", color=GRAPHITE, lw=0.8))
    ax.text(x[-1] - 0.12, db(VFS) + 2.5, f"EEG: {db(VFS) - db(s_eeg):.0f} dB headroom", fontsize=6.3, ha="right", va="bottom")
    ax.annotate("", xy=(x[-1] - 0.05, db(n_flt)), xytext=(x[-1] - 0.05, db(2 * VFS / 2 ** 16 / np.sqrt(12))),
                arrowprops=dict(arrowstyle="<->", color=GRAPHITE, lw=0.8))
    ax.text(x[-1] - 0.12, db(2 * VFS / 2 ** 16 / np.sqrt(12)) + 12,
            f"{db(n_flt) - db(2 * VFS / 2 ** 16 / np.sqrt(12)):.0f} dB:\nquantisation\nnegligible", fontsize=6.3, ha="right", va="center")
    ax.set_xticks(x); ax.set_xticklabels(nodes)
    ax.set_xlim(-0.3, len(nodes) - 0.1); ax.set_ylim(-140, 10)
    finish(ax, ylabel="Level (dBV)", legend=True, loc="lower right")
    ax.legend(loc="lower center", fontsize=6.2, bbox_to_anchor=(0.52, 0.02))
    savefig(fig, "ch29_levels")
    return dict(headroom=db(VFS) - db(s_eeg), q_margin=db(n_flt) - db(2 * VFS / 2 ** 16 / np.sqrt(12)),
                n_conv=n_flt, q16=2 * VFS / 2 ** 16 / np.sqrt(12), q12=2 * VFS / 2 ** 12 / np.sqrt(12))


if __name__ == "__main__":
    print("wet %.2f dry %.2f uVrms; power ECG/EEG %.2f EMG %.2f uW" % totals())
    fig()
    print(level_diagram())
