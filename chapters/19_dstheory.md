---
title: "19. ΔΣ Modulation: Theory"
parent: "Part III · Data Converters"
nav_order: 19
permalink: /part-3/ch19/
chapter: 19
---

# <span class="chapnum">Chapter 19</span>ΔΣ Modulation: Theory

Oversample, quantise coarsely and push the quantisation noise out of the band: noise shaping turns a 1-bit quantiser into a 16-bit converter.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 2 (the Python-only converter core: Chapters 13, 14 and 19 with Labs 6 and 9). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- derive the noise transfer function (NTF) and signal transfer function (STF) of first- and second-order loops;
- predict SQNR from loop order and oversampling ratio (OSR);
- check stability with the Lee criterion and understand idle tones and dither;
- synthesise and realise an NTF with `synthesizeNTF` and `realizeNTF`;
- know when linearised analysis fails and simulation is needed.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which loop order and OSR give 16 bits in the ECG/EEG band at the lowest clock rate?

</div>

## <span class="secnum">19.1</span>Noise shaping

The linear model of a ΔΣ loop; $$\mathrm{NTF}(z) = (1-z^{-1})^L$$ and its high-pass shape.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Peak SQNR of an order-\(L\) modulator</div>

$$
\mathrm{SQNR}_{L} \approx 6.02N + 1.76 - 10\log_{10}\!\frac{\pi^{2L}}{2L+1} + (20L+10)\log_{10}\mathrm{OSR}\ \mathrm{dB}
$$

</div>

## <span class="secnum">19.2</span>SQNR versus order and OSR

Each doubling of OSR buys $$6L + 3$$ dB; diminishing returns and the trade-off with stability.

## <span class="secnum">19.3</span>Stability, idle tones and dither

The Lee criterion $$\lVert \mathrm{NTF}\rVert_\infty < 1.5$$ for 1-bit loops; tones with DC inputs, which matter for ECG baselines.

## <span class="secnum">19.4</span>NTF synthesis

Using python-deltasigma {% include cite.html keys="pydeltasigma" %}, the Python port of Schreier's toolbox {% include cite.html keys="schreier" %}, to place zeros and poles and map them to a loop topology.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 9]({% link chapters/31_labs.md %}#lab-9) synthesises first- to third-order NTFs, simulates SQNR versus OSR and the incremental mode, and designs a fixed-point CIC decimator.

</div>

**Read with this chapter.** Schreier, Temes and Pavan {% include cite.html keys="schreier" %}, python-deltasigma {% include cite.html keys="pydeltasigma" %}.
