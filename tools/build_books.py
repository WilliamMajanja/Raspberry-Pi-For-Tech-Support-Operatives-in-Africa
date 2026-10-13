#!/usr/bin/env python3
"""Build linked PDF and EPUB editions from the book's SUMMARY.md reading order.

Optional build tools: Pandoc and Chromium. Reading the Markdown book itself
requires no build tools or installed packages.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
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
PRINTABLES_NAME = "field-hackathon-printables.zip"
PROFILE_PATHS = {
    "field-technician": "Prioritized sequence: Pi field support, Linux foundations, then FieldKit recipes; all other reference chapters follow.",
    "operations-lead": "Prioritized sequence: field operations, incident triage, safeguarding, and service continuity; all other reference chapters follow.",
    "informatics-practitioner": "Prioritized sequence: data stewardship, public-interest Informatics, privacy, and source evaluation; all other reference chapters follow.",
    "facilitator": "Prioritized sequence: offline challenges, facilitator guidance, and role boundaries; all other reference chapters follow.",
}
PROFILE_PRIORITY_PATHS = {
    "field-technician": (
        "Raspberry Pi Field Support/README.md",
        "Raspberry Pi Field Support/Imaging_and_First_Boot.md",
        "Raspberry Pi Field Support/Support_Playbooks.md",
        "Raspberry Pi Field Support/Field_Operations.md",
        "0. Linux Foundations/README.md",
        "0. Linux Foundations/Files_Users_and_Permissions.md",
        "0. Linux Foundations/Networking_Basics.md",
        "0. Linux Foundations/Services_Logs_and_Recovery.md",
        "Raspberry Pi Field Support/FieldKit.md",
        "Raspberry Pi Field Support/Security_Assessment_Playbook.md",
    ),
    "operations-lead": (
        "Raspberry Pi Field Support/Field_Operations.md",
        "Raspberry Pi Field Support/Support_Playbooks.md",
        "Peace Operations Field Support/README.md",
        "Peace Operations Field Support/Child_Protection_and_WPS.md",
        "Peace Operations Field Support/Mine_Action_and_Explosive_Hazards.md",
        "Raspberry Pi Field Support/Security_Assessment_Playbook.md",
        "Informatics and Public Interest/README.md",
        "Raspberry Pi Field Support/FieldKit.md",
    ),
    "informatics-practitioner": (
        "Informatics and Public Interest/README.md",
        "Peace Operations Field Support/Child_Protection_and_WPS.md",
        "Peace Operations Field Support/Mine_Action_and_Explosive_Hazards.md",
        "Peace Operations Field Support/Security_Council_Resolution_Reference.md",
        "0. Linux Foundations/Networking_Basics.md",
        "0. Linux Foundations/Files_Users_and_Permissions.md",
        "Raspberry Pi Field Support/FieldKit.md",
        "Challenges/README.md",
    ),
    "facilitator": (
        "Challenges/README.md",
        "Challenges/Coffee_Pot_Snake_Cryptex.md",
        "1. Introduction/Structure_of_the_book.md",
        "Raspberry Pi Field Support/README.md",
        "Raspberry Pi Field Support/Support_Playbooks.md",
        "Peace Operations Field Support/Child_Protection_and_WPS.md",
        "0. Linux Foundations/README.md",
        "Raspberry Pi Field Support/FieldKit.md",
    ),
}
PROFILE_CHALLENGES = {
    "field-technician": (
        "The device has a wireless link and a local address, but no expected default route. Write the next two read-only checks, the network owner to consult, and a stop condition. Do not probe other devices.",
        "A support Pi failed during a storage write and may hold the only copy of synthetic training data. Order the preservation, diagnosis, recovery, and handover steps.",
        "A service fails after an update on a fictional Debian host. Separate system identity, service status, logs, and rollback checks without changing state first.",
    ),
    "operations-lead": (
        "A field site expects a support device to return after a power interruption. Draft a short handover covering ownership, backup status, authorized access, and the next review date.",
        "Two support requests conflict: restore service quickly or preserve evidence of a suspected change. Define approval, impact, stop conditions, and a reversible first action.",
        "A deployment loses connectivity for a day. Prioritize the offline reference copy, staff roles, privacy controls, and synchronization reconciliation plan.",
    ),
    "informatics-practitioner": (
        "A dashboard combines records from two sources with different dates and confidence levels. Specify the provenance fields and validation steps before anyone uses its output.",
        "A prototype sends data to an external API while its description claims local-only processing. Map the data flow, identify what must be verified, and propose a synthetic-data test.",
        "A public report contains precise location and case details. Propose a minimal, role-restricted, correction-capable publication workflow.",
    ),
    "facilitator": (
        "Plan a 30-minute offline exercise where learners diagnose an address, route, and name-resolution problem from printed observations only.",
        "Create a handover role-play in which one learner is the device owner, one is the support operative, and one checks privacy and change-control boundaries.",
        "Ask learners to compare a source claim, a local test result, and an unverified assumption; have them label each before drafting a safe recommendation.",
    ),
}
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
    expected = {
        path.resolve()
        for path in ROOT.rglob("*.md")
        if path.resolve() != SUMMARY.resolve()
    }
    missing = sorted(expected - seen)
    if missing:
        names = ", ".join(path.relative_to(ROOT).as_posix() for path in missing)
        raise ValueError(f"SUMMARY.md omits repository Markdown pages: {names}")
    return documents


def prioritize_reading_order(documents: list[Path], profile: str) -> list[Path]:
    """Move a profile's recommended pages to the front without omitting content."""
    if profile not in PROFILE_PRIORITY_PATHS:
        raise ValueError("unknown edition profile")
    by_relative_path = {path.relative_to(ROOT).as_posix(): path for path in documents}
    priority = [by_relative_path[name] for name in PROFILE_PRIORITY_PATHS[profile] if name in by_relative_path]
    priority_set = set(priority)
    return [*priority, *(path for path in documents if path not in priority_set)]


