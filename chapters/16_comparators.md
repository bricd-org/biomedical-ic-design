---
title: 16. Comparators
parent: "Part III · Data Converters"
nav_order: 16
permalink: /part-3/ch16/
chapter: 16
---

# <span class="chapnum">Chapter 16</span>Comparators

A SAR converter makes one comparator decision per bit; its offset, noise and energy set much of the converter's performance.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 4 (the rest of Part III with Labs 7, 8 and 10). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- compare static preamplifier-plus-latch, dynamic StrongARM and double-tail comparators;
- predict offset from Pelgrom coefficients and calibrate it;
- measure input-referred noise with transient-noise simulation;
- control kickback and metastability;
- estimate energy per decision.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which comparator gives 12-bit decisions at the lowest energy, and how do you verify its offset and noise?

</div>

## <span class="secnum">16.1</span>Comparator architectures

Static preamplifier and latch versus the dynamic StrongARM latch and the double-tail comparator for low supplies.

## <span class="secnum">16.2</span>Offset and calibration

Monte Carlo offset from input-pair mismatch; foreground and background calibration.

## <span class="secnum">16.3</span>Noise

Input-referred noise of a regenerative latch and how to extract it from the probability of a '1' versus input voltage in transient-noise simulation.

## <span class="secnum">16.4</span>Kickback and metastability

Charge kicked back onto the DAC; decisions on tiny inputs that take too long, and what they cost an asynchronous SAR.

## <span class="secnum">16.5</span>Energy per decision

Switching energy of the latch and its clocking; how it scales with supply and speed.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 7]({% link chapters/31_labs.md %}#lab-7) designs a StrongARM comparator in SG13G2: Monte Carlo offset, transient-noise input-referred noise and energy per decision.

</div>

**Read with this chapter.** Razavi {% include cite.html keys="razavi" %}, the IHP Analog Academy {% include cite.html keys="ihpacademy" %} (the dynamic comparator module).
