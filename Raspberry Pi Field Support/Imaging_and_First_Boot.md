# Imaging and First Boot

## 1. Identify the deployment before writing an image

Record the board model and revision, intended role, architecture, peripherals, network connection, storage type, and recovery plan. Check the official compatibility and power requirements for that exact model. Raspberry Pi models differ in boot media, power connectors, wireless bands, firmware, and peripheral support; do not infer one model’s requirements from another.

For support work, decide in advance:

- Is this a desktop, headless server, kiosk, classroom device, gateway, or appliance?
- Who owns the device and who is authorized to administer it?
- Which data will it hold, how sensitive is that data, and how will it be backed up?
- What network is it allowed to join, and is remote administration required?
- Can the device be recovered locally if the network or remote service is unavailable?

## 2. Choose the operating system

Use the operating system supported for the intended workload and hardware. For a standard Raspberry Pi deployment, begin with Raspberry Pi’s [official OS options](https://www.raspberrypi.com/software/). A Debian image may be appropriate for some support workloads, but hardware enablement can differ from Raspberry Pi OS. Kali ARM images are for authorized security testing and should be kept separate from routine support deployments.

Check the target image’s release date, update policy, architecture, hardware support, and security maintenance before deployment. Store the image source, version, checksum or signature information where available, and date in the device’s support record.

## 3. Prepare boot media carefully

Raspberry Pi Imager can write supported operating-system images to microSD and other supported storage. **Imaging erases the selected destination.** Before writing:

1. Make sure the selected storage device is the intended card or drive.
2. Disconnect unrelated removable storage where practical.
3. Keep Imager’s protection against selecting the computer’s system disk enabled.
4. Use the official image source and complete the verification step offered by the tool.
5. Never use a production or evidence disk as test media.

Imager can also configure a hostname, user account, locale, wireless network, and remote access before first boot. Choose unique credentials; do not use a shared password across a fleet, and never include credentials in notes, screenshots, scripts, or this guide.

## 4. First boot checklist

For a desktop system, connect only the required display, keyboard, pointing device, network, and correct model-specific power supply. For a headless system, preconfigure network and an approved remote-access method before writing the card, then confirm the device identity through a trusted channel before logging in.

At first boot:

- Set the correct hostname, locale, timezone, keyboard layout, and administrative user.
- Confirm the intended network and verify that the device receives the expected address.
- Enable SSH or another remote-support feature only when needed; keep its access limited and authenticated.
- Apply OS updates according to the installed distribution’s official guidance and an agreed maintenance window.
- Record OS version, kernel release, architecture, device model, storage, and enabled services.
- Confirm a clean shutdown and a recoverable backup before handing the device over.

On Raspberry Pi OS, use its supported configuration interfaces. Tools such as `raspi-config` are not guaranteed to exist or behave the same way on generic Debian or Kali images.

## 5. Headless network setup

Ethernet is a useful first diagnostic where available. If Wi-Fi is required, confirm the network name, credentials, security mode, signal at the device location, and the board’s supported band. Some older Pi boards support 2.4 GHz only; check the model specification rather than guessing.

Use approved network settings. Do not connect a support device to an untrusted access point merely to “see if it works,” and do not scan other clients on the network as a connectivity test. If preconfigured Wi-Fi fails, use a local console or wired connection and follow the official Raspberry Pi OS documentation for the installed release. The old `wpa_supplicant.conf` boot-folder method is not applicable to current Raspberry Pi OS releases.

## 6. Power, shutdown, and hardware safety

Use a supply and cable suitable for the exact Pi model and its attached peripherals. Undersupply, damaged cables, poor connectors, and high peripheral load can cause instability or storage corruption. Check the official [power supply guidance](https://www.raspberrypi.com/documentation/computers/getting-started.html#power) before diagnosing a board as faulty.

Use the operating system’s shutdown function or `sudo poweroff` before disconnecting power. A hard power cut can corrupt filesystems or lose data. Disconnect power before attaching or removing HATs, GPIO wiring, storage, or other hardware. GPIO pins are low-voltage logic; never connect them directly to mains or unknown voltages. Follow the board and accessory manufacturer’s electrical safety guidance.

## 7. References

- [Official Raspberry Pi getting-started guide](https://www.raspberrypi.com/documentation/computers/getting-started.html)
- [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
- [Raspberry Pi boot diagnostics](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#boot-diagnostics)
- [Raspberry Pi GPIO documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#gpio)
