---
title: D. Glossary
parent: Appendices
nav_order: 4
permalink: /appendix/d/
---

# <span class="chapnum">Appendix D</span>Glossary

The acronyms and terms used in the tutorial, with the chapter that introduces each.
{: .chapterlead }

| Term | Meaning | Chapter |
|---|---|---|
| **AAF** | Anti-aliasing filter: removes what would fold into the band when sampled | [11]({% link chapters/11_filters.md %}), [13]({% link chapters/13_sampling.md %}) |
| **Active electrode** | An electrode with a buffer or amplifier at the skin, to lower the impedance its lead presents | [12]({% link chapters/12_cmcontrol.md %}) |
| **AFE** | Analog front-end: everything between the electrodes and the converter | [1]({% link chapters/01_why.md %}) |
| **Applied part (B, BF, CF)** | The IEC 60601 classes of patient connection; CF (cardiac) has the strictest current limits | [4]({% link chapters/04_interference.md %}) |
| **Bootstrapped switch** | A sampling switch whose gate rides on the input, so its on-resistance does not depend on the input | [15]({% link chapters/15_switches.md %}) |
| **CCIA** | Capacitively coupled instrumentation amplifier: gain set by input and feedback capacitors | [7]({% link chapters/07_ia.md %}) |
| **CDAC** | Capacitive digital-to-analog converter, the core of a SAR converter | [17]({% link chapters/17_cdac.md %}) |
| **Chopping** | Modulating the signal up to a higher frequency before an amplifier and back after it, to remove offset and 1/f noise | [9]({% link chapters/09_chopper.md %}) |
| **CIC, CoI** | Cascaded integrator–comb and cascade-of-integrators decimation filters | [20]({% link chapters/20_dscircuits.md %}), [23]({% link chapters/23_dsp.md %}) |
| **CMRR** | Common-mode rejection ratio: differential gain over common-mode gain | [4]({% link chapters/04_interference.md %}), [7]({% link chapters/07_ia.md %}) |
| **Coherent sampling** | Choosing a test tone that completes a whole number of cycles in the record, so the FFT needs no window | [22]({% link chapters/22_adctest.md %}) |
| **Cole model** | A tissue-impedance model with a constant-phase dispersion between a low- and a high-frequency resistance | [28]({% link chapters/28_bioz.md %}) |
| **DNL, INL** | Differential and integral nonlinearity: errors of each code step and of the transfer curve, in LSB | [14]({% link chapters/14_adcspecs.md %}) |
| **DRL, RLD** | Driven right leg, right-leg drive: feedback that drives the body's common mode through a third electrode | [12]({% link chapters/12_cmcontrol.md %}) |
| **DSL** | DC servo loop: an integrator that removes the electrode offset from the amplifier | [10]({% link chapters/10_dsl.md %}) |
| **Driven shield, guard** | A shield or guard held at the signal's own voltage, so its capacitance draws no current | [4]({% link chapters/04_interference.md %}), [12]({% link chapters/12_cmcontrol.md %}) |
| **ΔΣ (delta-sigma)** | An oversampling converter that shapes its quantisation noise out of the band | [19]({% link chapters/19_dstheory.md %}) |
| **ECG, EEG, EMG, EOG** | Electro-cardio-, encephalo-, myo- and oculography: heart, brain, muscle and eye potentials | [2]({% link chapters/02_signals.md %}) |
| **ECoG, LFP** | Electrocorticography and local field potentials, recorded on or in the brain | [2]({% link chapters/02_signals.md %}) |
| **EIS, bioZ** | Electrical impedance spectroscopy, bioimpedance: measuring tissue impedance with a small current | [28]({% link chapters/28_bioz.md %}) |
| **ENOB** | Effective number of bits: (SNDR − 1.76 dB)/6.02 | [13]({% link chapters/13_sampling.md %}) |
| **ExG** | Any of the surface biopotentials (ECG, EEG, EMG, EOG) | [2]({% link chapters/02_signals.md %}) |
| **FoM (Walden, Schreier)** | Converter figures of merit: energy per conversion step, and SNDR plus bandwidth over power | [14]({% link chapters/14_adcspecs.md %}) |
| **gm/I<sub>D</sub>** | Transconductance efficiency, the design variable of the gm/ID method | [5]({% link chapters/05_devices.md %}) |
| **Incremental ΔΣ** | A ΔΣ converter reset before each conversion, so it behaves like a Nyquist converter with high resolution | [19]({% link chapters/19_dstheory.md %}), [20]({% link chapters/20_dscircuits.md %}) |
| **IQ demodulation** | Multiplying by in-phase and quadrature references to recover amplitude and phase | [28]({% link chapters/28_bioz.md %}) |
| **kT/C** | The thermal noise frozen on a capacitor when a switch opens | [15]({% link chapters/15_switches.md %}) |
| **LDO** | Low-dropout regulator | [27]({% link chapters/27_soc.md %}) |
| **LNA** | Low-noise amplifier, the first gain stage | [8]({% link chapters/08_lna.md %}) |
| **Moderate / weak inversion** | MOSFET operation near or below threshold, where gm/ID is highest | [5]({% link chapters/05_devices.md %}) |
| **NEF, PEF** | Noise and power efficiency factors: an amplifier's noise for its current, relative to one bipolar transistor | [6]({% link chapters/06_noise.md %}) |
| **NTF, STF** | Noise and signal transfer functions of a ΔΣ loop | [19]({% link chapters/19_dstheory.md %}) |
| **OSR** | Oversampling ratio: sample rate over twice the signal bandwidth | [13]({% link chapters/13_sampling.md %}) |
| **OTA** | Operational transconductance amplifier | [8]({% link chapters/08_lna.md %}) |
| **PGA** | Programmable-gain amplifier | [11]({% link chapters/11_filters.md %}) |
| **Pseudo-resistor** | Diode-connected MOSFETs far below threshold, used as teraohm resistors | [8]({% link chapters/08_lna.md %}) |
| **PSRR** | Power-supply rejection ratio | [27]({% link chapters/27_soc.md %}) |
| **RF rectification** | Radio-frequency interference turned into a low-frequency error by a nonlinear input stage | [12]({% link chapters/12_cmcontrol.md %}) |
| **SAR** | Successive-approximation register converter: a binary search with a DAC and a comparator | [18]({% link chapters/18_sar.md %}) |
| **SFDR, SNDR, THD** | Spurious-free dynamic range, signal to noise and distortion, total harmonic distortion | [14]({% link chapters/14_adcspecs.md %}) |
| **SQNR** | Signal-to-quantisation-noise ratio: 6.02N + 1.76 dB for an ideal N-bit converter | [13]({% link chapters/13_sampling.md %}) |
| **StrongARM** | A clocked latch comparator with no static current | [16]({% link chapters/16_comparators.md %}) |
| **Tetrapolar** | Impedance measurement with separate current and voltage electrodes | [28]({% link chapters/28_bioz.md %}) |
| **Z<sub>cm</sub>** | Common-mode input impedance of the front-end | [4]({% link chapters/04_interference.md %}) |
