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

The set-up and Labs 1, 2, 3, 6, 9, 11, 12 and 13 are complete, with their scripts in `labs/python/` and `labs/spice/`, and so is the Python part of Lab 15. Lab 4 has its pseudo-resistor script and the targets for the amplifier you build. The other labs give their goal and deliverable; their scripts are being added. The SG13G2 scripts used for Chapters 8 and 15 are in `labs/spice/` and are the starting point for Labs 4 and 5.

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
3. Find the smallest right-leg-drive loop gain with which the boosted front-end still passes the CMRR test with 6 dB of margin. Compare it with the stability limit of [Figure 12.2]({% link chapters/12_cmcontrol.md %}#fig-12-2)b.
4. Replace the wet electrodes by dry ones (`biosig.z_electrode(f, "dry")`) for the ground electrode and the imbalance. What happens to the body's common mode and to the interference?
5. How many picofarads of input capacitance can the front-end afford, from pads, ESD diodes and wiring, before $$Z_\mathrm{cm}$$ falls below the 11.4 MΩ that the right-leg drive allows?

**Deliverable.** The two plots, the CMRR the design needs, and a recommendation for the split between amplifier CMRR, $$Z_\mathrm{cm}$$ and loop gain, with the margin each leaves in the CMRR test.

## Lab 3 · Devices in weak inversion {#lab-3}

**Goal.** Characterise the SG13G2 devices you will design with: gm/ID lookup tables, flicker noise against gate area, and the HBT against the MOSFET as an input device. Labs 4 and 5 reuse the tables. Goes with Chapters [5]({% link chapters/05_devices.md %}) and [6]({% link chapters/06_noise.md %}).

**Run.** With Docker and the container of the [set-up](#setup):

```bash
python labs/spice/sg13_char.py
```

The script writes a `.spiceinit` that loads the PSP and resistor models, generates the netlists, runs them in the container with `ngspice -b` and parses the results ([Chapter 30]({% link chapters/30_flow.md %})). It runs at the typical corner and 27 °C:

1. gm/ID sweeps of `sg13_lv_nmos` and `sg13_lv_pmos`, W = 10 µm, L = 0.5, 1 and 4 µm, &#124;V<sub>DS</sub>&#124; = 0.6 V;
2. the input-referred noise of both devices at &#124;I<sub>D</sub>&#124; = 1 µA for W/L = 10/1, 40/4 and 100/10 µm;
3. I<sub>C</sub> and I<sub>B</sub> against V<sub>BE</sub> of the `npn13G2` HBT at V<sub>CE</sub> = 0.6 V, and its input-referred noise at I<sub>C</sub> = 1 µA.

The results go to `figsrc/data/sg13_gmid.csv`, `sg13_noise.csv`, `sg13_hbt.csv` and `sg13_hbt_noise.csv`, the files that the Chapter 5 figures are drawn from. If your container reproduces them, your set-up is right.

**Expected results.**

| Quantity | Value | Where in the text |
|---|---|---|
| Slope factor n; gm/ID in deep weak inversion | 1.22; 31.7 V⁻¹ | Section 5.1 |
| Specific current I<sub>spec</sub> per square, NMOS / PMOS | 0.78 / 0.20 µA | Section 5.1 |
| Thermal noise at 1 µA in weak inversion | 18.5 nV/√Hz | Section 5.2 |
| Flicker coefficient K, NMOS / PMOS | 1.6 × 10⁻¹⁰ / 5.4 × 10⁻¹⁰ V²·µm² | Section 5.3 |
| Gate area per device for 1 µVrms unchopped, NMOS | about 1800 µm² | Section 5.3 |
| HBT at 1 µA: gm/IC, β, input noise | 37.7 V⁻¹, about 680, 15.1 nV/√Hz flat | Section 5.4 |

In these models the NMOS has less flicker noise than the PMOS, the opposite of the usual rule, which is why Open-BioAFE uses NMOS input devices.

**Questions.**

1. Build a lookup function `gm_id(ic)` from `sg13_gmid.csv` and use it to size an NMOS input pair for gm = 30 µS at 1 µA per device. What W/L comes out at L = 1 µm and at L = 4 µm, and what is the gate capacitance of each?
2. Plot the measured input noise against 1/(W·L) at 1 Hz. Is it a straight line? Extract K yourself and compare with the table.
3. At what source resistance does the HBT's base shot noise make it noisier than the MOSFET? Compare with the electrode impedances of [Chapter 3]({% link chapters/03_electrodes.md %}).
4. Add the ss and ff corners and 85 °C to the script. How much do n, I<sub>spec</sub> and K move? Which number in your design is most sensitive?
5. From the PDK's mismatch coefficients (A<sub>VT</sub> = 3.9 mV·µm for the NMOS), find the input-pair offset for the 1800 µm² devices, and say why chopping makes it irrelevant ([Chapter 9]({% link chapters/09_chopper.md %})).

**Deliverable.** gm/ID lookup tables for both devices at three lengths, flicker noise against gate area, and a one-paragraph choice of input device for the LNA of Lab 4.

## Lab 4 · The Harrison LNA {#lab-4}

**Goal.** Build the capacitive-feedback LNA of [Chapter 8]({% link chapters/08_lna.md %}) in SG13G2 and measure its gain, band, noise and NEF against bias current. Goes with Chapters [6]({% link chapters/06_noise.md %}) and [8]({% link chapters/08_lna.md %}).

**Part 1: the pseudo-resistor.**

```bash
python labs/spice/sg13_lna.py
```

The script simulates back-to-back pairs of diode-connected PMOS devices (W/L = 1/10 µm): one or four thin-oxide pairs and one thick-oxide pair, from −0.6 to +0.6 V at 27, 37 and 85 °C. It also extracts the gate capacitance of the NMOS input devices. The results go to `figsrc/data/sg13_pseudo.csv` and `sg13_cgg.csv`. It lowers $$g_\mathrm{min}$$ to $$10^{-15}$$ S. With ngspice's default the thick-oxide pair reads 1.9 TΩ, the parallel conductance of the simulator itself ([Chapter 30]({% link chapters/30_flow.md %})).

| Pseudo-resistor near 0 V | Resistance | High-pass corner with $$C_2$$ = 200 fF | Where in the text |
|---|---|---|---|
| One thin-oxide pair | 2 × 10¹¹ Ω | 4.1 Hz | Section 8.2 |
| Four thin-oxide pairs in series | 7.6 × 10¹¹ Ω | 1.05 Hz | Section 8.2 |
| One thick-oxide pair, 27 / 37 / 85 °C | 5.6 × 10¹³ Ω at 27 °C | 0.014 / 0.032 / 1.0 Hz | Section 8.2 |
| NMOS gate capacitance | about 2.2 fF/µm² | | Section 8.3 |

**Part 2: the amplifier.** Draw the LNA in Xschem: input capacitors $$C_1$$ = 20 pF (MIM, 1.5 fF/µm²), feedback capacitors $$C_2$$ = 200 fF with pseudo-resistors across them, the OTA of [Section 8.3]({% link chapters/08_lna.md %}) with NMOS input devices sized from your Lab 3 lookup tables, and a 2 pF load. Then simulate:

1. **AC**: the midband gain should be $$C_1/C_2$$ = 40 dB. The low corner is set by the pseudo-resistor. The high corner is $$g_\mathrm{m}/(2\pi A_\mathrm{M} C_\mathrm{L})$$, about 24 kHz with 2 pF.
2. **Noise**: the input-referred noise integrated over 0.5–100 Hz. Unchopped, flicker noise dominates: Chapter 8 needs about 6200 µm² of input device for 0.98 µVrms.
3. **Transient**: a 1 mV, 10 Hz input with a 300 mV step at the electrode. Watch how long the pseudo-resistor takes to recover, and how the recovery changes from 27 to 37 °C.
4. **NEF**: sweep the OTA's bias current from 0.5 to 5 µA, compute the NEF from the integrated noise and the total current ([Chapter 6]({% link chapters/06_noise.md %})), and compare with the weak-inversion limit of 1.73.

**Questions.**

1. Which pseudo-resistor would you use for EEG (0.5 Hz corner) and which for ECG (0.05 Hz)? What happens to each corner on the body (37 °C) and in a hot car (85 °C)?
2. Why does the noise gain $$(C_1 + C_2 + C_\mathrm{in})/C_1$$, with $$C_\mathrm{in}$$ the input devices' gate capacitance, punish large input devices, and where is the optimum area? Compare with Chapter 8's 6200 µm².
3. Apply a 50 mV differential step at the input. How does the pseudo-resistor's nonlinearity show in the output?
4. How much of the 1.5 µVrms EEG budget does your unchopped LNA use, and what does that tell you about [Lab 5]({% link chapters/31_labs.md %}#lab-5)?

**Deliverable.** An LNA that meets the gain and band, its noise spectrum, and the NEF against bias current with the theoretical limit.

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

**Goal.** Find how many bits and how much input noise a heartbeat detector tolerates, and how it fails under electrode motion, so that a monitoring mode can be specified from evidence. Goes with Chapters [24]({% link chapters/24_ecg.md %}) and [29]({% link chapters/29_arch.md %}).

**Data.** MIT-BIH record 100 with its beat annotations {% include cite.html keys="mitbih" %}, and the electrode-motion record `em` of the Noise Stress Test Database {% include cite.html keys="nstdb" %}, both streamed by wfdb. Offline, the script uses the synthetic ECG of Chapter 24 and band-limited (1–20 Hz) noise in place of electrode motion.

**Run.**

```bash
cd labs/python
python lab11_ecg_chain.py                          # record 100, first 5 minutes
python lab11_ecg_chain.py --record 105 --seconds 600
python lab11_ecg_chain.py --offline
```

The chain adds white input noise and 200 µV of baseline wander, quantises over the ±5 mV range of the ECG gain setting ([Table 11.1]({% link chapters/11_filters.md %}#tab-11-1)), and runs the simplified Pan–Tompkins detector of Chapter 24 {% include cite.html keys="pantompkins1985" %}. A detection within ±75 ms of an annotated beat is a true positive. The script then adds electrode-motion noise at the Noise Stress Test's signal-to-noise ratios, with the signal power taken from the QRS amplitude as in that database, (QRS peak-to-peak)²/8.

**Expected results.** Offline (70 synthetic beats), Se/PPV in per cent:

| Input noise | 3 bits | 4 bits | 5 bits | 8 bits | 12 bits |
|---|---|---|---|---|---|
| 0 | 49 / 31 | 84 / 78 | 100 / 100 | 100 / 100 | 100 / 100 |
| 100 µVrms | 56 / 56 | 96 / 96 | 100 / 100 | 100 / 100 | 100 / 100 |
| 200 µVrms | 62 / 46 | 94 / 94 | 99 / 99 | 99.5 / 99.5 | 99.5 / 99.5 |

With electrode motion at 12 bits: 100 % at 24 dB SNR, 98.6 % at 18 dB, 87 % at 12 dB, and below 65 % at 6 dB. These agree with [Worked Example 24.1]({% link chapters/24_ecg.md %}): five bits and 100 µVrms suffice for detection. Electrode motion, which shares the QRS band, breaks the detector long before the converter or the input noise does. Record 105, which is noisy, and records with many ectopic beats (for example 119 or 208) are harder than record 100.

**Questions.**

1. What is the smallest number of bits, at 100 µVrms of noise, that keeps Se and PPV above 99.5 % on record 100? On record 105?
2. Five bits over ±5 mV is an LSB of 312 µV, larger than the input noise. Why does the detector still work? Which stage of Pan–Tompkins is most sensitive to quantisation?
3. Replace electrode motion by NSTDB muscle noise (`ma`) and baseline wander (`bw`). Rank the three by how much they hurt the detector, and explain the ranking from their spectra.
4. A monitoring mode could run the converter at 6 bits and 250 S/s. Using the converter energy of [Chapter 18]({% link chapters/18_sar.md %}), estimate the power saved per channel against the diagnostic mode.
5. Is a sensitivity of 99 % good enough for an arrhythmia monitor that runs for a day? How many missed beats is that?

**Deliverable.** The Se/PPV table against bits and noise for at least two MIT-BIH records, the noise-stress curve, and a specification for an ECG monitoring mode (bits, noise, sample rate) with its evidence.

## Lab 12 · EEG seizure detection {#lab-12}

**Goal.** Detect seizures from band-power features, and find how far the converter's word length and sample rate can fall before the detector suffers, as a first step towards on-chip detection. Goes with Chapters [25]({% link chapters/25_eeg.md %}) and [27]({% link chapters/27_soc.md %}).

**Data.** Offline, the synthetic EEG of Worked Example 25.1: two-minute records of 20 µVrms background with three 10 s rhythmic discharges (3–6 Hz, 60 µV) each. For real data, download a CHB-MIT record with a seizure {% include cite.html keys="chbmit" %} (the record's summary file on PhysioNet gives the seizure's onset and end) and pass it with `--chbmit`.

**Run.**

```bash
cd labs/python
python lab12_eeg_seizure.py
python lab12_eeg_seizure.py --noise 15e-6
python lab12_eeg_seizure.py --chbmit chb01_03.edf --seizure 2996 3036
```

Each record passes through input noise, an optional decimation (the converter at 128 or 64 S/s instead of 256), and an N-bit converter over the ±0.625 mV range of the EEG gain setting. Per 2 s window the script computes line length and the power in the delta, theta, alpha and beta bands. Two detectors run on the features:

- a **threshold** on theta power at three times its median, as in Chapter 25;
- a **linear discriminant** on the four log band powers, trained on two records at full resolution and tested on four others.

For each detector the script reports window accuracy, event sensitivity, the mean detection latency after onset and the false detections per hour. The power proxy, $$(f_\mathrm{s}/256) \times 2^{N-12}$$, assumes the converter's energy per conversion doubles per bit ([Chapter 14]({% link chapters/14_adcspecs.md %})).

**Expected results.** Offline, at 1.5 µVrms of input noise:

| Bits, rate | Power proxy | Theta threshold: accuracy, latency | LDA: accuracy, latency |
|---|---|---|---|
| 12 b, 256 S/s | 1 | 99.6 %, 2.0 s | 99.2 %, 2.2 s |
| 6 b, 256 S/s | 0.016 | 99.6 %, 2.0 s | 97.9 %, 2.5 s |
| 4 b, 256 S/s | 0.004 | 91.2 %, 3.8 s | 94.6 %, 2.5 s, 30 false detections per hour |
| 12 b, 64 S/s | 0.25 | 99.6 %, 2.0 s | 99.2 %, 2.2 s |
| 6 b, 64 S/s | 0.004 | 99.2 %, 2.0 s | 95.4 %, 3.0 s |

Every discharge is found in every case. Line length stays at 75 % window accuracy, no better than always answering "no seizure", as [Worked Example 25.1]({% link chapters/25_eeg.md %}) found. Theta power needs only 6 bits and 64 S/s: a detection-only mode could run the converter at a fraction of a per cent of the diagnostic mode's energy. The latency of 2 s is set by the window length.

**Questions.**

1. Why does a single threshold on theta power do as well as the discriminant here? Construct a case where it would not, for example a record with strong alpha or eye-movement artefacts.
2. Halve the window to 1 s. What happens to latency, accuracy and false detections?
3. Raise the input noise to 15 µVrms, ten times the EEG target. Which detector degrades first, and why does band power tolerate noise better than line length?
4. Run a real CHB-MIT seizure. Train on one record of a patient and test on another of the same patient, then on a different patient. What happens to the false detections per hour, the number that decides whether a wearable detector is usable?
5. Count the operations per window of the theta-power detector at 64 S/s and 6 bits, and estimate its energy with the picojoule-per-operation figures of [Chapter 27]({% link chapters/27_soc.md %}).

**Deliverable.** Latency and accuracy against bits and sample rate, with the power proxy, for both detectors, and a proposed detection mode for the chip.

## Lab 13 · EMG gesture recognition {#lab-13}

**Goal.** Find what a gesture classifier needs from the front-end (channels, sample rate, bits), and whether the classifier itself fits in a few hundred gates of fixed-point logic. Goes with [Chapter 26]({% link chapters/26_emg.md %}).

**Data.** Offline, the synthetic 8-channel EMG of Worked Example 26.1: five gestures, each a fixed pattern of channel amplitudes with trial-to-trial variation. For real data, download a NinaPro subject's `.mat` file {% include cite.html keys="ninapro" %} (registration required) and pass it with `--ninapro`; the script uses repetitions 2 and 5 as the test set, as the NinaPro papers do.

**Run.**

```bash
cd labs/python
python lab13_emg_gestures.py                        # about a minute
python lab13_emg_gestures.py --ninapro S1_E1_A1.mat
```

The converter is modelled as signed integer codes over the ±5 mV range of the EMG gain setting. The four features of Chapter 26 (MAV, WL, ZC and SSC) are computed from the integer codes over 200 ms windows. A linear discriminant with a shared covariance, on standardised features, classifies them. The script works through three steps:

1. accuracy against 2, 4 and 8 channels, 500 to 2000 S/s and 3 to 12 bits;
2. the classifier in **fixed point**: integer features, a Mitchell approximation of log₂ (the position of the leading one plus the remaining bits as a fraction, a shift and a priority encoder in hardware), and weights quantised to 8, 6 and 4 bits;
3. an **electrode shift** between training and use, modelled by mixing each channel with its neighbour.

**Expected results.** Offline:

| Channels | 3 bits | 4 bits | 5 bits | 8 bits | 12 bits |
|---|---|---|---|---|---|
| 2 (1 kS/s) | 42 % | 66 % | 84 % | 89 % | 91 % |
| 4 (1 kS/s) | 45 % | 88 % | 96 % | 98.5 % | 99.5 % |
| 8 (500 / 1000 / 2000 S/s) | 48–51 % | 96–98.5 % | 100 % | 100 % | 100 % |

In fixed point, with 8 channels at 1 kS/s and 8 bits, accuracy stays at 100 % with 8-bit and 6-bit weights and 99.5 % with 4-bit weights. A shift that mixes 20 % of the neighbouring channel costs 1 %, but 40 % costs 15 % and 60 % leaves 40 %. The converter needs 5 bits and 500 S/s, as [Worked Example 26.1]({% link chapters/26_emg.md %}) found. The number of channels and the electrode placement matter far more than the converter, and the classifier fits in small integer logic. Standardising the features before quantising the weights is essential: without it the log features' large common offset swamps the differences between classes, and 8-bit weights fall to chance.

**Questions.**

1. Why do two channels stop at about 90 % however many bits you give them? Which gestures do they confuse? (Print a confusion matrix.)
2. Drop one feature at a time. Which feature carries the most information at 4 bits, and which at 12 bits?
3. Retrain after the electrode shift with only five trials per gesture. How much accuracy does a short recalibration recover?
4. Run NinaPro. How does the accuracy compare with the synthetic data, and does it still saturate at 5 bits?
5. Count the additions, comparisons and multiplications per window of the fixed-point classifier for 8 channels and 5 gestures, and estimate its energy with the figures of [Chapter 27]({% link chapters/27_soc.md %}).

**Deliverable.** Accuracy against channels, sample rate and resolution, the fixed-point classifier with its word lengths, and a recommendation for the EMG mode of the chip.

## Lab 14 · Layout to GDS {#lab-14}

Lay out the comparator and the CDAC in KLayout, run DRC, LVS and extraction with the JKU template {% include cite.html keys="jkutemplate" %}, and compare post-layout with schematic simulation. Goes with [Chapter 30]({% link chapters/30_flow.md %}).

## Lab 15 · Bioimpedance IQ readout {#lab-15}

**Goal.** Measure a tissue impedance and its small changes safely and precisely: see why four electrodes are needed, what resolution a given current buys, and what square-wave circuits cost in accuracy. Goes with [Chapter 28]({% link chapters/28_bioz.md %}).

**Part 1 (Python).**

```bash
cd labs/python
python lab15_bioz.py
python lab15_bioz.py --i 20e-6 --vn 30e-9
```

The script takes the Cole model of Chapter 28 ($$R_0$$ = 60 Ω, $$R_\infty$$ = 30 Ω, $$f_\mathrm{c}$$ = 30 kHz, α = 0.7) and works through four steps:

1. the tissue's impedance and phase from 5 to 500 kHz;
2. a bipolar measurement, with the wet or dry electrodes of `biosig.z_electrode()` in series, against a tetrapolar one;
3. a time-domain simulation of the readout: a 50 kHz current through the tissue, white readout noise, sampling at 400 kS/s, digital multiplication by the in-phase and quadrature references, and a boxcar low-pass with a 10 Hz noise bandwidth;
4. square-wave excitation demodulated by a square-wave reference, as switched current sources and chopper-style demodulators do.

The plot (`out/lab15_bioz.png`) shows the Cole plot and a recovered 0.5 Ω respiration with a 0.1 Ω cardiac component at 10 and 50 µA.

**Expected results.**

| Quantity | Result | Where in the text |
|---|---|---|
| Tissue at 50 kHz | 42.3 Ω, −12.0° | Section 28.2 |
| Bipolar reading at 50 kHz, wet / dry electrodes | 2047 Ω / 10 134 Ω for 42 Ω of tissue | Section 28.2 |
| ΔZ noise, 50 nV/√Hz in 10 Hz, at 10 / 50 / 500 µArms: simulated (formula) | 16.0 (15.8) / 3.21 (3.16) / 0.32 (0.32) mΩ | Worked Example 28.1 |
| Square-wave excitation and reference | 40.8 Ω, −11.4°: 3.6 % low; noise ×1.11 | Section 28.4 |

The simulated resolution confirms the formula $$v_\mathrm{n}\sqrt{B}/I_\mathrm{rms}$$ of Worked Example 28.1. The square-wave error comes from the harmonics at 150, 250 kHz and above, where the tissue's impedance is lower; it depends on the tissue, which is why Chapter 28 calibrates against an on-chip resistor.

**Questions.**

1. Respiration changes the thoracic impedance by about 1 Ω and the heartbeat by about 0.1 Ω. What current do you need to see the cardiac component with a signal-to-noise ratio of 20 dB, and is it inside the CF limit at 50 kHz?
2. Repeat the square-wave case for a tissue with $$f_\mathrm{c}$$ = 100 kHz. Does the error grow or shrink, and why?
3. Replace the square-wave excitation by a three-level pseudo-sine (0, ±1, with the zero levels lasting 1/6 of the period each), which has no third harmonic. What is the error now?
4. Add the ECG (1 mV) to the measured voltage. Why does it disappear after demodulation, and what limits how well?
5. The readout noise is 50 nV/√Hz at 50 kHz. Using the chopper amplifier of Chapter 9, is this realistic, and what sets it?

**Part 2 (SG13G2).** Build a balanced current source for 10–50 µA at 50 kHz and a square-wave IQ demodulator from the chopper switches of [Chapter 9]({% link chapters/09_chopper.md %}); simulate them with the Cole network as the load and compare the analog IQ error with Part 1.

**Deliverable.** The Cole plot, the ΔZ resolution against current with the safety limit, and the analog against digital IQ error.

## Capstone · One Open-BioAFE channel {#capstone}

Combine Lab 5, a PGA and Lab 8 (SAR) or Lab 10 (ΔΣ), and optionally Lab 15; verify across corners; feed real ECG and EEG through the transistor-level chain with ngspice PWL sources; and report against the specification of [Table 1.2]({% link chapters/01_why.md %}#tab-1-2). The best designs go to an IHP OpenMPW submission.
