"""lab7_comparator.py -- Lab 7: a StrongARM comparator in SG13G2 (Chapter 16), simulated with ngspice.

    python labs/spice/lab7_comparator.py            # delay, energy, noise estimate, offset Monte Carlo
    python labs/spice/lab7_comparator.py --mc 100   # more Monte Carlo samples

The circuit is the StrongARM latch of Figure 16.1 with a 4/1 um NMOS input pair (4 um^2), output
inverters and an SR latch built from two NOR gates, and two modes: fast (no added capacitance) and low-noise, with
342 fF added on the integration nodes P and Q (Worked Example 16.1). Supply 1.2 V, input common
mode 0.6 V, 10 MHz clock (reset while CLK is low; 50 MHz for the Monte Carlo ramps).

  1. delay from the clock edge to a full-swing decision, for inputs from 10 uV to 10 mV
  2. energy per decision from the supply charge, in both modes
  3. input-referred noise from the integrated charge, sigma_v = 2 n U_T sqrt(q / Q_int)
     (ngspice cannot simulate device noise in a transient; Chapter 16's key equation does it)
  4. offset by Monte Carlo with the PDK's mismatch models (mos_tt_mismatch, mm_ok=1): the input
     ramps slowly through zero and the SR latch records where the decision flips
Needs Docker and hpretl/iic-osic-tools:2026.10. Outputs in labs/spice/char/out/ and labs/spice/out/.
"""
import argparse
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sg13_char as ch  # noqa: E402

PLOTS = os.path.join(HERE, "out")
VDD, VCM, TCLK = 1.2, 0.6, 100e-9
TMC = 20e-9            # faster clock for the Monte Carlo ramps (fast mode decides in < 1 ns)
Q_E, K_B, T = 1.602177e-19, 1.380649e-23, 300.0
UT, N_SLOPE = K_B * T / Q_E, 1.22
C_LN = 342e-15


def core(mm):
    m = " mm_ok=1" if mm else ""
    inv = lambda y, a, t: (f"XPI{t} {y} {a} vdd vdd sg13_lv_pmos w=0.6u l=0.13u ng=1 m=1{m}\n"
                           f"XNI{t} {y} {a} 0 0 sg13_lv_nmos w=0.3u l=0.13u ng=1 m=1{m}")
    nor = lambda y, a, b, t: (f"XP{t}a n{t} {a} vdd vdd sg13_lv_pmos w=1u l=0.13u ng=1 m=1{m}\n"
                              f"XP{t}b {y} {b} n{t} vdd sg13_lv_pmos w=1u l=0.13u ng=1 m=1{m}\n"
                              f"XN{t}a {y} {a} 0 0 sg13_lv_nmos w=0.3u l=0.13u ng=1 m=1{m}\n"
                              f"XN{t}b {y} {b} 0 0 sg13_lv_nmos w=0.3u l=0.13u ng=1 m=1{m}")
    return f"""* StrongARM latch
XM0 tail clk 0 0 sg13_lv_nmos w=2u l=0.13u ng=1 m=1{m}
XM1 p inp tail 0 sg13_lv_nmos w=4u l=1u ng=1 m=1{m}
XM2 q inn tail 0 sg13_lv_nmos w=4u l=1u ng=1 m=1{m}
XM3 outn outp p 0 sg13_lv_nmos w=1u l=0.13u ng=1 m=1{m}
XM4 outp outn q 0 sg13_lv_nmos w=1u l=0.13u ng=1 m=1{m}
XM5 outn outp vdd vdd sg13_lv_pmos w=2u l=0.13u ng=1 m=1{m}
XM6 outp outn vdd vdd sg13_lv_pmos w=2u l=0.13u ng=1 m=1{m}
XS1 outn clk vdd vdd sg13_lv_pmos w=1u l=0.13u ng=1 m=1{m}
XS2 outp clk vdd vdd sg13_lv_pmos w=1u l=0.13u ng=1 m=1{m}
XS3 p clk vdd vdd sg13_lv_pmos w=1u l=0.13u ng=1 m=1{m}
XS4 q clk vdd vdd sg13_lv_pmos w=1u l=0.13u ng=1 m=1{m}
* output buffers keep the latch's state from loading the comparator (no hysteresis)
{inv('outpb', 'outp', 1)}
{inv('outnb', 'outn', 2)}
* NOR SR latch: Q = 1 when vinp > vinn
{nor('qq', 'outpb', 'qb', 1)}
{nor('qb', 'outnb', 'qq', 2)}
"""


