"""Dependency-free client for the CPIP Book Portal API."""

from __future__ import annotations

import hashlib
import json
import os
import re
import ssl
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

from .signatures import (
    MANIFEST_NAME,
    PUBLIC_KEY_NAME,
    SIGNATURE_NAME,
    EditionSignatureError,
    verify_edition_directory,
)


MAX_JSON_BYTES = 1024 * 1024
MAX_EDITION_BYTES = 128 * 1024 * 1024
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
EDITION_ID_RE = re.compile(r"^[a-f0-9]{24}$")
APP_TARGETS = {
    "linux-arm64": "fieldkit-linux-arm64.zip",
    "linux-x86_64": "fieldkit-linux-x86_64.zip",
    "windows-x86_64": "fieldkit-windows-x86_64.zip",
    "macos-arm64": "fieldkit-macos-arm64.zip",
    "macos-x86_64": "fieldkit-macos-x86_64.zip",
}


class PortalClientError(Exception):
    """Safe-to-display portal client failure; never includes cipher values."""


class SameOriginRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Reject redirects; the CPIP portal API must not redirect credentials."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise PortalClientError("The CPIP portal redirected a request; refusing to forward credentials.")


def portal_origin(value: str | None = None, allow_local_http: bool = False) -> str:
    raw = value or os.environ.get("CPIP_BOOK_PORTAL_ORIGIN", "")
    parsed = urlsplit(raw)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc or parsed.username or parsed.password:
        raise PortalClientError("Set CPIP_BOOK_PORTAL_ORIGIN to an HTTPS origin without credentials or a path.")
    if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise PortalClientError("CPIP_BOOK_PORTAL_ORIGIN must contain only scheme and host, not a path/query.")
    if parsed.scheme != "https":
        if not allow_local_http or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise PortalClientError("Portal requests require HTTPS; HTTP is allowed only for explicit loopback tests.")
    return f"{parsed.scheme}://{parsed.netloc}"


def _opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(SameOriginRedirectHandler(), urllib.request.HTTPSHandler(context=ssl.create_default_context()))


