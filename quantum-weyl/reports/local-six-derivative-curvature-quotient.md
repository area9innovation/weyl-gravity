# Local six-derivative curvature quotient receipt

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `INVARIANT_QUOTIENT_VERIFIED`

Classical snapshot: `UNFROZEN`

## Cubic quotient

All 10,395 complete contractions of three Riemann tensors are covered through
the signed orbit ledger.  Intrinsic symmetry leaves 13 nonzero orbits.
Applying the algebraic Bianchi identity to every raw contraction and every
factor generates ten unique nonzero relation rows of exact rank five.

```text
nonzero cubic symmetry orbits       13
generated cubic Bianchi rank         5
dimension-independent cubic quotient 8
```

No conventional cubic basis was installed as input.

## Second-derivative bridge

The bridge sector exhausts all 945 complete contractions of
`(nabla nabla Riemann) Riemann`.  Intrinsic symmetry leaves 14 monomials.
Generated algebraic and outer-differentiated Bianchi relations have combined
rank eight, leaving six bridge directions before derivative commutation.

The three pre-relation sectors are therefore:

```text
Riemann^3                         13
(nabla Riemann)^2                12
Riemann nabla^2 Riemann          14
total                            39
```

## Mixed quotient

The engine generates 28 unique total-divergence/IBP relations and six unique
nonzero contracted commutator relations.  Exact cumulative row reduction is:

```text
relations through cubic Bianchi             rank  5  dimension 34
+ (nabla R)^2 Bianchi                        rank 13  dimension 26
+ R nabla^2 R Bianchi                        rank 21  dimension 18
+ integration by parts                       rank 27  dimension 12
+ covariant commutators                      rank 29  dimension 10
```

In the final integrated quotient, the cubic sector has rank eight and the
derivative sector rank four.  Their union has rank ten, so exactly two
derivative directions lie outside the cubic span.

Before total-derivative reduction, intrinsic identities and commutators leave
16 classes in the represented degree-two/degree-three sectors.  Restoring the
omitted degree-one scalar `box box R` gives 17 local order-six scalars.  The
integrated dimension ten and local dimension seventeen independently agree
with the dimension-independent FKWC ledger of D\'ecanini and Folacci,
[arXiv:0805.1595](https://arxiv.org/abs/0805.1595).  This literature comparison
is a cross-check, not a proof input.

## Collision regression

During implementation, the first mixed run incorrectly returned dimension
eight.  The cause was concrete: when forward and reversed derivative terms
canonicalized to the same monomial, a dictionary literal overwrote one
coefficient instead of adding the two coefficients.  The computation was
not certified in that state.  Coefficients are now accumulated, and a direct
constructor regression verifies both a cancelling collision and a nonzero
commutator witness.  The corrected dimension is ten.

## Claim boundary

This is a dimension-independent parity-even curvature-invariant quotient.  It
is not yet the four-dimensional pure-Weyl counterterm basis.  Still absent
are:

- four-dimensional Schouten identities;
- tracefree Weyl specialization and parity-odd epsilon contractions;
- Weyl BRST variations and ghost-number-zero/one closure;
- antifield/Koszul--Tate rows and relative descent;
- cylinder restriction, coefficients, QME restoration, and Lorentzian causal
  products.

Accordingly, `cohomology_status` remains `NOT_COMPUTED`.

The machine receipts are:

- `quantum-weyl/local_bv/certificates/LOCAL_SIX_DERIVATIVE_CURVATURE_QUOTIENT_CERTIFICATE.json`;
- `quantum-weyl/certificates/LOCAL_SIX_DERIVATIVE_CURVATURE_QUOTIENT.json`.

## Verification receipt

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | compile local package, parse quantum JSON, scoped diff check | 0.09 s | pass |
| 1 | local-BV unit tests | 22.37 s | 74 pass |
| 1 | five local certificate reproduction checks | 25.65 s | pass |
| 1 | three enforced detailed-schema checks | 1.76 s | pass |
| 1 | five common result-envelope checks | 0.06 s | pass |
| 1 | six-derivative certificate under hash seeds `1,7,123` | 44.50 s | pass |
| 2 | two-pass `conformal-residual-cohomology.tex` build | 2.00 s | pass; no unresolved warning on final pass |

Every exact Tier-1 rail remains below the 60-second escalation threshold.
Tier 2 was limited to the affected paper because the classical import and
operator certificates did not change.  Tier 3 was not triggered: this is not
a classical freeze, QME result, cohomology theorem, lifecycle promotion, or
shared-core release.  The full repository suite was not run and is not
represented as passing.

## Next local gate

Apply the explicitly four-dimensional Schouten quotient, specialize Riemann
to tracefree Weyl where appropriate, generate parity-odd epsilon sectors, and
then install the Weyl BRST curvature rows needed for the bounded
ghost-number-zero and ghost-number-one ansatz.
