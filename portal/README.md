# CPIP Book Portal Deployment

The CPIP Book Portal is the only official host for personalized PDFs/EPUBs and standalone generator downloads. Source Markdown and original CC0-scoped tools remain public in GitHub; the repository does not store generated book binaries.

## Architecture

```text
Reader / standalone FieldKit client
            │ HTTPS + Coffee-Cipher bearer credential
            ▼
Caddy on the CPIP Book Portal domain
            │ loopback only
            ▼
Book Portal gateway :4310 ── SQLite + local hash-chain issuance ledger
            │ authenticated loopback HMAC API
            ▼
CPIP server :4180 ── CoffeeCipher/CovertChannel encoding and decoding
```

The CPIP service is not exposed directly. The portal gateway is the only public application surface and authenticates every edition, generator, and file-download operation. The public landing page and `PORTAL-0` starter puzzle are intentionally accessible so a new reader can obtain the first cipher. The starter answer is a puzzle gate, not identity verification; it can be shared.

The cipher is a bearer credential. It gates portal actions; it does not encrypt the book. The issued book prints its next Coffee Cipher so its owner can use the portal again. Copies may be shared, consistent with the no-DRM policy and CC0 scope.

## CPIP service configuration

Install the CPIP project at an explicitly reviewed commit and follow its own dependency/license notes. The current CPIP manifest declares runtime packages; it is **not zero-dependency**. The sample [`cpip.env.sample`](cpip.env.sample) binds CPIP to loopback, enables only the local CoffeeCipher/CovertChannel operation needed for edition ciphers, and disables mesh, radio, mobile, satellite, discovery, NTP, and cover traffic.

Set one persistent `CPIP_COVERT_KEY` in the CPIP and portal service environments. Use a second independent random `CPIP_BOOK_TOKEN_PEPPER` for portal credential digests. Store both in the host's protected secret store, not this repository. The CPIP key must survive restarts so existing ciphers remain decodable.

CPIP's built-in RPC HMAC gate protects only some mutating endpoints; it does not protect all GET routes or the dashboard. Binding CPIP to loopback and exposing only the portal gateway are mandatory. The portal invokes only the specific local encode/decode API paths it needs. No other CPIP routes are proxied.

## Portal host setup

1. Provision a Linux host, DNS name, and HTTPS-capable public endpoint. The CPIP domain is not configured in this source tree yet.
2. Install the pinned CPIP project and its declared dependencies in a dedicated environment.
3. Install Python 3.11+, Pandoc, Chromium, and Caddy on the portal host. These are maintainer/server dependencies; readers do not install them to read the book or run the standalone FieldKit utilities.
4. Copy [`cpip.env.sample`](cpip.env.sample) and [`portal.env.sample`](portal.env.sample) into a root-readable-only service configuration outside the repository; generate fresh keys and set the actual domain.
5. Run CPIP and the portal as separate unprivileged services. Use [`caddy.Caddyfile.example`](caddy.Caddyfile.example) to terminate HTTPS and reverse-proxy only to `127.0.0.1:4310`.
6. Confirm the CPIP backend is not reachable from another host, the portal requires a cipher except for bootstrap, files are not available at alternate public URLs, and no logs contain ciphers or personal data.
7. Perform an independent security review and integration test before advertising the origin as secured.

## Standalone FieldKit bundles

Build each target on a matching OS/architecture runner with the optional build-only PyInstaller dependency:

```bash
python3 tools/package_fieldkit.py --target linux-arm64 --output-dir ./build/release
```

The command refuses cross-compilation and smoke-tests the resulting executable. Repeat on Linux x86-64, Windows x86-64, macOS ARM64, and macOS x86-64 runners. It creates a `.zip` containing the executable, CC0 scope, and third-party notices, plus a SHA-256 manifest. Transfer these files to the portal host through an operator-controlled secure channel and install them locally:

```bash
python3 -m portal.admin publish-app linux-arm64 ./build/release/fieldkit-linux-arm64.zip ./build/release/fieldkit-linux-arm64.zip.manifest.json
```

The CPIP Portal serves the verified bundle only after a Coffee Cipher check. Do not attach these application bundles or personalized PDFs/EPUBs to GitHub releases or other public mirrors if the CPIP site is to remain the canonical official distributor.

The templates are not a deployment approval. CPIP's security claims are project-stated and have not been independently validated by this guide; CPIP is not a FIPS-validated cryptographic module.

## API and issuance ledger

- `POST /v1/bootstrap`: checks the public starter answer and returns a first CPIP Coffee Cipher.
- `POST /v1/editions`: requires a valid cipher, chooses a reading profile, generates a unique edition ID, cipher, and cover seed, then builds the PDF/EPUB.
- `GET /v1/editions/{id}/pdf|epub|cover`: requires the matching edition cipher and verifies the stored artifact digest before sending.
- Browser forms are available at `/`, `/starter`, `/issue`, and `/download`; all are same-origin and do not put ciphers in URLs.

To revoke a leaked/retired cipher, run `python3 -m portal.admin revoke EDITION_ID` on the portal host with `CPIP_BOOK_DATA_DIR` and `CPIP_BOOK_TOKEN_PEPPER` set from the protected service environment. Revocation blocks future portal operations for that edition; it cannot retrieve or lock copies already downloaded.

The local SQLite hash-chain ledger stores edition IDs, profiles, cipher hashes, artifact hashes, and timestamps—not names or email addresses. It is a single-site tamper-evident log, not a decentralized blockchain. Back up the database and issuance data securely; a broken chain causes the portal to fail closed.

## Privacy and copy policy

No registration, reader name, or email is required. Rate-limit state is memory-only. Reverse-proxy access logs should be disabled or privacy-minimized. Cipher tokens are bearer credentials and are included in the personalized edition; sharing a book shares its token. Revoke or rotate a token if it is exposed. Since the source and original material are CC0-scoped, this portal is the canonical distributor, not copy protection.
