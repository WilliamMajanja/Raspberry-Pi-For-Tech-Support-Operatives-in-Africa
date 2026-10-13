import hashlib
import io
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

from fieldkit.portal_client import PortalClientError, create_edition, download_standalone, portal_origin


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
                },
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
            result = create_edition("starter-cipher", "field-technician", Path(temporary), origin=self.origin)
            self.assertEqual(result["edition_id"], "a" * 24)
            pdf = Path(result["files"]["pdf"]["path"])
            epub = Path(result["files"]["epub"]["path"])
            self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
            self.assertEqual(epub.read_bytes(), EPUB_BYTES)
            self.assertEqual((pdf.parent / "coffee-cipher.txt").read_text().strip(), "next-edition-cipher")
            self.assertTrue((pdf.parent / "edition.json").is_file())

    def test_standalone_bundle_uses_portal_hash_and_same_origin(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = download_standalone("linux-x86_64", "starter-cipher", Path(temporary), origin=self.origin)
            self.assertEqual(path.read_bytes(), APP_BYTES)


if __name__ == "__main__":
    unittest.main()
