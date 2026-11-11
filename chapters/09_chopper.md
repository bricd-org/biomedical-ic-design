---
title: 9. Chopper Stabilisation and Offset Cancellation
parent: "Part II · The Analog Front-End"
nav_order: 9
permalink: /part-2/ch09/
chapter: 9
---

# <span class="chapnum">Chapter 9</span>Chopper Stabilisation and Offset Cancellation

Chopping moves the signal above the flicker-noise corner, amplifies it there and brings it back, leaving the offset and $$1/f$$ noise behind.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 3 (Part II with Labs 3–5). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- explain chopping as modulation and demodulation in the frequency domain;
- predict the residual offset and the output ripple of a chopper amplifier;
- design a ripple-reduction loop;
- compare chopping, auto-zeroing and correlated double sampling;
- quantify the input-impedance cost of an input chopper.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How much offset, ripple and input-impedance loss does chopping leave behind, and how do you suppress each?

</div>

## <span class="secnum">9.1</span>The modulation view of chopping

Multiplying by a square wave at $$f_\mathrm{ch}$$ moves the signal to odd harmonics of $$f_\mathrm{ch}$$; the amplifier's offset and $$1/f$$ noise stay at baseband and are modulated away by the output chopper.

## <span class="secnum">9.2</span>Residual offset and ripple

Charge injection and clock feedthrough of the input switches create a residual offset; the up-modulated amplifier offset appears as a triangular ripple at the output.

## <span class="secnum">9.3</span>Ripple-reduction loops

Sensing the ripple after the output chopper and feeding a correction back; the 60 nV/$$\sqrt{\mathrm{Hz}}$$, 60 µW front-end of Yazicioglu et al. {% include cite.html keys="yazicioglu2007" %} as the reference design.

## <span class="secnum">9.4</span>Auto-zero and correlated double sampling

Sampling the offset and subtracting it; the noise folding that makes auto-zero noisier than chopping.

## <span class="secnum">9.5</span>Chopper spikes and input impedance

An input chopper in front of the input capacitors draws charge every cycle, so the input impedance falls to roughly $$1/(2 f_\mathrm{ch} C_\mathrm{in})$$; why this matters for dry electrodes and how impedance boosting ([Chapter 10]({% link chapters/10_dsl.md %})) recovers it.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 5]({% link chapters/31_labs.md %}#lab-5) adds input and output choppers and a DC servo loop to your LNA: $$1/f$$ removal, ripple, input-impedance loss and ±300 mV offset tolerance.

</div>

**Read with this chapter.** Yazicioglu et al. {% include cite.html keys="yazicioglu2007" %}, Yazicioglu, Van Hoof and Puers {% include cite.html keys="yazicioglubook" %}.
