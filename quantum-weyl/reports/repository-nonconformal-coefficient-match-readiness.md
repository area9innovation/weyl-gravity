# Repository nonconformal coefficient-match readiness

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The remaining (C^2) coefficient gate now has an executable input contract.
An accepted carrier must simultaneously provide:

- a four-dimensional Euclidean background with nonzero local `C2` density;
- the repository gauge-fixed elliptic BV complex;
- complete determinant multiplicities and local measure;
- a declared local `b4` regulator and zero-mode policy;
- exact factor-by-factor coordinates in `(C2,E4,CdualC,BoxR)`;
- parity and round-`S4` cross-check proofs;
- the physical classical-snapshot compatibility bridge.

The receiver recomputes exact rational factor sums, recursively validates the
full-BV multiplicity export and snapshot bridge, and rejects formulation,
visibility, arithmetic, and digest mutations.

## Current candidate audit

- Unit Nariai is `C2`-visible and has an action-paired classical metric Bach
  complex, but it is Lorentzian and has no Euclidean elliptic determinant,
  BV measure/regulator ledger, or coefficient vector.
- The positive Berger clock is a coupled `REDUCED-MODE` classical background,
  not a pure-Weyl Euclidean full-BV coefficient carrier.
- The standard `(199/30,-87/20,0)` vector is not itself a repository match.
- Round `S4` has the accepted repository determinant ledger but `C2=0`.

Thus no current artifact lies in the required intersection. In particular,
the new Nariai causal Green results cannot be promoted into an
`EUCLIDEAN-SPECTRAL` coefficient theorem.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.nonconformal_coefficient_match_readiness --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_nonconformal_coefficient_match_readiness
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_nonconformal_coefficient_match_readiness
```
