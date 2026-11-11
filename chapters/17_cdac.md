---
title: 17. Capacitive DACs and References
parent: "Part III · Data Converters"
nav_order: 17
permalink: /part-3/ch17/
chapter: 17
---

# <span class="chapnum">Chapter 17</span>Capacitive DACs and References

The capacitive DAC is both the sample-and-hold and the reference ladder of a SAR converter; its matching sets the linearity.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 4 (the rest of Part III with Labs 7, 8 and 10). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- compare binary-weighted, split (bridge) and C-2C capacitor arrays;
- compute the switching energy of the conventional, monotonic, $$V_\mathrm{cm}$$-based and merged-capacitor schemes;
- size the unit capacitor from matching and from $$kT/C$$;
- choose between MOM and MIM capacitors in SG13G2 and lay them out in common centroid;
- design reference buffering and decoupling.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How small can the unit capacitor be for 12-bit linearity, and which switching scheme minimises the DAC energy?

</div>

## <span class="secnum">17.1</span>Capacitor array topologies

Binary arrays, split arrays with a bridge capacitor, and C-2C ladders: area, linearity and parasitic sensitivity.

## <span class="secnum">17.2</span>Switching schemes and energy

Conventional, monotonic, $$V_\mathrm{cm}$$-based and merged-capacitor switching; the average energy per conversion of each.

## <span class="secnum">17.3</span>Unit-capacitor sizing

Matching-limited versus $$kT/C$$-limited size; why matching usually wins for SAR converters above 10 bits.

## <span class="secnum">17.4</span>Capacitors in SG13G2

MOM and MIM options, their density and matching, and common-centroid layout of the array.

## <span class="secnum">17.5</span>References

The DAC draws charge from the reference every bit cycle; on-chip buffers versus large decoupling capacitors.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 8]({% link chapters/31_labs.md %}#lab-8) builds a CDAC with monotonic switching; [Lab 14]({% link chapters/31_labs.md %}#lab-14) lays it out.

</div>

**Read with this chapter.** Pelgrom {% include cite.html keys="pelgrom" %}, Moser and Pretl {% include cite.html keys="jkusar" %} (an open non-binary 12-bit CDAC).
