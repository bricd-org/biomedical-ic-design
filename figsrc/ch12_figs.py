"""ch12_figs.py -- Chapter 12 figure: the ECG CMRR test with a right-leg drive (residual differential
interference versus loop gain for several common-mode input impedances) and the stability of the
right-leg-drive loop versus its crossover frequency for several safety resistors."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

F = 50.0
VCM_TEST = 10.0                 # V rms, IEC 60601-2-25 CMRR test
CMRR_INT_DB = 100.0
C_BODY = 200e-12


def residual_pp(a, zcm):
    """Differential interference (V peak-to-peak, input-referred) in the CMRR test with a right-leg
    drive of loop gain a at 50 Hz: the common mode at the electrodes is reduced by 1 + a."""
    _, _, dz = bs.cmrr_test_zcm(F)
    vcm = VCM_TEST / (1 + a)
    vdm = vcm * (dz / zcm + 10 ** (-CMRR_INT_DB / 20))
    return 2 * np.sqrt(2) * vdm


def loop_pm(fu, r_o, c_b=C_BODY):
    """Phase margin (deg) of the RLD loop: integrating amplifier with unity-gain frequency fu (Hz)
    driving the body capacitance through the safety resistor r_o plus the RL electrode (51k||47n)."""
    f = np.logspace(1, 7, 6000)
    s = 2j * np.pi * f
    ze = bs.z_electrode(f, "wet Ag/AgCl")
    lg = (2 * np.pi * fu / s) / (1 + s * c_b * (r_o + ze))
    k = np.argmin(np.abs(np.abs(lg) - 1))
    return 180 + np.degrees(np.angle(lg[k]))


def fig():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    a = np.logspace(0, 3, 200)
    for zcm, c, lab in ((6.25e6, C4, "6.25 MΩ (chopped)"), (200e6, C1, "200 MΩ (boosted)"), (1.15e9, C3, "1.15 GΩ")):
        a1.loglog(a, residual_pp(a, zcm) * 1e3, color=c, label=r"$Z_\mathrm{cm}$ = " + lab)
    a1.axhline(1.0, color=AMBER, ls="--", lw=0.9)
    a1.text(1.2, 1.15, "1 mVpp limit", fontsize=6.5, color=AMBERDK, va="bottom")
    a1.axvline(100, color=MUTED, ls=":", lw=0.7)
    a1.set_xlim(1, 1000); a1.set_ylim(1e-3, 1e3)
    finish(a1, xlabel="Right-leg-drive loop gain at 50 Hz", ylabel="Residual in the CMRR test (mVpp)",
           legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=6.0)
    panel(a1, "a")
    fu = np.logspace(2.5, 5, 60)
    for r_o, c in ((120e3, C3), (150e3, C1), (390e3, C2), (1e6, C4)):
        pm = [loop_pm(x, r_o) for x in fu]
        a2.semilogx(fu, pm, color=c, label=rf"$R_\mathrm{{o}}$ = {r_o/1e3:g} kΩ  (saturated: {1.2/r_o*1e6:.1f} µA)")
    a2.axhline(45, color=MUTED, ls=":", lw=0.8)
    a2.axvline(5e3, color=MUTED, ls=":", lw=0.7)
    a2.text(5.4e3, 82, "loop gain 100\nat 50 Hz", fontsize=6.3, color=MUTED)
    a2.set_xlim(300, 1e5); a2.set_ylim(0, 95)
    finish(a2, xlabel="RLD unity-gain frequency (Hz)", ylabel="Phase margin (°)", legend=True, loc="lower left")
    a2.legend(loc="lower left", fontsize=5.8)
    panel(a2, "b")
    savefig(fig, "ch12_rld")


if __name__ == "__main__":
    zcm0, c0, dz = bs.cmrr_test_zcm(F)
    print("no RLD: Zcm needed %.2f GOhm (dz %.1f k)" % (zcm0 / 1e9, dz / 1e3))
    for a in (10, 40, 100):
        print("A=%d: Zcm needed %.1f MOhm; residual pp with 6.25M: %.3f mV, 200M: %.4f mV" % (
            a, zcm0 / (1 + a) / 1e6, residual_pp(a, 6.25e6) * 1e3, residual_pp(a, 200e6) * 1e3))
    for r_o in (120e3, 150e3, 390e3, 1e6):
        print("Ro %g k: Isat %.1f uA, PM at fu=2k %.0f, 5k %.0f deg" % (r_o / 1e3, 1.2 / r_o * 1e6, loop_pm(2e3, r_o), loop_pm(5e3, r_o)))
    print("PM 150k fu 5k with Cb 100p/300p: %.0f / %.0f" % (loop_pm(5e3, 150e3, 100e-12), loop_pm(5e3, 150e3, 300e-12)))
    print("series R noise: 5k pair %.2f uV, 10k pair %.2f uV" % (np.sqrt(2 * 4 * bs.K_B * 310 * 5e3 * 99.5) * 1e6, np.sqrt(2 * 4 * bs.K_B * 310 * 10e3 * 99.5) * 1e6))
    fig()
