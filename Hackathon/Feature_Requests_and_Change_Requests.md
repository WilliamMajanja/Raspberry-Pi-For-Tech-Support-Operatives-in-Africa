# Feature Requests and Requests for Change

Use these records to turn hackathon feedback into reviewable work. They are a local project process, not an IETF standards process. Keep all examples synthetic and all proposed tests within written scope.

## 1. Choose the right record

### RFF — Request for Feature

Use an **RFF** when requesting a new capability or a new user workflow. Describe the problem and the person who experiences it before proposing a feature. A request is not approval, a delivery promise, or permission to collect additional data.

Example ID: `RFF-2026-001`.

### RFC-CR — Request for Change

Use an **RFC-CR** when changing existing behavior, defaults, data handling, protocol/API compatibility, or operating procedures. State the current behavior and the proposed behavior so reviewers can judge impact and rollback.

Example ID: `RFC-CR-2026-001`.

### CPIP project RFC specifications

CPIP- also has files named `RFC-0001`, `RFC-0002`, and so on under its `specs/` directory. Those are **CPIP project design/specification records**, not IETF-published RFCs. Their identifier must not be used to claim IETF standardization or conformance. The pinned baseline reviewed for this edition labels 26 numbered CPIP proposal files `Draft`, targeting v6.0.0, while package metadata identifies v6.0.3. The CPIP project now has separate [RFF](https://github.com/WilliamMajanja/CPIP-/blob/d865e88/specs/rff-0000-template.md) and [RFC-CR](https://github.com/WilliamMajanja/CPIP-/blob/d865e88/specs/rfc-cr-0000-template.md) templates and a [project-specification index](https://github.com/WilliamMajanja/CPIP-/blob/d865e88/specs/README.md). One implemented example is [CPIP RFC-CR-0001](https://github.com/WilliamMajanja/CPIP-/blob/d865e88/specs/rfc-cr-0001-rfc7168-url.md), which corrects the metadata link for RFC 7168. Treat the remaining draft specifications as proposals until the project records an implemented version and tests.

## 2. Status lifecycle

Use one status at a time:

| Status | Meaning |
| --- | --- |
| Draft | Author is collecting context; not ready for a decision. |
| Needs review | Required fields, owner, evidence, safety, and tests are present. |
| Accepted | Maintainer authorizes work; implementation is not implied. |
| Deferred | Plausible request, but dependency, capacity, policy, or evidence is missing. |
| Rejected | Maintainer gives a reason and any safe alternative. |
| Implemented | A specific change/release is linked; tests and documentation are identified. |
| Verified | A named reviewer checked the acceptance criteria on the listed version and platform. |

An accepted proposal is not necessarily implemented. An implemented change is not deployment approval. Do not mark an untested feature `Verified` because a demo appeared to work once.

## 3. RFF template — Request for Feature

Copy this template to a new `RFF-YYYY-NNN` record. Remove examples and fill every field or explain why it does not apply.

```text
# RFF-YYYY-NNN: Short user-centered title

Status: Draft
Author/maintainer role:
Date opened / last reviewed:
Target project and version/commit:
Related RFF/RFC-CR/CPIP project RFC:

## User problem
Who experiences what problem, in which context, and how often?

## Existing workflow
What do users do now? What evidence shows where it fails?

## Desired outcome
What measurable outcome should improve? Avoid prescribing a solution too early.

## Proposed capability
Describe the smallest useful behavior and a non-digital/manual alternative.

## Acceptance criteria
- [ ] Observable result 1:
- [ ] Observable result 2:
- [ ] Offline/accessibility condition:
- [ ] Verification evidence:

## Data, privacy, and security
Synthetic test data; necessary fields; data flows; actors/access; retention/deletion;
misuse/harm risks; authorization and stop conditions.

## Dependencies and maintenance
Hardware/software/API/owner, support burden, update plan, and failure/recovery behavior.

## Evidence and references
Claim -> numbered footnote/reference; include title, owner, date, version/commit, URL,
access date, and limitations. Distinguish observed evidence from assumptions.

## Decision
Status / decision-maker / date / rationale / follow-up owner:
```

## 4. RFC-CR template — Request for Change

Use this for a proposed change to current behavior. If the change is actually a new capability, create an RFF and link the later change request to it.

```text
# RFC-CR-YYYY-NNN: Short change title

Status: Draft
Author/maintainer role:
Date opened / last reviewed:
Affected project, component, version/commit, and supported platforms:
Related RFF/CPIP project RFC/issue:

## Current behavior
What happens now? Cite the exact source, test, procedure, or user observation.

## Proposed behavior
What will change? What explicitly will not change?

## Reason and impact
Users, availability, compatibility, data, privacy, security, cost, and maintenance effects.

## Migration and rollback
Prerequisites, backup, staged rollout, recovery trigger, rollback steps, and owner.

## Verification plan
Reproducible tests, fixtures, expected results, platform/version, reviewer, and evidence.

## References and footnotes
Use primary/authoritative sources where available. Identify IETF RFCs by official number
and title; label CPIP `specs/RFC-NNNN` as internal project documents, not IETF RFCs.

## Decision and release record
Status / decision-maker / date / rationale / implementation commit / tests / release:
```

## 5. Review rules

- Ask whether a change can be made smaller, reversible, offline-capable, and easier to support.
- Reject or redesign requests that require real beneficiary, patient, child-protection, genomic, or sensitive location data in a demo.
- Require a written owner and scope before a request can authorize active network testing or service changes.
- Add security and data-flow review when an API, cloud provider, telemetry, model, new transport, credential, or new persistence layer is proposed.
- Reference claims precisely. A standards document describes a standard; it does not certify a particular CPIP implementation. A project RFC can document intent; it does not prove implementation.
- Link accepted requests to tests, release notes, and an accountable maintainer. Keep rejected/deferred records so teams do not repeatedly rediscover the same decision.

## 6. Reference and footnote style

In narrative chapters, cite the source near the claim with a numbered footnote. The note should identify author/organization, title, RFC/report number or version, publication date, stable official URL, access date for mutable pages, and any relevant status or limitation. Prefer the RFC Editor or Datatracker canonical page for IETF publications. For project documentation, pin a commit and label it as a project statement.

Example:

> HTCPCP’s humorous coffee-control vocabulary is described in RFC 2324.[^1] The RFC Editor marks it Informational, not an Internet Standards Track specification.[^2]

[^1]: L. Masinter, “Hyper Text Coffee Pot Control Protocol (HTCPCP/1.0),” RFC 2324, 1 April 1998, <https://www.rfc-editor.org/rfc/rfc2324> (accessed 15 October 2026).
[^2]: RFC Editor, RFC 2324 status and memo text, same URL. Status is part of the citation and must not be replaced by “standard.”

Do not invent page numbers, paraphrase a proposal as a requirement, or use a reference list to imply that cited organizations endorse this book.
