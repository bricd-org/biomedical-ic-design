---
title: "Lab 8. SAR ADC"
parent: Hands-On Labs
nav_order: 8
permalink: /labs/lab-08/
---

# <span class="chapnum">Lab 8 · SG13G2</span>SAR ADC

**Goal.** Put the SAR converter of Chapter 18 together from its parts and measure what each costs: the sampling switch, the capacitor mismatch, the comparator's noise modes and the energy. Goes with Chapters [15]({% link chapters/15_switches.md %}), [17]({% link chapters/17_cdac.md %}) and [18]({% link chapters/18_sar.md %}).

**Run.**

```bash
python labs/spice/lab8_sar.py               # Part A in ngspice, Part B in Python
python labs/spice/lab8_sar.py --part b      # the behavioural converter only, no Docker
```

**Part A: the sampler (SG13G2).** One side of the differential input, 0.6 V ± 0.25 V, is sampled onto 4 pF at 16 kS/s by a 2/0.13 µm NMOS switch, first driven to 1.2 V, then bootstrapped as in [Figure 15.1]({% link chapters/15_switches.md %}#fig-15-1)b (ideal steering switches and a 200 fF bootstrap capacitor). The held samples of a coherent 812.5 Hz tone go through `adctest.py`.

**Part B: the converter (Python).** Chapter 18's design: fourteen decisions with integer radix-1.8 weights (1, 2, 3, 5, 9, 17, 30, 55, … units, each at most one more than the sum below it, so no decision has negative redundancy), unit capacitors with σ<sub>u</sub> = 1.22 %, the differential kT/C noise of 4 pF per side, and the comparator of Lab 7: 61 µV of noise in its low-noise mode, 0.6 mV in its fast mode. The weights are read as designed or after a foreground calibration. The script sweeps how many of the last decisions use the low-noise mode, with the energies of Lab 7 (1.06 and 0.08 pJ) and 3.7 pJ for the DAC, logic and sampler.

**Expected results.**

| Test | Result |
|---|---|
| Plain NMOS sampling switch | SFDR 50 dB, SNDR 45 dB: charge injection and on-resistance follow the input |
| Bootstrapped switch (idealised steering) | SFDR above 100 dB |
| SAR, 3 / 5 / 7 / 14 low-noise decisions (calibrated, median of 20 chips) | ENOB 10.0 / 10.5 / 11.0 / 11.4 |
| Energy per conversion for the same cases | 7.8 / 9.7 / 11.7 / 18.5 pJ |
| Walden FoM at 16 kS/s, 7 low-noise decisions | 5.6 fJ per step |
| DNL / INL, calibrated, all decisions low-noise | −1.0 to +1.3 LSB / ±0.8 LSB |

The redundancy of the lowest decisions, 0–4 LSB, is smaller than the fast mode's 2.5 LSB of noise, so only the first seven decisions may be fast. That sets the design point of [Chapter 18]({% link chapters/18_sar.md %}): seven low-noise decisions, 11 effective bits, about 11.7 pJ per conversion.

**Questions.**

1. Why does the plain switch distort although its time constant, a few nanoseconds, is a thousand times shorter than the tracking time? Which part of its error depends on the input?
2. Change the radix to 1.7 and 1.9 (keep 14 cycles). How do the redundancy, the range and the ENOB with seven low-noise decisions change?
3. Lower the fast mode's noise to 0.3 mV by giving it a little load capacitance. How many decisions can then be fast, and what is the energy?
4. With designed weights the ENOB is almost as good as with calibrated ones here. Raise σ<sub>u</sub> to 3 % and repeat. When does calibration start to matter?
5. Replace the behavioural comparator by the transistor-level StrongARM of Lab 7 in a short ngspice transient of one conversion, with the decisions fed back by a behavioural SAR register. Does the conversion settle within the 62.5 µs period?

**Deliverable.** The sampler's SFDR with and without bootstrapping, and a SAR design point (low-noise decisions, ENOB, energy, FoM) with the evidence for it.

[All labs]({% link labs.md %}) · Previous: [Lab 7. StrongARM comparator]({% link labs/lab07_comparator.md %}) · Next: [Lab 9. ΔΣ by design]({% link labs/lab09_deltasigma.md %})
