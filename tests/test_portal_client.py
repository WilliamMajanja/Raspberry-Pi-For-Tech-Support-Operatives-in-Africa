import hashlib
import io
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from fieldkit.portal_client import PortalClientError, create_edition, download_standalone, portal_origin
from fieldkit.signatures import (
    MANIFEST_NAME,
    PUBLIC_KEY_NAME,
    SIGNATURE_NAME,
    key_fingerprint,
    sign_manifest,
    verify_edition_directory,
)


PDF_BYTES = b"%PDF-1.4\nsynthetic fixture\n"


def make_epub_fixture():
    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as archive:
        info = ZipInfo("mimetype")
        info.compress_type = ZIP_STORED
        archive.writestr(info, b"application/epub+zip")
        archive.writestr("META-INF/container.xml", b"<container/>")
    return buffer.getvalue()


EPUB_BYTES = make_epub_fixture()
COVER_BYTES = b"synthetic cover fixture"
def make_printables_fixture():
    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("printables/README.txt", b"Print at 100 percent")
        archive.writestr("printables/Coffee_Pot_Snake_Paper_Cryptex.svg", b"<svg/>")
        archive.writestr("printables/Participant_FieldKit_Worksheet.md", b"# Worksheet")
        archive.writestr("printables/Security_Assessment_Playbook.md", b"# Assessment")
        archive.writestr("printables/Data_Stewardship_and_Offline_Systems.md", b"# Stewardship")
        archive.writestr("printables/Researching_Public_Harm_and_Accountability.md", b"# Research")
    return buffer.getvalue()


PRINTABLES_BYTES = make_printables_fixture()
SIGNING_KEY = Ed25519PrivateKey.generate()
SIGNING_FINGERPRINT = key_fingerprint(SIGNING_KEY.public_key())
PUBLIC_KEY_BYTES = SIGNING_KEY.public_key().public_bytes(
    serialization.Encoding.PEM,
    serialization.PublicFormat.SubjectPublicKeyInfo,
)
MANIFEST_BYTES, SIGNATURE_BYTES, _PUBLIC_KEY, _FINGERPRINT = sign_manifest(
    {
        "edition_id": "a" * 24,
        "profile": "field-technician",
        "issued_utc": "2026-10-13T00:00:00+00:00",
        "source_revision": "b" * 40,
        "coffee_cipher_sha256": hashlib.sha256(b"next-edition-cipher").hexdigest(),
        "artifacts": {
            "pdf": {"file": "Raspberry-Pi-Field-Guide-" + "a" * 24 + ".pdf", "sha256": hashlib.sha256(PDF_BYTES).hexdigest(), "size": len(PDF_BYTES)},
            "epub": {"file": "Raspberry-Pi-Field-Guide-" + "a" * 24 + ".epub", "sha256": hashlib.sha256(EPUB_BYTES).hexdigest(), "size": len(EPUB_BYTES)},
            "cover": {"file": "cover.png", "sha256": hashlib.sha256(COVER_BYTES).hexdigest(), "size": len(COVER_BYTES)},
            "printables": {"file": "field-hackathon-printables.zip", "sha256": hashlib.sha256(PRINTABLES_BYTES).hexdigest(), "size": len(PRINTABLES_BYTES)},
        },
    },
    SIGNING_KEY,
)


def make_app_fixture():
    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("fieldkit", b"standalone fixture")
        archive.writestr("THIRD_PARTY_NOTICES.md", b"notices")
        archive.writestr("LICENSES/CC0-1.0.txt", b"license")
        archive.writestr("LICENSES/CC0-SCOPE.md", b"scope")
        archive.writestr("LICENSES/PyInstaller-COPYING.txt", b"packager license")
    return buffer.getvalue()


APP_BYTES = make_app_fixture()


class PortalHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        return

    def _send(self, status, body, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length))
        if self.path == "/v1/bootstrap":
            self._send(200, json.dumps({"cipher": "starter-cipher"}).encode())
            return
        if self.path == "/v1/editions":
            if self.headers.get("Authorization") != "Coffee-Cipher starter-cipher":
                self._send(401, b"{}")
                return
            self._send(200, json.dumps({
                "edition_id": "a" * 24,
                "cipher": "next-edition-cipher",
                "downloads": {
                    "pdf": {"url": "/files/book.pdf", "sha256": hashlib.sha256(PDF_BYTES).hexdigest()},
                    "epub": {"url": "/files/book.epub", "sha256": hashlib.sha256(EPUB_BYTES).hexdigest()},
                    "cover": {"url": "/files/cover.png", "sha256": hashlib.sha256(COVER_BYTES).hexdigest()},
                    "printables": {"url": "/files/printables.zip", "sha256": hashlib.sha256(PRINTABLES_BYTES).hexdigest()},
                    "manifest": {"url": "/files/" + MANIFEST_NAME, "sha256": hashlib.sha256(MANIFEST_BYTES).hexdigest()},
                    "signature": {"url": "/files/" + SIGNATURE_NAME, "sha256": hashlib.sha256(SIGNATURE_BYTES).hexdigest()},
                    "public-key": {"url": "/files/" + PUBLIC_KEY_NAME, "sha256": hashlib.sha256(PUBLIC_KEY_BYTES).hexdigest()},
                },
                "signing_key_fingerprint": SIGNING_FINGERPRINT,
            }).encode())
            return
        self._send(404, b"{}")

    def do_GET(self):
        if self.headers.get("Authorization") not in {"Coffee-Cipher next-edition-cipher", "Coffee-Cipher starter-cipher"}:
            self._send(401, b"{}")
            return
        if self.path == "/v1/apps":
            self._send(200, json.dumps({"apps": {"linux-x86_64": hashlib.sha256(APP_BYTES).hexdigest()}}).encode())
        elif self.path == "/v1/apps/linux-x86_64":
            self._send(200, APP_BYTES, "application/zip")
        elif self.path == "/files/book.pdf":
            self._send(200, PDF_BYTES, "application/pdf")
        elif self.path == "/files/book.epub":
            self._send(200, EPUB_BYTES, "application/epub+zip")
        elif self.path == "/files/cover.png":
            self._send(200, COVER_BYTES, "image/png")
        elif self.path == "/files/printables.zip":
            self._send(200, PRINTABLES_BYTES, "application/zip")
        elif self.path == "/files/" + MANIFEST_NAME:
            self._send(200, MANIFEST_BYTES, "application/json")
        elif self.path == "/files/" + SIGNATURE_NAME:
            self._send(200, SIGNATURE_BYTES, "application/octet-stream")
        elif self.path == "/files/" + PUBLIC_KEY_NAME:
            self._send(200, PUBLIC_KEY_BYTES, "application/x-pem-file")
        else:
            self._send(404, b"{}")


class PortalClientTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), PortalHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.origin = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def test_origin_validation(self):
        self.assertEqual(portal_origin(self.origin, allow_local_http=True), self.origin)
        with self.assertRaises(PortalClientError):
            portal_origin("http://example.com", allow_local_http=True)
        with self.assertRaises(PortalClientError):
            portal_origin("https://example.com/path")

    def test_edition_auth_downloads_and_hash_checks(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = create_edition(
                "starter-cipher", "field-technician", Path(temporary),
                origin=self.origin, trusted_fingerprint=SIGNING_FINGERPRINT,
            )
            self.assertEqual(result["edition_id"], "a" * 24)
            pdf = Path(result["files"]["pdf"]["path"])
            epub = Path(result["files"]["epub"]["path"])
            self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
            self.assertEqual(epub.read_bytes(), EPUB_BYTES)
            self.assertEqual((pdf.parent / "coffee-cipher.txt").read_text().strip(), "next-edition-cipher")
            self.assertTrue((pdf.parent / "edition.json").is_file())
            self.assertTrue((pdf.parent / MANIFEST_NAME).is_file())
            self.assertEqual(json.loads((pdf.parent / "edition.json").read_text())["signature_verified"], True)
            verified = verify_edition_directory(pdf.parent, SIGNING_FINGERPRINT)
            self.assertEqual(verified["edition_id"], "a" * 24)

    def test_signed_manifest_detects_changed_book_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = create_edition(
                "starter-cipher", "field-technician", Path(temporary),
                origin=self.origin, trusted_fingerprint=SIGNING_FINGERPRINT,
            )
            pdf = Path(result["files"]["pdf"]["path"])
            pdf.write_bytes(PDF_BYTES + b"changed")
            with self.assertRaisesRegex(ValueError, "size does not match|SHA-256 does not match"):
                verify_edition_directory(pdf.parent, SIGNING_FINGERPRINT)

    def test_standalone_bundle_uses_portal_hash_and_same_origin(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = download_standalone("linux-x86_64", "starter-cipher", Path(temporary), origin=self.origin)
            self.assertEqual(path.read_bytes(), APP_BYTES)


if __name__ == "__main__":
    unittest.main()
