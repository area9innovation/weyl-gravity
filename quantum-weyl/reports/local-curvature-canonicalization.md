# Local curvature canonicalization receipt

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `INFRASTRUCTURE_VERIFIED`

Classical snapshot: `UNFROZEN`

## Result

The local-BV package now contains an exact abstract-index layer over rational
coefficients.  Its canonical orbit includes:

- signed intrinsic tensor symmetries;
- graded factor permutations;
- dummy-index renaming while preserving free-index order;
- exact rational quotients by generated linear relations;
- covariant total derivatives and integration by parts;
- an explicit spacetime-parity involution.

For the parity-even scalar sector quadratic in the Riemann tensor and without
covariant derivatives, the program generates every perfect matching of the
eight tensor slots.  It does not install a preferred curvature basis.

```text
raw perfect matchings                  105
canonical monomials after symmetries     4
unique nonzero Bianchi relations          2
exact Bianchi relation rank                1
quotient dimension                         3
rank of conventional cross-check classes   3
```

In the generated four-element canonical basis `B0,B1,B2,B3`, exact row
reduction gives

```text
B2 - 2 B3 = 0.
```

The free columns are `(B0,B1,B3)`.  The conventional representatives have
coordinates

```text
R^2       = (1,0,0)
Ricci^2   = (0,1,0)
Riemann^2 = (0,0,2),
```

so they independently span the generated quotient.  The detailed certificate
stores the canonical basis, exact rational RREF, pivot/free columns and these
coordinate witnesses rather than only the dimension count.

## Total derivatives and parity

For two formal even scalars the covariant Leibniz rail generates

```text
nabla_a (A nabla^a B)
  = (nabla_a A)(nabla^a B) + A nabla_a nabla^a B.
```

Treating this divergence as a relation has exact rank one and leaves a
one-dimensional two-term quotient; the divergence reduces to zero.  This is
the first IBP rail, not a claim that every derivative monomial is already in a
global normal form.

The orientation tensor has the full signed antisymmetry group of order 24 and
parity eigenvalue `-1`; Riemann has its signed symmetry group of order 8 and
parity eigenvalue `+1`.  Applying parity twice is the identity.  Hodge-star
normalization and chiral projectors are not part of this certificate.

## Claim boundary

The common result envelope remains `cohomology_status: NOT_COMPUTED`.  This
work does not classify `H^{0,4}(s|d)` or `H^{1,4}(s|d)`.  It does not yet
implement:

- differential Bianchi identities or covariant-derivative commutators;
- dimension-dependent Schouten relations outside the generated sector;
- Hodge/chiral normalization;
- Weyl-BRST curvature transformations;
- a general derivative-bounded invariant ansatz;
- antifield/Koszul--Tate rows or descent;
- cylinder restriction, coefficients, QME restoration or Lorentzian causal
  products.

The machine receipts are:

- `quantum-weyl/local_bv/certificates/LOCAL_CURVATURE_CANONICALIZATION_CERTIFICATE.json`;
- `quantum-weyl/certificates/LOCAL_CURVATURE_CANONICALIZATION.json`.

## Verification receipt

Run from `physics/symplectic-reconstruction/`:

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | compile `quantum-weyl/local_bv` | 0.03 s | pass |
| 0 | parse scoped JSON and `git diff --check` | <0.2 s | pass |
| 1 | local-BV unit tests | 2.13 s | 30 pass |
| 1 | original minimal-BRST certificate reproduction | 0.37 s | pass |
| 1 | curvature canonicalization certificate reproduction | 0.57 s | pass |
| 1 | certificate check under hash seeds `1,7,123` | 1.9 s | pass |
| 1 | common result-envelope validation | 0.02 s | pass |

Tier 2 was not triggered: no pinned classical input, shared classical
operator, or upstream schema changed.  Tier 3 was not triggered: this is a
scoped infrastructure result, not a classical/quantum freeze, paper theorem,
lifecycle promotion, shared-core release or QME claim.  The full repository
suite was not run and is not represented as passing.

## Next local gate

The next productive layer is the covariant derivative algebra: differential
Bianchi identities, commutator curvature terms and Hodge/chiral normalization.
That will make it possible to generate the complete derivative-bounded
antifield-independent curvature ansatz while the classical contraction remains
unfrozen.
