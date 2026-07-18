# Repository round-S4 full-BV multiplicity ledger

Status: `PHYSICAL_FULL_BV_LEDGER_INDEPENDENTLY_ACCEPTED`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

The accepted physical TT dictionary has been composed with the already exact
York/Hodge measure, coupled scalar Diff--Weyl ghost reduction, nonminimal
quartet cancellation, and round-\(S^4\) zero-mode ledger.

| factor | operator | rank | exponent in \(Z\) | kernel treatment |
|---|---|---:|---:|---|
| physical depth 0 | \(\Delta_2^\perp(4)\) | 5 | \(-1/2\) | no zero modes |
| scalar ghost | \(\Delta_0(-4)\) | 1 | \(+1/2\) | delete five proper-conformal modes |
| physical depth 1 | \(\Delta_2^\perp(2)\) | 5 | \(-1/2\) | no zero modes |
| vector ghost | \(\Delta_1^\perp(-3)\) | 3 | \(+1/2\) | delete ten Killing modes |

All four integration rows and all four repository factors are covered. The
two scalar ghosts \((\xi_L,\omega)\) reduce to the single rank-one scalar
factor. The target signed rank is six, the exponent-weighted repository rank
is \(-3\), and the fifteen primed modes agree with the conformal-Killing
reducibility ledger.

The committed ledger is checked by both the exact composer and a separate
verifier that does not import the composer's factor dictionary.

This is a Euclidean spectral multiplicity result. It fixes local heat-kernel
ranks, exponents, and priming, but not the global conformal-group volume,
global determinant phase, regulated Slavnov breaking, QME, residual quantum
transfer, or Lorentzian quantum theory.
