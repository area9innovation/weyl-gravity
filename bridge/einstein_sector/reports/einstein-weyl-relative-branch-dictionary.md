# Same-background Einstein--Weyl relative branch dictionary

Bridge priority: 1.  Current global lifecycle: `ONSHELL_MAP_ONLY`.  Activation
gate: `OPEN`.

The generated dictionary exports, without cross-background identification,
the compact Plebański--Hacyan Einstein/Weyl inclusion, solution cofibers,
branch representatives and action-derived pairings.  The generic axial block
and generic polar blocks both have `DERIVED_COFIBER_TRIANGLE` lifecycle at the
polynomial ghost--field--equation--identity level, complete solution-module
quotients, and direct Lee--Wald forms.  Cyclic BV compatibility of the polar
chain map is no longer merely open: strict compatibility with the fixed
identity field map is obstructed by a nonradical solution-pairing defect in
both parities.  Corrected nonidentity or chain-homotopy cyclic morphisms remain
open.

The exceptional `ell=1,k=0` solution cofiber now has explicit CRT projectors
and a nonradical action pairing.  The homogeneous solution cofiber is zero,
although its identity inclusion has the nontrivial nilpotent relative form.
The generalized-zero twist primary also has zero solution cofiber, with
relative operator `-2*I`.  Nonzero-`k` exceptional and global off-shell fields
remain `NO_CERTIFIED_MAP`.  The boundary and
cross-background row is `NO_CERTIFIED_MAP` in every relevant field.  Hence the
dictionary does not activate `EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1`.

The quadratic handoff now imports the complete declared `k=0`
homogeneous/twist-times-`ell=2` extra bounded-resonance source matrix.  The
twist-position block has rank two and the twist-velocity block has pointwise
rank four for real time.  This does not substitute for the linear bridge or
complete the finite-harmonic tangent cone: the simultaneous stabilizer and
resonance zero locus remains open.

Evidence and verification:

- `bridge/certificates/einstein_weyl_relative_branch_dictionary.json`
- `bridge/einstein_sector/einstein_weyl_relative_branch_dictionary.py`
- `bridge/einstein_sector/verify_einstein_weyl_relative_branch_dictionary.py`

Tier 1 consists of the generator freshness check, the independent hash and
lifecycle verifier, and three scoped unit tests.  Imported Tier-2 mathematical
artifacts are accepted by content hash.  Tier 3 is not run because the full
all-sector relative triangle remains open.
