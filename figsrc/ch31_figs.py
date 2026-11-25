"""ch31_figs.py -- Chapter 31 figures and numbers: adaptive cancellation of a motion artefact with an impedance
reference, an accelerometer reference or both (NLMS), on a synthetic EEG. The artefact model: part follows the
electrode impedance change (lead-off current and common-mode conversion through the changing interface), part
follows head acceleration directly, and a small part follows neither.

    python ch31_figs.py      # Figures 31.1 and 31.2, then report() prints every number the chapter quotes

Figure 31.1: the three reference sets. Figure 31.2: (a) how fast the canceller learns for three step sizes,
(b) what a late impedance trace costs, and how lining the streams up gets it back. report() adds the
least-squares ceiling, the step-size sweep, the effective step and learning time from the key equation, and the
bit budget of the quality record (Worked Example 31.4)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig
from scipy import signal as sps

FS, DUR = 256.0, 60.0


def scene(seed=3):
    """Synthetic EEG, head acceleration, impedance change and the artefact they cause."""
    rng = np.random.default_rng(seed)
    t, eeg = biosig.eeg(fs=FS, duration=DUR, seed=seed)[:2]
    n = len(t)
    # head motion: walking bursts (1.8 Hz steps) and a few nods
    acc = np.zeros(n)
    for s0, s1, f0 in ((8, 20, 1.8), (30, 38, 1.6), (46, 54, 2.0)):
        m = (t >= s0) & (t < s1)
        env = np.sin(np.pi * (t[m] - s0) / (s1 - s0)) ** 2
        acc[m] += env * (np.sin(2 * np.pi * f0 * t[m]) + 0.4 * np.sin(4 * np.pi * f0 * t[m] + 0.7))
    acc += 0.05 * sps.lfilter(*sps.butter(2, 3, fs=FS), rng.standard_normal(n))
    # the interface responds to motion with a lag and a nonlinearity: impedance change in kOhm
    dz = sps.lfilter(*sps.butter(2, 1.5, fs=FS), np.abs(acc) ** 1.3 + 0.3 * acc) * 20.0
    dz += np.cumsum(rng.standard_normal(n)) * 0.002                     # slow drift of the contact
    # artefact in volts: 6 nA of lead-off current through dZ, plus a part that follows acceleration directly
    art = 6e-9 * dz * 1e3 + 40e-6 * sps.lfilter(*sps.butter(1, 4, fs=FS), acc)
    art += 8e-6 * sps.lfilter(*sps.butter(2, 2, fs=FS), rng.standard_normal(n))   # follows neither reference
    return t, eeg, acc, dz, art


def nlms(d, refs, taps=8, mu=0.01, eps=None):
    """Multichannel NLMS: each reference with `taps` delays; returns the cleaned signal e = d - y.
    The references are bursty (near zero between movements), so the step is regularised by eps, of the order of
    the references' typical power (default: one per tap), not divided by a tiny |x|^2."""
    refs = [(r - r.mean()) / (r.std() + 1e-30) for r in refs]
    n, k = len(d), taps * len(refs)
    eps = float(k) if eps is None else eps
    w, e, x = np.zeros(k), np.zeros(n), np.zeros(k)
    for i in range(n):
        x = np.concatenate([r[max(0, i - taps + 1): i + 1][::-1] if i >= taps - 1 else
                            np.pad(r[: i + 1][::-1], (0, taps - 1 - i)) for r in refs])
        y = w @ x
        e[i] = d[i] - y
        w += mu * e[i] * x / (eps + x @ x)
    return e


BURSTS = ((8, 20), (30, 38), (46, 54))       # the three walks in scene(), s
MUS = (0.003, 0.01, 0.03, 0.1, 0.3)


def filtered():
    """scene() through the recording chain's 0.5-40 Hz (servo and decimation filters); the references get the
    same filter, so that the offset of the artefact, which no recording keeps, does not count."""
    t, eeg, acc, dz, art = scene()
    bp = sps.butter(2, [0.5, 40], "band", fs=FS)
    eeg, acc, dz, art = (sps.lfilter(*bp, x) for x in (eeg, acc, dz, art))
    return t, eeg, acc, dz, art


