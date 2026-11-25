"""ch32_figs.py -- Chapter 32 figures and numbers.

Figure 32.1 (ch32_ear.svg): (a) the noise budget of an ear-EEG channel, wet and dry contacts, over the full EEG
band and over 1-40 Hz, scaled from the Chapter 29 budget; (b) the empirical ratio-of-ratios calibration of pulse
oximetry.
Figure 32.2 (ch32_system.svg): (a) 50 Hz mains on the signal against the common-mode input impedance, for the
standards' wet imbalance and for dry ear contacts; (b) where the power of an ear-worn system goes.

    python ch32_figs.py            # print every number the chapter quotes, then redraw both figures
    python ch32_figs.py report     # numbers only
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
import biosig as bs

# ------------------------------------------------------------------ Worked Example 32.1: the noise budget
# input-referred rms over 0.5-100 Hz (Chapter 29), white over the band, so they scale with sqrt(bandwidth)
SRC = [("electrodes", 0.34, 1.20), ("chopped LNA", 0.36, 0.36), ("input resistors", 0.13, 0.13), ("filter, PGA, ADC", 0.054, 0.054)]
BW_FULL, BW_EAR = 99.5, 39.0


def budget():
    rows = {}
    for lab, bw in (("full", BW_FULL), ("ear", BW_EAR)):
        k = np.sqrt(bw / BW_FULL)
        for el, i in (("wet", 1), ("dry", 2)):
            parts = [(s[0], (s[i] * k) ** 2) for s in SRC]
            rows[(el, lab)] = parts
    return rows


# ------------------------------------------------------------------ Worked Example 32.2: what a dry contact asks of the input
F_MAINS = 50.0
I_D = 230.0 * 2 * np.pi * F_MAINS * 3e-12   # mains displacement current into the body (Chapter 4), A rms
RLD_GAIN = 100.0                            # right-leg-drive loop gain at 50 Hz (Chapter 12)
CMRR_INT = 10 ** (-100 / 20)                # intrinsic CMRR, 100 dB (Chapters 9, 12)
Z_CHOP, Z_BOOST = 6.25e6, 200e6             # chopped and boosted input impedance (Chapter 10)
C_PAD = 5e-12                               # pad capacitance per input (Chapter 10)
V_TARGET = 0.5e-6                           # ear-EEG noise target (Worked Example 32.1)
F_TONE = 51.2e3                             # impedance excitation (Chapter 29)


def z_dry(f, k=1.0):
    """Chapter 3's dry model (5 kOhm + 1 MOhm || 4.7 nF); k = 2 is a contact of half the area."""
    return k * bs.z_electrode(f, "dry")


def mains_dm(zcm, vcm, dz):
    """50 Hz differential interference (V rms) for common mode vcm at the electrodes (Chapter 12's key equation)."""
    return vcm * (dz / zcm + CMRR_INT)


def rld_pm(r_o=150e3, fu=5e3, c_b=200e-12, kind="dry"):
    """Phase margin (deg) of Chapter 12's RLD loop with the RL electrode of the given kind."""
    f = np.logspace(1, 7, 60000)
    s = 2j * np.pi * f
    lg = (2 * np.pi * fu / s) / (1 + s * c_b * (r_o + bs.z_electrode(f, kind)))
    k = np.argmin(np.abs(np.abs(lg) - 1))
    return 180 + np.degrees(np.angle(lg[k]))


