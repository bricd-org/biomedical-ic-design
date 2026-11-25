"""ch33_figs.py -- Chapter 33 figures and numbers.

Figure 33.1: (a) the phase error that a loop latency causes for three brain rhythms, against a +-30 degree
tolerance; (b) the number of averaged epochs an auditory steady-state response needs at ear-EEG noise levels.
Figure 33.2: how long the front-end is blind after a step at its input (a stimulus or an overload), with the
servo's 0.05 / 0.5 Hz corners and its fast-settle mode (Chapter 10).
report() prints every number the chapter quotes (Worked Examples 33.1-33.3 and section 33.3).

    python ch33_figs.py            # report, then both figures
    python ch33_figs.py report     # numbers only
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "labs", "python"))
from bricdstyle import *
from scipy import signal
import biosig

RHYTHMS = [("slow oscillation, 0.75 Hz", 0.75, C3), ("theta, 6 Hz", 6.0, C2), ("alpha, 10 Hz", 10.0, C1)]

# ---------------------------------------------------------------- the chip (Tables 1.2 and 29.1)
FS = 500.0                 # EEG output rate (S/s)
M = 1024                   # incremental Delta-Sigma cycles per conversion (Ch 20)
FMOD = 512e3               # modulator clock (Hz)
F_AFE = 2e3                # one pole "at a few kilohertz" in the Delta-Sigma path (Ch 11); 2 kHz assumed
F_HP, F_HP_DIAG, F_HP_FAST = 0.5, 0.05, 50.0     # servo corners: EEG, diagnostic, fast-settle (Ch 10)
T_FS_SPEC = 20e-3          # fast-settle duration in Table 29.1
V_LIN = 0.45 / 100         # LNA linear input range: +-0.45 V output swing at a gain of 100 (Ch 8)
V_ADC = 0.5 / 800          # converter range referred to the input in EEG mode, gain 800 (Ch 11)
V_OK = 1.5e-6              # the channel's noise target (Table 1.2): a tail below it is harmless
# ---------------------------------------------------------------- the loop around it (assumptions, Ch 23 and 27)
N_OPS = 10                 # decision: two second-order sections (10 MACs) per sample
E_MAC = 10e-12             # J per 24-bit MAC (Ch 23, order of magnitude)
T_ACT = 1.5e-3             # actuator: audio DAC frame buffer and interpolation filter, assumed
T_CI = 30e-3               # BLE connection interval (Ch 27's raw-ECG setting)
T_AIR = 41 * 8 / 1e6       # one 20-byte notification, encrypted, on the LE 1M PHY: 41 bytes on air
EB, EEV = 5e-9, 10e-6      # BLE energy per bit and per connection event (Ch 27)
P_AFE8 = 8 * 6.8e-6        # eight ECG/EEG channels (Table 29.1)
# ---------------------------------------------------------------- ear-EEG noise (Ch 32, 1-40 Hz)
NOISE_DRY_CONTACT = 0.75e-6    # dry contacts alone (1.20 uVrms over 0.5-100 Hz, scaled to 1-40 Hz)
NOISE_DRY = 0.79e-6            # whole dry channel
NOISE_WET = 0.32e-6            # whole wet channel
ND = NOISE_DRY_CONTACT / np.sqrt(39.0)   # uV/rtHz used in Figure 33.1b
ASSR_AMPS = (0.3e-6, 0.1e-6, 0.05e-6)


def phase_deg(f, tau):
    """Key equation: phase error 360 deg * f * tau."""
    return 360.0 * f * tau


# ---------------------------------------------------------------- Figure 33.1
def fig():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    tau = np.linspace(0, 150, 300)
    for lab, f0, c in RHYTHMS:
        a1.plot(tau, 360 * f0 * tau * 1e-3, color=c, lw=1.5, label=lab)
    a1.axhspan(0, 30, color=AMBER, alpha=0.15)
    a1.text(24, 21, "±30° tolerance", fontsize=6.3, ha="left", color=AMBERDK)
    for t0, lab in ((5, "on device"), (60, "over BLE")):
        a1.axvline(t0, color=GRAPHITE, ls=":", lw=0.8)
        a1.text(t0 + 2, 160, lab, fontsize=6.3, color=GRAPHITE)
    a1.set_ylim(0, 180); a1.set_xlim(0, 150)
    finish(a1, xlabel="Loop latency (ms)", ylabel="Phase error (degrees)", legend=True, loc="upper left")
    a1.legend(loc="upper right", fontsize=6.0, bbox_to_anchor=(1.0, 0.80))
    panel(a1, "a")
    # ASSR: response amplitude A in one FFT bin against noise per bin sigma/sqrt(N)
    n = np.logspace(0, 3.5, 200)
    nd = ND                                           # dry-contact ear-EEG noise density over 1-40 Hz (Ch 32)
    for amp, c in ((0.3e-6, C1), (0.1e-6, C2), (0.05e-6, C3)):
        snr = 20 * np.log10(amp / (nd * 1.0 / np.sqrt(n)))   # 1 s epochs: 1 Hz bins
        a2.semilogx(n, snr, color=c, lw=1.5, label=f"{amp*1e6:.2f} µV response")
    a2.axhline(10, color=AMBERDK, ls="--", lw=0.9)
    a2.text(1.2, 11, "10 dB: a confident detection", fontsize=6.3, color=AMBERDK)
    finish(a2, xlabel="Averaged 1 s epochs", ylabel="SNR in the response bin (dB)", legend=True, loc="lower right")
    a2.legend(loc="lower right", fontsize=6.0)
    panel(a2, "b")
    savefig(fig, "ch33_loop")
    return assr_epochs(ND)


# ---------------------------------------------------------------- Worked Example 33.1: latency budget
def conversion_delay(f=(0.75, 10.0)):
    """Input weights of the 2nd-order incremental converter with its cascade-of-integrators decimator:
    s1 + a1*s2 = a1 * sum_n sum_{k<n} u[k] - x2[M]/a2, so u[k] weighs (M-1-k). Returns the centroid delay
    (from the weighted centre of the input to the end of the conversion) and the phase delay at f."""
    k = np.arange(M)
    w = (M - 1 - k).astype(float); w /= w.sum()
    centroid = (M - np.sum(k * w)) / FMOD
    pd = {}
    for fi in f:
        h = np.sum(w * np.exp(-2j * np.pi * fi * (M - k) / FMOD))
        pd[fi] = -np.angle(h) / (2 * np.pi * fi)
    return centroid, pd


def latency():
    t_afe = 1 / (2 * np.pi * F_AFE)                   # group delay of one pole at low frequency
    t_conv, _ = conversion_delay()
    t_dec = N_OPS / FMOD                              # one operation per 512 kHz cycle
    chip = t_afe + t_conv + t_dec + T_ACT
    # through the phone: the word waits 0..T_CI for the next event (uplink); the phone decides well within one
    # interval, so its command goes out at the following event (downlink) and takes T_AIR on air
    fixed = t_afe + t_conv + T_CI + T_AIR + T_ACT
    ble = (fixed, fixed + T_CI)                       # min, max: uniform in between
    return dict(t_afe=t_afe, t_conv=t_conv, t_dec=t_dec, chip=chip, ble_min=ble[0], ble_max=ble[1],
                ble_mean=np.mean(ble), ble_jit=T_CI / 2, grid_jit=0.5 / FS)


def energy():
    r_raw = FS * 16 * 1.04                            # one channel, 4 % framing (Ch 27)
    p_bits, p_ev = EB * r_raw, EEV / T_CI
    p_dec = FS * N_OPS * E_MAC
    p_log = EEV / 1.0                                 # on-chip loop: radio idles at a 1 s interval for logs
    return dict(r_raw=r_raw, p_bits=p_bits, p_ev=p_ev, p_ble=p_bits + p_ev, p_dec=p_dec, p_log=p_log)


# ---------------------------------------------------------------- section 33.3: a causal band-pass off its centre
def rbj_bandpass(f0, q=1.5, fs=FS):
    """The demo's band-pass: RBJ biquad, 0 dB and zero phase at f0 (alpha = sin(w0)/(2Q), Q = 1.5)."""
    w = 2 * np.pi * f0 / fs
    al = np.sin(w) / (2 * q)
    a0 = 1 + al
    return np.array([al, 0, -al]) / a0, np.array([1, -2 * np.cos(w) / a0, (1 - al) / a0])


