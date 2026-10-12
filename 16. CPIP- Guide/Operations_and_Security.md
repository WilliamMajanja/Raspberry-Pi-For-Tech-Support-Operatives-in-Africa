# CPIP-: Operations and Security Review

This chapter helps an authorized operator make an informed decision about a CPIP- deployment. It deliberately separates project documentation from verified behavior. It is not an endorsement for production, high-risk communications, or regulated use.

## 1. Configuration inventory

The project documents environment variables for the listener, TLS, mesh, covert messaging, satellite/radio/mobile transports, policy controls, persistence, and cryptography. Use the environment-variable table from the **same pinned commit**; defaults and names have changed across documentation versions.

Before starting, create a written configuration inventory:

| Area | Record |
| --- | --- |
| Identity | Commit/tag, checksum, source of the checkout |
| Runtime | Python version, architecture, resolved dependencies |
| Listener | Bind address, port, TLS mode, exposed routes |
| Authentication | Enabled mechanisms, secret generation and storage, rotation plan |
| Transports | Explicitly enabled transports, interfaces, peers, ports, hardware |
| Persistence | Paths, permissions, retention, backup and deletion procedure |
| Logging | Location, sensitive fields, retention and access controls |
| Recovery | Stop procedure, restore plan, known-good system state |

Start with optional services and transports disabled. Enable only one feature at a time after reviewing its code, documentation, permissions, and network effects.

## 2. Network exposure and authentication

The project documentation describes an HTTP service, dashboard, API, and network transports. Its documented bind default may listen beyond loopback; never assume that a development server is local-only. Confirm the actual listening socket from the process and the host’s network tools before connecting another device.

Operational rules:

1. Keep a learning instance bound to `127.0.0.1`.
2. Do not put the dashboard/API directly on the public internet.
3. Confirm authentication is enforced on **every** mutating route, including dashboard routes and optional services.
4. Use unique, non-default secrets and protect environment files with restrictive permissions.
5. Limit inbound connections at the host firewall to the minimum required for a lab.
6. Do not interpret a successful TLS handshake or security-header list as proof of a secure deployment.

The repository describes auto-generated self-signed certificates and sample `curl -k` commands. `-k` disables certificate verification. It is acceptable only as an explicit loopback diagnostic when you understand that server identity is not being verified; do not copy it into production or general examples. For a real deployment, configure a trusted certificate and verify it normally.

## 3. Keys, messages, and persistence

Before storing real data, inspect the pinned source for key generation, peer identity verification, key derivation, key rotation, encrypted persistence, backups, deletion, swap/core-dump behavior, and failure handling. Do not assume that a setting called “encrypted” or “secure wipe” provides a guarantee without examining implementation and threat model.

Use disposable keys and synthetic messages in a lab. Do not reuse SSH, account, API, or production secrets. Do not put a real person’s health, election, location, or operational data into test messages. Decide how to revoke peers and remove stored data before enabling persistence.

## 4. Crypto language: precise claims

- AES-GCM, ECDSA, ECDH, HKDF, and HMAC are names of algorithms or constructions; their use does not certify an application.
- FIPS publication references describe standards. **CPIP- is not thereby FIPS 140-2/3 validated.** Its own security policy says the application is not a validated module.
- Project-described startup self-tests show that selected code paths passed known-answer/round-trip checks; they do not establish a formal certification or system-level security.
- The project’s modified Kyber/ML-KEM component is labeled non-FIPS and experimental. It should not be used to satisfy FIPS 203 requirements.
- A hybrid construction’s claimed security property depends on exact composition, authentication, implementation, and key management; do not turn a project statement into a guarantee.

For compliance or high-assurance use, obtain an independent evaluation of the exact release and cryptographic module. Do not base a deployment decision solely on this guide or the project’s marketing language.

## 5. Active defense and diagnostics

The project describes probe scoring, request blocking, IP blacklisting, and network-diagnostic endpoints. These mechanisms are heuristic and may have false positives, lock out legitimate operators, or generate traffic outside the host. Test on localhost or an isolated network with explicit authorization. Keep logs and a rollback route. Do not scan, probe, block, or alter systems outside your scope.

Disable a feature using the documented control path only after confirming the selected version, required authorization, and effect. “Temporary” runtime switches may not persist after a restart; compare live state with the environment and service configuration before relying on a setting.

## 6. Deployment modes

The project repository includes or describes standalone, systemd, Docker, Kubernetes, Raspberry Pi, and radio setups. These are distinct deployment modes with different privileges, networking, and persistence. Do not combine snippets from different versioned examples.

Before using a deployment script or manifest:

- inspect every file it installs or changes;
- verify container image names and tags against the pinned release;
- check service user, capabilities, mounts, ports, bind address, and restart behavior;
- confirm secrets are not committed or printed;
- check firewall changes and rollback instructions;
- deploy first in an isolated test system and capture the before/after state.

In particular, do not run an installer as root merely because the README suggests `sudo`. Review the script and prefer an unprivileged, contained test when possible.

## 7. Troubleshooting checklist

- **Server will not start:** verify Python version, installation environment, dependency compatibility for the architecture, and syntax against the pinned revision.
- **Port already in use:** inspect the existing listener; do not change the bind to all interfaces as a workaround.
- **Dashboard unavailable:** verify local bind, configured port, server route, and browser certificate behavior.
- **Authentication failure:** use the same-version security documentation; never disable authentication to make a network-facing test pass.
- **Transport unavailable:** confirm the required hardware, interface, permissions, optional dependency, and regional rules. Keep other transports disabled while diagnosing.
- **Unexpected network traffic:** stop the service, preserve logs/configuration, isolate the test host, and compare the actual environment with the recorded inventory.

## 8. Shutdown and cleanup

Stop the foreground server with `Ctrl-C`; for managed services, use the matching service manager command only after checking the service name. Verify listeners have stopped. Remove temporary test keys, messages, and generated files from the disposable lab; retain sanitized logs only if useful for the test record. Restore any firewall, service, or environment changes documented in your pre-test inventory.

## 9. References

- [CPIP- security policy](https://github.com/WilliamMajanja/CPIP-/blob/master/SECURITY.md)
- [CPIP- configuration and deployment documentation](https://github.com/WilliamMajanja/CPIP-/blob/master/README.md)
- [NIST FIPS publications](https://csrc.nist.gov/publications/fips)
- [Debian security documentation](https://www.debian.org/security/)
- [Kali documentation](https://www.kali.org/docs/)