def contact():
    d = {}
    za, zb = z_dry(10), z_dry(10, 2)
    d["z10"] = (abs(za), abs(zb))
    d["loss_chop"] = (bs.divider_loss(za, Z_CHOP), bs.divider_loss(zb, Z_CHOP))
    d["loss_boost"] = (bs.divider_loss(za, Z_BOOST), bs.divider_loss(zb, Z_BOOST))
    z50 = z_dry(50)
    d["z50"] = abs(z50)
    d["vcm"] = I_D * abs(z50)                                  # dry RL contact
    d["vcm_rld"] = d["vcm"] / (1 + RLD_GAIN)
    d["dz"] = abs(z_dry(50, 2) - z50)
    _, _, d["dz_std"] = bs.cmrr_test_zcm(F_MAINS)
    d["vcm_wet_rld"] = bs.body_cm_voltage(z_ground=bs.z_electrode(F_MAINS, "wet Ag/AgCl")) / (1 + RLD_GAIN)
    d["vdm"] = mains_dm(Z_BOOST, d["vcm_rld"], d["dz"])
    d["vdm_wet"] = mains_dm(Z_BOOST, d["vcm_wet_rld"], d["dz_std"])
    d["vdm_norld"] = mains_dm(Z_BOOST, d["vcm"], d["dz"])
    d["zcm_need"] = d["vcm_rld"] * d["dz"] / (V_TARGET - d["vcm_rld"] * CMRR_INT)
    d["c_need"] = 1 / (2 * np.pi * F_MAINS * d["zcm_need"])
    d["z_pad"] = 1 / (2 * np.pi * F_MAINS * C_PAD)
    d["pm_wet"], d["pm_dry"] = rld_pm(kind="wet Ag/AgCl"), rld_pm(kind="dry")
    d["z5k"] = abs(z_dry(5e3))
    zt = z_dry(F_TONE)
    d["tone"] = (abs(zt), np.degrees(np.angle(zt)), zt.real, zt.imag)
    d["fp"] = 1 / (2 * np.pi * 1e6 * 4.7e-9)
    d["q_to_z50"] = abs(z50 - 5e3) / abs(zt.imag)           # interface |Z| at 50 Hz per ohm of quadrature at the tone
    d["rot1deg"] = zt.real * np.sin(np.radians(1))
    return d


# ------------------------------------------------------------------ Worked Example 32.3: SpO2 and the LEDs
PI_IR, PI_RED = 0.010, 0.005               # AC/DC of the two wavelengths (illustrative)
I_LED, V_LED, T_P, FS_PPG = 10e-3, 3.3, 50e-6, 100.0   # LED pulse current, supply, width, rate per LED (assumed)
P_CH, FS_EEG = 6.8e-6, 500.0               # Chapter 29: power per channel in EEG mode, sample rate


def spo2(r):
    return 110 - 25 * r


def led_power(n=2, i=I_LED, v=V_LED, tp=T_P, fs=FS_PPG):
    return n * i * v * tp * fs


def ppg():
    d = {}
    d["R"] = PI_RED / PI_IR
    d["spo2"] = spo2(d["R"])
    d["dR"] = 1 / 25                                         # one point of SpO2
    d["rel_R"] = (d["dR"] / d["R"], d["dR"] / 1.0)           # at R = 0.5 and R = 1
    d["ac_res"] = d["dR"] * PI_IR / np.sqrt(2)               # red pulse resolution as a fraction of its DC (any R)
    d["ac_res_db"] = 20 * np.log10(d["ac_res"])
    q = 2.0 ** -12 / np.sqrt(12) / 0.5                       # 12-bit quantisation, DC at half scale
    n = 4 * FS_PPG
    d["q12"] = (q, q * np.sqrt(2 / n))
    # ambient light not subtracted: red DC half the IR DC, ambient = 10 % of the red DC
    d["amb"] = (0.10, 0.05)
    d["R_amb_factor"] = (1 + d["amb"][1]) / (1 + d["amb"][0])
    d["spo2_amb"] = spo2(1.0 * d["R_amb_factor"])
    d["e_flash"] = I_LED * V_LED * T_P
    d["e_eeg"] = P_CH / FS_EEG
    d["p_led"] = led_power()
    d["p_afe8"] = 8 * P_CH
    d["p_led_slow"] = led_power(tp=25e-6, fs=25.0)
    return d


# ------------------------------------------------------------------ Worked Example 32.4: data and power of an earpiece
E_BIT, E_EV, FRAMING = 5e-9, 10e-6, 1.04    # Chapter 27's radio model and framing
N_EEG, FS_EAR, BITS = 4, 250.0, 16
LIPO = 0.040 * 3.7 * 3600                   # Chapter 1's small lithium-polymer cell, J


def raw_rate(fs_ppg=FS_PPG):
    s = {"EEG": N_EEG * FS_EAR * BITS, "PPG": 2 * fs_ppg * BITS, "motion": 3 * 100 * BITS,
         "contact, temperature": N_EEG * 2 * 2 * BITS + 1 * BITS}
    return s, sum(s.values()) * FRAMING


def feature_rate(t_ci=2.0):
    s = {"band powers": N_EEG * 6 * 8 / 2.0, "beat times": 16 * 1.2, "SpO2, perfusion": 2 * 8,
         "temperature": 16 / 2.0, "activity, contact codes": 8 + N_EEG * 2, "headers": 8 * 8 / t_ci}
    return s, sum(s.values())


