#!/usr/bin/env python3
"""Loopback-only CPIP Book Portal gateway.

Run behind a reviewed HTTPS reverse proxy. The CPIP backend must also bind to
loopback. This service never exposes the CPIP dashboard or general CPIP API.
"""

from __future__ import annotations

import hashlib
import hmac
import html
import ipaddress
import json
import os
import re
import secrets
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import zipfile
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from portal.cpip_adapter import CPIPAdapter, CPIPAdapterError


ROOT = Path(__file__).resolve().parent.parent
EDITION_ID_RE = re.compile(r"^[a-f0-9]{24}$")
JSON_BODY_LIMIT = 8 * 1024
PDF_LIMIT = 64 * 1024 * 1024
EPUB_LIMIT = 32 * 1024 * 1024
PROFILES = {
    "field-technician": "Field technician: prioritize setup, triage, recovery, and handover.",
    "operations-lead": "Operations lead: prioritize continuity, privacy, change control, and escalation.",
    "informatics-practitioner": "Informatics practitioner: prioritize data provenance, governance, validation, and risk.",
    "facilitator": "Facilitator: prioritize learning paths, offline exercises, and group discussion.",
}
APP_TARGETS = {
    "linux-arm64": "fieldkit-linux-arm64.zip",
    "linux-x86_64": "fieldkit-linux-x86_64.zip",
    "windows-x86_64": "fieldkit-windows-x86_64.zip",
    "macos-arm64": "fieldkit-macos-arm64.zip",
    "macos-x86_64": "fieldkit-macos-x86_64.zip",
}
STARTER_ANSWER = "FLAG{WRITTEN_SCOPE}"


class PortalError(Exception):
    """Expected portal failure; message must not contain credentials or user data."""


