# Source Listings: How to Read Them

The printed and EPUB editions include an annotated source appendix so the utilities and book-build infrastructure can be examined offline. It is assembled from the exact authored source files used for each build; generated PDFs and EPUBs are not embedded in themselves. A plain-language purpose and data-flow note precedes every file listing.

## System map

1. `SUMMARY.md` is the chapter-order source. `tools/build_books.py` checks that each maintained Markdown page is included, rebases cross-links, embeds the original SVG diagrams, and emits A5 PDF/EPUB plus a full-scale A4 printables ZIP.
2. `fieldkit.cli` is the command dispatcher. Local inventory, redaction, file manifests, and the local hash-chain ledger live in `fieldkit.core`; cover artwork is generated locally by `fieldkit.coffee_snake`.
3. `fieldkit.portal_client` speaks only to the configured same-origin HTTPS Book Portal. `portal.book_portal` validates Coffee Cipher access, requests the limited local encode/decode calls in `portal.cpip_adapter`, builds an edition, and checks the stored artifacts.
4. CPIP- produces the special Coffee Cipher bearer credential. Separately, the portal signs the canonical edition manifest with a publisher Ed25519 key. FieldKit verifies the signature against an independently obtained fingerprint and then checks every listed file hash; the signature is not proof of content correctness, participant identity, or DRM.
5. `tests/` exercises these boundaries with temporary files, synthetic records, and fake portal/CPIP services. The optional live-CPIP test runs only when explicitly configured. CI runs standard checks and native platform builds; it does not publish binaries.

## Reading and running the listings

- Read a file’s explanation first, then follow calls from its named entry point into the modules it imports.
- Sample `.env`, systemd, Caddy, and workflow settings are examples, not production values. They deliberately contain placeholders. Never place a production CPIP key, publisher private key, bearer cipher, real field record, or private key in this repository.
- `python3 -m unittest discover -s tests -v` runs the isolated test suite. `python3 tools/check_docs.py` checks Markdown links and parses Bash blocks but does not execute commands.
- `python3 tools/build_books.py --output-dir /tmp/field-book-preview` creates an unsigned local preview. Only the configured CPIP portal can issue a publisher-signed participant package.

The source appendix is documentary: opening the book does not execute its code. Prerequisites, trust boundaries, known limitations, and test status are described in each component README and in [Coverage and Editorial Status](../COVERAGE.md).
