"""ch16_figs.py -- Chapter 16 figure: input-referred noise of a dynamic (integrating) comparator versus
the charge its input pair integrates, and offset versus input-pair area from the SG13G2 Pelgrom
coefficients. Closed-form models; Lab 7 checks them with transient-noise and Monte Carlo simulation."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

Q = 1.602176634e-19
UT = bs.K_B * 300 / Q
N = 1.22
LSB12 = 1.0 / 4096
A_VT = {"NMOS": 3.9e-3, "PMOS": 2.2e-3}


def sigma_noise(qint):
    """Weak-inversion input pair integrating charge qint per device: shot noise of the two currents
    against the signal charge, sigma_v = 2 n U_T sqrt(q / Q_int)."""
    return 2 * N * UT * np.sqrt(Q / qint)


def fig():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    qi = np.logspace(-15, -12, 200)
    a1.loglog(qi * 1e15, sigma_noise(qi) * 1e6, color=C1, label=r"$\sigma_v = 2nU_T\sqrt{q/Q_\mathrm{int}}$")
    for nb, c in ((10, C2), (12, C3)):
        lsb = 1.0 / 2 ** nb
        a1.axhline(lsb / 4 * 1e6, color=c, ls="--", lw=0.9)
        a1.text(1.1, lsb / 4 * 1e6 * 1.12, f"LSB/4 at {nb} b", fontsize=6.5, color=c)
    a1.set_xlim(1, 1000); a1.set_ylim(20, 2e3)
    finish(a1, xlabel="Charge integrated per input device (fC)", ylabel="Input-referred noise (µVrms)",
           legend=True, loc="upper right")
    panel(a1, "a")
    wl = np.logspace(-1, 3, 200)
    for dev, c in (("NMOS", C1), ("PMOS", C4)):
        a2.loglog(wl, A_VT[dev] / np.sqrt(wl) * 1e3, color=c, label=f"{dev} pair, {A_VT[dev]*1e3:g} mV·µm")
    a2.axhline(LSB12 * 1e3, color=AMBER, ls="--", lw=0.9)
    a2.text(0.12, LSB12 * 1e3 * 1.12, "1 LSB at 12 b (244 µV)", fontsize=6.5, color=AMBERDK)
    a2.set_xlim(0.1, 1000); a2.set_ylim(0.05, 20)
    finish(a2, xlabel="Input-device area W·L (µm² each)", ylabel="Offset σ (mV)", legend=True, loc="upper right")
    panel(a2, "b")
    savefig(fig, "ch16_comparator")


if __name__ == "__main__":
    tgt = LSB12 / 4
    qn = Q * (2 * N * UT / tgt) ** 2
    print("12b: target %.1f uV -> Q_int %.0f fC per device; C_L for 0.5 V swing %.0f fF" % (tgt * 1e6, qn * 1e15, qn / 0.5 * 1e15))
    e = 2 * (qn / 0.5) * 1.2 ** 2
    print("energy per decision ~2 C_L VDD^2 = %.2f pJ; x12 = %.1f pJ; at 16 kS/s %.2f uW" % (e * 1e12, 12 * e * 1e12, 12 * e * 16e3 * 1e6))
    t10 = 1 / 1024 / 4
    q10 = Q * (2 * N * UT / t10) ** 2
    print("10b: Q %.1f fC, C_L %.0f fF, E %.3f pJ" % (q10 * 1e15, q10 / 0.5 * 1e15, 2 * q10 / 0.5 * 1.44 * 1e12))
    print("offset NMOS 4 um2 %.2f mV, PMOS %.2f mV" % (3.9 / 2, 2.2 / 2))
    tau = 50e-12; a = 10
    for t in (0.5e-9, 1e-9, 2e-9):
        print("metastability t=%.1f ns: P ~ %.2e" % (t * 1e9, 1.2 / (a * 1.0) * np.exp(-t / tau)))
    fig()
