---
title: 2. Bioelectric Signals
parent: "Part I · Foundations"
nav_order: 2
permalink: /part-1/ch02/
chapter: 2
---

# <span class="chapnum">Chapter 2</span>Bioelectric Signals

Biopotentials range from microvolts to millivolts and from below one hertz to several kilohertz; this chapter measures them so that every later budget starts from real numbers.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 1 (Part I with Labs 1 and 2). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- explain how an action potential arises, using the Hodgkin–Huxley model;
- describe the ECG waveform, its leads and Einthoven's triangle;
- name the EEG bands and the 10–20 electrode system;
- tell surface EMG from needle EMG, and spikes from local field potentials and ECoG;
- compute the dynamic range and bandwidth the front-end has to handle.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What dynamic range and bandwidth must the Open-BioAFE signal chain handle?

</div>

## <span class="secnum">2.1</span>Action potentials

The membrane at rest, ion channels and the Hodgkin–Huxley model {% include cite.html keys="hodgkin1952" %}: a rest potential near −65 mV, a peak near +39 mV and an after-hyperpolarisation.

## <span class="secnum">2.2</span>The electrocardiogram

The P wave, the QRS complex and the T wave; leads and Einthoven's triangle; a synthetic ECG model {% include cite.html keys="mcsharry2003" %} for the labs.

## <span class="secnum">2.3</span>The electroencephalogram

The δ (0.5–4 Hz), θ (4–8 Hz), α (8–13 Hz), β (13–30 Hz) and γ (30–100 Hz) bands, and electrode placement in the 10–20 system.

## <span class="secnum">2.4</span>The electromyogram

Motor units and their recruitment; surface versus needle EMG.

## <span class="secnum">2.5</span>Spikes, local field potentials and ECoG

What an intracortical electrode sees, and how these signals relate to the scalp EEG {% include cite.html keys="buzsaki2012" %}.

## <span class="secnum">2.6</span>Amplitude, bandwidth and dynamic range

The master amplitude-versus-bandwidth table (`SIGNALS` in `labs/python/biosig.py`). A DC-coupled channel that must accept ±300 mV of electrode offset above a 1.5 µVrms noise floor needs about 103 dB, or 16.8 bits, which is why ECG and EEG use the 16-bit ΔΣ converter. An AC-coupled 5 mV EMG signal needs about 67 dB, or 10.9 bits, which a 12-bit SAR provides.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 1]({% link chapters/31_labs.md %}#lab-1) loads ECG, EEG and EMG recordings from PhysioNet and NinaPro, plots their traces and spectra, and measures their amplitude and bandwidth.

</div>

**Read with this chapter.** Webster {% include cite.html keys="webster" %}, Buzsáki, Anastassiou and Koch {% include cite.html keys="buzsaki2012" %}.
