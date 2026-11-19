---
title: "Lab 2. Electrodes and interference"
parent: Hands-On Labs
nav_order: 2
permalink: /labs/lab-02/
---

# <span class="chapnum">Lab 2 · Python</span>Electrodes and interference

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

[All labs]({% link labs.md %}) · Previous: [Lab 1. Biosignal explorer]({% link labs/lab01_explorer.md %}) · Next: [Lab 3. Devices in weak inversion]({% link labs/lab03_devices.md %})
