---
title: 28. Bioimpedance Sensing and IQ Demodulation
parent: "Part IV · Biosignal Processing and Systems"
nav_order: 28
permalink: /part-4/ch28/
chapter: 28
---

# <span class="chapnum">Chapter 28</span>Bioimpedance Sensing and IQ Demodulation

Inject a small AC current, measure the voltage, and recover the complex impedance of tissue or of the electrode interface.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 5 (Part IV, including bioimpedance, with Labs 11–13 and 15). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- model tissue and electrodes with the Cole model and its dispersion;
- explain why a tetrapolar (four-electrode) measurement removes electrode impedance;
- design excitation sources: sine DAC with V-to-I converter, Howland and OTA-based current sources, square and pseudo-sine waves, multi-sine and chirp;
- implement IQ (quadrature) demodulation in the analog and digital domains and predict its errors;
- run ECG and impedance on the same electrodes by frequency separation;
- respect the frequency-dependent patient-current limits.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What excitation frequency, current and demodulator give the required $$\Delta Z$$ resolution within the safety limits?

</div>

## <span class="secnum">28.1</span>Applications

Respiration by impedance pneumography (reusing the ECG electrodes), impedance cardiography, body composition (BIA/BIS), electrical impedance tomography (EIT), electrodermal activity, electrode-contact quality and cell and tissue impedance spectroscopy.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · IQ demodulation</div>

$$
I = \tfrac{A}{2}\cos\varphi,\quad Q = \tfrac{A}{2}\sin\varphi \quad\Rightarrow\quad |Z| = \frac{2\sqrt{I^2+Q^2}}{I_{\mathrm{exc}}},\quad \varphi = \operatorname{atan2}(Q, I)
$$

</div>

## <span class="secnum">28.2</span>Tissue and electrode models

The Cole model and dispersion; bipolar versus tetrapolar measurement; the small $$\Delta Z$$ of respiration and heartbeat on top of a large baseline $$Z$$, which sets the dynamic range.

## <span class="secnum">28.3</span>Excitation

Sine DAC plus V-to-I converter, Howland and OTA-based current sources, square-wave and pseudo-sine excitation, multi-sine and chirp for spectroscopy; output impedance, common-mode control and the frequency-dependent patient-current limits of [Chapter 4]({% link chapters/04_interference.md %}).

## <span class="secnum">28.4</span>IQ demodulation

Mixing with in-phase and quadrature references, low-pass filtering, magnitude and phase; analog mixers versus chopper-style square-wave demodulators (and their odd-harmonic errors) versus digital IQ after the ADC; reference phase errors and I/Q mismatch; synchronous detection as a lock-in amplifier.

## <span class="secnum">28.5</span>Readout architecture

IA and baseline cancellation, ADC requirements for the IQ outputs, ECG and impedance on the same electrodes, and multi-frequency, multi-channel systems for EIT.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 15]({% link chapters/31_labs.md %}#lab-15) models Cole tissue in a tetrapolar set-up with digital IQ demodulation in Python, then builds an OTA current source and a square-wave IQ demodulator in SG13G2.

</div>

**Read with this chapter.** Webster {% include cite.html keys="webster" %}, Pallàs-Areny and Webster {% include cite.html keys="pallasareny" %}.
