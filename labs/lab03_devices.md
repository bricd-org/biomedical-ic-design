---
title: "Lab 3. Devices in weak inversion"
parent: Hands-On Labs
nav_order: 3
permalink: /labs/lab-03/
---

# <span class="chapnum">Lab 3 · SG13G2</span>Devices in weak inversion

**Goal.** Characterise the SG13G2 devices you will design with: gm/ID lookup tables, flicker noise against gate area, and the HBT against the MOSFET as an input device. Labs 4 and 5 reuse the tables. Goes with Chapters [5]({% link chapters/05_devices.md %}) and [6]({% link chapters/06_noise.md %}).

**Run.** With Docker and the container of the [set-up]({% link labs.md %}#setup):

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

[All labs]({% link labs.md %}) · Previous: [Lab 2. Electrodes and interference]({% link labs/lab02_interference.md %}) · Next: [Lab 4. The Harrison LNA]({% link labs/lab04_lna.md %})
