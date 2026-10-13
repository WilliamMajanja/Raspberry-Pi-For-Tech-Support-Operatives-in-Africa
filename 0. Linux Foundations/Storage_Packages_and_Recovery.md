# Storage, Packages, and Recovery

This chapter connects everyday Linux administration to safe Raspberry Pi support. The examples assume a Debian-family system with `apt`; command availability and behavior can differ on minimal images and other distributions. Read the local manual pages and the installed OS documentation before changing a service device.

![A safe support sequence from observation through verification and handover](../illustrations/field-support-loop.svg)

## 1. Identify disks and mounts before touching storage

Begin with inspection. Device names such as `/dev/sda` can change between boots or when another drive is connected; a name alone is not a reliable identification.

```bash
lsblk -o NAME,MODEL,SIZE,TRAN,FSTYPE,LABEL,UUID,MOUNTPOINTS
findmnt --real
df -hT
```

Check the model, capacity, filesystem, label, UUID, and current mount points against the approved inventory. `df` reports space available to a filesystem; it does not establish media health. Do not assume an SD card is disposable because it contains an OS image: it may also hold logs, configuration, or the only copy of data.

To locate large directories, limit inspection to paths you are authorized to examine:

```bash
du -x -h -d 1 /var 2>/dev/null | sort -h
```

This can be slow and may show access errors. It reads directory metadata and contents; it does not identify which files are safe to delete. Inspect the owner, purpose, and retention rule before removing anything. Never “clean up” by deleting all of `/var/log`, package databases, or files belonging to an active service.

## 2. Understand package state before updating

The package manager is part of the operating system’s trust and recovery chain. Keep the configured repositories matched to the installed distribution and release. Do not combine Kali, Debian, Raspberry Pi OS, Ubuntu, or third-party repositories to obtain one convenient package.

Read-only package queries help explain the installed state:

```bash
cat /etc/os-release
apt-cache policy PACKAGE
dpkg-query -W -f='${binary:Package}\t${Version}\n' PACKAGE
```

Replace `PACKAGE` with one exact package name. `apt-cache policy` shows candidate versions and their configured sources; it does not certify that a source is trustworthy. Review `/etc/apt/sources.list` and `/etc/apt/sources.list.d/` only within the authorized support task, and redact internal mirrors before sharing output.

For a planned maintenance window, record a baseline and backup first. Refresh package indexes, review the available changes, and simulate the transaction:

```bash
sudo apt-get update
apt list --upgradable
apt-get -s upgrade
```

The simulation may still access configured mirrors during `apt-get update`, but it does not install the proposed upgrades. Review removals, held packages, repository changes, disk space, service dependencies, and release notes with the system owner. On a production device, obtain approval before applying an update and schedule a recovery route. Do not use `-y` simply to suppress review. Distribution-specific release upgrades and firmware procedures require their own current official instructions.

After an approved update, capture the package result, check relevant services, verify the user-facing function, and record any rollback or follow-up action. A successful package transaction is not proof that the application is healthy.

## 3. Mounts, filesystems, and safe recovery

Use `findmnt` to understand what is mounted and where. Before editing mount configuration, make a protected copy, confirm the intended UUID using `blkid` or `lsblk`, and arrange local console access. A typo in `/etc/fstab` can delay boot or prevent a filesystem from mounting.

After an authorized edit, validate the syntax before rebooting:

```bash
sudo findmnt --verify --verbose
```

Resolve warnings and confirm the mount options with the service owner. Do not copy an `fstab` line from another Pi: UUIDs, filesystems, removable media, and security requirements differ. Do not run filesystem repair against a mounted filesystem. For suspected corruption, preserve data first, identify the correct unmounted device, and follow the filesystem and distribution recovery guidance. When the data may be evidence or the only copy, stop and escalate rather than experimenting.

## 4. Processes and services

Use process listings and service status to form a hypothesis, not to terminate anything automatically:

```bash
ps -eo pid,ppid,user,stat,etime,comm --sort=-%cpu
systemctl --failed --no-pager
systemctl status --no-pager --full SERVICE
journalctl -u SERVICE --since today --no-pager
```

Logs can contain usernames, addresses, tokens, and personal data. Review and redact them before export. Confirm that the service name and owner are correct. A `restart`, `kill`, `disable`, or package removal changes system state; take it only when approved, reversible, and consistent with the service’s recovery plan. Prefer the service’s documented shutdown and reload methods to force-killing a process.

## 5. Make backups that can be restored

Write a backup plan that names the data, configuration, owner, destination, frequency, retention period, encryption/key custody, and recovery authority. Separate the backup from the device; a second directory on the same SD card is not an independent backup. A whole-disk image may contain deleted data and credentials, so classify and protect it accordingly.

For a small, inactive, authorized configuration directory, `tar` can create an archive without deleting the source:

```bash
tar --create --file support-config.tar --directory /etc SERVICE-CONFIG-DIRECTORY
sha256sum support-config.tar
```

Replace the placeholder with a specific directory approved for collection. This example does not encrypt the archive, preserve every system property, or prove the archive is complete. Store it in an approved protected destination; do not put secrets in a public report or an unencrypted removable drive.

Test restore into a separate, non-production location or spare device. Verify file ownership, permissions, service behavior, and application-level data. Record the tested date and the person who approved recovery. A checksum detects a mismatch against a trusted recorded digest; it does not establish who created the backup or whether the source was safe.

## 6. Recovery decision sequence

1. **Stop writes:** if storage failure or accidental deletion is suspected, avoid updates, cleanup, repeated boots, and re-imaging.
2. **Record context:** capture device model, OS/image version, storage identity, symptom, first occurrence, power event, and recent changes.
3. **Protect the original:** consult the data owner and incident policy; preserve the original media or make an approved read-only copy before repair.
4. **Select the recovery source:** confirm the backup’s date, integrity record, custody, and compatibility with the target system.
5. **Restore in a controlled environment:** use spare media or a test device first when possible. Never overwrite the original evidence or sole copy.
6. **Verify:** compare expected services, configuration, records, and user-visible behavior; document any gap.
7. **Return to service:** obtain the owner’s acceptance, restore approved access, monitor, and schedule a follow-up restore test.

If these steps cannot be followed safely, preserve the current state and escalate. Recovery is an organizational decision, not just a command.

## References

- [Debian Administrator’s Handbook](https://www.debian.org/doc/manuals/debian-handbook/)
- [Debian APT User’s Guide](https://www.debian.org/doc/manuals/apt-guide/)
- [Debian Reference: package management](https://www.debian.org/doc/manuals/debian-reference/ch02.en.html)
- [Raspberry Pi OS documentation](https://www.raspberrypi.com/documentation/computers/os.html)
