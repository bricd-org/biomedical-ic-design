"""sg13_switch.py -- SG13G2 sampling-switch simulations for Chapter 15 (and Lab 8), using the runner in
sg13_char.py.

    python labs/spice/sg13_switch.py

  1. On-resistance versus input voltage at 1.2 V: NMOS 0.5/0.13 um (gate at 1.2 V), PMOS 1/0.13 um
     (gate at 0 V), the two as a transmission gate, and an ideally bootstrapped NMOS (V_G = V_in + 1.2 V).
  2. Off-state leakage of the NMOS (V_G = 0, 0.6 V across it) alone and as two devices in series, at 27,
     37 and 85 degC (gmin lowered so femtoampere currents are real).
  3. Gate capacitance of the on NMOS (V_GS = 1.2 V, V_DS = 0) for the charge-injection estimate.
Results: figsrc/data/sg13_switch_ron.csv, sg13_switch_leak.csv, sg13_switch_cgg.csv.
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sg13_char as ch

RON = """* on-resistance of {name}
.lib cornerMOSlv.lib mos_tt
Vin s 0 0
Vds d s 0.01
{devices}
.control
dc Vin 0 1.19 0.01
let ron = 0.01/abs(i(Vds))
wrdata /work/out/ron_{name}.txt ron
.endc
.end
"""
DEV = {
    "nmos": "Vg g 0 1.2\nXN d g s 0 sg13_lv_nmos w=0.5u l=0.13u ng=1 m=1",
    "pmos": "Vg g 0 0\nVw w 0 1.2\nXP d g s w sg13_lv_pmos w=1u l=0.13u ng=1 m=1",
    "tg": "Vg g 0 1.2\nVgb gb 0 0\nVw w 0 1.2\nXN d g s 0 sg13_lv_nmos w=0.5u l=0.13u ng=1 m=1\nXP d gb s w sg13_lv_pmos w=1u l=0.13u ng=1 m=1",
    "boot": "Eg gx 0 s 0 1\nVb g gx 1.2\nXN d g s 0 sg13_lv_nmos w=0.5u l=0.13u ng=1 m=1",
}

LEAK = """* off leakage, {stack} NMOS in series, {temp} degC
.lib cornerMOSlv.lib mos_tt
.temp {temp}
.option gmin=1e-18 abstol=1e-18
Vd d 0 0.6
Vsense s 0 0
{devices}
.control
op
let il = abs(i(Vsense))
wrdata /work/out/leak_{stack}_{temp}.txt il
.endc
.end
"""

CGG = """* gate capacitance of the on NMOS switch
.lib cornerMOSlv.lib mos_tt
Vd d 0 0.3
Vs s 0 0.3
Vg g 0 dc 1.2 ac 1
XN d g s 0 sg13_lv_nmos w=0.5u l=0.13u ng=1 m=1
.control
ac lin 1 10k 10k
let cgg = abs(imag(i(Vg)))/(2*pi*10e3)
wrdata /work/out/swcgg.txt cgg
.endc
.end
"""


def leak_devices(stack):
    if stack == 1:
        return "Vg g 0 0\nXN d g s 0 sg13_lv_nmos w=0.5u l=0.13u ng=1 m=1"
    return "Vg g 0 0\nXN1 d g m 0 sg13_lv_nmos w=0.5u l=0.13u ng=1 m=1\nXN2 m g s 0 sg13_lv_nmos w=0.5u l=0.13u ng=1 m=1"


def main():
    nl = {f"ron_{k}": RON.format(name=k, devices=v) for k, v in DEV.items()}
    temps = (27, 37, 85)
    nl.update({f"leak_{s}_{t}": LEAK.format(stack=s, temp=t, devices=leak_devices(s)) for s in (1, 2) for t in temps})
    nl["swcgg"] = CGG
    ch.run(nl)
    with open(os.path.join(ch.DATA, "sg13_switch_ron.csv"), "w") as f:
        f.write("switch,Vin_V,Ron_ohm\n")
        for k in DEV:
            v, r = ch.load(f"ron_{k}", 1)
            for a, b in zip(v, r):
                f.write(f"{k},{a:.3f},{b:.6e}\n")
    with open(os.path.join(ch.DATA, "sg13_switch_leak.csv"), "w") as f:
        f.write("stack,temp_C,I_A\n")
        for s in (1, 2):
            for t in temps:
                a = np.atleast_1d(np.loadtxt(os.path.join(ch.OUT, f"leak_{s}_{t}.txt")))
                f.write(f"{s},{t},{a[-1]:.6e}\n")
    _, c = ch.load("swcgg", 1)
    with open(os.path.join(ch.DATA, "sg13_switch_cgg.csv"), "w") as f:
        f.write("W_um,L_um,Cgg_F\n0.5,0.13,%.6e\n" % c[0])
    print("wrote", ch.DATA)


if __name__ == "__main__":
    main()
