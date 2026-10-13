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

An official edition includes its edition ID, profile, build/source revision, PDF/EPUB SHA-256 digests, and the associated hash-chain ledger record. Verify the release manifest before archiving a downloaded copy. The local hash-chain ledger is an audit aid, not a decentralized blockchain or a guarantee that a copy cannot be changed or shared.
