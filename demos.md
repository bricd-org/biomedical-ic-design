---
title: "Interactive Demos"
layout: default
nav_order: 1.5
permalink: /demos/
---

# Interactive demos

Seventeen interactive demos turn the hard ideas of the tutorial into things you can move. Each one runs in the page, with no install, and reproduces the numbers its chapter quotes at its default settings. Every demo ends with **three things to try**, each with the result you should see, and a **check-yourself question** that tells you why each answer is right or wrong.
{: .fs-5 .fw-300 }

## Part I · Foundations

- **Chapter 4** · [Mains interference at the electrodes]({% link chapters/04_interference.md %}#bdMains): how electrode imbalance and common-mode input impedance turn the body's mains pickup into a differential signal.

## Part II · The Analog Front-End

- **Chapter 6** · [Noise, current and NEF]({% link chapters/06_noise.md %}#bdNef): what an amplifier's current buys in noise, and the noise-efficiency factor that compares designs.
- **Chapter 8** · [The Harrison LNA's frequency response]({% link chapters/08_lna.md %}#bdLna): gain, band edges and noise of the capacitive-feedback LNA as you size its capacitors and OTA.
- **Chapter 9** · [Chopping, 1/f noise and offset]({% link chapters/09_chopper.md %}#bdChop): what chopping does to flicker noise and offset, and the ripple it leaves behind.
- **Chapter 11** · [Anti-alias filter order against aliasing]({% link chapters/11_filters.md %}#bdAaf): which filter order keeps interference from folding into the band at a given sample rate.

## Part III · Data Converters

- **Chapter 13** · [Sampling and quantisation]({% link chapters/13_sampling.md %}#bdSmp): aliasing, quantisation noise and the bits a signal needs.
- **Chapter 18** · [One SAR conversion, binary or redundant]({% link chapters/18_sar.md %}#sard): the binary search step by step, and how redundancy rescues noisy fast decisions.
- **Chapter 19** · [ΔΣ noise shaping, simulated live]({% link chapters/19_dstheory.md %}#bdDsm): a delta-sigma modulator's spectrum as you change order, oversampling ratio and input.
- **Chapter 20** · [Resolution of an incremental ΔΣ converter]({% link chapters/20_dscircuits.md %}#bdIncr): how many clock cycles per sample a reset delta-sigma needs for 16 bits.
- **Chapter 22** · [Coherent sampling and window leakage]({% link chapters/22_adctest.md %}#bdFft): why an ADC test tone must fit the FFT record, and what windows do when it does not.

## Part IV · Biosignal Processing and Systems

- **Chapter 24** · [The Pan–Tompkins QRS detector, stage by stage]({% link chapters/24_ecg.md %}#bdPt): how a heartbeat detector works, and how few ADC bits it needs.
- **Chapter 27** · [Sizing a Bluetooth Low Energy link]({% link chapters/27_soc.md %}#bdBle): throughput and radio power for each Open-BioAFE data stream.
- **Chapter 28** · [Tissue impedance and its measurement]({% link chapters/28_bioz.md %}#bdCole): the Cole model of tissue and how a bioimpedance channel measures it.

## Part V · Putting It Together

- **Chapter 29** · [The channel's noise and power budgets]({% link chapters/29_arch.md %}#bdBud): where the noise and the microwatts of one Open-BioAFE channel go.

## Part VI · Wearable Systems

- **Chapter 31** · [Adaptive cancellation of a motion artefact]({% link chapters/31_quality.md %}#bdNlms): an NLMS filter removing a walking artefact with accelerometer and impedance references.
- **Chapter 32** · [Signal-to-noise ratio of an ear-EEG channel]({% link chapters/32_ear.md %}#bdEar): electrodes, reference and amplifier noise against a brain rhythm at the ear.
- **Chapter 33** · [Timing stimuli to the phase of a brain rhythm]({% link chapters/33_closedloop.md %}#bdPh): how filter delay and jitter decide whether a closed loop hits the phase it aims for.
