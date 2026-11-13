"""ch05_figs.py -- Chapter 5 figures from SG13G2 ngspice data (labs/spice/sg13_char.py writes the CSVs):
gm/ID versus current density, flicker noise versus area, and MOSFET versus HBT input noise against
electrode impedance."""
import os, sys, csv
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
UT = bs.K_B * 300.0 / 1.602176634e-19
Q = 1.602176634e-19
KT = bs.K_B * 300.0


def rows(name):
    return list(csv.DictReader(open(os.path.join(DATA, name))))


def gmid(dev, L):
    r = [x for x in rows("sg13_gmid.csv") if x["device"] == dev and float(x["L_um"]) == L]
    vg = np.array([float(x["VGS_V"]) for x in r]); i = np.array([float(x["ID_A"]) for x in r])
    gm = np.array([float(x["gm_S"]) for x in r]); w = float(r[0]["W_um"])
    k = slice(5, -5)                        # drop the end points of the numerical derivative
    return vg[k], i[k], gm[k], w


def noise(dev, w, l):
    r = [x for x in rows("sg13_noise.csv") if x["device"] == dev and float(x["W_um"]) == w and float(x["L_um"]) == l]
    return np.array([float(x["f_Hz"]) for x in r]), np.array([float(x["vn_V_per_rtHz"]) for x in r])


SIZES = [(10.0, 1.0), (40.0, 4.0), (100.0, 10.0)]


def flicker_coeff(dev):
    """K (V^2 um^2): v_n^2 = K / (W L f) + floor^2, averaged over the three sizes; and the floors."""
    ks, floors = [], {}
    for w, l in SIZES:
        f, v = noise(dev, w, l)
        fl = v[-1] ** 2
        floors[(w, l)] = np.sqrt(fl)
        sel = (f >= 0.5) & (f <= 10)
        ks.append(np.mean((v[sel] ** 2 - fl) * f[sel]) * w * l)
    return float(np.mean(ks)), floors


def ispec(dev, L=1.0):
    """Specific current per square (A) from where gm/ID falls to half its weak-inversion maximum (IC = 2)."""
    vg, i, gm, w = gmid(dev, L)
    ok = i > 1e-12
    r = gm[ok] / i[ok]
    mx = r[i[ok] < 1e-8].max()
    j = np.argmin(np.abs(r - mx / 2))
    return i[ok][j] / (w / L) / 2.0, mx


def summary():
    out = {}
    for dev in ("nmos", "pmos"):
        k, fl = flicker_coeff(dev)
        isq, mx = ispec(dev)
        out[dev] = dict(K=k, floors=fl, ispec=isq, gmid_max=mx, n=1 / (mx * UT))
    h = rows("sg13_hbt.csv")
    vb = np.array([float(x["VBE_V"]) for x in h]); ic = np.array([float(x["IC_A"]) for x in h])
    ib = np.array([float(x["IB_A"]) for x in h])
    j = np.argmin(np.abs(ic - 1e-6))
    hn = np.loadtxt(os.path.join(DATA, "sg13_hbt_noise.csv"), delimiter=",", skiprows=1)
    out["hbt"] = dict(beta=ic[j] / ib[j], gm_ic=np.gradient(ic, vb)[j] / ic[j], en=float(np.median(hn[:, 1])),
                      ib=ib[j])
    return out


def fig_gmid():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    for dev, c in (("nmos", C1), ("pmos", C4)):
        for L, ls in ((1.0, "-"), (4.0, "--")):
            vg, i, gm, w = gmid(dev, L)
            ok = i > 1e-13
            dens = i[ok] / (w / L)
            a1.semilogx(dens, gm[ok] / i[ok], color=c, ls=ls, label=f"{dev.upper()} L = {L:g} µm")
            if L == 1.0:
                a2.semilogy(vg, i / (w / L), color=c, label=f"{dev.upper()}, W/L = 10/1")
    a1.axhline(1 / (1.2 * UT), color=MUTED, lw=0.7, ls=":")
    a1.text(2e-12, 1 / (1.2 * UT) + 0.8, r"$1/(nU_T)$, n = 1.2", fontsize=6.5, color=MUTED)
    a1.axvspan(1e-9, 1e-7, color=ATINT, lw=0)
    a1.text(1e-8, 3, "biomedical\nbias", fontsize=6.5, color=AMBERDK, ha="center")
    a1.set_xlim(1e-12, 1e-4); a1.set_ylim(0, 36)
    finish(a1, xlabel=r"Current density $I_\mathrm{D}/(W/L)$ (A)", ylabel=r"$g_\mathrm{m}/I_\mathrm{D}$ (1/V)", legend=True, loc="lower left")
    a1.legend(loc="lower left", fontsize=6.3)
    panel(a1, "a")
    a2.axhline(1e-7, color=AMBER, ls="--", lw=0.8)
    a2.text(0.02, 1.4e-7, "100 nA per square", fontsize=6.5, color=AMBERDK)
    a2.set_xlim(0, 1.2); a2.set_ylim(1e-12, 1e-3)
    finish(a2, xlabel=r"$|V_\mathrm{GS}|$ (V)", ylabel=r"$I_\mathrm{D}/(W/L)$ (A)", legend=True, loc="lower right")
    panel(a2, "b")
    savefig(fig, "ch05_gmid")


