# Zero-Dependency Quizzes and CTF-Style Challenges

This self-study track borrows the **progressive level, prompt, hint, flag, and answer-key** pattern of capture-the-flag learning, including William Majanja’s [HydraCTF](https://github.com/WilliamMajanja-zz/HydraCTF). The challenges and answers on this page are newly written for this guide; no HydraCTF code, database, flag, level text, or challenge content is copied.

## Zero-dependency rules

- No CTF server, internet connection, package install, Kali tool, account, or external dataset is needed.
- Challenges use only information in the prompt, the guide, and basic reasoning. Optional command-line approaches use standard Linux tools already covered in the book.
- Flags are learning tokens, not credentials or access tokens. They do not authenticate to a service.
- Cryptography levels use **toy encodings and concepts**. They do not teach breaking real encryption or attacking systems.
- Work on the worksheet offline if desired. The [answer key](Answer_Key.md) contains spoilers.

## How to play

1. Read one level and write down the safest correct decision or decoded toy string.
2. Submit the exact case-sensitive `FLAG{...}` token shown by your result.
3. Record a one-sentence explanation. A flag without a correct explanation does not demonstrate understanding.
4. Check the answer key only after attempting the level.

## Base Levels — Field Support

### BASE-0 — Identify the box

**Scenario:** A device reports `ID=debian`, `VERSION_ID=13`, and `uname -m=aarch64`. A colleague asks you to add Kali repositories so `kali-linux-default` can be installed.

**Task:** State the safe next step. Which OS repository must remain configured?

**Hint:** Hardware architecture does not determine which distribution repositories are safe to mix.

**Flag format:** `FLAG{...}`

### BASE-1 — Protect the data before recovery

**Scenario:** A Raspberry Pi will not boot after power was disconnected during a write. Its storage may hold the only copy of a community project’s data.

**Task:** Choose the first response that minimizes data loss. Do not assume the storage is empty or irrecoverable.

**Hint:** Record the symptom and verify supply/boot indicators for the exact board before re-imaging.

**Flag format:** `FLAG{...}`

### BASE-2 — Diagnose one layer at a time

**Scenario:** `ip -brief address` shows `wlan0 UP 192.168.1.42/24`; `ip route` shows a default route via `192.168.1.1`; `getent hosts example.org` returns no address.

**Task:** Identify what to investigate next without scanning other network devices.

**Hint:** The Pi has a link, an address, and a route. Name the next layer.

**Flag format:** `FLAG{...}`

### BASE-3 — Protect sensitive records

**Scenario:** A public support ticket contains a child’s name, a case narrative, and exact coordinates for an explosive-hazard report.

**Task:** State the safe response and the proper route for handling the record.

**Hint:** Do-no-harm, data minimization, and the organization’s designated protection channel apply to technical support too.

**Flag format:** `FLAG{...}`

## Quiz Levels — Knowledge Check

Each quiz is worth one point. Answer without consulting the key; use the linked chapter to review any missed concept. No software is required.

### QUIZ-0 — Who handles a suspected explosive item?

Choose one:

A. A technical support operative takes a close-up photo and identifies it from a database.
B. Nobody approaches or handles it; follow local safety procedure and report through the designated trained authority.
C. A community member moves it away from a path.

### QUIZ-1 — Which resolution is the thematic Security Council reference on mine action?

Choose one:

A. S/RES/2365 (2017)
B. S/RES/2493 (2019)
C. S/RES/2764 (2024)

### QUIZ-2 — What is the safe treatment of a child-protection report in a support ticket?

Choose one:

A. Include the child’s name and exact location so the ticket can be searched publicly.
B. Send the case details to the technical mailing list for awareness.
C. Minimize identifying details and use the organization’s restricted, designated child-protection channel.

### QUIZ-3 — What does meaningful WPS participation require in support-system design?

Choose one:

A. Consult only mission leadership and assume tools work equally for every user.
B. Consult affected women and relevant groups; address access, safety, and privacy barriers.
C. Collect gender and precise location data by default, whether or not needed.

### QUIZ-4 — How should you assess the claim “genetically engineered crops cause cancer”?

Choose one:

A. Treat every crop trait, pesticide, exposure, and food as one identical hazard.
B. Identify the specific crop/trait, product and exposure, consult current case-by-case assessments, and distinguish hazard evidence from exposure-specific risk.
C. Assume no engineered crop or associated agricultural practice can ever cause harm.

### QUIZ-5 — Does a company’s profit motive prove that it intended to cause a particular harm?

Choose one:

A. Yes; a financial incentive alone proves intent and causation.
B. No; examine the specific evidence, product, exposure, regulatory record, and any admissions or findings before claiming intent or causation.
C. Corporate conduct can never be investigated from public records.

### PORTAL-0 — Bootstrap puzzle for a Coffee Cipher

Before a support team performs an authorized security assessment, it records the approved assets, methods, time window, contacts, and stop conditions in a written **_____**.

**Task:** Fill in the missing phrase and submit its exact `FLAG{...}` token to the CPIP Book Portal starter form.

**Important:** This is a public puzzle gate, not identity verification. Its answer is shareable and is listed in the answer key. The portal issues a separate random per-edition Coffee Cipher after the starter step.

## Crypto Flag Levels

### CRYPTO-0 — ROT13 is encoding

**Ciphertext:** `SYNT{GUR_RAPBQRQ_ZRFFNTR_VF_ABG_FRPERG}`

**Task:** Rotate alphabetic characters by 13 places. Keep braces and underscores unchanged. What does the flag say?

**Hint:** A becomes N; N becomes A. This is a reversible substitution, not secure encryption.

**Flag format:** The decoded string itself.

### CRYPTO-1 — Caesar shift is a toy

**Ciphertext:** `IODJ{FDHVDU_LV_QRW_HQFUBSWLRQ}`

**Task:** Each alphabetic character was shifted forward by 3. Shift backward by 3 to recover the flag.

**Hint:** I becomes F. Preserve capitalization and punctuation.

**Flag format:** The decoded string itself.

### CRYPTO-2 — Hashes are not ciphertext

**Scenario:** A support log contains a SHA-256 digest of a credential. Someone asks you to “decrypt the hash” to recover the password.

**Task:** Choose the technically correct, authorized support response: decrypt it, publish it for lookup, or use the approved credential reset/verification process while protecting the digest.

**Hint:** Hashing and encryption have different purposes; do not expose real credential material in a challenge.

**Flag format:** `FLAG{...}`

## Debrief and next steps

The learning objective is sound judgment, not speed. For system support, continue with [the field troubleshooting playbooks](../Raspberry%20Pi%20Field%20Support/Support_Playbooks.md). For peace-operations context, read [mine-action support](../Peace%20Operations%20Field%20Support/Mine_Action_and_Explosive_Hazards.md) and [child protection/WPS](../Peace%20Operations%20Field%20Support/Child_Protection_and_WPS.md). For cryptography vocabulary, read [CPIP- architecture and principles](../16.%20CPIP-%20Guide/Architecture_and_Principles.md) and its caveats. Try other CTFs only in their intended, authorized environment.

## Inspiration and attribution

HydraCTF is a separate project by William Majanja, described in its repository as a CTF for hackathons and societal scenarios. This book uses only the broad educational idea of progressive levels and flags. Its challenge content and answer key are original to this guide.
