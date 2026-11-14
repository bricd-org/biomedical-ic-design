---
title: B. Reference Tables
parent: Appendices
nav_order: 2
permalink: /appendix/b/
---

# <span class="chapnum">Appendix B</span>Reference Tables

The numbers the chapters design with, collected in one place. The biosignal and electrode values are the ones in `labs/python/biosig.py`, so the labs use them too.
{: .chapterlead }

## <span class="secnum">B.1</span>Biosignals

**Table B.1. Amplitude and bandwidth of the biopotentials.** Orders of magnitude from the sources of [Chapter 2]({% link chapters/02_signals.md %}); sources differ by a factor of a few, so treat these as design ranges. The same values are `SIGNALS` in `biosig.py`.
{: .tabcaption #tab-b-1 }

| Signal | Amplitude | Bandwidth | Typical sample rate |
|---|---|---|---|
| ECG (surface) | 0.5–4 mV | 0.05–150 Hz | 500 S/s |
| EEG (scalp) | 5–300 µV | 0.5–100 Hz | 256 S/s |
| EMG (surface) | 50 µV–5 mV | 10–500 Hz | 2 kS/s |
| EOG | 10 µV–3.5 mV | 0.05–50 Hz | 250 S/s |
| ECoG | 10–500 µV | 0.5–500 Hz | 2 kS/s |
| LFP (intracortical) | 50 µV–2 mV | 0.5–300 Hz | 1 kS/s |
| Spikes (extracellular) | 50–500 µV | 300 Hz–7 kHz | 30 kS/s |

## <span class="secnum">B.2</span>Electrodes

**Table B.2. Electrode models.** A series resistance $$R_\mathrm{s}$$ and a parallel $$R_\mathrm{p}$$–$$C_\mathrm{p}$$ interface, or a constant-phase element for implanted microelectrodes ([Chapter 3]({% link chapters/03_electrodes.md %})). The wet values are the 51 kΩ‖47 nF network of the ECG standards.
{: .tabcaption #tab-b-2 }

| Electrode | Model | \|Z\| at 50 Hz | Half-cell / offset |
|---|---|---|---|
| Wet Ag/AgCl | 1 kΩ + 51 kΩ ‖ 47 nF | 41.5 kΩ | 0.222 V; ±300 mV differential offset to tolerate |
| Dry | 5 kΩ + 1 MΩ ‖ 4.7 nF | about 560 kΩ | drifts with sweat and pressure |
| Implanted micro | 10 kΩ + constant-phase element, n = 0.85 | 500 kΩ at 1 kHz | charge-injection limits apply |

## <span class="secnum">B.3</span>IHP SG13G2 device data

**Table B.3. SG13G2 numbers used in this tutorial.** From ngspice simulations of the IHP-Open-PDK models at the typical corner and 27 °C (`labs/spice/`), and from the PDK's mismatch coefficients.
{: .tabcaption #tab-b-3 }

| Quantity | Value | Chapter |
|---|---|---|
| Slope factor n; gm/I<sub>D</sub> in weak inversion | 1.22; 31.7 V⁻¹ | [5]({% link chapters/05_devices.md %}) |
| Specific current per square, NMOS / PMOS | 0.78 / 0.20 µA | 5 |
| Thermal noise of a MOSFET at 1 µA | 18.5 nV/√Hz | 5 |
| Flicker coefficient K, NMOS / PMOS | 1.6 × 10⁻¹⁰ / 5.4 × 10⁻¹⁰ V²·µm² | 5 |
| Pelgrom A<sub>VT</sub>, NMOS / PMOS | 3.9 / 2.2 mV·µm | 5 |
| Pelgrom A<sub>β</sub>, NMOS / PMOS | 0.5 / 0.33 %·µm | 5 |
| MIM capacitor density; matching | 1.5 fF/µm²; 1 %·µm | [17]({% link chapters/17_cdac.md %}) |
| Gate capacitance in weak inversion | about 2.2 fF/µm² | [8]({% link chapters/08_lna.md %}) |
| npn13G2 at 1 µA: gm/I<sub>C</sub>, β, input noise | 37.7 V⁻¹, about 680, 15.1 nV/√Hz | 5 |
| Pseudo-resistor near 0 V: one / four thin-oxide pairs | 2 × 10¹¹ / 7.6 × 10¹¹ Ω | 8 |
| Pseudo-resistor, one thick-oxide pair, 27 °C | 5.6 × 10¹³ Ω | 8 |
| Core supply; thick-oxide supply | 1.2 V; 3.3 V | [30]({% link chapters/30_flow.md %}) |

## <span class="secnum">B.4</span>Patient-current limits

**Table B.4. Patient leakage and auxiliary current limits, summarised from IEC 60601-1** {% include cite.html keys="iec60601-1" %}. Above 1 kHz the AC limits rise in proportion to frequency, up to 100 kHz, but never above 10 mA. Always work from the edition of the standard that applies to your device ([Chapter 4]({% link chapters/04_interference.md %})).
{: .tabcaption #tab-b-4 }

| Applied part | Normal condition | Single-fault condition |
|---|---|---|
| B, BF (body surface) | 100 µA | 500 µA |
| CF (cardiac) | 10 µA | 50 µA |
| DC, any type | 10 µA | — |

## <span class="secnum">B.5</span>The Open-BioAFE design in numbers

**Table B.5. The main design values,** with the chapter that sets each. [Table 29.1]({% link chapters/29_arch.md %}#tab-29-1) compares them with the specification.
{: .tabcaption #tab-b-5 }

| Block | Values | Chapter |
|---|---|---|
| LNA | chopped CCIA, C<sub>in</sub> 20 pF, C<sub>fb</sub> 200 fF, gain 40 dB, f<sub>ch</sub> 4 kHz, NMOS input devices of 1000 µm² | [8]({% link chapters/08_lna.md %})–[9]({% link chapters/09_chopper.md %}) |
| Servo and boosting loops | 3.3 V integrator, C<sub>DSL</sub> 4 pF (noise gain 1.32); input impedance about 200 MΩ | [10]({% link chapters/10_dsl.md %}) |
| Gain plan | ECG 100 × 1, EEG 100 × 8, EMG 10 × 8 onto ±0.5 V differential | [11]({% link chapters/11_filters.md %}) |
| Right-leg drive | loop gain 100 at 50 Hz, R<sub>o</sub> 150 kΩ, 53° phase margin; CMRR-test residual 0.06 mVpp | [12]({% link chapters/12_cmcontrol.md %}) |
| SAR converter | 12-bit asynchronous, 14 cycles at radix 1.8, about 1 fF units, 4 pF per side, V<sub>cm</sub> switching, about 7.6 pJ per conversion, 16 kS/s shared by 8 channels | [15]({% link chapters/15_switches.md %})–[18]({% link chapters/18_sar.md %}) |
| ΔΣ converter | second-order incremental, M = 1024 at 512 kHz, a<sub>1</sub> 0.5, a<sub>2</sub> 0.25, C<sub>s</sub> 1.1 pF, 16.5 bits worst case, about 1.9 µW per channel | [19]({% link chapters/19_dstheory.md %})–[20]({% link chapters/20_dscircuits.md %}) |
| Reference | off-chip 1 µF reservoir capacitor | [17]({% link chapters/17_cdac.md %}) |
| Budgets | noise 0.51 µVrms (wet) / 1.26 µVrms (dry); power 6.8 µW per channel (ECG/EEG), 4.9 µW (EMG); about 1.7 mm² of core | [29]({% link chapters/29_arch.md %}) |

## <span class="secnum">B.6</span>Constants

| Constant | Value |
|---|---|
| Boltzmann constant k | 1.380649 × 10⁻²³ J/K |
| Elementary charge q | 1.602177 × 10⁻¹⁹ C |
| Thermal voltage U<sub>T</sub> = kT/q | 25.9 mV at 300 K; 26.7 mV at 310 K |
| 4kT | 1.66 × 10⁻²⁰ J at 300 K; 1.71 × 10⁻²⁰ J at 310 K (body) |
| kT/C | 64 µVrms on 1 pF at 300 K |
| Mains | 230 V / 50 Hz or 120 V / 60 Hz |