def reduction(art, res, sel):
    """Artefact power removed, dB: artefact power over the power of what is left (output minus clean EEG)."""
    return 10 * np.log10(np.mean(art[sel] ** 2) / np.mean(res[sel] ** 2))


def delay(x, k):
    """x delayed by k samples (zeros shifted in)."""
    return np.concatenate([np.zeros(k), x[:len(x) - k]]) if k else x


def results():
    t, eeg, acc, dz, art = filtered()
    d = eeg + art
    out = {}
    for name, refs in (("accelerometer", [acc]), ("impedance", [dz]), ("both", [acc, dz])):
        e = nlms(d, refs)
        res = e - eeg
        sel = t > 5                                                         # after convergence
        out[name] = (e, 10 * np.log10(np.mean(art[sel] ** 2) / np.mean(res[sel] ** 2)))
    return t, eeg, art, d, out


def fig():
    t, eeg, art, d, out = results()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2, gridspec_kw={"width_ratios": [2.2, 1]})
    k = (t > 6) & (t < 24)
    a1.plot(t[k], art[k] * 1e6, color=GRAPHITE, lw=0.7, alpha=0.6, label="artefact in the recording")
    a1.plot(t[k], (out["both"][0] - eeg)[k] * 1e6, color=C1, lw=0.8, label="left after NLMS, both references")
    finish(a1, xlabel="Time (s)", ylabel="Error against the clean EEG (µV)", legend=True, loc="upper left")
    a1.legend(loc="lower left", fontsize=6.3, ncol=2)
    panel(a1, "a")
    names = ["accelerometer", "impedance", "both"]
    vals = [out[n][1] for n in names]
    a2.bar(range(3), vals, color=[C3, C2, C1], width=0.6)
    for i, v in enumerate(vals):
        a2.text(i, v + 0.4, f"{v:.1f}", ha="center", fontsize=6.8)
    a2.set_xticks(range(3)); a2.set_xticklabels(["accel.", "impedance", "both"], fontsize=7)
    finish(a2, ylabel="Artefact reduced by (dB)")
    panel(a2, "b")
    savefig(fig, "ch31_nlms")
    return {n: round(out[n][1], 1) for n in names}


def ls_ceiling(taps=8):
    """Least-squares FIR fit of the recording from both references over the whole minute: the most any
    canceller with these taps can remove."""
    t, eeg, acc, dz, art = filtered()
    d = eeg + art
    cols = []
    for r in (acc, dz):
        r = (r - r.mean()) / r.std()
        cols += [delay(r, k) for k in range(taps)]
    X = np.array(cols).T
    sel = t > 5
    w = np.linalg.lstsq(X[sel], d[sel], rcond=None)[0]
    return reduction(art, d - X @ w - eeg, sel)


def mu_sweep():
    """Both references, 8 taps each: artefact removed over the minute (after 5 s), on the first walk and on the
    last, for each step size; and the reduction in 2 s windows inside the walks (Figure 31.2a)."""
    t, eeg, acc, dz, art = filtered()
    d = eeg + art
    table, curves = {}, {}
    for mu in MUS:
        res = nlms(d, [acc, dz], mu=mu) - eeg
        table[mu] = (reduction(art, res, t > 5),
                     reduction(art, res, (t >= BURSTS[0][0]) & (t < BURSTS[0][1])),
                     reduction(art, res, (t >= BURSTS[2][0]) & (t < BURSTS[2][1])))
        tc, rc = [], []
        for s0, s1 in BURSTS:
            for c in np.arange(s0 + 1, s1 - 0.99, 0.5):
                tc.append(c); rc.append(reduction(art, res, (t >= c - 1) & (t < c + 1)))
            tc.append(np.nan); rc.append(np.nan)                   # break the line between walks
        curves[mu] = (np.array(tc), np.array(rc))
    return table, curves


def effective_step(mu=0.01, taps=8):
    """The key equation's numbers for the scene: the references (unit power over the minute) carry most of their
    power during the walks, so x'x there exceeds delta = one per tap, and the effective step is mu*x'x/(delta+x'x)."""
    t, eeg, acc, dz, art = filtered()
    moving = np.zeros(len(t), bool)
    for s0, s1 in BURSTS:
        moving |= (t >= s0) & (t < s1)
    refs = [(r - r.mean()) / r.std() for r in (acc, dz)]
    L = taps * len(refs)
    xx = taps * sum(np.mean(r[moving] ** 2) for r in refs)
    mu_eff = mu * xx / (L + xx)
    return dict(L=L, power_per_tap=xx / L, xx=xx, mu_eff=mu_eff, tau_samples=L / (2 * mu_eff),
                tau_s=L / (2 * mu_eff) / FS, M=mu_eff / (2 - mu_eff))


