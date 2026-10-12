# Introduction

**Raspberry Pi for Technical Support Operatives in Africa** is a field-oriented, source-linked guide by William Majanja. It is an initiative of the **Hack with Raspberry Pi** community.

The guide helps support staff understand, prepare, troubleshoot, maintain, and hand over Raspberry Pi and Linux systems. It combines task-first command-line recipes with underlying Linux concepts, platform notes, security practice, and protection-aware data support. The recipe format was informed by Jason Cannon’s local *Command Line Kung Fu* reference and the category-based reader experience of [Babe’s Bookstore](https://babesbooks.store/). All text and examples in this guide are independently written.

## Who this guide is for

- Technical support operatives supporting Raspberry Pi computers and Linux systems.
- Trainers and learners who need practical command-line, troubleshooting, and recovery skills.
- Organizations using small computers in community, education, health, agriculture, civic, or field deployments.
- Security learners who want to distinguish normal technical support from authorized assessment work.
- Informatics practitioners evaluating health, agricultural, and public-interest data systems.

The title’s regional focus is an invitation to adapt the material to African deployment contexts—not an assumption that every African site has the same infrastructure, language, climate, connectivity, power, or support resources. Document the conditions at each actual site and involve the people who use and maintain the systems.

## What is covered

The field-support chapters cover board-aware imaging and first boot, network and desktop triage, Linux kernel and Bash foundations, practical command-line recipes, change control, backup and restore planning, privacy, and handover. The guide also introduces safe technical support for peace operations and humanitarian data systems involving mine action, child protection, and Women, Peace and Security (WPS). Its public-interest Informatics chapter examines the Muainishi application series, health-data governance, evidence about corporate conduct, and how to assess agricultural and carcinogenicity claims. This is contextual guidance, not clinical, legal, EOD, peacekeeper, or regulatory advice.

The prior edition explicitly left Linux kernel and shell-programming topics out of scope; this edition covers them in full learning chapters. Older Kali-tool directories remain a historical archive and are not a current package catalogue.

## Operating-system choices

Raspberry Pi OS is Raspberry Pi’s official OS and the default point of reference for standard Pi setup. Debian can be suitable for other deployments; hardware enablement and firmware support vary by image and board. Kali is a specialized security-testing distribution and is treated here as an optional, isolated lab environment, not as the default support OS.

These distributions share Linux foundations but have different repositories, package versions, defaults, and maintenance policies. Follow instructions for the OS actually installed. **Do not add Kali repositories to Debian or Raspberry Pi OS.**

## Authoring environment and test scope

The authoring desktop is Debian GNU/Linux 13 (Trixie), ARM64, KDE Plasma 6.3.6 under Wayland. This is the environment used for local command and document checks. It does not imply that every Raspberry Pi model, official Raspberry Pi OS image, peripheral, Kali image, or African field deployment has been tested. Each page distinguishes general Linux advice, OS-specific guidance, source research, and behavior directly checked on the stated platform.

## Zero-dependency reading and challenges

The guide is static Markdown and can be read on GitHub or locally without a site generator. The [Base and Crypto challenge levels](../Challenges/README.md) are designed to work from the book and standard command-line tools; no CTF server, added package, or external dataset is required. These are educational toy challenges, not flags for accessing live systems. Applications described elsewhere may have their own dependencies.

For current Raspberry Pi, Kali, and Debian facts, begin with the linked official documentation. For humanitarian and peace-support material, use the current mission mandate, national standards, and qualified specialists. Summaries here are learning aids, not substitutes for governing documents or role-specific training.