def detune(f0, rel=0.08, q=1.5):
    b, a = rbj_bandpass(f0, q)
    fr = np.array([f0 * (1 - rel), f0, f0 * (1 + rel)])
    _, h = signal.freqz(b, a, worN=2 * np.pi * fr / FS)
    _, gd = signal.group_delay((b, a), w=[2 * np.pi * f0 / FS])
    return np.degrees(np.angle(h)), gd[0] / FS, np.degrees(2 * q * rel)


# ---------------------------------------------------------------- Worked Example 33.2: blind after a step
def t_recover(v0, v_ok, f_hp, v_lin=V_LIN):
    """Key equation: slew while the LNA clips (at most V_lin per time constant), then decay exponentially."""
    tau = 1 / (2 * np.pi * f_hp)
    if v0 <= v_lin:
        return tau * np.log(v0 / v_ok)
    return tau * (v0 / v_lin - 1 + np.log(v_lin / v_ok))


def t_recover_fast(v0, v_ok, t_fs, f_fast=F_HP_FAST, f_slow=F_HP):
    """Fast-settle for t_fs after the step, then the slow corner."""
    tf = 1 / (2 * np.pi * f_fast); ts = 1 / (2 * np.pi * f_slow)
    if v0 > V_LIN:
        t_slew = tf * (v0 / V_LIN - 1)
        if t_slew >= t_fs:
            raise ValueError("still slewing when fast-settle ends")
        v_end = V_LIN * np.exp(-(t_fs - t_slew) / tf)
    else:
        v_end = v0 * np.exp(-t_fs / tf)
    return v_end, (t_fs + ts * np.log(v_end / v_ok)) if v_end > v_ok else None


