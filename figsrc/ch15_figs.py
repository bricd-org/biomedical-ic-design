"""ch15_figs.py -- Chapter 15 figure from SG13G2 switch simulations (labs/spice/sg13_switch.py): on-resistance
versus input voltage, and hold droop from off-state leakage versus sampling capacitance."""
import os, sys, csv
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
LSB = 1.0 / 4096            # 12 bits over 1 V differential (the converter range of Chapter 11)
T_HOLD = 50e-6
T_ACQ = 1e-6


def ron(name):
    r = [x for x in csv.DictReader(open(os.path.join(DATA, "sg13_switch_ron.csv"))) if x["switch"] == name]
    return np.array([float(x["Vin_V"]) for x in r]), np.array([float(x["Ron_ohm"]) for x in r])


def leak():
    return {(int(x["stack"]), int(x["temp_C"])): float(x["I_A"]) for x in csv.DictReader(open(os.path.join(DATA, "sg13_switch_leak.csv")))}


def fig():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    for name, c, lab in (("nmos", C1, "NMOS 0.5/0.13 µm"), ("pmos", C4, "PMOS 1/0.13 µm"),
                         ("tg", C2, "transmission gate"), ("boot", C3, "bootstrapped NMOS")):
        v, r = ron(name)
        a1.semilogy(v, r, color=c, label=lab)
    rmax = T_ACQ / (13 * np.log(2)) / 4e-12
    a1.axhline(rmax, color=AMBER, ls="--", lw=0.9)
    a1.text(0.02, rmax * 1.3, "settling limit: 12 b in 1 µs on 4 pF", fontsize=6.5, color=AMBERDK)
    a1.set_xlim(0, 1.2); a1.set_ylim(5e2, 1e8)
    finish(a1, xlabel="Input voltage (V)", ylabel="On-resistance (Ω)", legend=True, loc="upper center")
    a1.legend(loc="upper center", fontsize=6.0)
    panel(a1, "a")
    lk = leak()
    cs = np.logspace(np.log10(0.3e-12), np.log10(30e-12), 100)
    for (s, t), c, ls in (((1, 37), C4, "-"), ((1, 85), C4, ":"), ((2, 37), C1, "-"), ((2, 85), C1, ":")):
        a2.loglog(cs * 1e12, lk[(s, t)] * T_HOLD / cs / LSB, color=c, ls=ls,
                  label=f"{'single' if s == 1 else 'two stacked'}, {t} °C ({lk[(s, t)]*1e12:.1f} pA)")
    a2.axhline(0.5, color=AMBER, ls="--", lw=0.9)
    a2.text(0.35, 0.56, "½ LSB", fontsize=6.5, color=AMBERDK)
    ktc = 24 * bs.K_B * 300 / LSB ** 2
    a2.axvline(ktc * 1e12, color=MUTED, ls=":", lw=0.8)
    a2.text(ktc * 1e12 * 1.08, 0.015, "kT/C limit\n(differential)", fontsize=6.3, color=MUTED)
    a2.set_xlim(0.3, 30); a2.set_ylim(0.01, 100)
    finish(a2, xlabel="Sampling capacitor per side (pF)", ylabel="Droop in 50 µs hold (LSB at 12 b)",
           legend=True, loc="upper right")
    a2.legend(loc="upper right", fontsize=5.8)
    panel(a2, "b")
    savefig(fig, "ch15_switch")


if __name__ == "__main__":
    lk = leak()
    print("LSB %.1f uV; kT/C diff C >= %.2f pF; settling Rmax %.1f kOhm" % (LSB * 1e6, 24 * bs.K_B * 300 / LSB ** 2 * 1e12, T_ACQ / (13 * np.log(2)) / 4e-12 / 1e3))
    for k, v in lk.items():
        print(k, "%.2f pA -> droop on 1 pF %.2f LSB, on 4 pF %.3f LSB" % (v * 1e12, v * T_HOLD / 1e-12 / LSB, v * T_HOLD / 4e-12 / LSB))
    cg = float(list(csv.DictReader(open(os.path.join(DATA, "sg13_switch_cgg.csv"))))[0]["Cgg_F"])
    q = cg * 0.9
    print("Cgg %.2f fF, Qch ~ %.2f fC, half on 1 pF: %.2f mV = %.2f LSB; on 4 pF %.3f mV" % (cg * 1e15, q * 1e15, q / 2 / 1e-12 * 1e3, q / 2 / 1e-12 / LSB, q / 2 / 4e-12 * 1e3))
    print("boot tau on 4 pF: %.1f ns" % (2e3 * 4e-12 * 1e9))
    fig()
