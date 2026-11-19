---
title: "Lab 15. Bioimpedance IQ readout"
parent: Hands-On Labs
nav_order: 15
permalink: /labs/lab-15/
---

# <span class="chapnum">Lab 15 · SG13G2</span>Bioimpedance IQ readout

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

**Part 2 (SG13G2).**

```bash
python labs/spice/lab15_bioz_sg13.py
python labs/spice/lab15_bioz_sg13.py --iexc 50e-6
```

The excitation is one PMOS current mirror (20 µA) steered by an SG13G2 transmission-gate H-bridge at 50 kHz into the outer electrodes through 1 µF blocking capacitors. The load is tetrapolar, with wet-electrode impedances on all five electrodes; the reference electrode returns to mid-supply through the 150 kΩ safety resistor of [Chapter 12]({% link chapters/12_cmcontrol.md %}). The measured segment is a Debye network ($$R_\infty$$ = 30 Ω in series with 30 Ω ‖ 177 nF), because Cole's α = 0.7 has no exact RC equivalent. A behavioural instrumentation amplifier (gain 10) feeds square-wave I and Q demodulators built from SG13G2 transmission gates.

**Expected results.** The circuit reads 37.2 Ω at −17.0°, within 2.1 % in magnitude and 1.3° in phase of the ideal square-wave reading computed in Python (38.0 Ω, −15.7°). Both are below the true 40.2 Ω, −19.2° at 50 kHz, because the square waves also weigh the tissue's lower impedance at the odd harmonics. Three details mattered on the way, and each is a design lesson:

- Two separate mirrors for source and sink never match; their difference has nowhere to go, so the bridge drifts out of saturation and the reading falls by half. One source, with the bridge returning to mid-supply, fixes it.
- Without the 150 kΩ in the reference electrode, part of the excitation returns through it and bypasses the measured segment.
- The blocking capacitors take tens of milliseconds to reach their balanced voltages; the simulation starts there.

**Questions.**

1. Compare the circuit's error with Part 1's square-wave error. Which would you calibrate with an on-chip resistor, and at how many frequencies?
2. Make the H-bridge switches small (2/0.13 µm) again. How does their on-resistance show up in the reading?
3. Replace the square-wave excitation by the three-level pseudo-sine of Part 1's question 3. How much closer does the reading get to the true impedance?

**Deliverable.** The Cole plot, the ΔZ resolution against current with the safety limit, and the analog against digital IQ error.

[All labs]({% link labs.md %}) · Previous: [Lab 14. Layout to GDS]({% link labs/lab14_layout.md %}) · Next: [Capstone. One Open-BioAFE channel]({% link labs/capstone.md %})
