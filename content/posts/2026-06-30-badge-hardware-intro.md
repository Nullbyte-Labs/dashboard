---
title: "Badge hardware hacking: find the debug header the vendor left behind"
slug: badge-hardware-intro
date: 2026-06-30
designator: H1
series: hardware
summary: "Conference badges are teaching boards with a silkscreen roadmap. Here is how to read one, find UART, and get a console on a device you have never seen."
tags: [hardware, uart, badges]
---

Every conference badge you own is an embedded device with the test points still exposed. The
manufacturer of your router removed them; the badge designer left them because they had to
program the thing on a deadline. That makes badges the cheapest possible training target for
the exact workflow you would use against real hardware.

## Read the board before you touch it

Start with the silkscreen. The white printing carries reference designators that tell you what
each part is before you measure anything:

- `U` — integrated circuit. The big one is your microcontroller. Read the part number, then
  pull the datasheet.
- `J` — connector or header. Unpopulated `J` footprints are your first suspects.
- `TP` — test point. Almost always something the designer needed during bring-up.
- `R` / `C` — resistors and capacitors. Useful mostly for finding pull-ups on I2C lines.

Photograph both sides at high resolution before you probe. You will want to zoom in later
without picking the board back up.

## Find UART

A serial console is often four pads in a row: ground, transmit, receive, and a voltage pin you
should not connect. Identify them with a multimeter, board unpowered first:

1. Set the meter to continuity and find ground by testing pads against a known ground —
   the shell of a USB port or the negative terminal of the battery holder.
2. Power the board and switch to DC volts. TX usually idles at logic level (3.3 V is typical,
   1.8 V on newer parts) and dips as boot messages stream out.
3. RX often sits near zero or floats.

Wire a USB-to-serial adapter — TX to RX, RX to TX, ground to ground, **never** the voltage
pin — and open the port:

```bash
sudo dmesg | tail            # confirm which /dev/ttyUSB* appeared
sudo screen /dev/ttyUSB0 115200
```

Garbage on screen means the baud rate is wrong. Work down the common list: 115200, 57600,
38400, 9600.

## What a console gets you

On a badge running MicroPython or CircuitPython, a serial console is often a full REPL — the
equivalent of a root shell. You can list the filesystem, read stored credentials, and rewrite
the firmware from that prompt. On bare-metal C firmware you are more likely to land at a
bootloader, which is where dumping flash over SWD or ICSP becomes the next move.

## The rules I follow

Work on hardware you own. Badges from a conference you attended are yours; the vendor demo
unit in the hallway is not. If you find a real vulnerability in a shipped product while
poking around, disclose it to the vendor before you post it.

## Next in this track

Dumping flash from an AVR badge over ICSP with `avrdude`, and what to do with the hex file
once you have it.
