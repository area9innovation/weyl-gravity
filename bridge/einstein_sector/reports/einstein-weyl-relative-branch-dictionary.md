# Same-background Einstein--Weyl relative branch dictionary

Bridge priority: 1.  Current global lifecycle: `ONSHELL_MAP_ONLY`.  Activation
gate: `OPEN`.

The generated dictionary exports, without cross-background identification,
the compact Plebański--Hacyan Einstein/Weyl inclusion, solution cofibers,
branch representatives and action-derived pairings.  The generic axial block
and generic polar blocks both have `DERIVED_COFIBER_TRIANGLE` lifecycle at the
polynomial ghost--field--equation--identity level, complete solution-module
quotients, and direct Lee--Wald forms.  Cyclic BV compatibility of the generic
axial and polar chain maps is no longer merely open. The Einstein source form has inertia
`(2,0)`, whereas the Weyl form on the complete `q`-primary target has inertia
`(1,1)` in both parities. Congruence invariance therefore obstructs every
real-structure-preserving, product-equivariant standard-pairing cyclic
correction, including nonidentity maps, chain-homotopy repairs and exact
current improvements. The remaining admissible target is a noncyclic triangle
carrying the Einstein, pulled-back Weyl and relative forms separately; an
explicitly pairing-changed theorem is a different open route.

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
rank four for real time.  It also imports the first exact nonzero intersection
with the stabilizer cone: on the shared-axis `m=0` face,
`B_z^2=(2/3)X` cancels the Taub energy and the twist--extra resonant map
vanishes.  The classical tangent-cone certificate now completes this
necessary classification: every common zero in the declared carrier is an
`SO(3)` rotation of the aligned face, with electric extension
`B^2=Q_e^2/2+(2/3)X`; no off-axis branch survives.  This does not substitute
for the linear bridge or complete the general finite-harmonic tangent cone.

The bounded class is now closed negatively.  Every nonzero point on the orbit
has `B!=0`, and its zero-frequency polar `L=2` source contains the nonzero
quadratic coefficient `-7*B^2*t^2`.  A stationary linear operator cannot map
a bounded finite-quasiperiodic correction to this growth.  Smooth
exponential-polynomial corrections have the opposite verdict: the complete
finite channel ledger and physical Smith factors supply secular right
inverses after the five stabilizer moment maps vanish.  Every point of the
orbit therefore extends at second order in that class.  The causal/retarded
class remains `NO_CERTIFIED_MAP`.

Evidence and verification:

- `bridge/certificates/einstein_weyl_relative_branch_dictionary.json`
- `bridge/einstein_sector/einstein_weyl_relative_branch_dictionary.py`
- `bridge/einstein_sector/verify_einstein_weyl_relative_branch_dictionary.py`

Tier 1 consists of the generator freshness check, the independent hash and
lifecycle verifier, and five scoped unit tests.  Imported Tier-2 mathematical
artifacts are accepted by content hash.  Tier 3 is not run because the full
all-sector relative triangle remains open.
