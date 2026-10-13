# FieldKit: Offline Support Utilities

FieldKit is the book’s original, CC0-scoped collection of small support utilities. The source is written in Python using the standard library; no `pip install`, account, telemetry service, or network connection is required. Standalone application bundles are intended to include the interpreter so users do not need to install Python separately.

## What the utilities are for

| Utility | Support task | Default behavior |
| --- | --- | --- |
| `inventory` | Produce a minimal local device/platform inventory. | Read-only; omits secrets and avoids probing other devices. |
| `report-scrub` | Create a redacted copy of a text report before sharing. | Writes a new file; never overwrites the input. Review output manually. |
| `manifest` | Create or verify SHA-256 file manifests for a backup or transfer. | Reads files; never removes or encrypts them. |
| `ledger` | Verify or append an edition fingerprint to a local hash chain. | Local file only; no account or personal data. |

The companion [Coffee Pot Snake generator](../tools/coffee_snake.py) writes original ASCII/SVG artwork and a pseudonymous edition fingerprint. It uses the standard library, works offline, and accepts a seed for reproducible artwork. A seed identifies a variant; it is not an authentication secret.

These utilities are intended to help with ordinary support records, not to replace a managed inventory, backup system, endpoint-protection platform, or security review. Their standard-library source and usage are documented in [`fieldkit`](../fieldkit/README.md).

## Dependency and platform contract

- Reading the book, working through its worksheets, and solving the printed challenges require no software installation.
- The source CLI requires Python 3.11 or newer and only Python’s standard library.
- Planned standalone packages target Linux ARM64, Linux x86-64, Windows x86-64, macOS ARM64, and macOS x86-64. A target is called supported only after its build and smoke tests pass. Each binary is platform-specific and includes notices for bundled runtimes/build components.
- Local inventory, report sanitization, manifests, the issuance ledger, and cover art work without connecting to CPIP. Only optional personalized edition issuance uses the CPIP Book Portal.

## Safe-use recipe

1. Read `python3 -m fieldkit --help` or the installed binary's `--help` output.
2. Use a disposable test directory and synthetic sample records first.
3. Review the proposed input and output paths; the tool should state whether it reads or writes.
4. Check the resulting report/manifest before sharing or acting on it.
5. Keep the original data, a verified backup, and the required access controls.

FieldKit does not scan networks, exploit software, change system configuration, or collect personal information by default. It is not a cryptographic assurance product. Hash manifests detect accidental changes only when the expected manifest is obtained from a trusted source. The local issuance chain is not a distributed blockchain and cannot establish global uniqueness or prevent sharing.

## Verification status

The source test suite uses Python’s standard-library `unittest` and temporary fixtures. The supported OS/architecture matrix and exact release artifacts are recorded in [Coverage and Editorial Status](../COVERAGE.md); an untested platform is labeled rather than implied to work.
