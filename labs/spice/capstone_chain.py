"""capstone_chain.py -- a reference run for the capstone: real ECG and EEG through one Open-BioAFE channel.

    .venv/bin/python labs/spice/capstone_chain.py               # corners + real signals, 5 runs in parallel
    .venv/bin/python labs/spice/capstone_chain.py --parse-only  # re-analyse the last run

1. Corners. The chopped CCIA of Lab 5 (SG13G2 transmission-gate choppers at 4 kHz, Cin = 20 pF,
   Cfb = 200 fF, DC servo through 4 pF, behavioural OTA) at the tt, ss and ff MOS corners: gain at
   37 Hz, residual output offset, chopper ripple and input impedance, with the 300 mV electrode offset.
2. Real signals. The same LNA (tt) driven by ngspice PWL sources: 3 s of MIT-BIH record 100 (ECG)
   and 2 s of CHB-MIT chb01_03, FP1-F7, from the seizure onset at 2996 s (EEG), each on top of the
   300 mV offset. Python then applies the PGA (x1 for ECG, x8 for EEG), decimates to 500 S/s and
   quantises to 16 bits over +-0.5 V (the incremental-DS path of Chapter 20), and compares the result
   with the input filtered the same way: gain, error and SNR over 0.5-40 Hz, and, for the ECG, the R
   peaks that Lab 11's Pan-Tompkins detector finds.
Needs Docker, hpretl/iic-osic-tools:2026.10, wfdb and the local PhysioNet copies of the set-up
(data/physionet/). Outputs go to labs/spice/out/ (git-ignored).
"""
import argparse
import os
import re
import sys

import numpy as np
from scipy import signal as sps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "python"))
import biosig  # noqa: E402
import lab5_chopper as L5  # noqa: E402
import sg13_char as ch  # noqa: E402

VOFF = 0.3
T0 = 0.3                       # discard the servo's settling (2 Hz high-pass in the lab netlist)
FS_OUT = 500.0


def pwl_lines(name, node, t, v):
    pts = [f"{a:.6g} {b:.7g}" for a, b in zip(t, v)]
    rows = [" ".join(pts[i:i + 8]) for i in range(0, len(pts), 8)]
    return f"{name} {node} 0 pwl(" + rows[0] + "\n" + "\n".join("+ " + r for r in rows[1:]) + ")"


def real_netlist(tag, t, x, tsim):
    """Lab 5's chopped netlist with the test tone replaced by a recorded signal x(t) in volts."""
    L5.T_SIM = tsim
    nl = L5.netlist(True, VOFF, tag)
    vp = L5.VCM + VOFF / 2 + x / 2
    vn = L5.VCM - VOFF / 2 - x / 2
    nl = re.sub(r"^Vep .*$", pwl_lines("Vep", "ep", t, vp), nl, flags=re.M)
    nl = re.sub(r"^Ven .*$", pwl_lines("Ven", "en", t, vn), nl, flags=re.M)
    return nl


def load_ecg(seconds):
    import wfdb
    name, pdir = biosig.physionet_source("mitdb", "100")
    n = int(seconds * 360)
    rec = wfdb.rdrecord(name, pn_dir=pdir, sampto=n)
    ann = wfdb.rdann(name, "atr", pn_dir=pdir, sampto=n)
    beats = np.array([s for s, c in zip(ann.sample, ann.symbol) if c in "NLRBAaJSVrFejnE/fQ?"]) / rec.fs
    return np.arange(n) / rec.fs, rec.p_signal[:, 0] * 1e-3, beats


def load_eeg(seconds, start=2996.0):
    rec = biosig.read_edf_record(os.path.join(biosig.DATA_DIR, "chbmit", "chb01_03.edf"))
    k = rec.sig_name.index("FP1-F7") if "FP1-F7" in rec.sig_name else 0
    fs = float(rec.fs)
    scale = {"uv": 1e-6, "mv": 1e-3}.get(str(rec.units[k]).lower(), 1.0)
    i0 = int(start * fs)
    x = rec.p_signal[i0:i0 + int(seconds * fs), k] * scale
    return np.arange(len(x)) / fs, x - np.mean(x)


def band(y, fs):
    """The comparison band: 0.5-40 Hz (zero-phase, so that delays do not count as error)."""
    sos = sps.butter(2, [0.5, 40], "band", fs=fs, output="sos")
    return sps.sosfiltfilt(sos, y)


def chain(tag, t_in, x_in, g_pga, seconds):
    """Output of the SPICE LNA through PGA, decimation and a 16-bit quantiser, against the input."""
    t, vy, ie, vd, vf = ch.load(tag, 4)
    fs1 = 16e3
    tu = np.arange(T0, seconds, 1 / fs1)
    y = np.interp(tu, t, vf) * g_pga
    y = sps.decimate(sps.decimate(y, 4, ftype="fir"), 8, ftype="fir")       # 16 kHz -> 500 S/s
    y = biosig.quantize(y, 16, 0.5)
    to = T0 + np.arange(len(y)) / FS_OUT
    ref = np.interp(to, t_in, x_in)
    yb, rb = band(y, FS_OUT), band(ref, FS_OUT)
    trim = slice(int(0.25 * FS_OUT), -int(0.25 * FS_OUT))                  # filter edges
    yb, rb = yb[trim], rb[trim]
    g = float(np.dot(yb, rb) / np.dot(rb, rb))
    err = yb - g * rb
    snr = 20 * np.log10(np.std(g * rb) / np.std(err))
    return dict(t=to, y=y, ref=ref, g=g, snr=snr, err_in=np.std(err) / g, sig_in=np.std(rb))


