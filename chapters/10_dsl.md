---
title: 10. Input Impedance, DC Servo Loops and Offset Rejection
parent: "Part II · The Analog Front-End"
nav_order: 10
permalink: /part-2/ch10/
chapter: 10
---

# <span class="chapnum">Chapter 10</span>Input Impedance, DC Servo Loops and Offset Rejection

Electrodes bring hundreds of millivolts of DC and megaohms of source impedance. The front-end must reject the first without loading the second.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 3 (Part II with Labs 3–5). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- derive the input impedance of a capacitively coupled, chopped front-end;
- design a positive-feedback impedance-boosting loop;
- design a DC servo loop (DSL) that rejects ±300 mV of electrode offset;
- compare DC-coupled and AC-coupled front-ends;
- state the trade-offs for dry electrodes.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do you tolerate ±300 mV of electrode offset and keep the input impedance high enough for dry electrodes?

</div>

## <span class="secnum">10.1</span>Input impedance of chopped CCIAs

Switched-capacitor input resistance, its frequency dependence, and the 2.5 MΩ the ECG standards require ([Chapter 4]({% link chapters/04_interference.md %})).

## <span class="secnum">10.2</span>Positive-feedback impedance boosting

Pre-charging the input capacitors from the output to cancel the current drawn from the electrode; stability and matching limits.

## <span class="secnum">10.3</span>The DC servo loop

An integrator in a feedback path subtracts the electrode offset at the input; the loop sets the high-pass corner and must not add noise in band.

## <span class="secnum">10.4</span>DC-coupled versus AC-coupled front-ends

DC coupling keeps the electrode offset for motion-artefact detection and needs a wide-range ADC; AC coupling removes it in the analog domain. The choice decides between the two converters of Part III.

## <span class="secnum">10.5</span>Dry electrodes

Megaohm source impedance, larger offsets and motion artefacts; what each front-end option buys and costs.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 5]({% link chapters/31_labs.md %}#lab-5) measures the input impedance with and without a chopper and verifies ±300 mV offset tolerance with the DC servo loop.

</div>

**Read with this chapter.** Yazicioglu, Van Hoof and Puers {% include cite.html keys="yazicioglubook" %}, Spinelli et al. {% include cite.html keys="spinelli2003" %}, Chi et al. {% include cite.html keys="chi2010" %}.
