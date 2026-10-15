# CPIP- Architecture and Principles

## 1. The protocol joke and the project

RFC 2324 defines the Hyper Text Coffee Pot Control Protocol (HTCPCP); RFC 7168 updates it with tea-brewing semantics.[^rfc2324][^rfc7168] Both are humorous **Informational** RFCs, not Internet Standards Track documents. CPIP- uses that vocabulary as the basis for a separate software project. Despite the playful protocol, its repository describes real network listeners, peer messaging, cryptographic operations, optional transports, a web interface, and active network defenses. Treat it as network software, not as a harmless toy.

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

Use the RFCs as protocol references, not as a security certification. An implementation can use valid method names while still having implementation bugs or unsafe network defaults. Check the relevant RFC section and test behavior against the current code. RFC 9110 is the current standards-track HTTP Semantics specification; it describes the general status-code context for 418, while RFC 2324 supplies the humorous teapot definition.[^rfc9110]

### IETF RFCs versus CPIP project RFCs

CPIP’s `specs/rfc-0001-*.md` records use an internal project numbering scheme. At baseline commit `df93a5258a0d9e5297d30bd6b630f299969ec8bb` they were marked `Draft` and targeted v6.0.0, while package metadata identified v6.0.3. Later documentation updates add RFF/RFC-CR templates, an index, and a corrected RFC-7168 metadata link. These are **CPIP project records**, not IETF RFC publications and not evidence that a feature is present in a release. See the [pinned CPIP specification and request index](https://github.com/WilliamMajanja/CPIP-/blob/d865e88/specs/README.md).

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

The book’s signed edition manifest uses Ed25519 via a maintained cryptography library. RFC 8032 describes EdDSA, including Ed25519, but is an IRTF Informational RFC rather than an Internet Standards Track RFC.[^rfc8032] The portal’s JSON representation is a versioned, project-defined deterministic format; it does **not** claim conformance with the JSON Canonicalization Scheme (JCS) in RFC 8785.[^rfc8785] The publisher fingerprint must be trusted independently of the downloaded manifest.

For standards background, use the primary NIST publications and the project’s own security policy. Do not repeat stronger assurances than those sources justify.

For a public CPIP Book Portal, terminate browser HTTPS at the reviewed reverse proxy and follow the current TLS 1.3 specification; do not confuse that transport protection with CPIP’s Coffee Cipher or the publisher’s detached edition signature.[^rfc9846]

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

## Protocol and security references

[^rfc2324]: L. Masinter, “Hyper Text Coffee Pot Control Protocol (HTCPCP/1.0),” RFC 2324, 1 April 1998. The RFC’s Status of This Memo explicitly says it does not specify an Internet Standard. <https://www.rfc-editor.org/rfc/rfc2324> (accessed 15 October 2026).

[^rfc7168]: I. Nazar, “The Hyper Text Coffee Pot Control Protocol for Tea Efflux Appliances (HTCPCP-TEA),” RFC 7168, 1 April 2014. Informational; updates RFC 2324. <https://www.rfc-editor.org/rfc/rfc7168> (accessed 15 October 2026).

[^rfc9110]: R. Fielding, M. Nottingham, and J. Reschke, eds., “HTTP Semantics,” RFC 9110, STD 97, June 2022. Standards Track; see Section 15.5.19 for status 418. <https://www.rfc-editor.org/rfc/rfc9110> (accessed 15 October 2026).

[^rfc9846]: E. Rescorla, “The Transport Layer Security (TLS) Protocol Version 1.3,” RFC 9846, Standards Track, 2026. It supersedes RFC 8446; use the current RFC Editor record for TLS 1.3. <https://www.rfc-editor.org/rfc/rfc9846> (accessed 15 October 2026).

[^rfc8032]: S. Josefsson and I. Liusvaara, “Edwards-Curve Digital Signature Algorithm (EdDSA),” RFC 8032, IRTF Informational, January 2017. <https://www.rfc-editor.org/rfc/rfc8032> (accessed 15 October 2026).

[^rfc8785]: A. Rundgren, B. Jordan, and S. Erdtman, “JSON Canonicalization Scheme (JCS),” RFC 8785, Informational, June 2020. FieldKit’s manifest format is versioned separately and does not claim JCS compliance. <https://www.rfc-editor.org/rfc/rfc8785> (accessed 15 October 2026).
