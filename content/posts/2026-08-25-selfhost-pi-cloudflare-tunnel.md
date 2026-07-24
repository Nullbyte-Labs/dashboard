---
title: "Self-host a real app from a Raspberry Pi without opening a port"
slug: selfhost-pi-cloudflare-tunnel
date: 2026-08-25
designator: K2
series: lab
summary: "A Flask app on a Pi 3, published to the internet through a Cloudflare Tunnel, deployed by a self-hosted GitHub Actions runner — and the mistakes that make this setup dangerous if you rush it."
draft: true
tags: [raspberry-pi, cloudflare, flask, gunicorn]
---

<!-- DRAFT OUTLINE — based on the dungeon-daily.com deployment. -->

## Why not port forwarding

The threat model of exposing 443 on your home router to a device on the same LAN as
everything else you own.

## The stack

Pi 3 → Gunicorn → Cloudflare Tunnel. No inbound firewall rule anywhere.

## Segment the Pi first

VLAN or a separate subnet before the app ever listens. This is the step everyone skips.

## Deploy pipeline

Self-hosted GitHub Actions runner, what permissions it needs and what it must never have.

## The security work people leave until it is too late

Server-side session state instead of client-side cookies, a config class that refuses to boot
without a real secret key, and how to tell whether your framework's defaults are protecting
you or just quiet.
