"""biosig.py -- shared models for the Open-BioAFE labs and figure scripts.

Every lab in labs/python/ and every figure script in figsrc/ imports this file,
so the numbers in the book and the numbers your labs print come from the same code.

Contents
  constants         Boltzmann, temperatures, mains
  SIGNALS           the master amplitude/bandwidth table of Chapter 2 (also Appendix B)
  synthetic signals ecg(), eeg(), emg(), spikes(), hodgkin_huxley()
  electrodes        ELECTRODES, z_electrode(), thermal_noise_rms()
  interference      body_cm_voltage(), cm_to_dm(), required_cmrr_db(), cmrr_test_zcm()
  safety            patient_current_limit()
  analysis          psd(), band_edges(), amplitude_stats()

Only NumPy and SciPy are needed.
"""
import numpy as np
from scipy import signal as sps

# ---------------------------------------------------------------------------- constants
K_B = 1.380649e-23        # Boltzmann constant (J/K)
T_BODY = 310.0            # body / electrode temperature (K), 37 degC
T_ROOM = 300.0            # circuit temperature used for amplifier noise (K)
MAINS = {"EU/Asia": (230.0, 50.0), "Americas": (120.0, 60.0)}

# ---------------------------------------------------------------------------- Chapter 2 master table
# name: (amplitude low, amplitude high) in volts, (f low, f high) in hertz, typical sample rate (S/s)
# Orders of magnitude from Webster (Medical Instrumentation), Harrison & Charles (2003) and
# Buzsaki et al. (2012); sources differ by a factor of a few, so treat these as design ranges.
SIGNALS = {
    "ECG (surface)":        ((0.5e-3, 4e-3),    (0.05, 150.0), 500),
    "EEG (scalp)":          ((5e-6, 300e-6),    (0.5, 100.0),  256),
    "EMG (surface)":        ((50e-6, 5e-3),     (10.0, 500.0), 2000),
    "EOG":                  ((10e-6, 3.5e-3),   (0.05, 50.0),  250),
    "ECoG":                 ((10e-6, 500e-6),   (0.5, 500.0),  2000),
    "LFP (intracortical)":  ((50e-6, 2e-3),     (0.5, 300.0),  1000),
    "Spikes (extracellular)": ((50e-6, 500e-6), (300.0, 7000.0), 30000),
}

# The Open-BioAFE targets (Chapter 1 spec sheet). Change them here, not in the labs.
SPEC = dict(
    channels=8,
    band=(0.5, 1000.0),          # ExG band (Hz); spike mode to 7 kHz optional
    noise_eeg_uVrms=1.5,         # input-referred, 0.5-100 Hz
    cmrr_db=90.0,
    offset_V=0.3,                # +-300 mV electrode DC offset tolerated
    sar_bits=12, ds_bits=16,
    power_per_ch_W=10e-6,
    vdd=1.2,
)


# ---------------------------------------------------------------------------- synthetic signals
def _rng(seed):
    return np.random.default_rng(seed)


# ECG beat as a sum of Gaussians, after the dynamical model of McSharry et al. (2003), written
# directly in time relative to the R peak. (amplitude mV, centre s, width s) at RR = 1 s; the
# centres scale with sqrt(RR) so the QT interval shortens at higher heart rates.
ECG_WAVES = {"P": (0.15, -0.20, 0.025), "Q": (-0.12, -0.035, 0.010), "R": (1.00, 0.0, 0.011),
             "S": (-0.25, 0.035, 0.010), "T": (0.30, 0.26, 0.045)}


def ecg(fs=500.0, duration=10.0, hr=72.0, hrv=0.03, amp=1e-3, seed=1):
    """Synthetic lead-II-like ECG in volts. hr in beats/min, hrv = relative RR std."""
    rng = _rng(seed)
    t = np.arange(int(duration * fs)) / fs
    x = np.zeros_like(t)
    rr0 = 60.0 / hr
    tr = 0.3
    peaks = []
    while tr < duration + 1.0:
        rr = rr0 * (1 + hrv * rng.standard_normal())
        peaks.append(tr)
        s = np.sqrt(rr)
        for a, mu, sig in ECG_WAVES.values():
            x += a * np.exp(-0.5 * ((t - tr - mu * s) / sig) ** 2)
        tr += rr
    return t, x * amp, np.array([p for p in peaks if p < duration])


EEG_BANDS = {"delta": (0.5, 4), "theta": (4, 8), "alpha": (8, 13), "beta": (13, 30), "gamma": (30, 100)}


