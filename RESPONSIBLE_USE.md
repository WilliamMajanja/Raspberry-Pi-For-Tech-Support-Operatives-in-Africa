# Responsible Use

This guide is for Raspberry Pi and Linux technical support, peace-support information systems, and authorized security learning. A tool’s presence in Kali does not grant permission to use it against a system.

## Before a security test

1. Obtain written authorization from the system owner.
2. Define exact systems, accounts, network ranges, time windows, and allowed methods.
3. Use a disposable VM or isolated lab for examples and unfamiliar software.
4. Agree on rate limits, data handling, stop conditions, contacts, and reporting before testing.
5. Keep evidence and logs secure; avoid collecting data outside the agreed scope.
6. Stop if the work could disrupt a service or affect a system not explicitly in scope.

Do not use example targets, public IPs, wireless networks, accounts, or devices as practice systems unless you own them or have explicit authorization. Do not use this guide to evade monitoring, intercept someone else’s traffic, maintain unauthorized access, deploy malware, or conceal activity.

## Treat commands as actions

Read each command before running it. Pay special attention to:

- `sudo`, root shells, package-source changes, and service enablement;
- redirection operators (`>`, `>>`), recursive file operations, and paths supplied by variables;
- network listeners, port forwards, scanning options, and commands that contact remote hosts;
- scripts downloaded from the internet or copied from an old book;
- commands that handle passwords, keys, personal data, or sensitive logs.

Prefer inspection first, least privilege, clear output paths, and a tested rollback. A checksum is useful only when compared with an authentic checksum from the publisher. A self-signed TLS certificate or an algorithm name is not proof that a service is secure.

## Platform boundaries

Kali and Debian are related but not interchangeable. Use the package repositories, update instructions, and service guidance for the distribution actually installed. **Never add Kali repositories to Debian as a shortcut.** The Debian/KDE/Wayland environment used to author this guide is not a substitute for testing Kali-specific packages or workflows.

## Project-specific cautions

- The CPIP- chapter describes an independent research project. Keep initial tests loopback-only and treat the project’s security claims as unverified unless independently reviewed.
- The Jester-themed ransomware fork in the author portfolio is included only as a historical security artifact. Do not build or run it on a personal or production system.
- Health, election, land, and agricultural Informatics projects linked from the portfolio are described according to their repositories; this book does not claim clinical, electoral, legal, or operational validation.
- Mine-action, child-protection, and WPS content is an orientation for technical support roles. It is not EOD, mine-clearance, peacekeeper, child-protection, or gender-adviser training. Follow the current mandate, national standards, qualified specialists, and organizational safeguarding rules.
- Never approach, touch, identify, move, mark, or attempt to disable a suspected explosive item. Use locally approved emergency reporting procedures and trained authorities.
