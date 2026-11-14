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
<div class="tbox-title">Lab status</div>

The set-up and Labs 1, 2, 6 and 9 are complete, with their scripts in `labs/python/`. The other labs give their goal and deliverable; their scripts are being added. The SG13G2 characterisation scripts used for Chapters 5, 8 and 15 are already in `labs/spice/` and are the starting point for Labs 3 and 4.

</div>

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

**Track A and C (Python).** Any Python 3.9 or newer works. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r labs/python/requirements.txt
```

This installs NumPy, SciPy, Matplotlib and wfdb, which streams PhysioNet records {% include cite.html keys="mitbih,chbmit" %} without a manual download. Every lab imports `labs/python/biosig.py`, the same module that computes the numbers and figures in the chapters, and writes its plots and tables to `labs/python/out/`. Each lab also runs offline: a recording that cannot be loaded is replaced by the synthetic signal of `biosig.py`, and the output says which was used.

**Track B and Lab 14 (SG13G2).** Install Docker and pull the IIC-OSIC-TOOLS container {% include cite.html keys="iicosic" %}, which includes the IHP-Open-PDK {% include cite.html keys="ihppdk" %}, Xschem, ngspice and KLayout:

```bash
docker pull hpretl/iic-osic-tools:2026.10
```

The scripts in `labs/spice/` start the container themselves, write a `.spiceinit` that loads the PSP and resistor models, run ngspice in batch mode and parse the results ([Chapter 30]({% link chapters/30_flow.md %})). Run `python labs/spice/sg13_char.py` once: if it reproduces the gm/ID curves of [Chapter 5]({% link chapters/05_devices.md %}), your set-up is complete. For interactive work with Xschem and KLayout, start the container with its desktop as described in its documentation.

## Lab 1 · Biosignal explorer {#lab-1}

**Goal.** Measure real biosignals and check the amplitude and bandwidth ranges of [Table 2.1]({% link chapters/02_signals.md %}#tab-2-1), which set every specification of the front-end. Goes with [Chapter 2]({% link chapters/02_signals.md %}).

**Data.** MIT-BIH Arrhythmia Database record 100, lead MLII, 360 S/s {% include cite.html keys="mitbih" %}; a CHB-MIT scalp EEG recording such as `chb01_03.edf` (256 S/s, about 40 MB) {% include cite.html keys="chbmit" %}; a NinaPro EMG file (2 kS/s; NinaPro asks you to register before downloading) {% include cite.html keys="ninapro" %}.

**Run.**

```bash
cd labs/python
python lab1_biosignal_explorer.py                                  # streams ECG and EEG
python lab1_biosignal_explorer.py --chbmit chb01_03.edf --ninapro S1_E1_A1.mat
python lab1_biosignal_explorer.py --offline                        # synthetic signals only
```

The script high-passes each signal at the lower edge of its band to remove baseline wander and electrode drift, then measures:

- the **amplitude** as a robust peak-to-peak value, between the 0.5th and 99.5th percentiles, and the RMS (`biosig.amplitude_stats`);
- the **power bandwidth**, the band that holds 95 % of the signal's power, from a Welch spectrum (`biosig.psd`, `biosig.band_edges`).

It plots five seconds of each trace next to its spectrum (`out/lab1_explorer.png`) and writes your version of Table 2.1 to `out/lab1_table.md`.

**Expected results.** With the synthetic signals (`--offline`) the script prints:

| Signal | p-p | RMS | 95 % power band | Table 2.1 |
|---|---|---|---|---|
| ECG | 1.21 mV | 168 µV | 1.2–21.5 Hz | 0.5–4 mV, 0.05–150 Hz |
| EEG | 105 µV | 19.7 µV | 0.5–21.8 Hz | 5–300 µV, 0.5–100 Hz |
| EMG (bursts) | 1.38 mV | 216 µV | 30–441 Hz | 0.05–5 mV, 10–500 Hz |

The real recordings give different numbers: compare them with the same columns.

**Questions.**

1. Does each measured amplitude fall inside the Table 2.1 range? Which recording comes closest to an edge of its range, and what does that mean for the gain plan of [Chapter 11]({% link chapters/11_filters.md %})?
2. The ECG's 95 % power band ends near 20–40 Hz, yet diagnostic ECG needs 150 Hz. Which features of the waveform live in the last few per cent of the power? (Hint: look at the QRS complex and at pacemaker spikes, [Chapter 24]({% link chapters/24_ecg.md %}).)
3. Find the mains line in the real ECG and EEG spectra. How large is it in microvolts, and how does it compare with the 1.5 µVrms noise target?
4. Change the high-pass corner from 0.05 Hz to 0.5 Hz for the ECG. What happens to the amplitude, and why does the standard ask for 0.05 Hz in diagnostic mode?
5. From your table, which signal sets the input-referred noise, which sets the input range, and which sets the sample rate?

**Deliverable.** Your version of Table 2.1 with the source of each row, and one paragraph on where your numbers differ from the chapter's and why.

## Lab 2 · Electrodes and interference {#lab-2}

**Goal.** Rebuild the interference model of Figure 4.1 and find the common-mode input impedance, amplifier CMRR and right-leg-drive loop gain the front-end needs. Goes with Chapters [3]({% link chapters/03_electrodes.md %}), [4]({% link chapters/04_interference.md %}) and [12]({% link chapters/12_cmcontrol.md %}).

**Run.**

```bash
cd labs/python
python lab2_electrodes_interference.py                     # 50 Hz, 100 dB amplifier, RLD loop gain 100
python lab2_electrodes_interference.py --f 60 --rld 40 --cmrr 110
```

The model is a chain of phasors. The mains couples 230 V to the body through 3 pF; the displacement current leaves through the ground electrode (1 kΩ plus 51 kΩ‖47 nF) and sets the body's common mode (`biosig.body_cm_voltage`). One lead carries the standards' 51 kΩ‖47 nF imbalance, and each input forms a divider with the common-mode input impedance $$Z_\mathrm{cm}$$, which turns common mode into differential interference (`biosig.cm_to_dm`). The amplifier's own CMRR adds to that, worst case in phase, and a behavioural right-leg drive divides the common mode at the electrodes by one plus its loop gain. The script works through five steps:

1. the body's common mode, floating and with a ground electrode;
2. the interference for $$Z_\mathrm{cm}$$ from 10 MΩ to 10 GΩ;
3. the $$Z_\mathrm{cm}$$ that 90 dB of effective CMRR needs, with and without the right-leg drive;
4. the 10 Vrms CMRR test of the ECG standards for the unboosted and the boosted front-ends of Chapter 10;
5. a grounded against a driven shield on one metre of lead.

**Expected results.** With the defaults the script prints, among others:

| Quantity | Value | Where in the text |
|---|---|---|
| Body common mode, floating / with ground electrode / with RLD | 3.40 V / 9.0 mV / 89 µV | Worked Example 4.1, Section 12.1 |
| Interference at $$Z_\mathrm{cm}$$ = 10 MΩ / 1 GΩ | 36.6 µVrms / 0.37 µVrms | Worked Example 4.2 |
| $$Z_\mathrm{cm}$$ for 90 dB with a 100 dB / 120 dB amplifier | 1.88 GΩ / 1.33 GΩ | Worked Example 4.4 |
| CMRR the test implies; $$Z_\mathrm{cm}$$ bound without / with RLD | 89.0 dB; 1.15 GΩ / 11.4 MΩ | Worked Example 4.3, Chapter 12 |
| Test residual, boosted front-end (200 MΩ), RLD loop gain 100 | 0.060 mVpp, 24 dB margin | Chapters 12 and 29 |
| Test residual, unboosted front-end (6.25 MΩ), RLD loop gain 100 | 1.83 mVpp, fails | Chapter 12 |
| Interference with a grounded / driven (1 % error) shield | 11.7 µVrms / 0.30 µVrms | Chapter 4 pitfall |

It also plots the interference against the imbalance for four values of $$Z_\mathrm{cm}$$, and the effective CMRR against $$Z_\mathrm{cm}$$ with and without the right-leg drive (`out/lab2_interference.png`), as in [Figure 4.2]({% link chapters/04_interference.md %}#fig-4-2).

**Questions.**

1. Why does an amplifier with 120 dB of CMRR barely relax the $$Z_\mathrm{cm}$$ requirement compared with one of 100 dB? Find the amplifier CMRR below which no $$Z_\mathrm{cm}$$ reaches 90 dB.
2. Run at 60 Hz. Which numbers change, and by how much? Is a 60 Hz country harder or easier for the front-end?
3. Find the smallest right-leg-drive loop gain with which the boosted front-end still passes the CMRR test with 6 dB of margin. Compare it with the stability limit of [Figure 12.1]({% link chapters/12_cmcontrol.md %}#fig-12-1)b.
4. Replace the wet electrodes by dry ones (`biosig.z_electrode(f, "dry")`) for the ground electrode and the imbalance. What happens to the body's common mode and to the interference?
5. How many picofarads of input capacitance can the front-end afford, from pads, ESD diodes and wiring, before $$Z_\mathrm{cm}$$ falls below the 11.4 MΩ that the right-leg drive allows?

**Deliverable.** The two plots, the CMRR the design needs, and a recommendation for the split between amplifier CMRR, $$Z_\mathrm{cm}$$ and loop gain, with the margin each leaves in the CMRR test.

## Lab 3 · Devices in weak inversion {#lab-3}

gm/ID lookup tables for SG13G2 MOS devices, flicker noise versus gate area, and HBT versus MOS input noise. Goes with Chapters [5]({% link chapters/05_devices.md %}) and [6]({% link chapters/06_noise.md %}).

## Lab 4 · The Harrison LNA {#lab-4}

The capacitive-feedback LNA with pseudo-resistors: AC, noise and transient simulations, and the NEF versus bias current. Goes with [Chapter 8]({% link chapters/08_lna.md %}).

## Lab 5 · Chopper amplifier {#lab-5}

Input and output choppers with a DC servo loop: 1/f noise removal, output ripple, input-impedance loss and ±300 mV offset tolerance. Goes with Chapters [9]({% link chapters/09_chopper.md %}) and [10]({% link chapters/10_dsl.md %}).

## Lab 6 · Ideal ADC and spectral testing {#lab-6}

**Goal.** Build `adctest.py`, the test bench that Labs 8 and 10 reuse, and learn what each test can and cannot see. Goes with Chapters [13]({% link chapters/13_sampling.md %}), [14]({% link chapters/14_adcspecs.md %}) and [22]({% link chapters/22_adctest.md %}).

**Run.**

```bash
cd labs/python
python adctest.py                  # 12-bit SAR, 1 % unit mismatch, seed 2 (Worked Example 14.1)
python adctest.py --sigma 0.002    # the 0.2 % of Chapter 17
```

`adctest.py` is both the lab and a module. `sine_test()` returns SNDR, SNR, THD, SFDR and ENOB of a sine record, coherent (rectangular window) or not (Hann or four-term Blackman–Harris, with the tone's power summed over its lobe). `ramp_histogram()` and `sine_histogram()` return DNL and INL. The sine version estimates the sine's amplitude and offset from the counts in the two end codes and corrects for the arcsine distribution, so it needs no precision ramp. The converter under test is `biosig.sar_convert()` with the mismatched weights of `biosig.cdac_weights()`; replace it by your own model or by codes exported from a simulation.

**Expected results.**

| Test | Result | Where in the text |
|---|---|---|
| Coherent 97 Hz tone at 2 kS/s, 8192 points, ideal 12-bit | SNDR 74.0 dB, ENOB 12.00 | Section 13.2 |
| Same, 1 % unit mismatch (seed 2) | SNDR 69.5 dB, ENOB 11.26, SFDR 76.2 dB | Worked Example 14.1 |
| Non-coherent tone, ideal converter: rectangular / Hann (±2 bins) / Hann (±30 bins) / Blackman–Harris | SNDR 9.8 / 40.8 / 73.7 / 73.9 dB | Section 22.1 |
| Ramp histogram, 64 hits per code | DNL −0.42 to +1.45 LSB, INL ±0.85 LSB | Worked Example 14.1 |
| Sine histogram, 2<sup>20</sup> samples | amplitude found to 0.01 %, DNL within 0.070 LSB rms of the ramp | Worked Example 22.1 |
| 10 converters each at σ<sub>u</sub> = 0.1, 0.2, 0.5, 1, 2 % | mean ENOB 11.99, 11.98, 11.89, 11.68, 11.20 | Chapter 17 |

The Hann rows show a trap: the Hann window's sidelobes fall slowly, so near a full-scale tone they still hold about −41 dBc. Summing only the three-bin main lobe as signal leaves that skirt in the noise; exclude about 30 bins, or use Blackman–Harris.

**Questions.**

1. Seed 2 at 1 % gives 11.26 effective bits, the ten-seed mean 11.68. What does that say about quoting a converter's ENOB from one simulated or one measured chip? How many chips would you measure?
2. Find the smallest σ<sub>u</sub> at which a missing code appears in 100 seeds. Compare it with the 3σ rule $$\sigma_u < 0.26\,\%$$ of Worked Example 14.1.
3. Reduce the sine-histogram record to 2<sup>16</sup> samples. How large is the DNL error now, and does it match $$1/\sqrt{\text{hits per code}}$$?
4. Add 0.1 LSB rms of white noise before the quantiser (comparator noise, Chapter 16). What happens to the SNDR, and to the DNL that the ramp histogram finds? Why does noise make the DNL look better?
5. Use `band_bins` to test an oversampled converter: quantise a 10 Hz tone at 16 kS/s with 12 bits and compute the SNDR in a 125 Hz band. Compare with `biosig.sqnr_os_db()`.

**Deliverable.** `adctest.py` with your own converter model plugged in, and a table of SNDR, SFDR, ENOB, DNL and INL for the ideal, 0.2 % and 1 % cases.

## Lab 7 · StrongARM comparator {#lab-7}

Design the comparator, find its offset with Monte Carlo and its input-referred noise with transient noise, and measure the energy per decision. Goes with [Chapter 16]({% link chapters/16_comparators.md %}).

## Lab 8 · SAR ADC {#lab-8}

Combine a bootstrapped sample-and-hold, a monotonic CDAC and Verilog SAR logic into a 10- to 12-bit SAR, and measure its ENOB and figure of merit with `adctest.py`. Goes with Chapters [15]({% link chapters/15_switches.md %}), [17]({% link chapters/17_cdac.md %}) and [18]({% link chapters/18_sar.md %}).

## Lab 9 · ΔΣ by design {#lab-9}

**Goal.** Choose the order, OSR and loop of the ECG/EEG converter from simulation rather than from the linear formula, and build its decimator in integer arithmetic. Goes with Chapters [19]({% link chapters/19_dstheory.md %}) and [20]({% link chapters/20_dscircuits.md %}).

**Run.**

```bash
cd labs/python
python lab9_deltasigma.py               # -6 dBFS tone, 65 536-point records
python lab9_deltasigma.py --amp 0.3
```

The script needs only NumPy and SciPy. `biosig.synth_ntf()` synthesises NTFs in the spirit of python-deltasigma's `synthesizeNTF` {% include cite.html keys="pydeltasigma" %}: zeros at DC or spread over the band, poles placed until $$\lVert\mathrm{NTF}\rVert_\infty$$ meets the Lee criterion. `biosig.simulate_dsm()` runs any NTF as a 1-bit modulator. If you have python-deltasigma installed, compare its results with these. The script works through four steps:

1. four NTFs and their in-band noise at OSR 128;
2. SQNR against OSR for first, second and third order, formula against simulation;
3. the second-order incremental converter of Chapter 20 ($$a_1 = 0.5$$, $$a_2 = 0.25$$) on 8001 DC inputs;
4. its cascade-of-integrators decimator in integer arithmetic, with register widths and the attenuation at the chopper frequency.

**Expected results.**

| Quantity | Result | Where in the text |
|---|---|---|
| In-band noise gain at OSR 128: MOD1 / MOD2 / MOD3 (1.5) / MOD3 (1.5, spread zeros) | −58 / −93 / −99 / −107 dB | Section 19.2 |
| MOD2 at OSR 128, −6 dBFS: formula / simulation | 94.2 / 85.5 dB | Worked Example 19.1 |
| MOD3 ($$\lVert\mathrm{NTF}\rVert_\infty$$ = 1.5) at OSR 128, −6 dBFS: formula / simulation | 127.9 / 102.0 dB | Section 19.4 |
| Incremental, M = 256 / 512 / 1024, worst case | 12.4 / 14.5 / 16.5 bits (17.6 bits rms at 1024) | Worked Example 19.3 |
| Integrator swing with $$a_2$$ = 0.25 / 0.5 | 1.12 / 2.25, identical codes | Chapter 20 |
| CoI registers at M = 1024 | 12 and 20 bits; 16-bit output within 0.73 LSB | Section 20.4 |
| CoI response at 50 Hz / 4 kHz (512 kHz clock) | −0.1 / −28.0 dB | Section 20.5 |

The plot (`out/lab9_deltasigma.png`) shows the NTFs and the SQNR against OSR, simulation as markers and the formula dashed. The gap grows with order: the linear model ignores the 1-bit quantiser's gain and its overload.

**Questions.**

1. Raise the third-order loop's $$\lVert\mathrm{NTF}\rVert_\infty$$ to 2 and 3 (`biosig.synth_ntf(3, 128, h)`). At what value does the 1-bit loop go unstable at −6 dBFS, and at what input amplitude does the stable one overload?
2. Why does the second-order modulator fall 9 dB short of its formula? Estimate the quantiser's effective gain from the simulated output and its input.
3. With a DC input of 0.002 full scale, look at the MOD1 and MOD2 output spectra for idle tones. How much dither removes them, and what does it cost in SQNR (Worked Example 19.2)?
4. For the incremental loop, find M for 14 bits and for 16 bits worst case, and the clock each needs at 500 S/s. How many cycles would a first-order incremental loop need for 16 bits?
5. Replace the CoI by a sinc² filter over the same 1024 cycles. What happens to the resolution and to the attenuation at 4 kHz?

**Deliverable.** The NTF, coefficients and M for the ECG/EEG channel, the SQNR-against-OSR plot, and a bit-true decimator with its register widths.

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
