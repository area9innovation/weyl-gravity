# Local four-dimensional Schouten quotient receipt

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `DIMENSIONAL_QUOTIENT_VERIFIED`

Classical snapshot: `UNFROZEN`

## Exhaustive generation

The dimension-independent 39-column order-six curvature system is retained as
the ambient basis.  For each signed-symmetry orbit representative, the engine
chooses five distinct contraction pairs, chooses one endpoint from each pair,
and antisymmetrizes those five positions over all `5!` permutations.  The
orbit-first rewiring is checked directly against the tensor occurrence-level
antisymmetrizer in all three sectors.

```text
sector                         candidates  nonzero  unique rows
Riemann^3                           2496     2160           36
(nabla Riemann)^2                    384      384           18
Riemann nabla^2 Riemann              448      448           18
total                               3328     2992           72
```

The 72 generated rows have exact rank 11 in the unreduced 39-column ambient
space.  Nine directions already lie in the universal Bianchi, integration-
by-parts, and commutator relation span.  The induced Schouten rank on the
ten-dimensional universal integrated quotient is therefore two.

## Exact specialization

```text
dimension-independent integrated quotient    10
new four-dimensional Schouten rank             2
four-dimensional integrated quotient           8
```

The cubic sector drops from rank eight to rank six.  The derivative sector
gains no additional dimension-dependent loss:

```text
sector                    before 4D  after 4D
Riemann^3                          8         6
(nabla Riemann)^2                 4         4
Riemann nabla^2 Riemann           6         6
```

The exact specialization projection is surjective and its two-dimensional
kernel is stored both in source quotient coordinates and as two explicit
ambient tensor expressions.

## Independent cross-check

Table 1 of Martín-García, Yllanes, and Portugal's Invar paper,
[arXiv:0802.1274](https://arxiv.org/abs/0802.1274), reports that the
nonproduct cubic case `{0,0,0}` drops from five invariants after derivative
commutation to three after four-dimensional identities, while cases `{1,1}`
and `{0,2}` do not lose additional directions.  Restoring the three product
classes gives the independently matching cubic count `8 -> 6`.  This
literature comparison is a cross-check and was not used to construct the
relations.

## Claim boundary

This is the four-dimensional parity-even Riemann-invariant quotient.  It is
not yet the strict pure-Weyl counterterm basis.  Still uncomputed are:

- the tracefree-Weyl image and its kernel;
- the parity-odd single-epsilon invariant sector;
- Weyl-BRST closure and exactness;
- antifield/Koszul--Tate completion and relative descent;
- local anomaly coefficients, QME restoration, and residual transfer.

Consequently `cohomology_status` remains `NOT_COMPUTED`.  The result does not
advance Gate A: the classical team's latest rank-14 endpoint work sharpens an
analytic obstruction boundary but has not yet exported the portable
`Q0`, `iota_cl`, `pi_cl`, `S_cl`, residual matrices, or centered H3/H5 bases
needed for the classical freeze.

## Verification receipt

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | compile local package, parse quantum JSON, scoped diff check, detailed and common schemas | 0.34 s | pass |
| 1 | complete local-BV unit suite, quiet mode | 36.89 s | 93 pass |
| 1 | four-dimensional certificate reproduction | 12.03 s | pass |
| 1 | four-dimensional certificate under hash seeds `1,7,123` | 13.51 s concurrent | pass |
| 2 | two-pass `conformal-residual-cohomology.tex` build | 1.29 s | pass; no unresolved references on final pass |

The full local suite remains below the agreed 60-second escalation threshold,
so it does not yet require subdivision.  The affected pre-existing local
receipts were regenerated after the package export changed, and their
reproducibility tests are included in the 93-test rail.  Tier 3 was not
triggered: this is an invariant-quotient theorem, not a classical freeze,
local BRST-cohomology theorem, QME result, lifecycle promotion, or shared-core
release.  The full repository suite was not run and is not represented as
passing.

## Machine receipts

- `quantum-weyl/local_bv/certificates/LOCAL_FOUR_DIMENSIONAL_SCHOUTEN_QUOTIENT_CERTIFICATE.json`;
- `quantum-weyl/certificates/LOCAL_FOUR_DIMENSIONAL_SCHOUTEN_QUOTIENT.json`.

## Next local gate

Construct the tracefree-Weyl image of the eight-dimensional quotient as an
explicit exact linear map, then enumerate the parity-odd single-epsilon
sector and reduce products of two epsilon tensors back to the even sector.
