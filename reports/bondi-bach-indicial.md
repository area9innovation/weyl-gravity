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

The `p=1` branch has Einstein `1/r` Cartesian falloff and leaves the
unphysical boundary metric fixed.  The `p=0` branch has `O(1)` Cartesian
amplitude, changes the unphysical boundary metric, and is outside the wave
kernel when its leading datum is time-dependent.  Fixing the unphysical
boundary metric therefore excludes the leading `p=0` branch kinematically.

This is a `REDUCED-MODE` result.  It is not a `LORENTZIAN-CAUSAL` theorem.
The certificate explicitly leaves false all claims of a complete tensor
Bondi recursion, causal Green-operator preservation, a surface-charge
classification, exhaustive extra-channel classification, and Einstein
scattering recovery.

The downstream asymptotic bootstrap imports the new certificate by hash.
`AF-E4` and `AF-E8` move from `OPEN` to `PARTIAL`; their required closure tag
remains `LORENTZIAN-CAUSAL`.  All full asymptotic claim flags remain false.

## Provenance

The indicial calculation imports the exact geometric identity
`B_1(h_TT)=-(1/4) Box^2 h_TT` from
`bridge/certificates/flat_tt_bach_operator.json`.

| Artifact | SHA-256 |
|---|---|
| `flat_tt_bach_operator.json` | `a4aa604755c3a6adecdd747e0411d555b82d8bcdfd483c451c7bdb42ee920242` |
| `bondi_bach_indicial.json` | `635e41fdc11745fb7185d2561b35e9f0d45bf37704f4407bab98dbb180e03652` |
| `asymptotic_bootstrap.schema.json` | `cfcc9d4493007933c5c6111acf0fc7d97c1386c9c555b1aea4ae32c750253d38` |
| `asymptotically_flat_einstein_bootstrap.json` | `e1b84bc9f6d60f29ae5f54e40bed9f659bb92a553e61ebbb0ac5fcc2979acf7b` |

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile bridge/einstein_sector/bondi_bach_indicial.py bridge/einstein_sector/asymptotic_bootstrap.py bridge/einstein_sector/tests/test_bondi_bach_indicial.py bridge/einstein_sector/tests/test_asymptotic_bootstrap.py` | 0.03 s | PASS |
| 0 | `python3 -m json.tool` on both changed certificates and the bootstrap schema | 0.08 s | PASS |
| 1 | `python3 -m bridge.einstein_sector.bondi_bach_indicial --verify bridge/certificates/bondi_bach_indicial.json` | 0.42 s | PASS |
| 2 | `python3 -m bridge.einstein_sector.asymptotic_bootstrap --verify bridge/certificates/asymptotically_flat_einstein_bootstrap.json` | 0.31 s | PASS |
| 1 | `python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'` | 0.87 s | PASS (17 tests) |

Tests cover the exact roots and coefficients, the two boundary roles, the
Einstein fixed-mode intertwiner, import-scope guards, and rejection of forged
causal or scattering promotions.

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
