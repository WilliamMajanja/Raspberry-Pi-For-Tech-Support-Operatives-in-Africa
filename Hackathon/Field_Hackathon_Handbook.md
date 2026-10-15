# Field Informatics and Raspberry Pi Hackathon Handbook

This hackathon uses a Raspberry Pi or Linux support problem to practice infrastructure, safe support, data stewardship, and responsible Informatics. Teams build and demonstrate a small, testable improvement—not a speculative product for vulnerable people. Each exercise uses synthetic data and a written scope. No participant receives permission to test a live third-party system.

## 1. Outcomes

By the end of the event, each team should be able to:

1. frame a field-support problem with a named user, owner, context, and stop condition;
2. collect a minimal, reproducible technical baseline and distinguish evidence from assumptions;
3. design for offline operation, data protection, accessibility, and recovery;
4. test a small technical change using synthetic fixtures and show a rollback path;
5. explain the limitations of its evidence, dependencies, and proposed deployment;
6. hand over a build and field record that another team can reproduce.

![Field data lifecycle and control checks used during the hackathon](../illustrations/offline-data-workflow.svg)

## 2. Participant path: the Coffee Cipher and signed edition

The public starter puzzle leads to the CPIP Book Portal. Participants may request a reader profile and an edition tailored by reading sequence, exercise, and generated cover. The portal uses CPIP-’s CoffeeCipher operation to create a **Coffee Cipher** bearer credential and associates it with that edition. A copy may display its cipher so the recipient can use the portal again; sharing the copy also shares that credential. It is not DRM, a person’s identity, or the digital signature.

The word **signed** means that the publisher creates a detached **Ed25519 signature over a release manifest**. The manifest binds the exact PDF and EPUB file digests to the edition ID, profile, source/build revision, issue time, and signing-key ID. The signature is made with a separate publisher signing key; it is not derived from the CPIP covert key or the Coffee Cipher. Readers verify the manifest signature using the trusted public key and then compare the file hashes. The public key’s fingerprint must be obtained through an independent trusted channel (for example, the project repository release page or event handout), not merely from the same download response.

A valid signature shows that the signed manifest has not been changed since the holder of the corresponding private key signed it. It does **not** prove that the book’s factual content is correct, that CPIP is secure, that a named person attended the hackathon, or that an edition cannot be copied. A Coffee Cipher authorizes a portal action; it does not sign or encrypt a book. The portal must label these two mechanisms separately.

### Issuance sequence

1. The participant solves the public starter challenge and receives a temporary bootstrap Coffee Cipher.
2. The participant selects a reading profile and requests an edition over HTTPS.
3. The portal validates the bearer credential through its loopback-only CPIP adapter, assigns an edition ID, and asks CPIP to encode the edition’s next cipher.
4. The build service creates the personalized PDF, EPUB, and cover, checks the expected formats, hashes each artifact, and produces a canonical JSON manifest.
5. The publishing service signs the manifest with its separate protected Ed25519 private key. It records issuance and digests in its local audit ledger.
6. The participant downloads the PDF, EPUB, full-scale printables ZIP, manifest, detached signature, and signer public-key information from the portal. The participant checks the pinned key fingerprint, verifies the signature, and checks every artifact hash.
7. The printed Coffee Cipher is used for the next portal session. Participants decide whether to retain it privately or share it with the edition.

Keep the signing key separate from CPIP keys, token peppers, TLS keys, and application configuration. Do not put a production private key in the PDF, source tree, app bundle, or hackathon participant machine. Use a test-only key for rehearsal. Publish the production public key and its fingerprint before issuing real event editions; define rotation and compromise procedures.

## 3. Challenge tracks

Choose one challenge per team. Organizers can provide a Raspberry Pi, a virtual machine, or a printed fixture. A hardware task must have a no-hardware alternative so an equipment shortage does not exclude participants.

### Track A — Offline support and recovery

**Brief:** A community learning centre’s synthetic support Pi loses power during a write. The only mock project data is on its card, connectivity is intermittent, and the service owner needs a safe recovery plan.

**Build:** a read-only baseline collection, a recovery checklist, and a restore verification plan. Teams may extend FieldKit using sample fixtures; they must not overwrite the supplied source image.

**Demo:** identify OS and media, mark assumptions, describe preservation-first actions, and show a restore test on a copy or mock directory.

### Track B — Safe field-information workflow

**Brief:** A local outreach team needs to reconcile duplicate synthetic referral records collected offline. No real person or case record may be used.

**Build:** a minimum-field schema, provenance markers, explicit conflict queue, role-specific views, and documented retention/deletion decision. A printed workflow is acceptable if it is testable.

**Demo:** retry the same mock sync twice, introduce a conflicting edit, and show that the system flags the conflict rather than silently overwriting it. Explain who is authorized to resolve it.

### Track C — Authorized device assessment

**Brief:** An isolated training Pi has a written scope, a known inventory, and a seeded configuration issue. The challenge owner supplies the VM/Pi and exact allowed tests.

**Build:** an assessment plan, safe baseline check, evidence record, owner-approved remediation, and retest. No internet target, persistence, credential capture, destructive validation, or unscoped scanning is allowed.

**Demo:** show the approved scope and stop conditions before the test, reproduce only the seeded issue, make one reversible fix, and document limitations.

### Track D — Informatics prototype review

**Brief:** A fictional browser application claims local-only analysis while showing an “AI result.” Teams receive synthetic input and an intentionally incomplete data-flow description.

