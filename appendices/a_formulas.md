---
title: A. Formula Sheet
parent: Appendices
nav_order: 1
permalink: /appendix/a/
---

# <span class="chapnum">Appendix A</span>Formula Sheet

Every key equation of the tutorial on one page, in the order of the chapters, each with a link to the chapter that derives it and explains its terms.
{: .chapterlead }

This page is generated from the chapters by `tools/build_formula_sheet.py`; the symbols are defined where each equation first appears.

## Part I · Foundations

### [1. Why Biomedical ICs?]({% link chapters/01_why.md %})

**Battery lifetime**

$$
T = \frac{E_\mathrm{batt}}{N P_\mathrm{ch} + P_\mathrm{dig} + P_\mathrm{radio}}
$$

### [2. Bioelectric Signals]({% link chapters/02_signals.md %})

**Nernst potential of an ion of charge z**

$$
E = \frac{kT}{zq}\,\ln\frac{c_\mathrm{out}}{c_\mathrm{in}}
$$

**Ideal converter SQNR, and the bits a dynamic range needs**

$$
\mathrm{SQNR} = 6.02\,N + 1.76\ \text{dB}
\qquad\Rightarrow\qquad
N = \frac{\mathrm{DR} - 1.76}{6.02}
$$

### [3. Electrodes and the Body as a Circuit]({% link chapters/03_electrodes.md %})

**Simplified electrode impedance**

$$
Z_\mathrm{e}(f) = R_\mathrm{s} + \frac{R_\mathrm{p}}{1 + j2\pi f R_\mathrm{p} C_\mathrm{p}},
\qquad f_\mathrm{p} = \frac{1}{2\pi R_\mathrm{p} C_\mathrm{p}}
$$

**Thermal noise of an electrode**

$$
v_\mathrm{n}^2 = \int_{f_1}^{f_2} 4kT\,\mathrm{Re}\{Z_\mathrm{e}(f)\}\,df
$$

**Loss to the input divider**

$$
\frac{V_\mathrm{in}}{V_\mathrm{electrode}} = \frac{Z_\mathrm{in}}{Z_\mathrm{e} + Z_\mathrm{in}}
$$

### [4. Interference, Safety and Standards]({% link chapters/04_interference.md %})

**Body common-mode voltage**

$$
i_\mathrm{d} = 2\pi f\,C_\mathrm{pow}\,V_\mathrm{mains},
\qquad
V_\mathrm{cm} \approx i_\mathrm{d}\,\lvert Z_3\rvert
\quad\text{(with a ground electrode)}
$$

**Common mode to differential mode, and the effective CMRR**

$$
V_\mathrm{dm} \approx V_\mathrm{cm}\,\frac{\Delta Z}{Z_\mathrm{cm}},
\qquad
\frac{1}{\mathrm{CMRR}_\mathrm{eff}} = \frac{1}{\mathrm{CMRR}_\mathrm{amp}} + \frac{\Delta Z}{Z_\mathrm{cm}}
$$

## Part II · The analog front-end

### [5. Devices for Microwatt Design]({% link chapters/05_devices.md %})

**Transconductance efficiency across inversion**

$$
\frac{g_\mathrm{m}}{I_\mathrm{D}} = \frac{1}{nU_T}\cdot\frac{2}{1 + \sqrt{1 + 4\,IC}}
$$

**Flicker noise and its corner frequency**

$$
\overline{v_{n,1/f}^2}(f) = \frac{K}{W L\, f}, \qquad f_\mathrm{c} = \frac{K}{WL\,\overline{v_{n,\mathrm{th}}^2}}
$$

**Pelgrom's law**

$$
\sigma(\Delta V_\mathrm{T}) = \frac{A_{V_T}}{\sqrt{WL}}, \qquad \sigma\!\left(\frac{\Delta\beta}{\beta}\right) = \frac{A_\beta}{\sqrt{WL}}
$$

### [6. Noise and the Noise–Power Trade-off]({% link chapters/06_noise.md %})

**Noise bandwidth and 1/f integration**

