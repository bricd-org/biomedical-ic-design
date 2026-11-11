---
title: 30. Open-Source Design and Verification Flow
parent: "Part V · Putting It Together"
nav_order: 30
permalink: /part-5/ch30/
chapter: 30
---

# <span class="chapnum">Chapter 30</span>Open-Source Design and Verification Flow

Every circuit in this tutorial can be designed, verified and taped out with free tools and an open PDK.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 6 (Part V, Lab 14, the capstone and the appendices). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- set up IIC-OSIC-TOOLS with Xschem, ngspice/Xyce and KLayout;
- write and simulate SAR logic in Verilog with mixed-signal co-simulation;
- run corners and Monte Carlo;
- run DRC, LVS and parasitic extraction in KLayout;
- use the JKU AMS chip template and submit to an IHP OpenMPW shuttle.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

How do you take an Open-BioAFE block from schematic to a verified GDS that IHP will accept?

</div>

## <span class="secnum">30.1</span>The tool set

IIC-OSIC-TOOLS {% include cite.html keys="iicosic" %}: Xschem, ngspice, Xyce, KLayout, Verilator and Icarus Verilog in one container, with the IHP-Open-PDK {% include cite.html keys="ihppdk" %}.

## <span class="secnum">30.2</span>Schematic and simulation

Xschem testbenches; ngspice and Xyce for AC, noise, transient and transient-noise analyses.

## <span class="secnum">30.3</span>Mixed-signal co-simulation

Verilog SAR logic with the analog CDAC and comparator.

## <span class="secnum">30.4</span>Corners and Monte Carlo

Process, voltage and temperature corners; mismatch; what a biomedical chip must survive.

## <span class="secnum">30.5</span>Layout and verification

KLayout DRC, LVS and PEX; post-layout simulation.

## <span class="secnum">30.6</span>From template to tape-out

The JKU ihp-sg13g2-ams-chip-template {% include cite.html keys="jkutemplate" %} with its padframe, and the IHP OpenMPW route documented in IHP-Open-DesignLib {% include cite.html keys="ihpdesignlib" %}.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 14]({% link chapters/31_labs.md %}#lab-14) lays out the comparator and CDAC, runs DRC, LVS and PEX with the JKU template and compares post-layout with schematic simulation.

</div>

**Read with this chapter.** Dorrer and Pretl {% include cite.html keys="jkutemplate" %}, IIC-OSIC-TOOLS {% include cite.html keys="iicosic" %}, IHP-Open-DesignLib {% include cite.html keys="ihpdesignlib" %}.
