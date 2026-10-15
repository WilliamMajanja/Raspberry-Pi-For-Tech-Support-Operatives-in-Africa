# CPIP-: Coffee Pot Internet Protocol

[CPIP-](https://github.com/WilliamMajanja/CPIP-) is William Majanja’s independent **Coffee Pot Internet Protocol** project. It is not an official Kali package or a preinstalled Kali tool. It builds on the deliberately whimsical HTCPCP standards for coffee and tea and describes additional networking, messaging, dashboard, and defensive features.

This chapter is a reader’s guide to understanding and evaluating the project. It distinguishes repository-stated design goals from independently verified properties. The protocol/runtime smoke test used CPIP code commit `df93a5258a0d9e5297d30bd6b630f299969ec8bb`; the RFC/request records and package-reference correction were reviewed at documentation commit `d865e88` on **15 October 2026**. The repository’s README, package metadata, and release notes have version drift. For reproducibility, choose and record an exact reviewed commit before following version-dependent steps.

## What “zero dependency” means here

This book is static Markdown and does not need a site generator or extra documentation packages. CPIP- itself is **not zero-dependency**: at the reviewed v6.0.3 source snapshot, `pyproject.toml` declares Python 3.10+ and required Python packages including `cryptography`, `numpy`, and `pqcrypto`; setuptools is its build backend. The TUI, rich CLI, and HSM integrations add optional dependencies. See the [pinned `pyproject.toml`](https://github.com/WilliamMajanja/CPIP-/blob/d865e88/pyproject.toml) before installing.

## The project’s stated design goals

The project’s [Blackpaper](https://github.com/WilliamMajanja/CPIP-/blob/d865e88/blackpaper.md) describes goals including:

- following the HTCPCP/HTCPCP-TEA vocabulary;
- operating a logical mesh over multiple transport types;
- providing an operator-facing CLI and dashboard;
- experimenting with cover traffic and active network defense;
- combining classical cryptographic algorithms with a research post-quantum component.

These are **project-stated goals**, not evidence of effectiveness, safety, privacy, standards conformance, or security review. A design goal such as “plausible cover traffic” does not make traffic undetectable. A tool’s feature label does not prove the feature works as claimed.

## Guide to this chapter

- [Understand the architecture, protocol, and project principles](Architecture_and_Principles.md)
- [Set up and try a local-only instance](Local_Setup.md)
- [Configure, operate, and assess security](Operations_and_Security.md)
- [Distinguish IETF RFCs from CPIP RFF/RFC-CR/spec records](Architecture_and_Principles.md#ietf-rfcs-versus-cpip-project-rfcs)
- [CPIP project RFF/RFC-CR templates and draft inventory](https://github.com/WilliamMajanja/CPIP-/blob/d865e88/specs/README.md)

## Safe starting point

Begin with a source review and a disposable, isolated environment. Do not expose a fresh instance to a network: project documentation describes defaults that may bind beyond loopback and enable services or discovery. For the first walkthrough, keep the service on `127.0.0.1`, disable mesh and optional transports, and use non-sensitive test data. Do not run deployment scripts as root without reading and understanding every change they make.

> **Research project, not an assurance claim:** the repository describes some features as FIPS-aligned or defensive, but its own security policy says CPIP is not a FIPS-validated cryptographic module. Its custom Kyber/ML-KEM variant is explicitly non-FIPS. No independent security audit is established by the material reviewed for this guide.

## Primary sources

- [CPIP- repository](https://github.com/WilliamMajanja/CPIP-)
- [README and quick start](https://github.com/WilliamMajanja/CPIP-/blob/d865e88/README.md)
- [Quick Start](https://github.com/WilliamMajanja/CPIP-/blob/d865e88/QUICKSTART.md)
- [Usage examples](https://github.com/WilliamMajanja/CPIP-/blob/d865e88/EXAMPLES.md)
- [Security policy](https://github.com/WilliamMajanja/CPIP-/blob/d865e88/SECURITY.md)
- [Blackpaper](https://github.com/WilliamMajanja/CPIP-/blob/d865e88/blackpaper.md)
- [RFC 2324: HTCPCP](https://www.rfc-editor.org/rfc/rfc2324)
- [RFC 7168: HTCPCP-TEA](https://www.rfc-editor.org/rfc/rfc7168)
