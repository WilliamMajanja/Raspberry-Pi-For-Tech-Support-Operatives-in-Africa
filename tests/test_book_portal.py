import hashlib
import io
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from fieldkit.signatures import verify_edition_directory
from portal.book_portal import BookPortal, PortalError, PortalHTTPServer, STARTER_ANSWER
from tools.build_books import build_printables_bundle


class FakeCPIP:
    def encode_token(self, edition_id, token):
        return f"fake:{edition_id}:{token}"

    def decode_token(self, cipher):
        prefix, edition_id, token = cipher.split(":", 2)
        if prefix != "fake":
            raise ValueError("invalid cipher")
        return edition_id, token


class TestBookPortal(BookPortal):
    def _build(self, edition_id, profile, cipher, cover_seed):
        base = self.data_dir / "editions" / edition_id
        base.mkdir(parents=True, mode=0o700)
        pdf = b"%PDF-1.4\nsynthetic test artifact\n"
        epub_buffer = io.BytesIO()
        with zipfile.ZipFile(epub_buffer, "w") as archive:
            info = zipfile.ZipInfo("mimetype")
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, b"application/epub+zip")
        epub = epub_buffer.getvalue()
        cover = b"synthetic png fixture"
        paths = {"pdf": ("book.pdf", pdf), "epub": ("book.epub", epub), "cover": ("cover.png", cover)}
        result = {}
        for kind, (name, data) in paths.items():
            (base / name).write_bytes(data)
            result[kind] = (f"editions/{edition_id}/{name}", hashlib.sha256(data).hexdigest())
        printables = build_printables_bundle(base)
        result["printables"] = (
            f"editions/{edition_id}/{printables.name}",
            hashlib.sha256(printables.read_bytes()).hexdigest(),
        )
        return result


class BookPortalTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        answer_hash = hashlib.sha256(STARTER_ANSWER.encode()).hexdigest()
        self.private_key = Ed25519PrivateKey.generate()
        self.signing_key_path = Path(self.temporary.name) / "signing-key.pem"
        self.signing_key_path.write_bytes(
            self.private_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
        self.signing_key_path.chmod(0o600)
        self.portal = TestBookPortal(
            Path(self.temporary.name), FakeCPIP(), b"t" * 32, answer_hash,
            signing_private_key_path=self.signing_key_path,
            source_revision="a" * 40,
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_public_starter_issues_cipher_then_edition_requires_it(self):
        first = self.portal.bootstrap(STARTER_ANSWER, "test-client")
        self.assertIn("cipher", first)
        result = self.portal.create_edition(first["cipher"], "field-technician", "test-client")
        self.assertEqual(result["profile"], "field-technician")
        self.assertEqual(
            set(result["downloads"]),
            {"pdf", "epub", "cover", "printables", "manifest", "signature", "public-key"},
        )
        self.assertNotEqual(result["cipher"], first["cipher"])
        self.assertEqual(self.portal.store.verify_chain(), [])
        edition_dir = self.portal.data_dir / "editions" / result["edition_id"]
        verified = verify_edition_directory(edition_dir, result["signing_key_fingerprint"])
        self.assertEqual(verified["edition_id"], result["edition_id"])
        self.assertEqual(verified["source_revision"], "a" * 40)

    def test_missing_or_wrong_cipher_is_rejected(self):
        with self.assertRaises(PortalError):
            self.portal.create_edition("wrong", "field-technician", "test-client")

    def test_download_cipher_is_bound_to_its_edition(self):
        first = self.portal.bootstrap(STARTER_ANSWER, "test-client")
        result = self.portal.create_edition(first["cipher"], "field-technician", "test-client")
        with self.assertRaises(PortalError):
            self.portal.artifact(result["edition_id"], "pdf", first["cipher"])
        path, mime, digest = self.portal.artifact(result["edition_id"], "pdf", result["cipher"])
        self.assertEqual(mime, "application/pdf")
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)

    def test_standalone_app_delivery_is_cipher_gated(self):
        starter = self.portal.bootstrap(STARTER_ANSWER, "test-client")
        app_path = self.portal.app_dir / "fieldkit-linux-arm64.zip"
        app_path.write_bytes(b"synthetic app bundle")
        with self.assertRaises(PortalError):
            self.portal.app_artifact("linux-arm64", "")
        path, mime, digest = self.portal.app_artifact("linux-arm64", starter["cipher"])
        self.assertEqual(mime, "application/zip")
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)

    def test_revocation_blocks_portal_access_but_preserves_local_chain(self):
        starter = self.portal.bootstrap(STARTER_ANSWER, "test-client")
        edition = self.portal.create_edition(starter["cipher"], "field-technician", "test-client")
        count = self.portal.store.revoke_edition_cipher(edition["edition_id"])
        self.assertEqual(count, 1)
        with self.assertRaises(PortalError):
            self.portal.artifact(edition["edition_id"], "pdf", edition["cipher"])
        self.assertEqual(self.portal.store.verify_chain(), [])

    def test_http_gate_requires_cipher_for_downloads(self):
        server = PortalHTTPServer(self.portal, 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        origin = f"http://127.0.0.1:{server.server_port}"
        try:
            with urllib.request.urlopen(origin + "/", timeout=2) as response:
                self.assertEqual(response.status, 200)
            try:
                urllib.request.urlopen(origin + "/v1/editions/" + "a" * 24 + "/pdf", timeout=2)
                self.fail("download without a Coffee Cipher should be rejected")
            except urllib.error.HTTPError as error:
                self.assertEqual(error.code, 401)

            starter = urllib.request.Request(
                origin + "/v1/bootstrap",
                data=json.dumps({"answer": STARTER_ANSWER}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(starter, timeout=2) as response:
                cipher = json.loads(response.read())["cipher"]
            issue = urllib.request.Request(
                origin + "/v1/editions",
                data=json.dumps({"profile": "field-technician"}).encode(),
                headers={"Content-Type": "application/json", "Authorization": "Coffee-Cipher " + cipher},
                method="POST",
            )
            with urllib.request.urlopen(issue, timeout=2) as response:
                edition = json.loads(response.read())
            download = urllib.request.Request(
                origin + edition["downloads"]["pdf"]["url"],
                headers={"Authorization": "Coffee-Cipher " + edition["cipher"]},
            )
            with urllib.request.urlopen(download, timeout=2) as response:
                self.assertTrue(response.read().startswith(b"%PDF-"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
