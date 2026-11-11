---
title: 31. Hands-on Labs
parent: "Part V · Putting It Together"
nav_order: 31
permalink: /part-5/ch31/
chapter: 31
---

# <span class="chapnum">Chapter 31</span>Hands-on Labs

Fifteen labs in three tracks, and a capstone: Python models first, then SG13G2 circuits, then the whole chain on real recordings.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. Labs 1 and 2 will be written in full in build stage 1; every other lab is written in the stage of its chapters. The goals and deliverables below are fixed.

</div>

The labs use only free tools. **Track A** (Python) models signals, interference and converters with NumPy, SciPy, wfdb and python-deltasigma {% include cite.html keys="pydeltasigma" %}. **Track B** (SG13G2) designs transistor-level circuits with Xschem and ngspice in the IHP open PDK {% include cite.html keys="ihppdk" %}. **Track C** (systems) runs the whole chain on real recordings and takes blocks to layout. The Python labs live in [`labs/python/`](https://github.com/bricd-org/biomedical-ic-design/tree/main/labs/python) and share one module, `biosig.py`.

**Table 31.1. The fifteen labs.**
{: .tabcaption #tab-31-1 }

| Lab | Track | Chapters | What you do | Deliverable |
|---|---|---|---|---|
| [1](#lab-1) Biosignal explorer | A | 2 | Load MIT-BIH, CHB-MIT and NinaPro recordings; plot traces and spectra; measure amplitude and bandwidth | Your version of the Chapter 2 amplitude-versus-bandwidth table |
| [2](#lab-2) Electrodes and interference | A | 3–4, 12 | Model the body, Randles electrodes and a 51 kΩ‖47 nF imbalance; inject 10 Vrms of mains common mode; sweep CMRR and input impedance; add right-leg drive | Interference versus CMRR and imbalance; the required CMRR |
| [3](#lab-3) Devices in weak inversion | B | 5–6 | gm/ID curves, flicker noise versus W·L, HBT versus MOS input noise | Lookup tables and noise plots, reused in Labs 4 and 5 |
| [4](#lab-4) The Harrison LNA | B | 6, 8 | Capacitive-feedback amplifier with pseudo-resistors; AC, noise and transient simulations; NEF | An LNA that meets the spec; NEF versus bias current |
| [5](#lab-5) Chopper amplifier | B | 9–10 | Input and output choppers and a DC servo loop; 1/f noise removal, ripple, input impedance; ±300 mV offset | Noise spectra before and after chopping, ripple and input-impedance plots |
| [6](#lab-6) Ideal ADC and spectral testing | A | 13–14, 22 | Quantise sine waves; coherent sampling and windows; SNDR, SFDR and ENOB; histogram DNL and INL with capacitor mismatch | A reusable `adctest.py` |
| [7](#lab-7) StrongARM comparator | B | 16 | Design; Monte Carlo offset; transient-noise input noise; energy per decision | A comparator with offset and noise numbers |
| [8](#lab-8) SAR ADC | B | 15, 17–18 | Bootstrapped sample-and-hold, monotonic CDAC, Verilog SAR logic; mixed-signal simulation; `adctest.py` | A 10- to 12-bit SAR with its ENOB and figure of merit |
| [9](#lab-9) ΔΣ by design | A | 19–20 | First-, second- and third-order NTFs; SQNR versus OSR; incremental mode; fixed-point CIC filter | NTF, coefficients and decimator for the ECG/EEG channel |
| [10](#lab-10) Switched-capacitor ΔΣ | B | 20 | The Lab 9 loop with switched-capacitor integrators and a 1-bit quantiser, compared with the ideal model | Transistor-level spectrum and SQNR |
| [11](#lab-11) ECG chain end to end | C | 24, 29 | MIT-BIH and the Noise Stress Test through a behavioural front-end and ADC; Pan–Tompkins QRS detection | QRS sensitivity and positive predictive value versus ADC bits and input noise |
| [12](#lab-12) EEG seizure detection | C | 25, 27 | Band-power features on CHB-MIT; a simple classifier; reduced word length and sample rate | Latency and accuracy versus bits and a power proxy |
| [13](#lab-13) EMG gesture recognition | C | 26 | MAV, WL, ZC and SSC features on NinaPro; LDA or SVM; fixed point | Accuracy versus channels, sample rate and resolution |
| [14](#lab-14) Layout to GDS | C | 30 | Comparator and CDAC in KLayout; DRC, LVS and extraction with the JKU template; post-layout simulation | Clean DRC and LVS; post-layout versus schematic |
| [15](#lab-15) Bioimpedance IQ readout | B | 28 | Cole tissue model, tetrapolar measurement and digital IQ in Python; then an SG13G2 current source and square-wave IQ demodulator | Cole plot, ΔZ resolution versus current, analog versus digital IQ error |

## Setting up {#setup}

A Python virtual environment for Track A and C (NumPy, SciPy, Matplotlib, wfdb), and the IIC-OSIC-TOOLS container {% include cite.html keys="iicosic" %} with the SG13G2 PDK for Track B and Lab 14.

## Lab 1 · Biosignal explorer {#lab-1}

Load MIT-BIH record 100 {% include cite.html keys="mitbih" %}, a CHB-MIT EEG recording {% include cite.html keys="chbmit" %} and NinaPro EMG {% include cite.html keys="ninapro" %} (or the synthetic signals of `biosig.py` when offline); plot traces and spectra; measure amplitude and bandwidth; write your own version of the Chapter 2 table. Goes with [Chapter 2]({% link chapters/02_signals.md %}).

## Lab 2 · Electrodes and interference {#lab-2}

A phasor model of the body, the electrodes and the amplifier: inject 10 Vrms of mains common mode, sweep CMRR, common-mode impedance and imbalance, add a behavioural right-leg drive, and print the CMRR the design needs. Goes with Chapters [3]({% link chapters/03_electrodes.md %}) and [4]({% link chapters/04_interference.md %}).

## Lab 3 · Devices in weak inversion {#lab-3}

gm/ID lookup tables for SG13G2 MOS devices, flicker noise versus gate area, and HBT versus MOS input noise. Goes with Chapters [5]({% link chapters/05_devices.md %}) and [6]({% link chapters/06_noise.md %}).

## Lab 4 · The Harrison LNA {#lab-4}

The capacitive-feedback LNA with pseudo-resistors: AC, noise and transient simulations, and the NEF versus bias current. Goes with [Chapter 8]({% link chapters/08_lna.md %}).

## Lab 5 · Chopper amplifier {#lab-5}

Input and output choppers with a DC servo loop: 1/f noise removal, output ripple, input-impedance loss and ±300 mV offset tolerance. Goes with Chapters [9]({% link chapters/09_chopper.md %}) and [10]({% link chapters/10_dsl.md %}).

## Lab 6 · Ideal ADC and spectral testing {#lab-6}

Quantise sine waves, apply coherent sampling and windows, compute SNDR, SFDR and ENOB, and histogram DNL and INL with injected capacitor mismatch; the result is the `adctest.py` module that Labs 8 and 10 reuse. Goes with Chapters [13]({% link chapters/13_sampling.md %}), [14]({% link chapters/14_adcspecs.md %}) and [22]({% link chapters/22_adctest.md %}).

## Lab 7 · StrongARM comparator {#lab-7}

Design the comparator, find its offset with Monte Carlo and its input-referred noise with transient noise, and measure the energy per decision. Goes with [Chapter 16]({% link chapters/16_comparators.md %}).

## Lab 8 · SAR ADC {#lab-8}

Combine a bootstrapped sample-and-hold, a monotonic CDAC and Verilog SAR logic into a 10- to 12-bit SAR, and measure its ENOB and figure of merit with `adctest.py`. Goes with Chapters [15]({% link chapters/15_switches.md %}), [17]({% link chapters/17_cdac.md %}) and [18]({% link chapters/18_sar.md %}).

## Lab 9 · ΔΣ by design {#lab-9}

Synthesise first- to third-order noise-transfer functions with python-deltasigma, plot SQNR versus OSR, run the loop in incremental mode and design a fixed-point CIC decimator. Goes with Chapters [19]({% link chapters/19_dstheory.md %}) and [20]({% link chapters/20_dscircuits.md %}).

## Lab 10 · Switched-capacitor ΔΣ {#lab-10}

Build the Lab 9 loop with switched-capacitor integrators and a 1-bit quantiser and compare it with the ideal model. Goes with [Chapter 20]({% link chapters/20_dscircuits.md %}).

## Lab 11 · ECG chain end to end {#lab-11}

Run MIT-BIH and the Noise Stress Test database {% include cite.html keys="nstdb" %} through a behavioural front-end and ADC, detect QRS complexes with Pan–Tompkins {% include cite.html keys="pantompkins1985" %}, and see how ADC bits and input noise move sensitivity and positive predictive value. Goes with Chapters [24]({% link chapters/24_ecg.md %}) and [29]({% link chapters/29_arch.md %}).

## Lab 12 · EEG seizure detection {#lab-12}

Band-power features on CHB-MIT, a simple classifier, and the cost of reducing word length and sample rate. Goes with Chapters [25]({% link chapters/25_eeg.md %}) and [27]({% link chapters/27_soc.md %}).

## Lab 13 · EMG gesture recognition {#lab-13}

Time-domain features on NinaPro, an LDA or SVM classifier in fixed point, and accuracy versus channels, sample rate and resolution. Goes with [Chapter 26]({% link chapters/26_emg.md %}).

## Lab 14 · Layout to GDS {#lab-14}

Lay out the comparator and the CDAC in KLayout, run DRC, LVS and extraction with the JKU template {% include cite.html keys="jkutemplate" %}, and compare post-layout with schematic simulation. Goes with [Chapter 30]({% link chapters/30_flow.md %}).

## Lab 15 · Bioimpedance IQ readout {#lab-15}

Model Cole tissue, tetrapolar measurement and digital IQ demodulation in Python, then build an SG13G2 current source and a square-wave IQ demodulator. Goes with [Chapter 28]({% link chapters/28_bioz.md %}).

## Capstone · One Open-BioAFE channel {#capstone}

Combine Lab 5, a PGA and Lab 8 (SAR) or Lab 10 (ΔΣ), and optionally Lab 15; verify across corners; feed real ECG and EEG through the transistor-level chain with ngspice PWL sources; and report against the specification of [Table 1.2]({% link chapters/01_why.md %}#tab-1-2). The best designs go to an IHP OpenMPW submission.
