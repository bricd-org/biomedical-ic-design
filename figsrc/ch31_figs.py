"""ch31_figs.py -- Chapter 31 figure: adaptive cancellation of a motion artefact with an impedance reference,
an accelerometer reference or both (NLMS), on a synthetic EEG. The artefact model: part follows the electrode
impedance change (lead-off current and common-mode conversion through the changing interface), part follows
head acceleration directly, and a small part follows neither."""
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


def results():
    t, eeg, acc, dz, art = scene()
    # the recording chain keeps 0.5-40 Hz (servo and decimation filters); the references get the same filter,
    # so that the offset of the artefact, which no recording keeps, does not count
    bp = sps.butter(2, [0.5, 40], "band", fs=FS)
    eeg, acc, dz, art = (sps.lfilter(*bp, x) for x in (eeg, acc, dz, art))
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


if __name__ == "__main__":
    print(fig())
