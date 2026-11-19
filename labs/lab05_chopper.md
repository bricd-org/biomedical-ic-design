---
title: "Lab 5. Chopper amplifier"
parent: Hands-On Labs
nav_order: 5
permalink: /labs/lab-05/
---

# <span class="chapnum">Lab 5 · SG13G2</span>Chopper amplifier

**Goal.** See chopping work in a circuit: what it does to the amplifier's offset and 1/f noise, what it costs in ripple and input impedance, and how a DC servo loop handles 300 mV of electrode offset. Goes with Chapters [9]({% link chapters/09_chopper.md %}) and [10]({% link chapters/10_dsl.md %}).

**Run.**

```bash
python labs/spice/lab5_chopper.py              # chopped and unchopped, in parallel, 20-40 minutes
python labs/spice/lab5_chopper.py --voff 0.1   # another electrode offset
python labs/spice/lab5_chopper.py --ota sg13   # the chopped case with transistor-level SG13G2 OTAs
```

The signal path is that of [Figure 10.1]({% link chapters/10_dsl.md %}#fig-10-1), fully differential. Its parts:

- **choppers:** SG13G2 transmission gates at 4 kHz with 20 ns of non-overlap;
- **feedback:** $$C_\mathrm{in}$$ = 20 pF and $$C_\mathrm{fb}$$ = 200 fF, with 10 GΩ across $$C_\mathrm{fb}$$ (enough when chopped, and as much as gate leakage allows, [Chapter 8]({% link chapters/08_lna.md %}); the unchopped run uses 10 TΩ);
- **servo loop:** integrates the demodulated output and feeds it back, chopped, through $$C_\mathrm{DSL}$$ = 4 pF;
- **output filter:** a 500 Hz anti-alias filter after the demodulator.

The amplifier is behavioural, so that its imperfections are known exactly: gain 10⁴ with a 10 MHz bandwidth, 1 mV of input offset, and 30 nV/√Hz of white noise plus 1/f noise with a corner near 200 Hz, from ngspice's `trnoise` source. The electrodes carry 300 mV of offset and a 1 mV, 37 Hz test tone. The script runs the circuit chopped and with the choppers held straight through.

**Expected results.**

| Quantity | Chopped | Unchopped |
|---|---|---|
| Gain at 37 Hz | 91.7 | 94.5 |
| Input noise, 4–100 Hz | 0.35 µVrms | 1.17 µVrms |
| Ripple at 4 kHz, before the filter | 1.2 mV | — |
| Servo output for 300 mV of electrode offset | −1.500 V (expected −1.500 V) | — |
| Input impedance, differential | 6.5 MΩ (1/(2 f<sub>ch</sub> C<sub>in</sub>) = 6.25 MΩ) | about 18 GΩ |

**With transistor-level OTAs.** `--ota sg13` replaces the behavioural amplifier with two low-noise SG13G2 folded cascodes from `labs/spice/sg13_ota.py` (1000 µm² PMOS input pair, 2 µA each), used as a pseudo-differential pair, with their measured input noise (93 nV/√Hz white, 1/f corner about 0.9 kHz, per OTA) copied into the trnoise source. The first run failed instructively: both outputs sat at the bottom rail, because the thin-oxide input gates leak about 60 pA, which is 0.6 V across the 10 GΩ feedback resistor (the leakage Chapter 8 met in pseudo-resistors). With 1 GΩ the shift drops to 60 mV and the R<sub>fb</sub>C<sub>fb</sub> corner, 800 Hz, stays below f<sub>ch</sub>. The chopped amplifier then gives a gain of 82.0 at 37 Hz (the OTA's 62 dB leaves a loop gain of only about 10 at this feedback factor), 2.2 mV of ripple, 6.4 MΩ of input impedance, the servo at −1.500 V, and 1.82 µVrms of input noise: five times the behavioural amplifier's, because this folded cascode's sinks and mirror more than double the input pair's noise and two OTAs add √2. The unchopped case cannot be run at all: no feedback resistor both passes 37 Hz and survives the leakage. Redesigning the OTA for the chip's 0.36 µVrms, with a current-reuse or telescopic input stage and thick-oxide or smaller input devices, is the exercise.

Chopping moves the amplifier's 1/f noise up to 4 kHz, where the filter removes it, and leaves its white floor: the in-band noise falls 3.3 times. The price is the 1.2 mV of ripple, the amplifier's 1 mV offset chopped up to 4 kHz, and an input impedance that falls from gigaohms to 6.5 MΩ, as Chapter 9 predicts. The servo loop cancels the 300 mV electrode offset with exactly the −1.5 V that $$C_\mathrm{in}/C_\mathrm{DSL}$$ requires; at 3.3 V it has room for about ±0.6 V. The chopped gain is slightly lower than the unchopped one, because the chopped signal passes through the amplifier at 4 kHz and its harmonics, where the 10 MHz bandwidth divided by the noise gain of 121 is no longer far away.

Three things in the measurement are worth copying. The input current is averaged over time, not over ngspice's unevenly spaced points, which cluster at the switching edges. The noise is measured after a least-squares fit of the test tone and of the servo loop's settling, which is still decaying when the record starts and would otherwise look like low-frequency noise. And the noise band starts at 4 Hz, because a 0.25 s record cannot resolve less.

**Questions.**

1. Where in the output spectrum (`labs/spice/out/lab5_chopper.png`) has the amplifier's 1/f noise gone in the chopped run, and what removes it there?
2. The ripple is the amplifier's offset, chopped up to 4 kHz and multiplied by the noise gain. Check the number against $$V_\mathrm{os}(1 + (C_\mathrm{in} + C_\mathrm{DSL})/C_\mathrm{fb})$$, and design a ripple-reduction loop for it ([Chapter 9]({% link chapters/09_chopper.md %}), Section 9.3).
3. Reduce the amplifier's bandwidth to 1 MHz. Why does the chopped gain fall while the unchopped gain does not?
4. Raise the electrode offset to 0.5 V. What does the servo's output have to do, and what limits the offset the servo can cancel at 3.3 V?
5. Add the positive-feedback impedance-boosting loop of [Chapter 10]({% link chapters/10_dsl.md %}) and measure the input impedance again. How close to 200 MΩ do you get, and what sets the limit?

**Deliverable.** Noise spectra before and after chopping, the ripple and input impedance, and the servo loop's response to the electrode offset.

[All labs]({% link labs.md %}) · Previous: [Lab 4. The Harrison LNA]({% link labs/lab04_lna.md %}) · Next: [Lab 6. Ideal ADC and spectral testing]({% link labs/lab06_adctest.md %})
