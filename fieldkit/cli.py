"""Command-line interface for the original, offline-first FieldKit utilities."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
from pathlib import Path

from . import __version__
from .coffee_snake import generate as generate_cover, make_seed
from .core import (
    FieldKitError,
    append_issuance_record,
    create_manifest,
    local_inventory,
    scrub_file,
    verify_issuance_ledger,
    verify_manifest,
    write_new_private_file,
)
from .portal_client import PortalClientError, bootstrap, create_edition, download_standalone


def _manifest_command(args: argparse.Namespace) -> int:
    if args.manifest_action == "create":
        manifest = create_manifest(args.root, args.output)
        print(f"Wrote SHA-256 manifest for {len(manifest['files'])} files: {args.output}")
        return 0
    problems = verify_manifest(args.root, args.manifest)
    if problems:
        for problem in problems:
            print(f"MISMATCH: {problem}", file=sys.stderr)
        return 1
    print("Manifest verified: every listed file matches its size and SHA-256 digest.")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fieldkit",
        description="Offline-first, read-only-by-default field-support utilities.",
    )
    parser.add_argument("--version", action="version", version=f"FieldKit {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    inventory = sub.add_parser("inventory", help="print a minimal local OS/device inventory")
    inventory.add_argument("--output", type=Path, help="create a new private JSON file; never overwrite")

    scrub = sub.add_parser("scrub-report", help="write a redacted copy of a text report")
    scrub.add_argument("input", type=Path)
    scrub.add_argument("output", type=Path)
    scrub.add_argument(
        "--redact-network",
        action="store_true",
        help="also redact IPv4 and MAC-looking strings; review for false positives",
    )

    manifest = sub.add_parser("manifest", help="create or verify a local SHA-256 manifest")
    manifest_sub = manifest.add_subparsers(dest="manifest_action", required=True)
    create = manifest_sub.add_parser("create", help="hash regular files without following symlinks")
    create.add_argument("root", type=Path)
    create.add_argument("output", type=Path)
    verify = manifest_sub.add_parser("verify", help="compare files with a saved manifest")
    verify.add_argument("root", type=Path)
    verify.add_argument("manifest", type=Path)

    ledger = sub.add_parser("ledger", help="verify or append to a local tamper-evident edition ledger")
    ledger_sub = ledger.add_subparsers(dest="ledger_action", required=True)
    ledger_verify = ledger_sub.add_parser("verify", help="verify a local hash chain")
    ledger_verify.add_argument("path", type=Path)
    ledger_append = ledger_sub.add_parser("append", help="append an edition fingerprint")
    ledger_append.add_argument("path", type=Path)
    ledger_append.add_argument("edition_id")
    ledger_append.add_argument("artifact_sha256")

    cover = sub.add_parser("cover", help="generate local Coffee Pot Snake ASCII/SVG cover art")
    cover.add_argument("--seed", help="hexadecimal seed for reproducible art; random by default")
    cover.add_argument("--output-dir", type=Path, default=Path("."))

    portal = sub.add_parser("portal", help="obtain and download a personalized CPIP edition")
    portal_sub = portal.add_subparsers(dest="portal_action", required=True)
    starter = portal_sub.add_parser("bootstrap", help="solve the public starter puzzle and obtain a Coffee Cipher")
    starter.add_argument("--origin", help="HTTPS CPIP Book Portal origin; defaults to CPIP_BOOK_PORTAL_ORIGIN")
    starter.add_argument("--output", type=Path, help="private cipher file; never overwrite")
    edition = portal_sub.add_parser("edition", help="request a personalized PDF/EPUB using a Coffee Cipher")
    edition.add_argument("--profile", required=True, help="edition profile from the CPIP portal")
    edition.add_argument("--cipher-file", type=Path, help="private file from `fieldkit portal bootstrap`; otherwise prompt")
    edition.add_argument("--origin", help="HTTPS CPIP Book Portal origin; defaults to CPIP_BOOK_PORTAL_ORIGIN")
    edition.add_argument("--output-dir", type=Path, default=Path("."))
    app = portal_sub.add_parser("app", help="download a standalone FieldKit binary from the CPIP portal")
    app.add_argument("--target", required=True, choices=("linux-arm64", "linux-x86_64", "windows-x86_64", "macos-arm64", "macos-x86_64"))
    app.add_argument("--cipher-file", type=Path, help="private Coffee Cipher file; otherwise prompt")
    app.add_argument("--origin", help="HTTPS CPIP Book Portal origin; defaults to CPIP_BOOK_PORTAL_ORIGIN")
    app.add_argument("--output-dir", type=Path, default=Path("."))

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "inventory":
            data = local_inventory()
            encoded = (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
            if args.output:
                write_new_private_file(args.output, encoded)
                print(f"Wrote local inventory to {args.output}")
            else:
                sys.stdout.buffer.write(encoded)
            return 0
        if args.command == "scrub-report":
            line_count = scrub_file(args.input, args.output, redact_network=args.redact_network)
            print(f"Wrote {line_count} sanitized lines to {args.output}; inspect before sharing.")
            return 0
        if args.command == "manifest":
            return _manifest_command(args)
        if args.command == "ledger":
            if args.ledger_action == "verify":
                problems = verify_issuance_ledger(args.path)
                if problems:
                    for problem in problems:
                        print(f"INVALID: {problem}", file=sys.stderr)
                    return 1
                print("Local issuance hash chain verified.")
                return 0
            block = append_issuance_record(args.path, args.edition_id, args.artifact_sha256)
            print(f"Appended local ledger block {block['index']}: {block['hash']}")
            return 0
        if args.command == "cover":
            paths = generate_cover(args.output_dir, make_seed(args.seed))
            for path in paths:
                print(path)
            return 0
        if args.command == "portal":
            if args.portal_action == "bootstrap":
                answer = input("Starter puzzle answer: ").strip()
                cipher = bootstrap(answer, origin=args.origin)
                output = args.output or (Path.home() / ".local" / "share" / "fieldkit" / "starter-cipher.txt")
                write_new_private_file(output, (cipher + "\n").encode("utf-8"))
                print(f"Coffee Cipher saved with owner-only permissions: {output}")
                return 0
            if args.cipher_file:
                path = args.cipher_file.expanduser()
                if path.is_symlink() or not path.is_file():
                    raise FieldKitError("Cipher file must be a regular file, not a symlink.")
                if os.name != "nt" and path.stat().st_mode & 0o077:
                    raise FieldKitError("Cipher file is readable by group/others; restrict its permissions first.")
                cipher = path.read_text(encoding="utf-8").strip()
            else:
                cipher = getpass.getpass("Coffee Cipher (input hidden): ").strip()
            if args.portal_action == "app":
                path = download_standalone(args.target, cipher, args.output_dir, origin=args.origin)
                print(f"FieldKit standalone bundle: {path}")
                return 0
            result = create_edition(cipher, args.profile, args.output_dir, origin=args.origin)
            print(f"Edition: {result['edition_id']}")
            for kind, item in result["files"].items():
                print(f"{kind.upper()}: {item['path']} (SHA-256 {item['sha256']})")
            print(f"Next edition cipher: {args.output_dir / result['edition_id'] / 'coffee-cipher.txt'}")
            return 0
    except (FieldKitError, PortalClientError, OSError, ValueError) as error:
        print(f"fieldkit: {error}", file=sys.stderr)
        return 2
    parser.error("unknown command")
    return 2
