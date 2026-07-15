# Compensated Einstein local-projector receipt

Date: 2026-07-15

## Established

For `Box(Box+M2)h=0` with `M2!=0`, the reduced TT operators

```text
Pi_E = 1 + Box/M2,
Pi_M = -Box/M2
```

are complementary on-shell projectors.  Their exact polynomial and Cauchy
realizations satisfy completeness, idempotence, orthogonality, and commutation
with the fourth-order evolution.

They reproduce the certified symplectic block decomposition:

```text
P_E^T Omega P_M = 0,
I_E^T Omega I_E =  (c1/2) J_2,
I_M^T Omega I_M = -(c1/2) J_2.
```

Both are second-order differential operators, hence support-nonincreasing on
smooth or distributional TT fields.  They contain no inverse spatial momentum
and are regular at `q=0` for nonzero `M2`.  The earlier `k=0` exclusion belongs
to the helicity frame, not the branch algebra.  The projectors become singular
in the pure-Weyl limit `M2->0`.

For a generic source, the certificate derives

```text
Box(Pi_E h) = J/M2,
(Box+M2)(Pi_M h) = -J/M2.
```

Thus a generic source excites both branches and does not preserve the vacuum
Einstein-only sector.

Verdict:

```text
LOCAL_ON_SHELL_EINSTEIN_MASSIVE_PROJECTORS_CERTIFIED_TT_SCOPE
```

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`.

## Claim boundary

The projectors are local only after TT reduction.  The theorem does not prove
that constructing a TT representative from an unreduced metric is local.  It
does not construct a source-compatible Einstein-defect complex, reduced
retarded Green split, full metric Diff x Weyl BV projector, nonlinear or
null-infinity projector, scattering equivalence, or quantum theory.

## Provenance

Input base commit: `4eecb219843281d0375b835d37e5b25e7b067039`.

| Artifact | SHA-256 |
|---|---|
| `compensated_einstein_local_projectors.py` | `0a18a853398568149e3e8d437cc9f95fa7892c45157d6ef0373a98ba871c228b` |
| `compensated_einstein_local_projectors.schema.json` | `452afa4a63dcbb6ad9cfd87ccfbbb774ad565a86ee25edb2136e4691f9e7cbef` |
| `compensated_einstein_local_projectors.json` | `0a895b5f4f3f5ed3d29c8474a4174bdc9f486579b7a57cc3accc8303c602818a` |
| `test_compensated_einstein_local_projectors.py` | `8af4ef2974148a7aee568d2ad8d69ee4224fbd3a2f8918a247eb2dc23a0b0a22` |
| `conformal-compensated-einstein-local-projectors.md` | `7ef27bef6e9a9cfccacb4c62a2b8e553676b56bc65b5038c1d531d4e32b92c8b` |
| imported `compensated_einstein_causal_subsector.json` | `ec91bb684fc0b306517de5d1bcd9763a5b69b1520fe3bd4a6b61de7e697b73b9` |

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile` on generator and test | under 0.1 s | PASS |
| 0 | `python3 -m json.tool` on schema and certificate | under 0.1 s | PASS |
| 1 | `python3 -m bridge.einstein_sector.compensated_einstein_local_projectors --verify bridge/certificates/compensated_einstein_local_projectors.json` | 0.63 s | PASS |
| 1/2 | `python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'` | 10.87 s | PASS (74 tests) |
| 2 | `python3 -m bridge.einstein_sector.compensated_einstein_causal_subsector --verify bridge/certificates/compensated_einstein_causal_subsector.json` | 0.40 s | PASS |
| coordination | `python3 d_quotient_programme/verify_programme_status.py --check --guards` | 0.12 s | FAIL: concurrent programme inputs do not yet match exact regeneration |

The coordination failure is not counted as a pass and supports no claim.  It
belongs to concurrent D/quantum-team work and none of those files are staged
with this theorem.

Tier 3 was not run because this is not a freeze, release, shared-core algebra,
full BV, scattering, or quantum theorem promotion.