def radio(rate, t_ci):
    return E_BIT * rate, E_EV / t_ci


def configs():
    """(label, AFE, LEDs, radio bits, radio events) in W."""
    afe = N_EEG * P_CH
    _, r_raw = raw_rate()
    _, r_raw_slow = raw_rate(25.0)
    _, r_feat = feature_rate()
    return [("stream all,\nPPG 100 S/s", afe, led_power(), *radio(r_raw, 0.1)),
            ("stream all,\nPPG 25 S/s", afe, led_power(tp=25e-6, fs=25.0), *radio(r_raw_slow, 0.1)),
            ("features out,\nPPG 25 S/s", afe, led_power(tp=25e-6, fs=25.0), *radio(r_feat, 2.0))]


# ------------------------------------------------------------------ figures
def fig():
    rows = budget()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2, gridspec_kw={"width_ratios": [1.5, 1]})
    order = [("wet", "full"), ("wet", "ear"), ("dry", "full"), ("dry", "ear")]
    labels = ["wet\n0.5–100 Hz", "wet\n1–40 Hz", "dry\n0.5–100 Hz", "dry\n1–40 Hz"]
    cols = [C3, C1, C2, GRAPHITE]
    totals = []
    for j, key in enumerate(order):
        b = 0
        for c, (name, v) in zip(cols, rows[key]):
            a1.bar(j, v, bottom=b, color=c, width=0.6, label=name if j == 0 else None)
            b += v
        totals.append(np.sqrt(b))
        a1.text(j, b + 0.04, f"{np.sqrt(b):.2f} µV", ha="center", fontsize=6.6)
    a1.axhline(0.5 ** 2, color=AMBERDK, ls="--", lw=0.9)
    a1.text(1.5, 0.5 ** 2 + 0.03, "0.5 µVrms", color=AMBERDK, fontsize=6.3, ha="center")
    a1.set_xticks(range(4)); a1.set_xticklabels(labels, fontsize=6.6)
    finish(a1, ylabel="Noise power (µV²)", legend=True, loc="upper left")
    a1.legend(loc="upper left", fontsize=6.0)
    panel(a1, "a")
    r = np.linspace(0.3, 1.6, 50)
    a2.plot(r, np.clip(110 - 25 * r, 0, 100), color=C1, lw=1.6)
    for rr in (0.5, 1.0):
        a2.plot([rr], [110 - 25 * rr], "o", color=AMBER, ms=4)
        a2.annotate(f"R = {rr:g}: {110 - 25 * rr:.1f} %", (rr, 110 - 25 * rr), xytext=(rr + 0.08, 110 - 25 * rr + 2), fontsize=6.6)
    finish(a2, xlabel="Ratio of ratios R", ylabel="SpO$_2$ (%)")
    a2.set_ylim(65, 102)
    panel(a2, "b")
    savefig(fig, "ch32_ear")
    return [round(t, 2) for t in totals]


