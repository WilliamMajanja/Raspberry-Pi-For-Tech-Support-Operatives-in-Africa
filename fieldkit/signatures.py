"""Ed25519 signing and verification for FieldKit edition packages.

The Coffee Cipher is a CPIP bearer credential. These signatures use a separate
publisher key and authenticate only the manifest and the files it hashes.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import os
import re
import stat
from pathlib import Path
from typing import Any
import zipfile


MANIFEST_NAME = "edition-manifest.json"
SIGNATURE_NAME = "edition-manifest.sig"
PUBLIC_KEY_NAME = "publisher-edition-key.pem"
MANIFEST_SCHEMA = "fieldkit-edition-manifest.v1"
MAX_MANIFEST_BYTES = 1024 * 1024
MAX_SIGNATURE_BYTES = 4096
MAX_PUBLIC_KEY_BYTES = 16 * 1024
MAX_ARTIFACT_BYTES = 128 * 1024 * 1024
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
EDITION_ID_RE = re.compile(r"^[a-f0-9]{24}$")


class EditionSignatureError(ValueError):
    """Edition manifest, signature, key, or artifact did not verify."""


def _crypto():
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
            Ed25519PublicKey,
        )
    except ImportError as error:
        raise EditionSignatureError(
            "Ed25519 verification requires the optional 'cryptography' package; use the standalone FieldKit or install the documented verifier dependency."
        ) from error
    return serialization, Ed25519PrivateKey, Ed25519PublicKey


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise EditionSignatureError("Manifest contains a duplicate JSON key.")
        result[key] = value
    return result


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def key_fingerprint(public_key: Any) -> str:
    serialization, _private_type, _public_type = _crypto()
    der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return hashlib.sha256(der).hexdigest()


def load_private_key(path: Path) -> Any:
    serialization, private_type, _public_type = _crypto()
    raw_path = path.expanduser()
    if raw_path.is_symlink() or not raw_path.is_file():
        raise EditionSignatureError("Publisher signing key must be a regular file, not a symlink.")
    if raw_path.stat().st_size > MAX_PUBLIC_KEY_BYTES:
        raise EditionSignatureError("Publisher signing key exceeds the size limit.")
    if os.name != "nt" and stat.S_IMODE(raw_path.stat().st_mode) & 0o077:
        raise EditionSignatureError("Publisher signing key must not be accessible to group or other users.")
    try:
        key = serialization.load_pem_private_key(raw_path.read_bytes(), password=None)
    except (ValueError, TypeError) as error:
        raise EditionSignatureError("Publisher signing key is not a valid unencrypted PEM key.") from error
    if not isinstance(key, private_type):
        raise EditionSignatureError("Publisher signing key must use Ed25519.")
    return key


def public_key_pem(private_key: Any) -> bytes:
    serialization, _private_type, _public_type = _crypto()
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def sign_manifest(payload: dict[str, Any], private_key: Any) -> tuple[bytes, bytes, bytes, str]:
    """Return canonical manifest bytes, base64 detached signature, PEM key, fingerprint."""
    fingerprint = key_fingerprint(private_key.public_key())
    signed_payload = dict(payload)
    signed_payload["schema"] = MANIFEST_SCHEMA
    signed_payload["signature_algorithm"] = "Ed25519"
    signed_payload["signing_key_fingerprint"] = fingerprint
    manifest = canonical_json_bytes(signed_payload)
    signature = base64.b64encode(private_key.sign(manifest)) + b"\n"
    return manifest, signature, public_key_pem(private_key), fingerprint


def verify_manifest_signature(
    manifest_bytes: bytes,
    signature_bytes: bytes,
    public_key_bytes: bytes,
    trusted_fingerprint: str,
) -> dict[str, Any]:
    """Verify canonical manifest bytes and the independently pinned Ed25519 key."""
    serialization, _private_type, public_type = _crypto()
    if not 0 < len(manifest_bytes) <= MAX_MANIFEST_BYTES:
        raise EditionSignatureError("Manifest is empty or exceeds the size limit.")
    if not 0 < len(signature_bytes) <= MAX_SIGNATURE_BYTES:
        raise EditionSignatureError("Signature is empty or exceeds the size limit.")
    if not 0 < len(public_key_bytes) <= MAX_PUBLIC_KEY_BYTES:
        raise EditionSignatureError("Public key is empty or exceeds the size limit.")
    try:
        payload = json.loads(
            manifest_bytes.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda _value: (_ for _ in ()).throw(EditionSignatureError("Manifest contains a non-finite number.")),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise EditionSignatureError("Manifest is not valid UTF-8 JSON.") from error
    if not isinstance(payload, dict) or canonical_json_bytes(payload) != manifest_bytes:
        raise EditionSignatureError("Manifest is not in the required canonical JSON format.")
    if payload.get("schema") != MANIFEST_SCHEMA or payload.get("signature_algorithm") != "Ed25519":
        raise EditionSignatureError("Manifest schema or signature algorithm is unsupported.")
    try:
        public_key = serialization.load_pem_public_key(public_key_bytes)
    except (ValueError, TypeError) as error:
        raise EditionSignatureError("Publisher public key is not a valid PEM key.") from error
    if not isinstance(public_key, public_type):
        raise EditionSignatureError("Publisher public key is not Ed25519.")
    actual_fingerprint = key_fingerprint(public_key)
    trusted = trusted_fingerprint.lower().removeprefix("sha256:").replace(":", "").strip()
    if not SHA256_RE.fullmatch(trusted) or not hmac.compare_digest(actual_fingerprint, trusted):
        raise EditionSignatureError("Publisher key fingerprint does not match the independently trusted fingerprint.")
    if payload.get("signing_key_fingerprint") != actual_fingerprint:
        raise EditionSignatureError("Manifest identifies a different publisher key.")
    if not EDITION_ID_RE.fullmatch(str(payload.get("edition_id", ""))):
        raise EditionSignatureError("Manifest has an invalid edition ID.")
    if not SHA256_RE.fullmatch(str(payload.get("coffee_cipher_sha256", ""))):
        raise EditionSignatureError("Manifest has an invalid Coffee Cipher digest.")
    if not re.fullmatch(r"[a-f0-9]{40}", str(payload.get("source_revision", ""))):
        raise EditionSignatureError("Manifest has an invalid source revision.")
    try:
        signature = base64.b64decode(signature_bytes.strip(), validate=True)
        public_key.verify(signature, manifest_bytes)
    except (binascii.Error, ValueError, TypeError) as error:
        raise EditionSignatureError("Detached Ed25519 signature is malformed.") from error
    except Exception as error:
        # cryptography exposes InvalidSignature as a dedicated exception.
        from cryptography.exceptions import InvalidSignature

        if isinstance(error, InvalidSignature):
            raise EditionSignatureError("Detached Ed25519 signature is invalid.") from error
        raise
    return payload


def verify_edition_directory(
    directory: Path,
    trusted_fingerprint: str,
    public_key_path: Path | None = None,
) -> dict[str, Any]:
    """Verify a downloaded sidecar signature and every artifact listed in it."""
    root = directory.expanduser()
    if root.is_symlink() or not root.is_dir():
        raise EditionSignatureError("Edition path must be a real directory, not a symlink.")
    root = root.resolve(strict=True)
    manifest_path = root / MANIFEST_NAME
    signature_path = root / SIGNATURE_NAME
    key_path = public_key_path.expanduser() if public_key_path else root / PUBLIC_KEY_NAME
    for path in (manifest_path, signature_path, key_path):
        if path.is_symlink() or not path.is_file():
            raise EditionSignatureError(f"Required signature file is missing or unsafe: {path.name}")
    limits = (MAX_MANIFEST_BYTES, MAX_SIGNATURE_BYTES, MAX_PUBLIC_KEY_BYTES)
    for path, limit in zip((manifest_path, signature_path, key_path), limits):
        if path.stat().st_size > limit:
            raise EditionSignatureError(f"Signature file exceeds the size limit: {path.name}")
    payload = verify_manifest_signature(
        manifest_path.read_bytes(),
        signature_path.read_bytes(),
        key_path.read_bytes(),
        trusted_fingerprint,
    )
    if not EDITION_ID_RE.fullmatch(str(payload.get("edition_id", ""))):
        raise EditionSignatureError("Manifest has an invalid edition ID.")
    if payload.get("profile") not in {
        "field-technician",
        "operations-lead",
        "informatics-practitioner",
        "facilitator",
    }:
        raise EditionSignatureError("Manifest has an unknown reader profile.")
    artifacts = payload.get("artifacts")
    required_artifacts = {"pdf", "epub", "cover", "printables"}
    if not isinstance(artifacts, dict) or not required_artifacts.issubset(artifacts):
        raise EditionSignatureError("Manifest is missing a required book or printable artifact.")
    for kind, entry in artifacts.items():
        if kind not in required_artifacts or not isinstance(entry, dict):
            raise EditionSignatureError("Manifest contains an unsupported artifact record.")
        filename = entry.get("file")
        expected_hash = entry.get("sha256")
        expected_size = entry.get("size")
        if not isinstance(filename, str) or Path(filename).name != filename or filename in {"", ".", ".."}:
            raise EditionSignatureError("Manifest contains an unsafe artifact filename.")
        if not isinstance(expected_hash, str) or not SHA256_RE.fullmatch(expected_hash):
            raise EditionSignatureError("Manifest contains an invalid artifact digest.")
        if not isinstance(expected_size, int) or expected_size < 0 or expected_size > MAX_ARTIFACT_BYTES:
            raise EditionSignatureError("Manifest contains an invalid artifact size.")
        artifact_path = root / filename
        if artifact_path.is_symlink() or not artifact_path.is_file():
            raise EditionSignatureError(f"Signed artifact is missing or unsafe: {filename}")
        if artifact_path.stat().st_size != expected_size:
            raise EditionSignatureError(f"Signed artifact size does not match: {filename}")
        digest = hashlib.sha256()
        with artifact_path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
        if not hmac.compare_digest(digest.hexdigest(), expected_hash):
            raise EditionSignatureError(f"Signed artifact SHA-256 does not match: {filename}")
        if kind == "printables":
            try:
                with zipfile.ZipFile(artifact_path) as archive:
                    names = archive.namelist()
                    required_files = {
                        "printables/README.txt",
                        "printables/Coffee_Pot_Snake_Paper_Cryptex.svg",
                        "printables/Participant_FieldKit_Worksheet.md",
                        "printables/Security_Assessment_Playbook.md",
                        "printables/Data_Stewardship_and_Offline_Systems.md",
                        "printables/Researching_Public_Harm_and_Accountability.md",
                    }
                    if not required_files.issubset(names):
                        raise EditionSignatureError("Signed printables package is incomplete.")
                    if len(names) != len(set(names)) or any(
                        name.startswith("/") or ".." in Path(name).parts or "\\" in name
                        for name in names
                    ):
                        raise EditionSignatureError("Signed printables package contains unsafe paths.")
                    if sum(member.file_size for member in archive.infolist()) > 10 * 1024 * 1024:
                        raise EditionSignatureError("Signed printables package expands beyond the size limit.")
                    if any(stat.S_ISLNK(member.external_attr >> 16) for member in archive.infolist()):
                        raise EditionSignatureError("Signed printables package contains a symlink.")
                    if archive.testzip() is not None:
                        raise EditionSignatureError("Signed printables package is corrupt.")
            except zipfile.BadZipFile as error:
                raise EditionSignatureError("Signed printables package is not a valid ZIP.") from error
    return payload
