# Raspberry Pi for Technical Support Operatives in Africa

### by William Majanja

An initiative of the **Hack with Raspberry Pi** community.

An original, digital-first field book for supporting Raspberry Pi computers and Linux systems. It combines practical setup, troubleshooting, command-line recipes, security fundamentals, peace-support data responsibilities, and carefully scoped, authorized security assessment.

This guide is designed for technical support operatives working across Africa’s varied deployment environments. It does not assume that every site has the same power, connectivity, language, hardware supply, or support capacity; use the checklists to document local constraints and plan accordingly.

> **Unofficial:** this book is not produced, endorsed, or maintained by Raspberry Pi Ltd, Debian, Kali Linux, or OffSec. Use security tools only on systems and networks you own or have explicit authorization to assess.

## Start here

- **Personalized editions and standalone generator:** distributed through the CPIP Book Portal. The portal address and edition verification instructions are published with each release. The source remains public and CC0-scoped; there is no DRM.
- [Book map and reading paths](SUMMARY.md)
- [Introduction and scope](1.%20Introduction/Introduction.md)
- [Raspberry Pi field-support guide](Raspberry%20Pi%20Field%20Support/README.md)
- [Linux foundations: kernel, Bash, and command-line recipes](0.%20Linux%20Foundations/README.md)
- [Authorized security assessment playbook](Raspberry%20Pi%20Field%20Support/Security_Assessment_Playbook.md)
- [FieldKit: offline support utilities](Raspberry%20Pi%20Field%20Support/FieldKit.md)
- [Peace Operations field-support context](Peace%20Operations%20Field%20Support/README.md)
- [Informatics, public health, and corporate accountability](Informatics%20and%20Public%20Interest/README.md)
- [Zero-dependency quizzes and CTF-style challenges](Challenges/README.md)
- [Field Informatics and Raspberry Pi Hackathon Handbook](Hackathon/Field_Hackathon_Handbook.md)
- [Participant FieldKit worksheet](Hackathon/Participant_FieldKit_Worksheet.md)
- [Feature Request and Request-for-Change templates](Hackathon/Feature_Requests_and_Change_Requests.md)
- [CPIP- user guide](16.%20CPIP-%20Guide/README.md)
- [William Majanja’s Informatics portfolio](1.%20Introduction/William_Majanja.md)

## What the guide covers

- **Raspberry Pi support:** model-aware setup, OS imaging, first boot, connectivity, troubleshooting, safe remote administration, updates, backups, and handover.
- **Linux foundations:** the kernel and user-space model, Bash scripting, and practical command-line recipes with explanations and checks.
- **System basics:** files, accounts, permissions, services, logs, and networking explained before being used in recipes.
- **System recovery:** storage, safe package changes, backups, restore testing, and owner-approved recovery procedures.
- **African field operations:** offline-friendly procedures, locally adaptable communication and training, reliable recovery, privacy, and site-specific constraints without assuming one context fits all.
- **Peace-support and humanitarian context:** safe technical support for mine-action information systems, child-protection data, WPS participation, and relevant UN Security Council frameworks. This is not EOD, peacekeeper, or child-protection operational training.
- **Public-interest Informatics:** the Muainishi application series, health-data safeguards, corporate-accountability evidence, and careful distinctions between GE crops, specific traits, pesticide exposures, cancer hazards, and exposure-specific risks.
- **Security operations:** authorization, least privilege, verification, recovery, and safe assessment practices integrated into support work. Exercises use owned or explicitly authorized systems only.
- **FieldKit:** original, offline-friendly support utilities with source code and tests; no external Python packages are required.
- **Field hackathon:** four scoped build tracks, team and organizer guides, judging rubric, signed-edition verification, printable participant worksheets, and RFF/RFC-CR proposal templates.
- **Field visuals:** original support, networking, data-lifecycle, and Informatics-review diagrams embedded in the reading flow.
- **Self-study challenges:** Base and Crypto tracks with quiz prompts and flags, solvable from the book and standard shell tools without installing challenge software.
- **CPIP- and Informatics projects:** a version-aware guide to William Majanja’s Coffee Pot Internet Protocol and selected projects from both GitHub accounts.

The book is **zero-install to read and learn from**: core lessons and exercises need no account, site generator, external dataset, or package installation. The standalone generator bundles its runtime for supported platforms. PDF/EPUB production and the CPIP distribution service have separate maintainer requirements.

Each hackathon participant can request a profile-ordered copy with a per-edition CPIP Coffee Cipher. A detached Ed25519 signature on the release manifest binds the exact PDF/EPUB hashes; it is separate from the Coffee Cipher. Verify with the publisher’s independently distributed public-key fingerprint. The cipher is a shareable portal bearer credential—not a signature, identity check, encryption key, or DRM.

## Design and reading experience

The book uses task-based recipes, progressive reading paths, topic categories, plain-language explanations, and source/license notes. This design takes inspiration from the local *Command Line Kung Fu* recipe reference and from [Babe’s Bookstore](https://babesbooks.store/), which describes itself as a category-based digital library with rights information. No text, code, books, or assets are copied from either source; the bookstore’s catalogue and rights claims are not independently audited here.

## Authoring and verification environment

The authoring desktop is **Debian GNU/Linux 13 (Trixie), ARM64, KDE Plasma 6.3.6, Wayland**. This does not mean every Raspberry Pi model, OS image, peripheral, or field deployment has been tested. Hardware-specific steps identify their assumptions and test status.

## Operating systems, security assessment, and CPIP-

Raspberry Pi OS and Debian are the primary support platforms. Never mix distribution package repositories. Security assessment material is limited to authorized, isolated work and emphasizes validation and remediation.

[CPIP-](https://github.com/WilliamMajanja/CPIP-) is William Majanja’s independent Coffee Pot Internet Protocol project, not an official Raspberry Pi, Debian, or Kali component. Its guide labels dependencies and source-stated security claims; it does not treat those claims as independently validated.

## Responsible use, credits, and licensing

Use an isolated lab for hands-on security work. Do not expose experimental services, run unknown code with elevated privileges, or test against systems without written authorization. See [Responsible Use](RESPONSIBLE_USE.md), [Code of Conduct](CODE_OF_CONDUCT.md), [Security Policy](SECURITY.md), and [Licensing and Provenance](LICENSING.md).

The original edition’s attribution to Chandrapal and Hack with Github is preserved separately from this edition. CC0 applies only to original material in the stated licensing scope; it does not relicense third-party content or CPIP.

## Contributing

Corrections and well-sourced improvements are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes.
