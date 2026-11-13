"""ch08_figs.py -- Chapter 8 figures from SG13G2 simulations (labs/spice/sg13_lna.py): pseudo-resistor
I-V and high-pass corner versus voltage and temperature; LNA input noise versus input-device area with
the capacitive noise gain, and the closed-loop response."""
import os, sys, csv
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CFB = 200e-15
CIN = 20e-12
K_NMOS = 1.58e-10
FLOOR = 18.5e-9           # thermal floor of one NMOS at 1 uA (Chapter 5)
F1, F2 = 0.5, 100.0


def pseudo(dev, pairs, temp):
    r = [x for x in csv.DictReader(open(os.path.join(DATA, "sg13_pseudo.csv")))
         if x["device"] == dev and int(x["pairs"]) == pairs and int(x["temp_C"]) == temp]
    v = np.array([float(x["V"]) for x in r]); i = np.array([float(x["I_A"]) for x in r])
    return v, i


def cgg_per_um2():
    r = list(csv.DictReader(open(os.path.join(DATA, "sg13_cgg.csv"))))
    wl = np.array([float(x["W_um"]) * float(x["L_um"]) for x in r]); c = np.array([float(x["Cgg_F"]) for x in r])
    return wl, c


def fig_pseudo():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    cases = (("lv", 1, C4, "1 pair, thin oxide"), ("lv", 4, C2, "4 pairs, thin oxide"), ("hv", 1, C1, "1 pair, thick oxide"))
    for dev, p, c, lab in cases:
        for t, ls in ((27, "-"), (85, "--")):
            v, i = pseudo(dev, p, t)
            sel = v > 0.004
            a1.semilogy(v[sel], i[sel], color=c, ls=ls, label=f"{lab}, {t} °C")
            ism = np.convolve(i, np.ones(5) / 5, mode="same")     # light smoothing before differentiating
            r = np.gradient(v, ism)
            a2.semilogy(v[sel][2:-2], 1 / (2 * np.pi * r[sel][2:-2] * CFB), color=c, ls=ls)
    a1.set_xlim(0, 0.6); a1.set_ylim(1e-16, 1e-8)
    finish(a1, xlabel="Voltage across the pseudo-resistor (V)", ylabel="Current (A)", legend=True, loc="lower right")
    a1.legend(loc="lower right", fontsize=5.6)
    panel(a1, "a")
    a2.axhline(0.5, color=AMBER, ls="--", lw=0.9)
    a2.text(0.02, 0.56, "0.5 Hz: EEG band edge", fontsize=6.5, color=AMBERDK, va="bottom")
    a2.set_xlim(0, 0.6); a2.set_ylim(5e-3, 1e3)
    finish(a2, xlabel="Voltage across the pseudo-resistor (V)", ylabel=r"High-pass corner, $C_2$ = 200 fF (Hz)")
    panel(a2, "b")
    savefig(fig, "ch08_pseudo")


def lna_noise(wl, c1, chopped=False):
    wlp, cp = cgg_per_um2()
    cgg = np.interp(np.log(wl), np.log(wlp), cp / wlp) * wl      # F, per-area value held flat outside the data
    gain = (c1 + CFB + cgg) / c1
    flick = 0.0 if chopped else 2 * K_NMOS / wl * np.log(F2 / F1)
    pair = np.sqrt(flick + 2 * FLOOR ** 2 * (F2 - F1))
    return gain * pair, gain


def fig_noise():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    wl = np.logspace(1, 4.5, 300)
    for c1, c in ((10e-12, C4), (20e-12, C1), (40e-12, C3)):
        v, _ = lna_noise(wl, c1)
        a1.loglog(wl, v * 1e6, color=c, label=f"unchopped, $C_1$ = {c1*1e12:g} pF")
        j = np.argmin(v)
        a1.plot(wl[j], v[j] * 1e6, "o", color=c, ms=4)
        vc, _ = lna_noise(wl, c1, chopped=True)
        a1.loglog(wl, vc * 1e6, color=c, ls="--", lw=0.9, label=f"chopped, $C_1$ = {c1*1e12:g} pF")
    a1.axhline(1.46, color=AMBER, ls="--", lw=0.8)
    a1.text(12, 1.6, "1.46 µV", fontsize=6.5, color=AMBERDK)
    a1.set_xlim(10, 3e4); a1.set_ylim(0.15, 20)
    finish(a1, xlabel="Input-device area W·L (µm² each)", ylabel="LNA input noise, 0.5–100 Hz (µVrms)",
           legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=5.6)
    panel(a1, "a")
    f = np.logspace(-2, 6, 600)
    am = CIN / CFB
    gm = 30e-6
    for cl, c in ((2e-12, C1), (10e-12, C3)):
        fh = gm / (2 * np.pi * am * cl)
        for t, ls in ((37, "-"), (85, "--")):
            v, i = pseudo("hv", 1, t)
            rr = np.gradient(v, i)[np.argmin(abs(v - 0.02))]
            fl = 1 / (2 * np.pi * rr * CFB)
            h = am * (1j * f / fl) / (1 + 1j * f / fl) / (1 + 1j * f / fh)
            a2.semilogx(f, 20 * np.log10(np.abs(h)), color=c, ls=ls,
                        label=rf"$C_\mathrm{{L}}$ = {cl*1e12:g} pF, {t} °C")
    a2.axvspan(0.5, 100, color=BTINT, lw=0)
    a2.set_xlim(1e-2, 1e6); a2.set_ylim(0, 45)
    finish(a2, xlabel="Frequency (Hz)", ylabel="Gain (dB)", legend=True, loc="lower center")
    a2.legend(loc="lower center", fontsize=5.6)
    panel(a2, "b")
    savefig(fig, "ch08_lna")


if __name__ == "__main__":
    wlp, cp = cgg_per_um2()
    print("Cgg per um2 (fF):", np.round(cp / wlp * 1e15, 2))
    for dev, p, ts in (("lv", 1, (27, 85)), ("lv", 4, (27, 85)), ("hv", 1, (27, 37, 85))):
        for t in ts:
            v, i = pseudo(dev, p, t)
            r = np.gradient(v, i)
            j = np.argmin(abs(v - 0.02))
            print(dev, p, t, "R %.2g fL %.3g Hz" % (r[j], 1 / (2 * np.pi * r[j] * CFB)))
    wl = np.logspace(1, 4.5, 2000)
    for c1 in (10e-12, 20e-12, 40e-12):
        v, g = lna_noise(wl, c1); j = np.argmin(v)
        vc, gc = lna_noise(np.array([100.0, 1000.0]), c1, chopped=True)
        print("C1 %.0f pF: optimum WL %.0f um2, noise %.3f uV, gain %.2f; chopped at 100/1000 um2: %s" % (c1 * 1e12, wl[j], v[j] * 1e6, g[j], np.round(vc * 1e6, 3)))
    print("fH C_L=2p:", 30e-6 / (2 * np.pi * 100 * 2e-12), "C_L=10p:", 30e-6 / (2 * np.pi * 100 * 10e-12))
    print("wideband thermal pair 26nV over pi/2*24k:", 26e-9 * np.sqrt(np.pi / 2 * 23.9e3))
    fig_pseudo()
    fig_noise()
