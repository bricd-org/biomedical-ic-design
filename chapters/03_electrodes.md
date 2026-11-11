---
title: 3. Electrodes and the Body as a Circuit
parent: "Part I · Foundations"
nav_order: 3
permalink: /part-1/ch03/
chapter: 3
---

# <span class="chapnum">Chapter 3</span>Electrodes and the Body as a Circuit

The electrode is the first component of the circuit: before the amplifier sees anything, it adds an offset of hundreds of millivolts, a frequency-dependent impedance and its own noise.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 1 (Part I with Labs 1 and 2). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- compare wet Ag/AgCl, dry and implanted electrodes;
- explain half-cell potentials and the DC offset they leave between two electrodes;
- model the electrode–skin interface with the Randles circuit;
- compute the thermal noise of an electrode;
- derive the input impedance the amplifier needs.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What input impedance, offset tolerance and noise floor does the electrode force on the amplifier?

</div>

## <span class="secnum">3.1</span>Electrode types

Wet Ag/AgCl, dry {% include cite.html keys="chi2010" %} and implanted electrodes, and what each costs in impedance and noise.

## <span class="secnum">3.2</span>Half-cell potential and DC offset

Each electrode has a half-cell potential (about +0.222 V versus the standard hydrogen electrode for Ag/AgCl). Two electrodes never match, so the front-end has to tolerate ±300 mV of DC offset.

## <span class="secnum">3.3</span>The electrode–skin model

The Randles circuit {% include cite.html keys="randles1947" %} and the models in `labs/python/biosig.py`: wet, 1 kΩ in series with 51 kΩ‖47 nF; dry, 5 kΩ in series with 1 MΩ‖4.7 nF; implanted micro-electrode, 10 kΩ in series with a constant-phase element.

## <span class="secnum">3.4</span>Electrode noise

The thermal noise of the real part of the electrode impedance, from 0.5 to 100 Hz at body temperature: about 0.24 µVrms for a wet electrode and 0.85 µVrms for a dry one. Real electrodes add excess noise on top.

## <span class="secnum">3.5</span>Motion artefacts and impedance mismatch

Why the electrode potential moves when the skin stretches, and why the two electrodes of a pair never have the same impedance.

## <span class="secnum">3.6</span>Input impedance

The ECG standards test the input with a 620 kΩ‖4.7 nF source and allow at most a 20 % signal drop {% include cite.html keys="medteqzin,iec60601-2-25" %}, which gives the 2.5 MΩ minimum input impedance.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 2]({% link chapters/31_labs.md %}#lab-2) builds the body and electrode model, adds an impedance imbalance and finds the CMRR and input impedance the amplifier needs.

</div>

**Read with this chapter.** Webster {% include cite.html keys="webster" %}, Chi et al. {% include cite.html keys="chi2010" %}.
