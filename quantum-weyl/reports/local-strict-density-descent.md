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
`d_h(omega) wedge Theta_E`; the remaining type-A continuation is therefore
kept `IN_PROGRESS` rather than silently identified with the variational
current.  The generalized connection
`tilde_omega_a = partial_a omega - Schouten_ab dx^b` has now been admitted.
Theorem 1 of Boulanger's
[Wess--Zumino classification](https://arxiv.org/abs/0704.2472) prints the
coefficient `(-1)^p 2^(-p) m!/(r!p!)`, which specializes to
`(1/4,-1,1)` for `r=(0,1,2)`.  The project top component is `omega E4`, so a
single global factor of four fixed by that top component gives the normalized
project vector `(1,-4,4)`.  The older `(4,-4,1)` vector is retained only as a
rejected, underived carrier rescaling.  No bidegree-dependent normalization
is allowed.  This resolves the convention map without claiming that the
intrinsic tower closes.

The generalized-connection dictionary now freezes total degree, ordinary
ghost/form bidegree components, parity, engineering dimension, Weyl weight,
tensor type, and index symmetries for `omega`, `dx`, `partial omega`,
`K dx`, `tilde_omega`, `Gamma dx`, the Weyl two-form, and epsilon.  It also
freezes the source definitions of the total differential,
`tilde_omega`, the Schouten tensor, the Weyl two-form, and the top Euler
factor `e^4_1=(1/4) omega E4`.  All five tower slots `(1,4)` through `(5,0)`
now have content-addressed coarse carrier manifests and explicit alternating
signs for `D=Q_W+(-1)^ghost_number d_h`.  Tensor-orbit generation, canonical
quotienting, and closure remain `NOT_COMPUTED`.  The `r=0` component is
recorded separately as type B; the `r=1,2` components form the type-A
template.  Its status is `NORMALIZED_TEMPLATE_NOT_YET_VERIFIED_TOWER`, not a
completed Euler certificate.  Separate regression gates cover the verified top
transgression, the retained `d omega wedge Theta_E` source, and the still-open
complete lower-descendant cancellation.

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

- the complete intrinsic type-A descent beginning at `omega E4`;
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

## Next local gate

Continue the intrinsic type-A anomaly descent from the certified
`d_h(omega) wedge Theta_E` residual, then formulate the exact mapping-cone
coboundary matrices.  Antifield completion remains blocked until the
classical team exports the portable Koszul--Tate rows.
