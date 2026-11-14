"""lab15_bioz_sg13.py -- Lab 15, part 2: a square-wave bioimpedance readout in SG13G2 (Chapter 28).

    python labs/spice/lab15_bioz_sg13.py
    python labs/spice/lab15_bioz_sg13.py --iexc 50e-6

Excitation: one PMOS current mirror (20 uA) steered by an SG13G2 transmission-gate H-bridge at
50 kHz, returning to mid-supply (two separate mirrors for source and sink never match, and their
difference drives the bridge out of saturation), through 1 uF DC-blocking capacitors, into the outer (current) electrodes.
Load: tetrapolar, with wet-electrode impedances (1 kOhm + 51 kOhm || 47 nF) on all five electrodes
(two current, two voltage, one reference to mid-supply through the 150 kOhm
safety resistor of Chapter 12), two 20 Ohm outer tissue segments and the
measured segment as a Debye network, R_inf = 30 Ohm in series with 30 Ohm || 177 nF (R0 = 60 Ohm,
fc = 30 kHz; the Cole alpha of 0.7 used in part 1 has no exact RC equivalent).
Readout: a behavioural instrumentation amplifier (gain 10, 2 MHz), then square-wave I and Q
demodulators made of SG13G2 transmission gates driven by the excitation clock and by a copy
delayed by a quarter period. The demodulated outputs are averaged over whole periods.
Compared with: the same square/square measurement computed in Python from the Debye model, and
the true impedance at 50 kHz. Needs Docker and hpretl/iic-osic-tools:2026.10.
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sg13_char as ch  # noqa: E402

F, VDD, VCM, GAIN = 50e3, 1.2, 0.6, 10.0
RINF, R1, C1 = 30.0, 30.0, 1 / (2 * np.pi * 30e3 * 30.0)
T_SIM, N_SKIP = 1.2e-3, 10          # periods skipped while the blocking capacitors settle


def z_tissue(f):
    return RINF + R1 / (1 + 1j * 2 * np.pi * f * R1 * C1)


def ideal_square_reading(f=F, nh=401):
    """Square-wave current of amplitude 1, square I and Q references: I + jQ in ohms."""
    k = np.arange(1, nh, 2)
    # current harmonics (4/pi)/k; reference harmonics (4/pi)/k; the average of the product keeps
    # (1/2)(4/pi)^2/k^2 Re/Im of Z(kf), with the Q reference's quarter-period delay giving (-1)^((k-1)/2)
    zk = z_tissue(k * f)
    i = np.sum(0.5 * (4 / np.pi) ** 2 / k ** 2 * zk.real)
    q = np.sum(0.5 * (4 / np.pi) ** 2 / k ** 2 * (-zk.imag) * (-1) ** ((k - 1) // 2))
    return i, q


def netlist(iexc, tag):
    tp = 1 / F
    ze = lambda a, b, t: f"Rs{t} {a} m{t} 1k\nRp{t} m{t} {b} 51k\nCp{t} m{t} {b} 47n"
    return f"""* Lab 15 part 2: square-wave bioimpedance readout, Iexc = {iexc*1e6:g} uA
