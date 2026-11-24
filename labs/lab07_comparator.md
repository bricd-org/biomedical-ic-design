---
title: "Lab 7. StrongARM comparator"
parent: Hands-On Labs
nav_order: 7
permalink: /labs/lab-07/
---

# <span class="chapnum">Lab 7 · SG13G2</span>StrongARM comparator

**Goal.** Characterise the SAR's comparator in SG13G2: how fast it decides, what a decision costs, how noisy it is in each mode and how large its offset is. Goes with [Chapter 16]({% link chapters/16_comparators.md %}).

**Run.**

```bash
python labs/spice/lab7_comparator.py            # 40 Monte Carlo samples: 15 minutes to an hour
python labs/spice/lab7_comparator.py --mc 100
python labs/spice/lab7_comparator.py --parse-only
```

The circuit is the StrongARM latch of [Figure 16.1]({% link chapters/16_comparators.md %}#fig-16-1) with a 4/1 µm NMOS input pair (4 µm²), minimum-length latch and reset devices, output inverters and a NOR SR latch, at 1.2 V with the inputs at 0.6 V. It runs in two modes: fast, with only the parasitic capacitance on the integration nodes P and Q, and low-noise, with 342 fF added there ([Worked Example 16.1]({% link chapters/16_comparators.md %})). The script measures:

1. the delay from the clock edge to a full-swing decision, for inputs from 10 µV to 10 mV;
2. the energy per decision, from the supply charge in one clock cycle;
3. the input-referred noise of the low-noise mode, from the integrated charge, $$\sigma_v = 2nU_T\sqrt{q/Q_\mathrm{int}}$$ (ngspice simulates no device noise in a transient, so Chapter 16's key equation stands in);
4. the offset, by Monte Carlo with the PDK's mismatch models (`mos_tt_mismatch`, `mm_ok=1`): the input ramps slowly up and back down, and the SR latch records where the decision flips each way. An occasional mismatch sample fails to converge; it is skipped.

**Expected results.**

| Quantity | Fast mode | Low-noise mode |
|---|---|---|
| Delay at 10 µV / 100 µV / 1 mV / 10 mV | 0.66 / 0.58 / 0.48 / 0.38 ns | 5.4 / 5.2 / 4.7 / 4.1 ns |
| Energy per decision | 0.08 pJ | 1.06 pJ |
| Input-referred noise | about 0.6 mV (parasitic charge only) | 61 µVrms |
| Offset (Monte Carlo, 29 samples) | σ = 4.5 mV, mean −0.6 mV | |
| Up and down thresholds | 2.0 mV apart | |

The delay grows by about 0.09 ns per decade of smaller input: the regeneration time constant is about 40 ps in the fast mode. The low-noise mode reproduces Worked Example 16.1: 61 µVrms for about 1 pJ. The offset is about 1.6 times the 2.8 mV that Pelgrom's law gives for the input pair alone. In the fast mode the integration phase is short, so the mismatch of the minimum-size latch devices, about 11 mV each, is divided by only a small gain. The up and down thresholds differ because charge left from the previous decision is not fully reset; the comparator leans away from what it decided before. A SAR does not mind either effect much, as long as the offset is calibrated and the redundancy covers the rest ([Chapter 18]({% link chapters/18_sar.md %})).

A practical note: an earlier version of the script stepped the transient at 1 ns, too coarse for a regeneration of a few hundred picoseconds, and the comparator made wrong decisions with 10 mV at its input. Resolve the fastest event in the circuit before trusting a decision.

**Questions.**

1. Plot the delay against ln(1/Δv). What regeneration time constant do you read, and how does it compare with $$C/g_\mathrm{m}$$ of the latch?
2. How does the offset change in the low-noise mode, where the integration lasts ten times longer? Rerun the Monte Carlo with the 342 fF added.
3. Make the latch devices four times larger. What happens to the offset, the delay and the energy?
4. The SAR needs 61 µV of noise only in its last decisions (Lab 8). How many decisions can use the fast mode, and what does that save?
5. Replace the StrongARM by a double-tail latch, the topology of the Open-BioAFE target box. Compare noise, energy and kickback.

**Deliverable.** A comparator with its delay, energy, noise in both modes and offset distribution, and the mode schedule you would use in the SAR.

[All labs]({% link labs.md %}) · Previous: [Lab 6. Ideal ADC and spectral testing]({% link labs/lab06_adctest.md %}) · Next: [Lab 8. SAR ADC]({% link labs/lab08_sar.md %})
