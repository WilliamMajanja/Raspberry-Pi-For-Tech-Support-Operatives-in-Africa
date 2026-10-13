# CPIP Book Portal

The CPIP Book Portal is the canonical distribution service for personalized PDF/EPUB editions and standalone generator downloads. Generated binaries are intentionally not stored in this GitHub repository. The portal origin is a deployment setting and is published only after its CPIP backend, TLS, all-route cipher gate, storage, and security review are configured.

The source book remains available as Markdown. Its original material is CC0-scoped as described in [`LICENSING.md`](../LICENSING.md); copies may be shared or rebuilt. A cipher gates CPIP application features and official issuance, not the text after a reader has received an edition. This project has no DRM.

## Local preview builds

The source book and core exercises require no software installation. Maintainers may make a local preview with Python 3.11+, Pandoc, and Chromium:

```bash
python3 tools/build_books.py --output-dir /tmp/field-book-preview
```

Local previews are not CPIP-issued editions: they have no CPIP Coffee Cipher or portal issuance record. They should not be presented as official personalized downloads.

## Edition verification

An official edition package includes its edition ID, reader profile, source revision, PDF/EPUB/cover/printables SHA-256 digests, canonical JSON manifest, detached Ed25519 signature, and publisher public key. The printables ZIP contains the exact-size A4 cryptex SVG and field worksheets. Obtain the signing fingerprint from an independent event or release channel, then verify the files with `fieldkit verify-edition EDITION_DIRECTORY --trusted-fingerprint FINGERPRINT` before archiving the copy. The Coffee Cipher is a separate CPIP bearer credential for future portal use; it is not the signature. The local hash-chain issuance ledger is an audit aid, not a decentralized blockchain or a guarantee that a copy cannot be changed or shared.

Local preview builds are unsigned and must not be presented as publisher-signed CPIP editions. The portal release key is not generated in this repository; the service operator provisions it outside Git and publishes its public-key fingerprint separately. Until the host, HTTPS, release key, and origin are configured and reviewed, no official signed download package is live.
