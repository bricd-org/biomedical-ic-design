---
title: 22. Testing and Characterising ADCs
parent: "Part III · Data Converters"
nav_order: 22
permalink: /part-3/ch22/
chapter: 22
---

# <span class="chapnum">Chapter 22</span>Testing and Characterising ADCs

A converter is only as good as the measurement that proves it.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 4 (the rest of Part III with Labs 7, 8 and 10). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- choose coherent sampling frequencies and windows for FFT tests;
- compute SNDR and SFDR from an FFT;
- measure DNL and INL with the sine-wave histogram and with static ramps;
- compare behavioural Verilog-A or Python models with transistor-level results;
- plan the measurements for a returned OpenMPW die.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do you prove, in simulation and on a returned die, that the Open-BioAFE converters meet their specifications?

</div>

## <span class="secnum">22.1</span>Coherent sampling and windowing

Choosing $$f_\mathrm{in} = (M/N)f_\mathrm{s}$$ with $$M$$ and $$N$$ co-prime; windows when coherence is impossible.

## <span class="secnum">22.2</span>FFT-based SNDR and SFDR

Bins, leakage, harmonics and the noise floor; the processing gain of a long FFT.

## <span class="secnum">22.3</span>Histogram and ramp tests

Code-density DNL and INL from a sine-wave histogram; static ramp tests for slow converters.

## <span class="secnum">22.4</span>Models versus transistors

Behavioural models for fast system simulation and their validation against transistor-level results.

## <span class="secnum">22.5</span>Testing a returned die

The bench set-up, the measurements that matter, and how to report them.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 6]({% link chapters/31_labs.md %}#lab-6) writes the `adctest.py` module used by Labs 8 and 10.

</div>

**Read with this chapter.** Pelgrom {% include cite.html keys="pelgrom" %}.
