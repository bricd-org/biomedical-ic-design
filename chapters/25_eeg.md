---
title: 25. EEG Processing and Brain–Computer Interfaces
parent: "Part IV · Biosignal Processing and Systems"
nav_order: 25
permalink: /part-4/ch25/
chapter: 25
---

# <span class="chapnum">Chapter 25</span>EEG Processing and Brain–Computer Interfaces

EEG carries information in rhythms and their changes; most of the processing estimates power in frequency bands.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 5 (Part IV, including bioimpedance, with Labs 11–13 and 15). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- compute band power and spectral features;
- remove EOG and EMG artefacts, including with ICA;
- detect seizure onset on the CHB-MIT database;
- explain the basics of SSVEP and motor-imagery BCIs.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which EEG features need which resolution and sample rate, and what does that save on chip?

</div>

## <span class="secnum">25.1</span>Band power and spectral features

Welch spectra, relative band power and spectral edge frequency for the $$\delta$$ to $$\gamma$$ bands of [Chapter 2]({% link chapters/02_signals.md %}).

## <span class="secnum">25.2</span>Artefact removal

Eye-blink and muscle artefacts; regression and independent component analysis.

## <span class="secnum">25.3</span>Seizure-onset detection

Patient-specific detectors on the CHB-MIT database {% include cite.html keys="chbmit" %} and the SoC of Verma et al. {% include cite.html keys="verma2010" %}.

## <span class="secnum">25.4</span>BCI basics

Steady-state visually evoked potentials and motor imagery.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 12]({% link chapters/31_labs.md %}#lab-12) computes band-power features on CHB-MIT, trains a simple classifier and repeats it with reduced word length and sample rate.

</div>

**Read with this chapter.** Shoeb {% include cite.html keys="chbmit" %}, Verma et al. {% include cite.html keys="verma2010" %}.