def loop_sim(x, fs, tau_of_t):
    """Input-referred servo loop: the LNA clips at +-V_lin, the integrator moves the feedback by
    (1 - exp(-dt/tau)) of the clipped error each step (exact for the linear part)."""
    f = 0.0; e = np.empty_like(x); dt = 1 / fs
    for i in range(x.size):
        e[i] = x[i] - f
        f += (1 - np.exp(-dt / tau_of_t[i])) * min(max(e[i], -V_LIN), V_LIN)
    return e


def sim_step(v0, setting, fs=20e3, dur=8.0, t0=0.5, seed=5):
    """Simulate a step v0 at t0 on synthetic EEG; return t, e (with step), error against no step."""
    t, eeg = biosig.eeg(fs=fs, duration=dur, rms=20e-6, alpha_rms=10e-6, seed=seed)
    tau = np.full(t.size, 1 / (2 * np.pi * (F_HP_DIAG if setting == "0.05" else F_HP)))
    if setting.startswith("fast"):
        t_fs = float(setting.split(":")[1])
        tau[(t >= t0) & (t < t0 + t_fs)] = 1 / (2 * np.pi * F_HP_FAST)
    x = eeg + v0 * (t >= t0)
    e = loop_sim(x, fs, tau)
    e_ref = loop_sim(eeg, fs, tau)
    return t - t0, e, e - e_ref


def last_above(t, err, level):
    i = np.nonzero((np.abs(err) > level) & (t >= 0))[0]
    return t[i[-1]] if i.size else 0.0


def recovery():
    out = {}
    for v0 in (V_LIN, 50e-3):
        for name, fhp in (("0.05 Hz", F_HP_DIAG), ("0.5 Hz", F_HP), ("fast 50 Hz", F_HP_FAST)):
            out[(v0, name)] = (t_recover(v0, V_ADC, fhp), t_recover(v0, V_OK, fhp))
    return out


# ---------------------------------------------------------------- Worked Example 33.3: averaging
def assr_epochs(nd, snr_db=10.0, amps=ASSR_AMPS):
    """Epochs of 1 s (1 Hz bins) for the response to stand snr_db above the noise in its bin."""
    return {a: float(np.ceil((10 ** (snr_db / 20) * nd / a) ** 2)) for a in amps}


