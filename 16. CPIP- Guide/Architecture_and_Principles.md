# CPIP- Architecture and Principles

## 1. The protocol joke and the project

RFC 2324 defines the Hyper Text Coffee Pot Control Protocol (HTCPCP); RFC 7168 extends it to tea. CPIP- uses that coffee-and-tea vocabulary as the basis for a software project. Despite the humorous protocol, the repository describes real network listeners, peer messaging, cryptographic operations, optional transports, a web interface, and active network defenses. Treat it as network software, not as a harmless toy merely because its protocol is playful.

The project is independent of the Kali distribution. The word “CPIP” is also used by unrelated projects; here the trailing hyphen identifies William Majanja’s Coffee Pot Internet Protocol repository.

## 2. Architecture as described by the project

The repository describes these main layers:

| Layer | Project-described role | Questions to verify for a chosen revision |
| --- | --- | --- |
| HTCPCP service | Coffee/tea request handling and status | Which methods, paths, and status codes are actually implemented? |
| HTTP/API and dashboard | Local status, configuration, controls | Which endpoints require authentication? Which actions change state? |
| Node and mesh logic | Peer discovery, routing, message queues | How are peers authenticated? What metadata is exposed? |
| Transports | LAN UDP and optional satellite, radio, or mobile links | Which components are compiled/enabled, and what hardware or service is required? |
| Cryptography | Message protection, identity, and key derivation | Which code path is used? What key is trusted, where is it stored, and what has been independently reviewed? |
| Defensive features | Probe heuristics, rate limits, and policy toggles | What are the false-positive modes, and what is actually blocked? |

The table summarizes the project documentation; it is not an architecture audit. Verify all ports, defaults, authentication behavior, data storage, and feature availability against the exact source revision you intend to run.

## 3. Reading the design goals critically

### RFC fidelity

Use the RFCs as protocol references, not as a security certification. An implementation can use valid method names while still having implementation bugs or unsafe network defaults. Check the relevant RFC section and test behavior against the current code.

### Multi-transport resilience

Multiple paths can improve availability, but every enabled transport adds configuration and attack surface. Radio, cellular, satellite, and relay behavior may expose location, network identifiers, peer relationships, timing, or other metadata. Enable only transports you own or are authorized to use, and document hardware, service, and regional regulatory requirements.

### Cover traffic and privacy

The project describes encoding data in protocol additions and generating cover traffic. Cover traffic is not a guarantee of anonymity or resistance to traffic analysis. Endpoints, timing, packet sizes, identifiers, radio emissions, DNS requests, and the surrounding network may remain observable. This guide explains the design at a conceptual level and confines any demonstration to an isolated lab.

### Active network defense

The project describes heuristic probe detection, HTTP 418 responses, and IP blacklisting. Heuristics can block legitimate clients, including scanners used by an authorized administrator. Treat these as experimental controls: assess logs, test false positives on localhost or a private lab, and do not deploy them as a substitute for a firewall, authentication, monitoring, or an incident-response plan.

### Cryptographic claims

- “Uses an algorithm named in a FIPS publication” does not mean the software or cryptographic module is FIPS validated.
- A startup self-test is useful diagnostics but is not a certification.
- The project labels its modified Kyber/ML-KEM implementation as non-FIPS and experimental. Do not rely on it for regulated or production security requirements.
- A cryptographic primitive does not compensate for weak key management, unauthenticated peer identity, incorrect protocol composition, insecure defaults, or implementation defects.
- Independent review of a particular source revision is required before making assurance claims.

For standards background, use the primary NIST publications and the project’s own security policy. Do not repeat stronger assurances than those sources justify.

## 4. Threat model and data questions

Before a lab or deployment, write down:

1. Which systems and networks are in scope, and who authorized the test?
2. What information can be observed by each transport, relay, peer, web browser, and operating system?
3. Where are keys, message history, logs, and configuration stored? How are they backed up and deleted?
4. Which component listens on each interface and port? Does it have an authentication boundary?
5. What happens if a peer is malicious, a key is copied, a transport fails, or a defense feature blocks a legitimate administrator?
6. How can the operator stop the service and restore the previous system state?

The project’s own threat model is useful input, not a substitute for one specific to your deployment.

## 5. Source/version discipline

The project’s public documentation has version mismatches: its README and `pyproject.toml` describe a newer version than some release notes and deployment examples. Do not mix commands, container tags, or configuration tables from different versions.

For a reproducible review, record:

- repository URL and commit hash or signed release tag;
- date reviewed and Python version/architecture;
- dependency lock or resolved package versions;
- enabled transports and environment variables;
- tests run and their results;
- deviations from upstream instructions.

Prefer source links pinned to a commit in a published walkthrough. A link to `master` is convenient but changes over time.