def _json_request(
    method: str,
    path: str,
    payload: dict[str, object] | None = None,
    cipher: str | None = None,
    origin: str | None = None,
    timeout: float = 15,
) -> dict[str, object]:
    base = portal_origin(origin, allow_local_http=True)
    if not path.startswith("/") or ".." in path.split("/"):
        raise PortalClientError("Refusing an invalid portal API path.")
    data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
    headers = {"Accept": "application/json", "User-Agent": "FieldKit/0.1"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if cipher is not None:
        if not cipher or "\r" in cipher or "\n" in cipher:
            raise PortalClientError("Coffee Cipher is empty or malformed.")
        headers["Authorization"] = "Coffee-Cipher " + cipher
    request = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    try:
        with _opener().open(request, timeout=timeout) as response:
            final = urlsplit(response.geturl())
            if (final.scheme, final.netloc) != (urlsplit(base).scheme, urlsplit(base).netloc):
                raise PortalClientError("Portal response origin changed; refusing the response.")
            raw = response.read(MAX_JSON_BYTES + 1)
    except urllib.error.HTTPError as error:
        # Do not surface remote response text: it could echo credentials or data.
        raise PortalClientError(f"CPIP portal request failed with HTTP {error.code}.") from None
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise PortalClientError(f"Could not reach the CPIP Book Portal: {error.reason if isinstance(error, urllib.error.URLError) else error}") from None
    if len(raw) > MAX_JSON_BYTES:
        raise PortalClientError("Portal JSON response exceeded the size limit.")
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise PortalClientError("Portal returned invalid JSON.") from None
    if not isinstance(result, dict):
        raise PortalClientError("Portal returned an unexpected response type.")
    return result


def bootstrap(answer: str, origin: str | None = None) -> str:
    """Exchange the public starter-puzzle answer for a CPIP Coffee Cipher."""
    response = _json_request("POST", "/v1/bootstrap", {"answer": answer}, origin=origin)
    cipher = response.get("cipher")
    if not isinstance(cipher, str) or not cipher:
        raise PortalClientError("Portal did not issue a Coffee Cipher.")
    return cipher


def _download_one(
    url: str,
    destination: Path,
    expected_sha256: str,
    cipher: str,
    origin: str | None = None,
    timeout: float = 60,
) -> Path:
    base = portal_origin(origin, allow_local_http=True)
    base_parts = urlsplit(base)
    resolved = urllib.parse.urljoin(base + "/", url)
    parts = urlsplit(resolved)
    if (parts.scheme, parts.netloc) != (base_parts.scheme, base_parts.netloc):
        raise PortalClientError("Portal supplied a download URL on a different origin.")
    if not SHA256_RE.fullmatch(expected_sha256):
        raise PortalClientError("Portal supplied an invalid artifact digest.")
    headers = {"Accept": "application/pdf, application/epub+zip", "User-Agent": "FieldKit/0.1", "Authorization": "Coffee-Cipher " + cipher}
    request = urllib.request.Request(resolved, headers=headers, method="GET")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        raise PortalClientError(f"Refusing to overwrite existing file: {destination}")
    temporary_path: Path | None = None
    digest = hashlib.sha256()
    size = 0
    try:
        with _opener().open(request, timeout=timeout) as response:
            final = urlsplit(response.geturl())
            if (final.scheme, final.netloc) != (base_parts.scheme, base_parts.netloc):
                raise PortalClientError("Download redirected outside the CPIP portal origin.")
            with tempfile.NamedTemporaryFile(prefix="fieldkit-download-", dir=destination.parent, delete=False) as output:
                temporary_path = Path(output.name)
                os.chmod(temporary_path, 0o600)
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_EDITION_BYTES:
                        raise PortalClientError("Downloaded edition exceeds the configured size limit.")
                    digest.update(chunk)
                    output.write(chunk)
                output.flush()
                os.fsync(output.fileno())
        if digest.hexdigest() != expected_sha256:
            raise PortalClientError("Downloaded edition failed its SHA-256 integrity check.")
        if destination.suffix == ".pdf":
            with temporary_path.open("rb") as artifact:
                if artifact.read(5) != b"%PDF-":
                    raise PortalClientError("Portal artifact is not a PDF.")
        elif destination.suffix == ".epub":
            try:
                with zipfile.ZipFile(temporary_path) as archive:
                    if archive.testzip() is not None or archive.namelist()[0] != "mimetype":
                        raise PortalClientError("Portal EPUB failed archive validation.")
                    if archive.read("mimetype") != b"application/epub+zip":
                        raise PortalClientError("Portal EPUB has an invalid media type.")
            except (zipfile.BadZipFile, KeyError, IndexError) as error:
                raise PortalClientError("Portal artifact is not a valid EPUB archive.") from error
        elif destination.suffix == ".zip":
            try:
                with zipfile.ZipFile(temporary_path) as archive:
                    if archive.testzip() is not None:
                        raise PortalClientError("Downloaded ZIP artifact failed integrity validation.")
                    names = archive.namelist()
                    if not names or any(name.startswith("/") or ".." in Path(name).parts for name in names):
                        raise PortalClientError("Downloaded ZIP artifact contains an unsafe path.")
                    if destination.name == "field-hackathon-printables.zip":
                        if "printables/Coffee_Pot_Snake_Paper_Cryptex.svg" not in names:
                            raise PortalClientError("Printable pack is missing the full-scale cryptex template.")
                    else:
                        if not any(Path(name).name.startswith("fieldkit") for name in names):
                            raise PortalClientError("Standalone app bundle contains no FieldKit executable.")
                        if "THIRD_PARTY_NOTICES.md" not in names:
                            raise PortalClientError("Standalone app bundle is missing component notices.")
            except (zipfile.BadZipFile, KeyError, IndexError) as error:
                raise PortalClientError("Standalone app artifact is not a valid ZIP bundle.") from error
        if destination.exists():
            raise PortalClientError(f"Refusing to overwrite existing file: {destination}")
        os.replace(temporary_path, destination)
        temporary_path = None
    except urllib.error.HTTPError as error:
        raise PortalClientError(f"Edition download failed with HTTP {error.code}.") from None
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise PortalClientError(f"Edition download failed: {error.reason if isinstance(error, urllib.error.URLError) else error}") from None
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except OSError:
                pass
    return destination


def create_edition(
    cipher: str,
    profile: str,
    output_dir: Path,
    origin: str | None = None,
    trusted_fingerprint: str | None = None,
) -> dict[str, object]:
    """Request an edition, verify same-origin artifact hashes, and download it."""
    if not trusted_fingerprint:
        raise PortalClientError("Supply the publisher signing-key fingerprint from an independent event or release source.")
    if not re.fullmatch(r"[a-z][a-z0-9-]{1,31}", profile):
        raise PortalClientError("Profile name must be a short lowercase identifier.")
    response = _json_request("POST", "/v1/editions", {"profile": profile}, cipher=cipher, origin=origin, timeout=60)
    edition_id_value = response.get("edition_id")
    next_cipher = response.get("cipher")
    downloads = response.get("downloads")
    signing_fingerprint = response.get("signing_key_fingerprint")
    if not isinstance(edition_id_value, str) or not re.fullmatch(r"[a-f0-9]{24}", edition_id_value):
        raise PortalClientError("Portal returned an invalid edition ID.")
    if not isinstance(next_cipher, str) or not next_cipher:
        raise PortalClientError("Portal returned no per-edition Coffee Cipher.")
    if not isinstance(downloads, dict):
        raise PortalClientError("Portal returned no edition download manifest.")
    if not isinstance(signing_fingerprint, str) or not SHA256_RE.fullmatch(signing_fingerprint):
        raise PortalClientError("Portal returned no valid publisher signing-key fingerprint.")
    if signing_fingerprint.lower() != trusted_fingerprint.lower().removeprefix("sha256:").replace(":", "").strip():
        raise PortalClientError("Portal signing key does not match the independently trusted fingerprint.")

    output_dir.mkdir(parents=True, exist_ok=True)
    edition_dir = output_dir / edition_id_value
    if edition_dir.exists() or edition_dir.is_symlink():
        raise PortalClientError(f"Edition output already exists: {edition_dir}")
    from .core import write_new_private_file

    results: dict[str, object] = {"edition_id": edition_id_value, "profile": profile, "files": {}}
    with tempfile.TemporaryDirectory(prefix=".fieldkit-edition-", dir=output_dir) as temporary:
        staging = Path(temporary)
        manifest_files: dict[str, dict[str, str]] = {}
        local_names = {
            "pdf": f"Raspberry-Pi-Field-Guide-{edition_id_value}.pdf",
            "epub": f"Raspberry-Pi-Field-Guide-{edition_id_value}.epub",
            "cover": "cover.png",
            "printables": "field-hackathon-printables.zip",
            "manifest": MANIFEST_NAME,
            "signature": SIGNATURE_NAME,
            "public-key": PUBLIC_KEY_NAME,
        }
        for kind, filename in local_names.items():
            item = downloads.get(kind)
            if not isinstance(item, dict):
                raise PortalClientError(f"Portal did not provide the signed-edition {kind} artifact.")
            url = item.get("url")
            sha256 = item.get("sha256")
            if not isinstance(url, str) or not isinstance(sha256, str):
                raise PortalClientError(f"Portal supplied an invalid {kind} artifact record.")
            saved = _download_one(url, staging / filename, sha256, next_cipher, origin=origin)
            manifest_files[kind] = {"file": filename, "sha256": sha256}
        signed_manifest = verify_edition_directory(staging, trusted_fingerprint)
        if signed_manifest.get("edition_id") != edition_id_value or signed_manifest.get("profile") != profile:
            raise PortalClientError("Signed manifest edition or profile does not match the portal response.")
        if signed_manifest.get("signing_key_fingerprint") != signing_fingerprint:
            raise PortalClientError("Signed manifest key does not match the portal response.")
        write_new_private_file(staging / "coffee-cipher.txt", (next_cipher + "\n").encode("utf-8"))
        manifest = {
            "edition_id": edition_id_value,
            "profile": profile,
            "signing_key_fingerprint": signing_fingerprint,
            "signature_verified": True,
            "files": manifest_files,
        }
        write_new_private_file(
            staging / "edition.json",
            (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
        if edition_dir.exists() or edition_dir.is_symlink():
            raise PortalClientError(f"Edition output already exists: {edition_dir}")
        os.rename(staging, edition_dir)
    results["files"] = {
        kind: {"path": str(edition_dir / item["file"]), "sha256": item["sha256"]}
        for kind, item in manifest_files.items()
    }
    results["cipher_file"] = str(edition_dir / "coffee-cipher.txt")
    return results


def download_standalone(target: str, cipher: str, output_dir: Path, origin: str | None = None) -> Path:
    """Download a platform-specific FieldKit binary from the CPIP origin only."""
    if target not in APP_TARGETS:
        raise PortalClientError("Unsupported standalone FieldKit target.")
    response = _json_request("GET", "/v1/apps", cipher=cipher, origin=origin)
    apps = response.get("apps")
    if not isinstance(apps, dict):
        raise PortalClientError("Portal returned no application manifest.")
    digest = apps.get(target)
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        raise PortalClientError(f"The portal has no verified app build for {target}.")
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / APP_TARGETS[target]
    saved = _download_one(f"/v1/apps/{target}", destination, digest, cipher, origin=origin)
    return saved
