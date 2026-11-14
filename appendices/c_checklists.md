---
title: C. Design-Review Checklists
parent: Appendices
nav_order: 3
permalink: /appendix/c/
---

# <span class="chapnum">Appendix C</span>Design-Review Checklists

The questions a reviewer should ask of a biopotential front-end, collected from the pitfall boxes of the chapters. Each item links to where it is explained.
{: .chapterlead }

## <span class="secnum">C.1</span>Specification

- [ ] Every amplitude stated as peak-to-peak or rms, and every noise figure with its bandwidth ([Chapters 2]({% link chapters/02_signals.md %}) and [6]({% link chapters/06_noise.md %})).
- [ ] The largest signal, the electrode offset and the artefacts all fit the input range at every gain setting ([Chapter 11]({% link chapters/11_filters.md %})).
- [ ] The specification names the electrodes it assumes, wet or dry, and the noise budget includes their thermal noise ([Chapters 3]({% link chapters/03_electrodes.md %}) and [29]({% link chapters/29_arch.md %})).
- [ ] The CMRR requirement is stated with the standards' electrode imbalance, not for the amplifier alone ([Chapter 4]({% link chapters/04_interference.md %})).
- [ ] The system budget includes the radio, not only the front-end ([Chapter 27]({% link chapters/27_soc.md %})).

## <span class="secnum">C.2</span>Analog front-end

- [ ] **Noise.** Input-referred noise integrated over the signal band, including the amplifier's current noise times the electrode impedance, the input-protection resistors, the servo loop's noise gain and the flicker noise left after chopping ([Chapters 6]({% link chapters/06_noise.md %}), [9]({% link chapters/09_chopper.md %}), [10]({% link chapters/10_dsl.md %})).
- [ ] **Wideband noise.** The LNA's noise above the signal band is filtered before any sampling, or it folds into the band ([Chapter 8]({% link chapters/08_lna.md %})).
- [ ] **CMRR.** Effective CMRR with the imbalance network at 50 and 60 Hz, including the input impedance, the RF filter's mismatch and the amplifier's intrinsic CMRR across frequency ([Chapters 4]({% link chapters/04_interference.md %}) and [7]({% link chapters/07_ia.md %})).
- [ ] **Offset.** ±300 mV of electrode offset tolerated at every gain, with the servo loop's range and recovery time checked ([Chapter 10]({% link chapters/10_dsl.md %})).
- [ ] **Input impedance.** At the chopping frequency, with the parasitic capacitance of pads, ESD and routing, and with the boosting loop's accuracy over corners ([Chapters 9]({% link chapters/09_chopper.md %}) and [10]({% link chapters/10_dsl.md %})).
- [ ] **Pseudo-resistors.** High-pass corner over temperature (27 to 85 °C moves it by about two decades) and recovery after a large step ([Chapter 8]({% link chapters/08_lna.md %})).
- [ ] **Chopper ripple and spikes.** Residual ripple at the output and the ripple's alias after sampling ([Chapter 9]({% link chapters/09_chopper.md %})).
- [ ] **Protection.** ESD on every pad, series resistance small enough for the noise budget, defibrillation protection off chip if required ([Chapter 12]({% link chapters/12_cmcontrol.md %})).
- [ ] **RF filtering.** Input RC filters matched, so that they do not turn common mode into differential mode ([Chapter 12]({% link chapters/12_cmcontrol.md %})).
- [ ] **Right-leg drive.** Output current limited for patient safety in normal and single-fault conditions; phase margin over the full range of body capacitance ([Chapter 12]({% link chapters/12_cmcontrol.md %})).
- [ ] **Shields.** Driven, not grounded; a grounded shield costs tens of megohms of common-mode impedance ([Chapter 4]({% link chapters/04_interference.md %})).
- [ ] **Lead-off detection.** DC currents small enough not to disturb the signal, and their effect on the input offset checked ([Chapter 12]({% link chapters/12_cmcontrol.md %})).

