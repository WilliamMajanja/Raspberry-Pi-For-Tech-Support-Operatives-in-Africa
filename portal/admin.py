"""Offline CPIP Book Portal administration: revoke ciphers or publish app bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import shutil
import stat
import sys
import zipfile
from pathlib import Path

from .book_portal import APP_TARGETS, PortalError, PortalStore


def _verify_app_bundle(target: str, bundle: Path, manifest_path: Path) -> tuple[str, str]:
    if target not in APP_TARGETS:
        raise PortalError("Unsupported standalone-app target.")
    for path in (bundle, manifest_path):
        if path.is_symlink() or not path.is_file():
            raise PortalError("Bundle and manifest must be regular files, not symlinks.")
    if bundle.stat().st_size > 256 * 1024 * 1024 or manifest_path.stat().st_size > 64 * 1024:
        raise PortalError("Bundle or manifest exceeds the configured size limit.")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise PortalError("App manifest is not valid JSON.") from error
    if manifest.get("target") != target:
        raise PortalError("Manifest target does not match the requested target.")
    if manifest.get("bundle") != bundle.name:
        raise PortalError("Manifest does not name the supplied bundle.")
    bundle_hash = hashlib.sha256(bundle.read_bytes()).hexdigest()
    if not hmac_compare(bundle_hash, str(manifest.get("bundle_sha256", ""))):
        raise PortalError("Standalone bundle digest does not match its manifest.")
    expected_binary = "fieldkit.exe" if target == "windows-x86_64" else "fieldkit"
    if manifest.get("binary") != expected_binary:
        raise PortalError("Manifest executable name does not match the target.")
    try:
        with zipfile.ZipFile(bundle) as archive:
            names = archive.namelist()
            if archive.testzip() is not None:
                raise PortalError("Standalone bundle ZIP is corrupt.")
            if any(name.startswith("/") or ".." in Path(name).parts for name in names):
                raise PortalError("Standalone bundle contains an unsafe path.")
            if any(stat.S_ISLNK(item.external_attr >> 16) for item in archive.infolist()):
                raise PortalError("Standalone bundle contains a symbolic link.")
            if expected_binary not in names:
                raise PortalError("Standalone bundle is missing its FieldKit executable.")
            required_notices = {
                "THIRD_PARTY_NOTICES.md",
                "LICENSES/CC0-1.0.txt",
                "LICENSES/CC0-SCOPE.md",
                "LICENSES/PyInstaller-COPYING.txt",
            }
            if not required_notices.issubset(set(names)):
                raise PortalError("Standalone bundle is missing license notices.")
            binary_hash = hashlib.sha256(archive.read(expected_binary)).hexdigest()
    except (zipfile.BadZipFile, KeyError) as error:
        raise PortalError("Standalone bundle is not a valid ZIP.") from error
    if not hmac_compare(binary_hash, str(manifest.get("binary_sha256", ""))):
        raise PortalError("FieldKit executable digest does not match its manifest.")
    return bundle_hash, expected_binary


def hmac_compare(left: str, right: str) -> bool:
    import hmac

    return hmac.compare_digest(left, right)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    revoke = actions.add_parser("revoke", help="revoke a cipher and all credentials for one edition ID")
    revoke.add_argument("edition_id")
    publish = actions.add_parser("publish-app", help="install a verified standalone bundle in the CPIP portal app directory")
    publish.add_argument("target", choices=sorted(APP_TARGETS))
    publish.add_argument("bundle", type=Path)
    publish.add_argument("manifest", type=Path)
    args = parser.parse_args()

    try:
        data_dir = Path(os.environ.get("CPIP_BOOK_DATA_DIR", str(Path.home() / ".local/share/cpip-book-portal")))
        pepper = os.environ.get("CPIP_BOOK_TOKEN_PEPPER", "").encode("utf-8")
        if len(pepper) < 32:
            raise PortalError("Set CPIP_BOOK_TOKEN_PEPPER via the protected service environment.")
        store = PortalStore(data_dir, pepper)
        if args.action == "revoke":
            count = store.revoke_edition_cipher(args.edition_id)
            if not count:
                print("No active cipher found for that edition ID.", file=sys.stderr)
                return 1
            print(f"Revoked {count} cipher credential(s) for edition {args.edition_id}.")
            print("Previously downloaded CC0 content remains readable and shareable; this revokes portal access only.")
            return 0

        if args.bundle.expanduser().is_symlink() or args.manifest.expanduser().is_symlink():
            raise PortalError("Bundle and manifest must not be symlinks.")
        bundle = args.bundle.expanduser().resolve(strict=True)
        manifest = args.manifest.expanduser().resolve(strict=True)
        bundle_hash, _binary_name = _verify_app_bundle(args.target, bundle, manifest)
        app_dir = Path(os.environ.get("CPIP_BOOK_APP_DIR", str(data_dir / "apps"))).expanduser()
        if app_dir.is_symlink():
            raise PortalError("Portal application directory must not be a symlink.")
        app_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(app_dir, 0o700)
        destination = app_dir.resolve() / APP_TARGETS[args.target]
        temporary = destination.with_name(f".{destination.name}.{secrets.token_hex(8)}.tmp")
        shutil.copyfile(bundle, temporary)
        os.chmod(temporary, 0o600)
        os.replace(temporary, destination)
        store.record_app_bundle(args.target, bundle_hash)
        print(f"Published verified {args.target} bundle: {destination}")
        return 0
    except (PortalError, OSError, ValueError) as error:
        print(f"portal-admin: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
