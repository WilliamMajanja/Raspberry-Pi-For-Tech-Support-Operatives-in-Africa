# Support and Troubleshooting Playbooks

Use the same sequence for every incident: **confirm authorization and impact → observe → record → form a hypothesis → make one reversible change → verify → document or escalate**. These playbooks are first-line support checks, not substitutes for board-specific diagnostics or specialist repair.

## 1. Capture a safe baseline

Run locally or over an approved SSH session:

```bash
date --iso-8601=seconds
hostnamectl
uname -a
cat /etc/os-release
df -hT
free -h
uptime
ip -brief address
ip route
systemctl --failed --no-pager
```

These are primarily inspection commands. Some may be absent on minimal images; record that rather than installing packages during initial triage. Do not publish raw output without reviewing it for usernames, hostnames, addresses, serial numbers, and sensitive operational details.

## 2. Device does not boot

1. Confirm the model and power supply against the manufacturer’s requirements; check the cable and connector.
2. Disconnect nonessential peripherals, then retry with known-good, compatible power and display equipment.
3. Allow the first boot time to complete. If it still does not start, read the board’s status LEDs using the **model-specific** warning-code table.
4. Check that the correct OS image was written to the intended storage and that the image verification step passed.
5. If re-imaging is necessary, first confirm that all needed data has a separate backup. Re-imaging is destructive.
6. If the board still fails, preserve the old media and logs where possible, and escalate to hardware or OS support.

Do not repeatedly remove power from a device that may still be writing to storage. Raspberry Pi’s current [troubleshooting guidance](https://www.raspberrypi.com/documentation/computers/getting-started.html#troubleshooting) and [boot diagnostic information](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#boot-diagnostics) are authoritative for model-specific indicators.

## 3. Device boots but has no network

Start locally and inspect links and routes:

```bash
ip -brief link
ip -brief address
ip route
```

Then check the physical connection, Wi-Fi band support, signal, approved SSID, credentials, DHCP availability, and whether the network requires a captive portal or device registration. If NetworkManager is installed, `nmcli device status` can help inspect device state; its absence does not prove a fault.

Test in layers, using only the organization’s approved gateway and resolver. A successful local address does not prove DNS, and successful DNS does not prove an external service is healthy. Do not change firewall rules, disable authentication, or scan neighboring devices to troubleshoot one Pi.

## 4. Remote access is unavailable

- Verify the expected hostname/address through the authorized device inventory or local console.
- Confirm that SSH or the approved remote-support service is installed, enabled, and bound only as intended.
- Check host-key identity before entering credentials. A changed SSH host key is a warning to investigate, not a prompt to bypass verification.
- Inspect service status and recent logs with `systemctl status --no-pager SERVICE` and `journalctl -u SERVICE --since today --no-pager`.
- Confirm that network policy, VPN, firewall, and NAT rules permit the approved path.
- Revoke credentials or device access through the designated administrator if a device is lost or compromised.

Never expose SSH or a desktop-sharing server directly to the public internet as a quick fix. Prefer the organization’s approved VPN or managed remote-support system, with MFA where available.

## 5. Desktop or display problem

Check monitor input, cable, power, resolution support, and whether the problem exists before the desktop starts. Record display model and connection type. In KDE/Wayland sessions, screen sharing and capture use desktop portal permissions; an X11-specific recipe or automation script may not behave the same under Wayland.

Inspect the current session without changing it:

```bash
printf 'Session: %s\n' "${XDG_SESSION_TYPE:-unknown}"
printf 'Desktop: %s\n' "${XDG_CURRENT_DESKTOP:-unknown}"
```

These environment variables are informative but not a complete display diagnostic. Keep SSH or a local TTY recovery route available before changing display-manager, compositor, or graphics-driver settings.

## 6. Slow, hot, or unstable device

Start with read-only resource checks:

```bash
uptime
free -h
df -hT
ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head
journalctl -k -p warning --since today --no-pager
```

Use these as clues, not diagnoses. Check ventilation, ambient conditions, power supply, attached USB devices, storage health, and recent package or configuration changes. Follow model-specific official guidance for thermal indicators and do not remove heatsinks or alter clock/voltage settings without understanding warranty and reliability implications.

## 7. Service failure

For a known service name:

```bash
systemctl status --no-pager --full SERVICE
journalctl -u SERVICE --since today --no-pager
```

Capture the exit code, error message, relevant recent change, and exact service name. Do not use `systemctl enable`, `disable`, `restart`, or root privileges until the service’s role and change authorization are clear. Kali intentionally has a different network-service default policy from a typical desktop distribution; consult [Kali’s policy](https://www.kali.org/docs/policy/kali-linux-network-service-policy/) before changing one.

## 8. Storage or update problem

First inspect free space with `df -hT` and identify large directories within data you are authorized to inspect. Do not delete logs, package databases, or user files simply to free space. Preserve logs and note package-manager errors before attempting recovery.

Use the update process for the installed OS. Raspberry Pi OS, Debian, and Kali can share APT concepts, but package sources, firmware, service policies, and release models differ. For Kali rolling, schedule updates outside a live assessment and read [Kali’s current update guidance](https://www.kali.org/docs/general-use/updating-kali/). Never add Kali sources to Debian or Raspberry Pi OS.

## 9. Escalation notes

When escalating, include the device model, OS/image version, kernel and architecture, symptom and first occurrence, recent changes, relevant sanitized output, reproduction steps, expected vs observed behavior, steps attempted, backup state, and impact. Do not attach private keys, passwords, raw child-protection records, casualty data, or unredacted mine-hazard coordinates to a public ticket.
