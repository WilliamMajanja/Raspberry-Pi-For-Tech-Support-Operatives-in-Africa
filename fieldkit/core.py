"""Safe local primitives used by FieldKit; Python standard library only."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import stat
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Iterator


MAX_TEXT_BYTES = 8 * 1024 * 1024
MAX_MANIFEST_FILES = 100_000
SECRET_ASSIGNMENT = re.compile(
    r"(?im)(\b(?:password|passwd|secret|token|api[_-]?key|authorization)\b\s*[:=]\s*)([^\s,;]+)"
)
BEARER_TOKEN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]+=*")
PRIVATE_KEY_BLOCK = re.compile(
    r"-----BEGIN [^-]*PRIVATE KEY-----.*?-----END [^-]*PRIVATE KEY-----",
    re.DOTALL,
)
EMAIL_ADDRESS = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
IPV4_ADDRESS = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
MAC_ADDRESS = re.compile(r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b")


class FieldKitError(Exception):
    """An expected, user-correctable FieldKit error."""


def _read_text(path: Path, limit: int = 64 * 1024) -> str | None:
    try:
        data = path.read_bytes()
    except (OSError, PermissionError):
        return None
    if len(data) > limit:
        data = data[:limit]
    return data.decode("utf-8", errors="replace").replace("\x00", "").strip()


def _os_release(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    text = _read_text(path)
    if not text:
        return result
    for line in text.splitlines():
        key, separator, value = line.partition("=")
        if not separator or not re.fullmatch(r"[A-Z0-9_]+", key):
            continue
        result[key] = value.strip().strip('"').strip("'")
    return result


def local_inventory(root: Path = Path("/")) -> dict[str, object]:
    """Collect a minimal local baseline; do not enumerate addresses or contact hosts."""
    root = root.resolve()
    interfaces = []
    net_dir = root / "sys/class/net"
    try:
        # sysfs class entries are expected symlinks; report interface names only.
        interfaces = sorted(item.name for item in net_dir.iterdir() if item.name != "lo")
    except OSError:
        pass

    model = _read_text(root / "proc/device-tree/model")
    if model:
        model = model.rstrip("\x00")
    mem_total_kib = None
    meminfo = _read_text(root / "proc/meminfo")
    if meminfo:
        match = re.search(r"(?m)^MemTotal:\s+(\d+)\s+kB", meminfo)
        if match:
            mem_total_kib = int(match.group(1))

    try:
        root_usage = os.statvfs(root)
        root_free_bytes = root_usage.f_bavail * root_usage.f_frsize
    except (AttributeError, OSError):
        root_free_bytes = None

    release = _os_release(root / "etc/os-release")
    return {
        "schema": "fieldkit.inventory.v1",
        "collected_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "distribution": release.get("PRETTY_NAME", "unknown"),
        "distribution_id": release.get("ID", "unknown"),
        "distribution_version": release.get("VERSION_ID", "unknown"),
        "architecture": platform.machine(),
        "kernel": platform.release(),
        "python": platform.python_version(),
        "device_model": model or "not reported",
        "memory_total_kib": mem_total_kib,
        "root_free_bytes": root_free_bytes,
        "interfaces": interfaces,
        "privacy_note": "Host name, IP addresses, MAC addresses, serials, and user names are omitted.",
    }


def redact_report(text: str, redact_network: bool = False) -> str:
    """Best-effort scrub of common secrets and contact identifiers before review."""
    if len(text.encode("utf-8")) > MAX_TEXT_BYTES:
        raise FieldKitError(f"Input exceeds the {MAX_TEXT_BYTES}-byte report limit.")
    text = PRIVATE_KEY_BLOCK.sub("[REDACTED PRIVATE KEY]", text)
    text = BEARER_TOKEN.sub("Bearer [REDACTED]", text)
    text = SECRET_ASSIGNMENT.sub(r"\1[REDACTED]", text)
    text = EMAIL_ADDRESS.sub("[REDACTED EMAIL]", text)
    if redact_network:
        text = MAC_ADDRESS.sub("[REDACTED MAC]", text)
        text = IPV4_ADDRESS.sub("[REDACTED IP]", text)
    return text


def write_new_private_file(path: Path, data: bytes) -> None:
    """Create a new file without overwriting an existing path; use owner-only mode."""
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise FieldKitError(f"Refusing to overwrite existing output: {path}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, stat.S_IRUSR | stat.S_IWUSR)
    except OSError as error:
        raise FieldKitError(f"Cannot safely create output {path}: {error}") from error
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def scrub_file(source: Path, destination: Path, redact_network: bool = False) -> int:
    """Write a new, private redacted copy; preserve the source unchanged."""
    if source.is_symlink() or not source.is_file():
        raise FieldKitError("Input must be a regular file, not a symlink.")
    if source.stat().st_size > MAX_TEXT_BYTES:
        raise FieldKitError(f"Input exceeds the {MAX_TEXT_BYTES}-byte report limit.")
    raw = source.read_text(encoding="utf-8", errors="replace")
    clean = redact_report(raw, redact_network=redact_network)
    write_new_private_file(destination, clean.encode("utf-8"))
    return len(clean.splitlines())


def _sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def create_manifest(root: Path, output: Path) -> dict[str, object]:
    """Create a portable SHA-256 manifest without following symlinks."""
    root = root.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise FieldKitError("Manifest root must be a directory.")
    output = output.expanduser().resolve()
    entries: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if path.resolve() == output:
            continue
        if path.is_symlink():
            raise FieldKitError(f"Refusing to follow symlink: {path.relative_to(root)}")
        if not path.is_file():
            continue
        if len(entries) >= MAX_MANIFEST_FILES:
            raise FieldKitError(f"Directory has more than {MAX_MANIFEST_FILES} files.")
        digest, size = _sha256_file(path)
        entries.append({"path": path.relative_to(root).as_posix(), "size": size, "sha256": digest})
    manifest = {
        "schema": "fieldkit.manifest.v1",
        "algorithm": "sha256",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "files": entries,
    }
    encoded = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    write_new_private_file(output, encoded)
    return manifest


def verify_manifest(root: Path, manifest_path: Path) -> list[str]:
    """Return mismatches; do not modify the files being checked."""
    root = root.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise FieldKitError("Manifest root must be a directory.")
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise FieldKitError("Manifest must be a regular file, not a symlink.")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise FieldKitError(f"Cannot read manifest: {error}") from error
    if manifest.get("schema") != "fieldkit.manifest.v1" or manifest.get("algorithm") != "sha256":
        raise FieldKitError("Unsupported manifest schema or digest algorithm.")
    entries = manifest.get("files")
    if not isinstance(entries, list) or len(entries) > MAX_MANIFEST_FILES:
        raise FieldKitError("Manifest file list is invalid or too large.")

    problems: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        relative = entry.get("path") if isinstance(entry, dict) else None
        if not isinstance(relative, str) or relative in seen:
            problems.append(f"invalid or duplicate entry: {relative!r}")
            continue
        seen.add(relative)
        posix = PurePosixPath(relative)
        if posix.is_absolute() or ".." in posix.parts:
            problems.append(f"unsafe manifest path: {relative}")
            continue
        candidate = root / Path(*posix.parts)
        if candidate.is_symlink():
            problems.append(f"symlink is not allowed: {relative}")
            continue
        target = candidate.resolve()
        try:
            target.relative_to(root)
        except ValueError:
            problems.append(f"path escapes manifest root: {relative}")
            continue
        if target.is_symlink() or not target.is_file():
            problems.append(f"missing or non-regular file: {relative}")
            continue
        actual_digest, actual_size = _sha256_file(target)
        if actual_size != entry.get("size"):
            problems.append(f"size mismatch: {relative}")
        if not hmac_compare(actual_digest, str(entry.get("sha256", ""))):
            problems.append(f"SHA-256 mismatch: {relative}")
    return problems


def hmac_compare(left: str, right: str) -> bool:
    """Constant-time digest comparison using only the standard library."""
    import hmac

    return hmac.compare_digest(left, right)


@contextmanager
def _exclusive_file_lock(path: Path) -> Iterator[None]:
    """Cross-platform advisory lock for concurrent local ledger writers."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as stream:
        stream.seek(0)
        if os.name == "nt":
            import msvcrt

            if path.stat().st_size == 0:
                stream.write(b"\0")
                stream.flush()
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _block_hash(block: dict[str, object]) -> str:
    body = {key: value for key, value in block.items() if key != "hash"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def append_issuance_record(path: Path, edition_id: str, artifact_sha256: str) -> dict[str, object]:
    """Append an edition fingerprint to a local hash chain; this is not global consensus."""
    if not re.fullmatch(r"(?:[a-f0-9]{24}|[a-f0-9]{32})", edition_id):
        raise FieldKitError("Edition ID must be a 24- or 32-character lowercase hexadecimal identifier.")
    if not re.fullmatch(r"[a-f0-9]{64}", artifact_sha256):
        raise FieldKitError("Artifact digest must be a lowercase SHA-256 hex string.")
    path = path.expanduser()
    lock_path = path.with_suffix(path.suffix + ".lock")
    with _exclusive_file_lock(lock_path):
        previous_hash = "0" * 64
        index = 0
        if path.exists():
            if path.is_symlink() or not path.is_file():
                raise FieldKitError("Ledger path must be a regular file, not a symlink.")
            problems = verify_issuance_ledger(path)
            if problems:
                raise FieldKitError("Existing ledger failed verification: " + "; ".join(problems[:3]))
            with path.open("r", encoding="utf-8") as stream:
                records = [json.loads(line) for line in stream if line.strip()]
            if records:
                index = int(records[-1]["index"]) + 1
                previous_hash = str(records[-1]["hash"])
        block: dict[str, object] = {
            "schema": "fieldkit.issuance.v1",
            "index": index,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "edition_id": edition_id,
            "artifact_sha256": artifact_sha256,
            "previous_hash": previous_hash,
        }
        block["hash"] = _block_hash(block)
        path.parent.mkdir(parents=True, exist_ok=True)
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
        flags |= getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags, stat.S_IRUSR | stat.S_IWUSR)
        with os.fdopen(fd, "a", encoding="utf-8") as stream:
            stream.write(json.dumps(block, sort_keys=True, separators=(",", ":")) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        return block


def verify_issuance_ledger(path: Path) -> list[str]:
    """Verify ordering and hashes in a local chain; a public checkpoint is needed to detect full rewrites."""
    if path.is_symlink() or not path.is_file():
        raise FieldKitError("Ledger must be a regular file, not a symlink.")
    problems: list[str] = []
    previous_hash = "0" * 64
    try:
        with path.open("r", encoding="utf-8") as stream:
            lines = stream.readlines()
    except OSError as error:
        raise FieldKitError(f"Cannot read ledger: {error}") from error
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            block = json.loads(line)
        except json.JSONDecodeError:
            problems.append(f"invalid JSON at line {index + 1}")
            continue
        if block.get("index") != index:
            problems.append(f"sequence mismatch at line {index + 1}")
        if block.get("previous_hash") != previous_hash:
            problems.append(f"previous-hash mismatch at line {index + 1}")
        expected = _block_hash(block)
        if not hmac_compare(expected, str(block.get("hash", ""))):
            problems.append(f"block hash mismatch at line {index + 1}")
        previous_hash = str(block.get("hash", ""))
    return problems
