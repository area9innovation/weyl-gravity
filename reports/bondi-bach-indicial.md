# Bondi/Bach radiative indicial receipt

Date: 2026-07-15

## Established

Exact symbolic differentiation in flat retarded coordinates proves, for the
scalar amplitude of each Cartesian TT polarization,

```text
Box[r^(-s)fY]
  = 2(s-1)r^(-s-1)f'Y+[s(s-1)-L]r^(-s-2)fY,

Box^2[r^(-s)fY]
  = 4s(s-1)r^(-s-2)f''Y
    +4s(s^2-1-L)r^(-s-3)f'Y
    +[s(s-1)-L][(s+1)(s+2)-L]r^(-s-4)fY.
```

The full radial recursion in this reduced channel is recorded in
`bridge/certificates/bondi_bach_indicial.json`.  Its radiative indicial
polynomial is `4p(p-1)`, with roots `p=0,1`.

The `p=1` branch has Einstein-compatible `1/r` Cartesian falloff and leaves
the unphysical boundary metric fixed.  Its next Bach recursion is
`d_u kappa=0`, for `kappa=2 d_u f_1-Lf_0`, while Einstein requires
`kappa=0`.  Thus the same falloff contains a non-Einstein Bach datum.

The `p=0` wave recursion requires both `d_u f_0=0` and `L f_0=0`; for
nonzero `L`, every nonzero leading datum is outside the wave kernel.  Fixing
the unphysical boundary metric excludes this leading `p=0` deformation
kinematically, but does not remove the surviving `p=1` `kappa` datum.

This is a `REDUCED-MODE` result.  It is not a `LORENTZIAN-CAUSAL` theorem.
The certificate explicitly leaves false all claims that `p=1` falloff is
Einstein or that fixing the boundary metric isolates the Einstein sector.
It also leaves false all claims of a complete tensor
Bondi recursion, causal Green-operator preservation, a surface-charge
classification, exhaustive extra-channel classification, and Einstein
scattering recovery.

The missing tensor replacement is not silently approximated.  An explicit
`OPEN_FAIL_CLOSED` gate lists the required Bondi metric components, Bach
rows, radial constraints, spin-2 angular operators, residual transformations,
and the unresolved fate of `kappa`.

The downstream asymptotic bootstrap imports the new certificate by hash.
`AF-E4` and `AF-E8` remain `PARTIAL`; their receipts now explicitly include
the same-falloff `p=1` obstruction.  Their required closure tag remains
`LORENTZIAN-CAUSAL`, and all full asymptotic claim flags remain false.

## Provenance

The indicial calculation imports the exact geometric identity
`B_1(h_TT)=-(1/4) Box^2 h_TT` from
`bridge/certificates/flat_tt_bach_operator.json`.

Version 2 replaces the stale single `source_commit` field with the input base
commit, generator path and SHA-256 hash, schema path and hash, and imported
operator hash.  The downstream bootstrap uses the same provenance form.

| Artifact | SHA-256 |
|---|---|
| `flat_tt_bach_operator.json` | `a4aa604755c3a6adecdd747e0411d555b82d8bcdfd483c451c7bdb42ee920242` |
| `bondi_bach_indicial.py` | `eaea583865be13681e2965e76c808fbb732af745c3524360ffa7043f8a2aaafe` |
| `bondi_bach_indicial.schema.json` | `115d9323589607d7c1652d131c12abcf8c906a6c284f3fe3c3cf5984f9690f75` |
| `bondi_bach_indicial.json` | `0c66fcf5f86f009769c652ed5aac8bcd117f9153c1e5d1d7d64f6ea53a617eee` |
| `asymptotic_bootstrap.py` | `f6e00630627e0317c8135332640fef4023159d41ca7dda831e181d49c6e79035` |
| `asymptotic_bootstrap.schema.json` | `74dfc2531f299b4a1ee6d549e5100753bca66f2899368969ea768e93f94ef065` |
| `asymptotically_flat_einstein_bootstrap.json` | `b59e813204859c2de4757613a11a71ff85681612fe54a6f4d1e1806a1fe2b9b0` |

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile bridge/einstein_sector/bondi_bach_indicial.py bridge/einstein_sector/asymptotic_bootstrap.py bridge/einstein_sector/tests/test_bondi_bach_indicial.py bridge/einstein_sector/tests/test_asymptotic_bootstrap.py` | 0.03 s | PASS |
| 0 | `python3 -m json.tool` on both schemas and both changed certificates | 0.12 s | PASS |
| 1 | `python3 -m bridge.einstein_sector.bondi_bach_indicial --verify bridge/certificates/bondi_bach_indicial.json` | 1.34 s | PASS |
| 2 | `python3 -m bridge.einstein_sector.asymptotic_bootstrap --verify bridge/certificates/asymptotically_flat_einstein_bootstrap.json` | 0.37 s | PASS |
| 1 | `python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'` | 5.37 s | PASS (24 tests) |

Tests cover direct wave and biwave differentiation, finite-series recurrence
extraction, the exact roots and coefficients, the `p=1` obstruction, the
stronger `p=0` wave-kernel statement, both boundary roles, generator/schema
provenance, the Einstein fixed-mode intertwiner, import-scope guards, and
rejection of forged Einstein-selection, causal, or scattering promotions.

Tier 2 was limited to the direct downstream asymptotic certificate.  The
content-addressed flat TT premise was unchanged, so its upstream algebra was
not rebuilt.  Tier 3 was not run because this change does not freeze or
release the programme, alter shared core algebra, or promote a paper theorem
or `LORENTZIAN-CAUSAL` lifecycle state.

## Unresolved fields

- full tensor Bondi-gauge and ghost recursion;
- exceptional angular harmonics and TT constraint coupling;
- soft, memory, and Coulombic boundary sectors;
- renormalized presymplectic flux and pure-Weyl surface charges;
- preservation of the selected boundary class by retarded/advanced maps;
- nonlinear Einstein-sector closure and scattering equivalence.

## Concurrent work

Unrelated medical, backgammon, quantum local-BV, transfer, paper, and workflow
changes were present in the shared tree.  They were neither staged nor
modified by this work.
