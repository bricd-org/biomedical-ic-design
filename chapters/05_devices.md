---
title: 5. Devices for Microwatt Design
parent: "Part II · The Analog Front-End"
nav_order: 5
permalink: /part-2/ch05/
chapter: 5
---

# <span class="chapnum">Chapter 5</span>Devices for Microwatt Design

A biopotential amplifier lives on a few hundred nanoamperes per transistor, so its devices sit in weak or moderate inversion, where the square law no longer applies.
{: .chapterlead }

<div class="tbox tbox-specnote" markdown="1">
<div class="tbox-title">Chapter status: outline</div>

This chapter is an outline. It will be written in build stage 3 (Part II with Labs 3–5). The topics, the design question and the labs below are fixed; the derivations, worked examples and figures are still to come.

</div>

<div class="tbox tbox-objectives" markdown="1">
<div class="tbox-title">In this chapter you will learn</div>

- place a MOSFET in weak, moderate or strong inversion from its inversion coefficient and read its $$g_\mathrm{m}/I_\mathrm{D}$$;
- explain why $$g_\mathrm{m}/I_\mathrm{D}$$ peaks at about $$1/(n U_T)$$ in weak inversion and what that means for noise per microampere;
- relate flicker noise to gate area and pick input-pair dimensions for a sub-100 Hz band;
- compare SG13G2 MOSFETs and SiGe HBTs as low-noise input devices (thermal noise, flicker noise, base current);
- estimate offset and gain mismatch from Pelgrom coefficients.

</div>

<div class="tbox tbox-insight" markdown="1">
<div class="tbox-title">Design question</div>

Which device, at what inversion level and size, gives the lowest input-referred noise for a microwatt bias current?

</div>

## <span class="secnum">5.1</span>Weak, moderate and strong inversion

The inversion coefficient $$IC = I_\mathrm{D}/I_\mathrm{spec}$$ places a transistor on one continuous curve from exponential (weak inversion) to square-law (strong inversion) behaviour. Biomedical front-ends bias their input pairs at $$IC \lesssim 1$$.

## <span class="secnum">5.2</span>The $$g_\mathrm{m}/I_\mathrm{D}$$ method at microwatt bias

Sizing from $$g_\mathrm{m}/I_\mathrm{D}$$ lookup tables instead of hand equations; the weak-inversion limit $$g_\mathrm{m}/I_\mathrm{D} \approx 1/(nU_T) \approx 25\ \text{V⁻¹}$$; why it saturates and what it costs in area and speed. This chapter cross-links *The Art of Analog IC Design* {% include cite.html keys="artofaicd" %} rather than repeating it.

## <span class="secnum">5.3</span>Flicker noise and device area

$$1/f$$ noise scales as $$1/(WL)$$, so the low corner of an EEG band forces large input devices; PMOS versus NMOS in SG13G2; the corner frequency and its dependence on bias.

## <span class="secnum">5.4</span>MOSFET versus SiGe HBT input pairs

An HBT reaches $$g_\mathrm{m} = I_\mathrm{C}/U_T$$ at any current and has very low $$1/f$$ noise, but its base current flows through the electrode impedance and adds shot noise. The trade-off decides the input stage of the Open-BioAFE LNA.

## <span class="secnum">5.5</span>Matching

Pelgrom's law $$\sigma(\Delta V_\mathrm{T}) = A_{V_T}/\sqrt{WL}$$, current-mirror and capacitor matching, and why large, slow biomedical devices match well but still need chopping for microvolt offsets.

<div class="tbox tbox-tryit" markdown="1">
<div class="tbox-title">Labs for this chapter</div>

[Lab 3]({% link chapters/31_labs.md %}#lab-3) characterises $$g_\mathrm{m}/I_\mathrm{D}$$, flicker noise versus $$W\!\cdot\!L$$ and HBT versus MOS input noise in SG13G2; its lookup tables are reused in Labs 4 and 5.

</div>

**Read with this chapter.** Sarpeshkar {% include cite.html keys="sarpeshkar" %} (subthreshold design, noise–power limits), Razavi {% include cite.html keys="razavi" %} (device noise), *The Art of Analog IC Design* {% include cite.html keys="artofaicd" %} (Part II: the transistor and $$g_\mathrm{m}/I_\mathrm{D}$$).
