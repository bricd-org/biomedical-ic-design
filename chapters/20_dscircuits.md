---
title: "20. ΔΣ Circuits: Discrete-Time, Continuous-Time and Incremental"
parent: "Part III · Data Converters"
nav_order: 20
permalink: /part-3/ch20/
chapter: 20
---

# <span class="chapnum">Chapter 20</span>ΔΣ Circuits: Discrete-Time, Continuous-Time and Incremental

From the loop filter on paper to integrators in silicon, and to the incremental converter that serves the high-resolution Open-BioAFE channels.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 4 (the rest of Part III with Labs 7, 8 and 10). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- build switched-capacitor integrators and set their OTA requirements;
- design continuous-time loops with resistive or Gm-C integrators and use their inherent anti-aliasing;
- handle excess loop delay;
- design an incremental ΔΣ converter for multiplexed channels;
- design and budget the decimation filter (CIC/sinc$$^K$$ and half-band FIR).

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do you implement the 2nd-order incremental modulator of Open-BioAFE and its decimator within the power budget?

</div>

## <span class="secnum">20.1</span>Switched-capacitor integrators

Charge transfer, OTA gain and slew requirements, and $$kT/C$$ noise of the sampling capacitor.

## <span class="secnum">20.2</span>Continuous-time ΔΣ

Resistive and Gm-C integrators; the implicit anti-aliasing of a CT loop; clock-jitter sensitivity.

## <span class="secnum">20.3</span>Excess loop delay

How a fraction of a clock period of delay destabilises the loop and how to compensate it.

## <span class="secnum">20.4</span>Incremental ΔΣ

Resetting the loop for every sample so channels can be multiplexed; the resolution versus number of cycles.

## <span class="secnum">20.5</span>Decimation

CIC (sinc$$^K$$) and half-band FIR stages, their word lengths and their power.

## <span class="secnum">20.6</span>The reference design

The full 2nd-order incremental modulator of the Open-BioAFE ECG/EEG mode.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 10]({% link chapters/31_labs.md %}#lab-10) implements the Lab 9 loop with switched-capacitor integrators and a 1-bit quantiser in SG13G2 and compares it with the ideal model.

</div>

**Read with this chapter.** Schreier, Temes and Pavan {% include cite.html keys="schreier" %}.
