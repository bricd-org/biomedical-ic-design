---
title: "Lab 10. Switched-capacitor ΔΣ"
parent: Hands-On Labs
nav_order: 10
permalink: /labs/lab-10/
---

# <span class="chapnum">Lab 10 · SG13G2</span>Switched-capacitor ΔΣ

**Goal.** Build the Lab 9 loop from switched capacitors and SG13G2 switches, and find out which circuit imperfections the ideal model leaves out. Goes with [Chapter 20]({% link chapters/20_dscircuits.md %}).

**Run.**

```bash
python labs/spice/lab10_scds.py             # three behavioural OTAs and the SG13G2 OTA, in parallel
python labs/spice/lab10_scds.py --ota sg13  # only the transistor-level OTA (labs/spice/sg13_ota.py)
python labs/spice/lab10_scds.py --n 8192
```

The loop is the second-order CIFB structure of [Figure 20.1]({% link chapters/20_dscircuits.md %}#fig-20-1), run free rather than reset, so that its spectrum can be compared with the ideal model. Each integrator is the parasitic-insensitive circuit of [Figure 20.2]({% link chapters/20_dscircuits.md %}#fig-20-2) with SG13G2 transmission-gate switches on two non-overlapping 512 kHz phases: $$C_\mathrm{s1}/C_\mathrm{i1}$$ = 1.1 pF / 2.2 pF and $$C_\mathrm{s2}/C_\mathrm{i2}$$ = 0.25 pF / 1 pF. The DAC connects the sampling capacitors' input side to $$V_\mathrm{CM} \pm V_\mathrm{REF}$$ in phase 2, and the 1-bit quantiser is latched at the end of phase 1. The model is single-ended with a ±0.25 V range, which stands for the chip's fully differential ±0.5 V and keeps the integrators within a 1.2 V supply. The OTAs are behavioural (one pole, gain $$A_0$$, bandwidth GBW), so that their effect can be varied. The input is a coherent tone at −6 dBFS, and the in-band SQNR at OSR 128 is compared with the ideal difference equations on the same input.

**Expected results.**

| Case | SQNR at OSR 128 | Integrator swing, x<sub>1</sub> / x<sub>2</sub> |
|---|---|---|
| Ideal difference equations | 92.4 dB | 0.31 / 0.11 V |
| SC loop, A<sub>0</sub> = 60 dB, GBW = 5 MHz | 88.3 dB | 0.32 / 0.12 V |
| SC loop, A<sub>0</sub> = 40 dB, GBW = 5 MHz | 83.3 dB | 0.30 / 0.10 V |
| SC loop, A<sub>0</sub> = 60 dB, GBW = 0.5 MHz | 84.5 dB | 0.26 / 0.10 V |
| SC loop, SG13G2 folded-cascode OTAs, 2 µA each | 85.3 dB | 0.27 / 0.11 V |

With a good OTA the transistor-switch loop comes within 4 dB of the ideal model, and its integrators swing exactly as the model predicts once the loop has started. A 40 dB OTA turns each integrator into a leaky one and costs 9 dB. A 0.5 MHz OTA cannot settle in a 0.98 µs phase and costs 8 dB; it also takes 123 cycles to recover from start-up, during which its integrators sit on the rails, compared with 9 cycles for the 5 MHz OTA. The last row replaces the behavioural OTAs with the transistor-level folded cascode of `labs/spice/sg13_ota.py`: a PMOS input pair at a 1 µA tail, NMOS folding sinks, cascodes and a wide-swing PMOS mirror, 2 µA in all, with an ideal bias network inside the subcircuit. `python labs/spice/sg13_ota.py` characterises it: 57.9 dB of gain, 1.96 MHz of unity-gain frequency into 1 pF, 78° of phase margin and an output range of 0.37–0.86 V. That range is the catch: integrator 1 wants to swing ±0.31 V around 0.6 V, the OTA gives about ±0.25 V, so the peaks are squeezed (0.27 V) and the loop loses 3 dB against the behavioural OTA of the same gain. Scale $$a_1$$ down, or give the first OTA a two-stage output, and it comes back. Chapter 20's estimate of about 1 µA for a 1.2 MHz OTA sits between the two cases (the record's window suppresses the start-up cycles, so they do not affect the SQNR). The swings are given as 99.9th percentiles after the first 200 cycles; the plot is `labs/spice/out/lab10_scds.png`.

**Questions.**

1. Derive the integrator leakage that a finite OTA gain causes, $$x_1 \to (1 - \epsilon)\,x_1$$ with $$\epsilon \approx (1 + C_\mathrm{s}/C_\mathrm{i})/A_0$$, and the noise floor it adds at low frequencies. Does it explain your 40 dB result?
2. How low can the GBW go before incomplete settling costs SQNR? Compare with the 1 % settling estimate of Worked Example 20.1.
3. Add the kT/C noise of $$C_\mathrm{s1}$$ in Python to the SPICE bit stream's input-referred spectrum. Which limits the converter, quantisation or thermal noise?
4. Remove the non-overlap of the clock phases. What happens, and why?
5. Turn the loop into the incremental converter of Chapter 20: reset both integrators every 1024 cycles and decimate with the CoI filter of `lab9_deltasigma.py`. Measure the conversion error at a few DC inputs.

**Deliverable.** The transistor-switch loop's spectrum and SQNR against the ideal model, with the OTA gain and bandwidth you would specify.

[All labs]({% link labs.md %}) · Previous: [Lab 9. ΔΣ by design]({% link labs/lab09_deltasigma.md %}) · Next: [Lab 11. ECG chain end to end]({% link labs/lab11_ecg.md %})
