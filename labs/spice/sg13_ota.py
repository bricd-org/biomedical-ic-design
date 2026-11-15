"""sg13_ota.py -- a transistor-level SG13G2 folded-cascode OTA for Labs 5 and 10 (Chapters 6, 10, 20).

    python labs/spice/sg13_ota.py              # characterise at 1 uA and 2 uA tail current
    python labs/spice/sg13_ota.py --ib 0.5u    # another bias

The OTA is single-ended with a PMOS input pair (the inputs sit at VCM = 0.6 V on a 1.2 V supply),
NMOS folding current sinks, NMOS cascodes and a wide-swing PMOS cascode mirror. Its bias network is
inside the subcircuit: an ideal reference current IB into diode-connected replicas of the tail and
the sinks, and cascode gates 0.2 V inside the rails (B-sources: designing a real cascode bias is
left as an exercise). Supply current is 2 IB. ``SUBCKT`` is imported by lab5_chopper.py and
lab10_scds.py; ``main()`` reports open-loop gain, unity-gain frequency, phase margin, output swing,
supply current and the input-referred noise (white level and 1/f corner) that Lab 5 copies into its
trnoise source, because ngspice simulates no device noise in a transient.
Needs Docker and hpretl/iic-osic-tools:2026.10.
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sg13_char as ch  # noqa: E402

VDD, VCM = 1.2, 0.6

SUBCKT = """.subckt ota_fc inp inm out vdd ib=1u wi=10u li=1u ws=2u ls=4u wm=4u lm=4u wcn=4u lcn=1u wcp=8u lcp=1u dvn=0.2 dvp=0.2
* bias: reference current into diode-connected replicas; cascode gates 0.2 V inside the rails
Ibp vbp 0 {ib}
XMBP vbp vbp vdd vdd sg13_lv_pmos w=4u l=4u ng=1 m=1
Ibn vdd vbn {ib}
XMBN vbn vbn 0 0 sg13_lv_nmos w={ws} l={ls} ng=1 m=1
Bvcn vcn 0 v = v(vbn) + {dvn}
Bvcp vcp 0 v = v(vbp) - {dvp}
* PMOS input pair and tail (tail = IB)
XM0 tail vbp vdd vdd sg13_lv_pmos w=4u l=4u ng=1 m=1
XM1 f1 inp tail vdd sg13_lv_pmos w={wi} l={li} ng=1 m=1
XM2 f2 inm tail vdd sg13_lv_pmos w={wi} l={li} ng=1 m=1
* NMOS folding sinks (IB each) and cascodes
XM3 f1 vbn 0 0 sg13_lv_nmos w={ws} l={ls} ng=1 m=1
XM4 f2 vbn 0 0 sg13_lv_nmos w={ws} l={ls} ng=1 m=1
XM5 a vcn f1 0 sg13_lv_nmos w={wcn} l={lcn} ng=1 m=1
XM6 out vcn f2 0 sg13_lv_nmos w={wcn} l={lcn} ng=1 m=1
* wide-swing PMOS cascode mirror
XM9 d9 a vdd vdd sg13_lv_pmos w={wm} l={lm} ng=1 m=1
XM10 d10 a vdd vdd sg13_lv_pmos w={wm} l={lm} ng=1 m=1
XM7 a vcp d9 vdd sg13_lv_pmos w={wcp} l={lcp} ng=1 m=1
XM8 out vcp d10 vdd sg13_lv_pmos w={wcp} l={lcp} ng=1 m=1
.ends
"""
# presets: the fast OTA of Lab 10 and the low-noise LNA OTA of Lab 5 (1000 um2 input devices, Chapter 9)
FAST = "wi=10u li=1u ws=2u ls=4u wm=4u lm=4u"
LOWNOISE = "wi=100u li=10u ws=8u ls=20u wm=8u lm=20u wcn=16u lcn=4u wcp=32u lcp=4u dvn=0.1 dvp=0.15"


def bench(ib, cl, tag, sizes=FAST):
    """Open loop at AC (DC loop closed through 1 GOhm and 1 F), noise, and a DC transfer sweep."""
    return f"""* sg13_ota characterisation, IB = {ib}, CL = {cl}
