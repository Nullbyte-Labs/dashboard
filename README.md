# nullbyte-labs.com

Static site for Nullbyte Labs tutorials. Markdown in, plain HTML out — no JavaScript
framework, no client-side JS at all beyond the YouTube iframe you opt into per post.

```
build.py                 site generator (Jinja2 + Markdown + PyYAML)
content/posts/*.md       tutorials, YAML front matter + Markdown body
templates/               base, index, tutorials index, post, 404
static/                  css + favicon
site/                    build output (gitignored, this is what gets served)
Caddyfile                web server config, HTTP only, behind the tunnel
docker-compose.yml       caddy + cloudflared
```

## Build

```bash
make install     # venv + deps
make serve       # build and serve on http://127.0.0.1:8000
make build       # build only
```

## Writing a tutorial

Create `content/posts/YYYY-MM-DD-slug.md`:

```yaml
---
title: "Install Kali in a VM and fix it with PimpMyKali"
slug: kali-vm-pimpmykali        # optional, derived from title if omitted
date: 2026-07-21
series: lab                     # lab | hardware | ctf
summary: "One sentence. Shows on every card and in the RSS feed."
video: https://www.youtube-nocookie.com/embed/VIDEO_ID   # optional
draft: false
tags: [kali, lab]
---
```

Tracks are defined in `SERIES` at the top of `build.py`. Each post gets a plain tag —
`LAB`, `HARDWARE`, or `CTF` — with a number showing its position within that track (oldest
published = 01), computed automatically at build time from publish date. No front matter
field to set; adding a track is a four-line dict edit to `SERIES`.

Use the `youtube-nocookie.com/embed/` form for videos — the Content-Security-Policy in the
Caddyfile only allows frames from that origin, and it keeps YouTube from setting cookies on
your visitors before they click play.

## Fonts

The templates load Chakra Petch and IBM Plex from Google Fonts. If you would rather not send
visitor IPs to Google, download the WOFF2 files into `static/fonts/`, drop `@font-face` rules
at the top of `style.css`, delete the three `<link>` tags in `templates/base.html`, and remove
`fonts.googleapis.com` / `fonts.gstatic.com` from the CSP.

## Deploying

### Option A — Cloudflare Pages (recommended)

The site is fully static. Pages serves it from Cloudflare's edge for free, with no origin to
attack, no Pi to patch, and no downtime when your ISP or your power blinks.

1. Push this repo to GitHub.
2. Cloudflare dashboard → Workers & Pages → Create → Pages → connect the repo.
3. Framework preset **None**. Build command
   `pip install -r requirements.txt && python build.py`, output directory `site`, root
   directory `/`.
4. Set the build environment variable `PYTHON_VERSION=3.13` (the repo also carries a
   `.python-version` file). Pages build image v3 defaults to Python 3.13, but pin it so a
   future image change cannot silently break your build.
5. Custom domains → add `nullbyte-labs.com` and `www.nullbyte-labs.com`. DNS records are
   created for you; confirm both are proxied.
6. Every push to `main` rebuilds. Every pull request gets its own preview URL — use that to
   proofread a tutorial before it goes live.

Delete `.github/workflows/deploy.yml` if you go this route; it is for the self-hosted path
and will fail without a runner.

### Option B — self-hosted behind a Cloudflare Tunnel

Use this if you want the box in the loop. Never port-forward 80/443 to it.

1. `python3 build.py`
2. Cloudflare dashboard → Zero Trust → Networks → Tunnels → Create a tunnel → Cloudflared.
   Copy the token.
3. `echo "TUNNEL_TOKEN=eyJ..." > .env`
4. `docker compose up -d`
5. In the tunnel's Public Hostname tab: hostname `nullbyte-labs.com`, service
   `http://web:8080`. Add a second entry for `www` pointing at the same service.
6. Cloudflare DNS gets the `CNAME` records automatically — verify both are proxied (orange
   cloud).

Hardware note: a Pi 3 or a 1 vCPU / 512 MB Proxmox CT is more than enough. This is flat files;
the tunnel and Cloudflare's cache absorb everything else.

### Cloudflare settings to set either way

| Setting | Value | Why |
| --- | --- | --- |
| SSL/TLS mode | Full (strict) on Pages, or leave default with a tunnel | Tunnel traffic is already authenticated end to end |
| Always Use HTTPS | On | |
| Automatic HTTPS Rewrites | On | |
| HSTS | Enable, 6 months, include subdomains once you are confident | Hard to undo, so do it after the site is stable |
| Bot Fight Mode | On | Free tier, kills most scraper noise |
| Email obfuscation | On | |
| Redirect rule | `www.nullbyte-labs.com/*` → `https://nullbyte-labs.com/$1`, 301 | One canonical hostname |
| DNSSEC | Enable at the registrar | |

If you self-host, also set a WAF custom rule blocking anything that is not `nullbyte-labs.com`
in the Host header, and check the tunnel is the only path in — `curl` your public IP directly
and confirm nothing answers on 80 or 443.

## What is deliberately not here

No analytics, no comments, no newsletter widget, no third-party JS. Add Cloudflare Web
Analytics from the dashboard if you want numbers; it needs one script tag and a CSP entry.
