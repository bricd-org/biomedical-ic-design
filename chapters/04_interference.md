---
title: 4. Interference, Safety and Standards
parent: "Part I · Foundations"
nav_order: 4
permalink: /part-1/ch04/
chapter: 4
---

# <span class="chapnum">Chapter 4</span>Interference, Safety and Standards

The patient sits in the mains field, so the front-end has to reject volts of common-mode interference while it amplifies microvolts, and it must never hurt the patient.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 1 (Part I with Labs 1 and 2). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- model how the mains couples to the body;
- compute how electrode impedance imbalance turns common-mode interference into a differential signal;
- read the CMRR test of the ECG standards and derive the CMRR it implies;
- summarise patient leakage-current limits, isolation, defibrillation and ESD;
- state the heating limits for implants.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How much CMRR and common-mode input impedance does Open-BioAFE need, and which safety limits bound the design?

</div>

## <span class="secnum">4.1</span>Mains coupling

The body couples to the mains through a few picofarads and to earth through a few hundred {% include cite.html keys="huhta1973" %}. With 3 pF and 200 pF at 230 V, 50 Hz, about 0.22 µA flows through the body; a floating body sits at about 3.4 V, and a ground electrode brings it down to millivolts.

## <span class="secnum">4.2</span>From common mode to differential mode

An imbalance between the two electrode impedances turns part of the common-mode voltage into a differential signal {% include cite.html keys="pallas1991" %}, so the common-mode input impedance matters as much as the amplifier's own CMRR.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Effective CMRR with electrode imbalance</div>

$$
\frac{1}{\mathrm{CMRR}_\mathrm{eff}} = \frac{1}{\mathrm{CMRR}_\mathrm{amp}} + \frac{\Delta Z}{Z_\mathrm{cm}}
$$

</div>

## <span class="secnum">4.3</span>The CMRR test of the ECG standards

10 Vrms of common mode, a 51 kΩ‖47 nF imbalance in one lead and 300 mV of DC offset, with less than 1 mV allowed at the output {% include cite.html keys="medteqcmrr,iec60601-2-25,iec60601-2-27" %}. This implies about 89 dB; Open-BioAFE targets more than 90 dB.

## <span class="secnum">4.4</span>Patient safety

Patient leakage-current limits for type BF and CF applied parts, in normal condition and with a single fault {% include cite.html keys="iec60601-1" %}. Standards are summarised here, never reproduced: always work from the edition that applies to your device.

## <span class="secnum">4.5</span>Isolation, defibrillation and ESD

Isolating the patient from the mains, surviving a defibrillator pulse and recovering quickly, and protecting the pins against electrostatic discharge.

## <span class="secnum">4.6</span>Implants

Keeping the tissue temperature rise to about 1 °C and the power density within safe limits {% include cite.html keys="kim2007" %}.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 2]({% link chapters/31_labs.md %}#lab-2) injects 10 Vrms of mains common mode into the body model, sweeps CMRR, common-mode impedance and imbalance, and adds a right-leg drive.

</div>

**Read with this chapter.** Pallàs-Areny and Webster {% include cite.html keys="pallasareny" %}, Webster {% include cite.html keys="webster" %}.
