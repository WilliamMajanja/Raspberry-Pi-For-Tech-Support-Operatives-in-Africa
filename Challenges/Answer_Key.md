# Challenge Answer Key

**Spoilers:** attempt the levels in [Challenges](README.md) before opening this page.

<details>
<summary>Base Levels — Field Support</summary>

### BASE-0

**Flag:** `FLAG{KEEP_DISTROS_SEPARATE}`

The machine identifies as Debian 13. Keep Debian repositories configured; use supported Debian packages or a separate Kali VM/device for Kali-only packages. Do not add Kali sources to Debian.

### BASE-1

**Flag:** `FLAG{PRESERVE_BEFORE_REIMAGE}`

Record the symptom and hardware/OS details, check the model-specific power and boot indicators, and preserve the original storage before any re-image attempt. Re-imaging overwrites the target media.

### BASE-2

**Flag:** `FLAG{DIAGNOSE_IN_LAYERS}`

The interface is up, has an address, and has a default route. Investigate name resolution using the approved resolver configuration and authorized diagnostics. Do not infer that the whole network is down or scan unrelated devices.

### BASE-3

**Flag:** `FLAG{DO_NO_HARM_WITH_DATA}`

Remove or restrict the public exposure through the authorized support process, preserve only what is necessary, and route the case through the organization’s designated child-protection channel. Do not repost the identifying information in a ticket.

</details>

<details>
<summary>Quiz Levels</summary>

- **QUIZ-0:** B. A support operative does not inspect or identify an explosive hazard; follow local safety procedures and report it to qualified personnel.
- **QUIZ-1:** A. S/RES/2365 (2017) is the thematic mine-action resolution.
- **QUIZ-2:** C. Minimize case data and use the designated restricted child-protection pathway.
- **QUIZ-3:** B. Meaningful participation and safety/accessibility barriers matter; avoid unnecessary sensitive data collection.
- **QUIZ-4:** B. Genetic engineering is a method, not one uniform exposure; assess a specific product and evidence case by case, and separate hazard from risk at a particular exposure.
- **QUIZ-5:** B. Profit can create incentives, but proving a specific harm or intent requires case-specific evidence. Purdue is a documented example with its own legal record, not a basis for claims about every pharmaceutical company.

</details>

<details>
<summary>Crypto Flag Levels</summary>

### CRYPTO-0

**Flag:** `FLAG{THE_ENCODED_MESSAGE_IS_NOT_SECRET}`

ROT13 shifts each letter by 13 places. It is an encoding/substitution exercise and provides no confidentiality.

### CRYPTO-1

**Flag:** `FLAG{CAESAR_IS_NOT_ENCRYPTION}`

Shift each letter backward by three positions. Caesar substitution is a toy cipher and must not be used to protect data.

### CRYPTO-2

**Flag:** `FLAG{HASH_IS_NOT_CIPHERTEXT}`

A cryptographic hash is not decrypted. Use the approved credential reset and verification process; do not disclose the digest or attempt recovery of a real credential outside an authorized process.

</details>