.lib cornerMOSlv.lib mos_tt
{SUBCKT}
Vdd vdd 0 {VDD}
Vcm cm 0 {VCM}
Vin in 0 dc 0 ac 1
* AC: inm follows the output at DC (servo through Rf), the test signal is coupled in through 1 F
X1 cm inm out vdd ota_fc ib={ib} {sizes}
Rf out inm 1G
Cc inm in 1
CL out 0 {cl}
* DC transfer: an open-loop copy with a swept differential input
Vsw sw 0 0
Bip ip 0 v = {VCM} + v(sw)/2
Bim im 0 v = {VCM} - v(sw)/2
X2 ip im o2 vdd ota_fc ib={ib} {sizes}
CL2 o2 0 {cl}
.control
op
let isup = -i(Vdd)
print isup v(out) v(o2)
ac dec 40 1 1e9
let g = v(out)/v(in)
wrdata /work/out/{tag}_ac.txt mag(g) phase(g)
noise v(out) Vin dec 20 1 1e6
setplot noise1
wrdata /work/out/{tag}_noise.txt inoise_spectrum
setplot dc1
dc Vsw -20m 20m 0.1m
wrdata /work/out/{tag}_dc.txt v(o2)
.endc
.end
"""


def characterise(ib="1u", cl="1p", preset="fast"):
    tag = f"ota_{preset}_{ib}_{cl}"
    ch.run({tag: bench(ib, cl, tag, FAST if preset == "fast" else LOWNOISE)})
    f, mag, ph = ch.load(tag + "_ac", 2)
    a0 = 20 * np.log10(mag[0])
    k = np.argmax(mag < 1.0)
    ugf = np.interp(0, -np.log10(mag[k - 1:k + 1]), f[k - 1:k + 1]) if k else np.nan
    phd = np.degrees(np.unwrap(ph))
    pm = 180 - (phd[0] - np.interp(ugf, f, phd))          # phase lag at unity gain, from the low-f phase
    fn, vn = ch.load(tag + "_noise", 1)
    white = float(np.median(vn[(fn > 2e4) & (fn < 1e5)]))
    corner = float(fn[np.argmax(vn <= np.sqrt(2) * white)])           # where 1/f adds as much power as white
    sw, vo = ch.load(tag + "_dc", 1)
    gain = np.gradient(vo, sw)
    ok = gain > 0.5 * gain.max()
    swing = (vo[ok].min(), vo[ok].max())
    log = open(os.path.join(ch.OUT, tag + ".log")).read()
    isup = float([ln.split("=")[1] for ln in log.splitlines() if ln.strip().startswith("isup")][0])
    ibv = float(ib.replace("u", "e-6"))
    isup = isup / 2 - 2 * ibv                              # one OTA's core (the bench has two; 2 IB is bias)
    return dict(preset=preset, ib=ib, cl=cl, a0=a0, ugf=ugf, pm=pm, white=white, corner=corner,
                vn10=float(np.interp(10, fn, vn)), vn1k=float(np.interp(1e3, fn, vn)), swing=swing, isup=isup)


def report(r):
    print(f"  {r['preset']:9s} IB = {r['ib']:>4s}, CL = {r['cl']}: core supply {r['isup']*1e6:.2f} µA, A0 {r['a0']:.1f} dB, "
          f"unity gain {r['ugf']/1e6:.2f} MHz, phase margin {r['pm']:.0f}°")
    print(f"      input noise {r['vn10']*1e9:.0f} nV/√Hz at 10 Hz, {r['vn1k']*1e9:.0f} at 1 kHz, white {r['white']*1e9:.1f}; "
          f"1/f corner {r['corner']:.0f} Hz; output swing {r['swing'][0]:.2f}–{r['swing'][1]:.2f} V")


def main():
    ap = argparse.ArgumentParser(description="SG13G2 folded-cascode OTA")
    ap.add_argument("--ib", default=None)
    ap.add_argument("--cl", default="1p")
    a = ap.parse_args()
    print("SG13G2 folded-cascode OTA; fast: PMOS input 10/1 µm, sinks 2/4, mirror 4/4; "
          "low-noise: input 100/10 µm (1000 µm²), sinks 2/8, mirror 2/8; cascodes 4/1 and 8/1:")
    runs = [(a.ib, "fast"), (a.ib, "lownoise")] if a.ib else [("1u", "fast"), ("1u", "lownoise")]
    for ib, preset in runs:
        report(characterise(ib, a.cl, preset))


if __name__ == "__main__":
    main()