$$
B_n = \frac{\pi}{2} f_\mathrm{c}\ \text{(1st order)}, \qquad B_n = \frac{\pi}{2\sqrt2} f_\mathrm{c} = 1.11 f_\mathrm{c}\ \text{(2nd-order Butterworth)}, \qquad \int_{f_\mathrm{L}}^{f_\mathrm{H}} \frac{K}{WL\,f}\,df = \frac{K}{WL}\ln\frac{f_\mathrm{H}}{f_\mathrm{L}}
$$

**Noise efficiency factor and power efficiency factor**

$$
\mathrm{NEF} = V_\mathrm{ni,rms}\sqrt{\frac{2\,I_\mathrm{tot}}{\pi\, U_T\, 4kT\, \mathrm{BW}}}, \qquad \mathrm{PEF} = \mathrm{NEF}^2\,V_\mathrm{DD}
$$

**NEF limit of a weak-inversion MOS pair**

$$
\mathrm{NEF}_\mathrm{min} = \sqrt2\,n \approx 1.73 \quad \text{for SG13G2 } (n = 1.22)
$$

### [7. Instrumentation Amplifier Architectures]({% link chapters/07_ia.md %})

**CMRR of the three-op-amp IA**

$$
\mathrm{CMRR_{DA}} \approx \frac{1 + G_2}{4t}, \qquad \frac{1}{\mathrm{CMRR}_\mathrm{IA}} \approx \frac{1}{G_1}\left(\frac{1}{\mathrm{CMRR_{DA}}} + \frac{1}{\mathrm{CMRR_{op}}}\right)
$$

**Gain of a capacitively coupled IA**

$$
G = \frac{C_\mathrm{in}}{C_\mathrm{fb}}, \qquad f_\mathrm{HP} = \frac{1}{2\pi R_\mathrm{fb} C_\mathrm{fb}}
$$

### [8. The AC-Coupled Biopotential LNA]({% link chapters/08_lna.md %})

**Gain and band edges of the capacitive-feedback LNA**

$$
A_\mathrm{M} = \frac{C_1}{C_2}, \qquad f_\mathrm{L} = \frac{1}{2\pi R_\mathrm{pr} C_2}, \qquad f_\mathrm{H} = \frac{g_\mathrm{m}}{2\pi A_\mathrm{M} C_\mathrm{L}}
$$

**Capacitive noise gain**

$$
v_{ni} = v_\mathrm{n,OTA}\,\frac{C_1 + C_2 + C_\mathrm{in}}{C_1}
$$

### [9. Chopper Stabilisation and Offset Cancellation]({% link chapters/09_chopper.md %})

**What chopping leaves at baseband**

$$
S_\mathrm{out}(f) = \sum_{k\ \mathrm{odd}} \frac{4}{\pi^2 k^2}\Bigl[S_\mathrm{amp}(kf_\mathrm{ch} - f) + S_\mathrm{amp}(kf_\mathrm{ch} + f)\Bigr] \;\approx\; S_\mathrm{white}\Bigl(1 + \frac{f_\mathrm{c}}{f_\mathrm{ch}}\cdot 0.85\Bigr)
$$

**Input impedance of a chopped capacitively coupled IA**

$$
Z_\mathrm{in,diff} \approx \frac{1}{2 f_\mathrm{ch} C_\mathrm{in}}
$$

### [10. Input Impedance, DC Servo Loops and Offset Rejection]({% link chapters/10_dsl.md %})

**Input impedance before and after chopping**

$$
Z_\mathrm{in,diff} = \frac{2}{j\omega C_\mathrm{in}}\ \text{(unchopped)}, \qquad Z_\mathrm{in,diff} \approx \frac{1}{2 f_\mathrm{ch} C_\mathrm{in}}\ \text{(chopped)}
$$

**DC servo loop range and high-pass corner**

