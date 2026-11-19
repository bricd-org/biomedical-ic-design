---
title: "Lab 4. The Harrison LNA"
parent: Hands-On Labs
nav_order: 4
permalink: /labs/lab-04/
---

# <span class="chapnum">Lab 4 · SG13G2</span>The Harrison LNA

**Goal.** Build the capacitive-feedback LNA of [Chapter 8]({% link chapters/08_lna.md %}) in SG13G2 and measure its gain, band, noise and NEF against bias current. Goes with Chapters [6]({% link chapters/06_noise.md %}) and [8]({% link chapters/08_lna.md %}).

**Part 1: the pseudo-resistor.**

```bash
python labs/spice/sg13_lna.py
```

The script simulates back-to-back pairs of diode-connected PMOS devices (W/L = 1/10 µm): one or four thin-oxide pairs and one thick-oxide pair, from −0.6 to +0.6 V at 27, 37 and 85 °C. It also extracts the gate capacitance of the NMOS input devices. The results go to `figsrc/data/sg13_pseudo.csv` and `sg13_cgg.csv`. It lowers $$g_\mathrm{min}$$ to $$10^{-15}$$ S. With ngspice's default the thick-oxide pair reads 1.9 TΩ, the parallel conductance of the simulator itself ([Chapter 30]({% link chapters/30_flow.md %})).

| Pseudo-resistor near 0 V | Resistance | High-pass corner with $$C_2$$ = 200 fF | Where in the text |
|---|---|---|---|
| One thin-oxide pair | 2 × 10¹¹ Ω | 4.1 Hz | Section 8.2 |
| Four thin-oxide pairs in series | 7.6 × 10¹¹ Ω | 1.05 Hz | Section 8.2 |
| One thick-oxide pair, 27 / 37 / 85 °C | 5.6 × 10¹³ Ω at 27 °C | 0.014 / 0.032 / 1.0 Hz | Section 8.2 |
| NMOS gate capacitance | about 2.2 fF/µm² | | Section 8.3 |

**Part 2: the amplifier.**

```bash
python labs/spice/lab4_lna.py                # thick-oxide input pair, four bias currents
python labs/spice/lab4_lna.py --input lv     # thin-oxide input pair: watch the bias fail
python labs/spice/lab4_lna.py --pr lv4       # four thin-oxide pseudo-resistor pairs
```

The script builds the single-ended Harrison LNA: $$C_1$$ = 20 pF, $$C_2$$ = 200 fF with a thick-oxide pseudo-resistor across it, $$C_\mathrm{L}$$ = 2 pF and $$V_\mathrm{REF}$$ = 0.65 V. The OTA is a folded cascode with a 250/4 µm NMOS input pair (1000 µm²). Its folding sources and bottom mirror are long devices in strong inversion, scaled with the current, so their noise stays small; the cascode gates use ideal bias sources. For tail currents of 0.5–4 µA it prints the operating point, then runs AC and noise analyses and computes the NEF from the total output noise referred to the input.

Two design choices come from the simulator, not the textbook:

- **A folded cascode, not a telescopic one.** In the Harrison loop the pseudo-resistor holds the OTA's output at its input common mode. A large weak-inversion input pair sits only tens of millivolts below its gate voltage, which leaves no room for a cascode between the pair and an output at the same level.
- **A thick-oxide input pair.** A 250/4 µm thin-oxide NMOS leaks 3–25 pA through its gate in SG13G2. The thick-oxide pseudo-resistor carries only 0.35 pA with 0.6 V across it, so the leakage wins and the output saturates (`--input lv`). Thick-oxide devices leak about 10⁻²⁰ A but have about 2.7 times the flicker-noise power ([Chapter 8]({% link chapters/08_lna.md %}), Section 8.5).

**Expected results** (`labs/spice/out/lab4_lna.png`, `lab4_summary.txt`):

| Tail current | Gain | f<sub>L</sub> | f<sub>H</sub> | Noise, 0.5–100 Hz | NEF |
|---|---|---|---|---|---|
| 0.5 µA | 39.4 dB | 0.014 Hz | 5.0 kHz | 4.4 µVrms | 4.1 |
| 1 µA | 39.4 dB | 0.014 Hz | 8.9 kHz | 3.6 µVrms | 4.1 |
| 2 µA | 39.4 dB | 0.014 Hz | 17.8 kHz | 3.1 µVrms | 4.1 |
| 4 µA | 39.3 dB | 0.014 Hz | 31.6 kHz | 2.8 µVrms | 4.4 |

The gain is 0.6 dB below $$C_1/C_2$$ because of the input devices' gate capacitance; $$f_\mathrm{H}$$ follows $$g_\mathrm{m}/(2\pi A_\mathrm{M} C_\mathrm{L})$$; and the EEG-band noise, two to three times the 1.5 µVrms target, is flicker noise that more current cannot buy down.

**Questions.**

1. Which pseudo-resistor would you use for EEG (0.5 Hz corner) and which for ECG (0.05 Hz)? What happens to each corner on the body (37 °C) and in a hot car (85 °C)? Rerun with `.temp 85`.
2. Why does the noise gain $$(C_1 + C_2 + C_\mathrm{in})/C_1$$, with $$C_\mathrm{in}$$ the input devices' gate capacitance, punish large input devices, and where is the optimum area? Sweep `WIN` and compare with Chapter 8's 6200 µm².
3. The NEF stays near 4, twice the weak-inversion limit of 1.73. Which devices besides the input pair contribute, and what would you change to approach the limit? (Hint: compare their gm/I with the input pair's.)
4. Run `--input lv`. How large is the offset between the OTA's inputs, and why does chopping, with the signal at 4 kHz at the OTA's input, let the thin-oxide devices back in ([Chapter 10]({% link chapters/10_dsl.md %}))?
5. Replace the ideal cascode bias sources with transistor bias circuits and check that the operating point still holds at all four currents.
6. How much of the 1.5 µVrms EEG budget does your unchopped LNA use, and what does that tell you about [Lab 5]({% link labs/lab05_chopper.md %})?

**Deliverable.** An LNA that meets the gain and band, its noise spectrum, and the NEF against bias current with the theoretical limit.

[All labs]({% link labs.md %}) · Previous: [Lab 3. Devices in weak inversion]({% link labs/lab03_devices.md %}) · Next: [Lab 5. Chopper amplifier]({% link labs/lab05_chopper.md %})
