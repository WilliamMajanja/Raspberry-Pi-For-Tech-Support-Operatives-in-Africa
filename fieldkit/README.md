# FieldKit

FieldKit is an original CC0-scoped support utility suite. Its local diagnostic and cover commands use Python's standard library and work offline. The optional `portal` commands contact only the CPIP Book Portal over HTTPS to obtain a personalized edition; they do not upload reports or personal profile data.

## Requirements and run

- Source execution: Python 3.11 or newer; no third-party modules.
- Standalone releases: per-platform ZIP bundles include the executable and runtime/component notices. Users do not install Python or CPIP packages separately; the CPIP service runs on the portal host.
- Standalone build dependency: maintainers use the pinned packages in `tools/requirements-build.txt`; these are not bundled as reader-side requirements.
- Tests: Python's built-in `unittest`.

From the repository root:

```bash
python3 -m fieldkit --help
python3 -m unittest discover -s tests
```

## Commands

### `inventory`

Collects a small local baseline: OS identity, kernel, architecture, Python version, available memory/disk estimate, device-tree model when available, and interface names. It omits host name, IP addresses, MAC addresses, and serial numbers. It reads local files only.

```bash
python3 -m fieldkit inventory
python3 -m fieldkit inventory --output ./support-inventory.json
```

The output file is created with owner-only permissions and is never overwritten. Review even sanitized reports before sharing.

### `scrub-report`

Writes a redacted copy of a text report without changing the original. It removes common secret assignments, bearer tokens, private-key blocks, and email addresses. `--redact-network` also removes IPv4 and MAC-looking strings; this can erase useful evidence, so inspect the result manually.

```bash
python3 -m fieldkit scrub-report raw.txt redacted.txt --redact-network
```

This is best-effort redaction, not a guarantee that all sensitive data is found. The source file remains unchanged; output paths are never overwritten.

### `manifest`

Creates and verifies SHA-256 manifests for local files. Symlinks and unsafe paths are rejected. A digest proves that bytes match a particular manifest; it does not prove who made the manifest or that the source is trustworthy.

```bash
python3 -m fieldkit manifest create ./backup ./backup-manifest.json
python3 -m fieldkit manifest verify ./restored-backup ./backup-manifest.json
```

### `ledger`

Appends edition fingerprints to a local, locked, hash-chained JSONL ledger and checks its sequence. The chain makes accidental or unsophisticated edits detectable relative to a trusted checkpoint. It is **not** a decentralized blockchain, a global uniqueness service, DRM, or proof that an edition is authentic unless its checkpoint is separately authenticated.

```bash
python3 -m fieldkit ledger append ./editions.jsonl EDITION_ID SHA256_DIGEST
python3 -m fieldkit ledger verify ./editions.jsonl
```

### `cover`

Creates original Coffee Pot Snake ASCII art, an SVG cover, and an edition manifest using local random seed material. Supply `--seed` when an exact reproducible cover is required; without it each run gets a fresh variant. The seed and edition ID identify the artwork only—they are not identity proofs or security secrets.

```bash
python3 -m fieldkit cover --output-dir ./my-cover
python3 -m fieldkit cover --seed 0123456789abcdef0123456789abcdef --output-dir ./repeatable-cover
```

### `portal`

`portal bootstrap` submits the public starter puzzle and saves the issued CPIP Coffee Cipher to a private local file. `portal edition` uses that cipher to request a reader path and download its personalized PDF/EPUB from the configured CPIP Book Portal. Downloads are checked against the portal's SHA-256 manifest and are saved in a new, owner-only edition directory.

```bash
python3 -m fieldkit portal bootstrap
python3 -m fieldkit portal edition --profile field-technician
python3 -m fieldkit portal app --target linux-arm64
```

Set `CPIP_BOOK_PORTAL_ORIGIN` to the official HTTPS portal origin. The cipher is a shareable bearer code, not DRM or proof of identity. If it is included in a book copy, anyone who has that copy can use the portal with it.

The standalone app bundles the local FieldKit client, not the CPIP server. Bundles for other supported targets are downloaded only through the CPIP Portal after a valid cipher is supplied.

## Operational limits

FieldKit performs no port scans, exploit attempts, credential capture, remote probes, service changes, or privileged actions. It does not replace organizational asset management, backup systems, malware scanners, or a professional security review. Run it as an ordinary user, use synthetic fixtures for practice, and protect reports according to local policy.
