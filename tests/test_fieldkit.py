import json
import tempfile
import unittest
from pathlib import Path

from fieldkit.core import (
    FieldKitError,
    append_issuance_record,
    create_manifest,
    local_inventory,
    redact_report,
    verify_issuance_ledger,
    verify_manifest,
    write_new_private_file,
)


class RedactionTests(unittest.TestCase):
    def test_redacts_common_secret_fields_and_private_key(self):
        report = (
            "password=example123 Authorization: Bearer abc.def\n"
            "-----BEGIN PRIVATE KEY-----\nprivate\n-----END PRIVATE KEY-----\n"
            "person@example.test"
        )
        scrubbed = redact_report(report)
        self.assertNotIn("example123", scrubbed)
        self.assertNotIn("abc.def", scrubbed)
        self.assertNotIn("private\n", scrubbed)
        self.assertNotIn("person@example.test", scrubbed)
        self.assertIn("[REDACTED PRIVATE KEY]", scrubbed)

    def test_network_identifiers_are_opt_in(self):
        report = "gateway 192.168.1.1 at aa:bb:cc:dd:ee:ff"
        self.assertIn("192.168.1.1", redact_report(report))
        scrubbed = redact_report(report, redact_network=True)
        self.assertNotIn("192.168.1.1", scrubbed)
        self.assertNotIn("aa:bb:cc:dd:ee:ff", scrubbed)


class ManifestTests(unittest.TestCase):
    def test_manifest_verifies_and_detects_change(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "data"
            root.mkdir()
            source = root / "sample.txt"
            source.write_text("synthetic fixture\n", encoding="utf-8")
            manifest_path = Path(temporary) / "manifest.json"
            manifest = create_manifest(root, manifest_path)
            self.assertEqual(len(manifest["files"]), 1)
            self.assertEqual(verify_manifest(root, manifest_path), [])
            source.write_text("changed fixture\n", encoding="utf-8")
            self.assertIn("SHA-256 mismatch: sample.txt", verify_manifest(root, manifest_path))

    def test_manifest_rejects_parent_traversal(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "root"
            root.mkdir()
            manifest = Path(temporary) / "unsafe.json"
            manifest.write_text(json.dumps({
                "schema": "fieldkit.manifest.v1",
                "algorithm": "sha256",
                "files": [{"path": "../outside", "size": 0, "sha256": "0" * 64}],
            }), encoding="utf-8")
            self.assertIn("unsafe manifest path: ../outside", verify_manifest(root, manifest))


class InventoryAndLedgerTests(unittest.TestCase):
    def test_inventory_omits_hostname_and_addresses(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "etc").mkdir()
            (root / "proc/device-tree").mkdir(parents=True)
            (root / "sys/class/net").mkdir(parents=True)
            (root / "etc/os-release").write_text('PRETTY_NAME="Test Linux"\nID=test\n', encoding="utf-8")
            (root / "proc/device-tree/model").write_bytes(b"Test Board\0")
            (root / "sys/class/net/eth0").mkdir()
            data = local_inventory(root)
            self.assertEqual(data["distribution"], "Test Linux")
            self.assertEqual(data["device_model"], "Test Board")
            self.assertEqual(data["interfaces"], ["eth0"])
            self.assertNotIn("hostname", data)
            self.assertNotIn("addresses", data)

    def test_issuance_chain_verifies_and_detects_tampering(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "editions.jsonl"
            first = append_issuance_record(path, "a" * 32, "b" * 64)
            second = append_issuance_record(path, "c" * 32, "d" * 64)
            self.assertEqual(first["index"], 0)
            self.assertEqual(second["index"], 1)
            self.assertEqual(second["previous_hash"], first["hash"])
            self.assertEqual(verify_issuance_ledger(path), [])
            path.write_text(path.read_text(encoding="utf-8").replace("b" * 64, "e" * 64), encoding="utf-8")
            self.assertTrue(verify_issuance_ledger(path))

    def test_private_output_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out.txt"
            write_new_private_file(output, b"first")
            with self.assertRaises(FieldKitError):
                write_new_private_file(output, b"second")


if __name__ == "__main__":
    unittest.main()
