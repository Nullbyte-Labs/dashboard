#!/usr/bin/env python3
"""Nullbyte Labs static site builder.

Reads Markdown + YAML front matter from content/posts/, renders Jinja2
templates from templates/, writes a fully static site to site/.

    python3 build.py            # build once
    python3 build.py --serve    # build, then serve site/ on :8000

Front matter keys:
    title       required
    date        required (YYYY-MM-DD)
    designator  required (silkscreen ref, e.g. K1, H3, C2)
    series      required (must match a key in SERIES below)
    summary     required (one sentence, shown on cards)
    video       optional (YouTube URL; adds a watch link)
    draft       optional (true = excluded from build)
    tags        optional (list)
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent.resolve()
CONTENT = ROOT / "content" / "posts"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUT = ROOT / "site"

SITE = {
    "name": "Nullbyte Labs",
    "tagline": "Hardware hacking and security tutorials, from bench to breach.",
    "url": "https://nullbyte-labs.com",
    "author": "K0DA",
    "youtube": "https://www.youtube.com/@Nullbyte-Labs",
    "github": "https://github.com/Nullbyte-Labs",
    "description": (
        "Long-form tutorials on lab setup, badge hardware hacking, and "
        "capture the flag, written and filmed by K0DA at Nullbyte Labs."
    ),
}

# Track labels shown as tags on every post. Plain and self-explanatory —
# no cipher to learn. `slug` feeds the CSS modifier class (.tag--lab etc).
SERIES = {
    "lab": {
        "label": "LAB",
        "name": "Build the lab",
        "blurb": "Get a working attack box and a target to point it at.",
    },
    "hardware": {
        "label": "HARDWARE",
        "name": "Open the hardware",
        "blurb": "Badges, headers, and the pads the vendor forgot to remove.",
    },
    "ctf": {
        "label": "CTF",
        "name": "Play the game",
        "blurb": "Capture the flag from first flag to first placement.",
    },
}

MD_EXTENSIONS = ["extra", "toc", "codehilite", "sane_lists", "admonition"]
MD_CONFIG = {"codehilite": {"guess_lang": False, "css_class": "code"}}


@dataclass
class Post:
    slug: str
    title: str
    date: dt.date
    series: str
    summary: str
    body: str
    toc: str
    video: str | None = None
    tags: list[str] = field(default_factory=list)
    reading_minutes: int = 1
    track_number: int = 1  # position within its series, oldest = 1; set by load_posts()

    @property
    def url(self) -> str:
        return f"/tutorials/{self.slug}/"

    @property
    def series_name(self) -> str:
        return SERIES[self.series]["name"]

    @property
    def track_label(self) -> str:
        return SERIES[self.series]["label"]

    @property
    def date_display(self) -> str:
        return self.date.strftime("%d %b %Y").upper()


def slugify(value: str) -> str:
    value = re.sub(r"[^\w\s-]", "", value.lower()).strip()
    return re.sub(r"[\s_-]+", "-", value)


def parse_post(path: Path) -> Post | None:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        sys.exit(f"{path.name}: missing YAML front matter")
    _, fm_raw, body_raw = raw.split("---", 2)
    meta = yaml.safe_load(fm_raw) or {}

    if meta.get("draft"):
        return None

    for key in ("title", "date", "series", "summary"):
        if key not in meta:
            sys.exit(f"{path.name}: front matter missing '{key}'")
    if meta["series"] not in SERIES:
        sys.exit(f"{path.name}: unknown series '{meta['series']}'")

    md = markdown.Markdown(extensions=MD_EXTENSIONS, extension_configs=MD_CONFIG)
    body = md.convert(body_raw.strip())
    words = len(re.findall(r"\w+", body_raw))

    date = meta["date"]
    if isinstance(date, str):
        date = dt.date.fromisoformat(date)

    return Post(
        slug=meta.get("slug") or slugify(meta["title"]),
        title=meta["title"],
        date=date,
        series=meta["series"],
        summary=meta["summary"],
        body=body,
        toc=getattr(md, "toc", ""),
        video=meta.get("video"),
        tags=meta.get("tags", []) or [],
        reading_minutes=max(1, round(words / 200)),
    )


def load_posts() -> list[Post]:
    posts = [p for f in sorted(CONTENT.glob("*.md")) if (p := parse_post(f))]
    posts.sort(key=lambda p: p.date)  # oldest first, for stable per-series numbering
    counters = {key: 0 for key in SERIES}
    for p in posts:
        counters[p.series] += 1
        p.track_number = counters[p.series]
    posts.sort(key=lambda p: p.date, reverse=True)  # newest first for display
    return posts


def render_sitemap(posts: list[Post]) -> str:
    urls = ["/", "/tutorials/"] + [p.url for p in posts]
    body = "\n".join(
        f"  <url><loc>{SITE['url']}{u}</loc></url>" for u in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n</urlset>\n"
    )


def render_feed(posts: list[Post]) -> str:
    items = []
    for p in posts[:20]:
        stamp = dt.datetime.combine(p.date, dt.time()).strftime(
            "%a, %d %b %Y %H:%M:%S +0000"
        )
        items.append(
            "    <item>\n"
            f"      <title>{p.title}</title>\n"
            f"      <link>{SITE['url']}{p.url}</link>\n"
            f"      <guid>{SITE['url']}{p.url}</guid>\n"
            f"      <pubDate>{stamp}</pubDate>\n"
            f"      <description>{p.summary}</description>\n"
            "    </item>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>\n'
        f"    <title>{SITE['name']}</title>\n"
        f"    <link>{SITE['url']}</link>\n"
        f"    <description>{SITE['description']}</description>\n"
        + "\n".join(items)
        + "\n</channel></rss>\n"
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    posts = load_posts()
    by_series = {
        key: [p for p in posts if p.series == key] for key in SERIES
    }
    ctx = {
        "site": SITE,
        "series": SERIES,
        "posts": posts,
        "by_series": by_series,
        "year": dt.date.today().year,
        "build_stamp": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
    }

    write(OUT / "index.html", env.get_template("index.html").render(**ctx))
    write(
        OUT / "tutorials" / "index.html",
        env.get_template("tutorials.html").render(**ctx),
    )
    write(OUT / "404.html", env.get_template("404.html").render(**ctx))

    post_tpl = env.get_template("post.html")
    for i, post in enumerate(posts):
        write(
            OUT / "tutorials" / post.slug / "index.html",
            post_tpl.render(
                post=post,
                newer=posts[i - 1] if i else None,
                older=posts[i + 1] if i + 1 < len(posts) else None,
                **ctx,
            ),
        )

    write(OUT / "sitemap.xml", render_sitemap(posts))
    write(OUT / "feed.xml", render_feed(posts))
    write(
        OUT / "robots.txt",
        f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n",
    )
    shutil.copytree(STATIC, OUT / "static")

    print(f"built {len(posts)} tutorials -> {OUT}")


def serve() -> None:
    import http.server
    import socketserver

    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(
        *a, directory=str(OUT), **kw
    )
    with socketserver.TCPServer(("", 8000), handler) as httpd:
        print("serving http://127.0.0.1:8000 (ctrl-c to stop)")
        httpd.serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve", action="store_true", help="serve after building")
    args = ap.parse_args()
    build()
    if args.serve:
        serve()