class RateLimiter:
    """Small in-memory limiter; client addresses are never written to disk."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self.events: dict[str, list[float]] = {}
        self.lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self.lock:
            recent = [when for when in self.events.get(key, []) if now - when < self.window]
            if len(recent) >= self.limit:
                self.events[key] = recent
                return False
            recent.append(now)
            self.events[key] = recent
            if len(self.events) > 4096:
                self.events = {k: v for k, v in self.events.items() if any(now - t < self.window for t in v)}
            return True


class PortalStore:
    def __init__(self, data_dir: Path, token_pepper: bytes):
        raw_dir = data_dir.expanduser()
        if raw_dir.is_symlink():
            raise PortalError("Portal data directory must not be a symlink.")
        raw_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.data_dir = raw_dir.resolve(strict=True)
        try:
            os.chmod(self.data_dir, 0o700)
        except OSError:
            pass
        self.db_path = self.data_dir / "portal.sqlite3"
        self.pepper = token_pepper
        self._init_db()
        chain_errors = self.verify_chain()
        if chain_errors:
            raise PortalError("Portal issuance chain failed integrity verification.")

    @contextmanager
    def _connect(self):
        if self.db_path.is_symlink():
            raise PortalError("Portal database path must not be a symlink.")
        connection = sqlite3.connect(self.db_path, timeout=15)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA journal_mode=WAL")
            yield connection
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _init_db(self) -> None:
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS credentials (
                    token_digest TEXT PRIMARY KEY,
                    edition_id TEXT NOT NULL,
                    profile TEXT NOT NULL,
                    created_utc TEXT NOT NULL,
                    revoked INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS editions (
                    edition_id TEXT PRIMARY KEY,
                    profile TEXT NOT NULL,
                    created_utc TEXT NOT NULL,
                    pdf_name TEXT NOT NULL,
                    pdf_sha256 TEXT NOT NULL,
                    epub_name TEXT NOT NULL,
                    epub_sha256 TEXT NOT NULL,
                    cover_name TEXT NOT NULL,
                    cover_sha256 TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS blocks (
                    block_index INTEGER PRIMARY KEY,
                    previous_hash TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    block_hash TEXT NOT NULL UNIQUE
                );
            """)
        try:
            os.chmod(self.db_path, 0o600)
        except OSError:
            pass

    def _append_block(self, db: sqlite3.Connection, payload: dict[str, object]) -> None:
        row = db.execute(
            "SELECT block_index, block_hash FROM blocks ORDER BY block_index DESC LIMIT 1"
        ).fetchone()
        index = 0 if row is None else int(row["block_index"]) + 1
        previous = "0" * 64 if row is None else str(row["block_hash"])
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(f"{index}:{previous}:{serialized}".encode("utf-8")).hexdigest()
        db.execute(
            "INSERT INTO blocks(block_index, previous_hash, payload_json, block_hash) VALUES (?, ?, ?, ?)",
            (index, previous, serialized, digest),
        )

    def verify_chain(self) -> list[str]:
        problems: list[str] = []
        previous = "0" * 64
        with self._connect() as db:
            rows = db.execute("SELECT * FROM blocks ORDER BY block_index").fetchall()
        for expected_index, row in enumerate(rows):
            if row["block_index"] != expected_index:
                problems.append(f"block sequence mismatch at index {expected_index}")
            if row["previous_hash"] != previous:
                problems.append(f"previous hash mismatch at index {expected_index}")
            expected = hashlib.sha256(
                f"{expected_index}:{previous}:{row['payload_json']}".encode("utf-8")
            ).hexdigest()
            if not hmac.compare_digest(expected, row["block_hash"]):
                problems.append(f"block digest mismatch at index {expected_index}")
            previous = row["block_hash"]
        return problems

    def token_digest(self, edition_id: str, token: str) -> str:
        return hmac.new(self.pepper, f"{edition_id}:{token}".encode("utf-8"), hashlib.sha256).hexdigest()

    def add_bootstrap_credential(self, edition_id: str, token: str, cipher: str) -> None:
        digest = self.token_digest(edition_id, token)
        created = datetime.now(timezone.utc).isoformat(timespec="seconds")
        payload = {
            "type": "starter-cipher-issued",
            "edition_id": edition_id,
            "cipher_sha256": hashlib.sha256(cipher.encode("utf-8")).hexdigest(),
            "created_utc": created,
        }
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                "INSERT INTO credentials(token_digest, edition_id, profile, created_utc) VALUES (?, ?, ?, ?)",
                (digest, edition_id, "starter", created),
            )
            self._append_block(db, payload)
            db.commit()

    def credential_is_active(self, edition_id: str, token: str) -> bool:
        digest = self.token_digest(edition_id, token)
        with self._connect() as db:
            row = db.execute(
                "SELECT revoked FROM credentials WHERE token_digest=? AND edition_id=?",
                (digest, edition_id),
            ).fetchone()
        return bool(row is not None and row["revoked"] == 0)

    def record_edition(
        self,
        edition_id: str,
        profile: str,
        token: str,
        pdf_name: str,
        pdf_hash: str,
        epub_name: str,
        epub_hash: str,
        cover_name: str,
        cover_hash: str,
        cipher_hash: str,
    ) -> None:
        token_digest = self.token_digest(edition_id, token)
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        combined_hash = hashlib.sha256((pdf_hash + epub_hash + cover_hash).encode("ascii")).hexdigest()
        payload = {
            "type": "personalized-edition-issued",
            "edition_id": edition_id,
            "profile": profile,
            "artifact_sha256": combined_hash,
            "cipher_sha256": cipher_hash,
            "created_utc": now,
        }
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                "INSERT INTO editions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (edition_id, profile, now, pdf_name, pdf_hash, epub_name, epub_hash, cover_name, cover_hash),
            )
            db.execute(
                "INSERT INTO credentials(token_digest, edition_id, profile, created_utc) VALUES (?, ?, ?, ?)",
                (token_digest, edition_id, profile, now),
            )
            self._append_block(db, payload)
            db.commit()

    def get_edition(self, edition_id: str) -> sqlite3.Row | None:
        if not EDITION_ID_RE.fullmatch(edition_id):
            return None
        with self._connect() as db:
            return db.execute("SELECT * FROM editions WHERE edition_id=?", (edition_id,)).fetchone()

    def revoke_edition_cipher(self, edition_id: str) -> int:
        if not EDITION_ID_RE.fullmatch(edition_id):
            raise PortalError("Invalid edition ID.")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            cursor = db.execute(
                "UPDATE credentials SET revoked=1 WHERE edition_id=? AND revoked=0",
                (edition_id,),
            )
            count = cursor.rowcount
            if count:
                self._append_block(db, {
                    "type": "edition-cipher-revoked",
                    "edition_id": edition_id,
                    "credential_count": count,
                    "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                })
            db.commit()
        return count

    def record_app_bundle(self, target: str, sha256_digest: str) -> None:
        payload = {
            "type": "standalone-app-published",
            "target": target,
            "sha256": sha256_digest,
            "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._append_block(db, payload)
            db.commit()


class BookPortal:
    def __init__(
        self,
        data_dir: Path,
        cpip: CPIPAdapter,
        token_pepper: bytes,
        starter_answer_hash: str,
        app_dir: Path | None = None,
        allowed_host: str | None = None,
    ):
        if not re.fullmatch(r"[a-f0-9]{64}", starter_answer_hash):
            raise PortalError("Starter answer hash must be a 64-character SHA-256 digest.")
        self.store = PortalStore(data_dir, token_pepper)
        self.cpip = cpip
        self.starter_hash = starter_answer_hash
        self.data_dir = self.store.data_dir
        self.app_dir = app_dir.expanduser().resolve() if app_dir else self.data_dir / "apps"
        self.allowed_host = allowed_host.lower().rstrip(".") if allowed_host else None
        self.app_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            os.chmod(self.app_dir, 0o700)
        except OSError:
            pass
        self.bootstrap_limiter = RateLimiter(limit=8, window_seconds=900)
        self.edition_limiter = RateLimiter(limit=4, window_seconds=3600)

    def _new_cipher(self, edition_id: str, token: str) -> str:
        try:
            return self.cpip.encode_token(edition_id, token)
        except (CPIPAdapterError, ValueError) as error:
            raise PortalError("CPIP could not issue the edition cipher.") from error

    def _decode_and_authenticate(self, cipher: str) -> tuple[str, str]:
        try:
            edition_id, token = self.cpip.decode_token(cipher)
        except (CPIPAdapterError, ValueError) as error:
            raise PortalError("Coffee Cipher rejected.") from error
        if not self.store.credential_is_active(edition_id, token):
            raise PortalError("Coffee Cipher rejected.")
        return edition_id, token

    def bootstrap(self, answer: str, rate_key: str) -> dict[str, str]:
        if not self.bootstrap_limiter.allow(rate_key):
            raise PortalError("Starter challenge rate limit reached; try again later.")
        normalized = answer.strip().upper()
        actual = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        if not hmac.compare_digest(actual, self.starter_hash):
            raise PortalError("Starter puzzle answer is incorrect.")
        edition_id = secrets.token_hex(12)
        token = secrets.token_urlsafe(32)
        cipher = self._new_cipher(edition_id, token)
        self.store.add_bootstrap_credential(edition_id, token, cipher)
        return {"edition_id": edition_id, "cipher": cipher}

    def _build(self, edition_id: str, profile: str, cipher: str, cover_seed: str) -> dict[str, tuple[str, str]]:
        import tempfile

        from tools.build_books import EPUB_NAME, PDF_NAME, COVER_NAME

        with tempfile.TemporaryDirectory(prefix="cpip-book-build-", dir=self.data_dir) as temporary:
            root = Path(temporary)
            output_dir = root / "output"
            output_dir.mkdir(mode=0o700)
            config = {
                "edition_id": edition_id,
                "profile": profile,
                "cipher": cipher,
                "cover_seed": cover_seed,
            }
            config_path = root / "edition.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            try:
                os.chmod(config_path, 0o600)
            except OSError:
                pass
            env = {
                "PATH": os.environ.get("PATH", ""),
                "HOME": str(root),
                "LANG": "C.UTF-8",
                "PYTHONUTF8": "1",
            }
            command = [sys.executable, str(ROOT / "tools" / "build_books.py"), "--output-dir", str(output_dir), "--edition-config", str(config_path)]
            try:
                result = subprocess.run(
                    command,
                    cwd=ROOT,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=600,
                    check=False,
                )
            except subprocess.TimeoutExpired as error:
                raise PortalError("Edition build timed out; retry later.") from error
            if result.returncode != 0:
                # Never return Pandoc/Chromium output, which may contain edition material.
                raise PortalError("Edition build failed; the maintainer log contains the sanitized failure status.")
            names = {
                "pdf": f"{Path(PDF_NAME).stem}-{edition_id}.pdf",
                "epub": f"{Path(EPUB_NAME).stem}-{edition_id}.epub",
                "cover": f"cover-{edition_id}.png",
            }
            results: dict[str, tuple[str, str]] = {}
            for kind, filename in names.items():
                path = output_dir / filename
                if not path.is_file() or path.is_symlink():
                    raise PortalError(f"Edition builder omitted {kind} output.")
                if path.stat().st_size > 128 * 1024 * 1024:
                    raise PortalError("Edition artifact exceeded the configured size limit.")
                if kind == "pdf" and not path.read_bytes().startswith(b"%PDF-"):
                    raise PortalError("Edition PDF failed format validation.")
                if kind == "epub":
                    try:
                        with zipfile.ZipFile(path) as archive:
                            if archive.testzip() is not None or archive.namelist()[0] != "mimetype":
                                raise PortalError("Edition EPUB failed ZIP validation.")
                            if archive.read("mimetype") != b"application/epub+zip":
                                raise PortalError("Edition EPUB has the wrong media type.")
                    except (zipfile.BadZipFile, IndexError, KeyError) as error:
                        raise PortalError("Edition EPUB failed archive validation.") from error
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                results[kind] = (filename, digest)

            final_dir = self.data_dir / "editions" / edition_id
            final_dir.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            if final_dir.exists() or final_dir.is_symlink():
                raise PortalError("Edition ID collision; please retry.")
            final_dir.parent.chmod(0o700)
            os.rename(output_dir, final_dir)
            for kind, (filename, _) in results.items():
                results[kind] = (f"editions/{edition_id}/{filename}", results[kind][1])
            return results

    def create_edition(self, cipher: str, profile: str, rate_key: str) -> dict[str, Any]:
        if not self.edition_limiter.allow(rate_key):
            raise PortalError("Edition rate limit reached; try again later.")
        self._decode_and_authenticate(cipher)
        if profile not in PROFILES:
            raise PortalError("Unknown edition profile.")
        edition_id = secrets.token_hex(12)
        next_token = secrets.token_urlsafe(32)
        next_cipher = self._new_cipher(edition_id, next_token)
        cover_seed = secrets.token_hex(32)
        artifacts = self._build(edition_id, profile, next_cipher, cover_seed)
        self.store.record_edition(
            edition_id,
            profile,
            next_token,
            artifacts["pdf"][0], artifacts["pdf"][1],
            artifacts["epub"][0], artifacts["epub"][1],
            artifacts["cover"][0], artifacts["cover"][1],
            hashlib.sha256(next_cipher.encode("utf-8")).hexdigest(),
        )
        return {
            "edition_id": edition_id,
            "profile": profile,
            "cipher": next_cipher,
            "downloads": {
                "pdf": {"url": f"/v1/editions/{edition_id}/pdf", "sha256": artifacts["pdf"][1]},
                "epub": {"url": f"/v1/editions/{edition_id}/epub", "sha256": artifacts["epub"][1]},
                "cover": {"url": f"/v1/editions/{edition_id}/cover", "sha256": artifacts["cover"][1]},
            },
            "apps": self.available_apps(),
        }

    def artifact(self, edition_id: str, kind: str, cipher: str) -> tuple[Path, str, str]:
        auth_edition, _token = self._decode_and_authenticate(cipher)
        if auth_edition != edition_id:
            raise PortalError("Coffee Cipher is not authorized for this edition.")
        row = self.store.get_edition(edition_id)
        if row is None:
            raise PortalError("Edition not found.")
        fields = {
            "pdf": (row["pdf_name"], row["pdf_sha256"], "application/pdf"),
            "epub": (row["epub_name"], row["epub_sha256"], "application/epub+zip"),
            "cover": (row["cover_name"], row["cover_sha256"], "image/png"),
        }
        if kind not in fields:
            raise PortalError("Unknown edition artifact.")
        relative, expected_hash, content_type = fields[kind]
        path = (self.data_dir / relative).resolve()
        try:
            path.relative_to(self.data_dir.resolve())
        except ValueError as error:
            raise PortalError("Stored edition path is invalid.") from error
        if path.is_symlink() or not path.is_file():
            raise PortalError("Edition artifact is unavailable.")
        if path.stat().st_size > 128 * 1024 * 1024:
            raise PortalError("Edition artifact exceeds the serving size limit.")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
        if not hmac.compare_digest(digest.hexdigest(), expected_hash):
            raise PortalError("Stored edition artifact failed its integrity check.")
        return path, content_type, expected_hash

    def app_artifact(self, target: str, cipher: str) -> tuple[Path, str, str]:
        self._decode_and_authenticate(cipher)
        filename = APP_TARGETS.get(target)
        if filename is None:
            raise PortalError("Unsupported FieldKit build target.")
        app_dir = self.app_dir.resolve()
        candidate = self.app_dir / filename
        if candidate.is_symlink() or not candidate.is_file():
            raise PortalError("That standalone FieldKit build is not yet published.")
        path = candidate.resolve()
        try:
            path.relative_to(app_dir)
        except ValueError as error:
            raise PortalError("Standalone application path is invalid.") from error
        if path.stat().st_size > 256 * 1024 * 1024:
            raise PortalError("Standalone application exceeds the serving size limit.")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return path, "application/zip", digest

    def available_apps(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for target, filename in APP_TARGETS.items():
            candidate = self.app_dir / filename
            if candidate.is_file() and not candidate.is_symlink():
                result[target] = hashlib.sha256(candidate.read_bytes()).hexdigest()
        return result


def _starter_answer_hash(answer: str) -> str:
    return hashlib.sha256(answer.strip().upper().encode("utf-8")).hexdigest()


def config_from_env() -> tuple[BookPortal, int]:
    data_dir = Path(os.environ.get("CPIP_BOOK_DATA_DIR", str(Path.home() / ".local/share/cpip-book-portal")))
    cpip_origin = os.environ.get("CPIP_INTERNAL_ORIGIN", "http://127.0.0.1:4180")
    cpip_key = os.environ.get("CPIP_COVERT_KEY", "")
    app_dir = Path(os.environ.get("CPIP_BOOK_APP_DIR", str(Path.home() / ".local/share/cpip-book-portal/apps")))
    token_pepper_text = os.environ.get("CPIP_BOOK_TOKEN_PEPPER", "")
    if len(token_pepper_text.encode("utf-8")) < 32:
        raise PortalError("Set CPIP_BOOK_TOKEN_PEPPER to an independent 32-byte-or-longer secret.")
    starter_hash = os.environ.get("CPIP_BOOK_STARTER_ANSWER_SHA256", _starter_answer_hash(STARTER_ANSWER))
    public_host = os.environ.get("CPIP_BOOK_DOMAIN", "").strip()
    portal = BookPortal(
        data_dir,
        CPIPAdapter(cpip_origin, cpip_key),
        token_pepper_text.encode("utf-8"),
        starter_hash,
        app_dir,
        public_host or None,
    )
    port = int(os.environ.get("CPIP_BOOK_PORTAL_PORT", "4310"))
    if not 1024 <= port <= 65535:
        raise PortalError("CPIP_BOOK_PORTAL_PORT must be an unprivileged TCP port.")
    return portal, port


class PortalHandler(BaseHTTPRequestHandler):
    server_version = "CPIPBookPortal"
    sys_version = ""

    def log_message(self, fmt: str, *args: object) -> None:
        # Requests can contain bearer ciphers; do not log paths or headers.
        return

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
        super().end_headers()

    @property
    def portal(self) -> BookPortal:
        return self.server.portal  # type: ignore[attr-defined]

    def _client_key(self) -> str:
        # The service binds to loopback and trusts only its local reverse proxy.
        if self.client_address[0] in {"127.0.0.1", "::1"}:
            forwarded = self.headers.get("X-Forwarded-For", "").split(",", 1)[0].strip()
            if forwarded and len(forwarded) <= 64:
                try:
                    return str(ipaddress.ip_address(forwarded))
                except ValueError:
                    pass
        return self.client_address[0]

    def _send(self, status: int, data: bytes, content_type: str = "application/json; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, status: int, payload: dict[str, object]) -> None:
        self._send(status, (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))

    def _body(self) -> bytes:
        if self.headers.get("Transfer-Encoding"):
            raise PortalError("Chunked request bodies are not accepted.")
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise PortalError("Invalid request length.") from error
        if length < 0 or length > JSON_BODY_LIMIT:
            raise PortalError("Request body exceeds the allowed size.")
        return self.rfile.read(length)

    def _cipher(self) -> str:
        value = self.headers.get("Authorization", "")
        prefix = "Coffee-Cipher "
        if not value.startswith(prefix):
            raise PortalError("A valid Coffee Cipher is required.")
        return value[len(prefix):].strip()

    def _host_allowed(self) -> bool:
        host_header = self.headers.get("Host", "")
        hostname = urllib.parse.urlsplit("//" + host_header).hostname
        if not hostname:
            return False
        if self.portal.allowed_host:
            return hostname.lower().rstrip(".") == self.portal.allowed_host
        return hostname.lower() in {"localhost", "127.0.0.1", "::1"}

    def do_GET(self) -> None:
        if not self._host_allowed():
            self._json(421, {"error": "Unexpected Host header."})
            return
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.query or parsed.fragment:
            self._json(400, {"error": "Query strings and fragments are not accepted."})
            return
        if parsed.path == "/":
            self._send(200, self._landing().encode("utf-8"), "text/html; charset=utf-8")
            return
        if parsed.path == "/v1/apps":
            try:
                self.portal._decode_and_authenticate(self._cipher())
                self._json(200, {"apps": self.portal.available_apps()})
            except PortalError as error:
                self._json(401 if "Cipher" in str(error) else 400, {"error": str(error)})
            return
        match = re.fullmatch(r"/v1/editions/([a-f0-9]{24})/(pdf|epub|cover)", parsed.path)
        app_match = re.fullmatch(
            r"/v1/apps/(linux-arm64|linux-x86_64|windows-x86_64|macos-arm64|macos-x86_64)",
            parsed.path,
        )
        if not match and not app_match:
            self._json(404, {"error": "Not found."})
            return
        try:
            if match:
                path, content_type, digest = self.portal.artifact(match.group(1), match.group(2), self._cipher())
            else:
                path, content_type, digest = self.portal.app_artifact(app_match.group(1), self._cipher())
            self._send_file(path, content_type, digest)
        except PortalError as error:
            self._json(401 if "Cipher" in str(error) else 400, {"error": str(error)})

    def do_POST(self) -> None:
        if not self._host_allowed():
            self._json(421, {"error": "Unexpected Host header."})
            return
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.query or parsed.fragment:
            self._json(400, {"error": "Query strings and fragments are not accepted."})
            return
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        try:
            raw = self._body()
            if parsed.path == "/v1/bootstrap" and content_type == "application/json":
                body = json.loads(raw.decode("utf-8"))
                result = self.portal.bootstrap(str(body.get("answer", "")), self._client_key())
                self._json(200, result)
                return
            if parsed.path == "/v1/editions" and content_type == "application/json":
                body = json.loads(raw.decode("utf-8"))
                result = self.portal.create_edition(self._cipher(), str(body.get("profile", "")), self._client_key())
                self._json(201, result)
                return
            if parsed.path == "/starter" and content_type == "application/x-www-form-urlencoded":
                values = urllib.parse.parse_qs(raw.decode("utf-8", errors="strict"), max_num_fields=4)
                result = self.portal.bootstrap(values.get("answer", [""])[0], self._client_key())
                raw_cipher = result["cipher"]
                cipher = html.escape(raw_cipher, quote=True)
                profile_options = "".join(
                    '<option value="{}">{}</option>'.format(html.escape(profile), html.escape(profile.replace("-", " ").title()))
                    for profile in PROFILES
                )
                app_forms = self._app_forms(raw_cipher, self.portal.available_apps())
                page = self._landing(
                    '<h2>Your starter Coffee Cipher</h2>'
                    '<p>Keep this code if you want to request a personalized edition. It is a shareable bearer code, not a personal identity or DRM.</p>'
                    f'<textarea readonly rows="5" cols="72">{cipher}</textarea>'
                    '<form method="post" action="/issue">'
                    f'<input type="hidden" name="cipher" value="{cipher}">'
                    f'<label>Reader path <select name="profile">{profile_options}</select></label>'
                    '<button type="submit">Create my edition</button></form>'
                    + app_forms
                )
                self._send(200, page.encode("utf-8"), "text/html; charset=utf-8")
                return
            if parsed.path == "/issue" and content_type == "application/x-www-form-urlencoded":
                values = urllib.parse.parse_qs(raw.decode("utf-8", errors="strict"), max_num_fields=8)
                cipher = values.get("cipher", [""])[0]
                profile = values.get("profile", [""])[0]
                result = self.portal.create_edition(cipher, profile, self._client_key())
                forms = "".join(
                    f'<form method="post" action="/download"><input type="hidden" name="cipher" value="{html.escape(result["cipher"])}">'
                    f'<input type="hidden" name="edition_id" value="{result["edition_id"]}"><input type="hidden" name="kind" value="{kind}">'
                    f'<button type="submit">Download {kind.upper()}</button></form>'
                    for kind in ("pdf", "epub")
                )
                forms += self._app_forms(result["cipher"], result.get("apps", {}))
                next_cipher = html.escape(result["cipher"])
                page = self._landing(
                    f"<h2>Your edition is ready</h2><p>Edition {result['edition_id']} · profile {html.escape(profile)}</p>"
                    f"<p>Store this cipher for future CPIP Book Portal sessions:</p><textarea readonly rows=5 cols=72>{next_cipher}</textarea>{forms}"
                )
                self._send(201, page.encode("utf-8"), "text/html; charset=utf-8")
                return
            if parsed.path == "/download" and content_type == "application/x-www-form-urlencoded":
                values = urllib.parse.parse_qs(raw.decode("utf-8", errors="strict"), max_num_fields=8)
                edition_id = values.get("edition_id", [""])[0]
                kind = values.get("kind", [""])[0]
                cipher = values.get("cipher", [""])[0]
                path, mime, digest = self.portal.artifact(edition_id, kind, cipher)
                self._send_file(path, mime, digest)
                return
            if parsed.path == "/app" and content_type == "application/x-www-form-urlencoded":
                values = urllib.parse.parse_qs(raw.decode("utf-8", errors="strict"), max_num_fields=8)
                target = values.get("target", [""])[0]
                cipher = values.get("cipher", [""])[0]
                path, mime, digest = self.portal.app_artifact(target, cipher)
                self._send_file(path, mime, digest)
                return
            self._json(404, {"error": "Not found."})
        except (PortalError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            message = str(error)
            status = 401 if "Cipher" in message else 400
            if parsed.path.startswith("/v1/"):
                self._json(status, {"error": message})
            else:
                page = self._landing(f"<p role=\"alert\">{html.escape(message)}</p>")
                self._send(400, page.encode("utf-8"), "text/html; charset=utf-8")

    def _send_file(self, path: Path, content_type: str, digest: str) -> None:
        size = path.stat().st_size
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(size))
        self.send_header("Content-Disposition", f'attachment; filename="{path.name}"')
        self.send_header("ETag", '"' + digest + '"')
        self.end_headers()
        with path.open("rb") as stream:
            shutil.copyfileobj(stream, self.wfile)

    @staticmethod
    def _app_forms(cipher: str, apps: dict[str, str]) -> str:
        if not apps:
            return "<p>No standalone app bundles have been published for this portal yet.</p>"
        forms = []
        safe_cipher = html.escape(cipher, quote=True)
        for target in sorted(apps):
            safe_target = html.escape(target, quote=True)
            forms.append(
                '<form method="post" action="/app">'
                f'<input type="hidden" name="cipher" value="{safe_cipher}">'
                f'<input type="hidden" name="target" value="{safe_target}">'
                f'<button type="submit">Download FieldKit for {html.escape(target)}</button></form>'
            )
        return "".join(forms)

    @staticmethod
    def _landing(extra: str = "") -> str:
        return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CPIP Book Portal</title><h1>Raspberry Pi for Technical Support Operatives in Africa</h1>
<p>This portal issues personalized, CC0-compatible editions. The book remains readable and shareable; the Coffee Cipher is not DRM.</p>
<h2>Starter puzzle</h2><p>Before an authorized security assessment, what written record defines the approved targets, methods, time window, and stop conditions?</p>
<form method="post" action="/starter"><label>Answer <input name="answer" autocomplete="off" required></label><button type="submit">Request starter Coffee Cipher</button></form>
{extra}<p>Official editions are delivered over HTTPS. Edition IDs identify variants; no name or email is required.</p></html>"""


class PortalHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, portal: BookPortal, port: int):
        self.portal = portal
        super().__init__(("127.0.0.1", port), PortalHandler)


def main() -> int:
    try:
        portal, port = config_from_env()
        server = PortalHTTPServer(portal, port)
    except (PortalError, OSError, ValueError) as error:
        print(f"CPIP Book Portal configuration error: {error}", file=sys.stderr)
        return 2
    print(f"CPIP Book Portal listening on loopback only at 127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
