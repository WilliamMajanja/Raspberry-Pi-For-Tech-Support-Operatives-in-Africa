# Raspberry Pi for Technical Support Operatives in Africa

### by William Majanja

An initiative of the **Hack with Raspberry Pi** community.

An open-source, zero-dependency field guide to supporting Raspberry Pi computers and Linux systems. It combines practical setup, troubleshooting, Bash recipes, security fundamentals, peace-support data responsibilities, and carefully scoped Kali/Linux material.

This guide is designed for technical support operatives working across Africa’s varied deployment environments. It does not assume that every site has the same power, connectivity, language, hardware supply, or support capacity; use the checklists to document local constraints and plan accordingly.

> **Unofficial:** this book is not produced, endorsed, or maintained by Raspberry Pi Ltd, Debian, Kali Linux, or OffSec. Use security tools only on systems and networks you own or have explicit authorization to assess.

## Start here

- [Book map and reading paths](SUMMARY.md)
- [Introduction and scope](1.%20Introduction/Introduction.md)
- [Raspberry Pi field-support guide](Raspberry%20Pi%20Field%20Support/README.md)
- [Linux foundations: kernel, Bash, and command-line recipes](0.%20Linux%20Foundations/README.md)
- [Peace Operations field-support context](Peace%20Operations%20Field%20Support/README.md)
- [Informatics, public health, and corporate accountability](Informatics%20and%20Public%20Interest/README.md)
- [Zero-dependency quizzes and CTF-style challenges](Challenges/README.md)
- [CPIP- user guide](16.%20CPIP-%20Guide/README.md)
- [William Majanja’s Informatics portfolio](1.%20Introduction/William_Majanja.md)

## What the guide covers

- **Raspberry Pi support:** model-aware setup, OS imaging, first boot, connectivity, troubleshooting, safe remote administration, updates, backups, and handover.
- **Linux foundations:** the kernel and user-space model, Bash scripting, and practical command-line recipes with explanations and checks.
- **African field operations:** offline-friendly procedures, locally adaptable communication and training, reliable recovery, privacy, and site-specific constraints without assuming one context fits all.
- **Peace-support and humanitarian context:** safe technical support for mine-action information systems, child-protection data, WPS participation, and relevant UN Security Council frameworks. This is not EOD, peacekeeper, or child-protection operational training.
- **Public-interest Informatics:** the Muainishi application series, health-data safeguards, corporate-accountability evidence, and careful distinctions between GE crops, specific traits, pesticide exposures, cancer hazards, and exposure-specific risks.
- **Security learning:** authorization, least privilege, isolated labs, source verification, and a historical, unreviewed Kali-tool archive kept separate from maintained guidance.
- **Self-study challenges:** Base and Crypto tracks with quiz prompts and flags, solvable from the book and standard shell tools without installing challenge software.
- **CPIP- and Informatics projects:** a version-aware guide to William Majanja’s Coffee Pot Internet Protocol and selected projects from both GitHub accounts.

The book is **zero-dependency to read and browse**: it is plain Markdown on GitHub, with no build system, required account, or site generator. The software and devices discussed in the guide may have their own dependencies.

## Design and reading experience

The book uses task-based recipes, progressive reading paths, topic categories, plain-language explanations, and source/license notes. This design takes inspiration from the local *Command Line Kung Fu* recipe reference and from [Babe’s Bookstore](https://babesbooks.store/), which describes itself as a category-based digital library with rights information. No text, code, books, or assets are copied from either source; the bookstore’s catalogue and rights claims are not independently audited here.

## Authoring and verification environment

The authoring desktop is **Debian GNU/Linux 13 (Trixie), ARM64, KDE Plasma 6.3.6, Wayland**. The kernel identifies Raspberry Pi ARM hardware, but this does not mean every model, OS image, peripheral, or field deployment has been tested. Kali-specific commands and Raspberry Pi OS features are labeled and must be checked on their own target platforms before being called tested.

## Kali Linux and CPIP-

Kali appears as a **specialized, optional security-lab platform**, not as the default operating system for routine Pi support. Check [Kali’s ARM documentation](https://www.kali.org/docs/arm/) for model and image compatibility. Never mix Kali package repositories into Debian or Raspberry Pi OS.

[CPIP-](https://github.com/WilliamMajanja/CPIP-) is William Majanja’s independent Coffee Pot Internet Protocol project, not an official Raspberry Pi, Debian, or Kali component. Its guide labels dependencies and source-stated security claims; it does not treat those claims as independently validated.

## Historical material

Older Kali-tool folders are retained as an **unreviewed historical archive**, not as current tool recommendations. Empty placeholders have been removed; surviving pages may contain obsolete commands, exploit/persistence examples, broken links, or third-party content. Browse the [archive note](LEGACY_ARCHIVE.md) before opening those folders. The curated contents list identifies the maintained reading path.

## Responsible use, credits, and licensing

Use a disposable VM or isolated lab for hands-on security work. Do not expose experimental services to a network, run unknown code with elevated privileges, or test against a third party without written authorization. See [Responsible Use](RESPONSIBLE_USE.md), [Code of Conduct](CODE_OF_CONDUCT.md), [Security Policy](SECURITY.md), and [Licensing and Provenance](LICENSING.md).

The original edition’s attribution to Chandrapal and Hack with Github is preserved separately from this edition. The existing CC0 file is inherited; it does not relicense third-party content.

## Contributing

Corrections and well-sourced improvements are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes.
