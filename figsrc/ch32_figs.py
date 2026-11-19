"""ch32_figs.py -- Chapter 32 figure: (a) the noise budget of an ear-EEG channel, wet and dry contacts, over the
full EEG band and over 1-40 Hz, scaled from the Chapter 29 budget; (b) the empirical ratio-of-ratios calibration
of pulse oximetry."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *

# input-referred rms over 0.5-100 Hz (Chapter 29), white over the band, so they scale with sqrt(bandwidth)
SRC = [("electrodes", 0.34, 1.20), ("chopped LNA", 0.36, 0.36), ("input resistors", 0.13, 0.13), ("filter, PGA, ADC", 0.054, 0.054)]
BW_FULL, BW_EAR = 99.5, 39.0


def budget():
    rows = {}
    for lab, bw in (("full", BW_FULL), ("ear", BW_EAR)):
        k = np.sqrt(bw / BW_FULL)
        for el, i in (("wet", 1), ("dry", 2)):
            parts = [(s[0], (s[i] * k) ** 2) for s in SRC]
            rows[(el, lab)] = parts
    return rows


def fig():
    rows = budget()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2, gridspec_kw={"width_ratios": [1.5, 1]})
    order = [("wet", "full"), ("wet", "ear"), ("dry", "full"), ("dry", "ear")]
    labels = ["wet\n0.5–100 Hz", "wet\n1–40 Hz", "dry\n0.5–100 Hz", "dry\n1–40 Hz"]
    cols = [C3, C1, C2, GRAPHITE]
    totals = []
    for j, key in enumerate(order):
        b = 0
        for c, (name, v) in zip(cols, rows[key]):
            a1.bar(j, v, bottom=b, color=c, width=0.6, label=name if j == 0 else None)
            b += v
        totals.append(np.sqrt(b))
        a1.text(j, b + 0.04, f"{np.sqrt(b):.2f} µV", ha="center", fontsize=6.6)
    a1.axhline(0.5 ** 2, color=AMBERDK, ls="--", lw=0.9)
    a1.text(1.5, 0.5 ** 2 + 0.03, "0.5 µVrms", color=AMBERDK, fontsize=6.3, ha="center")
    a1.set_xticks(range(4)); a1.set_xticklabels(labels, fontsize=6.6)
    finish(a1, ylabel="Noise power (µV²)", legend=True, loc="upper left")
    a1.legend(loc="upper left", fontsize=6.0)
    panel(a1, "a")
    r = np.linspace(0.3, 1.6, 50)
    a2.plot(r, np.clip(110 - 25 * r, 0, 100), color=C1, lw=1.6)
    for rr in (0.5, 1.0):
        a2.plot([rr], [110 - 25 * rr], "o", color=AMBER, ms=4)
        a2.annotate(f"R = {rr:g}: {110 - 25 * rr:.1f} %", (rr, 110 - 25 * rr), xytext=(rr + 0.08, 110 - 25 * rr + 2), fontsize=6.6)
    finish(a2, xlabel="Ratio of ratios R", ylabel="SpO$_2$ (%)")
    a2.set_ylim(65, 102)
    panel(a2, "b")
    savefig(fig, "ch32_ear")
    return [round(t, 2) for t in totals]


if __name__ == "__main__":
    print(fig())
