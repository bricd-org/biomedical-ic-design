---
title: 15. Sample-and-Hold Circuits and Switches
parent: "Part III · Data Converters"
nav_order: 15
permalink: /part-3/ch15/
chapter: 15
---

# <span class="chapnum">Chapter 15</span>Sample-and-Hold Circuits and Switches

The sampling switch and capacitor set the noise floor of a SAR converter before a single comparison is made.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 4 (the rest of Part III with Labs 7, 8 and 10). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- derive $$kT/C$$ noise and the minimum sampling capacitance per bit;
- size a switch for settling within the acquisition time;
- reduce charge injection and clock feedthrough with bottom-plate sampling;
- design a bootstrapped switch for a 1.2 V supply;
- handle leakage at very low sample rates and multiplexer crosstalk.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How large must the sampling capacitor be, and how should the switch be built, for 12 bits at 1.2 V and a few kilosamples per second?

</div>

## <span class="secnum">15.1</span>$$kT/C$$ noise and capacitor size

The sampled thermal noise is independent of the switch resistance; the capacitance needed for $$N$$ bits grows as $$2^{2N}$$.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Sampled noise and minimum capacitance</div>

$$
v_{n,\mathrm{rms}} = \sqrt{kT/C} \quad\Rightarrow\quad C_{\min} \approx \frac{12\,kT\,2^{2N}}{V_{\mathrm{FS}}^2}
$$

</div>

## <span class="secnum">15.2</span>Settling and on-resistance

Exponential settling to half an LSB in the acquisition window; the on-resistance across the input range at a low supply.

## <span class="secnum">15.3</span>Charge injection and clock feedthrough

Signal-dependent errors from channel charge; bottom-plate sampling and dummy switches.

## <span class="secnum">15.4</span>Bootstrapped switches

Keeping $$V_\mathrm{GS}$$ constant to linearise the switch at 1.2 V; reliability limits in SG13G2.

## <span class="secnum">15.5</span>Leakage and multiplexing

At a few hundred samples per second the held charge leaks through off switches, a problem specific to biomedical ADCs; crosstalk between multiplexed channels.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 8]({% link chapters/31_labs.md %}#lab-8) builds a bootstrapped sample-and-hold as part of the SAR ADC.

</div>

**Read with this chapter.** Razavi {% include cite.html keys="razavi" %}, Pelgrom {% include cite.html keys="pelgrom" %}.
