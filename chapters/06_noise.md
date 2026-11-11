---
title: 6. Noise and the Noise–Power Trade-off
parent: "Part II · The Analog Front-End"
nav_order: 6
permalink: /part-2/ch06/
chapter: 6
---

# <span class="chapnum">Chapter 6</span>Noise and the Noise–Power Trade-off

Every microvolt of noise you remove costs current. The noise efficiency factor tells you how close a design is to the physical limit.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 3 (Part II with Labs 3–5). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- compute thermal, flicker, shot and $$kT/C$$ noise and refer them to the amplifier input;
- integrate a noise spectrum over the signal band with the right noise bandwidth;
- derive the noise efficiency factor (NEF) and the power efficiency factor (PEF) and use them to compare designs;
- explain why a single bipolar or subthreshold device has $$\mathrm{NEF} \approx 1$$ and a differential pair about 2;
- set a current budget per channel from the 1.5 µVrms noise target.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

What is the minimum supply current that can meet the EEG-mode noise target, and how close to it can a real amplifier get?

</div>

## <span class="secnum">6.1</span>Noise sources

Thermal noise of resistors and channels, $$1/f$$ noise, shot noise of junction currents and $$kT/C$$ noise of sampled capacitors, with their spectral densities and the conditions where each dominates in a biopotential amplifier.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Noise efficiency factor</div>

$$
\mathrm{NEF} = V_\mathrm{ni,rms}\sqrt{\frac{2\,I_\mathrm{tot}}{\pi\, U_T\, 4kT\, \mathrm{BW}}}, \qquad \mathrm{PEF} = \mathrm{NEF}^2\,V_\mathrm{DD}
$$

</div>

## <span class="secnum">6.2</span>Input-referred noise and noise bandwidth

Referring output noise to the input; the equivalent noise bandwidth of first- and second-order roll-offs ($$\pi/2$$ and $$\pi/(2\sqrt2)$$ factors); integrating $$1/f$$ noise between a sub-hertz high-pass and the low-pass corner.

## <span class="secnum">6.3</span>Noise efficiency factor and power efficiency factor

$$\mathrm{NEF} = V_\mathrm{ni,rms}\sqrt{2 I_\mathrm{tot}/(\pi U_T\, 4kT\, \mathrm{BW})}$$, introduced by Steyaert and Sansen {% include cite.html keys="steyaert1987" %} and made the standard yardstick by Harrison and Charles {% include cite.html keys="harrison2003" %}; $$\mathrm{PEF} = \mathrm{NEF}^2V_\mathrm{DD}$$ adds the supply voltage. Published amplifiers plotted against both.

## <span class="secnum">6.4</span>The physical limit

Why a single BJT or weak-inversion MOSFET gives $$\mathrm{NEF} = 1$$, a differential pair $$\sqrt2$$ to 2, and current-reuse topologies below 2. What the limit means for the 10 µW per channel budget.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 4]({% link chapters/31_labs.md %}#lab-4) computes the NEF of your Harrison LNA versus bias current.

</div>

**Read with this chapter.** Steyaert and Sansen {% include cite.html keys="steyaert1987" %}, Harrison and Charles {% include cite.html keys="harrison2003" %}, Sarpeshkar {% include cite.html keys="sarpeshkar" %}, Razavi {% include cite.html keys="razavi" %} (Chapter on noise).