def assr_time(nd, amp, snr=10.0):
    """Key equation: T = SNR * e_n^2 / A^2, whatever the epoch length."""
    return snr * nd ** 2 / amp ** 2


def coherence_loss(f_mod, eps, t):
    """Amplitude kept by a coherent average whose response phase drifts linearly by 2 pi f_mod eps t."""
    th = 2 * np.pi * f_mod * eps * t
    return np.degrees(th), 20 * np.log10(abs(np.sinc(th / (2 * np.pi))))


# ---------------------------------------------------------------- Figure 33.2
def fig_recovery():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=FULL2)
    t = np.logspace(-3, np.log10(40), 600)
    for v0, ls in ((50e-3, "-"), (V_LIN, "--")):
        # servo at a fixed corner, and fast-settle held until the tail is below the noise target
        for fhp, c in ((F_HP_DIAG, C5), (F_HP, C4), (F_HP_FAST, C1)):
            tau = 1 / (2 * np.pi * fhp); t_sl = tau * max(v0 / V_LIN - 1, 0)
            r = np.where(t < t_sl, v0 - V_LIN * t / tau, min(v0, V_LIN) * np.exp(-(t - t_sl) / tau))
            a1.loglog(t, r * 1e3, color=c, ls=ls, lw=1.3)
    for x, lab, c, ha in ((0.016, "fast-settle\n(50 Hz)", C1, "center"), (2.6, "0.5 Hz", C4, "center"),
                          (36, "0.05 Hz", C5, "right")):
        a1.text(x, 110, lab, fontsize=6.3, color=c, ha=ha, va="bottom")
    for lev, lab in ((V_LIN, "LNA clips"), (V_ADC, "ADC range"), (V_OK, "noise target")):
        a1.axhline(lev * 1e3, color=AMBERDK, ls=":", lw=0.8)
        a1.text(0.065, lev * 1e3 * 1.25, lab, fontsize=6.0, color=AMBERDK)
    a1.text(0.12, 2.2e-2, "solid: 50 mV step\ndashed: 4.5 mV step", fontsize=6.0, color=GRAPHITE, va="center")
    a1.set_xlim(1e-3, 40); a1.set_ylim(5e-4, 600)
    finish(a1, xlabel="Time after the step (s)", ylabel="Residual at the input (mV)")
    panel(a1, "a")
    # a 50 mV step on synthetic EEG, as the converter sees it (decimated to 500 S/s for drawing)
    for setting, c, lab in (("0.5", C4, "servo at 0.5 Hz"), ("fast:0.06", C1, "60 ms fast-settle, then 0.5 Hz")):
        tt, e, _ = sim_step(50e-3, setting, dur=7.0)
        k = slice(None, None, 40)
        a2.plot(tt[k], np.clip(e[k], -V_ADC, V_ADC) * 1e3, color=c, lw=0.8, label=lab)
    a2.axhline(V_ADC * 1e3, color=AMBERDK, ls=":", lw=0.8); a2.axhline(-V_ADC * 1e3, color=AMBERDK, ls=":", lw=0.8)
    a2.text(6.4, -V_ADC * 1e3 + 0.04, "ADC range", fontsize=6.0, color=AMBERDK, ha="right")
    a2.set_xlim(-0.5, 6.5); a2.set_ylim(-0.8, 0.95)
    finish(a2, xlabel="Time after the step (s)", ylabel="At the converter, input-referred (mV)")
    a2.legend(loc="upper right", fontsize=6.0, ncol=1)
    panel(a2, "b")
    savefig(fig, "ch33_recovery")