def fig_system():
    c = contact()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2, gridspec_kw={"width_ratios": [1, 1.25]})
    zcm = np.logspace(7, 11, 200)
    a1.loglog(zcm, mains_dm(zcm, c["vcm_wet_rld"], c["dz_std"]) * 1e6, color=C3, label="wet, standards' imbalance")
    a1.loglog(zcm, mains_dm(zcm, c["vcm_rld"], c["dz"]) * 1e6, color=C1, label="dry ear contacts")
    a1.axhline(V_TARGET * 1e6, color=AMBERDK, ls="--", lw=0.9)
    a1.text(9e10, V_TARGET * 1e6 * 1.25, "0.5 µVrms", color=AMBERDK, fontsize=6.3, va="bottom", ha="right")
    for z, col, lab in ((Z_BOOST, MUTED, "200 MΩ, boosted"), (c["z_pad"], C4, "5 pF of pads")):
        a1.axvline(z, color=col, ls=":", lw=0.8)
        a1.text(z / 1.12, 40, lab, fontsize=6.0, color=col, rotation=90, ha="right", va="bottom")
    for v in (c["vdm"], c["vdm_wet"]):
        a1.plot([Z_BOOST], [v * 1e6], "o", color=AMBER, ms=3.5, zorder=5)
    a1.annotate(f"{c['vdm'] * 1e6:.1f} µV", (Z_BOOST, c["vdm"] * 1e6), xytext=(4.5e7, 1.1),
                fontsize=6.3, arrowprops=dict(arrowstyle="-", lw=0.5, color=GRAPHITE))
    a1.annotate(f"{c['vdm_wet'] * 1e6:.3f} µV", (Z_BOOST, c["vdm_wet"] * 1e6), xytext=(3.0e7, 0.004),
                fontsize=6.3, arrowprops=dict(arrowstyle="-", lw=0.5, color=GRAPHITE))
    a1.set_xlim(1e7, 1e11); a1.set_ylim(5e-4, 1e3)
    finish(a1, xlabel="Common-mode input impedance $Z_\\mathrm{cm}$ (Ω)", ylabel="50 Hz on the signal (µVrms)")
    a1.legend(loc="upper right", fontsize=5.8)
    panel(a1, "a")
    cf = configs()
    cols = [GRAPHITE, C2, C1, PALE]
    names = ["front-end, 4 ch", "PPG LEDs", "radio, bits", "radio, events"]
    for j, row in enumerate(cf):
        left = 0
        for k, (v, col) in enumerate(zip(row[1:], cols)):
            a2.barh(j, v * 1e6, left=left, color=col, height=0.55, label=names[k] if j == 0 else None)
            left += v * 1e6
        a2.text(left + 12, j, f"{left:.0f} µW", va="center", fontsize=6.6)
    a2.set_yticks(range(len(cf))); a2.set_yticklabels([r[0] for r in cf], fontsize=6.4)
    a2.invert_yaxis()
    a2.set_xlim(0, 720)
    finish(a2, xlabel="Average power (µW)")
    a2.legend(loc="lower right", fontsize=5.8)
    panel(a2, "b")
    savefig(fig, "ch32_system")


