"""ch28_figs.py -- Chapter 28 figure: a Cole tissue model against what a two-electrode measurement sees
with wet and dry electrodes in series (tetrapolar removes them), and the impedance resolution versus
excitation current for three readout noise levels, with the patient-current limit at 50 kHz."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

R0, RINF, FC, ALPHA = 60.0, 30.0, 30e3, 0.7      # illustrative thoracic segment


def cole(f):
    return RINF + (R0 - RINF) / (1 + (1j * f / FC) ** ALPHA)


def fig():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    f = np.logspace(2, 6.3, 300)
    zt = cole(f)
    a1.loglog(f, np.abs(zt), color=C1, lw=1.6, label="tissue (Cole), = tetrapolar reading")
    for kind, c in (("wet Ag/AgCl", C3), ("dry", C4)):
        zb = zt + 2 * bs.z_electrode(f, kind)
        a1.loglog(f, np.abs(zb), color=c, label=f"bipolar reading, {kind} electrodes")
    a1.axvline(50e3, color=MUTED, ls=":", lw=0.8)
    a1.text(55e3, 2e5, "50 kHz", fontsize=6.5, color=MUTED)
    a1.set_xlim(100, 2e6); a1.set_ylim(10, 1e7)
    finish(a1, xlabel="Frequency (Hz)", ylabel="|Z| (Ω)", legend=True, loc="upper right")
    a1.legend(loc="upper right", fontsize=6.0)
    panel(a1, "a")
    i = np.logspace(-7, -3, 200)
    bw = 10.0
    for vn, c in ((20e-9, C3), (50e-9, C1), (200e-9, C4)):
        a2.loglog(i * 1e6, vn * np.sqrt(bw) / i * 1e3, color=c, label=f"readout {vn*1e9:g} nV/√Hz")
    lim = bs.patient_current_limit(50e3, "CF")
    a2.axvline(lim * 1e6, color=AMBER, ls="--", lw=0.9)
    a2.text(lim * 1e6 * 0.85, 300, f"CF limit at 50 kHz\n{lim*1e6:.0f} µA", fontsize=6.3, color=AMBERDK, ha="right")
    a2.axhline(10, color=MUTED, ls=":", lw=0.8)
    a2.text(0.12, 12, "10 mΩ", fontsize=6.3, color=MUTED)
    a2.set_xlim(0.1, 1000); a2.set_ylim(1e-3, 1e3)
    finish(a2, xlabel="Excitation current (µA rms)", ylabel="ΔZ resolution in 10 Hz (mΩ rms)", legend=True, loc="lower left")
    a2.legend(loc="lower left", fontsize=6.0)
    panel(a2, "b")
    savefig(fig, "ch28_bioz")


if __name__ == "__main__":
    for f0 in (1e3, 10e3, 50e3, 100e3):
        zt = cole(f0); print("f %g: tissue %.1f ohm %.1f deg; +2 wet %.0f ohm; +2 dry %.0f ohm" % (f0, abs(zt), np.degrees(np.angle(zt)), abs(zt + 2 * bs.z_electrode(f0, "wet Ag/AgCl")), abs(zt + 2 * bs.z_electrode(f0, "dry"))))
    print("CF limit 50 kHz: %.0f uA" % (bs.patient_current_limit(50e3, "CF") * 1e6))
    for i in (10e-6, 50e-6):
        print("I %g: res %.2f mOhm (50 nV/rtHz, 10 Hz); signal for 1 ohm: %.0f uV" % (i, 50e-9 * np.sqrt(10) / i * 1e3, i * 1e6))
    print("3rd harmonic weight of square-wave demod: %.3f" % (1 / 3))
    fig()