## <span class="secnum">C.3</span>Converters

- [ ] **kT/C.** Sampling capacitors sized for noise at the converter's resolution, differential noise included ([Chapters 14]({% link chapters/14_adcspecs.md %}) and [15]({% link chapters/15_switches.md %})).
- [ ] **Matching.** Unit capacitors sized for the DNL target at 3σ, or redundancy and calibration planned ([Chapter 17]({% link chapters/17_cdac.md %})).
- [ ] **Comparator.** Input-referred noise below the LSB budget, offset handled, kickback and metastability checked ([Chapter 16]({% link chapters/16_comparators.md %})).
- [ ] **Switches.** On-resistance across the input range (bootstrapped if needed), charge injection, and leakage in hold at the highest temperature ([Chapter 15]({% link chapters/15_switches.md %})).
- [ ] **Reference.** Charge per conversion supplied without disturbing the reference; decoupling sized ([Chapter 17]({% link chapters/17_cdac.md %})).
- [ ] **ΔΣ loop.** Stability at the largest input including offsets, integrator swing, idle tones with DC inputs ([Chapters 19]({% link chapters/19_dstheory.md %}) and [20]({% link chapters/20_dscircuits.md %})).
- [ ] **Decimator.** Word lengths, droop and attenuation at the chopper frequency ([Chapters 20]({% link chapters/20_dscircuits.md %}) and [23]({% link chapters/23_dsp.md %})).
- [ ] **Clocks.** Jitter adequate for the input frequency; chopper, converter and excitation clocks derived from one source, with no harmonic collisions ([Chapters 13]({% link chapters/13_sampling.md %}) and [28]({% link chapters/28_bioz.md %})).

## <span class="secnum">C.4</span>Simulation

- [ ] Simulator settings do not dominate the result: $$g_\mathrm{min}$$ and the absolute tolerance lowered for teraohm and femtoampere work ([Chapter 30]({% link chapters/30_flow.md %})).
- [ ] Time-varying circuits (choppers, switched capacitors, comparators) simulated with transient or periodic-steady-state noise, not AC noise ([Chapter 30]({% link chapters/30_flow.md %})).
- [ ] Corners (process, ±10 % supply, temperature) and Monte Carlo with the PDK's mismatch libraries for every specification ([Chapter 30]({% link chapters/30_flow.md %})).
- [ ] Spectral tests use coherent sampling or a window whose leakage stays below the noise floor ([Chapter 22]({% link chapters/22_adctest.md %})).

## <span class="secnum">C.5</span>Layout

- [ ] Input pairs and capacitor arrays common-centroid with dummies ([Chapter 17]({% link chapters/17_cdac.md %})).
- [ ] Guard rings around the input pads and between analog and digital areas; high-impedance nodes shielded ([Chapter 12]({% link chapters/12_cmcontrol.md %}#shielding)).
- [ ] Choppers and comparators laid out symmetrically; clock lines kept away from the inputs.
- [ ] Separate supplies and grounds for analog, converter and digital sections ([Chapter 27]({% link chapters/27_soc.md %})).
- [ ] DRC, LVS and post-layout simulation clean at all corners ([Chapter 30]({% link chapters/30_flow.md %})).

## <span class="secnum">C.6</span>Before tape-out

- [ ] Every block's reliability checked: no thin-oxide device sees more than its rated voltage, including the bootstrapped switch and the 3.3 V servo ([Chapter 15]({% link chapters/15_switches.md %})).
- [ ] Test access: raw converter outputs, test points or scan for the digital logic, and a bench plan ([Chapter 22]({% link chapters/22_adctest.md %})).
- [ ] Seal ring, ESD on every pad, padframe from the template ([Chapter 30]({% link chapters/30_flow.md %})).
- [ ] Design files, simulation scripts and results under version control and an open licence.