def source_files() -> list[Path]:
    """Return authored non-Markdown source/configuration files for the source appendix."""
    candidates = [ROOT / ".gitignore", ROOT / "LICENSE", ROOT / "fieldkit_launcher.py"]
    candidates.extend((ROOT / "LICENSES").glob("*.txt"))
    candidates.extend((ROOT / "fieldkit").rglob("*.py"))
    candidates.extend((ROOT / "portal").rglob("*.py"))
    candidates.extend((ROOT / "Challenges").glob("*.scad"))
    candidates.extend((ROOT / "Challenges").glob("*.svg"))
    candidates.extend((ROOT / "illustrations").rglob("*.svg"))
    candidates.extend((ROOT / "portal").glob("*.example"))
    candidates.extend((ROOT / "portal").glob("*.sample"))
    candidates.extend((ROOT / "portal").glob("*.txt"))
    candidates.extend((ROOT / "tests").rglob("*.py"))
    candidates.extend((ROOT / "tools").glob("*.py"))
    candidates.extend((ROOT / "tools").glob("*.txt"))
    candidates.extend((ROOT / "tools").glob("*.css"))
    candidates.extend((ROOT / "tools").glob("*.svg"))
    candidates.extend((ROOT / ".github" / "workflows").glob("*.yml"))
    return sorted({path.resolve() for path in candidates if path.is_file() and not path.is_symlink()})