$$
C_\mathrm{DSL} \ge \frac{V_\mathrm{off}}{V_\mathrm{DSL}}\,C_\mathrm{in}, \qquad f_\mathrm{HP} = \frac{C_\mathrm{DSL}}{C_\mathrm{fb}}\cdot\frac{1}{2\pi\tau_\mathrm{int}}
$$

### [11. Filters, PGAs and Anti-Aliasing]({% link chapters/11_filters.md %})

**Gm-C and switched-capacitor corners**

$$
f_\mathrm{c} = \frac{g_\mathrm{m}}{2\pi C}\ \text{(Gm-C)}, \qquad f_\mathrm{c} \approx \frac{f_\mathrm{s}}{2\pi}\,\frac{C_1}{C_2}\ \text{(switched-capacitor integrator)}
$$

### [12. Common-Mode Control and Electrode Monitoring]({% link chapters/12_cmcontrol.md %})

**Common mode with a right-leg drive**

$$
V_\mathrm{cm,RLD} = \frac{V_\mathrm{cm}}{1 + A(f)}, \qquad V_\mathrm{dm} = \frac{V_\mathrm{cm}}{1 + A}\left(\frac{\Delta Z}{Z_\mathrm{cm}} + \frac{1}{\mathrm{CMRR_{int}}}\right)
$$

## Part III · Data converters

### [13. Sampling and Quantisation]({% link chapters/13_sampling.md %})

**Where a tone lands after sampling**

$$
f_\mathrm{alias} = \bigl\lvert f - k f_\mathrm{s} \bigr\rvert, \qquad k = \mathrm{round}\!\left(\frac{f}{f_\mathrm{s}}\right), \qquad 0 \le f_\mathrm{alias} \le \frac{f_\mathrm{s}}{2}
$$

**Quantisation-limited SNR and effective number of bits**

$$
\mathrm{SQNR} = 6.02N + 1.76\ \mathrm{dB}, \qquad \mathrm{ENOB} = \frac{\mathrm{SNDR} - 1.76}{6.02}
$$

**Jitter-limited SNR**

$$
\mathrm{SNR}_\mathrm{jitter} = -20\log_{10}\!\left(2\pi f_\mathrm{in}\,\sigma_t\right)
$$

### [14. Specifications, Figures of Merit and Architecture Choice]({% link chapters/14_adcspecs.md %})

**Spectral metrics of a converter**

$$
\mathrm{SNR} = 10\log_{10}\frac{P_\mathrm{sig}}{P_\mathrm{noise}}, \quad
\mathrm{THD} = 10\log_{10}\frac{P_\mathrm{harm}}{P_\mathrm{sig}}, \quad
\mathrm{SNDR} = 10\log_{10}\frac{P_\mathrm{sig}}{P_\mathrm{noise} + P_\mathrm{harm}}, \quad
\mathrm{SFDR} = 10\log_{10}\frac{P_\mathrm{sig}}{P_\mathrm{largest\ spur}}
$$

**Walden and Schreier figures of merit**

$$
\mathrm{FoM_W} = \frac{P}{f_\mathrm{s}\,2^{\mathrm{ENOB}}}, \qquad \mathrm{FoM_S} = \mathrm{SNDR} + 10\log_{10}\!\frac{\mathrm{BW}}{P}
$$

with $$\mathrm{BW} = f_\mathrm{s}/2$$ for a Nyquist converter and the signal bandwidth for an oversampled one.

**kT/C-limited capacitance and the thermal energy bound**

$$
C \ge \frac{12\,kT\,2^{2N}}{V_\mathrm{FS}^2\;\mathrm{OSR}}, \qquad E_\mathrm{sample} \ge 8\,kT\cdot\mathrm{SNR}
$$

### [15. Sample-and-Hold Circuits and Switches]({% link chapters/15_switches.md %})

**Sampling capacitor for N bits (differential)**

$$
\frac{2kT}{C_\mathrm{s}} \le \frac{\Delta^2}{12} \quad\Rightarrow\quad C_\mathrm{s} \ge \frac{24\,kT}{\Delta^2}, \qquad \Delta = \frac{V_\mathrm{FS,diff}}{2^N}
$$

