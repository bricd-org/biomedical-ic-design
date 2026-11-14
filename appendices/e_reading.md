---
title: E. Further Reading
parent: Appendices
nav_order: 5
permalink: /appendix/e/
---

# <span class="chapnum">Appendix E</span>Further Reading

The books, papers, datasets and tools behind the tutorial, grouped by topic, with a word on what each is good for. The numbers are those of the [References]({% link references.md %}) page.
{: .chapterlead }

## <span class="secnum">E.1</span>Start here

Webster's *Medical Instrumentation* is the classic text on biopotentials, electrodes and instrumentation; Yazicioglu, Van Hoof and Puers treat biopotential readout circuits for portable systems in depth; Sarpeshkar covers ultra-low-power bioelectronics from devices to systems.

{% include reflist.html keys="webster,yazicioglubook,sarpeshkar,pallasareny" %}

## <span class="secnum">E.2</span>Signals and electrodes

The origin of biopotentials, from the action potential to extracellular fields, and the electrode interface as a circuit (Chapters 2 and 3).

{% include reflist.html keys="hodgkin1952,buzsaki2012,mcsharry2003,randles1947,chi2010" %}

## <span class="secnum">E.3</span>Interference, safety and standards

Mains coupling, the right-leg drive and the CMRR of real front-ends; shielding and guarding; and the IEC 60601 family, which the tutorial summarises but never reproduces (Chapters 4 and 12).

{% include reflist.html keys="huhta1973,winter1983,pallas1991,spinelli2003,rich1983,ott2009,medteqcmrr,medteqzin,iec60601-1,iec60601-2-25,iec60601-2-27,iec60601-2-47,kim2007" %}

## <span class="secnum">E.4</span>Low-noise amplifiers

The micropower instrumentation amplifier, the capacitive-feedback neural amplifier and the chopped readout ASIC that Part II builds on, and two analog design texts (Chapters 5–12).

{% include reflist.html keys="steyaert1987,harrison2003,yazicioglu2007,razavi,artofaicd" %}

## <span class="secnum">E.5</span>Data converters

Nyquist and oversampled converters, the survey of published converters, and open-source SAR designs and ΔΣ tools (Chapters 13–22).

{% include reflist.html keys="pelgrom,schreier,murmannsurvey,jkusar,twepp2024sar,pydeltasigma" %}

## <span class="secnum">E.6</span>Biosignal processing and systems

Digital processing of biosignals, the QRS detector of Chapter 24 and a seizure-detection SoC (Chapters 23–28).

{% include reflist.html keys="tompkins,pantompkins1985,verma2010" %}

## <span class="secnum">E.7</span>Open data

The recordings used by the labs, and the library that reads them.

{% include reflist.html keys="physionet,mitbih,nstdb,chbmit,ninapro,wfdb" %}

## <span class="secnum">E.8</span>Open-source silicon

The PDK, the tools, the chip template and the designs already taped out on IHP's open shuttles (Chapter 30).

{% include reflist.html keys="ihppdk,iicosic,jkutemplate,ihpdesignlib,ihpacademy,serdestut" %}

## <span class="secnum">E.9</span>How this tutorial is made

This tutorial, its figures and its lab code were developed with the help of AI tools, and this draft may contain mistakes. If you find an error, an unclear derivation or a figure that does not explain what it should, please email [bricd.org@gmail.com](mailto:bricd.org@gmail.com) or open an issue on [GitHub](https://github.com/bricd-org/biomedical-ic-design/issues), and we will correct it.
