# Flat Einstein symplectic-restriction receipt

Date: 2026-07-15

## Established

For the reduced flat TT pure-Weyl action, the action-derived current is
linear in `chi=Box h` and its first derivative.  Its restriction to two
Einstein wave tangents vanishes pointwise.  An explicit TT Schwartz
Cauchy-data pair has nonzero Einstein-Hilbert pairing.

The restricted pure-Weyl and Einstein-Hilbert Cauchy matrices have ranks
zero and two respectively, so no nonzero normalization identifies them.
Local finite-jet improvements integrate to zero on the Schwartz domain.
With vacuum normalization, the restricted pure-Weyl `P_0` charge is also
zero, whereas the Einstein-Hilbert wave Hamiltonian is nonzero.

Verdict:

```text
REDUCED_FLAT_EINSTEIN_SYMPLECTIC_EMBEDDING_REFUTED
```

Dependency tags: `REDUCED-MODE`, `LORENTZIAN-CAUSAL`.

## Claim boundary

This receipt does not claim a full metric BV theorem, null-infinity current,
classification of all boundary counterterms, or a complete Einstein
scattering no-go.  It leaves open compensators, symmetry breaking,
nonlocal/corner extensions, soft data, and curved boundary-selected sectors.

## Provenance

Input base commit: `ed5ada08f4dbe0dca929fc49957770b4a8a99fd0`.

| Artifact | SHA-256 |
|---|---|
| `flat_einstein_symplectic_restriction.py` | `2bd50de076fc55597b8efedec0088126b1dc1c831570fd3c87e41d43e0e83008` |
| `flat_einstein_symplectic_restriction.schema.json` | `8147a963aea6372bdb8134176fcb750b43778b8f3b44be36e87bad48fd304ed1` |
| `flat_einstein_symplectic_restriction.json` | `8e3e690b5a1f62d79cdd587c2fa35c9f958604c01ce4f2a08749c367d5ab8f6d` |
| `test_flat_einstein_symplectic_restriction.py` | `1f5d0e51798f1030c7214a2e7fa4b90afe62ef7f0fbf6d290d053758611ead3b` |
| `conformal-flat-einstein-symplectic-restriction.md` | `fc9935b41cbcc5be48ff9960f2a1ded0fa99f8d868df5015c0206ae1a0a65565` |
| `asymptotically_flat_einstein_bootstrap.json` | `eedea768772c69bf33b4e2436492f2843d5aadaeabb0485b1ec8d472665a2468` |
| `d_quotient_asymptotic_seed.json` | `359914fbb0122ee49e8351b5b87d62c536adbfeb4d754a3deebf87ac3ecb6663` |

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile` on the three affected generators and tests | 0.04 s | PASS |
| 0 | `python3 -m json.tool` on the three affected schemas/certificates | 0.18 s | PASS |
| 1 | `python3 -m bridge.einstein_sector.flat_einstein_symplectic_restriction --verify bridge/certificates/flat_einstein_symplectic_restriction.json` | 0.48 s | PASS |
| 2 | `python3 -m bridge.einstein_sector.asymptotic_bootstrap --verify bridge/certificates/asymptotically_flat_einstein_bootstrap.json` | 0.40 s | PASS |
| 2 | `python3 -m bridge.einstein_sector.d_quotient_asymptotic_seed --verify bridge/certificates/d_quotient_asymptotic_seed.json` | 0.53 s | PASS |
| 1/2 | `python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'` | 6.92 s | PASS (47 tests) |

Tier 2 followed the direct certificate chain through bootstrap schema v2 and
the D-quotient seed's content hash.  Tier 3 was not run because no freeze,
release, shared core algebra, or full scattering theorem was promoted.

## Concurrent work

Unrelated medical, quantum-transfer, and backgammon changes were present in
the shared tree.  They were neither modified nor staged by this work.