### [16. Comparators]({% link chapters/16_comparators.md %})

**Input-referred noise of an integrating comparator (weak inversion)**

$$
\sigma_v = 2\,nU_T\sqrt{\frac{q}{Q_\mathrm{int}}} = \sqrt{\frac{kT}{C_\mathrm{L}}\cdot\frac{4n^2U_T}{\Delta V}}, \qquad Q_\mathrm{int} = C_\mathrm{L}\Delta V
$$

### [17. Capacitive DACs and References]({% link chapters/17_cdac.md %})

**Unit capacitor from matching**

$$
\sigma_\mathrm{DNL,mid} \approx \sigma_u\sqrt{2^N}, \qquad \sigma_u = \frac{A_C}{\sqrt{A_\mathrm{unit}}} \quad\Rightarrow\quad A_\mathrm{unit} \ge \left(\frac{A_C\sqrt{2^N}}{\sigma_\mathrm{DNL,max}}\right)^2
$$

### [18. The SAR ADC]({% link chapters/18_sar.md %})

**SAR timing**

$$
T_\mathrm{conv} = T_\mathrm{sample} + M\,(t_\mathrm{DAC} + t_\mathrm{comp} + t_\mathrm{logic}), \qquad M \ge N
$$

### [19. ΔΣ Modulation: Theory]({% link chapters/19_dstheory.md %})

**Peak SQNR of an order-\(L\) modulator (linear model)**

$$
\mathrm{SQNR}_{L} \approx 6.02N + 1.76 - 10\log_{10}\!\frac{\pi^{2L}}{2L+1} + (20L+10)\log_{10}\mathrm{OSR}\ \mathrm{dB}
$$

**Error of a second-order incremental converter**

$$
\lvert u - \hat u \rvert \le \frac{\lvert x_2\rvert_\mathrm{max}}{a_1 a_2\,M(M-1)/2}, \qquad \hat u = \frac{\sum_n v[n] + a_1 \sum_n \sum_{k<n} v[k]}{a_1\,M(M-1)/2}
$$

### [20. ΔΣ Circuits: Discrete-Time, Continuous-Time and Incremental]({% link chapters/20_dscircuits.md %})

**Sampling capacitor and OTA of an incremental integrator**

$$
C_\mathrm{s} \ge \frac{16\,kT}{3M\,\sigma_\mathrm{target}^2}, \qquad \mathrm{GBW}\cdot\beta \ge \frac{n_\tau}{2\pi\,T_\mathrm{clk}/2}
$$

### [22. Testing and Characterising ADCs]({% link chapters/22_adctest.md %})

**Coherent input frequency**

$$
f_\mathrm{in} = \frac{M}{N_\mathrm{FFT}}\,f_\mathrm{s}, \qquad M \text{ and } N_\mathrm{FFT} \text{ co-prime (an odd } M \text{ with } N_\mathrm{FFT} = 2^k\text{)}
$$

## Part IV · Biosignal processing and systems

### [23. A DSP Toolkit for Biosignals]({% link chapters/23_dsp.md %})

**Delay of a linear-phase FIR**

$$
\tau_\mathrm{g} = \frac{N-1}{2f_\mathrm{s}}, \qquad N - 1 \approx \frac{(A - 7.95)\,f_\mathrm{s}}{14.36\,\Delta f} \quad\Rightarrow\quad \tau_\mathrm{g} \approx \frac{A - 7.95}{28.7\,\Delta f}
$$

**A second-order notch, its width and its time constant**

$$
H(z) = \frac{1 - 2\cos\omega_0\,z^{-1} + z^{-2}}{1 - 2r\cos\omega_0\,z^{-1} + r^2 z^{-2}}, \qquad \omega_0 = \frac{2\pi f_0}{f_\mathrm{s}}
$$

$$
\Delta f_{-3\,\mathrm{dB}} \approx \frac{(1 - r)\,f_\mathrm{s}}{\pi}, \qquad \tau = \frac{1}{(1 - r)\,f_\mathrm{s}} = \frac{1}{\pi\,\Delta f_{-3\,\mathrm{dB}}}
$$

