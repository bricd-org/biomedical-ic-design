"""ch33_figs.py -- Chapter 33 figure: (a) the phase error that a loop latency causes for three brain rhythms,
against a +-30 degree tolerance; (b) the number of averaged epochs an auditory steady-state response needs at
ear-EEG noise levels."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *

RHYTHMS = [("slow oscillation, 0.75 Hz", 0.75, C3), ("theta, 6 Hz", 6.0, C2), ("alpha, 10 Hz", 10.0, C1)]


def fig():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    tau = np.linspace(0, 150, 300)
    for lab, f0, c in RHYTHMS:
        a1.plot(tau, 360 * f0 * tau * 1e-3, color=c, lw=1.5, label=lab)
    a1.axhspan(0, 30, color=AMBER, alpha=0.15)
    a1.text(24, 21, "±30° tolerance", fontsize=6.3, ha="left", color=AMBERDK)
    for t0, lab in ((5, "on device"), (60, "over BLE")):
        a1.axvline(t0, color=GRAPHITE, ls=":", lw=0.8)
        a1.text(t0 + 2, 160, lab, fontsize=6.3, color=GRAPHITE)
    a1.set_ylim(0, 180); a1.set_xlim(0, 150)
    finish(a1, xlabel="Loop latency (ms)", ylabel="Phase error (degrees)", legend=True, loc="upper left")
    a1.legend(loc="upper right", fontsize=6.0, bbox_to_anchor=(1.0, 0.80))
    panel(a1, "a")
    # ASSR: response amplitude A in one FFT bin against noise per bin sigma/sqrt(N)
    n = np.logspace(0, 3.5, 200)
    nd = 0.75e-6 / np.sqrt(39.0)                      # dry ear-EEG noise density, uV/rtHz over 1-40 Hz (Ch 32)
    for amp, c in ((0.3e-6, C1), (0.1e-6, C2), (0.05e-6, C3)):
        snr = 20 * np.log10(amp / (nd * 1.0 / np.sqrt(n)))   # 1 s epochs: 1 Hz bins
        a2.semilogx(n, snr, color=c, lw=1.5, label=f"{amp*1e6:.2f} µV response")
    a2.axhline(10, color=AMBERDK, ls="--", lw=0.9)
    a2.text(1.2, 11, "10 dB: a confident detection", fontsize=6.3, color=AMBERDK)
    finish(a2, xlabel="Averaged 1 s epochs", ylabel="SNR in the response bin (dB)", legend=True, loc="lower right")
    a2.legend(loc="lower right", fontsize=6.0)
    panel(a2, "b")
    savefig(fig, "ch33_loop")
    need = {a: float(np.ceil((10 ** (10 / 20) * nd / a) ** 2)) for a in (0.3e-6, 0.1e-6, 0.05e-6)}
    return need


if __name__ == "__main__":
    print(fig())
