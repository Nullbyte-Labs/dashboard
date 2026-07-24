---
title: "Reflash your ZERODAY badge into a CircuitPython macropad"
slug: zeroday-badge-macropad
date: 2026-07-28
designator: H2
series: hardware
summary: "The badge from the meetup is a Pico W with an OLED, four keys, and RGB. Here is how to update the firmware you have, or wipe it and turn the badge into a USB macropad you will actually keep on your desk."
video: https://www.youtube-nocookie.com/embed/VIDEO_ID
tags: [pico, circuitpython, micropython, badge]
draft: true
---

The badge you took home is not a souvenir, it is a Raspberry Pi Pico W with a display, four
keys, and addressable RGB soldered to it. This guide covers both things people asked me for
after the meetup: pulling the latest badge firmware onto a badge you already have, and
converting it into a CircuitPython USB macropad once you are done playing the game.

Nothing here can brick the board permanently. The Pico's bootloader lives in mask ROM — if
the firmware ends up in a bad state, you hold BOOTSEL, replug, and start over.

## Know your board first

| Part | What it is | Note |
| --- | --- | --- |
| MCU | Raspberry Pi Pico W (RP2040) | USB-C or micro-USB depending on your revision |
| Display | SH1106 OLED over I2C | Driven by `display.py` in the badge firmware |
| RGB | WS2812B NeoPixels on GP6 | Single data line, chained |
| Keys | Four tactile switches, MX-style sockets | Mapped like an NES pad: A and B |
| Power | USB, plus battery header | |

One hardware rule before you get out an iron: **never solder pin 37 (3V3_EN)**. Pulling that
pin the wrong way takes the regulator out of the picture and the board stops enumerating.
Nothing else on this badge is that unforgiving.

A quirk worth knowing if you write your own key handling: the switch labelled A is wired to
`PIN_SW2` and B is wired to `PIN_SW1`. That is why the cheat code on the badge is entered as
**B A A B** rather than the sequence you would expect from the silkscreen.

## Path 1 — update the badge firmware you already have

The badge ships MicroPython with the Nullbyte Labs badge firmware on top of it. Updating
means replacing the Python files, not the whole runtime, unless you are also moving to a
newer MicroPython build.

1. Install Thonny (any OS) or `mpremote` if you prefer the terminal.
2. Plug the badge in. In Thonny, set the interpreter to MicroPython (Raspberry Pi Pico) and
   pick the serial port that appeared.
3. Back up what is on there first — your saved game state lives in a JSON file written by
   `store.py`, and reflashing will take it with you:

   ```bash
   mpremote connect /dev/ttyACM0 fs ls
   mpremote connect /dev/ttyACM0 fs cp :state.json ./state-backup.json
   ```

4. Clone the firmware and push the module set:

   ```bash
   git clone -b dev https://github.com/Nullbyte-Labs/CR_HardwareBadge
   cd CR_HardwareBadge/firmware
   mpremote connect /dev/ttyACM0 fs cp *.py :
   mpremote connect /dev/ttyACM0 reset
   ```

5. The OLED should show the boot banner and the firmware version. If the screen stays dark
   but the RGB lights up, you have an I2C problem, not a code problem — reseat the display
   ribbon and check for a cold joint on the SDA and SCL pads.

The badge WiFi and the HQ server it talks to are event-specific and are configured in
`config.py`. Off-network, the badge runs standalone and the multiplayer infection states
simply never change.

## Path 2 — convert it to a CircuitPython macropad

This wipes MicroPython. Back up first if you care about your game state.

### Flash CircuitPython

1. Download the CircuitPython UF2 for **Raspberry Pi Pico W** from circuitpython.org.
2. Hold BOOTSEL, plug the badge into USB, release. A drive named `RPI-RP2` mounts.
3. Drag the UF2 onto it. The board reboots and remounts as `CIRCUITPY`.

### Add the libraries

Download the CircuitPython library bundle matching your version and copy these into
`CIRCUITPY/lib/`:

```
adafruit_hid/
adafruit_displayio_sh1106.mpy
neopixel.mpy
```

### Write code.py

Save this as `code.py` in the root of `CIRCUITPY`. It enumerates as a USB keyboard, lights
the keys, and sends four macros.

```python
import board
import digitalio
import neopixel
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# Confirm these against your badge revision before you rely on them.
KEY_PINS = (board.GP2, board.GP3, board.GP4, board.GP5)
PIXEL_PIN = board.GP6
PIXEL_COUNT = 4

MACROS = (
    (Keycode.CONTROL, Keycode.SHIFT, Keycode.T),   # reopen closed tab
    (Keycode.GUI, Keycode.L),                      # lock the workstation
    (Keycode.CONTROL, Keycode.ALT, Keycode.T),     # terminal
    (Keycode.CONTROL, Keycode.SHIFT, Keycode.ESCAPE),
)

COLORS = ((40, 0, 0), (0, 40, 0), (0, 0, 40), (40, 30, 0))

keys = []
for pin in KEY_PINS:
    io = digitalio.DigitalInOut(pin)
    io.direction = digitalio.Direction.INPUT
    io.pull = digitalio.Pull.UP          # switches pull to ground
    keys.append(io)

pixels = neopixel.NeoPixel(PIXEL_PIN, PIXEL_COUNT, brightness=0.25, auto_write=True)
for i, color in enumerate(COLORS[:PIXEL_COUNT]):
    pixels[i] = color

kbd = Keyboard(usb_hid.devices)
held = [False] * len(keys)

while True:
    for i, key in enumerate(keys):
        pressed = not key.value          # active low
        if pressed and not held[i]:
            kbd.send(*MACROS[i])
        held[i] = pressed
```

Save the file and CircuitPython reloads on its own. Press a key; if nothing happens, open the
serial console (`screen /dev/ttyACM0 115200`) and read the traceback — CircuitPython prints
errors there instead of failing silently.

> The GPIO numbers above match my badges. If yours came from a different fabrication run,
> check the schematic in the repo before you assume. A key that never registers is almost
> always a pin mapping mistake, not dead hardware.

### Where to take it next

Swap `kbd.send()` for `adafruit_hid.consumer_control` to get media keys, or use the OLED to
show which macro layer you are on and add a layer toggle on a long press. The display driver
is already in the bundle you installed.

## Going back to the badge firmware

Hold BOOTSEL, drop the MicroPython UF2 on, re-copy the badge `.py` files. Nothing you did
here is one-way.
