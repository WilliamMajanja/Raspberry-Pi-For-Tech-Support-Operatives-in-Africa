# CPIP-: Coffee Pot Internet Protocol

[CPIP-](https://github.com/WilliamMajanja/CPIP-) is William Majanja’s independent **Coffee Pot Internet Protocol** project. It is not an official Kali package or a preinstalled Kali tool. It builds on the deliberately whimsical HTCPCP standards for coffee and tea and describes additional networking, messaging, dashboard, and defensive features.

This chapter is a reader’s guide to understanding and evaluating the project. It distinguishes the repository’s stated design goals from independently verified properties. The documentation checked for this edition is the project’s public `master` branch as viewed on **12 October 2026**; the repository’s README, package metadata, and release notes show version drift. For reproducibility, choose and record a specific reviewed commit before following version-dependent steps.

## What “zero dependency” means here

This book is static Markdown and does not need a site generator or extra documentation packages. CPIP- itself is **not zero-dependency**: its current `pyproject.toml` declares Python 3.10+ plus required Python packages, including `cryptography`, `numpy`, and `pqcrypto`; setuptools is its build backend. The TUI, rich CLI, and HSM integrations add optional dependencies. Check the exact revision’s [`pyproject.toml`](https://github.com/WilliamMajanja/CPIP-/blob/master/pyproject.toml) before installing.

## The project’s stated design goals

The project’s [Blackpaper](https://github.com/WilliamMajanja/CPIP-/blob/master/blackpaper.md) describes goals including:

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

## Safe starting point

Begin with a source review and a disposable, isolated environment. Do not expose a fresh instance to a network: project documentation describes defaults that may bind beyond loopback and enable services or discovery. For the first walkthrough, keep the service on `127.0.0.1`, disable mesh and optional transports, and use non-sensitive test data. Do not run deployment scripts as root without reading and understanding every change they make.

> **Research project, not an assurance claim:** the repository describes some features as FIPS-aligned or defensive, but its own security policy says CPIP is not a FIPS-validated cryptographic module. Its custom Kyber/ML-KEM variant is explicitly non-FIPS. No independent security audit is established by the material reviewed for this guide.

## Primary sources

- [CPIP- repository](https://github.com/WilliamMajanja/CPIP-)
- [README and quick start](https://github.com/WilliamMajanja/CPIP-/blob/master/README.md)
- [Quick Start](https://github.com/WilliamMajanja/CPIP-/blob/master/QUICKSTART.md)
- [Usage examples](https://github.com/WilliamMajanja/CPIP-/blob/master/EXAMPLES.md)
- [Security policy](https://github.com/WilliamMajanja/CPIP-/blob/master/SECURITY.md)
- [Blackpaper](https://github.com/WilliamMajanja/CPIP-/blob/master/blackpaper.md)
- [RFC 2324: HTCPCP](https://www.rfc-editor.org/rfc/rfc2324)
- [RFC 7168: HTCPCP-TEA](https://www.rfc-editor.org/rfc/rfc7168)
