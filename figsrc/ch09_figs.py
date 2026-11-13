"""ch09_figs.py -- Chapter 9 figures: noise of a chopped amplifier (flicker noise moved to the chopping
frequency), ripple from the up-modulated offset in the time domain, and the chopping-frequency trade-off
between input impedance and residual flicker noise. SG13G2 numbers from Chapters 5 and 8."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

K_NMOS = 1.58e-10        # V^2 um^2
FLOOR = 18.5e-9          # one NMOS at 1 uA
F1, F2 = 0.5, 100.0
A_VT = 3.9e-3            # V um
GAIN = 100.0


def pair_psd(f, wl):
    return 2 * (K_NMOS / (wl * f) + FLOOR ** 2)


def chopped_psd(f, wl, fch, kmax=99):
    """Baseband PSD after chopping: the amplifier PSD shifted by odd harmonics of fch, weighted by the
    squared Fourier coefficients of a +-1 square wave (8/(pi^2 k^2)), summed over both sidebands."""
    s = np.zeros_like(f)
    for k in range(1, kmax + 1, 2):
        w = 8 / (np.pi ** 2 * k ** 2) / 2
        s += w * (pair_psd(np.abs(k * fch - f) + 1e-3, wl) + pair_psd(k * fch + f, wl))
    return s


def inband(fch, wl):
    f = np.linspace(F1, F2, 400)
    return np.sqrt(np.trapz(chopped_psd(f, wl, fch), f))


def fig_spectra():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    f = np.logspace(-0.5, 4.5, 800)
    wl, fch = 1000.0, 4e3
    a1.loglog(f, np.sqrt(pair_psd(f, wl)) * 1e9, color=C4, label="unchopped pair (1000 µm² each)")
    a1.loglog(f, np.sqrt(chopped_psd(f, wl, fch)) * 1e9, color=C1, label="chopped at 4 kHz")
    a1.axvspan(F1, F2, color=BTINT, lw=0)
    a1.axvline(fch, color=MUTED, ls=":", lw=0.7)
    a1.text(fch * 1.1, 900, r"$f_\mathrm{ch}$", fontsize=7, color=MUTED)
    a1.set_xlim(0.3, 3e4); a1.set_ylim(10, 2e3)
    finish(a1, xlabel="Frequency (Hz)", ylabel="Input-referred noise (nV/√Hz)", legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=6.3)
    panel(a1, "a")
    fs = 400e3
    t = np.arange(0, 0.2, 1 / fs)
    vin = 50e-6 * np.sin(2 * np.pi * 10 * t)
    vos = 0.39e-3                                      # 1 sigma offset of a 100 um^2 NMOS pair
    m = np.sign(np.sin(2 * np.pi * fch * t) + 1e-12)
    amp = GAIN * (vin * m + vos)                      # input chopper, amplifier with offset
    out = amp * m                                      # output chopper
    from scipy import signal as sps
    b, a = sps.butter(2, 200 / (fs / 2))
    filt = sps.lfilter(b, a, out)
    sel = t > 0.05
    a2.plot(t[sel] * 1e3, out[sel] * 1e3, color=PALE, lw=0.4, label="after output chopper")
    a2.plot(t[sel] * 1e3, filt[sel] * 1e3, color=C1, lw=1.3, label="after 2nd-order low-pass at 200 Hz")
    a2.plot(t[sel] * 1e3, GAIN * vin[sel] * 1e3, color=C3, lw=0.8, ls="--", label="ideal: 100 × input")
    a2.set_xlim(50, 200); a2.set_ylim(-50, 50)
    finish(a2, xlabel="Time (ms)", ylabel="Output (mV)", legend=True, loc="upper right")
    a2.legend(loc="upper right", fontsize=6.0)
    panel(a2, "b")
    savefig(fig, "ch09_chop")


def fig_tradeoff():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    fch = np.logspace(2, 5, 200)
    for cin, c in ((10e-12, C3), (20e-12, C1), (40e-12, C4)):
        a1.loglog(fch, 1 / (2 * fch * cin) / 1e6, color=c, label=rf"$C_\mathrm{{in}}$ = {cin*1e12:g} pF")
    a1.axhline(2.5, color=AMBER, ls="--", lw=0.9)
    a1.text(120, 2.8, "2.5 MΩ (ECG standards)", fontsize=6.5, color=AMBERDK)
    a1.axhline(100, color=MUTED, ls=":", lw=0.9)
    a1.text(120, 115, "100 MΩ (dry electrodes)", fontsize=6.5, color=MUTED)
    a1.set_xlim(100, 1e5); a1.set_ylim(0.1, 1e3)
    finish(a1, xlabel="Chopping frequency (Hz)", ylabel="Differential input impedance (MΩ)", legend=True,
           loc="lower left")
    a1.legend(loc="lower left", fontsize=6.3)
    panel(a1, "a")
    fchs = np.logspace(np.log10(300), 5, 60)
    for wl, c in ((100.0, C4), (1000.0, C1)):
        v = [inband(x, wl) for x in fchs]
        a2.semilogx(fchs, np.array(v) * 1e6, color=c, label=f"input devices {wl:g} µm² each")
    a2.axhline(np.sqrt(2 * FLOOR ** 2 * (F2 - F1)) * 1e6, color=MUTED, ls=":", lw=0.8)
    a2.text(320, 0.275, "thermal floor 0.26 µV", fontsize=6.5, color=MUTED, va="bottom")
    a2.axvline(4e3, color=AMBER, ls="--", lw=0.8)
    a2.text(4.3e3, 0.6, "4 kHz", fontsize=6.5, color=AMBERDK)
    a2.set_xlim(300, 1e5); a2.set_ylim(0.2, 0.8)
    finish(a2, xlabel="Chopping frequency (Hz)", ylabel="Chopped noise, 0.5–100 Hz (µVrms)", legend=True,
           loc="upper right")
    a2.legend(loc="upper right", fontsize=6.3)
    panel(a2, "b")
    savefig(fig, "ch09_tradeoff")


if __name__ == "__main__":
    for wl in (100.0, 1000.0):
        fc = K_NMOS / wl / FLOOR ** 2
        print("WL %g: 1/f corner %.0f Hz; offset sigma %.3f mV; in-band chopped noise at 1/2/4/10 kHz:" % (wl, fc, A_VT / np.sqrt(wl) * 1e3 * np.sqrt(2) / np.sqrt(2)),
              [round(inband(x, wl) * 1e6, 3) for x in (1e3, 2e3, 4e3, 10e3)])
    for x in (1e3, 4e3, 10e3):
        print("fch %g: Zin(20pF) %.2f MOhm" % (x, 1 / (2 * x * 20e-12) / 1e6))
    print("residual offset 2 fch dq Rs, dq=1fC, fch=4k: wet 50k %.2f uV, dry 1M %.2f uV" % (2 * 4e3 * 1e-15 * 50e3 * 1e6, 2 * 4e3 * 1e-15 * 1e6 * 1e6))
    print("ripple: 100 x 0.39 mV = %.0f mV; after 2nd-order LPF at 200 Hz: x1/%.0f" % (100 * 0.39, (4e3 / 200) ** 2))
    fig_spectra()
    fig_tradeoff()
