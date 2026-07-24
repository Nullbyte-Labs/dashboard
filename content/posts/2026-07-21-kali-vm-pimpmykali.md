---
title: "Install Kali in a VM and fix it with PimpMyKali"
slug: kali-vm-pimpmykali
date: 2026-07-21
designator: K1
series: lab
summary: "A clean Kali virtual machine, snapshotted before you touch it, then patched with PimpMyKali so the tools you need on day one actually run."
tags: [kali, virtualization, lab]
---

Kali ships as a distribution, not as a finished lab. The prebuilt VM images boot fine, then
you hit the same wall everyone hits: a missing Impacket dependency, a broken `golang` path, a
`pip` that refuses to install anything because the environment is externally managed. This
walkthrough gets you from download to a working, snapshotted box in about forty minutes, and
explains what the fixup script is actually changing so you are not running someone else's
`sudo` blindly.

## What you need

| Item | Notes |
| --- | --- |
| Hypervisor | VMware Workstation Pro, VirtualBox, or Proxmox. All free for personal use. |
| Disk | 80 GB thin-provisioned minimum. Kali plus wordlists eats 40 GB fast. |
| RAM | 4 GB works, 8 GB is comfortable once you start running targets alongside it. |
| Download | The prebuilt VM image from kali.org, plus the published SHA256SUMS file. |

## Verify the image before you boot it

Skipping this step is the single most common mistake in every lab-setup guide on the
internet. Download the checksum file alongside the image and compare:

```bash
sha256sum kali-linux-*-vmware-amd64.7z
grep "$(sha256sum kali-linux-*-vmware-amd64.7z | cut -d' ' -f1)" SHA256SUMS
```

No match means no boot. Delete it and pull again from a different mirror.

## First boot, then snapshot

Boot the VM, log in with the default credentials, and change them immediately:

```bash
passwd
sudo hostnamectl set-hostname nbl-kali
sudo apt update && sudo apt full-upgrade -y
sudo reboot
```

Now take a snapshot and name it `clean-updated`. Every time you break the box — and you will,
usually at 1 a.m. while installing something from a GitHub repo with three open issues — you
roll back here instead of rebuilding.

## What PimpMyKali actually does

PimpMyKali is a maintained shell script that applies the fixes the community keeps
re-discovering: repairing `pip` and virtual environment handling, installing the Impacket
suite properly, fixing missing desktop and driver bits, adding common tools like
`bloodhound`, `feroxbuster`, and `seclists`, and correcting file permissions the images ship
with.

> Read the script before you run it. Not because this one is untrustworthy, but because
> "curl this URL into bash as root" is a habit you do not want to form in a security career.

```bash
git clone https://github.com/Dewalt-arch/pimpmykali
cd pimpmykali
less pimpmykali.sh          # actually read it
sudo ./pimpmykali.sh
```

Choose the fix option for an existing install, or the new-VM option if this is a fresh
image. The menu tells you which fixes it is applying; note them, because half of them are
things you will need to fix by hand on a client-provided box someday.

## Snapshot again

When it finishes and you have rebooted, snapshot as `pimped`. That is your working baseline.

## Where to go next

The lab is only half built — you have an attacker and no target. Next in this track: standing
up a vulnerable target VM on an isolated host-only network so nothing you do can route to
your home LAN.