def eeg(fs=256.0, duration=10.0, rms=20e-6, alpha_rms=10e-6, seed=2):
    """Synthetic scalp EEG in volts: 1/f background plus a waxing and waning alpha rhythm."""
    rng = _rng(seed)
    n = int(duration * fs)
    t = np.arange(n) / fs
    f = np.fft.rfftfreq(n, 1 / fs)
    spec = rng.standard_normal(f.size) + 1j * rng.standard_normal(f.size)
    shape = np.where(f > 0.5, 1 / np.maximum(f, 0.5), 0) * (f < 100)
    bg = np.fft.irfft(spec * shape, n)
    bg *= rms / np.std(bg)
    env = 0.6 + 0.4 * np.sin(2 * np.pi * 0.15 * t + 1.0)
    alpha = np.sqrt(2) * alpha_rms * env * np.sin(2 * np.pi * 10.0 * t + rng.uniform(0, 2 * np.pi))
    return t, bg + alpha


def emg(fs=2000.0, duration=4.0, peak=1e-3, bursts=((0.5, 1.4), (2.2, 3.4)), seed=3):
    """Synthetic surface EMG in volts: band-limited (20-450 Hz) noise gated by contraction bursts."""
    rng = _rng(seed)
    n = int(duration * fs)
    t = np.arange(n) / fs
    b, a = sps.butter(4, [20, 450], btype="band", fs=fs)
    w = sps.filtfilt(b, a, rng.standard_normal(n))
    env = np.full(n, 0.03)
    for t0, t1 in bursts:
        rise = 1 / (1 + np.exp(-(t - t0) / 0.04)) * 1 / (1 + np.exp((t - t1) / 0.04))
        env = np.maximum(env, rise)
    x = w * env
    return t, x * peak / np.max(np.abs(x))


def spikes(fs=30000.0, duration=0.5, rate=20.0, amp=150e-6, noise_rms=8e-6, seed=4):
    """Extracellular recording in volts (300 Hz-7 kHz band): biphasic spikes on background noise."""
    rng = _rng(seed)
    n = int(duration * fs)
    t = np.arange(n) / fs
    tt = np.arange(-0.5e-3, 1.5e-3, 1 / fs)
    tmpl = -np.exp(-0.5 * (tt / 0.12e-3) ** 2) + 0.35 * np.exp(-0.5 * ((tt - 0.45e-3) / 0.25e-3) ** 2)
    tmpl /= -tmpl.min()
    x = np.zeros(n)
    times = np.cumsum(rng.exponential(1 / rate, int(rate * duration * 3) + 5))
    times = times[times < duration - 2e-3]
    for ts in times:
        k = int(ts * fs)
        x[k:k + tmpl.size] += amp * rng.uniform(0.7, 1.0) * tmpl[:n - k]
    b, a = sps.butter(2, [300, 7000], btype="band", fs=fs)
    x += sps.filtfilt(b, a, rng.standard_normal(n)) * noise_rms / 0.37
    return t, x, times


def hodgkin_huxley(t_end=20e-3, dt=10e-6, i_stim=10.0, t_on=2e-3, t_dur=1e-3):
    """Membrane potential (V) of the Hodgkin-Huxley squid axon model (1952), resting at -65 mV.
    i_stim in uA/cm^2 applied from t_on for t_dur. Forward Euler on the ms/mV scale."""
    gna, gk, gl, ena, ek, el, cm = 120.0, 36.0, 0.3, 50.0, -77.0, -54.4, 1.0
    n_steps = int(t_end / dt)
    dtm = dt * 1e3
    v, m, h, nn = -65.0, 0.05, 0.6, 0.32
    out = np.empty(n_steps)
    for k in range(n_steps):
        tk = k * dt
        am = 0.1 * (v + 40) / (1 - np.exp(-(v + 40) / 10)); bm = 4 * np.exp(-(v + 65) / 18)
        ah = 0.07 * np.exp(-(v + 65) / 20);                 bh = 1 / (1 + np.exp(-(v + 35) / 10))
        an = 0.01 * (v + 55) / (1 - np.exp(-(v + 55) / 10)); bn = 0.125 * np.exp(-(v + 65) / 80)
        i_ion = gna * m ** 3 * h * (v - ena) + gk * nn ** 4 * (v - ek) + gl * (v - el)
        i_app = i_stim if t_on <= tk < t_on + t_dur else 0.0
        v += dtm * (i_app - i_ion) / cm
        m += dtm * (am * (1 - m) - bm * m)
        h += dtm * (ah * (1 - h) - bh * h)
        nn += dtm * (an * (1 - nn) - bn * nn)
        out[k] = v
    return np.arange(n_steps) * dt, out * 1e-3


