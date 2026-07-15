# Compensated Einstein causal-subsector receipt

Date: 2026-07-15

## Established

For the source-free flat TT constant-compensator phase,

```text
D_q(D_q+M2)h=0,
chi=D_q h,
(D_q+M2)chi=0.
```

The two local Cauchy constraints

```text
chi|Sigma=0,
n.chi|Sigma=0
```

have rank two, intertwine the fourth-order evolution, and cut out exactly the
ordinary massless Einstein wave Cauchy data.  Massive Klein--Gordon uniqueness
propagates the zero defect on the full domain of dependence.  No future
boundary condition is required.

The action-derived Einstein--Weyl current restricts to

```text
omega|E=(c1/2) omega_EH.
```

Its Cauchy matrix has rank two.  The massive branch is symplectically
orthogonal and has the opposite matrix.  For the healthy repository sign
`c1=-1`, the selected `P_0` Hamiltonian is positive and equals the
Einstein-Hilbert wave energy.  The result applies to both TT helicities.

Verdict:

```text
LINEAR_FLAT_TT_EINSTEIN_SECTOR_CAUSALLY_CLOSED_AND_SYMPLECTIC
```

Dependency tags: `REDUCED-MODE`, `LORENTZIAN-CAUSAL`.

## Interpretation

The compensated theory contains an honest classical free helicity-`+/-2`
Einstein Cauchy phase space.  The graviton is the massless simple root with
nonzero `c1` normalization.  In pure Weyl gravity `c1->0`, that restricted
normalization vanishes as the two roots coalesce.

The theorem selects a source-free solution subspace.  It does not remove the
massive branch from the full Einstein--Weyl theory.  Generic sources satisfy
`(D_q+M2)chi=J` and may excite the defect.

## Claim boundary

This receipt does not claim a full tensor Diff x Weyl BV--BFV complex,
source-compatible projected Green operator, null-infinity phase space, Bondi
charge/flux comparison, nonlinear constraint propagation, Einstein scattering
equivalence, one-particle quantum Hilbert space, or unitarity.

## Provenance

Input base commit: `0c200a2805f1085f44e466987dc126001035585b`.

| Artifact | SHA-256 |
|---|---|
| `compensated_einstein_causal_subsector.py` | `dea4089dded7078b9ddc178d11a3af9e17b1575ae5d138043329dbfe1424b4ad` |
| `compensated_einstein_causal_subsector.schema.json` | `c4e4c28bf648baac86b25bbaf456fe4cc6e6b2bd80b8819a13b5830cfff0a773` |
| `compensated_einstein_causal_subsector.json` | `ec91bb684fc0b306517de5d1bcd9763a5b69b1520fe3bd4a6b61de7e697b73b9` |
| `test_compensated_einstein_causal_subsector.py` | `80d4b4eafe6f9f487fa66aa6d7aea10c1b6441fb5f05e981224451843136fecb` |
| `conformal-compensated-einstein-causal-subsector.md` | `e38c26277365a0bf1084ca3dc55275ce08c2f15f6f337e0ac50cdebbd73f88cb` |
| imported `compensator_einstein_phase.json` | `b5c9f6caa05a263cdb006c33e6bbf60139139d8c30303706e073948a62e7a6b4` |
| imported `flat_einstein_symplectic_restriction.json` | `8e3e690b5a1f62d79cdd587c2fa35c9f958604c01ce4f2a08749c367d5ab8f6d` |

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile` on the generator and test | under 0.1 s | PASS |
| 0 | `python3 -m json.tool` on the schema and certificate | under 0.1 s | PASS |
| 1 | `python3 -m bridge.einstein_sector.compensated_einstein_causal_subsector --verify bridge/certificates/compensated_einstein_causal_subsector.json` | 0.43 s | PASS |
| 1/2 | `python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'` | 8.12 s | PASS (64 tests) |
| 2 | `python3 -m bridge.einstein_sector.compensator_einstein_phase --verify bridge/certificates/compensator_einstein_phase.json` | 0.43 s | PASS |
| 2 | `python3 -m bridge.einstein_sector.flat_einstein_symplectic_restriction --verify bridge/certificates/flat_einstein_symplectic_restriction.json` | 0.38 s | PASS |
| coordination | `python3 d_quotient_programme/verify_programme_status.py --check --guards` | 0.20 s | PASS (8 guards) after the concurrent neutral-clock registration regenerated the dossier |

An earlier check correctly failed while the phase-space registry had advanced
without its generated programme certificate.  The classical/D-programme team
completed that regeneration; none of its files are staged with this theorem.

Tier 3 was not run because no freeze, release, shared-core algebra, full BV,
scattering, or quantum theorem was promoted.
