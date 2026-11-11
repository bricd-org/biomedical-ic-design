---
title: 8. The AC-Coupled Biopotential LNA
parent: "Part II · The Analog Front-End"
nav_order: 8
permalink: /part-2/ch08/
chapter: 8
---

# <span class="chapnum">Chapter 8</span>The AC-Coupled Biopotential LNA

Two capacitors, two pseudo-resistors and an OTA: the Harrison amplifier is the circuit every neural and ExG front-end is compared with.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 3 (Part II with Labs 3–5). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- derive the gain, band edges and noise of the capacitive-feedback LNA;
- explain how MOS-bipolar pseudo-resistors reach high-pass corners in the millihertz range;
- design the OTA (folded cascode or current-scaled telescopic) for a given noise and bandwidth;
- budget gain, bandwidth and noise for ECG, EEG and EMG modes;
- recognise the linearity, leakage and PVT problems of pseudo-resistors.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do you size the capacitors, pseudo-resistors and OTA so that one AC-coupled LNA meets the noise, bandwidth and power targets of every Open-BioAFE mode?

</div>

## <span class="secnum">8.1</span>The Harrison topology

Midband gain $$A_\mathrm{M} = C_1/C_2$$, low corner $$f_\mathrm{L} = 1/(2\pi R_\mathrm{pr} C_2)$$ and high corner set by the OTA transconductance and load; the original design reaches 0.025–7200 Hz with 2.2 µVrms of noise at 80 µW {% include cite.html keys="harrison2003" %}.

## <span class="secnum">8.2</span>Pseudo-resistors

Diode-connected MOS-bipolar devices give teraohm small-signal resistance in a tiny area; their resistance depends strongly on voltage, temperature and leakage, so the high-pass corner moves.

## <span class="secnum">8.3</span>OTA design

Folded cascode versus current-scaled telescopic OTAs; putting most of the current into the input pair to approach the NEF limit of [Chapter 6]({% link chapters/06_noise.md %}); capacitive noise gain $$(C_1+C_2+C_\mathrm{in})/C_2$$.

## <span class="secnum">8.4</span>Gain, bandwidth and noise budget

Allocating the 1.5 µVrms EEG-mode noise target, choosing $$C_1$$ for the input impedance it presents ([Chapter 3]({% link chapters/03_electrodes.md %})), and switching bandwidth between modes.

## <span class="secnum">8.5</span>Linearity and pseudo-resistor problems

Distortion at large EMG and artefact amplitudes, leakage at high temperature, and tunable alternatives (bias-controlled pseudo-resistors, duty-cycled resistors).

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 4]({% link chapters/31_labs.md %}#lab-4) designs the capacitive-feedback LNA with pseudo-resistors in SG13G2: AC, noise and transient simulations and the NEF versus bias current.

</div>

**Read with this chapter.** Harrison and Charles {% include cite.html keys="harrison2003" %}, Yazicioglu, Van Hoof and Puers {% include cite.html keys="yazicioglubook" %}.
