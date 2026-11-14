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
    ("SAR share (Ch 18)", 0.0, 0.015),
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


if __name__ == "__main__":
    print("wet %.2f dry %.2f uVrms; power ECG/EEG %.2f EMG %.2f uW" % totals())
    fig()
