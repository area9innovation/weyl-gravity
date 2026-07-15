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

Schema v2 additionally imports the flat TT Schwartz-core symplectic
restriction.  The pure-Weyl current is zero on two Einstein tangents, while
the Einstein-Hilbert Cauchy matrix has rank two.  Local finite-jet
improvements do not change the zero integral on this domain.  Thus `AF-E6`
and `AF-E7` are now `PARTIAL` with a scoped `LORENTZIAN-CAUSAL` obstruction;
the null-infinity current, corners, full scattering cohomology, nonlinear
closure, charges, flux, and extra-channel classification remain open.

## Provenance

Original source commit: `cab0e805238440d9d6e9ec39e1f3cf10624fae5e`.
Symplectic-restriction update base: `ed5ada08f4dbe0dca929fc49957770b4a8a99fd0`.

The generated certificate now also binds the flat symplectic-restriction
certificate.  Existing Einstein-sector, closed-universe, cylinder causal,
and reduced cylinder TT inputs remain content-addressed.  Their scope guards
prevent the flat or compact results from being promoted to a complete
null-infinity phase space.

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | combined affected-generator `python3 -m py_compile` | 0.04 s | PASS |
| 0 | combined affected-certificate `python3 -m json.tool` | 0.18 s | PASS |
| 1 | `python3 -m bridge.einstein_sector.flat_einstein_symplectic_restriction --verify bridge/certificates/flat_einstein_symplectic_restriction.json` | 0.48 s | PASS |
| 2 | `python3 -m bridge.einstein_sector.asymptotic_bootstrap --verify bridge/certificates/asymptotically_flat_einstein_bootstrap.json` | 0.40 s | PASS |
| 2 | `python3 -m bridge.einstein_sector.d_quotient_asymptotic_seed --verify bridge/certificates/d_quotient_asymptotic_seed.json` | 0.53 s | PASS |
| 1/2 | `python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'` | 6.92 s | PASS (47 tests) |

The affected tests additionally verify the zero-versus-rank-two symplectic
matrices, local-improvement guard, `AF-E6/E7` partial statuses, and rejection
of a forged full scattering promotion.

Tier 2 regenerated the direct asymptotic and D-quotient consumers.  Existing
cylinder and residual mathematical inputs were unchanged and checked by
hash.  Tier 3 was not run because no freeze, release, shared core algebra, or
full scattering theorem was promoted.

## Concurrent work

Unrelated medical, backgammon, and quantum local-BV changes were present in
the shared tree.  They were neither staged nor modified by this work.