LAGS = np.arange(0, 33, 2)          # samples at 256 S/s: 0 to 125 ms


def lag_sweep():
    """Both references when the impedance trace arrives late: as it is, and with the recording and the
    accelerometer delayed by the same amount so all three streams line up (Figure 31.2b). Also the impedance
    trace through a second-order Butterworth output low-pass (10 Hz, as in Chapter 28's readout, and 2 Hz)."""
    t, eeg, acc, dz, art = filtered()
    sel = t > 5

    def run(z, k_align=0, refs="both"):
        e0, a0, ac = delay(eeg, k_align), delay(art, k_align), delay(acc, k_align)
        rr = [ac, z] if refs == "both" else [z]
        return reduction(a0, nlms(e0 + a0, rr) - e0, sel)

    late = np.array([run(delay(dz, int(k))) for k in LAGS])
    aligned = np.array([run(delay(dz, int(k)), int(k)) for k in LAGS[::4]])
    lpf = {}
    for fc in (10, 2):
        b = sps.butter(2, fc, fs=FS)
        z = sps.lfilter(*b, dz)
        gd = float(sps.group_delay(b, w=[1.8], fs=FS)[1][0])      # samples, at the walking rhythm
        k = int(round(gd))
        lpf[fc] = dict(delay_samples=gd, delay_ms=gd / FS * 1e3, both=run(z), imp=run(z, refs="imp"),
                       aligned=run(z, k))
        # impedance alone with only the recording delayed (no accelerometer to misalign)
        e0, a0 = delay(eeg, k), delay(art, k)
        lpf[fc]["imp_aligned"] = reduction(a0, nlms(e0 + a0, [z]) - e0, sel)
        # both references, but only the recording delayed: the accelerometer is now early
        lpf[fc]["both_recording_only"] = reduction(a0, nlms(e0 + a0, [acc, z]) - e0, sel)
    return late, aligned, lpf


def quality_bits():
    """Worked Example 31.4: the quality record of section 31.4 for eight channels, against Chapter 27's streams."""
    ch, win = 8, 0.25                         # channels, window (s)
    flags = ch * (2 + 3) / win                # 2-bit class + lead-off, saturation and servo-step flags
    imp = ch * 2 * 12 / 1.0                   # |Z| and phase at 12 bits, once per second
    q = flags + imp
    raw_eeg = ch * 256 * 16                   # Chapter 27: 256 S/s, 16 bits
    bands = ch * 6 * 16 / 2.0                 # Chapter 27: six band powers per 2 s window and channel
    still = ch * 2 / win                      # only the class, when nothing changes
    return dict(flags=flags, imp=imp, total=q, raw_eeg=raw_eeg, share_raw=q / raw_eeg, bands=bands,
                share_bands=q / bands, power_uW=q * 5e-9 * 1e6, still=still)


