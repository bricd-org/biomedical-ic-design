---
title: 11. Filters, PGAs and Anti-Aliasing
parent: "Part II · The Analog Front-End"
nav_order: 11
permalink: /part-2/ch11/
chapter: 11
---

# <span class="chapnum">Chapter 11</span>Filters, PGAs and Anti-Aliasing

Between the LNA and the ADC the signal needs more gain, a defined bandwidth and protection from aliasing, at corner frequencies from a fraction of a hertz to a few kilohertz.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 3 (Part II with Labs 3–5). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- design Gm-C and switched-capacitor filters with sub-hertz to kilohertz corners;
- design a programmable-gain amplifier for the three Open-BioAFE modes;
- choose the anti-aliasing filter order from the ADC oversampling ratio;
- explain why mains notch filters belong in the digital domain.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How much filtering and gain does each mode need before the SAR and the ΔΣ ADC, and where should each filter live?

</div>

## <span class="secnum">11.1</span>Very-low-frequency filters on chip

Gm-C filters with nanoampere transconductors and switched-capacitor filters at low clock rates; area, noise and linearity at sub-hertz corners.

## <span class="secnum">11.2</span>Programmable gain

Capacitive and resistive PGAs; gain steps for ECG, EEG and EMG amplitudes ([Chapter 2]({% link chapters/02_signals.md %})) so the ADC range is used well.

## <span class="secnum">11.3</span>Anti-aliasing versus oversampling

The required attenuation at $$f_\mathrm{s} - f_\mathrm{B}$$ for the SAR; why the ΔΣ converter relaxes the analog filter; mains harmonics and EMG folding into the ECG band ([Chapter 13]({% link chapters/13_sampling.md %})).

## <span class="secnum">11.4</span>Mains notch filtering

Analog notches drift and distort; adaptive and comb notches after the ADC ([Chapter 23]({% link chapters/23_dsp.md %})) track the mains frequency.

**Read with this chapter.** Razavi {% include cite.html keys="razavi" %} (switched-capacitor circuits), Yazicioglu, Van Hoof and Puers {% include cite.html keys="yazicioglubook" %}.
