#!/usr/bin/env python3
"""Dependency-free checks for this Markdown book.

Checks local Markdown links and empty maintained pages. Bash snippets are parsed
with ``bash -n`` only; they are never executed.
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
LEGACY_DIRS = {
    "2. Exploitation Tools",
    "3. Forensics Tools",
    "4. Hardware Hacking",
    "5. Information Gathering",
    "6. Maintaining Access",
    "7. Password Attacks",
    "8. Reporting Tools",
    "9. Reverse Engineering",
    "10. Sniffing & Spoofing",
    "11. Stress Testing",
    "12. Web Applications",
    "13. Wireless Attacks",
    "14. Useful Github Repositories",
    "15. Conclusion",
    "Miscellaneous",
}
LINK_START = re.compile(r"!?\[[^\]]*\]\(")


def markdown_destinations(text: str):
    """Yield inline Markdown link destinations, including balanced parentheses."""
    cursor = 0
    while match := LINK_START.search(text, cursor):
        index = match.end()
        while index < len(text) and text[index].isspace():
            index += 1

        if index >= len(text):
            break

        if text[index] == "<":
            end = text.find(">", index + 1)
            if end < 0:
                cursor = index + 1
                continue
            destination = text[index + 1 : end]
            cursor = end + 1
            yield destination
            continue

        start = index
        depth = 0
        escaped = False
        while index < len(text):
            char = text[index]
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
            elif char.isspace() and depth == 0:
                break
            index += 1

        destination = text[start:index].replace("\\ ", " ")
        cursor = index + 1
        if destination:
            yield destination


def maintained_markdown(include_legacy: bool) -> list[Path]:
    documents = []
    for path in sorted(ROOT.rglob("*.md")):
        relative = path.relative_to(ROOT)
        if not include_legacy and relative.parts and relative.parts[0] in LEGACY_DIRS:
            continue
        documents.append(path)
    return documents


def local_target(source: Path, destination: str) -> Path | None:
    destination = html.unescape(destination)
    parsed = urlsplit(destination)
    if parsed.scheme or parsed.netloc or destination.startswith("#"):
        return None

    path_text = unquote(parsed.path)
    if not path_text:
        target = source
    elif path_text.startswith("/"):
        target = ROOT / path_text.lstrip("/")
    else:
        target = source.parent / path_text

    target = target.resolve()
    if target.is_dir():
        target = target / "README.md"
    return target


def check_links(documents: list[Path]) -> list[str]:
    errors = []
    for source in documents:
        text = source.read_text(encoding="utf-8")
        for destination in markdown_destinations(text):
            target = local_target(source, destination)
            if target is None:
                continue
            try:
                target.relative_to(ROOT)
            except ValueError:
                errors.append(f"{source.relative_to(ROOT)}: link escapes repository: {destination}")
                continue
            if not target.exists():
                errors.append(f"{source.relative_to(ROOT)}: missing local target: {destination}")
    return errors


def check_shell(documents: list[Path]) -> tuple[list[str], int]:
    bash = shutil.which("bash")
    if not bash:
        return ["bash not found; unable to syntax-check Bash fences"], 0

    errors = []
    checked = 0
    for source in documents:
        text = source.read_text(encoding="utf-8")
        lines = text.splitlines()
        index = 0
        while index < len(lines):
            opening = re.match(r"^\s*```(?:bash|sh)\s*$", lines[index])
            if not opening:
                index += 1
                continue
            index += 1
            block = []
            while index < len(lines) and not re.match(r"^\s*```\s*$", lines[index]):
                block.append(lines[index])
                index += 1
            result = subprocess.run(
                [bash, "-n"],
                input="\n".join(block) + "\n",
                capture_output=True,
                text=True,
                check=False,
            )
            checked += 1
            if result.returncode:
                detail = result.stderr.strip().replace("\n", " ")
                errors.append(f"{source.relative_to(ROOT)}: invalid shell snippet: {detail}")
            index += 1
    return errors, checked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-legacy",
        action="store_true",
        help="also check the unreviewed historical catalog",
    )
    parser.add_argument(
        "--no-shell-check",
        action="store_true",
        help="skip Bash syntax validation",
    )
    args = parser.parse_args()

    documents = maintained_markdown(args.include_legacy)
    errors = []
    empty = [path for path in documents if not path.read_text(encoding="utf-8").strip()]
    errors.extend(f"{path.relative_to(ROOT)}: maintained Markdown page is empty" for path in empty)
    errors.extend(check_links(documents))

    shell_count = 0
    if not args.no_shell_check:
        shell_errors, shell_count = check_shell(documents)
        errors.extend(shell_errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Failed: {len(errors)} issue(s) across {len(documents)} maintained Markdown pages.")
        return 1

    print(
        f"OK: {len(documents)} maintained Markdown pages; "
        f"local links resolved; {shell_count} Bash snippets syntax-checked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
