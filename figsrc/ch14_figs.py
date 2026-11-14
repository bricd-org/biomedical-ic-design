"""ch14_figs.py -- Chapter 14 figures: spectrum and DNL/INL of a 12-bit SAR with capacitor mismatch,
kT/C capacitor size versus resolution, and energy per sample against the figures of merit.
Models from labs/python/biosig.py."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

N = 12
SIGMA_U, SEED = 0.01, 2          # 1 % unit-capacitor mismatch, the seed used in the text
FS_SAR = 2000.0                  # EMG-mode SAR rate (S/s)


def sar_spectrum_dnl():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    n = 8192
    f, m = bs.coherent_tone(97.0, FS_SAR, n)
    x = 0.99 * np.sin(2 * np.pi * f * np.arange(n) / FS_SAR)
    fr = np.fft.rfftfreq(n, 1 / FS_SAR)
    for w, c, lab, z in ((None, MUTED, "ideal 12-bit", 1), (bs.cdac_weights(N, SIGMA_U, SEED), C4, "1 % unit mismatch", 2)):
        y = bs.code_to_volts(bs.sar_convert(x, N, w), N)
        p = np.abs(np.fft.rfft(y - y.mean())) ** 2
        p = p / p[m]
        met = bs.tone_metrics(y, m)
        a2_lab = f"{lab}: SNDR {met['sndr']:.1f} dB, SFDR {met['sfdr']:.1f} dB"
        a1.plot(fr, 10 * np.log10(p + 1e-30), color=c, lw=0.6, label=a2_lab, zorder=z)
    a1.set_xlim(0, FS_SAR / 2); a1.set_ylim(-140, 5)
    finish(a1, xlabel="Frequency (Hz)", ylabel="Spectrum (dBc)", legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=6.3)
    panel(a1, "a")
    w = bs.cdac_weights(N, SIGMA_U, SEED)
    r = np.linspace(-1, 1, 2 ** N * 64, endpoint=False) + 1.0 / 2 ** N / 64
    dnl, inl = bs.dnl_inl(bs.sar_convert(r, N, w), N)
    k = np.arange(1, 2 ** N - 1)
    a2.plot(k, dnl, color=C1, lw=0.5, label="DNL")
    a2.plot(k, inl, color=C4, lw=1.2, label="INL (end-point fit)")
    a2.axhline(-1, color=AMBER, ls="--", lw=0.8)
    a2.text(60, -1.12, "−1 LSB: a missing code", fontsize=6.5, color=AMBERDK, va="top")
    a2.set_xlim(0, 2 ** N); a2.set_ylim(-1.6, 1.8)
    a2.set_xticks([0, 1024, 2048, 3072, 4096])
    finish(a2, xlabel="Output code", ylabel="Error (LSB)", legend=True, loc="upper right")
    panel(a2, "b")
    savefig(fig, "ch14_sar")


def power_per_bit():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    nb = np.arange(8, 19)
    for osr, c, lab in ((1, C4, "Nyquist (OSR 1)"), (16, C2, "OSR 16"), (128, C1, "OSR 128")):
        a1.semilogy(nb, bs.ktc_cap(nb, osr=osr) * 1e12, color=c, marker="o", ms=2.8, label=lab)
    a1.plot(12, bs.ktc_cap(12) * 1e12, "s", color=GRAPHITE, ms=4.5, zorder=5)
    note(a1, (12, bs.ktc_cap(12) * 1e12), "12 b: 0.58 pF", (8.6, 5.0), fs=7)
    note(a1, (16, bs.ktc_cap(16) * 1e12), "16 b: 150 pF", (12.6, 2.5e3), fs=7)
    note(a1, (16, bs.ktc_cap(16, osr=128) * 1e12), "16 b at OSR 128: 1.2 pF", (16.4, 0.02), fs=7, ha="center")
    a1.set_ylim(5e-3, 5e4)
    finish(a1, xlabel="Resolution N (bits)", ylabel="kT/C-limited capacitor (pF)",
           legend=True, loc="upper left")
    panel(a1, "a")
    s = np.linspace(40, 115, 300)
    a2.semilogy(s, bs.e_thermal_min(s), color=GRAPHITE, lw=1.6, label="thermal bound 8kT·SNR")
    for fom, c in ((185, C3), (175, C1)):
        a2.semilogy(s, 0.5 * 10 ** ((s - fom) / 10), color=c, ls="--", lw=1, label=f"Schreier FoM {fom} dB")
    for fw, c in ((1e-15, C5), (10e-15, C2)):
        a2.semilogy(s, fw * 2 ** bs.enob(s), color=c, ls=":", lw=1.3, label=f"Walden FoM {fw*1e15:g} fJ/step")
    e_sar = 10e-15 * 2 ** 11
    e_ds = 0.5 * 10 ** ((98 - 175) / 10)
    a2.plot(68.0, e_sar, "o", color=C4, ms=5, zorder=5)
    a2.plot(98.0, e_ds, "s", color=C4, ms=5, zorder=5)
    a2.text(66, e_sar * 3.5, "SAR\n12 b", fontsize=6.5, color=C4, ha="right")
    a2.text(96, e_ds * 3, "ΔΣ 16 b", fontsize=6.5, color=C4, ha="right")
    a2.set_xlim(40, 115); a2.set_ylim(1e-15, 1e-5)
    finish(a2, xlabel="SNDR (dB)", ylabel="Energy per Nyquist sample (J)", legend=True, loc="upper left")
    a2.legend(loc="upper left", fontsize=6.2)
    panel(a2, "b")
    savefig(fig, "ch14_power")


def arch_map():
    """Where each converter architecture sits in resolution and sample rate (qualitative regions, as in
    published surveys), with the Open-BioAFE signals marked. Regions are drawn as rotated ellipses in
    (log10 fs, bits)."""
    from matplotlib.patches import Ellipse
    fig, ax = plt.subplots(figsize=(6.3, 3.3))
    regions = [  # (centre log10 fs, centre bits, width in decades, height in bits, angle, colour, label, label xy)
        (3.6, 18.5, 5.4, 6.0, -12, C1, "ΔΣ (oversampled)", (2.2, 22.3)),
        (5.0, 11.5, 6.4, 5.0, -18, C3, "SAR", (6.3, 13.9)),
        (8.0, 11.0, 2.8, 4.0, -20, C5, "pipelined", (8.6, 13.6)),
        (9.4, 6.0, 2.2, 3.2, -10, C4, "flash", (9.6, 3.9)),
        (6.5, 9.5, 3.0, 3.6, -15, C2, "VCO / time-domain", (6.6, 6.6)),
    ]
    for cx, cy, w, h, ang, c, lab, (lx, ly) in regions:
        ax.add_patch(Ellipse((cx, cy), w, h, angle=ang, facecolor=c, alpha=0.16, edgecolor=c, lw=1.2))
        ax.text(lx, ly, lab, color=c, fontsize=7.5, ha="center", fontweight="bold")
    signals = [  # (fs, bits, label, ha)
        (500, 16, "ECG, EEG\n500 S/s, 16 b", "right"),
        (2000, 12, "EMG\n2 kS/s, 12 b", "left"),
        (30000, 10, "spikes\n30 kS/s, 10 b", "left"),
        (20, 13, "bioimpedance IQ\ntens of S/s", "left"),
    ]
    for f, b, lab, ha in signals:
        ax.plot(np.log10(f), b, "s", color=GRAPHITE, ms=5, zorder=5)
        dx = -0.15 if ha == "right" else 0.15
        ax.text(np.log10(f) + dx, b, lab, fontsize=6.8, ha=ha, va="center", color=GRAPHITE)
    ax.axvspan(0.5, 4.7, color=AMBERLT, alpha=0.12, zorder=0)
    ax.text(2.6, 25.0, "biosignals", fontsize=7, color=AMBERDK, ha="center")
    ax.set_xlim(0.5, 10.5); ax.set_ylim(2, 26)
    ax.set_xticks(range(1, 11)); ax.set_xticklabels(["10", "100", "1k", "10k", "100k", "1M", "10M", "100M", "1G", "10G"])
    finish(ax, xlabel="Sample rate (S/s)", ylabel="Resolution (bits)")
    savefig(fig, "ch14_archmap")


if __name__ == "__main__":
    sar_spectrum_dnl()
    power_per_bit()
    arch_map()
