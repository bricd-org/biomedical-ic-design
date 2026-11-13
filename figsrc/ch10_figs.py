"""ch10_figs.py -- Chapter 10 figures: input impedance of the chopped CCIA with positive-feedback
boosting and pad parasitics, and the DC-servo-loop capacitor and noise penalty versus offset range."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

CIN, CFB, CP_GATE = 20e-12, 200e-15, 2.16e-12      # Chapters 7-8 (1000 um2 input device)
FCH = 4e3


def z_boost(f, eps, c_pad):
    """Differential input impedance: chopped CCIA 1/(2 fch Cin), boosted by 1/eps (eps = residual
    mismatch of the positive-feedback loop), in parallel with the pads' capacitance to ground (two pads)."""
    zb = 1 / (2 * FCH * CIN) / eps
    yp = 1j * 2 * np.pi * f * c_pad / 2
    return np.abs(1 / (1 / zb + yp))


def fig_zin():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    f = np.logspace(0, 4, 300)
    a1.loglog(f, 2 / (2 * np.pi * f * CIN) / 1e6, color=MUTED, ls=":", label=r"unchopped CCIA, $2/(\omega C_\mathrm{in})$")
    for eps, c, lab in ((1.0, C4, "chopped, no boosting"), (0.1, C2, "boosted, 10 % residual"),
                        (0.03, C1, "boosted, 3 % residual")):
        a1.loglog(f, z_boost(f, eps, 5e-12) / 1e6, color=c, label=lab + ", 5 pF pads")
    a1.loglog(f, z_boost(f, 0.03, 1e-12) / 1e6, color=C1, ls="--", lw=0.9, label="boosted, 3 %, 1 pF pads")
    a1.axhline(100, color=AMBER, ls="--", lw=0.8)
    a1.text(1.2, 115, "100 MΩ", fontsize=6.5, color=AMBERDK)
    a1.axhline(2.5, color=AMBER, ls=":", lw=0.8)
    a1.text(1.2, 2.8, "2.5 MΩ", fontsize=6.5, color=AMBERDK)
    a1.set_xlim(1, 1e4); a1.set_ylim(0.5, 5e4)
    finish(a1, xlabel="Frequency (Hz)", ylabel="Differential input impedance (MΩ)", legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=5.6)
    panel(a1, "a")
    off = np.linspace(0.05, 0.4, 200)
    for swing, c, lab in ((0.5, C4, "integrator swing ±0.5 V (1.2 V)"), (1.5, C1, "integrator swing ±1.5 V (3.3 V)")):
        cdsl = off / swing * CIN
        gain = (CIN + CFB + CP_GATE + cdsl) / CIN
        a2.plot(off * 1e3, gain, color=c, label=lab)
        a2.plot(off * 1e3, cdsl / CIN + 1, color=c, ls=":", lw=0.8)
    a2.axhline((CIN + CFB + CP_GATE) / CIN, color=MUTED, ls="--", lw=0.8)
    a2.text(255, 1.105, "without a servo loop: 1.12", fontsize=6.5, color=MUTED, va="top")
    a2.axvline(300, color=AMBER, ls="--", lw=0.8)
    a2.set_xlim(50, 400); a2.set_ylim(1.0, 2.2)
    finish(a2, xlabel="Electrode offset to cancel (mV)", ylabel="Capacitive noise gain", legend=True,
           loc="upper left")
    a2.legend(loc="upper left", fontsize=6.0)
    panel(a2, "b")
    savefig(fig, "ch10_zin")


if __name__ == "__main__":
    for eps in (1, 0.1, 0.03):
        print("eps", eps, "Z 10Hz 5pF %.1f MOhm, 50Hz %.1f, 1kHz %.1f; 1pF 50Hz %.1f" % (
            z_boost(10, eps, 5e-12) / 1e6, z_boost(50, eps, 5e-12) / 1e6, z_boost(1e3, eps, 5e-12) / 1e6, z_boost(50, eps, 1e-12) / 1e6))
    for sw in (0.5, 1.5):
        cd = 0.3 / sw * CIN
        print("swing %.1f: Cdsl %.1f pF, noise gain %.2f (vs 1.12)" % (sw, cd * 1e12, (CIN + CFB + CP_GATE + cd) / CIN))
    print("tau for fHP 0.5 Hz with Cdsl/Cfb = 20: %.1f s" % (20 / (2 * np.pi * 0.5)))
    print("pad CM impedance 5 pF at 50 Hz: %.0f MOhm" % (1 / (2 * np.pi * 50 * 5e-12) / 1e6))
    fig_zin()
