---
title: 18. The SAR ADC
parent: "Part III · Data Converters"
nav_order: 18
permalink: /part-3/ch18/
chapter: 18
---

# <span class="chapnum">Chapter 18</span>The SAR ADC

Binary search in silicon: the 12-bit asynchronous SAR is the converter for the multiplexed EMG and spike modes of Open-BioAFE.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 4 (the rest of Part III with Labs 7, 8 and 10). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- implement the binary search algorithm with a CDAC, a comparator and SAR logic;
- choose between synchronous and asynchronous timing;
- write the SAR logic in Verilog and synthesise or hand-build it;
- add redundancy with non-binary weights and calibrate digitally;
- power-gate and duty-cycle the converter between biosignal samples.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What SAR design reaches 12 bits at the lowest energy per conversion for eight multiplexed channels?

</div>

## <span class="secnum">18.1</span>The binary search algorithm

Sampling, $$N$$ comparison cycles and the DAC update; the timing of a conversion.

## <span class="secnum">18.2</span>Synchronous versus asynchronous timing

An external fast clock versus self-timed comparisons; why asynchronous SARs dominate low-power designs.

## <span class="secnum">18.3</span>SAR logic

Verilog for the successive-approximation register, synthesised with the open flow or built from custom cells.

## <span class="secnum">18.4</span>Redundancy and calibration

Non-binary weights tolerate DAC settling errors and decision errors; digital correction and calibration.

## <span class="secnum">18.5</span>Power gating and duty cycling

At a few kilosamples per second the converter idles most of the time; leakage then dominates.

## <span class="secnum">18.6</span>Case study: a 12-bit SAR in a seizure-detection SoC

The 1 V SAR inside the EEG acquisition SoC of Verma et al. {% include cite.html keys="verma2010" %}, read alongside the open SKY130 design of Moser and Pretl {% include cite.html keys="jkusar" %}.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 8]({% link chapters/31_labs.md %}#lab-8) integrates the S/H, the CDAC and Verilog SAR logic into a 10- to 12-bit SAR and measures its ENOB and FoM with `adctest.py`.

</div>

**Read with this chapter.** Verma et al. {% include cite.html keys="verma2010" %}, Moser and Pretl {% include cite.html keys="jkusar" %}, the TWEPP 2024 talk {% include cite.html keys="twepp2024sar" %}, the IHP Analog Academy {% include cite.html keys="ihpacademy" %}.
