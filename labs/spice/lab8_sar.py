"""lab8_sar.py -- Lab 8: the Open-BioAFE SAR converter (Chapters 15, 17, 18).

    python labs/spice/lab8_sar.py               # both parts
    python labs/spice/lab8_sar.py --part b      # the behavioural converter only (no Docker)

Part A (ngspice, SG13G2): the sampling front-end. One side of the differential input,
0.6 V +- 0.25 V, is sampled onto 4 pF at 16 kS/s by (1) a plain 2/0.13 um NMOS switch driven to
1.2 V and (2) the same NMOS bootstrapped as in Figure 15.1b (ideal steering switches, a 200 fF
bootstrap capacitor). The held samples of a coherent 1.625 kHz tone are analysed with adctest.py:
the plain switch's charge injection depends on the input, the bootstrapped switch's does not.

Part B (Python): the converter of Chapter 18 -- 14 decisions with radix-1.8 weights built from
unit MIM capacitors of about 1 fF (sigma_u = 1.22 %, from the PDK's 1 %.um matching), the
differential kT/C noise of 4 pF per side, and a comparator with 61 uV of noise in its last three
(low-noise) decisions and 0.6 mV in the others (Lab 7). Weights are read either as designed or
after a foreground calibration that measures them. Reported: ENOB, DNL/INL and the Walden figure
of merit with the 7.6 pJ per conversion of Chapter 18.
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "python"))
import adctest  # noqa: E402
import biosig  # noqa: E402

PLOTS = os.path.join(HERE, "out")
FS, NS, M_TONE = 16e3, 256, 13                 # 256 coherent samples, tone in bin 13 (812.5 Hz)
VCM, AMP, CS = 0.6, 0.25, 4e-12


# ---------------------------------------------------------------- Part A: the sampler in ngspice
def sampler_netlist(boot, tag):
    ts = 1 / FS
    fin = M_TONE * FS / NS
    trk = 0.5 * ts
    clk = f"Vphi phi 0 pulse(0 1.2 0 2n 2n {trk} {ts})"                 # track while phi is high
    if boot:
        sw = f"""* bootstrapped: hold -> CB charges to VDD and the gate is grounded; track -> CB between vin and gate
.model swm sw vt=0.6 vh=0.05 ron=200 roff=1e13
Bphb phb 0 v = 1.2 - v(phi)
S1 vdd cbt phb 0 swm
S2 cbb 0 phb 0 swm
S5 gate 0 phb 0 swm
S3 cbt gate phi 0 swm
S4 cbb vin phi 0 swm
CB cbt cbb 200f
XMS vin gate cs 0 sg13_lv_nmos w=2u l=0.13u ng=1 m=1"""
    else:
        sw = "XMS vin phi cs 0 sg13_lv_nmos w=2u l=0.13u ng=1 m=1"
    return f"""* Lab 8 sampler, bootstrapped = {boot}
