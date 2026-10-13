# Services, Logs, and Recovery

This chapter explains how to inspect a Linux service, collect useful evidence, and recover safely. A support operative should distinguish observing a failure from changing service state.

## Process, service, and application

- A **process** is a running program instance with an identifier and resources.
- A **service** is a managed background workload, often configured to start or stop under a service manager.
- An **application** may consist of multiple processes, services, configuration files, data stores, and network dependencies.

On many Debian and Raspberry Pi OS systems, `systemd` is the service manager. Minimal or specialized images can differ; identify the installed OS before using distribution-specific commands.

## Inspect before changing

For a service name you recognize and are authorized to support:

```bash
systemctl status --no-pager --full SERVICE
journalctl -u SERVICE --since today --no-pager
```

Replace `SERVICE` with the exact unit name. These commands inspect status and recent logs. If either command is unavailable, report the platform and the missing tool; do not install a package as an unapproved workaround.

Logs may contain usernames, addresses, document paths, access tokens, or case information. Keep the original record protected and create a sanitized copy before sharing it.

## Service failure recipe

1. **Confirm impact:** ask who is affected, what function failed, and when it began.
2. **Capture a baseline:** record device, OS release, service name, timestamps, recent changes, and sanitized status/log excerpts.
3. **Check dependencies:** verify only approved local state such as storage capacity, required mounts, and the relevant network interface.
4. **Compare with a known-good state:** use the service's own documentation and recorded configuration; do not copy a configuration from another distribution without review.
5. **Make one reversible change:** require the service owner's approval, save the original configuration, and document the rollback.
6. **Verify:** check service state and the specific user-visible function; a running process alone does not prove the service works.
7. **Close or escalate:** record the final state, unresolved causes, and the person responsible for follow-up.

## Restart and rollback boundaries

Restarting, stopping, enabling, or disabling a service changes system state and may interrupt users or erase transient evidence. Before taking such an action:

- confirm the unit and its role;
- obtain approval and a maintenance window if needed;
- preserve relevant logs and status first;
- know how to restore the prior configuration;
- communicate the expected service interruption.

Do not use `kill -9`, broad `pkill`, or root shells as a generic repair method. Escalate when the service owns sensitive data, supports a safety-critical workflow, or the cause is not understood.

## Recovery and handover record

For a durable support record, include the device model, OS and kernel version, service/unit name, start time of the incident, sanitized symptoms, authorized checks performed, changes made, verification result, backup status, and the next responsible contact. Do not include passwords, private keys, Coffee Cipher tokens, health records, or sensitive field coordinates.

## Known limits

This chapter covers first-line service inspection. Service-specific recovery, database repair, kernel debugging, and incident forensics need their own documented procedures, data-owner approval, and platform-specific tests.