def make_source_appendix(temp_dir: Path) -> Path:
    """Embed source/configuration text, but not generated binary book artifacts."""
    lines = [
        "# Appendix: Complete Source Listings",
        "",
        "This appendix is generated from the exact source tree used for this edition. It excludes the PDF/EPUB outputs themselves and includes only text assets and sample configuration. Sample files contain placeholders, never production keys.",
        "",
    ]
    for path in source_files():
        relative = path.relative_to(ROOT).as_posix()
        suffix = path.suffix.lower()
        language = {
            ".py": "python",
            ".css": "css",
            ".svg": "xml",
            ".txt": "text",
            ".sample": "text",
            ".example": "text",
        }.get(suffix, "text")
        if path.name == ".gitignore":
            language = "text"
        content = path.read_text(encoding="utf-8")
        longest_backticks = max((len(match.group(0)) for match in re.finditer(r"`+", content)), default=0)
        fence = "`" * max(4, longest_backticks + 1)
        lines.extend([f"## `{relative}`", "", f"{fence}{language}", content.rstrip("\n"), fence, ""])
    appendix = temp_dir / "source-appendix.md"
    appendix.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return appendix


def build_printables_bundle(output_dir: Path) -> Path:
    """Package source worksheets and the native-size A4 SVG without rescaling."""
    files = (
        (ROOT / "Challenges" / "Coffee_Pot_Snake_Paper_Cryptex.svg", "printables/Coffee_Pot_Snake_Paper_Cryptex.svg"),
        (ROOT / "Hackathon" / "Participant_FieldKit_Worksheet.md", "printables/Participant_FieldKit_Worksheet.md"),
        (ROOT / "Raspberry Pi Field Support" / "Security_Assessment_Playbook.md", "printables/Security_Assessment_Playbook.md"),
        (ROOT / "Peace Operations Field Support" / "Data_Stewardship_and_Offline_Systems.md", "printables/Data_Stewardship_and_Offline_Systems.md"),
        (ROOT / "Informatics and Public Interest" / "Researching_Public_Harm_and_Accountability.md", "printables/Researching_Public_Harm_and_Accountability.md"),
    )
    for source, _archive_name in files:
        if source.is_symlink() or not source.is_file():
            raise FileNotFoundError(f"Required printable is missing or unsafe: {source}")
    output_dir.mkdir(parents=True, exist_ok=True)
    bundle = output_dir / PRINTABLES_NAME
    readme = (
        "Field hackathon printable pack\n"
        "The cryptex SVG is A4 at intrinsic 210 x 297 mm. Print at 100% / actual size; disable fit-to-page.\n"
        "Markdown worksheets are readable offline and may be printed from a Markdown editor. Use synthetic data only.\n"
        "Official CPIP editions include this pack in the publisher-signed manifest. Verify before use.\n"
    ).encode("utf-8")
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        entries = [(None, "printables/README.txt", readme), *[(source, name, None) for source, name in files]]
        for source, name, content in entries:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100600 << 16
            archive.writestr(info, content if content is not None else source.read_bytes())
    with zipfile.ZipFile(bundle) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Printable pack failed ZIP integrity validation.")
    return bundle


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


def local_image_target(destination: str, source: Path) -> str | None:
    """Copy a local image reference to a safe path under the book build root."""
    raw = destination.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1]
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    target = (source.parent / unquote(parsed.path)).resolve()
    try:
        relative = target.relative_to(ROOT).as_posix()
    except ValueError:
        return None
    if not target.is_file() or target.is_symlink():
        return None
    return relative + (f"#{quote(unquote(parsed.fragment), safe='-._~')}" if parsed.fragment else "")


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

        is_image = line[index] == "!" and index + 1 < len(line) and line[index + 1] == "["
        label_start = index + 1 if is_image else index
        if line[label_start] != "[" or (index > 0 and line[index - 1] == "!"):
            output.append(line[index])
            index += 1
            continue

        label_end = label_start + 1
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
        replacement = (
            local_image_target(token, source)
            if is_image
            else local_link_target(token, source, page_ids, heading_ids)
        )
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