**Why narrow filters need long words**

$$
\text{pole radius } r \approx 1 - \frac{2\pi f_\mathrm{c}}{f_\mathrm{s}} \quad\Rightarrow\quad \text{coefficients must resolve } 1 - r \approx 6\times10^{-3}\ (f_\mathrm{c} = 0.5\ \text{Hz},\ f_\mathrm{s} = 500\ \text{S/s})
$$

### [24. ECG Processing]({% link chapters/24_ecg.md %})

**The Pan–Tompkins detector at 200 S/s**

$$
H_\mathrm{LP}(z) = \frac{\left(1 - z^{-6}\right)^2}{\left(1 - z^{-1}\right)^2}, \qquad H_\mathrm{HP}(z) = z^{-16} - \frac{1}{32}\,\frac{1 - z^{-32}}{1 - z^{-1}}
$$

$$
d[n] = \tfrac{1}{8}\bigl(2x[n] + x[n-1] - x[n-3] - 2x[n-4]\bigr), \qquad y[n] = \frac{1}{N}\sum_{k=0}^{N-1} d^2[n-k], \qquad N = 0.15\,f_\mathrm{s}
$$

$$
\mathrm{THR} = \mathrm{NPKI} + 0.25\,(\mathrm{SPKI} - \mathrm{NPKI})
$$

$$
\mathrm{SPKI} \leftarrow 0.125\,P + 0.875\,\mathrm{SPKI}\ \ (P > \mathrm{THR}), \qquad \text{else}\ \ \mathrm{NPKI} \leftarrow 0.125\,P + 0.875\,\mathrm{NPKI}
$$

**Heart-rate variability**

$$
\mathrm{SDNN} = \sqrt{\frac{1}{N-1}\sum_{i=1}^{N}\bigl(\mathrm{RR}_i - \overline{\mathrm{RR}}\bigr)^2}, \qquad \mathrm{RMSSD} = \sqrt{\frac{1}{N-1}\sum_{i=1}^{N-1}\bigl(\mathrm{RR}_{i+1} - \mathrm{RR}_i\bigr)^2}
$$

$$
\mathrm{LF} = \int_{0.04\ \mathrm{Hz}}^{0.15\ \mathrm{Hz}} S_\mathrm{RR}(f)\,df, \qquad \mathrm{HF} = \int_{0.15\ \mathrm{Hz}}^{0.4\ \mathrm{Hz}} S_\mathrm{RR}(f)\,df
$$

**Sensitivity and positive predictivity**

$$
\mathrm{Se} = \frac{\mathrm{TP}}{\mathrm{TP} + \mathrm{FN}}, \qquad \mathrm{PPV} = \frac{\mathrm{TP}}{\mathrm{TP} + \mathrm{FP}}
$$

### [25. EEG Processing and Brain–Computer Interfaces]({% link chapters/25_eeg.md %})

**Band power and relative band power**

$$
P_\mathrm{band} = \int_{f_1}^{f_2} S(f)\,df \approx \Delta f \sum_{f_1 \le f_k < f_2} \hat S(f_k), \qquad p_\mathrm{rel} = \frac{P_\mathrm{band}}{P_\mathrm{total}}
$$

**Welch estimate: resolution and scatter**

$$
\Delta f = \frac{f_\mathrm{s}}{N} = \frac{1}{T_\mathrm{seg}}, \qquad \frac{\sigma_{\hat S}}{S} \approx \frac{1}{\sqrt{K}}, \qquad \frac{\sigma_{\hat P}}{P} \approx \frac{1}{\sqrt{B\,T}}
$$

**Detecting a steady-state line**

$$
\mathrm{SNR}(f_0) = \frac{\hat S(f_0)}{\overline{\hat S}_\mathrm{neighbours}} \approx 1 + \frac{A_\mathrm{rms}^2\,T}{\mathrm{ENBW} \cdot S_\mathrm{n}(f_0)}
$$

