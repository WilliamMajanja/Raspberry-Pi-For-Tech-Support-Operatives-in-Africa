"""Optional smoke test against a separately installed/pinned CPIP checkout.

Set CPIP_SOURCE_ROOT to the checkout root to run this test. All CPIP network,
radio, mesh, discovery, and satellite/mobile transports are disabled; the
server binds only to a temporary loopback port.
"""

from __future__ import annotations

import os
import hashlib
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request
from pathlib import Path

from portal.cpip_adapter import CPIPAdapter
from portal.book_portal import BookPortal, STARTER_ANSWER


class LiveCPIPIntegrationTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("CPIP_SOURCE_ROOT"), "set CPIP_SOURCE_ROOT for the optional live CPIP test")
    def test_local_cpip_coffee_cipher_roundtrip(self):
        source_root = Path(os.environ["CPIP_SOURCE_ROOT"]).resolve()
        server_script = source_root / "server.py"
        self.assertTrue(server_script.is_file(), "CPIP_SOURCE_ROOT must point to a CPIP checkout")

        with tempfile.TemporaryDirectory(prefix="fieldbook-cpip-test-") as data_dir:
            listener = socket.socket()
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
            listener.close()
            cpip_key = "fieldbook-cpip-local-test-key-0123456789abcdef"
            environment = os.environ.copy()
            environment.update({
                "HOME": data_dir,
                "CPIP_BIND": "127.0.0.1",
                "CPIP_PORT": str(port),
                "CPIP_SSL": "0",
                "CPIP_SSL_AUTO": "0",
                "CPIP_HTTP_REDIRECT": "0",
                "CPIP_RPC_AUTH": "1",
                "CPIP_COVERT": "1",
                "CPIP_COVERT_KEY": cpip_key,
                "CPIP_COVER_TRAFFIC": "0",
                "CPIP_MESH": "0",
                "CPIP_RADIO": "0",
                "CPIP_SAT": "0",
                "CPIP_MOBILE": "0",
                "CPIP_AVAHI": "0",
                "CPIP_NTP": "0",
                "CPIP_PROVIDER_DNS": "0",
                "CPIP_PROVIDER_MESH": "0",
                "CPIP_DISCOVERY_PORT": "0",
                "CPIP_MESH_PERSIST_DIR": str(Path(data_dir) / "mesh"),
            })
            process = subprocess.Popen(
                [sys.executable, str(server_script)],
                cwd=source_root,
                env=environment,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            try:
                ready = False
                for _ in range(80):
                    try:
                        with urllib.request.urlopen(f"http://127.0.0.1:{port}/cpip/status", timeout=0.5) as response:
                            if response.status == 200:
                                ready = True
                                break
                    except Exception:
                        time.sleep(0.25)
                self.assertTrue(ready, "CPIP loopback service did not become ready")
                client = CPIPAdapter(f"http://127.0.0.1:{port}", cpip_key)
                cipher = client.encode_token("a1b2c3d4e5f607182930abcd", "synthetic-coffee-token")
                self.assertEqual(
                    client.decode_token(cipher),
                    ("a1b2c3d4e5f607182930abcd", "synthetic-coffee-token"),
                )

                class SmokePortal(BookPortal):
                    def _build(self, edition_id, profile, cipher, cover_seed):
                        folder = self.data_dir / "editions" / edition_id
                        folder.mkdir(parents=True, mode=0o700)
                        artifacts = {
                            "pdf": ("preview.pdf", b"%PDF-1.4\nsynthetic fixture"),
                            "epub": ("preview.epub", b"synthetic EPUB fixture"),
                            "cover": ("cover.png", b"synthetic PNG fixture"),
                        }
                        result = {}
                        for kind, (name, content) in artifacts.items():
                            (folder / name).write_bytes(content)
                            result[kind] = (
                                f"editions/{edition_id}/{name}",
                                hashlib.sha256(content).hexdigest(),
                            )
                        return result

                starter_hash = hashlib.sha256(STARTER_ANSWER.encode("utf-8")).hexdigest()
                portal = SmokePortal(Path(data_dir) / "portal", client, b"x" * 32, starter_hash)
                starter = portal.bootstrap(STARTER_ANSWER, "loopback-test")
                edition = portal.create_edition(starter["cipher"], "field-technician", "loopback-test")
                path, _mime, digest = portal.artifact(edition["edition_id"], "pdf", edition["cipher"])
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
                self.assertEqual(portal.store.verify_chain(), [])
            finally:
                process.terminate()
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)


if __name__ == "__main__":
    unittest.main()