def build(
    output_dir: Path,
    edition_id: str | None = None,
    edition_profile: str | None = None,
    edition_cipher: str | None = None,
    cover_seed: str | None = None,
    signing_key_fingerprint: str | None = None,
    source_revision: str | None = None,
) -> tuple[Path, Path, Path, Path]:
    pandoc = shutil.which("pandoc")
    chromium = shutil.which("chromium") or shutil.which("chromium-browser")
    if not pandoc:
        raise RuntimeError("Pandoc is required to build editions (Debian: sudo apt install pandoc).")
    if not chromium:
        raise RuntimeError("Chromium is required for PDF output (Debian: sudo apt install chromium).")
    for asset in (CSS, COVER_SVG):
        if not asset.is_file():
            raise FileNotFoundError(asset)

    if edition_id:
        if not re.fullmatch(r"[a-f0-9]{24}", edition_id):
            raise ValueError("edition ID must be 24 lowercase hexadecimal characters")
        if edition_profile not in PROFILE_PATHS:
            raise ValueError("unknown edition profile")
        if not edition_cipher or len(edition_cipher) > 16_384 or not re.fullmatch(r"[A-Za-z0-9;=,._ -]+", edition_cipher):
            raise ValueError("edition cipher must be a single-line CPIP additions value")
        if not cover_seed or not re.fullmatch(r"[a-f0-9]{64}", cover_seed):
            raise ValueError("personalized editions require a 32-byte hexadecimal cover seed")
        if not signing_key_fingerprint or not re.fullmatch(r"[a-f0-9]{64}", signing_key_fingerprint):
            raise ValueError("personalized editions require the publisher Ed25519 key fingerprint")
        if not source_revision or not re.fullmatch(r"[a-f0-9]{40}", source_revision):
            raise ValueError("personalized editions require the exact 40-character source commit SHA")
    elif edition_profile or edition_cipher or cover_seed or signing_key_fingerprint or source_revision:
        raise ValueError("edition ID, profile, cipher, cover seed, signing fingerprint, and source revision must be supplied together")

    documents = reading_order()
    if edition_profile:
        documents = prioritize_reading_order(documents, edition_profile)
    output_dir.mkdir(parents=True, exist_ok=True)
    edition_suffix = f"-{edition_id}" if edition_id else ""
    pdf_path = output_dir / f"{Path(PDF_NAME).stem}{edition_suffix}.pdf"
    epub_path = output_dir / f"{Path(EPUB_NAME).stem}{edition_suffix}.epub"
    cover_path = output_dir / (f"cover-{edition_id}.png" if edition_id else COVER_NAME)

    with tempfile.TemporaryDirectory(prefix="raspberry-pi-book-") as temporary:
        temp_dir = Path(temporary)
        illustrations = ROOT / "illustrations"
        if illustrations.is_dir():
            shutil.copytree(illustrations, temp_dir / "illustrations")
        prepared_paths, _ = prepare_documents(documents, temp_dir)
        source_appendix = make_source_appendix(temp_dir)
        shutil.copyfile(CSS, temp_dir / "book.css")
        if edition_id:
            if str(ROOT) not in sys.path:
                sys.path.insert(0, str(ROOT))
            from fieldkit.coffee_snake import render_svg

            (temp_dir / "book-cover.svg").write_text(
                render_svg(bytes.fromhex(cover_seed), edition_id), encoding="utf-8"
            )
            edition_card = temp_dir / "edition-card.md"
            challenge_digest = hashlib.sha256(bytes.fromhex(cover_seed) + edition_profile.encode("ascii")).digest()
            exercise = PROFILE_CHALLENGES[edition_profile][int.from_bytes(challenge_digest[:4], "big") % len(PROFILE_CHALLENGES[edition_profile])]
            edition_card.write_text(
                "# Your Personalized Field-Book Edition\n\n"
                f"Edition ID: `{edition_id}`\n\n"
                f"Source revision: `{source_revision}`\n\n"
                f"Reader path: {PROFILE_PATHS[edition_profile]}\n\n"
                "## Your Field Exercise\n\n"
                f"{exercise}\n\n"
                "This edition places the recommended pages first; every reference page is still included. Technical facts, safety boundaries, citations, and core instructions are identical across profiles; only page order, this suggested path, the synthetic practice scenario, and the cover variation differ.\n\n"
                "## Coffee Cipher and signed edition manifest\n\n"
                "This per-edition CPIP cipher is a bearer code for the CPIP Book Portal. "
                "It is printed in this copy so you can use the portal; anyone who receives "
                "a copy can also read and share it. It is not DRM, a personal identity, or a "
                "secret suitable for protecting unrelated accounts. The cipher is a puzzle/portal "
                "credential only; it does not encrypt this book.\n\n"
                "The portal also supplies a detached Ed25519 signature over `edition-manifest.json`. "
                "The manifest binds the PDF, EPUB, and cover SHA-256 digests to this edition and source revision. "
                "Verify the signature and all hashes with FieldKit using the publisher’s independently published fingerprint. "
                "The Coffee Cipher is not the signature.\n\n"
                f"Publisher signing-key fingerprint: `{signing_key_fingerprint}`\n\n"
                "```text\n"
                f"{edition_cipher}\n"
                "```\n",
                encoding="utf-8",
            )
            prepared_paths.insert(0, edition_card)
        else:
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
            f"identifier={REPOSITORY}/edition/{edition_id}" if edition_id else f"identifier={REPOSITORY}",
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
                *(str(path) for path in [*prepared_paths, source_appendix]),
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
                *(str(path) for path in [*prepared_paths, source_appendix]),
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
    printables_path = build_printables_bundle(output_dir)
    return pdf_path, epub_path, cover_path, printables_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "build" / "preview",
        help="directory for local preview editions (default: build/preview/)",
    )
    parser.add_argument(
        "--edition-config",
        type=Path,
        help="private JSON config created by the CPIP portal; do not pass cipher material on the command line",
    )
    args = parser.parse_args()
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    try:
        edition = None
        if args.edition_config:
            config_path = args.edition_config.expanduser()
            if config_path.is_symlink() or not config_path.is_file() or config_path.stat().st_size > 64 * 1024:
                raise ValueError("edition config must be a small regular file, not a symlink")
            if os.name != "nt" and config_path.stat().st_mode & 0o077:
                raise ValueError("edition config must not be readable by group/others")
            edition = json.loads(config_path.read_text(encoding="utf-8"))
            if not isinstance(edition, dict):
                raise ValueError("edition config must be a JSON object")
            required = {"edition_id", "profile", "cipher", "cover_seed", "signing_key_fingerprint", "source_revision"}
            if set(edition) != required or not all(isinstance(edition[key], str) for key in required):
                raise ValueError("edition config must contain only string edition_id/profile/cipher/cover_seed fields")
        pdf_path, epub_path, cover_path, printables_path = build(
            output_dir,
            edition_id=edition.get("edition_id") if edition else None,
            edition_profile=edition.get("profile") if edition else None,
            edition_cipher=edition.get("cipher") if edition else None,
            cover_seed=edition.get("cover_seed") if edition else None,
            signing_key_fingerprint=edition.get("signing_key_fingerprint") if edition else None,
            source_revision=edition.get("source_revision") if edition else None,
        )
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PDF:  {pdf_path.relative_to(ROOT) if pdf_path.is_relative_to(ROOT) else pdf_path}")
    print(f"EPUB: {epub_path.relative_to(ROOT) if epub_path.is_relative_to(ROOT) else epub_path}")
    print(f"Cover: {cover_path.relative_to(ROOT) if cover_path.is_relative_to(ROOT) else cover_path}")
    print(f"Printables: {printables_path.relative_to(ROOT) if printables_path.is_relative_to(ROOT) else printables_path}")
    print(f"Included {len(reading_order())} Markdown pages in SUMMARY.md order.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
