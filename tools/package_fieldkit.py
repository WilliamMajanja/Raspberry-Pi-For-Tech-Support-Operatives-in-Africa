#!/usr/bin/env python3
"""Build and smoke-test FieldKit for the current host using PyInstaller.

PyInstaller is a build-time dependency only. Each OS/architecture must be built
on a matching runner; this script deliberately refuses cross-compilation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TARGETS = {
    ("Linux", "aarch64"): "linux-arm64",
    ("Linux", "arm64"): "linux-arm64",
    ("Linux", "x86_64"): "linux-x86_64",
    ("Windows", "AMD64"): "windows-x86_64",
    ("Windows", "x86_64"): "windows-x86_64",
    ("Darwin", "arm64"): "macos-arm64",
    ("Darwin", "x86_64"): "macos-x86_64",
}


def run(command: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {command[0]}")


def build(output_dir: Path, expected_target: str | None = None) -> tuple[Path, Path, Path]:
    target = TARGETS.get((platform.system(), platform.machine()))
    if target is None:
        raise RuntimeError(f"Unsupported build host: {platform.system()} {platform.machine()}")
    if expected_target and expected_target != target:
        raise RuntimeError(f"Refusing cross-build: host is {target}, requested {expected_target}")
    try:
        import PyInstaller  # noqa: F401
        pyinstaller_distribution = importlib.metadata.distribution("pyinstaller")
    except ImportError as error:
        raise RuntimeError("Install the pinned build-only dependencies from tools/requirements-build.txt.") from error

    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="fieldkit-pyinstaller-") as temporary:
        temp = Path(temporary)
        run([
            sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", "--onefile",
            "--name", "fieldkit", "--distpath", str(output_dir), "--workpath", str(temp / "work"),
            "--specpath", str(temp / "spec"), str(ROOT / "fieldkit_launcher.py"),
        ])

    binary = output_dir / ("fieldkit.exe" if platform.system() == "Windows" else "fieldkit")
    if not binary.is_file():
        raise RuntimeError("PyInstaller did not produce the expected executable.")
    run([str(binary), "--version"])
    with tempfile.TemporaryDirectory(prefix="fieldkit-smoke-") as temporary:
        run([str(binary), "cover", "--seed", "0123456789abcdef0123456789abcdef", "--output-dir", str(Path(temporary) / "cover")])

    binary_digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    bundle = output_dir / f"fieldkit-{target}.zip"
    bundle_binary_name = "fieldkit.exe" if platform.system() == "Windows" else "fieldkit"
    notice_files = (
        ROOT / "THIRD_PARTY_NOTICES.md",
        ROOT / "LICENSE",
        ROOT / "LICENSES" / "CC0-1.0.txt",
        ROOT / "LICENSES" / "CC0-SCOPE.md",
    )
    if any(not path.is_file() for path in notice_files):
        raise RuntimeError("A required license/notice file is missing from the bundle.")
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.write(binary, bundle_binary_name)
        for notice in notice_files:
            archive.write(notice, notice.relative_to(ROOT).as_posix())
        pyinstaller_license = next(
            (pyinstaller_distribution.locate_file(item) for item in pyinstaller_distribution.files or []
             if str(item).lower().endswith("/licenses/copying.txt")),
            None,
        )
        if not pyinstaller_license or not Path(pyinstaller_license).is_file():
            raise RuntimeError("PyInstaller's COPYING.txt license notice was not found in the build environment.")
        archive.write(pyinstaller_license, "LICENSES/PyInstaller-COPYING.txt")
        python_license_candidates = (
            Path(sys.base_prefix) / "LICENSE.txt",
            Path(sys.base_prefix) / "LICENSE",
            Path(f"/usr/share/doc/python{sys.version_info.major}.{sys.version_info.minor}/copyright"),
        )
        python_license = next((path for path in python_license_candidates if path.is_file()), None)
        if python_license:
            archive.write(python_license, "LICENSES/Python-Runtime-Notice.txt")
    with zipfile.ZipFile(bundle) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Packaged FieldKit archive failed integrity validation.")
        if bundle_binary_name not in archive.namelist():
            raise RuntimeError("Packaged FieldKit archive is missing the executable.")

    bundle_digest = hashlib.sha256(bundle.read_bytes()).hexdigest()
    manifest = {
        "target": target,
        "python": platform.python_version(),
        "fieldkit_version": "0.1.0",
        "pyinstaller_version": pyinstaller_distribution.version,
        "bundle": bundle.name,
        "bundle_sha256": bundle_digest,
        "binary": bundle_binary_name,
        "binary_sha256": binary_digest,
    }
    manifest_path = output_dir / f"{bundle.name}.manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return binary, bundle, manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "build" / "standalone")
    parser.add_argument("--target", choices=sorted(set(TARGETS.values())))
    args = parser.parse_args()
    try:
        binary, bundle, manifest = build(args.output_dir, args.target)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(binary)
    print(bundle)
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
