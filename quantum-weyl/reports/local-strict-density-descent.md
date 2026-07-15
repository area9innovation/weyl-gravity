# Strict-density descent receipt

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

The same generated tower applies to `C^2` and `C dual C`, because both are
covariant strict Weyl-invariant densities.  Their counterterm and Weyl-ghost
entries now carry `NONTRIVIAL` descent status and length four.  Here
`NONTRIVIAL` means that the stored descent tower is nonzero; it does not claim
that the associated BV cohomology class is nontrivial.

`Box R` and `omega Box R` retain `TRIVIAL` status from their explicit total
derivative and `-(1/12)s(R^2)` witnesses.  The Euler counterterm and
`omega E4` remain `NOT_COMPUTED`: their Weyl variation has a separate current
descent and must not be replaced by the strict-density tower.

## Claim boundary

This is the strict-density part of the antifield-independent descent
database, not the complete `H^{0,4}(s|d)` or `H^{1,4}(s|d)` result.  Still
unavailable are:

- the Euler Weyl-current descent;
- antifield/Koszul--Tate and equation-of-motion sectors;
- proof of cohomological nontriviality for the strict candidates;
- anomaly coefficients, QME restoration, and residual transfer.

The coordinate BRST differential and horizontal differential commute.  The
standard bicomplex totalization supplies the grading sign; this convention is
stored explicitly rather than silently switching between commuting and
anticommuting presentations.

## Machine receipts

- `quantum-weyl/local_bv/certificates/LOCAL_STRICT_DENSITY_DESCENT_CERTIFICATE.json`;
- `quantum-weyl/local_bv/descent/DESCENT_DATABASE_DIMENSION_FOUR_STRICT.json`.

## Verification receipt

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | compile changed Python, reproduce certificates, validate schemas, scoped diff check | 2.2 s | pass |
| 1 | focused horizontal-form/descent/candidate rail | 1.58 s wall | 19 pass in 1.28 s |
| 1 | complete local-BV unit rail | 22.39 s wall | 134 pass in 21.99 s |
| 1 | both affected certificates under hash seeds `1,7,123`, parallel | 1.7 s wall | pass |
| 2 | two-pass paper build in isolated output directory | 2.3 s | pass; no unresolved references |

The complete local rail remains below the agreed 60-second threshold.  Tier
3 was not triggered: this is a partial local descent database, not the full
cohomology theorem, a classical freeze, a lifecycle promotion to coefficient
or QME status, or a release.

## Next local gate

Construct the Euler transgression current and solve its coupled Weyl--Diff
descent.  That will complete the antifield-independent descent status of all
four dimension-four curvature candidates.  Antifield completion remains
blocked until the classical team exports the portable Koszul--Tate rows.
