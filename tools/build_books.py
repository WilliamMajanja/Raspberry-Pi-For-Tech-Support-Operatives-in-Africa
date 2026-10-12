#!/usr/bin/env python3
"""Build linked PDF and EPUB editions from the book's SUMMARY.md reading order.

Optional build tools: Pandoc and Chromium. Reading the Markdown book itself
requires no build tools or installed packages.
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
SUMMARY = ROOT / "SUMMARY.md"
CSS = ROOT / "tools" / "book.css"
COVER_SVG = ROOT / "tools" / "book-cover.svg"
REPOSITORY = "https://github.com/WilliamMajanja/Raspberry-Pi-For-Tech-Support-Operatives-in-Africa"
TITLE = "Raspberry Pi for Technical Support Operatives in Africa"
AUTHOR = "William Majanja"
PUBLISHER = "Hack with Raspberry Pi community"
PDF_NAME = "Raspberry-Pi-for-Technical-Support-Operatives-in-Africa.pdf"
EPUB_NAME = "Raspberry-Pi-for-Technical-Support-Operatives-in-Africa.epub"
COVER_NAME = "cover.png"
INLINE_LINK = re.compile(r"\[[^\]\n]*\]\(")
ATX_HEADING = re.compile(r"^( {0,3})(#{1,6})[ \t]+(.+?)\s*$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def slugify(value: str) -> str:
    value = re.sub(r"\{#[^}]+\}\s*$", "", value)
    value = re.sub(r"!?(?:\[([^\]]+)\]\([^)]*\))", r"\1", value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"[`*_~]", "", value)
    value = html.unescape(value).strip().lower()
    parts: list[str] = []
    pending_dash = False
    for char in value:
        if unicodedata.category(char)[0] in {"L", "N"}:
            if pending_dash and parts:
                parts.append("-")
            parts.append(char)
            pending_dash = False
        else:
            pending_dash = True
    return "".join(parts).strip("-") or "section"


def reading_order() -> list[Path]:
    """Return local Markdown pages linked directly from the published contents."""
    documents: list[Path] = []
    seen: set[Path] = set()
    contents = SUMMARY.read_text(encoding="utf-8")
    for match in INLINE_LINK.finditer(contents):
        opening = match.end()
        closing = contents.find(")", opening)
        if closing < 0:
            continue
        destination = contents[opening:closing].strip()
        if destination.startswith("<") and ">" in destination:
            destination = destination[1 : destination.index(">")]
        parsed = urlsplit(destination)
        if parsed.scheme or parsed.netloc or not parsed.path.lower().endswith(".md"):
            continue
        target = (ROOT / unquote(parsed.path)).resolve()
        if target == SUMMARY.resolve() or target in seen:
            continue
        try:
            target.relative_to(ROOT)
        except ValueError as error:
            raise ValueError(f"Contents link escapes the book directory: {destination}") from error
        if not target.is_file():
            raise FileNotFoundError(f"Contents link points to a missing page: {destination}")
        seen.add(target)
        documents.append(target)
    if not documents:
        raise ValueError("No Markdown pages found in SUMMARY.md")
    return documents


def add_heading_ids(text: str, page_id: str) -> tuple[str, dict[str, str]]:
    """Prefix heading IDs so same-named sections remain unique across chapters."""
    output: list[str] = []
    headings: dict[str, str] = {}
    occurrences: dict[str, int] = {}
    fence_char: str | None = None
    fence_size = 0

    for line in text.splitlines(keepends=True):
        fence = FENCE.match(line)
        if fence:
            marker = fence.group(1)
            if fence_char is None:
                fence_char, fence_size = marker[0], len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_size:
                fence_char, fence_size = None, 0
            output.append(line)
            continue

        match = ATX_HEADING.match(line.rstrip("\r\n")) if fence_char is None else None
        if not match:
            output.append(line)
            continue

        indent, marks, title = match.groups()
        title = re.sub(r"\s+#+\s*$", "", title).strip()
        existing = re.search(r"\s+\{#([^}]+)\}\s*$", title)
        if existing:
            title_for_slug = title[: existing.start()].strip()
            old_id = existing.group(1)
        else:
            title_for_slug = title
            old_id = ""

        slug = slugify(old_id or title_for_slug)
        count = occurrences.get(slug, 0)
        occurrences[slug] = count + 1
        if count:
            slug = f"{slug}-{count}"
        new_id = f"{page_id}--{slug}"
        headings.setdefault("", new_id)
        headings[slugify(title_for_slug)] = new_id
        if old_id:
            headings[slugify(old_id)] = new_id
        newline = "\n" if line.endswith("\n") else ""
        output.append(f"{indent}{marks} {title_for_slug} {{#{new_id}}}{newline}")

    return "".join(output), headings


def local_link_target(
    destination: str,
    source: Path,
    page_ids: dict[Path, str],
    heading_ids: dict[Path, dict[str, str]],
) -> str | None:
    """Map a local Markdown link to an in-book anchor or a public source URL."""
    raw = destination.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1]
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc:
        return None

    path_text = unquote(parsed.path)
    fragment = unquote(parsed.fragment)
    if not path_text and not fragment:
        return None

    target = (source.parent / path_text).resolve() if path_text else source.resolve()
    if target == SUMMARY.resolve():
        target = (ROOT / "README.md").resolve()
    if target.is_dir():
        target = (target / "README.md").resolve()

    if target in page_ids:
        page_id = page_ids[target]
        if fragment:
            heading_id = heading_ids[target].get(slugify(fragment))
            if heading_id:
                return f"#{heading_id}"
        return f"#{heading_ids[target].get('', page_id)}"

    try:
        relative = target.relative_to(ROOT).as_posix()
    except ValueError:
        return None
    url = f"{REPOSITORY}/blob/main/{quote(relative, safe='/-_.~')}"
    if parsed.fragment:
        url += f"#{quote(fragment, safe='-._~')}"
    return url


def rewrite_line_links(
    line: str,
    source: Path,
    page_ids: dict[Path, str],
    heading_ids: dict[Path, dict[str, str]],
) -> str:
    output: list[str] = []
    index = 0
    while index < len(line):
        if line[index] == "`":
            run_end = index + 1
            while run_end < len(line) and line[run_end] == "`":
                run_end += 1
            run = line[index:run_end]
            closing = line.find(run, run_end)
            if closing >= 0:
                output.append(line[index : closing + len(run)])
                index = closing + len(run)
                continue

        if line[index] != "[" or (index > 0 and line[index - 1] == "!"):
            output.append(line[index])
            index += 1
            continue

        label_end = index + 1
        escaped = False
        while label_end < len(line):
            char = line[label_end]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "]":
                break
            label_end += 1
        if label_end + 1 >= len(line) or line[label_end + 1] != "(":
            output.append(line[index])
            index += 1
            continue

        dest_start = label_end + 2
        content_end = dest_start
        depth = 0
        escaped = False
        while content_end < len(line):
            char = line[content_end]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
            content_end += 1
        if content_end >= len(line):
            output.append(line[index])
            index += 1
            continue

        content = line[dest_start:content_end]
        leading = len(content) - len(content.lstrip())
        token_end = content.find(" ", leading)
        if token_end < 0:
            token_end = len(content)
        token = content[leading:token_end]
        replacement = local_link_target(token, source, page_ids, heading_ids)
        output.append(line[index : dest_start + leading])
        output.append(replacement if replacement is not None else token)
        output.append(line[dest_start + token_end : content_end + 1])
        index = content_end + 1

    return "".join(output)


def prepare_documents(
    documents: list[Path], temp_dir: Path
) -> tuple[list[Path], dict[Path, str]]:
    page_ids: dict[Path, str] = {}
    heading_ids: dict[Path, dict[str, str]] = {}
    prepared_text: dict[Path, str] = {}

    for number, path in enumerate(documents, 1):
        page_id = f"page-{number:03d}-{slugify(path.stem)}"
        page_ids[path.resolve()] = page_id
        source_text = path.read_text(encoding="utf-8")
        if path.resolve() == (ROOT / "Challenges" / "Answer_Key.md").resolve():
            # Disclosure widgets are useful online but are closed by default in
            # print/PDF and can become malformed when EPUB chapters are split.
            source_text = re.sub(
                r"<details>\s*<summary>\s*(.*?)\s*</summary>",
                lambda match: f"## {match.group(1).strip()}\n\n",
                source_text,
                flags=re.DOTALL,
            )
            source_text = re.sub(r"</?details>", "", source_text)
        text, ids = add_heading_ids(source_text, page_id)
        heading_ids[path.resolve()] = ids
        prepared_text[path.resolve()] = text

    prepared_paths: list[Path] = []
    for number, path in enumerate(documents, 1):
        source = path.resolve()
        text = prepared_text[source]
        rewritten = ""
        fence_char: str | None = None
        fence_size = 0
        for line in text.splitlines(keepends=True):
            fence = FENCE.match(line)
            if fence:
                marker = fence.group(1)
                if fence_char is None:
                    fence_char, fence_size = marker[0], len(marker)
                elif marker[0] == fence_char and len(marker) >= fence_size:
                    fence_char, fence_size = None, 0
                rewritten += line
            elif fence_char is None:
                rewritten += rewrite_line_links(line, source, page_ids, heading_ids)
            else:
                rewritten += line

        prepared = temp_dir / f"chapter-{number:03d}.md"
        prepared.write_text(rewritten, encoding="utf-8")
        prepared_paths.append(prepared)
    return prepared_paths, page_ids


def run(command: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode:
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {command[0]}")


def build(output_dir: Path) -> tuple[Path, Path, Path]:
    pandoc = shutil.which("pandoc")
    chromium = shutil.which("chromium") or shutil.which("chromium-browser")
    if not pandoc:
        raise RuntimeError("Pandoc is required to build editions (Debian: sudo apt install pandoc).")
    if not chromium:
        raise RuntimeError("Chromium is required for PDF output (Debian: sudo apt install chromium).")
    for asset in (CSS, COVER_SVG):
        if not asset.is_file():
            raise FileNotFoundError(asset)

    documents = reading_order()
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / PDF_NAME
    epub_path = output_dir / EPUB_NAME
    cover_path = output_dir / COVER_NAME

    with tempfile.TemporaryDirectory(prefix="raspberry-pi-book-") as temporary:
        temp_dir = Path(temporary)
        prepared_paths, _ = prepare_documents(documents, temp_dir)
        shutil.copyfile(CSS, temp_dir / "book.css")
        shutil.copyfile(COVER_SVG, temp_dir / "book-cover.svg")
        cover_fragment = temp_dir / "cover.html"
        cover_fragment.write_text(
            '<div class="book-cover">\n'
            '<img src="book-cover.svg" alt="Book cover featuring the ASCII Coffee Pot Snake">\n'
            '</div>\n',
            encoding="utf-8",
        )
        profile = temp_dir / "chromium-profile"
        run(
            [
                chromium,
                "--headless",
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                "--window-size=1600,2400",
                f"--user-data-dir={profile}-cover",
                f"--screenshot={cover_path}",
                (temp_dir / "book-cover.svg").as_uri(),
            ]
        )
        metadata = [
            "--metadata",
            f"title={TITLE}",
            "--metadata",
            f"author={AUTHOR}",
            "--metadata",
            f"publisher={PUBLISHER}",
            "--metadata",
            "lang=en",
            "--metadata",
            f"identifier={REPOSITORY}",
        ]
        common = [
            "--from=markdown",
            "--toc",
            "--toc-depth=3",
            "--resource-path",
            f"{temp_dir}:{ROOT}",
            *metadata,
        ]

        html_path = temp_dir / "book.html"
        run(
            [
                pandoc,
                *common,
                "--to=html5",
                "--standalone",
                "--css=book.css",
                f"--include-before-body={cover_fragment}",
                "--output",
                str(html_path),
                *(str(path) for path in prepared_paths),
            ]
        )

        run(
            [
                chromium,
                "--headless",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--no-pdf-header-footer",
                f"--user-data-dir={profile}",
                f"--print-to-pdf={pdf_path}",
                html_path.as_uri(),
            ]
        )

        run(
            [
                pandoc,
                *common,
                "--to=epub3",
                "--split-level=1",
                f"--css={temp_dir / 'book.css'}",
                f"--epub-cover-image={cover_path}",
                "--output",
                str(epub_path),
                *(str(path) for path in prepared_paths),
            ]
        )

    if not pdf_path.is_file() or not pdf_path.read_bytes().startswith(b"%PDF-"):
        raise RuntimeError("Chromium did not produce a valid PDF file.")
    if not epub_path.is_file():
        raise RuntimeError("Pandoc did not produce an EPUB file.")
    if not cover_path.is_file() or not cover_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("Chromium did not produce a valid PNG cover image.")
    with zipfile.ZipFile(epub_path) as archive:
        bad_member = archive.testzip()
        if bad_member:
            raise RuntimeError(f"EPUB ZIP archive is corrupt at {bad_member}.")
    return pdf_path, epub_path, cover_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "downloads",
        help="directory for the generated editions (default: downloads/)",
    )
    args = parser.parse_args()
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    try:
        pdf_path, epub_path, cover_path = build(output_dir)
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PDF:  {pdf_path.relative_to(ROOT) if pdf_path.is_relative_to(ROOT) else pdf_path}")
    print(f"EPUB: {epub_path.relative_to(ROOT) if epub_path.is_relative_to(ROOT) else epub_path}")
    print(f"Cover: {cover_path.relative_to(ROOT) if cover_path.is_relative_to(ROOT) else cover_path}")
    print(f"Included {len(reading_order())} Markdown pages in SUMMARY.md order.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
