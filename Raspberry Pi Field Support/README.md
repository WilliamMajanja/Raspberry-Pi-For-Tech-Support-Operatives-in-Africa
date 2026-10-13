# Raspberry Pi Field Support

This part of the book is the practical core for technical support operatives maintaining Raspberry Pi systems. It offers repeatable first-line checks, recovery planning, and safe handover practices for offices, schools, community networks, labs, NGOs, and other deployments. Actual needs differ by site; assess local power, connectivity, language, accessibility, hardware supply, and organizational policy instead of assuming one African operating environment.

## Field-support path

1. [Identify hardware and choose an operating system](Imaging_and_First_Boot.md).
2. [Use a consistent triage process](Support_Playbooks.md).
3. [Plan backups, updates, handover, and sustained support](Field_Operations.md).
4. Set a supported [security baseline and maintenance cycle](Secure_Baseline_and_Maintenance.md).
5. Use the [printable participant field worksheet](../Hackathon/Participant_FieldKit_Worksheet.md) to record scope, tests, recovery, and handover.
6. Learn the [kernel, Bash, and practical command line](../0.%20Linux%20Foundations/README.md).

## Keep the platform identity clear

- **Raspberry Pi OS** is the official operating system published by Raspberry Pi; its Imager and support documentation are the primary reference for standard Pi deployments.
- **Debian** is a separate general-purpose distribution. Raspberry Pi hardware support depends on the specific board, image, kernel, and firmware.
- **Kali Linux** is a specialized security-testing distribution. It is an optional, authorized lab platform in this book, not the default support image for day-to-day Pi deployments. Check [Kali’s current ARM device support](https://www.kali.org/docs/arm/) before selecting a Kali image.

Use the OS-specific documentation and repositories for the OS installed on the device. Never mix Kali repositories into Debian or Raspberry Pi OS to “get a tool.”

## Test scope

The guide authoring environment is Debian 13 (Trixie), ARM64, KDE Plasma 6.3.6 on Wayland. This confirms the documented authoring environment only. It does **not** mean every Pi model, Raspberry Pi OS image, peripheral, or Kali ARM image has been tested. Recipes identify their assumptions and direct readers to current vendor documentation for hardware-dependent details.

## Primary references

- [Raspberry Pi: Getting started](https://www.raspberrypi.com/documentation/computers/getting-started.html)
- [Raspberry Pi OS downloads and Raspberry Pi Imager](https://www.raspberrypi.com/software/)
- [Raspberry Pi: Configuration](https://www.raspberrypi.com/documentation/computers/configuration.html)
- [Raspberry Pi: Remote access](https://www.raspberrypi.com/documentation/computers/remote-access.html)
- [Raspberry Pi: Operational security](https://www.raspberrypi.com/documentation/security/operational-security.html)
