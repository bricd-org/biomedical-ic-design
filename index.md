---
title: Home
layout: default
nav_order: 0
permalink: /
---

<div class="hero">
  <div class="hero-cover"><a href="{% link preface.md %}"><img src="{{ '/assets/images/cover.svg' | relative_url }}" alt="Cover of the Open-BioAFE Tutorial: Designing a Biopotential Acquisition Chip from Scratch"></a></div>
  <div class="hero-text">
    <p class="eyebrow">Open-BioAFE · IHP SG13G2 · 8-channel ExG front-end</p>
    <h1>Designing a Biopotential Acquisition Chip from Scratch</h1>
    <p class="fs-5">A design tutorial for undergraduate and early-graduate engineers building an open-source biomedical analog front-end and data converters in 130&nbsp;nm SiGe BiCMOS. Bioelectric signals, electrodes and safety, low-noise amplifiers, chopping, SAR and ΔΣ ADCs, bioimpedance sensing, biosignal processing, the open-source flow, and hands-on labs.</p>
    <p>
      <a class="btn btn-primary mr-2" href="{% link preface.md %}">Start reading</a>
      <a class="btn mr-2" href="{% link chapters/31_labs.md %}">Go to the labs</a>
      <a class="btn" href="https://github.com/bricd-org/biomedical-ic-design">Source on GitHub</a>
    </p>
  </div>
</div>

<div class="key-numbers">
  <div><b>8</b><span>channels: ECG, EEG or EMG</span></div>
  <div><b>0.5 Hz–1 kHz</b><span>ExG band (spikes to 7 kHz)</span></div>
  <div><b>&lt; 1.5 µVrms</b><span>input noise, 0.5–100 Hz</span></div>
  <div><b>&gt; 90 dB</b><span>CMRR at 50/60 Hz</span></div>
  <div><b>±300 mV</b><span>electrode offset tolerated</span></div>
  <div><b>12 b / 16 b</b><span>SAR / incremental ΔΣ</span></div>
  <div><b>&lt; 10 µW</b><span>front-end power per channel</span></div>
</div>

Every wearable ECG patch, EEG headset, prosthetic-control armband and neural implant needs a chip that turns microvolt biopotentials into clean numbers while the body picks up volts of mains interference and the battery allows a few microwatts per channel. This tutorial follows one design, the **Open-BioAFE** front-end in IHP's open SG13G2 PDK, from the signals and electrodes to a tape-out-ready architecture. Every concept follows the same pattern: a short derivation, a worked example with the project's real numbers, and a *what this means for your design* box. The numbers above are the design targets ([Table 1.2]({% link chapters/01_why.md %}#tab-1-2)).

<figure class="chain-figure">
  <img src="{{ '/assets/figs/signal-chain.svg' | relative_url }}" alt="The Open-BioAFE signal chain, from the electrodes to the data output">
  <figcaption>The Open-BioAFE signal chain and the chapters that design each block.</figcaption>
</figure>

## What is inside

<div class="card-grid">
  <div class="card"><span class="card-label">Part I · Ch 1–4 <span class="status status-written">written</span></span><h3><a href="{% link parts/part-1.md %}">Foundations</a></h3><p>Why biomedical ICs, bioelectric signals, electrodes and the body as a circuit, interference, safety and standards.</p></div>
  <div class="card"><span class="card-label">Part II · Ch 5–12 <span class="status status-outline">outline</span></span><h3><a href="{% link parts/part-2.md %}">The analog front-end</a></h3><p>Devices in weak inversion, noise and power, instrumentation amplifiers, the AC-coupled LNA, chopping, DC servo loops, filters and common-mode control.</p></div>
  <div class="card"><span class="card-label">Part III · Ch 13–22 <span class="status status-outline">outline</span></span><h3><a href="{% link parts/part-3.md %}">Data converters</a></h3><p>Sampling, specifications, switches, comparators, capacitive DACs, the SAR ADC, ΔΣ theory and circuits, and ADC testing.</p></div>
  <div class="card"><span class="card-label">Part IV · Ch 23–28 <span class="status status-outline">outline</span></span><h3><a href="{% link parts/part-4.md %}">Biosignal processing and systems</a></h3><p>DSP for biosignals, ECG, EEG and EMG processing on open datasets, on-chip features and bioimpedance sensing.</p></div>
  <div class="card"><span class="card-label">Part V · Ch 29–31 <span class="status status-outline">outline</span></span><h3><a href="{% link parts/part-5.md %}">Putting it together</a></h3><p>The full architecture and its budgets, the open-source flow to an IHP OpenMPW tape-out, and fifteen hands-on labs.</p></div>
</div>

## Hands-on labs

Fifteen labs in three tracks use only free tools: Python for signal and system models, Xschem and ngspice for SG13G2 circuits, and KLayout for layout. They are listed in [Chapter 31]({% link chapters/31_labs.md %}); the scripts live in [`labs/python/`](https://github.com/bricd-org/biomedical-ic-design/tree/main/labs/python).

## About

The tutorial is written for the Open-BioAFE project at [BRICD](https://www.thebricd.org) (Biomedical Research in Integrated Circuit Design). It builds on IHP's open SG13G2 PDK, JKU's IIC-OSIC-TOOLS and open data from PhysioNet and NinaPro. Every source is listed on the [References]({% link references.md %}) page.

**How this tutorial is made.** The Open-BioAFE Tutorial is being developed with the help of AI tools, and this draft may contain mistakes. If you spot one, please email [bricd.org@gmail.com](mailto:bricd.org@gmail.com) and we will correct it.

This is a living draft (v0.1, November 2026): Part I is written, and the other chapters are outlines that are being filled in. Corrections and contributions are welcome through [GitHub issues](https://github.com/bricd-org/biomedical-ic-design/issues).
