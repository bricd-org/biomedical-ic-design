---
title: 1. Why Biomedical ICs?
parent: "Part I · Foundations"
nav_order: 1
permalink: /part-1/ch01/
chapter: 1
---

# <span class="chapnum">Chapter 1</span>Why Biomedical ICs?

Every biomedical front-end starts from an application: how many channels, which signal, how much noise, and how long the battery has to last.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 1 (Part I with Labs 1 and 2). The topics, the design question and the specification below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- name the main applications (wearable ECG patches, Holter monitors, EEG headsets, sEMG prosthetic control, neural implants and brain–computer interfaces) and what limits each one;
- explain why integration wins on channel count, power and size;
- draw the Open-BioAFE signal chain and say which chapter covers each block;
- read the Open-BioAFE specification sheet;
- estimate battery lifetime and data rate from a power and sampling budget.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What does each application demand in channels, noise, power and lifetime?

</div>

## <span class="secnum">1.1</span>Applications

Wearable ECG patches and Holter monitors, EEG headsets, surface EMG for prosthetic control, and neural implants and brain–computer interfaces, compared by channel count, signal and band, and what limits the design.

## <span class="secnum">1.2</span>Why integrate

Channel count, power and size. Commercial discrete front-ends are of the order of 1 mW per channel; an integrated front-end aims at microwatts.

## <span class="secnum">1.3</span>The signal chain

<figure id="fig-1-1" class="chain-figure">
  <img src="{{ '/assets/figs/signal-chain.svg' | relative_url }}" alt="The Open-BioAFE signal chain, from the electrodes to the data output">
  <figcaption><span class="capnum">Figure 1.1.</span> <strong>The Open-BioAFE signal chain.</strong> Electrodes and body, ESD protection and lead-off detection, the chopper LNA with its DC servo loop, the PGA and anti-alias filter, then one of two converters (Part III), decimation and feature extraction, and the data output. The right-leg drive feeds the common mode back to the body.</figcaption>
</figure>

## <span class="secnum">1.4</span>The Open-BioAFE specification

The targets below are still to be confirmed by the budgets of Parts II and III. The chip is built in IHP SG13G2, a 130 nm SiGe BiCMOS process with HBTs of roughly 350/450 GHz $$f_\mathrm{T}/f_\mathrm{max}$$, 1.2 V core and 3.3 V I/O MOS devices, and MIM capacitors {% include cite.html keys="ihppdk" %}. Its HBTs have low $$1/f$$ noise, but their base current flows through the electrode.

**Table 1.1. The Open-BioAFE specification.** Targets, and the chapters that set or meet each one.
{: .tabcaption #tab-1-1 }

| Parameter | Target | Chapters |
|---|---|---|
| Channels | 8, ECG, EEG or EMG selectable | 1 |
| Signal band | 0.5 Hz–1 kHz; spikes to 7 kHz optional | 2 |
| Input-referred noise | < 1.5 µVrms, 0.5–100 Hz (EEG mode) | 2, 3, 6 |
| CMRR | > 90 dB at 50/60 Hz | 4 |
| Electrode DC offset | ±300 mV tolerated | 3, 10 |
| Input impedance | ≥ 2.5 MΩ per input; common-mode goal > 1 GΩ at 50 Hz | 3, 4 |
| Converters | 12-bit SAR for EMG and spikes; 16-bit incremental ΔΣ for ECG and EEG | 13–20 |
| Front-end power | < 10 µW per channel | 6, 29 |
| Supply | 1.2 V | 5 |
| Process | IHP SG13G2 130 nm SiGe BiCMOS | 5, 30 |
| Bioimpedance | optional respiration channel | 28 |
| Data out | SPI | 27 |

## <span class="secnum">1.5</span>Battery life and data rate

How long a coin cell lasts at 10 µW, 100 µW and 1 mW per channel, and how many bits per second each mode produces. Even an efficient radio costs more than the whole front-end, which is why [Chapter 27]({% link chapters/27_soc.md %}) extracts features on chip.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Battery lifetime</div>

$$
T = \frac{E_\mathrm{batt}}{N P_\mathrm{ch} + P_\mathrm{dig} + P_\mathrm{radio}}
$$

</div>

**Read with this chapter.** Webster {% include cite.html keys="webster" %}, Sarpeshkar {% include cite.html keys="sarpeshkar" %}.
