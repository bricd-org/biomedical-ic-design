---
title: 29. The Full Architecture and Its Budgets
parent: "Part V · Putting It Together"
nav_order: 29
permalink: /part-5/ch29/
chapter: 29
---

# <span class="chapnum">Chapter 29</span>The Full Architecture and Its Budgets

Every chapter so far has answered one budget question. This chapter puts the answers together on one chip.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 6 (Part V, Lab 14, the capstone and the appendices). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- assemble the noise, CMRR, power, area and data-rate budgets of Open-BioAFE;
- choose SAR or ΔΣ per mode;
- add the optional bioimpedance channel;
- draw the top-level floorplan.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Does the assembled Open-BioAFE chip meet every number of its specification ([Table 1.1]({% link chapters/01_why.md %}#tab-1-1)), and where is the margin?

</div>

## <span class="secnum">29.1</span>Noise budget

From electrode noise ([Chapter 3]({% link chapters/03_electrodes.md %})) through the LNA, PGA and ADC to the 1.5 µVrms EEG target.

## <span class="secnum">29.2</span>CMRR budget

Electrode imbalance, amplifier mismatch and right-leg drive against the 90 dB target.

## <span class="secnum">29.3</span>Power, area and data rate

The 10 µW per channel front-end budget, converter energy, and the output data rate per mode.

## <span class="secnum">29.4</span>SAR or ΔΣ per mode

The routing of [Figure 1.1]({% link chapters/01_why.md %}#fig-1-1) justified by the budgets.

## <span class="secnum">29.5</span>The bioimpedance channel

The optional respiration channel of [Chapter 28]({% link chapters/28_bioz.md %}).

## <span class="secnum">29.6</span>Floorplan

Placing eight channels, two converters, references and the digital back end.

**Read with this chapter.** Verma et al. {% include cite.html keys="verma2010" %}, Yazicioglu, Van Hoof and Puers {% include cite.html keys="yazicioglubook" %}.