def fig_noise(s):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    for dev, c in (("nmos", C1), ("pmos", C4)):
        for (w, l), ls in zip(SIZES, ("-", "--", ":")):
            f, v = noise(dev, w, l)
            a1.loglog(f, v * 1e9, color=c, ls=ls, lw=1.1, label=f"{dev.upper()} {w:g}/{l:g} ({w*l:g} µm²)")
    hn = np.loadtxt(os.path.join(DATA, "sg13_hbt_noise.csv"), delimiter=",", skiprows=1)
    a1.loglog(hn[:, 0], hn[:, 1] * 1e9, color=C3, lw=1.4, label="HBT npn13G2 (voltage noise)")
    a1.axvspan(0.5, 100, color=BTINT, lw=0)
    a1.set_xlim(0.1, 1e6); a1.set_ylim(5, 2e4)
    finish(a1, xlabel="Frequency (Hz)", ylabel="Input-referred noise (nV/√Hz)", legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=5.8)
    panel(a1, "a")
    wl = np.logspace(1, 4.5, 100)
    for dev, c in (("nmos", C1), ("pmos", C4)):
        k = s[dev]["K"]
        fl = s[dev]["floors"][(100.0, 10.0)]
        pair = np.sqrt(2 * (k / wl * np.log(100 / 0.5) + fl ** 2 * 99.5))
        a2.loglog(wl, pair * 1e6, color=c, label=f"{dev.upper()} pair, 0.5–100 Hz")
    a2.axhline(1.5, color=AMBER, ls="--", lw=1)
    a2.text(12, 1.6, "1.5 µVrms target", fontsize=7, color=AMBERDK, va="bottom")
    a2.axhline(1.0, color=MUTED, ls=":", lw=0.8)
    a2.text(12, 0.93, "1 µVrms for the pair", fontsize=6.5, color=MUTED, va="top")
    a2.set_xlim(10, 3e4); a2.set_ylim(0.1, 20)
    finish(a2, xlabel="Gate area W·L per device (µm²)", ylabel="Pair noise (µVrms)", legend=True, loc="upper right")
    panel(a2, "b")
    savefig(fig, "ch05_noise")


def fig_hbt(s):
    fig, ax = plt.subplots(figsize=FULL)
    rs = np.logspace(3, 8, 200)
    th = 4 * KT * rs
    f10 = 10.0
    f, v = noise("nmos", 100.0, 10.0)
    en_mos = np.interp(f10, f, v)
    en_hbt = s["hbt"]["en"]
    in_hbt = np.sqrt(2 * Q * s["hbt"]["ib"])
    tot_mos = np.sqrt(en_mos ** 2 + th)
    tot_hbt = np.sqrt(en_hbt ** 2 + (in_hbt * rs) ** 2 + th)
    ax.loglog(rs, np.sqrt(th) * 1e9, color=MUTED, ls=":", label="source resistance alone, 4kTR")
    ax.loglog(rs, tot_mos * 1e9, color=C1, label="NMOS 100/10 µm at 1 µA (10 Hz)")
    ax.loglog(rs, tot_hbt * 1e9, color=C3, label=r"HBT at 1 µA, base shot noise $2qI_\mathrm{B}$")
    for z, lab in ((50e3, "wet\nAg/AgCl"), (1e6, "dry"), (1e7, "dry, low f /\nnon-contact")):
        ax.axvline(z, color=GRID, lw=1.2, zorder=0)
        ax.text(z * 1.1, 6, lab, fontsize=6.5, color=MUTED, va="bottom")
    ax.set_xlim(1e3, 1e8); ax.set_ylim(5, 3e3)
    finish(ax, xlabel="Electrode impedance (Ω)", ylabel="Total input noise at 10 Hz (nV/√Hz)",
           legend=True, loc="upper left")
    savefig(fig, "ch05_hbt")


if __name__ == "__main__":
    s = summary()
    for d in ("nmos", "pmos"):
        x = s[d]
        print(d, "K = %.3g V^2um^2" % x["K"], "Ispec/sq = %.3g nA" % (x["ispec"] * 1e9),
              "gm/ID max %.1f n %.2f" % (x["gmid_max"], x["n"]),
              "floors nV:", {k: round(v * 1e9, 1) for k, v in x["floors"].items()})
    print("hbt", s["hbt"])
    fig_gmid()
    fig_noise(s)
    fig_hbt(s)
