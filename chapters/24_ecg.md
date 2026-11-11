---
title: 24. ECG Processing
parent: "Part IV · Biosignal Processing and Systems"
nav_order: 24
permalink: /part-4/ch24/
chapter: 24
---

# <span class="chapnum">Chapter 24</span>ECG Processing

Detecting heartbeats is the oldest biomedical DSP problem, and the best way to see how ADC bits and amplifier noise reach a clinical result.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 5 (Part IV, including bioimpedance, with Labs 11–13 and 15). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- implement the Pan–Tompkins QRS detector;
- compute heart rate and heart-rate variability metrics;
- classify beats on the MIT-BIH Arrhythmia Database;
- test robustness with the MIT-BIH Noise Stress Test Database;
- show how ADC bits and AFE noise move detection sensitivity.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How many bits and how much input noise can the ECG chain afford before QRS detection degrades?

</div>

## <span class="secnum">24.1</span>Pan–Tompkins QRS detection

Band-pass, derivative, squaring, moving-window integration and adaptive thresholds {% include cite.html keys="pantompkins1985" %}.

## <span class="secnum">24.2</span>Heart rate and HRV

RR intervals, time-domain and frequency-domain HRV metrics.

## <span class="secnum">24.3</span>Beat classification

Features and simple classifiers on the MIT-BIH Arrhythmia Database {% include cite.html keys="mitbih" %}.

## <span class="secnum">24.4</span>Noise stress testing

Calibrated baseline wander, muscle and electrode-motion noise from the Noise Stress Test Database {% include cite.html keys="nstdb" %}.

## <span class="secnum">24.5</span>Co-design: bits and noise versus sensitivity

Sweeping the front-end parameters of a behavioural chain against detection sensitivity and positive predictivity.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 11]({% link chapters/31_labs.md %}#lab-11) passes MIT-BIH and Noise Stress Test records through a behavioural AFE and ADC and plots QRS sensitivity and PPV versus ADC bits and input noise.

</div>

**Read with this chapter.** Pan and Tompkins {% include cite.html keys="pantompkins1985" %}, Tompkins {% include cite.html keys="tompkins" %}, Moody and Mark {% include cite.html keys="mitbih" %}.