# ---------------------------------------------------------------------------- electrodes (Chapter 3)
# Simplified electrode-skin models: series resistance Rs, then Rp in parallel with a capacitor
# (Cp) or a constant-phase element (Q, n). The wet model uses the 51 kOhm || 47 nF network that
# the ECG standards use to represent one poor electrode contact.
ELECTRODES = {
    "wet Ag/AgCl": dict(Rs=1e3, Rp=51e3, Cp=47e-9, ehc=0.222),
    "dry":         dict(Rs=5e3, Rp=1e6, Cp=4.7e-9, ehc=None),
    "implanted micro": dict(Rs=10e3, Rp=1e10, Q=None, n=0.85, z1k=500e3, ehc=None),
}


def z_electrode(f, kind="wet Ag/AgCl", **override):
    """Complex electrode-skin (or electrode-tissue) impedance at frequency f (Hz)."""
    p = dict(ELECTRODES[kind]); p.update(override)
    w = 2 * np.pi * np.asarray(f, float)
    if p.get("n") is not None:                       # constant-phase element
        q = p["Q"] if p.get("Q") else 1.0 / (p["z1k"] * (2 * np.pi * 1e3) ** p["n"])
        y = 1.0 / p["Rp"] + q * (1j * w) ** p["n"]
    else:
        y = 1.0 / p["Rp"] + 1j * w * p["Cp"]
    return p["Rs"] + 1.0 / y


def thermal_noise_rms(kind, f1, f2, T=T_BODY, n=4000, **override):
    """RMS thermal noise (V) of one electrode, integrating 4kT Re{Z} from f1 to f2 (Hz)."""
    f = np.logspace(np.log10(f1), np.log10(f2), n)
    s = 4 * K_B * T * np.real(z_electrode(f, kind, **override))
    return np.sqrt(np.trapz(s, f))


def divider_loss(z_source, z_in):
    """Fraction of the electrode voltage lost to the source/input divider: 1 - |Zin/(Zs+Zin)|."""
    return 1 - np.abs(z_in / (z_source + z_in))


# ---------------------------------------------------------------------------- interference (Chapter 4)
def body_cm_voltage(v_mains=230.0, f=50.0, c_pow=3e-12, c_body=200e-12, z_ground=None):
    """Common-mode voltage of the body (Vrms). With z_ground=None the body floats and the two
    capacitors divide the mains; otherwise the displacement current flows through z_ground."""
    w = 2 * np.pi * f
    if z_ground is None:
        return v_mains * c_pow / (c_pow + c_body)
    i_d = v_mains * w * c_pow                         # displacement current (A rms)
    return i_d * abs(z_ground)


def cm_to_dm(v_cm, z_e1, z_e2, z_cm):
    """Differential voltage created by electrode imbalance: each input sees a divider between its
    electrode impedance and the amplifier's common-mode input impedance z_cm."""
    return abs(v_cm * (z_cm / (z_e2 + z_cm) - z_cm / (z_e1 + z_cm)))


def required_cmrr_db(v_cm_rms, v_out_pp_limit):
    """CMRR needed so a sinusoidal common-mode v_cm_rms appears below v_out_pp_limit (peak-to-peak)."""
    return 20 * np.log10(2 * np.sqrt(2) * v_cm_rms / v_out_pp_limit)


def cmrr_test_zcm(f=50.0, v_cm_rms=10.0, limit_pp=1e-3, r=51e3, c=47e-9):
    """Common-mode input impedance (ohm) and the equivalent capacitance (F) needed so that the
    imbalance network alone stays within the CMRR-test limit if the full test voltage were common
    mode at the electrodes (a worst-case bound, see Chapter 4)."""
    dz = abs(r / (1 + 1j * 2 * np.pi * f * r * c))
    zcm = dz * 2 * np.sqrt(2) * v_cm_rms / limit_pp
    return zcm, 1 / (2 * np.pi * f * zcm), dz


# ---------------------------------------------------------------------------- safety (Chapter 4)
# Patient leakage / patient auxiliary current limits of IEC 60601-1 in normal condition (A, a.c.),
# with the frequency allowance above 1 kHz (limit x f/1 kHz up to 100 kHz, never above 10 mA).
# Summarised for teaching; always check the edition of the standard that applies to your device.
PATIENT_LIMITS_NC = {"B": 100e-6, "BF": 100e-6, "CF": 10e-6}
PATIENT_LIMITS_SFC = {"B": 500e-6, "BF": 500e-6, "CF": 50e-6}
PATIENT_LIMIT_DC = 10e-6


