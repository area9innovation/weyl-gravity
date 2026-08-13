# BT quadrupole mirror-sheet dichotomy

**Certificate:**
`REVERSE_PHYSICS_BT_QUADRUPOLE_MIRROR_SHEET_DICHOTOMY_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Lifecycle:** `CLASSIFIED`

## Result

The compact scalar quadrupole cannot satisfy the positive-Hilbert
ghost-even observable gate by a regular parity projection on the public
perturbative vacuum chart.  This is now an exact quadrupole-specific
obstruction, rather than an unchecked parity condition.

There is also a smallest constructive escape: put the perturbative vacuum and
its exchanged mirror vacuum on two cross-paired sheets.  The block-diagonal
pair of mirrored quadrupoles is then local sheet by sheet, ghost-even,
Krein-self-adjoint and Hilbert-self-adjoint.  On the normalized symmetric
sheet sector it retains the already certified exact darkness and strict
compact-spacetime order-eight response.

The price is substantive.  The doubled source and mirror dynamics are new
data.  The public one-sheet scalar action and public (R_t) do not select
them, so this is a changed theory and not a proof of Eq. (19).

## Exact hidden image

Write the compact quadrupole as a symmetric bilinear differential expression

\[
 D[\phi]=B(\phi,\phi).
\]

On the overlap of the two extended-field charts the hidden exchange is

\[
 h(\phi)=g-\phi,
 \qquad g={1\over\lambda}\log{\psi\over\lambda}.
\]

Bilinearity gives the exact identity

\[
 D[h(\phi)]=D[\phi]-2B(\phi,g)+D[g].
\]

Therefore

\[
 D_{\rm even}=D[\phi]-B(\phi,g)+{1\over2}D[g],
 \qquad
 D_{\rm odd}=B(\phi,g)-{1\over2}D[g].
\]

Both expressions contain (log(\psi/\lambda)).  They are defined on the
chart overlap (psi\ne0), not at the perturbative vacuum (psi=0).  The
predecessor's unit/nonunit theorem already shows that the logarithm cannot be
created by a regular same-chart local-symbol automorphism.  The calculation
below proves directly that the quadrupole itself does not acquire a removable
singularity.

## Scaled mirror-jet nonextension

Set (phi=0) and choose a local jet (f) with a nonzero quadrupole pair
coefficient.  For (t>0), define

\[
 \psi_t=\lambda t e^{\lambda f}.
\]

Every finite local jet of (psi_t) tends to zero with (t), so all these
paths approach the same perturbative-vacuum jet.  But

\[
 h(0)={1\over\lambda}\log t+f.
\]

The constant (lambda^{-1}log t) has no nonzero-momentum pair coefficient.
Consequently the selected pair coefficient of (D[h(0)]) equals that of
(D[f]), independently of (t).

The exact rational fixture is

\[
 P=(1,0,0,0),\qquad r=(0,1/2,0,0),\qquad a=(0,1,0,0),
\]

for which the certified covariant quadrupole symbol is exactly one.  The
sample sequence (t=1,1/2,1/3,1/5) therefore gives coefficients
(1,1,1,1), even though every (psi_t) jet tends to zero.  Taking (f=0)
instead gives coefficient zero with the same limiting vacuum jet.

Hence the hidden quadrupole image has no single-valued continuous local-jet
extension to (psi=0).  The even and odd projections each contain one half
of this direction-dependent term, so neither extends regularly either.

This closes the direct task left by the positive-real-structure theorem:
the public compact scalar quadrupole is not a regular same-chart ghost-even
observable.

## Minimal two-sheet completion

Introduce two isomorphic local sheets (A) and (B), centered on the two
exchanged vacua.  On their sheet label use

\[
 G=\kappa=
 \begin{pmatrix}0&1\\1&0\end{pmatrix},
 \qquad G\kappa=I.
\]

Let (D_A) be the original quadrupole and (D_B) its regular mirror-chart
copy.  Their combined density is

\[
 D_{\rm dbl}=\begin{pmatrix}D_A&0\\0&D_B\end{pmatrix}.
\]

Exchange covariance identifies the two transported local expressions, and
therefore

\[
 \kappa D_{\rm dbl}\kappa=D_{\rm dbl},\qquad
 D_{\rm dbl}^{\sharp}=D_{\rm dbl},\qquad
 D_{\rm dbl}^{*}=D_{\rm dbl}.
\]

This is precisely the ghost-even real structure required by the positive
Hilbertization theorem.  Locality is componentwise:
(D_{\rm dbl}(O)\) lies in the direct sum of the two sheet-local algebras, and
(kappa) exchanges those summands.

The symmetric sheet projector is

\[
 P_+={1\over2}\begin{pmatrix}1&1\\1&1\end{pmatrix}.
\]

It is idempotent and ghost-even.  If both transported sheet amplitudes equal
(a), normalized symmetric preparation and detection give (a), not
(2a).  The exact fixture (a=3/5) yields probability (9/25) both before
and after doubling.  Thus normalization removes the apparent factor of two.

The leading scalar response vanishes on each sheet by the same fibrewise STF
identity, while the higher quadrupole response is equal and nonzero on the
two transported sheets.  The predecessor's strict bound is therefore
inherited unchanged:

\[
 {Q_{8,\rm compact}\over\bar q_4}>{1\over18874368000}.
\]

## Meaning

This calculation gives a clean fork.

- In the public one-sheet perturbative scalar theory, regular ghost-parity
  projection of the compact quadrupole is obstructed.
- In a declared doubled mirror-vacuum theory, a local ghost-even positive
  quadrupole exists and retains the physical dark response.

The second statement is constructive, but it changes the source architecture.
It does not show that public BT dynamics prepares the symmetric sheet state,
couples the two sheets, or reproduces this block through (R_t).  Treating it
as the original theory would conceal the main scientific cost of the repair.

## Claim boundary and next gate

This result does not establish a no-go for singular, localized, on-shell,
unbounded or nonperturbative hidden parity.  It does not construct a positive
Haag--Kastler net, all-order Born rule, complete finite-time evolution,
all-time scattering operator, general Eq. (19), gravity/BV--BRST transfer or
anything `LORENTZIAN-CAUSAL`.

The best remaining one-sheet physical calculation is now to construct a
polynomial ghost-even detector directly in the auxiliary
(Omega,\Upsilon) fields and test its (q_8) response.  The alternative is
to adopt the doubled theory explicitly and derive common domains and dynamics
for its symmetric sector.  Regular parity projection of the scalar
quadrupole should not be pursued further.

## Verification commands

```text
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_quadrupole_mirror_sheet_dichotomy.py --write --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_quadrupole_mirror_sheet_dichotomy.py
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_quadrupole_mirror_sheet_dichotomy
```

## Verification receipt

All Python and TeX processes ran sequentially under `ulimit -v 500000`; no
out-of-memory event occurred.

- Tier 0: three Python files compile; the work item, append-only event, schema
  and certificate parse as JSON; and the certificate validates against its
  JSON schema.  The compile and schema processes peaked at 14,932 KiB and
  21,564 KiB, respectively.
- Producer: 34/34 exact checks pass in 0.03 s at 16,348 KiB peak RSS.
- Independent verifier: 46/46 checks pass in 0.02 s at 15,516 KiB.  It
  reconstructs the quadrupole fixture, cross-sheet adjoints, projector and
  normalization without importing the producer.
- Focused suite: all 30 tests pass in 0.07 s at 18,228 KiB, including 29
  mutations of the parity image, path witness, sheet metric, response and
  claim boundaries.
- Papers V and VI compile twice with halt-on-error.  Their final PDFs have 75
  pages (723,791 bytes) and 65 pages (684,752 bytes), with SHA-256
  `f11bd715a4c0b6f7975be4c26b26c4b9e3607aaac7a9fa0fa2ad69856c2812a0`
  and
  `26ef9b8253937c008c71c80216313ac378c86ce88b0d509e6d5fb07f4a430e29`.
  The final passes took 0.51 s and 0.52 s at 50,920 KiB and 51,004 KiB.
  There are no undefined citations or references and no new overfull box.
- Tier 3 is fail-closed, not a pass: 2,913 tests ran in 807.390 s (808.45 s
  enclosing wall time) at 391,436 KiB peak RSS, with 32 failures and 9 skips.
  All 30 new tests passed.  The sorted failure-name list has SHA-256
  `aa3bafce92f854ff187965026231c88dd3913d490c610a32a942eee59b68f386`,
  exactly the preceding baseline hash.  The old failures therefore remain
  findings and block a repository freeze, while this package introduces no
  Tier-3 regression.
- The Science Forge planning fold accepts 1,557 nodes with zero invalid work
  items and zero malformed events in 5.91 s at 258,356 KiB peak RSS.
- The advisory shadow rail inventories 1,618 certificates and 1,396 verifier
  files.  Its wrapper exits zero by design, but the bridge audit remains a
  fail-closed `E9118` finding caused by the known Forge binary/stdlib hash
  mismatch, and the coverage census remains drifted from the 2026-07-19
  baseline.  Diagnostics are preserved under
  `/tmp/bt-quadrupole-mirror-shadow.tFbRL2`; no advisory finding is counted as
  a pass.

The generated certificate SHA-256 is
`03a81f8bc113eaf4ebdb0d25a1e3f1308850b385202989e4d14ca0f8b79866a7`.

CLOSE-OUT: DONE — regular same-chart ghost parity of the compact scalar
quadrupole is exactly obstructed, while the minimal doubled mirror-sheet
carrier supplies a local ghost-even positive observable with the inherited
normalized dark response; the latter is a changed theory, not public Eq. (19).

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_QUADRUPOLE_MIRROR_SHEET_DICHOTOMY_V1.json`