.lib cornerMOSlv.lib mos_tt
Vdd vdd 0 1.2
Vin vin 0 dc {VCM} sin({VCM} {AMP} {fin})
{clk}
{sw}
Cs cs 0 {CS}
.control
tran 20n {(NS + 4) * ts} 0 200n
wrdata /work/out/{tag}.txt v(cs)
.endc
.end
"""


def part_a():
    import sg13_char as ch
    nl = {"lab8_plain": sampler_netlist(False, "lab8_plain"), "lab8_boot": sampler_netlist(True, "lab8_boot")}
    ch.run(nl)
    ts = 1 / FS
    out = {}
    for k in nl:
        t, v = ch.load(k, 1)
        tk = (np.arange(NS) + 4) * ts + 0.75 * ts            # middle of each hold phase
        held = np.interp(tk, t, v) - VCM
        met = adctest.sine_test(held, M_TONE)
        out[k] = (met, held)
    print("Part A: held samples of a 0.6 V +- 0.25 V tone on 4 pF at 16 kS/s")
    for k, lab in (("lab8_plain", "plain NMOS switch"), ("lab8_boot", "bootstrapped switch")):
        m = out[k][0]
        print(f"   {lab:>20}: SFDR {m['sfdr']:5.1f} dB, THD {m['thd']:6.1f} dB, SNDR {m['sndr']:5.1f} dB")
    return out


# ---------------------------------------------------------------- Part B: the behavioural converter
NB, NCYC, RADIX = 12, 14, 1.8
SIGMA_U = 0.0122
SIG_LN, SIG_FAST, N_LN = 61e-6, 0.6e-3, 3
VFS = 0.5                                      # +-0.5 V differential range
KT_C = np.sqrt(2 * biosig.K_B * biosig.T_ROOM / CS)


def design_weights():
    """Integer radix-1.8 weights in units. Each weight is at most one more than the sum of the weights
    below it, so every decision has non-negative redundancy (no missing codes); the scale is chosen so
    that the weights cover the 2^12-LSB range with about 2 % to spare."""
    def build(scale):
        w = [1.0]
        for k in range(1, NCYC):
            w.append(min(round(RADIX ** k * scale), sum(w) + 1))
        return np.array(w)
    lo, hi = 0.1, 10.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if build(mid).sum() < 1.02 * 2 ** NB else (lo, mid)
    return build(hi)


def convert(x, w_real, w_read, rng, n_ln=N_LN):
    """SAR with real (mismatched) weights deciding and read weights summing. The comparator adds
    SIG_FAST of noise to every decision except the last n_ln, which use the low-noise mode."""
    u = (x + VFS) / (2 * VFS) * 2 ** NB + KT_C / (2 * VFS) * 2 ** NB * rng.standard_normal(x.shape)
    acc = np.zeros_like(u)
    code = np.zeros_like(u)
    lsb = 2 * VFS / 2 ** NB
    for k in range(NCYC - 1, -1, -1):
        sig = (SIG_LN if k < n_ln else SIG_FAST) / lsb
        keep = u + sig * rng.standard_normal(u.shape) >= acc + w_real[k]
        acc = np.where(keep, acc + w_real[k], acc)
        code = code + keep * w_read[k]
    return code


def real_weights(w0, seed):
    r = np.random.default_rng(seed)
    units = [r.normal(1.0, SIGMA_U, int(wk)).sum() for wk in w0]
    return np.array(units) / np.sum(units) * w0.sum()


E_LN, E_FAST, E_REST = 1.06e-12, 0.08e-12, 3.7e-12   # Lab 7 comparator modes; DAC, logic, sampler (Ch 18)


def part_b(seeds=20):
    w0 = design_weights()
    rng = np.random.default_rng(18)
    n, fin_bin = 4096, 1601
    x = 0.98 * VFS * np.sin(2 * np.pi * fin_bin * np.arange(n) / n)
    print("Part B: behavioural 12-bit SAR, 14 cycles at radix 1.8, sigma_u = 1.22 %, kT/C on 4 pF")
    print(f"   weights (units): {' '.join(str(int(v)) for v in w0)}")
    red = [int(w0[:k].sum() - w0[k] + 1) for k in range(NCYC)]
    print(f"   redundancy per decision (LSB): {' '.join(str(v) for v in red)}")
    print(f"   kT/C noise {KT_C*1e6:.0f} µVrms differential; comparator {SIG_LN*1e6:.0f} µV low-noise, {SIG_FAST*1e3:.1f} mV fast")
    print("   low-noise decisions   median ENOB (designed / calibrated weights)   energy per conversion   Walden FoM")
    sweep = {}
    for n_ln in (3, 5, 7, NCYC):
        res = {"designed": [], "calibrated": []}
        for sd in range(seeds):
            w_real = real_weights(w0, 100 + sd)
            for lab, w_read in (("designed", w0), ("calibrated", w_real)):
                res[lab].append(adctest.sine_test(convert(x, w_real, w_read, rng, n_ln), fin_bin)["enob"])
        e = n_ln * E_LN + (NCYC - n_ln) * E_FAST + E_REST
        en = float(np.median(res["calibrated"]))
        sweep[n_ln] = (res, e, en)
        print(f"   {n_ln:>19}   {np.median(res['designed']):10.2f} / {en:5.2f}"
              f"                     {e*1e12:6.1f} pJ            {biosig.fom_walden(e*FS, FS, en)*1e15:5.1f} fJ/step")
    w_real = real_weights(w0, 100)
    ramp = np.linspace(-VFS, VFS, 2 ** NB * 32, endpoint=False)
    c = np.clip(np.round(convert(ramp, w_real, w_real, rng, NCYC)).astype(int), 0, 2 ** NB - 1)
    dnl, inl = adctest.ramp_histogram(c, NB)
    print(f"   calibrated chip, all decisions low-noise: DNL {dnl.min():+.2f} .. {dnl.max():+.2f} LSB, "
          f"INL {inl.min():+.2f} .. {inl.max():+.2f} LSB")
    return sweep, dnl, inl


def main():
    ap = argparse.ArgumentParser(description="Lab 8: the Open-BioAFE SAR converter")
    ap.add_argument("--part", choices=["a", "b", "both"], default="both")
    args = ap.parse_args()
    os.makedirs(PLOTS, exist_ok=True)
    a = part_a() if args.part in ("a", "both") else None
    b = part_b() if args.part in ("b", "both") else None
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
        if a:
            for k, lab in (("lab8_plain", "plain"), ("lab8_boot", "bootstrapped")):
                h = a[k][1]
                p = np.abs(np.fft.rfft(h - h.mean())) ** 2
                axs[0].plot(np.arange(len(p)) * FS / NS / 1e3, 10 * np.log10(p / p.max() + 1e-20), lw=0.8, label=lab)
            axs[0].set(xlabel="frequency (kHz)", ylabel="dBc", ylim=(-130, 5), title="(a) held samples: sampler distortion")
            axs[0].legend(fontsize=8)
        if b:
            sweep, dnl, inl = b
            ks = sorted(sweep)
            axs[1].plot([sweep[k][1] * 1e12 for k in ks], [sweep[k][2] for k in ks], "o-")
            for k in ks:
                axs[1].annotate(f"{k} low-noise", (sweep[k][1] * 1e12, sweep[k][2]), fontsize=8,
                                xytext=(5, -10), textcoords="offset points")
            axs[1].set(xlabel="energy per conversion (pJ)", ylabel="median ENOB (calibrated)",
                       title="(b) comparator noise mode: ENOB against energy")
        fig.savefig(os.path.join(PLOTS, "lab8_sar.png"), dpi=130)
        print("wrote", os.path.join(PLOTS, "lab8_sar.png"))
    except ImportError:
        pass


if __name__ == "__main__":
    main()