def fig2():
    table, curves = mu_sweep()
    late, aligned, lpf = lag_sweep()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2, gridspec_kw={"width_ratios": [1.45, 1]})
    for s0, s1 in BURSTS:
        a1.axvspan(s0, s1, color=GRAPHITE, alpha=0.06, lw=0)
    for mu, col in ((0.003, C2), (0.01, C1), (0.1, C4)):
        tc, rc = curves[mu]
        a1.plot(tc, rc, color=col, lw=1.2, label=f"μ = {mu:g}")
    a1.set_ylim(-8, 20); a1.set_xlim(6, 56)
    a1.text(14, 18.2, "walk 1", ha="center", fontsize=6.5, color=GRAPHITE)
    a1.text(34, 18.2, "walk 2", ha="center", fontsize=6.5, color=GRAPHITE)
    a1.text(50, 18.2, "walk 3", ha="center", fontsize=6.5, color=GRAPHITE)
    finish(a1, xlabel="Time (s), 2 s windows", ylabel="Artefact reduced by (dB)")
    a1.legend(loc="lower center", fontsize=6.3, ncol=3, frameon=False)
    panel(a1, "a")
    ms = LAGS / FS * 1e3
    a2.plot(ms, late, color=C4, lw=1.2, marker="o", ms=2.5, label="trace late")
    a2.plot(ms[::4], aligned, color=C1, lw=1.2, marker="s", ms=2.5, label="all streams lined up")
    for fc, m in ((10, "^"), (2, "v")):
        a2.plot(lpf[fc]["delay_ms"], lpf[fc]["both"], m, color=C2, ms=4)
        a2.annotate(f"{fc} Hz output filter", (lpf[fc]["delay_ms"], lpf[fc]["both"]),
                    xytext=(lpf[fc]["delay_ms"] + (6 if fc == 10 else -4), lpf[fc]["both"] - 1.6),
                    fontsize=6, color=C2, ha="left" if fc == 10 else "right")
    a2.set_ylim(4, 14)
    finish(a2, xlabel="Lag of the impedance trace (ms)", ylabel="Artefact reduced by (dB)")
    a2.legend(loc="upper right", fontsize=6.3, frameon=False)
    panel(a2, "b")
    savefig(fig, "ch31_learning")


def report():
    print("Figure 31.1 (accelerometer, impedance, both):", fig_numbers())
    print("least-squares ceiling, both references, 8 taps: %.1f dB; 32 taps: %.1f dB" % (ls_ceiling(8), ls_ceiling(32)))
    t, eeg, acc, dz, art = filtered()
    print("EEG %.1f uVrms, artefact %.1f uVrms over the minute (0.5-40 Hz)" % (eeg.std() * 1e6, art.std() * 1e6))
    table, curves = mu_sweep()
    for mu in MUS:
        print("mu %-6g minute %.1f dB, first walk %.1f dB, last walk %.1f dB" % ((mu,) + table[mu]))
    for mu in (0.01, 0.003, 0.1):
        tc, rc = curves[mu]
        first = [(round(a, 1), round(b, 1)) for a, b in zip(tc, rc) if 8 < a < 20]
        print("mu %g, 2 s windows in walk 1 (centre s, dB):" % mu, first)
    for mu in (0.003, 0.01, 0.1):
        e = effective_step(mu)
        print("mu %g: L %d, power per tap while moving %.2f, x'x %.1f, mu_eff %.4f, tau %.0f samples = %.1f s, M %.4f"
              % (mu, e["L"], e["power_per_tap"], e["xx"], e["mu_eff"], e["tau_samples"], e["tau_s"], e["M"]))
    late, aligned, lpf = lag_sweep()
    print("lag (ms):", [round(x, 1) for x in LAGS / FS * 1e3])
    print("both refs, trace late (dB):", [round(x, 1) for x in late])
    print("both refs, aligned (dB) at lags", [round(x, 1) for x in LAGS[::4] / FS * 1e3], [round(x, 1) for x in aligned])
    for fc, v in lpf.items():
        print("%d Hz output filter: delay %.1f samples = %.0f ms; both %.1f dB, aligned %.1f dB; impedance alone %.1f dB, "
              "recording delayed %.1f dB; both with only the recording delayed %.1f dB"
              % (fc, v["delay_samples"], v["delay_ms"], v["both"], v["aligned"], v["imp"], v["imp_aligned"],
                 v["both_recording_only"]))
    q = quality_bits()
    print("quality record: flags %.0f b/s + impedance %.0f b/s = %.0f b/s; %.1f %% of raw EEG (%d b/s); %.0f %% of band "
          "powers (%.0f b/s); %.2f uW at 5 nJ/b; class only %.0f b/s" % (q["flags"], q["imp"], q["total"],
          100 * q["share_raw"], q["raw_eeg"], 100 * q["share_bands"], q["bands"], q["power_uW"], q["still"]))
    print("MAC/s for 8 channels, 16 taps, 500 S/s: %d per filter pass" % (8 * 16 * 500))


def fig_numbers():
    t, eeg, art, d, out = results()
    return {n: round(out[n][1], 1) for n in ("accelerometer", "impedance", "both")}


if __name__ == "__main__":
    print(fig())
    fig2()
    report()