**Build:** a data-flow map, source/provenance review, privacy and validity risks, and a synthetic-data test plan. Teams need not implement an AI model.

**Demo:** identify the unverified claim, show which network/retention questions require evidence, and present a human-review and correction route before suggesting use.

## 4. Event preparation

### Organizers

- Appoint a technical lead, a safeguarding/data-protection contact, an accessibility contact, a safety/incident lead, and judges with relevant domain experience.
- Publish the challenge scope, supplied assets, allowed tools, data rules, submission format, judging rubric, and incident contact before registration closes.
- Prepare tested images or virtual machines, spare media, offline references, adapters, power/cooling, accessible workstations, and printed equivalents. Label every intentionally vulnerable fixture.
- Make each team’s work isolated from organizational and public networks unless a narrowly approved service connection is needed.
- Review scenario wording for local relevance with local partners; do not treat “Africa” as one deployment environment or invent community requirements without consultation.
- Keep participant accounts and challenge credentials synthetic and disposable. Remove them after the event under the published retention plan.

### Participants

Bring no real beneficiary, patient, genomic, child-protection, mine-action, or corporate-confidential data. Use only issued lab hardware and fixtures. Ask the scope owner before changing a service, contacting an external endpoint, or connecting to a network. Stop and report unexpected data or unsafe behavior.

## 5. Example one-day schedule

| Time | Activity | Evidence/output |
| --- | --- | --- |
| 08:30–09:00 | Welcome, access, accessibility and safety briefing | Attendance stored only as the event requires; rules accepted |
| 09:00–09:30 | CPIP starter challenge and edition setup | Optional signed edition; participants can instead use printed public materials |
| 09:30–10:00 | Problem framing and team charter | Owner, user, scope, data boundaries, stop conditions |
| 10:00–12:00 | Build sprint 1 | Baseline, prototype, test plan, issue log |
| 12:00–12:45 | Rest and meal | No compulsory work or public presentation of protected material |
| 12:45–14:30 | Build sprint 2 and mentor review | Tested change, synthetic fixtures, recovery path |
| 14:30–15:15 | Verification and handover | Reproducible steps, known limits, sanitized evidence |
| 15:15–16:15 | Short demos | Five-minute demonstration plus questions from judges |
| 16:15–16:45 | Scoring and participant debrief | Transparent rubric, corrections and follow-up owners |
| 16:45–17:00 | Close and device/account return | Data/device disposition confirmed |

Adapt duration, breaks, language, and schedule with participants. Provide an async/offline route for people whose access or connectivity differs.

## 6. Judging rubric

Score each category from 0 (not demonstrated) to 4 (clear, tested, and reproducible); multiply by its weight. A safety breach is an automatic stop and referral to the event lead, not a low score to be offset by polish.

| Category | Weight | A strong submission demonstrates |
| --- | ---: | --- |
| Problem fit and user/owner validation | 15% | Specific need, local constraints, and a confirmed accountable owner |
| Technical correctness and reproducibility | 20% | Small working solution, clear prerequisites, test results, and source/build revision |
| Privacy, safeguarding, and data minimization | 20% | Synthetic data, roles, provenance, safe retention, and no unnecessary identifiers |
| Security, authorization, and recovery | 20% | Written scope, low-impact test, rollback, stop conditions, and sanitized findings |
| Offline resilience and accessibility | 15% | Useful operation during connectivity interruption and usable alternatives |
| Handover and honest limitations | 10% | Maintainer instructions, known gaps, citations, ownership, and next review date |

Do not score teams on collecting more personal data, exploiting systems, using cloud AI, or claiming unsupported impact. Judges should state uncertainty and recuse themselves from conflicts of interest.

## 7. Submission and handover

Every team submits:

- problem statement, owner, written scope, and exclusions;
- diagram of devices, software, data, networks, and external services;
- source code or paper workflow, dependencies, license, and build/run steps;
- synthetic test fixtures, expected outcomes, actual results, and a rollback/restore path;
- data handling, accessibility, security, and unresolved risk notes;
- a short operator handover with responsible contact and next review date.

Do not include passwords, API tokens, production private keys, exact sensitive coordinates, personal records, or unrevised logs in the submission. Do not upload participant artifacts to a public repository without contributor consent and license review.

## 8. After the event

Assign an owner to each follow-up. Separate “demo passed” from “ready for deployment”; the latter needs operational ownership, policy review, maintenance capacity, secure hosting, and realistic field testing. Destroy disposable test accounts, handle data and hardware according to the retention plan, and publish an accessible summary with corrections. Ask participants what excluded them or made participation unsafe and make changes before the next event.

When a useful improvement needs more than a hackathon demo, submit an [RFF for a new feature or RFC-CR for a change to existing behavior](Feature_Requests_and_Change_Requests.md). A completed form enters review; it does not authorize a production rollout.

## References and related chapters

- [Participant FieldKit worksheet](Participant_FieldKit_Worksheet.md)
- [RFF and RFC-CR proposal templates](Feature_Requests_and_Change_Requests.md)
- [Authorized security assessment](../Raspberry%20Pi%20Field%20Support/Security_Assessment_Playbook.md)
- [Field data stewardship](../Peace%20Operations%20Field%20Support/Data_Stewardship_and_Offline_Systems.md)
- [Muainishi prototype review](../Informatics%20and%20Public%20Interest/Muainishi_Project_Review.md)
- [CPIP- user guide](../16.%20CPIP-%20Guide/README.md)
- [International Mine Action Standards](https://www.mineactionstandards.org/standards/)
