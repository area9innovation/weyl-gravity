# Local specialization foundations receipt

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `SPECIALIZATION_INFRASTRUCTURE_VERIFIED`

Classical snapshot: `UNFROZEN`

## Outcome

The dimension-independent six-derivative curvature quotient can now be
specialized without mutating or silently replacing its universal relations.
An immutable tower retains one ambient monomial basis and appends named
relation families stage by stage.  Each stage records:

- exact source and target dimensions;
- the induced surjective projection matrix;
- an exact basis of its kernel;
- relation-family provenance and assumptions;
- even and odd parity-block dimensions;
- deterministic coordinates and hashes for named representatives.

The real universal import covers the existing 39-column order-six system,
imports all five generated relation families, and independently reproduces
its ten-dimensional integrated quotient.  A clearly marked, non-geometric
controlled tower verifies dimensions `4 -> 3 -> 2` with one exact kernel
witness at each projection.

## Four-dimensional primitives

The foundation adds occurrence-level antisymmetrization.  Its dimension-
checked Schouten wrapper requires exactly `dimension + 1` occurrences.  The
four-dimensional witness generates all `5! = 120` signed permutations and
changes sign under an input transposition.  This is the generator needed for
the next calculation; no resulting Schouten relation has yet been applied to
the curvature basis.

Weyl is represented by a distinct tensor specification with Riemann slot
symmetries and an explicit tracefree reducer.  A traced Riemann witness maps
to zero after Weyl specialization, while an untraced witness remains nonzero.
Thus the next phase cannot implement Weyl specialization as a mere tensor
rename.

## Epsilon elimination

Two epsilon tensors reduce through the full 24-term generalized-delta
matching ledger.  The reducer identifies external index components, counts
closed delta loops exactly, and keeps Euclidean and Lorentzian signs separate.
The complete contraction verifies

```text
epsilon_abcd epsilon^abcd = +24  Euclidean
epsilon_abcd epsilon^abcd = -24  Lorentzian
```

This extends the earlier two-form Hodge convention to a reusable tensor-level
epsilon-pair eliminator.

## Claim boundary

This certificate verifies infrastructure, not the four-dimensional invariant
basis.  In particular, it does not claim:

- generated Schouten relations on the order-six curvature basis;
- the rank or dimension of the resulting four-dimensional quotient;
- the parity-odd Weyl invariant catalogue;
- Weyl-BRST closure, antifield descent, or `H^{g,4}(s|d)`.

The controlled projection relations in the receipt are labelled
`INFRASTRUCTURE_ONLY_NOT_GEOMETRIC_INPUT` and never enter the universal or
future geometric quotient.

## Verification receipt

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | compile local package, parse quantum JSON, scoped diff check, detailed and common schemas | 0.50 s | pass |
| 1 | complete local-BV unit suite | 19.14 s | 85 pass |
| 1 | specialization certificate reproduction | 12.13 s | pass |
| 1 | specialization certificate under hash seeds `1,7,123` | 11.87 s concurrent | pass |
| 2 | two-pass `07-08-conformal-residual-cohomology-archive.tex` build | 1.39 s | pass; no unresolved references on final pass |

The affected pre-existing local receipts were regenerated because the exact
quotient source manifest changed; their reproducibility tests are included in
the 85-test rail.  Every exact Tier-1 rail remains below the 60-second
escalation threshold.  Tier 3 was not triggered: this is infrastructure, not
a classical freeze, local-cohomology theorem, QME result, lifecycle promotion,
or shared-core release.  The full repository suite was not run and is not
represented as passing.

## Machine receipts

- `quantum-weyl/local_bv/certificates/LOCAL_SPECIALIZATION_FOUNDATIONS_CERTIFICATE.json`;
- `quantum-weyl/certificates/LOCAL_SPECIALIZATION_FOUNDATIONS.json`.

## Next local gate

Generate every nonzero five-index antisymmetrization induced on the universal
order-six basis, store it as a provenance-bearing `dimension_4_schouten`
relation family, and inspect the exact projection kernel before performing
the tracefree-Weyl and parity-odd specializations.

This gate is now completed by
`reports/local-four-dimensional-schouten-quotient.md`; the foundation receipt
remains the fail-closed record of the preceding infrastructure milestone.