def header(lib, tclk=TCLK):
    return f""".lib cornerMOSlv.lib {lib}
Vdd vdd 0 {VDD}
Vclk clk 0 pulse(0 {VDD} {tclk/2} 0.05n 0.05n {tclk/2-0.05e-9} {tclk})
"""


def tran_fixed(dv, cl, tag):
    """A few cycles at a fixed differential input dv; measure delay, energy and the P-node swing."""
    extra = f"Cpx p 0 {cl}\nCqx q 0 {cl}\n" if cl > 0 else ""
    t_ev = 1.5 * TCLK   # second evaluation phase starts at 1.5 TCLK
    return f"""* comparator, dv = {dv}, extra C = {cl}
{header('mos_tt')}Vip inp 0 {VCM + dv/2}
Vin inn 0 {VCM - dv/2}
{extra}{core(False)}
.control
tran 0.02n {4*TCLK}
meas tran qsup integ i(Vdd) from={t_ev - TCLK/2} to={t_ev + TCLK/2}
wrdata /work/out/{tag}.txt v(outp) v(outn)
.endc
.end
"""


def tran_mc(nmc, vr, ncyc, tag, mm=True):
    """Monte Carlo offset and hysteresis: the input ramps from -vr to +vr and back over 2 x ncyc
    clock cycles; the SR latch records where the decision flips on the way up and on the way down."""
    tr = ncyc * TMC
    lib = "mos_tt_mismatch" if mm else "mos_tt"
    return f"""* comparator offset Monte Carlo
{header(lib, TMC)}Bvd vd 0 v = {vr} - {2*vr} * abs(time - {tr}) / {tr}
Bip inp 0 v = {VCM} + v(vd)/2
Bin inn 0 v = {VCM} - v(vd)/2
{core(mm)}
.control
set rndseed=7
let run = 0
dowhile run < {nmc}
  if run > 0
    mc_source
  end
  tran 0.1n {2*tr} 0 0.1n
  meas tran tup when v(qq)={VDD/2} rise=1 td={3*TMC}
  meas tran tdn when v(qq)={VDD/2} fall=1 td={tr}
  let run = run + 1
end
.endc
.end
"""


def grab(log, name):
    return [float(v) for v in re.findall(rf"^{name}\s*=\s*([-+0-9.eE]+)", log, re.M)]


def parse_mc(log):
    """(tup, tdn) of every Monte Carlo sample whose two measurements both succeeded, in order.
    A sample whose transient aborts (rare convergence failures) prints errors instead and is skipped."""
    ev = re.findall(r"^(tup|tdn)\s*=\s*([-+0-9.eE]+)|measure\s+(tup|tdn)\s+when", log, re.M)
    tu, td, cur = [], [], {}
    for name, val, err in ev:
        key = name or err
        cur[key] = float(val) if name else None
        if key == "tdn":
            if cur.get("tup") is not None and cur.get("tdn") is not None:
                tu.append(cur["tup"]); td.append(cur["tdn"])
            cur = {}
    return np.array(tu), np.array(td)