def main():
    ap = argparse.ArgumentParser(description="Capstone reference run")
    ap.add_argument("--parse-only", action="store_true")
    a = ap.parse_args()
    T_ECG, T_EEG = 3.0, 2.0
    te, xe, beats = load_ecg(T_ECG)
    tg, xg = load_eeg(T_EEG)
    nl = {}
    for corner in ("tt", "ss", "ff"):
        L5.T_SIM = 0.4
        nl[f"cap_{corner}"] = L5.netlist(True, VOFF, f"cap_{corner}").replace("mos_tt", f"mos_{corner}")
    nl["cap_ecg"] = real_netlist("cap_ecg", te, xe, T_ECG)
    nl["cap_eeg"] = real_netlist("cap_eeg", tg, xg, T_EEG)
    if not a.parse_only:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(len(nl)) as ex:
            list(ex.map(lambda kv: ch.run({kv[0]: kv[1]}), nl.items()))
    print(f"1. Chopped LNA at three corners (electrode offset {VOFF*1e3:.0f} mV, 1 mV test tone at {L5.F_SIG:g} Hz):")
    print("   corner   gain   offset (mV)   ripple (mV)   Zin (MOhm)")
    for corner in ("tt", "ss", "ff"):
        r = L5.analyse(f"cap_{corner}")
        print(f"   {corner:6s} {r['gain']:6.1f}   {r['offset']*1e3:9.2f}   {r['ripple']*1e3:10.2f}   "
              f"{abs(VOFF / r['i_avg'])/1e6:9.2f}")
    e = chain("cap_ecg", te, xe, 1.0, T_ECG)
    g = chain("cap_eeg", tg, xg, 8.0, T_EEG)
    import lab11_ecg_chain as L11
    pk = L11.pan_tompkins(e["y"] / e["g"], FS_OUT) + T0
    tb = beats[(beats > T0 + 0.3) & (beats < T_ECG - 0.3)]
    pk = pk[(pk > T0 + 0.3) & (pk < T_ECG - 0.3)]
    found = sum(np.any(np.abs(pk - b) < 0.075) for b in tb)
    print("2. Real signals through the LNA (tt), PGA, decimation to 500 S/s and 16 bits; 0.5-40 Hz band:")
    print(f"   ECG, MIT-BIH 100, 3 s: chain gain {e['g']:.1f} (LNA x PGA x1), SNR {e['snr']:.1f} dB, "
          f"error {e['err_in']*1e6:.1f} µVrms referred to the input; R peaks found {found} of {len(tb)}, "
          f"extra detections {len(pk) - found}")
    print(f"   EEG, CHB-MIT chb01_03 FP1-F7 at 2996 s, 2 s: chain gain {g['g']:.0f} (LNA x PGA x8), "
          f"SNR {g['snr']:.1f} dB, error {g['err_in']*1e6:.2f} µVrms for a {g['sig_in']*1e6:.1f} µVrms signal")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        sys.path.insert(0, os.path.join(HERE, "..", "..", "figsrc"))
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8), constrained_layout=True)
        for ax, d, sc, lab in ((a1, e, 1e3, "ECG (mV)"), (a2, g, 1e6, "EEG (µV)")):
            k = d["t"] > T0 + 0.25
            ax.plot(d["t"][k], band(d["ref"], FS_OUT)[k] * sc, color="0.6", lw=2.2, label="input, 0.5–40 Hz")
            ax.plot(d["t"][k], band(d["y"], FS_OUT)[k] / d["g"] * sc, lw=0.9, label="chain output / gain")
            ax.set(xlabel="time (s)", ylabel=lab)
            ax.legend(fontsize=8, loc="upper right")
        a1.set_title(f"(a) MIT-BIH 100 through the chopped LNA: SNR {e['snr']:.0f} dB", fontsize=10)
        a2.set_title(f"(b) CHB-MIT seizure onset: SNR {g['snr']:.0f} dB", fontsize=10)
        os.makedirs(L5.PLOTS, exist_ok=True)
        fig.savefig(os.path.join(L5.PLOTS, "capstone.png"), dpi=130)
        np.savez(os.path.join(L5.PLOTS, "capstone.npz"), te=e["t"], ye=e["y"] / e["g"], re=e["ref"],
                 tg=g["t"], yg=g["y"] / g["g"], rg=g["ref"], snr_e=e["snr"], snr_g=g["snr"])
        print("wrote", os.path.join(L5.PLOTS, "capstone.png"))
    except ImportError:
        pass


if __name__ == "__main__":
    main()
