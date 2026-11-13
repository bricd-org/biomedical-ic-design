"""ch17_figs.py -- Chapter 17 figure: switching energy of a differential binary CDAC versus output code for
three switching schemes (charge-conservation model, energy drawn from V_ref), and mid-scale DNL versus unit
capacitance in SG13G2 MIM (1.5 fF/um^2, 1 %.um) with the total array size."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs


def _switch(caps, vb, vx, vb_new, vref):
    """Switch bottom plates vb -> vb_new on a floating top plate at vx; return new vx and energy from vref."""
    ct = caps.sum()
    vx_new = vx + np.dot(caps, vb_new - vb) / ct
    to_ref = vb_new == vref
    q = np.sum(caps[to_ref] * ((vref - vx_new) - (vb[to_ref] - vx)))
    return vx_new, vref * q


def energy(code, n, scheme, vref=1.0):
    """Energy (units of C_u * vref^2) to convert to `code` (0..2^n-1) in a differential array."""
    if scheme == "monotonic":                       # top-plate sampling, n-1 bit arrays, one side moves down
        caps = np.r_[2.0 ** np.arange(n - 2, -1, -1), 1.0]
        e = 0.0
        vp = np.full(len(caps), vref); vn = np.full(len(caps), vref)
        xp = xn = 0.0
        bits = [(code >> (n - 1 - k)) & 1 for k in range(n)]
        for k in range(n - 1):
            if bits[k]:                              # input positive: lower the positive side
                new = vp.copy(); new[k] = 0.0
                xp, de = _switch(caps, vp, xp, new, vref); vp = new
            else:
                new = vn.copy(); new[k] = 0.0
                xn, de = _switch(caps, vn, xn, new, vref); vn = new
            e += de
        return e
    caps = np.r_[2.0 ** np.arange(n - 1, -1, -1), 1.0]
    m = len(caps)
    bits = [(code >> (n - 1 - k)) & 1 for k in range(n)]
    e = 0.0
    if scheme == "conventional":                     # bottom plates: try MSB at vref, keep or reset
        for side, b_of in ((0, lambda b: b), (1, lambda b: 1 - b)):
            vb = np.zeros(m); x = 0.0
            for k in range(n):
                trial = vb.copy(); trial[k] = vref
                x, de = _switch(caps, vb, x, trial, vref); e += de; vb = trial
                if not b_of(bits[k]):
                    keep = vb.copy(); keep[k] = 0.0
                    x, de = _switch(caps, vb, x, keep, vref); e += de; vb = keep
        return e
    if scheme == "vcm":                               # bottom plates start at vref/2, move up or down
        for side, up_if in ((0, 1), (1, 0)):
            vb = np.full(m, vref / 2); x = 0.0
            for k in range(1, n):
                new = vb.copy(); new[k] = vref if bits[k - 1] == up_if else 0.0
                x, de = _switch(caps, vb, x, new, vref); e += de; vb = new
        return e
    raise ValueError(scheme)


def fig():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    n = 10
    codes = np.arange(0, 2 ** n, 4)
    for s, c, lab in (("conventional", C4, "conventional"), ("monotonic", C2, "monotonic"), ("vcm", C1, r"$V_\mathrm{cm}$-based")):
        ee = np.array([energy(int(k), n, s) for k in codes])
        a1.plot(codes, ee, color=c, lw=0.8, label=f"{lab}: mean {ee.mean():.0f}")
    a1.set_xlim(0, 2 ** n); a1.set_ylim(0, 3200)
    finish(a1, xlabel="Output code (10-bit array)", ylabel=r"Switching energy ($C_u V_\mathrm{ref}^2$)", legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=6.0)
    panel(a1, "a")
    cu = np.logspace(np.log10(0.3e-15), np.log10(50e-15), 200)
    sig_u = 0.01 / np.sqrt(cu / 1.5e-15)
    a2.loglog(cu * 1e15, sig_u * np.sqrt(4096), color=C1, label="mid-scale DNL σ, 12-bit binary")
    a2.axhline(0.5 / 3, color=AMBER, ls="--", lw=0.9)
    a2.text(0.33, 0.19, "0.5 LSB at 3σ", fontsize=6.5, color=AMBERDK)
    for ctot, lab in ((1.7e-12, "kT/C: 1.7 pF"), (4e-12, "leakage: 4 pF")):
        a2.axvline(ctot / 4096 * 1e15, color=MUTED, ls=":", lw=0.8)
        a2.text(ctot / 4096 * 1e15 * 1.07, 2.5, lab, fontsize=6.2, color=MUTED, rotation=90, va="top")
    ax2 = a2.twiny()
    ax2.set_xscale("log"); ax2.set_xlim(0.3e-15 * 4096 * 1e12, 50e-15 * 4096 * 1e12)
    ax2.set_xlabel("Total array per side (pF)", fontsize=8)
    a2.set_xlim(0.3, 50); a2.set_ylim(0.05, 5)
    finish(a2, xlabel="Unit capacitor (fF, MIM)", ylabel="Mid-scale DNL σ (LSB)", legend=True, loc="lower left")
    panel(a2, "b")
    savefig(fig, "ch17_cdac")


if __name__ == "__main__":
    for n in (10, 12):
        for s in ("conventional", "monotonic", "vcm"):
            ee = np.array([energy(k, n, s) for k in range(0, 2 ** n, 1 if n == 10 else 4)])
            print(n, s, "mean %.1f CuV^2" % ee.mean())
    cu = 4e-12 / 4096
    print("Cu for 4 pF %.2f fF, area %.2f um2, sigma_u %.2f %%, DNL mid %.2f LSB" % (cu * 1e15, cu / 1.5e-15, 1 / np.sqrt(cu / 1.5e-15), 0.01 / np.sqrt(cu / 1.5e-15) * 64))
    print("Cu for 0.26%%: area %.1f um2, Cu %.1f fF, total %.0f pF" % ((1 / 0.26) ** 2, (1 / 0.26) ** 2 * 1.5, (1 / 0.26) ** 2 * 1.5e-15 * 4096 * 1e12))
    fig()
