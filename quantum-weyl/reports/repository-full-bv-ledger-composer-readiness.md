# Repository full-BV ledger composer readiness

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The non-TT part of the round-(S^4) multiplicity problem is now completely
bound. The composer imports the exact rank-two-to-rank-one Diff-Weyl scalar
ghost reduction, York/Hodge measure, nonminimal quartet Berezinian, standard
factor exponents, and zero-mode dimensions

\[
(0,5,0,10)
\]

for

\[
\Delta_2^\perp(4),\quad
\Delta_0(-4),\quad
\Delta_2^\perp(2),\quad
\Delta_1^\perp(-3).
\]

Given one content-addressed physical
`REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1`, it produces and independently
replays a `REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER`. The resulting local
partition-function exponents are

\[
-\frac12,\quad +\frac12,\quad -\frac12,\quad +\frac12,
\]

with bundle ranks `(5,1,5,3)`. Exact row/factor coverage, the coupled scalar
source map, physical factor ordering, determinant exponents, and priming
policies are enforced. Mutations of the upper TT operator, scalar source,
vector zero-mode policy, and factor map all fail.

The `xi_L` and `omega` carrier rows are not separately diagonal determinant
factors: each therefore has individual row exponent zero. Their coupled
rank-two FP matrix is reduced once, and only its rank-one quotient factor
`Delta_0(-4)` carries exponent `+1/2`. This convention prevents silently
counting the scalar determinant twice.

The committed run uses a visibly synthetic TT dictionary while retaining the
real non-TT certificates. It proves composer mechanics only. The physical TT
input remains absent, so neither the repository multiplicity ledger nor the
repository anomaly coefficient is promoted.

This local multiplicity result will not fix the global determinant phase or
finite conformal-group volume. It also supplies no regulated Slavnov breaking,
QME disposition, residual transfer, or Lorentzian quantum theorem.

When the physical input lands, the executable path is:

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.full_bv_ledger_composer \
  --tt-input path/to/REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1.json \
  --emit path/to/REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER.json
```

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.full_bv_ledger_composer_readiness --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_full_bv_ledger_composer_readiness
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_full_bv_ledger_composer -v
```
