# CPIP-: Local-Only Setup

This walkthrough is designed for an **isolated, disposable test environment**. It is not a production deployment guide. It does not demonstrate covert operation, evasion, scanning of third parties, or radio transmission.

## 1. Check prerequisites and source

CPIP-’s current package metadata requires Python 3.10 or later and declares required dependencies, including `cryptography`, `numpy`, and `pqcrypto`. Its build backend uses setuptools. Optional terminal UI and HSM features add more dependencies. ARM64 availability depends on the exact Python and package versions selected; check whether compatible wheels exist before attempting an install.

Review the repository’s [README](https://github.com/WilliamMajanja/CPIP-/blob/master/README.md), [`pyproject.toml`](https://github.com/WilliamMajanja/CPIP-/blob/master/pyproject.toml), [`SECURITY.md`](https://github.com/WilliamMajanja/CPIP-/blob/master/SECURITY.md), and install/deployment scripts. Choose a specific tag or commit. Do not assume that the `master` branch has been audited or that its version badge matches every included manifest.

The following commands are a **generic Python project workflow**, not a claim that a particular CPIP- commit has been executed on this machine:

```bash
git clone https://github.com/WilliamMajanja/CPIP-.git
cd CPIP-
# Check out a reviewed tag or commit before installing.
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
```

Installing `.` resolves the package metadata and declared dependencies for the checked-out revision. Do not use `sudo pip`, install dependencies globally, or paste unreviewed shell installers into a privileged shell. If a required package is unavailable for the target architecture, stop and resolve compatibility rather than weakening the environment or silently substituting versions.

## 2. Start a local-only service

The project documentation describes the following variables, but defaults can change. Inspect the selected source revision to confirm they are recognized and behave as expected before starting the service.

For an initial local test, keep the listener on loopback and disable external transports and mesh features. An example configuration is:

```bash
CPIP_BIND=127.0.0.1 \
CPIP_SSL=0 \
CPIP_MESH=0 \
CPIP_SAT=0 \
CPIP_RADIO=0 \
CPIP_MOBILE=0 \
CPIP_COVERT=0 \
./server.py
```

The `CPIP_BIND` and feature variables are documented by the project; verify their names and defaults for your pinned version. If the server cannot be confirmed as loopback-only, do not continue with a shared network connection. Run as an ordinary user in a disposable virtual machine or isolated lab, never as root for this walkthrough.

## 3. Verify a basic local request

In a second terminal on the same machine, use the project’s documented dashboard URL and a simple RFC-style request. The examples below use plain HTTP only because this local walkthrough explicitly disables TLS and binds to loopback:

```bash
curl --max-time 5 -i http://127.0.0.1:4180/
curl --max-time 5 -i -X BREW http://127.0.0.1:4180/coffee
```

Open `http://127.0.0.1:4180/dashboard` only if the pinned version serves that route. Do not forward the port from a router or expose it through a public tunnel. Stop the server with `Ctrl-C` and verify that its listener has exited.

If a request fails, inspect the server output, verify that the selected port is free, confirm the configured bind address, and consult the documentation for the same commit. Do not respond to a failure by enabling all network transports or opening firewall ports.

## 4. CLI and dashboard

The repository documents a Bash CLI named `cpip`, a web dashboard, and optional TUI support. Commands and installed paths vary by revision and installation method. Start with read-only status/version commands from the pinned README or `./cpip --help`; check every command against the version actually installed.

Keep controls on localhost. The project’s security policy states that mutating API calls require HMAC authentication by default, but this must be confirmed in the code path and configuration of the chosen revision. Do not place tokens or secret keys in screenshots, shell history, Git, issue reports, or public logs.

## 5. Optional transports and hardware

Do not enable optional transports as part of the first-run test. Each needs a separate review:

- **LAN mesh:** restrict to a lab network you administer; document discovery and broadcast behavior.
- **Radio/LoRa/TNC:** require compatible hardware and legal frequency, duty-cycle, power, and licensing checks for your location. A “simulation” mode must be confirmed not to transmit.
- **Mobile/cellular:** review modem interfaces, carrier terms, identifiers, and location/telemetry exposure.
- **Satellite or relay paths:** verify service ownership, destination, egress policy, and metadata exposure.

This guide does not provide instructions for hiding activity from network operators, bypassing controls, or using covert channels on systems or networks without explicit authorization.

## 6. What has and has not been tested

This repository documents the procedure but does not claim the CPIP- application was installed or exercised by this book’s validation. The authoring desktop is Debian 13 Trixie, ARM64, Wayland, KDE Plasma 6.3.6. That fact does not substitute for testing a particular CPIP- release, and it does not establish compatibility with Kali. Report results only for the exact commit, hardware, Python, dependencies, and configuration tested.
