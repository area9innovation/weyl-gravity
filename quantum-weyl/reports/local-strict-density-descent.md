# Horizontal bicomplex, intrinsic descent, and triviality receipt

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `PARTIAL_DESCENT_DATABASE`

Classical snapshot: `UNFROZEN`

## Outcome

The local algebra now has an exact horizontal exterior algebra over the
coordinate jets.  It implements coefficient-parity-aware wedge products,
the horizontal differential, contraction with the odd diffeomorphism ghost,
and the BRST row for a covariant weight-one top-density coefficient.  Exact
checks give

```text
d_h^2 = 0
Q density = partial_mu(xi^mu density)
Q^2 density = 0
Q d_h = d_h Q
```

For a strict Weyl-invariant top density `L`, and separately for its Weyl-ghost
lift `omega L`, the engine constructs the raw contraction tower
`I_k = i_xi^k I_0`.  It then solves the proportionality rows rather than
inserting a factorial formula:

```text
Q I_k = (1/(k+1)) d_h I_(k+1).
```

The resulting descent coefficients are

```text
1, -1, 1/2, -1/6, 1/24,
```

and every equation `Q a_k + d_h a_(k+1) = 0` is verified exactly through the
BRST-closed form-degree-zero bottom.  The counterterm tower has bidegrees

```text
(form degree, ghost number) = (4,0), (3,1), ..., (0,4),
```

while the anomaly tower runs from `(4,1)` to `(0,5)`.

## Candidate ledger

The ledger no longer overloads one descent status.  Every covariant top form
has `diff_descent_status: NONZERO_DIFF_TOWER` and length four.  The separate
`intrinsic_weyl_descent_status` is `STRICTLY_WEYL_INVARIANT` for the
ghost-number-zero `C^2` and `C dual C` densities, while their Weyl-ghost lifts
have intrinsic descent `TRIVIAL`.  It is `TRIVIAL_WITH_PRIMITIVE` for the
type-D pair and `IN_PROGRESS` for the type-A anomaly continuation.
Relative class status is a third independent field:
only `Box R` and `omega Box R` are currently `EXACT`; all other candidates
remain `UNDECIDED` pending the complete coboundary ansatz.

The type-D certificate stores both primitives.  In particular,

```text
d_h(R nabla omega - omega nabla R) = R Box omega - omega Box R
omega Box R = -(1/12) Q_W(R^2) - d_h(R nabla omega - omega nabla R).
```

For Euler, the machine derives the Weyl connection row from
`Q_W g_ab=2 omega g_ab`, derives `delta R=D(delta connection)`, verifies
`D R=0`, and proves

```text
delta E4 - d_h Theta_E(delta) = 0
Q E4 + d_h(-Theta_E(Q)) = 0.
```

