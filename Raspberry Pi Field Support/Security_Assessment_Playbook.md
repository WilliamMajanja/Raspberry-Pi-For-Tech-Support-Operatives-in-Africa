# Authorized Security Assessment Playbook for Support Teams

Security assessment is part of reliable technical support when it is authorized, proportionate, and tied to a service owner’s decision. The goal is to discover and reduce risk—not to demonstrate access, collect unrelated data, or keep a foothold. This playbook emphasizes safe validation, remediation, and recovery.

## 1. Confirm the mandate before testing

Write down the authorized owner, exact devices/accounts/network ranges, dates and time window, allowed methods, excluded systems, data-handling rules, emergency contact, and stop condition. A general request to “check security” is not a scope definition. If any target or action is unclear, stop and ask the owner.

Use only devices owned by the organization or explicitly included in written permission. Never use public hosts, neighboring Wi-Fi clients, a beneficiary’s device, or an operational system as a practice target.

## 2. Start with a safe baseline

The first pass should be read-only and limited to the local device and approved inventory:

1. Record model, OS release, architecture, kernel, ownership, and service purpose.
2. Review account and group assignments with the system owner.
3. Check supported update status using the distribution’s own tools and advisory sources.
4. Inspect enabled services and listening interfaces; treat logs and addresses as sensitive evidence.
5. Confirm backups, recovery access, and recent authorized changes.
6. Record what was checked and what could not be checked.

An inventory or version match is evidence for triage, not proof that a device is secure or vulnerable.

## 3. Validate safely

Prefer configuration review, version comparison, vendor advisories, and non-invasive checks. If a finding needs active validation, first reproduce it in an isolated lab using a deliberately vulnerable fixture with synthetic data. For an operational device, the owner must approve a specific, non-disruptive validation method and rollback plan.

Do not deploy payloads, attempt privilege escalation, establish persistence, evade monitoring, exfiltrate data, or test destructive behavior as part of routine support. This guide does not provide such procedures. Refer penetration testing or incident response to a qualified team with explicit scope and appropriate safeguards.

## 4. Report findings so they can be acted on

For each finding, record:

- the affected asset and service owner;
- evidence and the exact check performed;
- the source used to assess the issue and its publication date;
- observed impact and realistic conditions required for that impact;
- uncertainty and untested assumptions;
- a prioritized remediation and recovery option;
- the person responsible and the planned retest date.

Do not include passwords, private keys, bearer tokens, child-protection details, health data, or precise sensitive site coordinates in a general support report. Use the organization’s approved restricted channel.

## 5. Close the loop

The support team helps the service owner plan a change window, protect a backup, apply a supported fix, verify the service, and document residual risk. Re-test only the agreed condition. If the system is outside scope, the evidence is uncertain, or the change fails, preserve sanitized evidence and escalate rather than extending the test.

## Worked case: an exposed service

**Scenario:** an inventory says a Pi should accept remote administration only through an organization-managed VPN. A local inspection shows the service listening on a broader interface than expected.

**Safe response:** record the local observation, confirm the intended design with the owner, check the firewall/VPN configuration through approved read-only procedures, and agree on a controlled corrective change. Do not scan the surrounding network or attempt credentials. Verify the listener and legitimate support path after the owner-approved change.

**Learning point:** a support operative can identify and help correct a risky configuration without exploiting the service or expanding scope.

## Status and limitations

This chapter is original operational guidance, not a penetration-testing certification. Platform-specific checks are valid only for their stated system/version and must be checked against current vendor documentation. See [Responsible Use](../RESPONSIBLE_USE.md) before any assessment.
