# Security Policy

This repository contains book source, original standard-library support utilities, a personalized-edition client, and CPIP Book Portal integration material. The portal is not considered production-secure merely because it uses CPIP or cryptography; see [Coverage and Editorial Status](COVERAGE.md) for deployment status. Report issues in CPIP itself to its upstream maintainers.

## Reporting a problem in this guide

For a privacy concern, exposed edition cipher, unsafe command, FieldKit defect, or portal security issue, do not post the sensitive material in a public issue. Contact the repository maintainer through GitHub's private reporting option if enabled. Otherwise, open a minimal issue asking for a private channel without including the credential, token, exploit detail, or personal data. A portal operator can revoke an edition cipher with `python3 -m portal.admin revoke EDITION_ID` on the host; this revokes portal access, not already downloaded CC0 content.

This repository has no published response-time guarantee. If an issue affects a third-party project or bundled runtime, contact that project's maintainers directly and follow its own disclosure process.