For `omega E4`, the first attempted intrinsic step leaves the exact residual
`d_h(omega) wedge Theta_E`; that residual remains a regression input rather
than being silently identified with the variational current.  The generalized connection
`tilde_omega_a = partial_a omega - Schouten_ab dx^b` has now been admitted.
Theorem 1 of Boulanger's
[Wess--Zumino classification](https://arxiv.org/abs/0704.2472) prints the
coefficient `(-1)^p 2^(-p) m!/(r!p!)`, which specializes to
`(1/4,-1,1)` for `r=(0,1,2)`.  The project top component is `omega E4`, so a
single global factor of four fixed by that top component gives the normalized
project vector `(1,-4,4)`.  The older `(4,-4,1)` vector is retained only as a
rejected, underived carrier rescaling.  No bidegree-dependent normalization
is allowed.  This resolves the convention map; the frozen-carrier connecting
equations now close.  The independent Lorentzian tensor-basis reconstruction
described below also closes the epsilon-contracted top-identification gate.

The generalized-connection dictionary now freezes total degree, ordinary
ghost/form bidegree components, parity, engineering dimension, Weyl weight,
tensor type, and index symmetries for `omega`, `dx`, `partial omega`,
`K dx`, `tilde_omega`, `Gamma dx`, the Weyl two-form, and epsilon.  It also
freezes the source definitions of the total differential,
`tilde_omega`, the Schouten tensor, the Weyl two-form, and the top Euler
factor `e^4_1=(1/4) omega E4`.  All five tower slots `(1,4)` through `(5,0)`
now have content-addressed coarse carrier manifests and explicit alternating
signs for `D=Q_W+(-1)^ghost_number d_h`.  A primary-source reread sharpened
the carrier bound to `0 <= r <= m=n/2=2`: the intrinsic four-dimensional
tower therefore has term counts `(3,2,1,0,0)`, and the `(4,1)` and `(5,0)`
slots are structurally zero.  The earlier coarse manifests that omitted this
bound remain immutable historical receipts, but every corrected manifest
names and supersedes its predecessor.

Expanding `tilde_omega=U-P`, with `U_a=partial_a omega` and
`P_a=K_ab dx^b`, gives exact normalized coefficient rows

```text
(1,4):  1,  4,  4
(2,3): -4, -8
(3,2):  4
(4,1):  zero
(5,0):  zero.
```

The top row reconstructs `omega epsilon (W+2X)(W+2X)=omega E4`, while the
bottom `4 omega epsilon U U dx dx` is `Q_W`-closed directly from
`Q_W omega=Q_W U=Q_W dx=0`.  These are now verified component statements.
The two connecting identities are now verified in the frozen Euler carrier
algebra after expanding `tilde_omega=U-P`.  Tensor-orbit generation and
canonical quotienting of the full production basis remain `NOT_COMPUTED`.
The `r=0` component is recorded separately as type B; the `r=1,2` components
form the type-A template.  After the independent head reconstruction, its
intrinsic descent status is `NONTRIVIAL_COMPLETE`.  This label applies to the
intrinsic Weyl descent only; the relative BV class remains `UNDECIDED`.

The connecting-identity preflight now separates coefficient parity from total
form parity in an indexed carrier algebra and applies `Q_W` rather than merely
inspecting factor counts.  It independently reproduces zero for the bottom
representative and verifies `Q_W^2=0` on every generator whose row is
available.  The Weyl-two-form and Cotton rows remain explicitly
`NOT_COMPUTED`; they are not silently interpreted as zero.

There is also a nontrivial source/project convention bridge.  With the project
definition

```text
A_project[a,b,c] = nabla_b P_ca - nabla_c P_ba,
```

the source convention is exactly

```text
C_source[a,b,c] = -A_project[a,b,c].
```

This sign is proved against the existing Schouten derivative relation and is
now inserted in the pending horizontal Weyl identity.  Finally, the Ricci
decomposition engine permits an explicitly bounded two-Riemann expansion:
the exact 25 branches split into `1` Weyl--Weyl, `8` Weyl--Schouten, and `16`
Schouten--Schouten terms.  The independent reconstruction now compares this
decomposition with the frozen Euler density as a completed tensor identity.

The reconstruction fixes Lorentzian signature `(-,+,+,+)`, carrier
orientation `epsilon_0123=+1`, and
`epsilon_abcd epsilon^cdef=-2 delta_ab^ef`.  It constructs the full
ten-dimensional algebraic Weyl space and ten-dimensional symmetric Schouten
space and checks 55 Weyl-square, 55 Schouten-square, and 100 mixed basis
cases.  All 210 exact residuals vanish.  Reversing the carrier orientation
fails on nonzero cases, and perturbing the Schouten-square coefficient fails.
The mixed epsilon contraction vanishes structurally by Weyl tracefreeness, so
it is recorded as coefficient-insensitive rather than used as a false
negative control.

An exact reduced covariant tensor-sector audit now constructs the full
four-dimensional algebraic Weyl space (dimension `10`) and irreducible
Cotton space (dimension `16`) from their defining linear identities.  Every
independent rational basis case vanishes in the four curvature sectors that
enter the generalized-connection calculation.  The independent ordinary
projector then substitutes `tilde_omega=U-P` before cancellation, uses
`D=Q_W+(-1)^g d_h`, and retains separate Hessian and Cotton images.  Across
`136` exact Schouten, Weyl, Cotton, and Schouten--Weyl basis cases it verifies

```text
Q_W a14 + d_h a23 = 0
Q_W a23 - d_h a32 = 0
Q_W a32 = 0.
```

The witness calculation contains `12`, `60`, and `48` nonzero differential
summands in the three components before cancellation.  Both connecting pairs
carry independent left/right hashes and verify `RIGHT_EQUALS_NEGATIVE_LEFT`.
Changing the mixed `U/P` coefficient by the factor `5/4` breaks all `136`
cases.  A relative Cotton-sign flip is invisible after imposing the
irreducible Cotton identities; the receipt records that fact rather than
claiming false sensitivity.  A deliberately nonphysical raw Cotton
coordinate probe changes under the same flip and therefore checks only the
row wiring.  Exact constraint ranks are `11` in the 21-coordinate Weyl
presentation and `8` in the 24-coordinate Cotton presentation.  Cached
analyses are serialized and every caller receives a fresh copy.

The generic quotient engine's exhaustiveness proof is also fail-closed at the
artifact layer.  Promotion to `COMPLETE_NONTRIVIALITY_WITNESS` now requires
seven embedded canonical artifacts: the basis manifest, declared bounds,
generator algebra, grading solution, orbit enumeration, identity quotient
including the exact `Q` and `d_h` matrices, and the proof/source artifact.
Every payload is reparsed, canonically serialized, rehashed, and cross-checked
against its named proof field.  Well-formed but unsupported hash strings no
longer suffice.

## Claim boundary

This is the strict-density part of the antifield-independent descent
database, not the complete `H^{0,4}(s|d)` or `H^{1,4}(s|d)` result.  Still
unavailable are:

- exhaustive AFN0 lower-form mapping-cone and boundary bases;
- antifield/Koszul--Tate and equation-of-motion sectors;
- proof of cohomological nontriviality for the strict candidates;
- anomaly coefficients, QME restoration, and residual transfer.

The coordinate BRST differential and horizontal differential commute.  The
standard bicomplex totalization supplies the grading sign; this convention is
stored explicitly rather than silently switching between commuting and
anticommuting presentations.

## Machine receipts

- `quantum-weyl/local_bv/certificates/HORIZONTAL_BICOMPLEX_CERTIFICATE.json`;
- `quantum-weyl/local_bv/certificates/EULER_TRANSGRESSION_CERTIFICATE.json`;
- `quantum-weyl/local_bv/certificates/euler_bidegree_manifests/*.json`;
- `quantum-weyl/local_bv/certificates/TRIVIALITY_CERTIFICATE.json`;
- `quantum-weyl/local_bv/descent/DESCENT_DATABASE_DIMENSION_FOUR.json`.

## Verification receipt

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | compile changed Python, reproduce four certificates, validate schemas, scoped diff check | under 5 s | pass |
| 1 | focused bicomplex/triviality/Euler/candidate/AFN0 rail | under 2 s | pass |
| 1 | complete local-BV unit rail | 23.64 s wall | 159 pass in 23.24 s |
| 1 | five primary affected certificates under hash seeds `1,7,123`, parallel | under 2 s wall | pass |
| 2 | two-pass paper build in isolated output directory | 4.4 s | pass; no unresolved references |

The complete local rail remains below the agreed 60-second threshold.  Tier
3 was not triggered: this is a partial local descent database, not the full
cohomology theorem, a classical freeze, a lifecycle promotion to coefficient
or QME status, or a release.

### Pre-production hardening addendum

The generalized-connection normalization, five bidegree manifests, strict
Euler schema, and artifact-bound exhaustiveness proof were verified with:

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | `py_compile` for six changed modules; JSON parse; scoped `git diff --check` | under 1 s | pass |
| 1 | focused generalized-connection, Euler, quotient, AFN0, and basis-gap consumers | 5.0 s | 29 pass |
| 2 | complete `quantum-weyl/local_bv/tests` discovery rail | 26.6 s | 175 pass |
| 2 | Euler, quotient, AFN0, and basis-gap checks under hash seeds `1,7,123` | 23.7 s | pass |

The complete classical pipeline and repository Tier 3 suite were not run:
this change neither freezes a classical snapshot nor promotes the intrinsic
Euler tower, an AFN0 quotient theorem, a QME state, or a `d_quotient`
contribution verdict.

### Intrinsic component-expansion addendum

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | compile expansion modules, strict schema validation, certificate reproduction, scoped diff check | under 3 s | pass |
| 1 | Euler/generalized-connection plus AFN0 and basis-gap consumers | 5.7 s | 17 pass |
| 2 | complete `quantum-weyl/local_bv/tests` discovery rail | 28.2 s | 177 pass |
| 2 | Euler certificate under hash seeds `1,7,123` | 1.8 s | pass |

Tier 3 and the classical pipeline were again not triggered.  Ordinary
bidegree expansion is now verified, but the two connecting identities and
the AFN0 quotient theorem remain open; no lifecycle state or `d_quotient`
verdict was promoted.

### Connecting-identity preflight addendum

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | Euler certificate reproduction/check, strict nested schema, scoped diff check | under 3 s | pass |
| 1 | focused Euler preflight, intrinsic expansion, certificate, and Weyl decomposition rail | 0.7 s | 13 pass |
| 1 | exact reduced tensor-sector audit plus certificate consumers | 1.5 s | 7 pass |
| 2 | complete `quantum-weyl/local_bv/tests` discovery rail | 30.4 s wall | 181 pass in 30.0 s |
| 2 | Euler preflight hash under seeds `1,7,123`; affected Weyl decomposition, Schouten-zero image, and dimension-four catalogue certificates | under 15 s | pass |

The complete local rail remains below 60 seconds.  Tier 3 and the classical
pipeline were not triggered because this preflight deliberately leaves the
horizontal generator rows, epsilon contraction, connecting cancellations,
AFN0 theorem, and `d_quotient` verdict unpromoted.

### Ordinary-bidegree projection addendum

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | compile changed modules; reproduce/check Euler and horizontal certificates; strict schemas; scoped diff check | under 30 s | pass |
| 1 | Euler tensor audit, ordinary projection, expansion, preflight, certificate, and descent-database consumers | 12.9 s | 16 pass |
| 2 | complete `quantum-weyl/local_bv/tests` discovery rail | 41.2 s wall | 185 pass in 40.7 s |
| 2 | Euler projection and horizontal-database hashes under seeds `1,7,123`, parallel | 14.2 s wall | pass |

The complete local rail remains below the agreed 60-second threshold.  Tier
3 and the classical pipeline were not triggered: the intrinsic Euler tower
advanced, but the AFN0 quotient theorem, classical
freeze, QME lifecycle, and `d_quotient` verdict remain unpromoted.

### Lorentzian Euler-head reconstruction addendum

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | changed Python compile, strict schema parse, generated-artifact reproduction, scoped diff check | under 30 s | pass |
| 1 | Euler head, connecting equations, expansion, preflight, descent database, and candidate consumers | 24.5 s | 30 pass |
| 2 | complete `quantum-weyl/local_bv/tests` rail | about 28 s wall | 188 pass |
| 2 | Euler, horizontal, and candidate certificate consumers under hash seeds `1,7,123`, parallel | under 25 s wall | 10 pass per seed |

The suite remains below the 60-second full-tier threshold.  No classical,
spectral, Lorentzian, or `d_quotient` verdict was rerun because the new proof
is `LOCAL-ALGEBRAIC` and changes none of those inputs.

## Next local gate

Integrate the completed intrinsic Euler tower into the exhaustive AFN0
mapping-cone bases and formulate the exact coboundary matrices.  Antifield
completion remains blocked until the classical team exports the portable
Koszul--Tate rows.
