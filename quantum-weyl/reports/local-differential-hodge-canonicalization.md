# Differential curvature and Hodge receipt

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `INFRASTRUCTURE_VERIFIED`

Classical snapshot: `UNFROZEN`

## Exact finite quotient

The local-BV package now generates every complete contraction of two
once-differentiated Riemann tensors.  No preferred invariant basis is
installed.  Exact canonicalization and rational row reduction give:

```text
raw perfect matchings                         945
canonical monomials after intrinsic symmetry  12
unique algebraic-Bianchi relations              6
algebraic-Bianchi rank                           3
unique differential-Bianchi relations          16
differential-Bianchi rank                         8
combined relation rank                            8
finite quotient dimension                         4
```

The certificate stores all 12 generated basis monomials, the exact RREF,
pivot columns `(0,1,2,3,4,8,9,10)`, free columns `(5,6,7,11)`, and canonical
hashes for both relation sets.  Memoizing immutable monomial orbits keeps the
exhaustive exact test under ten seconds on the current workspace.

## Commutator and Hodge conventions

The covariant-derivative convention is executable and fixed as

```text
[nabla_a,nabla_b] T_{c1...cr}
  = -sum_i R^d{}_{ci ab} T_{c1...d...cr}.
```

Scalar, covector, and rank-two covariant witnesses verify respectively two,
three, and four relation terms, rank-one exact quotients, and antisymmetry
under exchange of the derivative indices.  Acting on tensors that already
carry derivative indices is intentionally rejected until the higher-rank
curvature action is implemented.

On the formal two-form basis `(F,*F)`, exact matrices verify:

- Euclidean `star^2=+1` with eigenvalues `+1,-1`;
- Lorentzian `star^2=-1` with eigenvalues `+i,-i`;
- complementary orthogonal idempotent chiral projectors;
- parity squared equal to one, parity reversal of `star`, and exchange of the
  two chiral projectors;
- `epsilon_abcd epsilon^{cdef}=2 sigma delta_ab^{ef}` with `sigma=+1`
  Euclidean and `sigma=-1` Lorentzian.

## Claim boundary

The four-dimensional quotient above is only the finite
`(nabla Riemann)^2` sector modulo intrinsic and Bianchi relations.  Integration
by parts and derivative commutators mix it with cubic curvature, so the number
four is not a dimension claim for the complete six-derivative scalar
invariant space.  Also not computed are dimension-dependent Schouten
relations, the tracefree Weyl-tensor Hodge quotient, Weyl BRST curvature rows,
the derivative-bounded ghost ansatz, antifield/Koszul--Tate rows,
`H^{g,4}(s|d)`, descent, cylinder restriction, coefficients, QME restoration,
or Lorentzian causal products.

The machine receipts are:

- `quantum-weyl/local_bv/certificates/LOCAL_DIFFERENTIAL_HODGE_CANONICALIZATION_CERTIFICATE.json`;
- `quantum-weyl/certificates/LOCAL_DIFFERENTIAL_HODGE_CANONICALIZATION.json`.

## Verification receipt

Run from the standalone `weyl-gravity` repository root:

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | compile `quantum-weyl/local_bv` | 0.03 s | pass |
| 0 | parse scoped JSON and `git diff --check` | 0.05 s | pass |
| 1 | local-BV unit tests | 5.38 s | 45 pass |
| 1 | minimal, curvature, and differential/Hodge certificate reproduction | 5.14 s | pass |
| 1 | differential/Hodge certificate under hash seeds `1,7,123` | 11.91 s | pass |
| 1 | common result-envelope validation | 0.03 s | pass |

Tier 2 is not triggered unless a pinned classical dependency or consumed
schema changes.  Tier 3 is not triggered because this result remains scoped
infrastructure: it does not freeze classical data, promote a theorem or
lifecycle state, alter a shared core, or claim a QME result.  The full
repository suite is not run and must not be represented as passing.

## Next local gate

Build the complete six-derivative invariant space containing both
`(nabla Riemann)^2` and `Riemann^3`, then quotient their integration-by-parts
and derivative-commutator mixing.  In parallel, add Weyl BRST transformations
for curvature and generate the bounded ghost-number-zero/one ansatz.  The
antifield completion remains gated by the frozen classical export.
