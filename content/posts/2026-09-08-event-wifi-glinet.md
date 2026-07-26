---
title: "Build an isolated WiFi network for a live event with a travel router"
slug: event-wifi-glinet
date: 2026-09-08
designator: H4
series: hardware
summary: "How the ZERODAY badges and the scoreboard server talked to each other without touching the venue network — and why you wipe the router the moment the event ends."
draft: true
tags: [glinet, networking, event, badges]
---

<!-- DRAFT OUTLINE -->

## The problem an event network solves

Venue WiFi is out of your control and often filtered in ways that break device-to-device
traffic entirely. Badges that need to see each other, and a scoreboard server that needs to
see all of them, want their own Layer 2 network with nothing else on it — not the venue's
guest WiFi, not attendees' phones, nothing you didn't put there on purpose.

## Why a travel router instead of venue infrastructure

- No dependency on venue IT saying yes to a VLAN request
- Fully portable, torn down and rebuilt in minutes
- One thing you own end to end, so when something breaks at 8am on event day you can
  actually fix it

## Access point mode, no WAN uplink

The GLiNet ran as a plain access point — no repeater, no bridge to venue WiFi, and
deliberately no internet uplink at all. That last part is the detail worth calling out: this
wasn't "isolated from the venue network," it was disconnected from the internet entirely.
Nothing on that SSID could reach anything outside the room, in either direction, because
there was no path out to begin with. That's a stronger guarantee than firewall rules on a
network that's still technically routed somewhere — there's simply nowhere for traffic to go.

Cover in this section:

- Where in the GLiNet admin UI you set AP mode instead of the factory default (often
  repeater/travel mode out of the box)
- Confirming no WAN interface is configured — the router should show no internet connection
  in its own status page, which is the check that matters more than any firewall setting
- Setting the event SSID and passphrase (placeholder values only, see below)

## Scoreboard server on the network

The Raspberry Pi running the scoreboard connected to the GLiNet AP and came up automatically
on boot — no manual join step on event day, which mattered because the last thing you want at
8am on event morning is troubleshooting a WiFi handshake in front of people. Cover:

- How the Pi's WiFi client was configured to auto-join the event SSID on boot
- Static DHCP reservation so the badges always find the same address for HQ

## What NOT to put in this article

No real SSID, no real passphrase, no real IP address, no real port number from the actual
event. Every screenshot gets the SSID/IP field blurred or replaced with a placeholder before
this goes anywhere near YouTube or the blog. This isn't paranoia — it's the same network this
router might get reused for at the next event, and screenshots outlive the event by years.

## Sanitize the router the moment the event ends

This is the section that matters most and should not be an afterthought at the bottom.

- Factory reset the travel router before it goes back in the bag — don't just change the
  SSID, actually reset it
- Rotate any admin password that was reused across events
- If the router was ever bridged onto a network with broader access (hotel WiFi, home
  network) during setup or testing, treat that as a reason to reset regardless
- Make this a checklist item that happens at strike, not "whenever I remember" — pair it with
  packing up the badges themselves so it's part of the physical teardown routine, not a
  separate task that gets skipped

## Recap

One-time credentials, wiped hardware, no lingering access into a network that no longer needs
to exist once the event is over.