def patient_current_limit(f, part="CF", single_fault=False):
    base = (PATIENT_LIMITS_SFC if single_fault else PATIENT_LIMITS_NC)[part]
    f = np.asarray(f, float)
    scale = np.clip(f / 1e3, 1.0, 100.0)
    return np.minimum(base * scale, 10e-3)


# ---------------------------------------------------------------------------- analysis helpers
def psd(x, fs, seg_s=4.0):
    """One-sided Welch PSD (V^2/Hz) with Hann windows of seg_s seconds."""
    nper = int(min(len(x), seg_s * fs))
    return sps.welch(x, fs=fs, nperseg=nper, detrend="constant")


def band_edges(f, p, lo=0.025, hi=0.975):
    """Frequencies below which lo and hi of the total power lie (a power-based bandwidth)."""
    c = np.cumsum(p)
    c = c / c[-1]
    return f[np.searchsorted(c, lo)], f[np.searchsorted(c, hi)]


def amplitude_stats(x):
    """Robust amplitude numbers: peak-to-peak between the 0.5th and 99.5th percentiles, and RMS."""
    x = np.asarray(x, float) - np.median(x)
    lo, hi = np.percentile(x, [0.5, 99.5])
    return dict(pp=hi - lo, rms=np.std(x))


# ---------------------------------------------------------------------------- converters (Part III)
def quantize(x, nbits, vfs=1.0):
    """Ideal mid-rise quantiser over [-vfs, +vfs]: returns the reconstructed value (V).
    One LSB is 2*vfs/2**nbits; inputs outside the range clip to the end codes."""
    lsb = 2.0 * vfs / 2 ** nbits
    code = np.clip(np.floor(np.asarray(x, float) / lsb), -2 ** (nbits - 1), 2 ** (nbits - 1) - 1)
    return (code + 0.5) * lsb


def sqnr_ideal_db(nbits):
    """SQNR of an ideal N-bit quantiser driven by a full-scale sine (dB)."""
    return 6.02 * nbits + 1.76


def enob(sndr_db):
    """Effective number of bits from a measured SNDR (dB)."""
    return (np.asarray(sndr_db, float) - 1.76) / 6.02


def alias_freq(f, fs):
    """Frequency (Hz) at which a tone at f appears after sampling at fs (folded into 0..fs/2)."""
    r = np.mod(np.asarray(f, float), fs)
    return np.minimum(r, fs - r)


def butter_atten_db(f, fc, order):
    """Attenuation (dB, positive) of an order-n Butterworth low-pass with corner fc at frequency f."""
    return 10 * np.log10(1 + (np.asarray(f, float) / fc) ** (2 * order))


def sqnr_os_db(nbits, osr, order=0):
    """Peak SQNR (dB) of an N-bit quantiser oversampled by osr, with order-L noise shaping
    (L = 0: plain oversampling, +3 dB per octave; L >= 1: NTF = (1 - z^-1)^L, linear model)."""
    L = order
    return (6.02 * nbits + 1.76 - 10 * np.log10(np.pi ** (2 * L) / (2 * L + 1))
            + (20 * L + 10) * np.log10(np.asarray(osr, float)))


def jitter_snr_db(f_in, sigma_t):
    """SNR (dB) limit set by rms sampling-clock jitter sigma_t (s) on a full-scale sine at f_in (Hz)."""
    return -20 * np.log10(2 * np.pi * np.asarray(f_in, float) * sigma_t)


def coherent_tone(f_target, fs, n):
    """Frequency (Hz) and cycle count M of a tone near f_target that completes an odd number of
    cycles in an n-point record (M odd, so it is coprime with a power-of-two n)."""
    m = max(1, int(round(f_target * n / fs)))
    if m % 2 == 0:
        m += 1
    return m * fs / n, m


