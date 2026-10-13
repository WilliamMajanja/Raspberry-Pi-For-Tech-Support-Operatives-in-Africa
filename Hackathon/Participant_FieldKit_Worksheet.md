# Participant FieldKit Worksheet

Print one worksheet per team or keep one copy in the team’s offline notebook. Use synthetic information only. Do not record personal case data, real credentials, production secrets, or exact sensitive locations here.

## 1. Team charter and scope

```text
Team / challenge track:
Date / event session:
Team roles and preferred contact:
Fictional user / service owner:
Problem to solve (one sentence):
What is in scope:
What is explicitly out of scope:
Allowed hardware / accounts / network:
Allowed methods and time window:
Stop condition / incident contact:
Approval from challenge owner:
```

Do not test an asset because it appears in a diagram or is reachable. It must be named in the written scope.

## 2. Baseline and assumptions

| Item | Observation/source | Confidence or limitation |
| --- | --- | --- |
| Device/model/fixture ID |  |  |
| OS/build/commit |  |  |
| Data used (synthetic fixture ID) |  |  |
| Network and external services |  |  |
| Intended user/owner |  |  |
| Backup/recovery path |  |  |

Separate observations from assumptions. Do not copy raw logs into a public submission until they have been reviewed for secrets and sensitive details.

## 3. Data and threat review

```text
What is the minimum information needed?
Who may read, change, export, or delete it?
Where is data stored, processed, backed up, or sent?
What happens offline? How are conflicts reviewed?
What could harm a person if exposed or wrong?
How can a participant correct or challenge an output?
Retention/deletion decision and owner:
```

## 4. Test record

| Test ID | Expected result | Observed result | Evidence/fixture | Pass, fail, or blocked |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

If a test changes system state, record prior state, approval, exact change, verification, and rollback result. Never test against real users or services outside the scope.

## 5. Change and recovery plan

```text
Proposed single change:
Reason and owner approval:
Expected result:
Impact if it fails:
Backup or snapshot checked:
Rollback action and who can perform it:
How success is verified:
Stop/escalation trigger:
```

## 6. Handover and known limits

```text
What works and how to reproduce it:
What did not work:
Unverified assumptions / out-of-scope items:
Dependencies and versions:
Data/power/connectivity constraints:
Next action and responsible role:
Next review date:
Sanitization check before sharing:
```

### Optional signed-edition verification record

Use only the publisher’s independently published trust key. The Coffee Cipher is a CPIP portal credential; it is not the signature and must not be placed in this team worksheet.

```text
Edition ID:
Manifest filename / SHA-256:
Publisher signing-key fingerprint checked against:
Signature verification result:
PDF SHA-256 result:
EPUB SHA-256 result:
Verification tool/version and date:
```
