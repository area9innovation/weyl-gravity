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
has `diff_descent_status: NONZERO_COMPLETE` and length four.  The separate
`intrinsic_weyl_descent_status` is `TRIVIAL` for the type-B strict densities,
`TRIVIAL_WITH_PRIMITIVE` for the type-D pair, and explicitly pending for the
type-A anomaly continuation.  Class status is a third independent field:
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
kept `NOT_COMPUTED` rather than silently identified with the variational
current.

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
- `quantum-weyl/local_bv/certificates/TRIVIALITY_CERTIFICATE.json`;
- `quantum-weyl/local_bv/descent/DESCENT_DATABASE_DIMENSION_FOUR.json`.

## Verification receipt

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | compile changed Python, reproduce four certificates, validate schemas, scoped diff check | under 5 s | pass |
| 1 | focused bicomplex/triviality/Euler/candidate rail | 1.28 s | 25 pass in 1.22 s |
| 1 | complete local-BV unit rail | 29.32 s wall | 140 pass in 28.68 s |
| 1 | four affected certificates under hash seeds `1,7,123`, parallel | 3.8 s wall | pass |
| 2 | two-pass paper build in isolated output directory | 4.4 s | pass; no unresolved references |

The complete local rail remains below the agreed 60-second threshold.  Tier
3 was not triggered: this is a partial local descent database, not the full
cohomology theorem, a classical freeze, a lifecycle promotion to coefficient
or QME status, or a release.

## Next local gate

Continue the intrinsic type-A anomaly descent from the certified
`d_h(omega) wedge Theta_E` residual, then formulate the exact mapping-cone
coboundary matrices.  Antifield completion remains blocked until the
classical team exports the portable Koszul--Tate rows.
