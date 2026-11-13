"""ch06_figs.py -- Chapter 6 figures: noise density and noise bandwidth of an input pair, and the
current a noise target costs (NEF), with an SG13G2 NMOS pair from figsrc/data/sg13_gmid.csv."""
import os, sys, csv
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
KT = bs.K_B * 300.0
UT = KT / 1.602176634e-19
N_SLOPE = 1.22                     # NMOS, Chapter 5
K_NMOS = 1.58e-10                  # V^2 um^2, Chapter 5
F1, F2 = 0.5, 100.0
BW = F2 - F1
C_NEF = 4 * KT * UT * BW                 # I_tot = NEF^2 * C_NEF / V^2 with BW the noise bandwidth
#   (Steyaert's NEF with BW_3dB = 2 B_n / pi, i.e. a brick-wall band of B_n hertz)


def gmid_table(L=4.0):
    r = [x for x in csv.DictReader(open(os.path.join(DATA, "sg13_gmid.csv")))
         if x["device"] == "nmos" and float(x["L_um"]) == L]
    i = np.array([float(x["ID_A"]) for x in r]); gm = np.array([float(x["gm_S"]) for x in r])
    w = float(r[0]["W_um"])
    ok = (i > 1e-12) & (gm > 0)
    k = slice(5, -5)
    dens = (i[ok] / (w / L))[k]; g = (gm[ok] / i[ok])[k]
    o = np.argsort(dens)
    return dens[o], g[o]


def pair_thermal(i_tot, wl_squares=10.0):
    """Thermal noise (V rms over 0.5-100 Hz) of an NMOS pair of W/L = wl_squares per device at total current i_tot."""
    dens, g = gmid_table()
    gmid = np.interp(np.log(i_tot / 2 / wl_squares), np.log(dens), g)
    gm = gmid * i_tot / 2
    return np.sqrt(2 * 2 * N_SLOPE * KT / gm * BW), gmid


def fig_bandwidth():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    f = np.logspace(np.log10(F1), 6, 3000)
    wl = 1800.0
    floor = 18.5e-9
    psd = 2 * (K_NMOS / (wl * f) + floor ** 2)          # pair, V^2/Hz
    a1.loglog(f, np.sqrt(psd) * 1e9, color=C1, label="NMOS pair, 1800 µm² each, 1 µA each")
    a1.loglog(f, np.sqrt(2 * K_NMOS / (wl * f)) * 1e9, color=C1, ls=":", lw=0.8, label="flicker part")
    a1.axhline(np.sqrt(2) * floor * 1e9, color=C1, ls="--", lw=0.8, label="thermal part")
    a1.axvspan(F1, F2, color=BTINT, lw=0)
    a1.set_xlim(F1, 1e5); a1.set_ylim(10, 3e3)
    finish(a1, xlabel="Frequency (Hz)", ylabel="Input-referred noise (nV/√Hz)", legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=6.3)
    panel(a1, "a")
    res = {}
    th = 2 * floor ** 2 * np.ones_like(f)                 # chopped pair: thermal only
    for name, h2, c in (("brick wall at 100 Hz", np.where(f <= F2, 1.0, 0.0), GRAPHITE),
                        ("1st-order low-pass", 1 / (1 + (f / F2) ** 2), C4),
                        ("2nd-order Butterworth", 1 / (1 + (f / F2) ** 4), C3)):
        for p, ls, tag in ((psd, "-", "unchopped"), (th, "--", "chopped")):
            cum = np.sqrt(np.concatenate([[0], np.cumsum(0.5 * (p[1:] * h2[1:] + p[:-1] * h2[:-1]) * np.diff(f))]))
            a2.semilogx(f, cum * 1e6, color=c, ls=ls, label=f"{tag}, {name}" if tag == "unchopped" or c != GRAPHITE or True else None)
            res[f"{tag}, {name}"] = cum[-1]
    a2.axhline(1.0, color=MUTED, ls=":", lw=0.8)
    a2.axvline(F2, color=MUTED, ls=":", lw=0.7)
    a2.set_xlim(F1, 1e5); a2.set_ylim(0, 1.25)
    finish(a2, xlabel="Upper integration limit (Hz)", ylabel="Integrated noise from 0.5 Hz (µVrms)",
           legend=True, loc="lower right")
    a2.legend(loc="center right", fontsize=5.6)
    panel(a2, "b")
    savefig(fig, "ch06_bw")
    return res


