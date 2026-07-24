---
title: "Twenty-five badges in six weeks: the ZERODAY build log"
slug: zeroday-badge-build-log
date: 2026-08-11
designator: H3
series: hardware
summary: "Schematic to assembled hardware for a run of Pico W conference badges — the part choices, the BOM mistake that cost a week, and what I would do differently on the next revision."
draft: true
tags: [pcb, easyeda, jlcpcb, hardware]
---

<!-- DRAFT OUTLINE — do not publish until the employer review in the README is signed off. -->

## What the badge had to do

- Run standalone for a full day on battery
- Support a multiplayer game across the room without pairing
- Be repairable on a folding table with one iron

## Design

- EasyEDA schematic, RP2040 module rather than bare silicon, and why
- SH1106 over SSD1306
- Key switch footprint decision
- The rev 2.1 changes

## The BOM mistake

Ordered Kailh K-Low sockets instead of MX (CPG151101S11). What that costs when the boards are
already in the mail, and how to sanity check a footprint against a part number before you
click order.

## Fabrication

- JLCPCB order settings that actually matter
- What to assemble yourself and what to pay for

## Firmware architecture

`config.py` → `store.py` (flat JSON persistence, tested) → hardware modules → BLE advertiser
and scanner → game modules. Why persistence went in early instead of last.

## What broke at the event

## Revision 3 wish list
