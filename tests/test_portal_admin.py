import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from portal.admin import _verify_app_bundle
from portal.book_portal import PortalError


class PortalAdminTests(unittest.TestCase):
    def test_bundle_and_manifest_are_checked_before_publish(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "fieldkit-linux-arm64.zip"
            binary = b"synthetic standalone executable"
            with zipfile.ZipFile(bundle, "w") as archive:
                archive.writestr("fieldkit", binary)
                archive.writestr("THIRD_PARTY_NOTICES.md", b"notices")
                archive.writestr("LICENSES/CC0-1.0.txt", b"license")
                archive.writestr("LICENSES/CC0-SCOPE.md", b"scope")
                archive.writestr("LICENSES/PyInstaller-COPYING.txt", b"packager license")
            manifest = root / "bundle.json"
            manifest.write_text(json.dumps({
                "target": "linux-arm64",
                "bundle": bundle.name,
                "bundle_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(),
                "binary": "fieldkit",
                "binary_sha256": hashlib.sha256(binary).hexdigest(),
            }), encoding="utf-8")
            bundle_hash, executable = _verify_app_bundle("linux-arm64", bundle, manifest)
            self.assertEqual(bundle_hash, hashlib.sha256(bundle.read_bytes()).hexdigest())
            self.assertEqual(executable, "fieldkit")

            manifest.write_text(manifest.read_text(encoding="utf-8").replace(bundle_hash, "0" * 64), encoding="utf-8")
            with self.assertRaises(PortalError):
                _verify_app_bundle("linux-arm64", bundle, manifest)


if __name__ == "__main__":
    unittest.main()