def fig_nef():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    v = np.logspace(np.log10(0.2e-6), np.log10(5e-6), 200)
    for nef, c, lab in ((np.sqrt(2), GRAPHITE, "NEF = √2 (ideal BJT pair)"),
                        (np.sqrt(2) * N_SLOPE, C1, "NEF = 1.73 (weak-inversion MOS pair)"),
                        (3.0, C2, "NEF = 3"), (4.0, C5, "NEF = 4"), (6.0, C4, "NEF = 6")):
        a1.loglog(v * 1e6, nef ** 2 * C_NEF / v ** 2 * 1e9, color=c, label=lab)
    for tgt, lab in ((1.46e-6, "wet: 1.46 µV"), (0.9e-6, "dry: 0.9 µV")):
        a1.axvline(tgt * 1e6, color=AMBER, ls="--", lw=0.8)
        a1.text(tgt * 1e6 * 1.04, 1.3e4, lab, fontsize=6.5, color=AMBERDK, rotation=90, va="top")
    a1.set_xlim(0.2, 5); a1.set_ylim(1, 3e4)
    a1.set_xticks([0.2, 0.5, 1, 2, 5]); a1.set_xticklabels(["0.2", "0.5", "1", "2", "5"])
    finish(a1, xlabel="Amplifier noise budget, 0.5–100 Hz (µVrms)", ylabel="Total current needed (nA)",
           legend=True, loc="lower left")
    a1.legend(loc="lower left", fontsize=6.0)
    panel(a1, "a")
    it = np.logspace(-8, -4.3, 200)
    th, gmid = pair_thermal(it)
    a2.loglog(it * 1e6, th * 1e6, color=C1, label="NMOS pair 100/10 µm, thermal only")
    a2.loglog(it * 1e6, np.sqrt(2) * N_SLOPE * np.sqrt(C_NEF / it) * 1e6, color=C1, ls=":", lw=0.8,
              label="weak-inversion limit, NEF = √2·n")
    for wl, c in ((1000.0, C4), (1800.0, C2)):
        fl = np.sqrt(2 * K_NMOS / wl * np.log(F2 / F1))
        a2.loglog(it * 1e6, np.sqrt(th ** 2 + fl ** 2) * 1e6, color=c, label=f"with 1/f, unchopped, {wl:g} µm²")
    a2.axhline(1.46, color=AMBER, ls="--", lw=0.8)
    a2.text(0.012, 1.55, "1.46 µV", fontsize=6.5, color=AMBERDK, va="bottom")
    a2.set_xlim(0.01, 50); a2.set_ylim(0.05, 20)
    finish(a2, xlabel="Total pair current (µA)", ylabel="Input noise, 0.5–100 Hz (µVrms)", legend=True,
           loc="upper right")
    a2.legend(loc="upper right", fontsize=6.0)
    panel(a2, "b")
    savefig(fig, "ch06_nef")


if __name__ == "__main__":
    res = fig_bandwidth()
    print({k: round(v * 1e6, 3) for k, v in res.items()})
    print("C_NEF", C_NEF)
    for nef in (2**0.5, 2**0.5*N_SLOPE, 3, 4, 6):
        print("NEF", nef, "I for 1.46uV: %.0f nA, 0.9uV: %.0f nA" % (nef**2*C_NEF/1.46e-6**2*1e9, nef**2*C_NEF/0.9e-6**2*1e9))
    for it in (0.1e-6, 0.3e-6, 1e-6, 2e-6, 4e-6, 10e-6):
        th, g = pair_thermal(np.array([it]))
        nef = th[0] / np.sqrt(C_NEF / it)
        print("I_tot %.1f uA: thermal %.3f uV, gm/ID %.1f, NEF %.2f, PEF(1.2V) %.1f" % (it * 1e6, th[0] * 1e6, g[0], nef, nef**2 * 1.2))
    fig_nef()
