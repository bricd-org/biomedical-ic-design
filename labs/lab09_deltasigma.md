---
title: "Lab 9. ΔΣ by design"
parent: Hands-On Labs
nav_order: 9
permalink: /labs/lab-09/
---

# <span class="chapnum">Lab 9 · Python</span>ΔΣ by design

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

[All labs]({% link labs.md %}) · Previous: [Lab 8. SAR ADC]({% link labs/lab08_sar.md %}) · Next: [Lab 10. Switched-capacitor ΔΣ]({% link labs/lab10_scdeltasigma.md %})
