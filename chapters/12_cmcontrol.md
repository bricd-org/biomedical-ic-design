---
title: 12. Common-Mode Control and Electrode Monitoring
parent: "Part II · The Analog Front-End"
nav_order: 12
permalink: /part-2/ch12/
chapter: 12
---

# <span class="chapnum">Chapter 12</span>Common-Mode Control and Electrode Monitoring

The third electrode is not a reference: it is the output of a feedback loop that pins the body to the amplifier's common mode.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 3 (Part II with Labs 3–5). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- design a right-leg drive (driven-right-leg) loop and analyse its stability;
- relate RLD loop gain to the residual common-mode and differential interference;
- implement common-mode feedback for the multichannel front-end;
- detect lead-off with DC and AC methods;
- protect the inputs against ESD and defibrillation pulses in SG13G2;
- filter RF before the first transistor without losing CMRR;
- drive cable shields and guards so the leads do not load the inputs.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How much right-leg-drive gain and which protection network let the Open-BioAFE channel pass the ECG CMRR test with margin?

</div>

## <span class="secnum">12.1</span>The right-leg drive loop

Sensing the average input common mode and driving it back into the body; the loop gain reduces the body common-mode voltage of [Chapter 4]({% link chapters/04_interference.md %}); stability with the electrode and body capacitances {% include cite.html keys="winter1983" %}. Safety when the loop saturates: a large transient drives the RLD amplifier to its rail, and the body then sees the rail through the RLD output resistance alone, so a series resistor must keep that current below the patient-current limits of [Chapter 4]({% link chapters/04_interference.md %}), while a high loop gain keeps the effective resistance to the body low in normal operation.

## <span class="secnum">12.2</span>Common-mode feedback

Setting the output common mode of the fully differential stages across eight channels.

## <span class="secnum">12.3</span>Lead-off detection

DC methods (small pull-up/pull-down currents) and AC methods (an excitation above the signal band); leakage-current limits from [Chapter 4]({% link chapters/04_interference.md %}); the full impedance measurement follows in [Chapter 28]({% link chapters/28_bioz.md %}).

## <span class="secnum">12.4</span>Input protection, ESD and RF filtering

Series resistors, clamps and their noise and leakage cost; defibrillation-proof inputs; the ESD devices available in SG13G2. RF rectification in the input pair and the RC filters that prevent it {% include cite.html keys="ott2009" %}: a mismatch between the two inputs' RC time constants turns common mode into differential mode, so the filter costs CMRR unless its parts match or a capacitor across the inputs dominates.

## <span class="secnum">12.5</span>Shielding, guarding and active electrodes {#shielding}

Cable shields tied to the reference at one end only; why a grounded shield's capacitance lowers $$Z_\mathrm{cm}$$ and with it the effective CMRR of [Chapter 4]({% link chapters/04_interference.md %}); driving the shield (or a guard trace around a high-impedance input on the board) at the input's own potential so no current flows through that capacitance {% include cite.html keys="rich1983" %}; a shield-drive output for the eight channels; active electrodes that buffer the signal at the skin, as dry and non-contact electrodes need {% include cite.html keys="chi2010" %}; twisted leads against magnetic pickup.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 2]({% link chapters/31_labs.md %}#lab-2) already adds a behavioural right-leg drive to the body model of [Chapter 4]({% link chapters/04_interference.md %}).

</div>

**Read with this chapter.** Winter and Webster {% include cite.html keys="winter1983" %}, Huhta and Webster {% include cite.html keys="huhta1973" %}, Webster {% include cite.html keys="webster" %}, Rich {% include cite.html keys="rich1983" %} (shielding and guarding), Ott {% include cite.html keys="ott2009" %} (RF rectification and filtering).