def main():
    ap = argparse.ArgumentParser(description="Lab 7: StrongARM comparator in SG13G2")
    ap.add_argument("--mc", type=int, default=40, help="Monte Carlo samples for the offset")
    ap.add_argument("--parse-only", action="store_true", help="analyse the logs of the last run")
    args = ap.parse_args()
    dvs = (1e-5, 1e-4, 1e-3, 1e-2)
    nl = {}
    for mode, cl in (("fast", 0.0), ("lownoise", C_LN)):
        for dv in dvs:
            nl[f"lab7_{mode}_{dv:g}"] = tran_fixed(dv, cl, f"lab7_{mode}_{dv:g}")
    vr, ncyc = 0.03, 150
    nl["lab7_mc"] = tran_mc(args.mc, vr, ncyc, "")
    if not args.parse_only:
        ch.run(nl)

    res = {}
    for mode, cl in (("fast", 0.0), ("lownoise", C_LN)):
        rows = []
        for dv in dvs:
            log = open(os.path.join(ch.OUT, f"lab7_{mode}_{dv:g}.log")).read()
            qs = grab(log, "qsup")
            t, vp, vn = ch.load(f"lab7_{mode}_{dv:g}", 2)
            t0 = 1.5 * TCLK                                  # second evaluation phase
            sel = (t > t0) & (t < 2 * TCLK) & (vp - vn > VDD / 2)
            td = (t[sel][0] - t0) if sel.any() else np.nan     # vinp > vinn: outp stays high, outn falls
            rows.append((dv, td, abs(qs[0]) if qs else np.nan))
        res[mode] = rows
    print("Delay from the clock edge to a full-swing decision (ns):")
    print("   input     " + "  ".join(f"{m:>9}" for m in res))
    for k, dv in enumerate(dvs):
        print(f"   {dv*1e6:7.0f} µV " + "  ".join(f"{res[m][k][1]*1e9:9.2f}" for m in res))
    for m, cl in (("fast", 0.0), ("lownoise", C_LN)):
        e = res[m][2][2] * VDD
        line = f"Energy per decision, {m}: {e*1e12:.2f} pJ"
        if cl > 0:
            sig = 2 * N_SLOPE * UT * np.sqrt(Q_E / (cl * 0.5))
            line += f"; noise from Q_int = {cl*1e15:.0f} fF x 0.5 V: sigma_v = {sig*1e6:.0f} µVrms (target 61)"
        print(line)

    log = open(os.path.join(ch.OUT, "lab7_mc.log")).read()
    tu, tdn = parse_mc(log)
    tr = ncyc * TMC
    n = len(tu)
    v_up = -vr + 2 * vr * tu / tr                     # input at which the decision flips going up
    v_dn = vr - 2 * vr * (tdn - tr) / tr              # and going down
    vos = -(v_up + v_dn) / 2                          # input-referred offset
    hys = v_up - v_dn
    print(f"Offset Monte Carlo ({n} samples, 4/1 µm input pair, step {2*vr/ncyc*1e3:.2f} mV):"
          f" mean {vos.mean()*1e3:+.2f} mV, sigma {vos.std(ddof=1)*1e3:.2f} mV (Pelgrom estimate 2.0 mV);"
          f" thresholds going up and down {abs(hys.mean())*1e3:.2f} ± {hys.std(ddof=1)*1e3:.2f} mV apart"
          f" ({'leaning away from' if hys.mean() < 0 else 'leaning towards'} the previous decisions)")
    os.makedirs(PLOTS, exist_ok=True)
    with open(os.path.join(PLOTS, "lab7_summary.txt"), "w") as fh:
        for m in res:
            for r in res[m]:
                fh.write(f"{m} " + " ".join(f"{x:.6g}" for x in r) + "\n")
        fh.write("offsets_mV " + " ".join(f"{v*1e3:.3f}" for v in vos) + "\n")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
        for m in res:
            a1.semilogx([r[0] * 1e6 for r in res[m]], [r[1] * 1e9 for r in res[m]], "o-", label=m)
        a1.set(xlabel="differential input (µV)", ylabel="delay (ns)", title="(a) regeneration: delay grows as ln(1/Δv)")
        a1.legend(fontsize=8)
        a2.hist(vos * 1e3, bins=12, color="C0", alpha=0.8)
        a2.set(xlabel="offset (mV)", ylabel="samples", title=f"(b) offset, σ = {vos.std(ddof=1)*1e3:.2f} mV")
        fig.savefig(os.path.join(PLOTS, "lab7_comparator.png"), dpi=130)
        print("wrote", os.path.join(PLOTS, "lab7_comparator.png"))
    except ImportError:
        pass


if __name__ == "__main__":
    main()
