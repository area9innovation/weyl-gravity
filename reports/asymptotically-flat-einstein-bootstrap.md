# Asymptotically flat Einstein bootstrap receipt

Date: 2026-07-15

## Established

The bootstrap proves, by exact symbolic matrix identities, that the
linearized Einstein two-jet constraint is invariant under fixed nonzero TT
Fourier-mode Bach evolution on four-dimensional Minkowski space:

```text
C_E A_B = A_E C_E,
A_B i_E = i_E A_E.
```

The Bach Cauchy space has dimension four per helicity and its Einstein kernel
has dimension two.  This is a `REDUCED-MODE` theorem.  It does not claim a
null-infinity support theorem.

The bootstrap also records a smooth conformal-completion/Bondi seed and the
Wald--Zoupas charge criterion distinguishing proper gauge transformations
from charged asymptotic symmetries.  These are explicit specifications with
open admissibility and charge calculations, not promoted theorems.

Obligations `AF-E1`, `AF-E3`, and `AF-E5` move to `PARTIAL`.  `AF-E2`,
`AF-E4`, `AF-E6`, `AF-E7`, and `AF-E8` remain `OPEN`.  Every full scattering,
nonlinear, charge, flux, and extra-channel claim flag remains false.

## Provenance

Source commit: `cab0e805238440d9d6e9ec39e1f3cf10624fae5e`.

The generated certificate binds SHA-256 hashes of the existing
Einstein-sector theorem, closed-universe BFV choice, cylinder causal
transport, and reduced cylinder TT factorization.  Those inputs were
unchanged.  Their scope guards are imported to prove that compact-cylinder
causal transport cannot be silently reused at null infinity.

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile bridge/einstein_sector/asymptotic_bootstrap.py bridge/einstein_sector/tests/test_asymptotic_bootstrap.py` | 0.02 s | PASS |
| 0 | `python3 -m json.tool bridge/certificates/asymptotically_flat_einstein_bootstrap.json` | 0.02 s | PASS |
| 1 | `python3 -m bridge.einstein_sector.asymptotic_bootstrap --verify bridge/certificates/asymptotically_flat_einstein_bootstrap.json` | 0.29 s | PASS |
| 1 | `python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'` | 0.37 s | PASS (8 tests) |

The new tests verify the exact zero intertwining defect, the `4 -> 2` data
restriction, rejection of a forged cylinder compactness premise, and
rejection of a false scattering promotion.

Tier 2 did not require regeneration of the existing cylinder or residual
chains: their content-addressed mathematical inputs did not change, and the
new certificate has no existing downstream consumer.  Tier 3 was not run
because no paper theorem, lifecycle state, shared core algebra, freeze, tag,
or release was modified.

## Concurrent work

Unrelated medical, backgammon, and quantum local-BV changes were present in
the shared tree.  They were neither staged nor modified by this work.
