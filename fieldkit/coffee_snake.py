#!/usr/bin/env python3
"""Generate original Coffee Pot Snake cover art using Python's standard library."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from random import Random
import shutil


TITLE = "Raspberry Pi for Technical Support Operatives in Africa"
AUTHOR = "William Majanja"
COMMUNITY = "Hack with Raspberry Pi community"
PALETTES = (
    ("#102a3a", "#07151f", "#8ee3d0", "#f4a261", "#e2f4ef"),
    ("#132d25", "#081810", "#c4e86b", "#f2b84b", "#eff8d9"),
    ("#26304a", "#101628", "#8ad4ff", "#ffb38a", "#edf6ff"),
    ("#38233c", "#171020", "#e7a8ff", "#ffcc66", "#fff0fa"),
    ("#26353c", "#101a20", "#70dfc1", "#ff805b", "#eafff7"),
)
EYES = ("o o", "0 0", "^ ^", ". .", "@ @")
STEAM = ("~ ~ ~", ". . .", "' ' '", "^ ^ ^")


def make_seed(seed_text: str | None) -> bytes:
    if seed_text is None:
        return secrets.token_bytes(32)
    try:
        seed = bytes.fromhex(seed_text)
    except ValueError as error:
        raise ValueError("--seed must be hexadecimal") from error
    if not 16 <= len(seed) <= 64:
        raise ValueError("--seed must decode to 16–64 bytes")
    return seed


def edition_id(seed: bytes) -> str:
    """Return a pseudonymous variant identifier, not a user or security identity."""
    return hashlib.sha256(b"coffee-snake-edition-v1\0" + seed).hexdigest()[:24]


def art_lines(seed: bytes) -> list[str]:
    rng = Random(int.from_bytes(hashlib.sha256(seed).digest(), "big"))
    slash = chr(92)
    eyes = rng.choice(EYES)
    steam = rng.choice(STEAM)
    lean = rng.choice(("left", "right"))
    if lean == "left":
        head = [
            "       /" + slash + "_/" + slash,
            "      /  " + eyes + "  " + slash,
            "      " + slash + "   Y   /",
            "       `-----'",
        ]
        pot = [
            "      .-========-.       ",
            "   __/  COFFEE   " + slash + "____   ",
            "  /    |   POT   |    " + slash + "__",
            " |     |_________|       )",
            "  " + slash + "_____________________/",
        ]
    else:
        head = [
            "                     /" + slash + "_/" + slash,
            "                    /  " + eyes + "  " + slash,
            "                    " + slash + "   Y   /",
            "                     `-----'",
        ]
        pot = [
            "       .----------.      ",
            "   ___/  COFFEE    " + slash + "___  ",
            "  /    |    POT    |   " + slash + "_",
            " |     |___________|     /",
            "  " + slash + "____________________/",
        ]
    return [
        "             " + rng.choice(STEAM),
        *head,
        "          __/      " + slash + "__",
        "      _.-'            `-._",
        "    .'                    `.",
        *pot,
        "    `-._   ||      ||   _.-'",
        "         `-||------||-'",
        "           ||      ||",
    ]


def render_ascii(seed: bytes, variant_id: str | None = None) -> str:
    variant_id = variant_id or edition_id(seed)
    return (
        f"{TITLE}\nby {AUTHOR}\n\n"
        "           THE COFFEE POT SNAKE\n\n"
        + "\n".join(art_lines(seed))
        + f"\n\nEdition fingerprint: {variant_id}\n"
        + f"An initiative of the {COMMUNITY}\n"
    )


def render_svg(seed: bytes, variant_id: str | None = None) -> str:
    variant_id = variant_id or edition_id(seed)
    palette_rng = Random(int.from_bytes(hashlib.sha256(b"palette\0" + seed).digest(), "big"))
    background_a, background_b, accent, orange, foreground = palette_rng.choice(PALETTES)
    x = 360 if art_lines(seed)[1].startswith("       ") else 260
    art = "\n".join(
        f'<text x="{x}" y="{1030 + index * 42}" xml:space="preserve">{html.escape(line)}</text>'
        for index, line in enumerate(art_lines(seed))
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="2400" viewBox="0 0 1600 2400" role="img" aria-labelledby="title description">
  <title id="title">{html.escape(TITLE)}</title>
  <desc id="description">Original randomized Coffee Pot Snake ASCII cover, edition {variant_id}.</desc>
  <defs>
    <linearGradient id="background" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{background_a}"/><stop offset="1" stop-color="{background_b}"/>
    </linearGradient>
    <pattern id="grid" width="80" height="80" patternUnits="userSpaceOnUse">
      <path d="M80 0H0V80" fill="none" stroke="{accent}" stroke-opacity=".06" stroke-width="2"/>
      <circle cx="0" cy="0" r="3" fill="{accent}" fill-opacity=".2"/>
    </pattern>
  </defs>
  <rect width="1600" height="2400" fill="url(#background)"/>
  <rect width="1600" height="2400" fill="url(#grid)"/>
  <path d="M0 0H1600V22H0Z" fill="{orange}"/>
  <text x="130" y="175" fill="{accent}" font-family="sans-serif" font-size="27" font-weight="700" letter-spacing="4">{html.escape(COMMUNITY.upper())}</text>
  <text x="130" y="400" fill="{foreground}" font-family="sans-serif" font-size="82" font-weight="700">Raspberry Pi</text>
  <text x="130" y="505" fill="{foreground}" font-family="sans-serif" font-size="57" font-weight="700">for Technical Support</text>
  <text x="130" y="585" fill="{accent}" font-family="sans-serif" font-size="57" font-weight="700">Operatives in Africa</text>
  <text x="135" y="665" fill="{foreground}" fill-opacity=".8" font-family="sans-serif" font-size="27">A field guide to Raspberry Pi, Linux, and responsible support</text>
  <rect x="100" y="760" width="1400" height="1120" rx="26" fill="{background_b}" stroke="{accent}" stroke-opacity=".7" stroke-width="3"/>
  <text x="800" y="845" text-anchor="middle" fill="{orange}" font-family="sans-serif" font-size="26" font-weight="700" letter-spacing="5">THE COFFEE POT SNAKE</text>
  <text x="800" y="888" text-anchor="middle" fill="{accent}" font-family="sans-serif" font-size="20">ORIGINAL ASCII ART · NO EXTERNAL ASSETS</text>
  <g fill="{foreground}" font-family="DejaVu Sans Mono, Liberation Mono, monospace" font-size="29">{art}</g>
  <path d="M100 1980H1500" stroke="{accent}" stroke-opacity=".7" stroke-width="3"/>
  <text x="130" y="2080" fill="{foreground}" font-family="sans-serif" font-size="38" font-weight="700">{html.escape(AUTHOR)}</text>
  <text x="130" y="2140" fill="{foreground}" fill-opacity=".8" font-family="sans-serif" font-size="24">An initiative of the {html.escape(COMMUNITY)}</text>
  <text x="130" y="2260" fill="{accent}" font-family="monospace" font-size="19">Edition {variant_id}</text>
  <text x="1470" y="2260" text-anchor="end" fill="{accent}" font-family="sans-serif" font-size="20" letter-spacing="2">DIGITAL-FIRST · FIELD-READY · CC0 ORIGINALS</text>
</svg>
'''


def write_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()


def generate(output_dir: Path, seed: bytes) -> tuple[Path, Path, Path]:
    variant = edition_id(seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    edition_dir = output_dir / variant
    if edition_dir.exists() or edition_dir.is_symlink():
        raise FileExistsError(f"Edition already exists: {edition_dir}")
    edition_dir.mkdir()
    ascii_path = edition_dir / "cover.txt"
    svg_path = edition_dir / "cover.svg"
    manifest_path = edition_dir / "edition.json"
    svg = render_svg(seed, variant)
    manifest = {
        "schema": "coffee-snake-edition.v1",
        "edition_id": variant,
        "seed_hex": seed.hex(),
        "cover_sha256": hashlib.sha256(svg.encode("utf-8")).hexdigest(),
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "privacy": "No name, email, host name, or network address is collected.",
    }
    try:
        write_new(ascii_path, render_ascii(seed, variant).encode("utf-8"))
        write_new(svg_path, svg.encode("utf-8"))
        write_new(manifest_path, (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    except Exception:
        shutil.rmtree(edition_dir, ignore_errors=True)
        raise
    return ascii_path, svg_path, manifest_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", help="hexadecimal seed for reproducible artwork; random if omitted")
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    try:
        seed = make_seed(args.seed)
        paths = generate(args.output_dir, seed)
    except (OSError, ValueError) as error:
        print(f"coffee-snake: {error}", file=sys.stderr)
        return 2
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
