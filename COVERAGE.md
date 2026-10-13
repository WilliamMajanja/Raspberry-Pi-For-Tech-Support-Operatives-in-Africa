# Coverage and Editorial Status

This living edition is digital-first. Each PDF/EPUB is a dated snapshot; consult the current source and linked primary references before using time-sensitive guidance. This page records subject coverage and verification limits so omitted or untested material is visible.

## Field-guide coverage

| Area | Core outcomes | Limits and evidence |
| --- | --- | --- |
| Raspberry Pi setup | Identify hardware, choose a supported image, prepare storage, boot safely, and record a baseline. | Hardware-specific steps must match the exact board and current vendor documentation. |
| Linux basics | Explain the kernel/user-space boundary, files and permissions, shell usage, services, logs, and networking. | Commands identify platform assumptions; optional utilities are labeled. |
| Technical support operations | Triage, gather evidence, make reversible changes, protect data, recover, and hand over. | Site policy and the service owner take precedence. |
| Security operations | Set written scope, conduct low-impact assessment, document findings, remediate, and retest. | No unauthorized access, persistence, evasion, credential capture, or destructive validation. |
| Peace-support information systems | Support safe and accessible mine-action, child-protection, and WPS data workflows. | Orientation only; never replaces qualified specialists, mandates, or national standards. |
| Informatics and public interest | Assess data provenance, privacy, validation, health claims, and corporate-accountability evidence. | Linked applications are not certified by this guide. |
| FieldKit and cryptex | Use original offline support utilities and a printable multi-step learning puzzle. | Hashes and puzzle encodings do not establish authenticity or protect real secrets. The paper prop is non-locking; the OpenSCAD model has not been printed or fit-tested. |
| Hackathon delivery | Run four role-scoped tracks with synthetic data, team roles, scoring, handover, and a CPIP edition flow. | A demo is not deployment approval. Official portal hosting and release-key provisioning require operator setup. |
| Signed editions | Verify a detached publisher signature over the edition manifest and check the PDF/EPUB digests. | The CPIP Coffee Cipher is a separate portal credential, not a digital signature or proof of identity. Trust the signing key only through its independently published fingerprint. |

## Evidence labels

- **Tested locally:** the stated command or program behavior ran on the named platform/version.
- **Source reviewed:** the cited upstream source was examined; no runtime test is implied.
- **Platform-specific:** behavior depends on a named OS, board, service, or policy.
- **Not tested:** the page describes a concept or source but has not validated runtime behavior.
- **Optional component:** the item has a separate dependency, hardware, or service requirement.

The label applies only to the step or claim identified—not to the security of a complete system.

## Recipe completeness checklist

Each practical recipe should include the task, intended user, prerequisites, authorized scope, steps, expected result, verification, recovery/stop procedure, privacy notes, dated sources, and test status. If an element does not apply, say why. If a source or hardware test is unavailable, mark that limit rather than implying completeness.

## CPIP Book Portal status

The CPIP Book Portal source and deployment configuration are maintained separately from the static book. A local end-to-end smoke test has generated a personalized PDF/EPUB through CPIP v6.0.3 commit `df93a5258a0d9e5297d30bd6b630f299969ec8bb`; mesh/radio/mobile/satellite/discovery transports were disabled and the service bound to loopback. The portal itself is not deployed. Its public origin, HTTPS termination, all-route cipher gate, download authorization, logging/privacy behavior, and direct-backend isolation still require host configuration and site-level review. CPIP- is not a FIPS-validated cryptographic module.

## Release status

The standalone FieldKit `linux-arm64` target has passed a local PyInstaller build and smoke test. Linux x86-64, Windows x86-64, and macOS ARM64/x86-64 require their matrix builds before they are advertised as supported. Each release records its commit, edition ID, PDF/EPUB hashes, app target matrix, source dates, and known issues. The CPIP site has no configured public domain or TLS deployment in this workspace, so no official download service is live yet.