.lib cornerMOSlv.lib mos_tt
.subckt tg a b c cb
XN a c b 0 sg13_lv_nmos w=2u l=0.13u ng=1 m=1
XP a cb b vdd sg13_lv_pmos w=4u l=0.13u ng=1 m=1
.ends
.subckt tgw a b c cb
* wide switches for the H-bridge: their on-resistance carries the excitation current
XN a c b 0 sg13_lv_nmos w=10u l=0.13u ng=1 m=1
XP a cb b vdd sg13_lv_pmos w=20u l=0.13u ng=1 m=1
.ends
Vdd vdd 0 {VDD}
Vcm vcm 0 {VCM}
Vph ph 0 pulse(0 {VDD} 0 5n 5n {tp/2-10e-9} {tp})
Bphn phn 0 v = {VDD} - v(ph)
Vqd qd 0 pulse(0 {VDD} {tp/4} 5n 5n {tp/2-10e-9} {tp})
Bqdn qdn 0 v = {VDD} - v(qd)
* one PMOS current source (mirror of {iexc*1e6:g} uA); the bridge returns to mid-supply, so a single
* device sets the current and no source/sink mismatch has to flow anywhere
Iref2 pref 0 {iexc}
XPR pref pref vdd vdd sg13_lv_pmos w=20u l=2u ng=1 m=1
XPS top pref vdd vdd sg13_lv_pmos w=20u l=2u ng=1 m=1
Vbot bot vcm 0
* H-bridge: phase high drives current from hp to hn, phase low from hn to hp
X1 top hp ph phn tgw
X2 hn bot ph phn tgw
X3 top hn phn ph tgw
X4 hp bot phn ph tgw
* DC-blocking capacitors and current electrodes
Cbp hp e1 1u
Cbn hn e4 1u
{ze('e1', 'ta', 1)}
{ze('e4', 'td', 4)}
* tissue: outer segment, measured Debye segment, outer segment
Rta ta tb 20
Rinf tb tm {RINF}
R1 tm tc {R1}
C1 tm tc {C1}
Rtd tc td 20
* reference electrode from the measured segment's middle to mid-supply, through the 150 kOhm
* safety resistor of the right-leg drive (Chapter 12), so that the excitation does not return through it
{ze('tm', 'rref', 5)}
Ro rref vcm 150k
* voltage electrodes into the instrumentation amplifier (no current flows)
{ze('tb', 'vp', 2)}
{ze('tc', 'vn', 3)}
Bia ia 0 v = {VCM} + {GAIN} * (v(vp) - v(vn))
Ria ia iaf 1k
Cia iaf 0 {1/(2*np.pi*1e3*2e6)}
Biab iab 0 v = 2*{VCM} - v(iaf)
* square-wave demodulators: in phase and quadrature (choppers against mid-supply)
XI1 iaf di ph phn tg
XI2 iab di phn ph tg
XQ1 iaf dq qd qdn tg
XQ2 iab dq qdn qd tg
Rdi di vcm 100meg
Rdq dq vcm 100meg
* start from the balanced state the blocking capacitors reach after many periods (their time
* constant with the electrodes is about 50 ms, far longer than the simulation)
.ic v(hp)={VCM} v(hn)={VCM} v(e1)={VCM} v(e4)={VCM}
.control
tran 10n {T_SIM} 0 20n
let vi = v(di) - {VCM}
let vq = v(dq) - {VCM}
let ie = i(Vdd)
wrdata /work/out/{tag}.txt vi vq v(e1)
.endc
.end
"""


def main():
    ap = argparse.ArgumentParser(description="Lab 15 part 2: SG13G2 bioimpedance readout")
    ap.add_argument("--iexc", type=float, default=20e-6, help="excitation current amplitude (A)")
    args = ap.parse_args()
    tag = "lab15b"
    ch.run({tag: netlist(args.iexc, tag)})
    t, vi, vq, ve = ch.load(tag, 3)
    tp = 1 / F
    t0, t1 = N_SKIP * tp, (int(T_SIM / tp) - 1) * tp
    tu = np.arange(t0, t1, 10e-9)
    i_avg = np.mean(np.interp(tu, t, vi)) / (GAIN * args.iexc)
    q_avg = np.mean(np.interp(tu, t, vq)) / (GAIN * args.iexc)
    i_id, q_id = ideal_square_reading()
    z = z_tissue(F)
    print(f"Square-wave readout at {F/1e3:g} kHz, {args.iexc*1e6:g} µA, Debye tissue (true Z = {abs(z):.2f} Ohm, {np.degrees(np.angle(z)):.1f} deg):")
    for lab, (ii, qq) in (("SG13G2 circuit", (i_avg, q_avg)), ("ideal square/square", (i_id, q_id))):
        print(f"   {lab:>20}: I = {ii:6.2f} Ohm, Q = {qq:6.2f} Ohm -> |Z| = {np.hypot(ii, qq):6.2f} Ohm, "
              f"phase {np.degrees(np.arctan2(-qq, ii)):6.1f} deg")
    err = np.hypot(i_avg, q_avg) / np.hypot(i_id, q_id) - 1
    print(f"   circuit against ideal square/square: {err*100:+.2f} % in magnitude")


if __name__ == "__main__":
    main()
