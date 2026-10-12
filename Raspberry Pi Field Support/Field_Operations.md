# Field Operations, Maintenance, and Handover

## 1. Build a supportable deployment

Before a Pi enters service, record who owns it, what it does, who may administer it, what data it handles, how it connects, and how it can be recovered. Use a unique hostname and device identity; keep the inventory private when it contains site or operational information.

Design for the conditions at the actual deployment site. Where power interruptions, costly connectivity, long travel to a repair location, multiple working languages, or limited spare parts are relevant, plan around those constraints. Do not assume those conditions apply everywhere in Africa or to every organization.

Practical resilience measures include:

- a compatible power supply and known-good cable for the board and peripherals;
- a labeled, verified recovery image and spare boot media where appropriate;
- a tested backup and restore procedure for configuration and user data;
- a documented offline troubleshooting path and local copy of essential manuals;
- clear ownership for updates, credentials, incident reporting, and replacement;
- an escalation contact and handover record in the users’ preferred language where feasible.

## 2. Updates and change control

Do not update a production or mission device opportunistically. Record the current state, read release notes, back up necessary data, agree a maintenance window, and know how to recover. Change one class of component at a time and verify the service after reboot.

Use only the operating system’s supported repositories. Raspberry Pi OS firmware and tooling, Debian stable packages, and Kali rolling packages do not have identical lifecycles. Follow the applicable upstream instructions rather than reusing a command simply because the distributions share APT.

For an authorized Kali lab, the current official guidance describes `apt update` followed by `apt full-upgrade`; review proposed package changes and schedule outside an engagement. For Raspberry Pi OS and Debian, check each distribution’s release-specific instructions before applying updates. Do not use `-y` on an unfamiliar or operational system merely to make an example shorter.

## 3. Backups and recovery

A backup is useful only if it can be restored. Define:

- which user data, service configuration, and application state must be retained;
- where copies are stored and who may access them;
- how encryption keys and recovery credentials are protected;
- how often backups run and how long they are retained;
- how a restore is tested without overwriting the live deployment.

Keep at least one backup separate from the device and verify it periodically. Record the exact image and package state needed to rebuild. A whole-disk image contains deleted space and sensitive data; store it as confidential material. Re-imaging an SD card or SSD overwrites its contents, so confirm the target and backup before writing.

## 4. Data protection and localization

Collect only the support data needed to resolve an incident. Minimize personally identifying information, avoid publishing network maps or exact sensitive site coordinates, and follow applicable organizational policy and local law. Protect service logs and backups; access should be role-based and time-limited.

Make support materials usable by the people who will rely on them: use clear language, explain acronyms, provide a compact checklist for low-connectivity situations, and account for accessibility needs. Translation should be reviewed by a fluent local speaker rather than assumed from machine output.

## 5. Handover template

```text
Device / hostname:
Model and storage:
Operating system / image date:
Kernel / architecture:
Purpose and owner:
Network and approved remote-access method:
Backup and recovery location:
Known issues / peripherals:
Last maintenance date:
Responsible support contact:
Next review date:
```

Do not put passwords, private keys, access tokens, or sensitive beneficiary information in this handover. Store such material in the organization’s approved credential or case-management system.

## 6. Hardware handling

Shut down before moving storage or connecting a HAT. Disconnect power before changing GPIO wiring. Use GPIO only with compatible low-voltage hardware and reviewed pinout documentation; Raspberry Pi GPIO is not a mains interface. Have qualified electrical personnel design or inspect mains-powered equipment and enclosures.

When a unit returns from the field, record condition, preserve evidence if an incident is suspected, check storage and power before reimaging, and wipe or retire data according to the organization’s policy.

## 7. Authoritative references

- [Raspberry Pi security guidance](https://www.raspberrypi.com/documentation/security/operational-security.html)
- [Raspberry Pi remote access](https://www.raspberrypi.com/documentation/computers/remote-access.html)
- [Raspberry Pi OS updates](https://www.raspberrypi.com/documentation/computers/os.html#manage-software-and-firmware-updates)
- [Kali update policy](https://www.kali.org/docs/general-use/updating-kali/)
- [Debian documentation](https://www.debian.org/doc/)