# ------------------------------------------------------------------ numbers
def report():
    rows = budget()
    print("Worked Example 32.1 (noise, µVrms):")
    for key in (("wet", "full"), ("dry", "full"), ("wet", "ear"), ("dry", "ear")):
        p = rows[key]
        print("  %s %s: %.2f, electrodes %.0f %% of the power" % (key[0], key[1], np.sqrt(sum(v for _, v in p)),
                                                                   100 * p[0][1] / sum(v for _, v in p)))
    print("  band factor sqrt(39/99.5) = %.3f" % np.sqrt(BW_EAR / BW_FULL))

    c = contact()
    print("Worked Example 32.2 (dry ear contacts; contact B has twice the impedance of A):")
    print("  |Z| at 10 Hz: A %.0f kOhm, B %.0f kOhm; at 50 Hz A %.0f kOhm" % (c["z10"][0] / 1e3, c["z10"][1] / 1e3, c["z50"] / 1e3))
    print("  divider loss at 10 Hz: chopped 6.25 MOhm %.1f / %.1f %% (gains %.2f / %.2f), boosted 200 MOhm %.2f / %.2f %%"
          % (100 * c["loss_chop"][0], 100 * c["loss_chop"][1], 1 - c["loss_chop"][0], 1 - c["loss_chop"][1],
             100 * c["loss_boost"][0], 100 * c["loss_boost"][1]))
    print("  displacement current %.3f uA; Vcm through a dry RL contact %.0f mV, with RLD (A=100) %.2f mV"
          % (I_D * 1e6, c["vcm"] * 1e3, c["vcm_rld"] * 1e3))
    print("  wet case (Ch 4/12): Vcm with RLD %.0f uV, standards' dZ %.1f kOhm" % (c["vcm_wet_rld"] * 1e6, c["dz_std"] / 1e3))
    print("  dZ at 50 Hz %.0f kOhm = %.1f x the standards'; Vcm ratio %.1f x" % (c["dz"] / 1e3, c["dz"] / c["dz_std"], c["vcm_rld"] / c["vcm_wet_rld"]))
    print("  50 Hz on the signal at 200 MOhm: dry %.2f uV (no RLD %.0f uV rms, %.2f mV peak vs the +-0.625 mV EEG range), wet %.3f uV; ratio %.0f x"
          % (c["vdm"] * 1e6, c["vdm_norld"] * 1e6, c["vdm_norld"] * np.sqrt(2) * 1e3, c["vdm_wet"] * 1e6, c["vdm"] / c["vdm_wet"]))
    print("  effective CMRR from the imbalance at 200 MOhm: %.1f dB" % (-20 * np.log10(c["dz"] / Z_BOOST)))
    print("  Zcm for 0.5 uV: %.2f GOhm = %.2f pF at 50 Hz; 5 pF of pads = %.0f MOhm" % (c["zcm_need"] / 1e9, c["c_need"] * 1e12, c["z_pad"] / 1e6))
    print("  RLD phase margin (150 kOhm, 5 kHz, 200 pF): wet RL %.0f deg, dry RL %.0f deg; dry |Z| at 5 kHz %.1f kOhm"
          % (c["pm_wet"], c["pm_dry"], c["z5k"] / 1e3))
    t = c["tone"]
    print("  tone at 51.2 kHz: |Z| %.2f kOhm at %.1f deg; in phase %.0f Ohm, quadrature %.0f Ohm; corner f_p %.0f Hz"
          % (t[0] / 1e3, t[1], t[2], t[3], c["fp"]))
    print("  interface time constant Rp Cp = %.1f ms" % (1e6 * 4.7e-9 * 1e3))
    print("  interface |Z| at 50 Hz / quadrature at 51.2 kHz = %.0f; 1 deg of reference phase moves %.0f Ohm into Q (%.0f %% of it)"
          % (c["q_to_z50"], c["rot1deg"], 100 * c["rot1deg"] / abs(t[3])))

    p = ppg()
    print("Worked Example 32.3 (SpO2):")
    print("  R = %.2f -> SpO2 %.1f %%; R = 1 -> %.1f %%" % (p["R"], p["spo2"], spo2(1.0)))
    print("  +-1 point: dR %.2f = %.0f %% of R at 0.5, %.0f %% at 1; red pulse to %.2e of DC (%.0f dB)"
          % (p["dR"], 100 * p["rel_R"][0], 100 * p["rel_R"][1], p["ac_res"], p["ac_res_db"]))
    print("  12-bit quantisation, DC at half scale: %.2e per sample, %.1e over 4 s at 100 S/s" % p["q12"])
    print("  ambient 10 %% of red DC, 5 %% of IR DC: R x %.3f; 85 %% reads %.1f %%" % (p["R_amb_factor"], p["spo2_amb"]))
    print("  LED flash %.2f uJ vs one EEG sample %.1f nJ (%.0f x)" % (p["e_flash"] * 1e6, p["e_eeg"] * 1e9, p["e_flash"] / p["e_eeg"]))
    print("  two LEDs at 100 S/s, 50 us, 10 mA, 3.3 V: %.0f uW = %.1f x the 8-channel front-end (%.1f uW); 25 S/s, 25 us: %.1f uW"
          % (p["p_led"] * 1e6, p["p_led"] / p["p_afe8"], p["p_afe8"] * 1e6, p["p_led_slow"] * 1e6))
    print("  half the pulse width: half the charge, %.1f dB of SNR with white receiver noise" % (10 * np.log10(2)))

    print("Worked Example 32.4 (data and power):")
    s, r = raw_rate()
    print("  raw: " + ", ".join("%s %.2f kb/s" % (k, v / 1e3) for k, v in s.items()) + "; with framing %.1f kb/s" % (r / 1e3))
    for tci in (0.1, 0.25):
        b, e = radio(r, tci)
        print("    radio at %.0f ms: bits %.0f uW + events %.0f uW = %.0f uW; %.0f bytes per event" % (tci * 1e3, b * 1e6, e * 1e6, (b + e) * 1e6, r * tci / 8))
    s, r = feature_rate()
    b, e = radio(r, 2.0)
    print("  features: " + ", ".join("%s %.1f b/s" % (k, v) for k, v in s.items()) + "; total %.0f b/s (%.0f x less)" % (r, raw_rate()[1] / r))
    print("    radio at 2 s: bits %.2f uW + events %.1f uW = %.1f uW" % (b * 1e6, e * 1e6, (b + e) * 1e6))
    for row in configs():
        tot = sum(row[1:])
        print("  %-28s front-end %.1f, LEDs %.1f, radio %.1f + %.1f -> %.0f uW; 40 mAh 3.7 V cell %.1f days"
              % (row[0].replace("\n", " "), row[1] * 1e6, row[2] * 1e6, row[3] * 1e6, row[4] * 1e6, tot * 1e6, LIPO / tot / 86400))


if __name__ == "__main__":
    report()
    if "report" not in sys.argv[1:]:
        print(fig())
        fig_system()
