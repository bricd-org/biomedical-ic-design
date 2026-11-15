"""lab5_chopper.py -- Lab 5: a chopped capacitively coupled amplifier with a DC servo loop (Chapters 9, 10).

    python labs/spice/lab5_chopper.py              # chopped and unchopped runs, 0.4 s each
    python labs/spice/lab5_chopper.py --voff 0.1   # another electrode offset

The signal path is that of Figure 10.1, fully differential: SG13G2 transmission-gate choppers at
4 kHz (20 ns non-overlap), Cin = 20 pF, Cfb = 200 fF with 10 GOhm across it (enough when chopped,
and the most that gate leakage allows, Chapter 8; the unchopped run uses 10 TOhm), and a DC servo loop that integrates the demodulated
output and feeds it back, chopped, through C_DSL = 4 pF. The amplifier itself is behavioural: gain
10^4 with one pole (GBW 10 MHz), 1 mV of input offset and an input noise of 30 nV/rtHz white plus
1/f noise with a corner near 200 Hz (ngspice trnoise), so that the run shows what chopping does to them. The electrode carries a DC
offset (default 300 mV) and a 1 mV, 37 Hz test tone. Each run is simulated twice: chopped, and with
the choppers held in the straight-through position.

Reported: gain at 37 Hz, the output's residual offset, the input-referred noise over 4-100 Hz
(after subtracting the tone),
the chopper ripple at 4 kHz before any low-pass filter, the servo's output, and the input
impedance from the average current drawn from the electrode (expected 1/(2 f_ch Cin) = 6.25 MOhm).
Needs Docker and hpretl/iic-osic-tools:2026.10.
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sg13_char as ch  # noqa: E402
import sg13_ota  # noqa: E402

PLOTS = os.path.join(HERE, "out")
VDD, VCM = 1.2, 0.6
FCH, CIN, CFB, CDSL = 4e3, 20e-12, 200e-15, 4e-12
F_SIG, A_SIG = 37.0, 1e-3
T_SIM, T_START = 0.4, 0.15
F_HP = 2.0                       # servo high-pass corner (Hz); 0.5 Hz in the chip, faster here to settle
NT = 2e-6                        # noise source update step (white noise up to 250 kHz)


def netlist(chop, voff, tag, ota=None):
    tch = 1 / FCH
    if chop:
        clk = (f"Vphi phi 0 pulse(0 {VDD} 0 5n 5n {tch/2-30e-9} {tch})\n"
               f"Vphb phb 0 pulse(0 {VDD} {tch/2} 5n 5n {tch/2-30e-9} {tch})\n")
    else:
        clk = f"Vphi phi 0 {VDD}\nVphb phb 0 0\n"
    k_int = 2 * np.pi * F_HP * CFB / CDSL          # integrator gain (1/s) for a high-pass corner at F_HP
    v_dsl0 = -voff * CIN / CDSL if chop else 0.0   # servo output that cancels the (chopped) electrode offset
    rfb = '10G' if chop else '10T'                 # chopped: 10 GOhm is enough; unchopped needs teraohms
    if ota is not None:                            # the SG13G2 input pair leaks ~60 pA through its 1000 um2 thin-oxide
        rfb = '1G'                                 # gates: 1 GOhm keeps the shift at ~60 mV (corner 800 Hz < f_ch)
    if ota is None:                                # behavioural: 30 nV/rtHz, 1/f corner near 200 Hz
        white = 30e-9 * np.sqrt(1 / (2 * NT))      # rms per step for 30 nV/rtHz
        namp = 0.5e-6
    else:                                          # the SG13G2 OTA pair: sqrt(2) x one OTA's .noise result
        wd = np.sqrt(2) * ota["white"]
        white = wd * np.sqrt(1 / (2 * NT))
        namp = 0.5e-6 * np.sqrt(wd ** 2 * ota["corner"] / (30e-9 ** 2 * 200))   # 0.5u <-> (30 nV)^2 x 200 Hz
    if ota is None:
        amp = f"""* behavioural amplifier: inverting, gain 1e4, pole at 1 kHz (GBW 10 MHz: the chopped signal
* needs bandwidth well above f_ch times the noise gain), offset and noise at its input
Vos nos 0 dc 1m trnoise({white} {NT} 1 {namp})
Bamp n1 0 v = -1e4 * (v(xp) - v(xn) + v(nos))
Rp n1 n2 1k
Cp n2 0 {1/(2*np.pi*1e3*1e3)}
Bod od 0 v = max(min(v(n2), 0.6), -0.6)
Bop op 0 v = {VCM} + v(od)/2
Bon on 0 v = {VCM} - v(od)/2"""
    else:
        amp = f"""{sg13_ota.SUBCKT}
