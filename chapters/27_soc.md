---
title: 27. On-Chip Processing and System Integration
parent: "Part IV · Biosignal Processing and Systems"
nav_order: 27
permalink: /part-4/ch27/
chapter: 27
---

# <span class="chapnum">Chapter 27</span>On-Chip Processing and System Integration

On a wearable or implant, the radio usually costs more energy than the sensing; computing on chip is how you spend less of it.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 5 (Part IV, including bioimpedance, with Labs 11–13 and 15). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- place feature extraction and small machine-learning models in silicon;
- use the seizure-detection SoC of Verma et al. {% include cite.html keys="verma2010" %} as a case study;
- compress biosignal data before transmission;
- design power management with LDOs and energy harvesting;
- compare BLE, backscatter and inductive data links;
- introduce stimulation: current DACs and charge balance.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which processing belongs on the Open-BioAFE chip, and which data must leave it?

</div>

## <span class="secnum">27.1</span>Feature extraction and edge ML in silicon

Energy per operation versus energy per transmitted bit.

## <span class="secnum">27.2</span>Case study: an EEG seizure-detection SoC

Chopper IA, 12-bit SAR and feature processor on one die {% include cite.html keys="verma2010" %}.

## <span class="secnum">27.3</span>Compression

Lossless and lossy compression for ECG, EEG and spikes.

## <span class="secnum">27.4</span>Power management

LDOs, their noise and PSRR for microvolt front-ends; batteries and energy harvesting.

## <span class="secnum">27.5</span>Data links

BLE, backscatter and inductive links; energy per bit.

## <span class="secnum">27.6</span>Stimulation

Current-steering DACs, charge balance and electrode safety.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 12]({% link chapters/31_labs.md %}#lab-12) relates seizure-detection accuracy to bits and a power proxy.

</div>

**Read with this chapter.** Verma et al. {% include cite.html keys="verma2010" %}, Sarpeshkar {% include cite.html keys="sarpeshkar" %}.