def tone_metrics(y, m, n_harm=5, band_bins=None):
    """SNDR, SNR, THD and SFDR (dB) of a coherently sampled record y with the tone in bin m
    (rectangular window). band_bins limits the noise sum to bins 1..band_bins (oversampled case)."""
    y = np.asarray(y, float)
    n = len(y)
    p = np.abs(np.fft.rfft(y - np.mean(y))) ** 2
    p[0] = 0.0
    top = len(p) - 1 if band_bins is None else band_bins
    ps = p[m]
    harm = [h * m % n for h in range(2, n_harm + 2)]
    harm = sorted({min(k, n - k) for k in harm} - {0, m})
    harm_in = [k for k in harm if k <= top]
    pn_all = p[1:top + 1].sum() - ps
    ph = sum(p[k] for k in harm_in)
    spur = np.delete(p[1:top + 1], m - 1).max() if top >= m else p[1:top + 1].max()
    return dict(sndr=10 * np.log10(ps / pn_all), snr=10 * np.log10(ps / (pn_all - ph)),
                thd=10 * np.log10(ph / ps) if ph > 0 else -np.inf, sfdr=10 * np.log10(ps / spur))


def cdac_weights(nbits, sigma_u=0.0, seed=0):
    """Actual bit weights (in LSB) of a binary-weighted capacitive DAC built from unit capacitors
    whose values scatter by sigma_u (relative, rms). Bit k has 2**k units; one dummy unit makes
    the total 2**nbits units. Weights are normalised to the total, as the charge redistribution does."""
    rng = _rng(seed)
    caps = [rng.normal(1.0, sigma_u, 2 ** k).sum() for k in range(nbits)]
    dummy = rng.normal(1.0, sigma_u)
    total = sum(caps) + dummy
    return np.array(caps) / total * 2 ** nbits


def sar_convert(x, nbits, weights=None, vfs=1.0):
    """Behavioural SAR conversion of x (V) over [-vfs, +vfs] with bit weights in LSB (MSB last
    index = nbits-1). The comparator decides with the real weights; the code is read as ideal binary."""
    w = 2.0 ** np.arange(nbits) if weights is None else np.asarray(weights, float)
    u = (np.asarray(x, float) + vfs) / (2 * vfs) * 2 ** nbits      # input in LSB, 0 .. 2^N
    acc = np.zeros_like(u)
    code = np.zeros(u.shape, dtype=np.int64)
    for k in range(nbits - 1, -1, -1):
        keep = u >= acc + w[k]
        acc = np.where(keep, acc + w[k], acc)
        code = code + keep * (1 << k)
    return code


def code_to_volts(code, nbits, vfs=1.0):
    """Mid-tread reconstruction of an ideal binary code over [-vfs, +vfs]."""
    return (np.asarray(code, float) + 0.5) * 2 * vfs / 2 ** nbits - vfs


def dnl_inl(codes, nbits):
    """DNL and INL (LSB) from a code histogram of a uniform ramp; the two end codes are dropped."""
    h = np.bincount(np.asarray(codes, int), minlength=2 ** nbits)[1:-1].astype(float)
    dnl = h / h.mean() - 1.0
    inl = np.cumsum(dnl)
    inl = inl - np.linspace(inl[0], inl[-1], len(inl))     # end-point fit
    return dnl, inl


def ktc_cap(nbits, vfs_pp=1.2, osr=1.0, T=T_ROOM):
    """Sampling capacitance (F) whose kT/C noise equals the N-bit quantisation noise, Delta^2/12,
    over a peak-to-peak range vfs_pp; oversampling by osr spreads the noise and divides C by osr."""
    lsb = vfs_pp / 2 ** nbits
    return 12 * K_B * T / lsb ** 2 / osr


def e_thermal_min(snr_db, T=T_ROOM):
    """Thermal (kT/C) lower bound on energy per Nyquist sample, 8 kT * SNR (J), for a full-swing
    sampled sine charged from the supply."""
    return 8 * K_B * T * 10 ** (np.asarray(snr_db, float) / 10)


def fom_walden(p, fs, enob_bits):
    """Walden figure of merit (J per conversion step)."""
    return p / (fs * 2 ** np.asarray(enob_bits, float))


def fom_schreier(sndr_db, bw, p):
    """Schreier figure of merit (dB); bw is the signal bandwidth (fs/2 for a Nyquist converter)."""
    return sndr_db + 10 * np.log10(bw / p)


def ntf_pure(order):
    """NTF(z) = (1 - z^-1)^L as (b, a) coefficient arrays in powers of z^-1."""
    return np.poly(np.ones(order)), np.r_[1.0, np.zeros(order)]