### [26. EMG and Neural Spike Processing]({% link chapters/26_emg.md %})

**Time-domain EMG features over a window of \(N\) samples**

$$
\begin{aligned}
\mathrm{MAV} &= \frac{1}{N}\sum_{n=1}^{N}\lvert x[n]\rvert, \qquad
\mathrm{RMS} = \sqrt{\frac{1}{N}\sum_{n=1}^{N} x[n]^2}, \qquad
\mathrm{WL} = \sum_{n=2}^{N}\lvert d[n]\rvert,\\
\mathrm{ZC} &= \#\bigl\{n : x[n]\,x[n-1] < 0 \ \text{and}\ \lvert d[n]\rvert \ge T\bigr\},\\
\mathrm{SSC} &= \#\bigl\{n : d[n]\,d[n-1] < 0 \ \text{and}\ \max\bigl(\lvert d[n]\rvert, \lvert d[n-1]\rvert\bigr) \ge T\bigr\}
\end{aligned}
$$

**Robust noise estimate, threshold and false-alarm rate**

$$
\hat\sigma = \frac{\operatorname{median}\lvert x[n]\rvert}{0.6745}, \qquad \theta = -k\,\hat\sigma \quad (k = 4 \ldots 5), \qquad R_\mathrm{FA} \approx f_\mathrm{s}\,Q(k)
$$

**Nonlinear energy operator**

$$
\psi[n] = x[n]^2 - x[n-1]\,x[n+1]
$$

### [27. On-Chip Processing and System Integration]({% link chapters/27_soc.md %})

**BLE throughput**

$$R = \frac{N_\mathrm{pkt}\, 8 L}{T_\mathrm{CI}}, \qquad N_\mathrm{pkt} \le \frac{T_\mathrm{CI}}{t_\mathrm{data} + t_\mathrm{IFS} + t_\mathrm{ack} + t_\mathrm{IFS}}$$

$$L$$ is the ATT payload (20 or 244 bytes), $$N_\mathrm{pkt}$$ the packets per event, $$t_\mathrm{IFS}$$ = 150 µs the gap between packets. In practice the phone also caps $$N_\mathrm{pkt}$$, often at four to seven, and sets a minimum interval, often 15 ms.

### [28. Bioimpedance Sensing and IQ Demodulation]({% link chapters/28_bioz.md %})

**Cole model of tissue impedance**

$$
Z(f) = R_\infty + \frac{R_0 - R_\infty}{1 + (jf/f_\mathrm{c})^{\alpha}}
$$

**IQ demodulation**

$$
I = \frac{\lvert Z\rvert I_\mathrm{exc}}{2}\cos\varphi, \quad Q = \frac{\lvert Z\rvert I_\mathrm{exc}}{2}\sin\varphi, \qquad \lvert Z\rvert = \frac{2\sqrt{I^2 + Q^2}}{I_\mathrm{exc}}, \quad \varphi = \operatorname{atan2}(Q, I)
$$

## Part VI · Wearable systems

### [31. Signal Quality and Motion Artefacts]({% link chapters/31_quality.md %})

**Normalised LMS**

$$e[n] = d[n] - \mathbf{w}^\mathsf{T}\mathbf{x}[n], \qquad \mathbf{w} \leftarrow \mathbf{w} + \frac{\mu\, e[n]\, \mathbf{x}[n]}{\delta + \mathbf{x}^\mathsf{T}[n]\,\mathbf{x}[n]}$$

$$\mathbf{x}$$ holds the last $$L$$ samples of every reference, $$0 < \mu < 2$$ is the step size and $$\delta$$ regularises the division.

### [33. Closed-Loop Systems]({% link chapters/33_closedloop.md %})

**Phase error from latency**

$$\Delta\varphi = 360^\circ \cdot f \cdot \tau$$

A latency $$\tau$$ that is not compensated becomes a phase error $$\Delta\varphi$$ at the rhythm's frequency $$f$$; a jitter in $$\tau$$ becomes a phase jitter by the same rule.
