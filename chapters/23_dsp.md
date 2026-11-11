---
title: 23. A DSP Toolkit for Biosignals
parent: "Part IV · Biosignal Processing and Systems"
nav_order: 23
permalink: /part-4/ch23/
chapter: 23
---

# <span class="chapnum">Chapter 23</span>A DSP Toolkit for Biosignals

Most of what a clinician sees has been filtered, decimated and cleaned after the ADC. The filters must not distort the waveform features they are meant to reveal.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 5 (Part IV, including bioimpedance, with Labs 11–13 and 15). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- choose sample rates for each biosignal;
- compare FIR and IIR filters and use zero-phase filtering;
- remove baseline wander and mains interference with adaptive and comb notch filters;
- use wavelets for denoising and feature extraction;
- predict fixed-point effects and choose word lengths.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which filters, at what word length, clean each biosignal without distorting it, and how much do they cost on chip?

</div>

## <span class="secnum">23.1</span>Sample-rate choices

Rates for diagnostic and monitoring ECG, EEG, EMG and spikes, and decimation between them.

## <span class="secnum">23.2</span>FIR, IIR and zero-phase filtering

Phase distortion of ST segments by causal IIR high-pass filters; forward–backward filtering offline.

## <span class="secnum">23.3</span>Baseline wander and mains interference

High-pass filtering versus spline and median baselines; adaptive notch and comb filters that track 50 Hz or 60 Hz and their harmonics.

## <span class="secnum">23.4</span>Wavelets

Multi-resolution decompositions for denoising and QRS detection.

## <span class="secnum">23.5</span>Fixed-point effects

Coefficient quantisation, limit cycles and word-length choices for on-chip filters.

**Read with this chapter.** Tompkins {% include cite.html keys="tompkins" %}.