def synth_ntf(order, osr, h_inf=1.5, opt_zeros=False):
    """Low-pass NTF of the given order with |NTF| <= h_inf (the Lee criterion), in the spirit of
    Schreier's synthesizeNTF: zeros at DC (or, with opt_zeros, at the Legendre-root frequencies
    that minimise in-band noise) and Butterworth-high-pass poles scaled until max|NTF| = h_inf.
    Returns (b, a) in powers of z^-1 with b[0] = a[0] = 1."""
    if opt_zeros:
        r = np.polynomial.legendre.leggauss(order)[0]
        zeros = np.exp(1j * r * np.pi / osr)
    else:
        zeros = np.ones(order, complex)
    b = np.real(np.poly(zeros))
    w = np.linspace(0, np.pi, 2048)
    zz = np.exp(1j * w)

    def hmax(wc):
        _, p, _ = sps.butter(order, wc, "high", output="zpk")
        a = np.real(np.poly(p))
        return np.abs(np.polyval(b, zz) / np.polyval(a, zz)).max(), a

    # max|NTF| is large for very low corners (poles near z = 1 lift the NTF at DC when the zeros
    # are spread), dips, then grows towards 2^L; bisect on the rising branch only.
    grid = np.logspace(-4, np.log10(0.999), 80)
    lo, hi = grid[int(np.argmin([hmax(g)[0] for g in grid]))], 0.999
    for _ in range(60):
        mid = np.sqrt(lo * hi)
        if hmax(mid)[0] > h_inf:
            hi = mid
        else:
            lo = mid
    return b, hmax(lo)[1]


def ntf_response(b, a, f):
    """|NTF| at normalised frequency f = f/fs (0..0.5)."""
    z = np.exp(2j * np.pi * np.asarray(f, float))
    return np.abs(np.polyval(b, z) / np.polyval(a, z))


def simulate_dsm(u, b, a, limit=1e3, dither=None):
    """1-bit delta-sigma modulator with NTF = b/a and STF = 1 (error-feedback form; every loop-filter
    topology with the same NTF and STF gives the same output). Output levels +-1, so the input full
    scale is 1. `dither` (array like u) is added at the quantiser input. Returns (v, stable); stable
    is False if the quantiser input exceeded `limit`."""
    c = (np.asarray(b, float) - np.asarray(a, float))[1:]      # (NTF - 1) numerator, z^-1 .. z^-L
    d = np.asarray(a, float)[1:]
    L = len(c)
    e_hist = np.zeros(L)
    y_hist = np.zeros(L)
    v = np.empty(len(u))
    for n, un in enumerate(u):
        yf = c @ e_hist - d @ y_hist
        w = un + yf + (0.0 if dither is None else dither[n])
        if abs(w) > limit:
            v[n:] = np.nan
            return v, False
        vn = 1.0 if w >= 0 else -1.0
        e_hist = np.r_[vn - (w - (0.0 if dither is None else dither[n])), e_hist[:-1]]   # dither is shaped
        y_hist = np.r_[yf, y_hist[:-1]]
        v[n] = vn
    return v, True


def dsm_sqnr(v, m, osr):
    """In-band SQNR (dB) of a modulator output v (length n) holding a tone in bin m. Uses a Hann^2
    window, whose sidelobes fall fast enough for third- and fourth-order shaped noise (a plain Hann
    window leaks out-of-band noise into the band above about 100 dB); signal = bins m-2..m+2,
    noise = in-band bins 4..n/(2 osr) minus the signal bins."""
    n = len(v)
    p = np.abs(np.fft.rfft(v * np.hanning(n) ** 2)) ** 2
    top = int(n / (2 * osr))
    sig = p[m - 2:m + 3].sum()
    noise = p[4:top + 1].sum() - sig
    return 10 * np.log10(sig / noise)


def incremental2(u_dc, m_cycles, a1=0.5, a2=0.5):
    """Second-order incremental delta-sigma (two delaying integrators, feedback to both, 1-bit),
    reset before each conversion; returns the input estimate from a cascade-of-integrators filter
    for each DC input in u_dc (full scale +-1)."""
    u_dc = np.atleast_1d(np.asarray(u_dc, float))
    x1 = np.zeros_like(u_dc)
    x2 = np.zeros_like(u_dc)
    s1 = np.zeros_like(u_dc)        # sum of v
    s2 = np.zeros_like(u_dc)        # sum over n of (sum_{k<n} v)
    run = np.zeros_like(u_dc)
    for _ in range(m_cycles):
        v = np.where(x2 >= 0, 1.0, -1.0)
        s2 += run
        run += v
        s1 += v
        x2 = x2 + a2 * (x1 - v)
        x1 = x1 + a1 * (u_dc - v)
    return (s1 + a1 * s2) / (a1 * m_cycles * (m_cycles - 1) / 2)
