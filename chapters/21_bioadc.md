---
title: 21. Biomedical Converter Innovations
parent: "Part III · Data Converters"
nav_order: 21
permalink: /part-3/ch21/
chapter: 21
---

# <span class="chapnum">Chapter 21</span>Biomedical Converter Innovations

In recent designs the boundary between the amplifier and the converter is dissolving.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 4 (the rest of Part III with Labs 7, 8 and 10). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- explain direct digitisation with ΔΣ front-ends that take the electrode as input;
- design for the large input range that motion artefacts require;
- describe VCO- and time-based ADCs;
- compare level-crossing and event-driven sampling with uniform sampling;
- assess compressive sensing for biosignals.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

When does it pay to merge the amplifier and the ADC, and when to sample only on events?

</div>

## <span class="secnum">21.1</span>Direct digitisation

ΔΣ loops that close around the electrode, removing the LNA and gaining dynamic range against artefacts.

## <span class="secnum">21.2</span>VCO- and time-domain ADCs

Voltage-controlled oscillators as integrating quantisers with first-order shaping; nonlinearity and supply sensitivity.

## <span class="secnum">21.3</span>Level-crossing and event-driven sampling

Data and power that scale with activity for sparse spikes and ECG.

## <span class="secnum">21.4</span>Compressive sensing

Random projections of sparse signals; what it saves in the radio and costs in reconstruction.

## <span class="secnum">21.5</span>The dissolving AFE/ADC boundary

Reading recent ISSCC designs with the budgets of this tutorial.

**Read with this chapter.** Murmann {% include cite.html keys="murmannsurvey" %}.
