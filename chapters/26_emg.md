---
title: 26. EMG and Neural Spike Processing
parent: "Part IV · Biosignal Processing and Systems"
nav_order: 26
permalink: /part-4/ch26/
chapter: 26
---

# <span class="chapnum">Chapter 26</span>EMG and Neural Spike Processing

Muscle signals are read through their envelope; neural signals through the timing of individual spikes.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 5 (Part IV, including bioimpedance, with Labs 11–13 and 15). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- compute EMG envelopes and the time-domain features MAV, WL, ZC and SSC;
- classify hand gestures on NinaPro;
- detect neural spikes with the nonlinear energy operator (NEO);
- explain spike sorting and why implants compress before transmitting.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How much resolution, sample rate and channel count does gesture recognition or spike detection actually need?

</div>

## <span class="secnum">26.1</span>EMG envelopes and features

Rectification and smoothing; mean absolute value, waveform length, zero crossings and slope-sign changes.

## <span class="secnum">26.2</span>Gesture classification

LDA and SVM classifiers on the NinaPro database {% include cite.html keys="ninapro" %}.

## <span class="secnum">26.3</span>Spike detection

Thresholds and the NEO; detection versus the noise of [Chapter 6]({% link chapters/06_noise.md %}).

## <span class="secnum">26.4</span>Spike sorting and compression

Clustering waveforms; why a thousand-channel implant must send spikes, not samples.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 13]({% link chapters/31_labs.md %}#lab-13) computes MAV, WL, ZC and SSC on NinaPro, classifies with LDA or SVM and repeats with fixed-point features.

</div>

**Read with this chapter.** Atzori et al. {% include cite.html keys="ninapro" %}.