* two SG13G2 folded-cascode OTAs as a pseudo-differential pair (1 uA tail each, 2 uA per OTA);
* offset and the pair's input-referred noise (from sg13_ota's .noise) sit at one non-inverting input
Vcm cm 0 {VCM}
Vos cmn cm dc 1m trnoise({white} {NT} 1 {namp})
XAP cmn xp op vdd ota_fc ib=1u {sg13_ota.LOWNOISE}
XAN cm xn on vdd ota_fc ib=1u {sg13_ota.LOWNOISE}
* test-bench buffers: the 1 MOhm measurement filter must not load the OTAs (on chip they drive the PGA's capacitors)
Ebp opb 0 op 0 1
Ebn onb 0 on 0 1"""
    return f"""* Lab 5 chopped CCIA, chop={chop}, electrode offset {voff} V
.lib cornerMOSlv.lib mos_tt
.option method=gear
.subckt tg a b c cb
XN a c b 0 sg13_lv_nmos w=2u l=0.13u ng=1 m=1
XP a cb b vdd sg13_lv_pmos w=4u l=0.13u ng=1 m=1
.ends
.subckt chopper ip in op on phi phb phin phbn
X1 ip op phi phin tg
X2 in on phi phin tg
X3 ip on phb phbn tg
X4 in op phb phbn tg
.ends
Vdd vdd 0 {VDD}
{clk}Bphin phin 0 v = {VDD} - v(phi)
Bphbn phbn 0 v = {VDD} - v(phb)
* electrodes: offset + test tone
Vep ep 0 dc {VCM + voff/2} sin({VCM + voff/2} {A_SIG/2} {F_SIG})
Ven en 0 dc {VCM - voff/2} sin({VCM - voff/2} {-A_SIG/2} {F_SIG})
* input chopper and coupling capacitors
XCH1 ep en ap an phi phb phin phbn chopper
Cinp ap xp {CIN}
Cinn an xn {CIN}
{amp}
Cfbp op xp {CFB}
Cfbn on xn {CFB}
Rfbp op xp {rfb}
Rfbn on xn {rfb}
* output chopper (demodulator)
XCH2 {"opb onb" if ota is not None else "op on"} yp yn phi phb phin phbn chopper
Rlp yp 0 100G
Rln yn 0 100G
* 500 Hz anti-alias filter after the demodulator (the measurement reads its output)
Rfp yp yfp 1meg
Cfp yfp 0 318p
Rfn yn yfn 1meg
Cfn yfn 0 318p
* DC servo: non-inverting integrator of the demodulated output, chopped back through C_DSL
Bint 0 nint i = {k_int} * (v(yp) - v(yn))
Cint nint 0 1
.ic v(nint)={v_dsl0}
Bdp dp 0 v = {VCM} + v(nint)/2
Bdn dn 0 v = {VCM} - v(nint)/2
XCH3 dp dn dcp dcn phi phb phin phbn chopper
Cdp dcp xp {CDSL}
Cdn dcn xn {CDSL}
.control
save v(yp) v(yn) v(yfp) v(yfn) v(nint) vep#branch
tran 1u {T_SIM} 0 2u
let vy = v(yp) - v(yn)
let vf = v(yfp) - v(yfn)
let ie = i(Vep)
wrdata /work/out/{tag}.txt vy ie v(nint) vf
.endc
.end
"""


def analyse(tag):
    t, vy, ie, vd, vf = ch.load(tag, 4)
    sel = t >= T_START
    t, vy, ie, vd, vf = t[sel], vy[sel], ie[sel], vd[sel], vf[sel]
    fs = 200e3
    tu = np.arange(t[0], t[-1], 1 / fs)
    y = np.interp(tu, t, vf)                     # filtered output: gain, offset, noise
    yr = np.interp(tu, t, vy)                    # raw demodulator output: ripple
    n = len(y)
    f = np.fft.rfftfreq(n, 1 / fs)
    Y = np.fft.rfft((y - y.mean()) * np.hanning(n))
    amp = np.abs(Y) * 2 / np.sum(np.hanning(n))
    k_sig = np.argmin(abs(f - F_SIG))
    gain = amp[k_sig - 2:k_sig + 3].max() / A_SIG
    k_ch = np.argmin(abs(f - FCH))
    ampr = np.abs(np.fft.rfft((yr - yr.mean()) * np.hanning(n))) * 2 / np.sum(np.hanning(n))
    ripple = ampr[k_ch - 3:k_ch + 4].max()
    # noise: subtract a least-squares fit of the tone, DC, drift and the servo's settling exponential,
    # then integrate the residual's
    # spectrum over 4-100 Hz (the 0.25 s record cannot resolve lower frequencies)
    tt = np.arange(n) / fs
    tau = 1 / (2 * np.pi * F_HP)                 # the servo loop's settling, still visible at T_START
    basis = np.column_stack([np.sin(2 * np.pi * F_SIG * tt), np.cos(2 * np.pi * F_SIG * tt), np.ones(n), tt,
                             np.exp(-tt / tau)])
    res = y - basis @ np.linalg.lstsq(basis, y, rcond=None)[0]
    w = np.hanning(n)
    psd = np.abs(np.fft.rfft(res * w)) ** 2 / (fs * np.sum(w ** 2)) * 2
    band = (f >= 4) & (f <= 100)
    vn_out = np.sqrt(np.sum(psd[band]) * (f[1] - f[0]))
    # low-pass the output (brick wall at 200 Hz) for the residual offset
    resid = np.mean(y)
    i_avg = np.trapz(ie, t) / (t[-1] - t[0])      # time-weighted: ngspice steps cluster at the edges
    return dict(gain=gain, ripple=ripple, vn=vn_out / gain, offset=resid, dsl=np.mean(vd), i_avg=i_avg,
                f=f, psd=psd)


def main():
    ap = argparse.ArgumentParser(description="Lab 5: chopped CCIA with a DC servo loop")
    ap.add_argument("--voff", type=float, default=0.3, help="electrode DC offset (V)")
    ap.add_argument("--parse-only", action="store_true", help="analyse the outputs of the last run")
    ap.add_argument("--ota", choices=["behavioural", "sg13"], default="behavioural",
                    help="behavioural amplifier, or two SG13G2 folded-cascode OTAs (sg13_ota.py)")
    args = ap.parse_args()
    ota, sfx = None, ""
    if args.ota == "sg13":
        ota = sg13_ota.characterise("1u", "1p", "lownoise")
        sfx = "_sg13"
        print(f"SG13G2 OTA (one of two): A0 {ota['a0']:.1f} dB, unity gain {ota['ugf']/1e6:.2f} MHz, "
              f"white {ota['white']*1e9:.0f} nV/√Hz, 1/f corner {ota['corner']:.0f} Hz")
    nl = {"lab5_chop" + sfx: netlist(True, args.voff, "lab5_chop" + sfx, ota)}
    if ota is None:          # unchopped with the SG13G2 OTAs is impossible: no feedback resistor both passes 37 Hz and
        nl["lab5_nochop"] = netlist(False, args.voff, "lab5_nochop", ota)   # survives the gates' leakage
    if not args.parse_only:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(2) as ex:
            list(ex.map(lambda kv: ch.run({kv[0]: kv[1]}), nl.items()))
    r = {k.replace(sfx, "") if sfx else k: analyse(k) for k in nl}
    print(f"Electrode offset {args.voff*1e3:.0f} mV, test tone {A_SIG*1e3:g} mV at {F_SIG:g} Hz:")
    c, u = r["lab5_chop"], r.get("lab5_nochop")
    col = lambda key, sc, fmt: (fmt % (u[key] * sc)) if u else "       –"
    print("                       chopped     unchopped")
    print(f"  gain at {F_SIG:g} Hz        {c['gain']:8.1f}    {col('gain', 1, '%8.1f')}")
    print(f"  output offset (mV)    {c['offset']*1e3:8.2f}    {col('offset', 1e3, '%8.2f')}")
    print(f"  input noise 4-100 Hz (µVrms) {c['vn']*1e6:7.2f}    {col('vn', 1e6, '%8.2f')}")
    print(f"  ripple at 4 kHz (mV)  {c['ripple']*1e3:8.2f}    {col('ripple', 1e3, '%8.2f')}")
    print(f"  servo output (V)      {c['dsl']:8.3f}    {col('dsl', 1, '%8.3f')}   (expected {-args.voff*CIN/CDSL:.3f} V)")
    z = abs(args.voff / 2 / r['lab5_chop']['i_avg']) if r['lab5_chop']['i_avg'] else np.inf
    print(f"  input impedance (chopped): {abs(args.voff / r['lab5_chop']['i_avg'])/1e6:.2f} MOhm differential"
          f" (1/(2 f_ch Cin) = {1/(2*FCH*CIN)/1e6:.2f} MOhm)")
    os.makedirs(PLOTS, exist_ok=True)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 4.2), constrained_layout=True)
        for k, lab in [(k, l) for k, l in (("lab5_nochop", "unchopped"), ("lab5_chop", "chopped")) if k in r]:
            g = r[k]["gain"]
            ax.loglog(r[k]["f"][1:], np.sqrt(r[k]["psd"][1:]) / g * 1e9, lw=0.6, label=lab)
        ax.set(xlabel="frequency (Hz)", ylabel="input-referred noise (nV/√Hz)", xlim=(1, 2e4),
               title="Chopping moves the amplifier's 1/f noise and offset to 4 kHz")
        ax.legend(fontsize=8)
        fig.savefig(os.path.join(PLOTS, f"lab5_chopper{sfx}.png"), dpi=130)
        print("wrote", os.path.join(PLOTS, f"lab5_chopper{sfx}.png"))
    except ImportError:
        pass


if __name__ == "__main__":
    main()
