# Quantum programme bootstrap integration

Date: 2026-07-15
Classical source commit: `a3fc926cc289e5a545933a43331e395328580e0e`

## Integrated outcome

The three initial branches now have fail-closed, machine-readable starting
points:

- `LOCAL-ALGEBRAIC`: an import verifier checks 17 classical artifacts at the
  pinned commit and in the working tree.  Only 3 of 18 required export
  categories are currently portable; the other 15 remain incomplete or
  unavailable, so all six Gate-A identities are blocked and Gate A is
  `FAIL_CLOSED`.
- `LOCAL-ALGEBRAIC`: the minimal coordinate-jet algebra over exact rationals
  represents `g`, `xi`, and `omega`, verifies the declared graded operations,
  and computes `Q_0^2=0` on all 15 independent minimal generators.  It does
  not contain the imported antifield rows or the covariant/IBP/Bianchi/Hodge
  quotients and does not compute local cohomology.
- `REDUCED-MODE`: the parity-complete `E/A/L` ledger verifies exact branch
  thresholds, multiplicities, residues, Krein signs, and the rational
  character identity through an exact symbolic proof plus a finite
  regression.  Determinants, ghost/auxiliary multiplicities, a complete
  zero-mode prescription, regularization, and one-loop coefficients remain
  `NOT_COMPUTED`.

No result carries `EUCLIDEAN-SPECTRAL` or `LORENTZIAN-CAUSAL`, and nothing in
this bootstrap restores a QME or transfers a quantum correction to residual
cohomology.

## Integrated verification receipt

Run from `physics/symplectic-reconstruction/` after all three branches were
integrated:

| Tier | Rail | Elapsed | Result |
|---|---|---:|---|
| 0 | compile all `quantum-weyl` Python | 0.04 s | pass |
| 0 | parse every `quantum-weyl` JSON file | <1 s | pass |
| 0 | scoped `git diff --check` | <0.1 s | pass |
| 1 | common result-contract tests | 0.05 s | 4 pass |
| 1 | classical-import mutation tests | 0.31 s | 4 pass |
| 1 | classical-import certificate reproduction | 0.12 s | pass; Gate A still fail-closed |
| 1 | local-BV exact tests | 1.71 s | 14 pass |
| 1 | local-BV certificate reproduction | 0.46 s | pass |
| 1 | reduced-mode producer, scoped regression, and common-envelope validation | 2.34 s | pass |

Tier 2 was not triggered because no imported classical producer, shared
operator, or upstream schema changed; the imported inputs were checked by
their pinned hashes.  Tier 3 was not triggered because this is infrastructure
bootstrap work, not a freeze, paper-theorem promotion, lifecycle promotion,
shared-core change, or release.  The full classical suite was not run and is
not represented as passing.

## Next gates

1. Classical team exports portable `Q_0`, `iota_cl`, `pi_cl`, `S_cl`, cyclic
   pairing, representation matrices, normalized representatives, and H3/H5
   bases so the independent Gate-A identities can run.
2. Branch A adds covariant tensor canonicalization, integration by parts,
   curvature/Bianchi/Hodge relations, and the imported antifield filtration.
3. Branch B constructs the actual local-to-cylinder projection only after
   `pi_cl` and adjacent centered bases are frozen.
4. Branch C completes ghost/auxiliary and zero-mode bookkeeping before any
   determinant is evaluated.
