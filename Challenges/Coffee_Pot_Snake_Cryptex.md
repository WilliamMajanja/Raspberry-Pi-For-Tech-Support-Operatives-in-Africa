# The Coffee Pot Snake Cryptex

This offline puzzle trail connects the book’s support and information-management ideas. It can be solved from the book with either a paper wheel prop or a 3D-printed six-wheel alignment prop. No CTF server, network access, or package installation is required.

## The story

A community support team is preparing an offline field kit. Its handover note is held by a six-letter word-wheel prop. Solve six short support questions, take the first letter of each answer, and set the wheels in order.

The physical device is a classroom puzzle, not secure storage. Its code is a toy answer, not a password, API key, CPIP credential, or protection for real data.

## Solve the offline starter

For each prompt, write the missing word and take its **first letter**. Read the six letters in order to get the word-wheel setting.

1. Preserve a separate ______ before re-imaging a device. *(Hint: a recovery copy.)*
2. Share sensitive case reports only through an ______ channel. *(Hint: access has been approved.)*
3. ______ the current state before making an approved change. *(Hint: make a record.)*
4. ______ original storage if it might contain the only copy of important data. *(Hint: do not overwrite it.)*
5. Remove ______ identifiers from a public support report. *(Hint: data minimization.)*
6. Compare a digest with the ______ SHA-256 manifest. *(Hint: it was issued with the files.)*

The answer is a puzzle word, not the separate **PORTAL-0** answer. The CPIP Book Portal starter puzzle has its own answer in the [challenge answer key](Answer_Key.md); neither answer is an identity check or a secret.

## Paper/cardboard version

Download the [A4 paper-wheel and sleeve template](Coffee_Pot_Snake_Paper_Cryptex.svg). Print at **100% / actual size**; disable “fit to page.” Reuse a smooth paper or cardboard tube about 50 mm in diameter and 140–160 mm long. The template has six alphabet bands, six viewing windows, a sleeve, and a glue tab. Cut the red outlines and fold the green dashed line. Use blunt scissors and paper-safe glue; an instructor may pre-cut the windows.

Wrap one alphabet band around the tube for each window. Tape each band into a loose ring so it can rotate; do not glue it to the tube. Place the sleeve around the bands and align its six windows with the rings. Rotate one ring at a time until the answer letters appear vertically in order. The paper version is a **non-locking display prop**; a note can be placed inside the tube and removed without using the code.

## 3D-printed version

The [parametric OpenSCAD model](Coffee_Pot_Snake_Cryptex.scad) provides a slotted sleeve, six notched wheels, a sliding keyed plug, and retaining collars. Open it in OpenSCAD and set `part` to `"sleeve"`, `"wheel"`, `"plug"`, or `"collar"`; set `wheel_index` from 0 to 5 when exporting a wheel. The default `"assembly"` view shows the parts together. Export one sleeve, six wheels, one plug, and two collars. The alphabet bands on the SVG template wrap around the wheel rims; orient each answer letter over its wheel’s internal notch, then install the wheel so the fixed sleeve window shows that letter when the notch faces the plug lugs.

The plug lugs are blocked by unaligned wheels and can slide when all six notches line up. Add the wheels through one end of the sleeve, insert the plug, test the setting, and secure a retaining collar at each end with a removable method. Print a single wheel and test-fit it in the sleeve before making the full set: printer calibration and material shrinkage affect the clearances. Keep the plug accessible and provide a non-destructive reset path. Do not put valuables or real credentials inside.

The 3D model has not been fabricated or fit-tested in this workspace. Review the dimensions in OpenSCAD and use a locally validated printer profile. The model is a low-force teaching prop; do not force a jammed plug. Stop use if any part cracks, has a sharp edge, or creates a pinch hazard.

## Personalized editions

The optional edition generator can create a local edition identifier, a random Coffee Pot Snake cover variation, and a seeded synthetic practice exercise. The public starter puzzle remains solvable without an account. CPIP may be used by the official portal to encode puzzle-only data and issue a per-edition Coffee Cipher. The text of the book remains readable without that cipher and is not encrypted or DRM-protected.

Each generated edition can include a digest and an entry in its local issuance ledger. The ledger is a tamper-evident hash chain, not a decentralized public blockchain and not proof of a person’s identity. Copies can be shared under the stated license; the ID identifies an edition and does not restrict it.

## Hints and answer key

The [answer key](Answer_Key.md) gives the expected reasoning and word. It is intentionally separate so instructors can distribute the puzzle without its solution. Invite learners to explain the data-preservation and privacy decisions, not just set the wheels quickly.

## Editorial and security note

The puzzle word and physical wheels are not security features. Any CPIP use must be pinned to a reviewed revision, restricted to the book-puzzle operation, and described with its actual dependencies and license. The site’s cipher gate is a puzzle/access gate, not DRM or user identity verification.