# ---------------------------------------------------------------- numbers
def report():
    L = latency()
    t_conv, pd = conversion_delay()
    print("WE 33.1  latency budget")
    print("  front-end pole at %.0f kHz: %.3f ms" % (F_AFE / 1e3, L["t_afe"] * 1e3))
    print("  conversion: word every %.1f ms; ramp-weight centroid %.3f ms before the word; phase delay %s"
          % (M / FMOD * 1e3, t_conv * 1e3, ", ".join("%.3f ms at %g Hz" % (v * 1e3, f) for f, v in pd.items())))
    print("  decision: %d ops at 512 kHz = %.3f ms; actuator %.1f ms (assumed)" % (N_OPS, L["t_dec"] * 1e3, T_ACT * 1e3))
    print("  ON CHIP total %.2f ms: %.2f deg at 0.75 Hz, %.1f deg at 10 Hz" % (L["chip"] * 1e3, phase_deg(0.75, L["chip"]), phase_deg(10, L["chip"])))
    print("  sample grid if not interpolated: +-%.0f ms -> +-%.2f deg at 0.75 Hz, +-%.1f deg at 10 Hz"
          % (L["grid_jit"] * 1e3, phase_deg(0.75, L["grid_jit"]), phase_deg(10, L["grid_jit"])))
    print("  PHONE, T_CI %.0f ms, air %.2f ms: %.1f-%.1f ms, mean %.1f ms, +-%.0f ms"
          % (T_CI * 1e3, T_AIR * 1e3, L["ble_min"] * 1e3, L["ble_max"] * 1e3, L["ble_mean"] * 1e3, L["ble_jit"] * 1e3))
    for f in (0.75, 10.0):
        print("    %5.2f Hz: mean %.0f deg (range %.0f-%.0f), jitter +-%.1f deg (rms %.1f)"
              % (f, phase_deg(f, L["ble_mean"]), phase_deg(f, L["ble_min"]), phase_deg(f, L["ble_max"]),
                 phase_deg(f, L["ble_jit"]), phase_deg(f, T_CI / np.sqrt(12))))
    h = np.ceil(L["ble_max"] * 1e3) * 1e-3
    print("  scheduled on the sample counter, horizon %.0f ms: uncompensated %.0f / %.0f deg; "
          "5 %% frequency error leaves +-%.1f / +-%.1f deg" % (h * 1e3, phase_deg(0.75, h), phase_deg(10, h),
                                                            0.05 * phase_deg(0.75, h), 0.05 * phase_deg(10, h)))
    E = energy()
    print("  energy: raw channel %.2f kb/s -> bits %.1f uW + events %.0f uW = %.0f uW (%.1fx the %.1f uW front-end)"
          % (E["r_raw"] / 1e3, E["p_bits"] * 1e6, E["p_ev"] * 1e6, E["p_ble"] * 1e6, E["p_ble"] / P_AFE8, P_AFE8 * 1e6))
    print("          on chip: decision %.3f uW (%.0fx less than the link), log at 1 s %.0f uW"
          % (E["p_dec"] * 1e6, E["p_ble"] / E["p_dec"], E["p_log"] * 1e6))

    print("Section 33.3  RBJ band-pass, Q = 1.5, +-8 % detuning")
    for f0 in (0.75, 10.0):
        ph, gd, approx = detune(f0)
        print("  f0 %.2f Hz: group delay at f0 %.0f ms (Q/(pi f0) = %.0f ms); phase at -8/0/+8 %%: %+.1f / %+.1f / %+.1f deg; 2Q*0.08 = %.1f deg"
              % (f0, gd * 1e3, 1.5 / (np.pi * f0) * 1e3, ph[0], ph[1], ph[2], approx))
    print("  360 * tau_g * 1 Hz at 10 Hz: %.0f deg" % (360 * detune(10.0)[1]))

    print("WE 33.2  recovery after a step (in range = +-%.3f mV, clean = %.1f uV); tau = %.3f / %.2f / %.2f ms"
          % (V_ADC * 1e3, V_OK * 1e6, 1e3 / (2 * np.pi * F_HP), 1e3 / (2 * np.pi * F_HP_DIAG), 1e3 / (2 * np.pi * F_HP_FAST)))
    R = recovery()
    for (v0, name), (tr, tc) in R.items():
        print("  %5.1f mV, %-10s: in range %.4g s, clean %.4g s" % (v0 * 1e3, name, tr, tc))
    tf = 1 / (2 * np.pi * F_HP_FAST)
    for tfs in (T_FS_SPEC, 26e-3):
        v_end, t_clean = t_recover_fast(V_LIN, V_OK, tfs)
        print("  4.5 mV, fast-settle %.0f ms (%.2f tau) then 0.5 Hz: %.2f uV left, clean at %s" % (tfs * 1e3, tfs / tf,
              v_end * 1e6, "%.3f s" % t_clean if t_clean else "end of fast-settle"))
    print("  50 mV slews for %.1f time constants" % (50e-3 / V_LIN - 1))
    print("  fast-settle needed for 4.5 mV -> 1.5 uV: %.1f ms (%.1f tau); for 50 mV: %.1f ms (slew %.1f ms)"
          % (t_recover(V_LIN, V_OK, F_HP_FAST) * 1e3, np.log(V_LIN / V_OK), t_recover(50e-3, V_OK, F_HP_FAST) * 1e3,
             tf * (50e-3 / V_LIN - 1) * 1e3))
    for rate in (1.0, 10.0):
        print("  stimuli at %.0f /s: fast-settle 26 ms loses %.1f %%; 50 mV fast %.1f %%; 0.5 Hz alone needs %.2f s per step"
              % (rate, rate * 26e-3 * 100, rate * t_recover(50e-3, V_OK, F_HP_FAST) * 100, t_recover(V_LIN, V_OK, F_HP)))
    for tp in (1e-3,):
        print("  a %.0f ms pulse that clips the LNA moves the feedback by %.2f mV in fast-settle, %.1f uV at 0.5 Hz"
              % (tp * 1e3, V_LIN * tp / tf * 1e3, V_LIN * tp * 2 * np.pi * F_HP * 1e6))
    print("  simulated (20 kS/s loop on synthetic EEG), against the key equation:")
    worst = 0.0
    for v0, setting, fhp in ((V_LIN, "0.5", F_HP), (V_LIN, "0.05", F_HP_DIAG), (V_LIN, "fast:0.026", F_HP_FAST),
                             (50e-3, "0.5", F_HP), (50e-3, "fast:0.06", F_HP_FAST)):
        tt, e, err = sim_step(v0, setting, dur=40.0 if setting == "0.05" else 8.0)
        sim = (last_above(tt, err, V_ADC), last_above(tt, err, V_OK))
        ana = (t_recover(v0, V_ADC, fhp), t_recover(v0, V_OK, fhp))
        worst = max(worst, *[abs(a / b - 1) for a, b in zip(sim, ana)])
        print("    %5.1f mV, %-10s: in range %.4g s, clean %.4g s (key equation %.4g, %.4g)"
              % (v0 * 1e3, setting, sim[0], sim[1], ana[0], ana[1]))
    print("    largest difference %.2f %%" % (worst * 100))

    print("WE 33.3  ASSR averaging, 1 s epochs, 10 dB")
    for lab, nrms in (("dry contacts", NOISE_DRY_CONTACT), ("dry channel", NOISE_DRY), ("wet channel", NOISE_WET)):
        nd = nrms / np.sqrt(39.0)
        ep = assr_epochs(nd)
        print("  %-12s %.2f uVrms -> %.4f uV/rtHz: " % (lab, nrms * 1e6, nd * 1e6) +
              ", ".join("%.2f uV: %.0f epochs (T = %.1f s)" % (a * 1e6, ep[a], assr_time(nd, a)) for a in ASSR_AMPS))
    print("  dry channel / dry contacts noise power: %.3f; dry / wet channel time: %.1f"
          % ((NOISE_DRY / NOISE_DRY_CONTACT) ** 2, (NOISE_DRY / NOISE_WET) ** 2))
    print("  F-test threshold (Ch 25) 5.85 -> SNR 4.85 (%.1f dB): 0.1 uV in %.1f s; 10 dB takes %.2fx as long"
          % (10 * np.log10(4.85), assr_time(ND, 0.1e-6, 4.85), 10 / 4.85))
    for eps, lab in ((50e-6, "50 ppm crystal"), (1e-2, "1 % RC oscillator")):
        d, loss = coherence_loss(80.0, eps, 58.0)
        print("  80 Hz response, stimulus clock %s: drift %.0f deg over 58 s, average loses %.2f dB; full cycle in %.3g s"
              % (lab, d, loss, 1 / (80.0 * eps)))


if __name__ == "__main__":
    args = sys.argv[1:] or ["report", "fig", "recovery"]
    if "report" in args:
        report()
    if "fig" in args:
        print(fig())
    if "recovery" in args:
        fig_recovery()
