---
title: 14. Specifications, Figures of Merit and Architecture Choice
parent: "Part III · Data Converters"
nav_order: 14
permalink: /part-3/ch14/
chapter: 14
---

# <span class="chapnum">Chapter 14</span>Specifications, Figures of Merit and Architecture Choice

A converter is described by a dozen numbers, but for a biosignal chip two of them, resolution and energy per conversion, decide the architecture.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 2 (the Python-only converter core: Chapters 13, 14 and 19 with Labs 6 and 9). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- define SNR, SNDR, SFDR, THD, ENOB, DNL, INL, offset and gain error and measure each;
- compute the Walden and Schreier figures of merit and know when each applies;
- place biomedical converters on the Murmann ADC survey;
- explain why thermal-noise-limited power grows $$\times 4$$ per bit and $$CV^2$$-limited power $$\times 2$$;
- choose between SAR, ΔΣ, incremental, VCO-based and event-driven converters for a given biosignal.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which converter architecture fits each Open-BioAFE mode, and what energy per conversion should you expect?

</div>

## <span class="secnum">14.1</span>Dynamic and static specifications

Spectral metrics from an FFT, and code-density metrics (DNL, INL) from a histogram; offset and gain error and why biomedical systems can often calibrate them away.

<div class="tbox tbox-keyeq" markdown="1">
<div class="tbox-title">Key equation · Walden and Schreier figures of merit</div>

$$
\mathrm{FoM_W} = \frac{P}{f_s\,2^{\mathrm{ENOB}}}, \qquad \mathrm{FoM_S} = \mathrm{SNDR} + 10\log_{10}\!\frac{f_s/2}{P}
$$

</div>

**Table 14.1. Converter architectures for biosignals.** The two converters built in this tutorial are the SAR and the incremental ΔΣ; the others appear in [Chapter 21]({% link chapters/21_bioadc.md %}) or only for contrast.
{: .tabcaption #tab-14-1 }

| Architecture | Typical bio use | Strength | Weakness |
|---|---|---|---|
| SAR | Multiplexed ExG, neural spikes, 8–12 b | Lowest energy per conversion, mostly digital, scales with technology | Needs an anti-alias filter and S/H; $$kT/C$$ and DAC matching limit the bits |
| ΔΣ (DT or CT) | ECG/EEG at 14–20 b | Relaxed anti-alias filter, high resolution, mismatch-tolerant with a 1-bit DAC | Decimation-filter power; continuous operation; idle tones |
| Incremental ΔΣ | Multiplexed high-resolution channels | ΔΣ accuracy with a reset per sample, multiplexer-friendly | Lower SQNR per OSR than a free-running ΔΣ |
| VCO / time-domain | Direct digitisation, tiny area | Mostly digital, inherent first-order shaping | VCO nonlinearity, supply sensitivity |
| Level-crossing / event-driven | Sparse signals (spikes, ECG) | Data and power scale with activity | Non-uniform samples, harder DSP |
| Pipeline / flash | Not used for ExG | Speed | Power far beyond biosignal needs; shown only for contrast |

## <span class="secnum">14.2</span>Figures of merit

Walden FoM for converters limited by energy per step, Schreier FoM for thermal-noise-limited designs; reading the survey data of Murmann {% include cite.html keys="murmannsurvey" %}.

## <span class="secnum">14.3</span>Power per bit

$$kT/C$$ sets the capacitor size and therefore the energy for high-resolution converters ($$\times 4$$ per extra bit); switching energy $$CV^2$$ dominates at low resolution ($$\times 2$$ per bit).

## <span class="secnum">14.4</span>Architecture choice for biosignals

The summary in [Table 14.1](#tab-14-1): SAR for multiplexed EMG and spikes, incremental ΔΣ for high-resolution ECG and EEG, and newer time-domain and event-driven options.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 6]({% link chapters/31_labs.md %}#lab-6) computes SNDR, SFDR and ENOB and histogram DNL/INL with injected capacitor mismatch.

</div>

**Read with this chapter.** Murmann {% include cite.html keys="murmannsurvey" %}, Pelgrom {% include cite.html keys="pelgrom" %}.
