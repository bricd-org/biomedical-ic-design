"""ch24_figs.py -- Chapter 24 figure: a Pan-Tompkins QRS detector on a synthetic ECG through a behavioural
front-end and ADC, and its sensitivity versus ADC bits for several input noise levels."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs
from scipy import signal as sps

FS = 500.0
FS_IN = 5e-3            # +-5 mV at the electrodes fills the converter (gain 100 into +-0.5 V)


def pan_tompkins(x, fs=FS):
    """Simplified Pan-Tompkins: 5-15 Hz band-pass, derivative, squaring, 150 ms integration, adaptive
    threshold with a 200 ms refractory period. Returns detected R times (s) and the stages."""
    sos = sps.butter(2, [5 / (fs / 2), 15 / (fs / 2)], "band", output="sos")
    bp = sps.sosfilt(sos, x)
    d = np.convolve(bp, np.array([1, 2, 0, -2, -1]) * fs / 8, mode="same")
    sq = d ** 2
    w = int(0.15 * fs)
    mwi = np.convolve(sq, np.ones(w) / w, mode="same")
    pk, _ = sps.find_peaks(mwi, distance=int(0.2 * fs))
    spki, npki = np.max(mwi[: int(2 * fs)]) * 0.5, np.mean(mwi[: int(2 * fs)]) * 0.5
    det = []
    for p in pk:
        thr = npki + 0.25 * (spki - npki)
        if mwi[p] > thr:
            det.append(p); spki = 0.125 * mwi[p] + 0.875 * spki
        else:
            npki = 0.125 * mwi[p] + 0.875 * npki
    det = np.array(det, dtype=int)
    # refine to the R peak in the raw signal within +-75 ms (group delay of the filters)
    r = [p - int(0.075 * fs) + np.argmax(bp[max(p - int(0.075 * fs), 0): p + int(0.075 * fs)]) for p in det]
    return np.array(r) / fs, (bp, mwi)


def score(det, truth, tol=0.075):
    det = det[(det > truth.min() - 0.3) & (det < truth.max() + 0.3)]      # same window as the truth
    tp = sum(np.any(np.abs(det - t) < tol) for t in truth)
    fp = len(det) - sum(np.any(np.abs(truth - d) < tol) for d in det)
    return tp / len(truth), tp / max(tp + fp, 1)


def chain(t, x, noise_rms, bits, seed):
    rng = np.random.default_rng(seed)
    y = x + noise_rms * rng.standard_normal(len(x)) + 200e-6 * np.sin(2 * np.pi * 0.3 * t)
    y = np.clip(y, -FS_IN, FS_IN * (1 - 2.0 ** (1 - bits)))
    return bs.code_to_volts(bs.quantize(y, bits, vfs=FS_IN) * 0 + np.floor((y + FS_IN) / (2 * FS_IN) * 2 ** bits), bits, vfs=FS_IN)


def fig():
    t, x, pk = bs.ecg(fs=FS, duration=60.0, hr=75, hrv=0.05, seed=24)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    y = chain(t, x, 50e-6, 8, 1)
    det, (bp, mwi) = pan_tompkins(y)
    sel = (t > 10) & (t < 14)
    a1.plot(t[sel], y[sel] / np.max(np.abs(y[sel])) + 2.2, color=GRAPHITE, lw=0.7, label="ECG, 8 bits, 50 µVrms noise")
    a1.plot(t[sel], bp[sel] / np.max(np.abs(bp[sel])) + 1.0, color=C2, lw=0.7, label="band-pass 5–15 Hz")
    a1.plot(t[sel], mwi[sel] / np.max(mwi[sel]) - 0.4, color=C1, lw=0.9, label="moving-window integral")
    for d in det[(det > 10) & (det < 14)]:
        a1.axvline(d, color=C3, lw=0.8, ls=":")
    a1.set_xlim(10, 14); a1.set_yticks([])
    finish(a1, xlabel="Time (s)", ylabel="Stages (normalised, offset)", legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=5.8)
    panel(a1, "a")
    bits = np.arange(3, 13)
    res = {}
    for nz, c in ((10e-6, C3), (50e-6, C1), (100e-6, C2), (200e-6, C4)):
        se = []
        for b in bits:
            vals = [score(pan_tompkins(chain(t, x, nz, b, s))[0], pk[(pk > 2) & (pk < 58)])[0] for s in range(3)]
            se.append(np.mean(vals) * 100)
        res[nz] = se
        a2.plot(bits, se, "o-", color=c, ms=3, label=f"{nz*1e6:g} µVrms input noise")
    a2.axhline(99, color=AMBER, ls="--", lw=0.8)
    a2.text(3.1, 99.3, "99 %", fontsize=6.5, color=AMBERDK)
    a2.set_xlim(2.5, 12.5); a2.set_ylim(60, 101)
    finish(a2, xlabel="ADC bits (±5 mV input range)", ylabel="QRS sensitivity (%)", legend=True, loc="lower right")
    a2.legend(loc="lower right", fontsize=6.0)
    panel(a2, "b")
    savefig(fig, "ch24_qrs")
    return bits, res


if __name__ == "__main__":
    bits, res = fig()
    for k, v in res.items():
        print("noise %.0f uV:" % (k * 1e6), " ".join("%d:%.1f" % (b, s) for b, s in zip(bits, v)))
    t, x, pk = bs.ecg(fs=FS, duration=60.0, hr=75, hrv=0.05, seed=24)
    for nz, b in ((10e-6, 12), (100e-6, 6), (200e-6, 12)):
        se, ppv = score(pan_tompkins(chain(t, x, nz, b, 0))[0], pk[(pk > 2) & (pk < 58)])
        print("noise %g bits %d: Se %.3f PPV %.3f" % (nz, b, se, ppv))
