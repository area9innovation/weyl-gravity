# Compensator-generated Einstein--Weyl phase receipt

Date: 2026-07-15

## Established

For the minimal four-dimensional Weyl Stueckelberg uplift,

```text
S = S_W + integral sqrt(-g)
    [zeta(phi^2 R - 6 phi Box phi) - lambda phi^4],
```

the local constant frame `phi=v!=0` generates

```text
c1 = zeta v^2,
M_P^2 = -2 zeta v^2,
Lambda_eff = lambda v^2/(2 zeta)
```

in repository conventions.  The scalar and metric background equations agree
exactly, and flat space requires `lambda=0` absent another vacuum-energy
cancellation.

The flat TT kinetic polynomial factorizes as

```text
K(y) = (1/2)y(c1+alpha y) = (alpha/2)y(y+M^2),
M^2 = c1/alpha.
```

The massless and massive roots have normalizations `c1/2` and `-c1/2`.
Thus the generated Einstein-Hilbert term repairs the certified zero-pairing of
the pure-Weyl Einstein root, while retaining an opposite-residue massive
spin-2 branch.  The pure-Weyl limit coalesces the roots and returns the
zero-normalization Jordan sector.

Verdict:

```text
EINSTEIN_WEYL_PHASE_REPAIRS_MASSLESS_PAIRING_BUT_RETAINS_EXTRA_SPIN2
```

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

## Interpretation and coordination

The exact constant-frame theory is Einstein--Weyl gravity, not pure Einstein
gravity.  Einstein metrics with the matching cosmological constant remain an
exact solution sector.  Einstein gravity is a conditional low-energy sector,
or a possible boundary-selected sector if a separate causal/symplectic theorem
removes the massive branch.

The compensator is a Stueckelberg frame variable, not a monotone clock and not
by itself a gauge-invariant order parameter for spontaneous breaking.

The theorem imports the classical team's
`SCALAR_CLOCK_VERTICAL_SLICE.json` by hash.  That certificate proves local
one-scalar clock charts but obstructs a nonzero homogeneous clock on the exact
vacuum cylinder.  The shared next gate is
`BACKREACTED_OR_COMPOSITE_CLOCK_MODEL`.

## Claim boundary

This receipt does not claim a full scalar-metric BV count, spontaneous local
Weyl breaking, causal removal of the massive branch, nonlinear preservation of
the Einstein sector, asymptotically flat scattering equivalence, a positive
quantum Hilbert space, or anomaly cancellation.  It carries no
`LORENTZIAN-CAUSAL` tag.

## Provenance

Input base commit: `704787c06de9e3746c1230e130bb652cb787a825`.

| Artifact | SHA-256 |
|---|---|
| `compensator_einstein_phase.py` | `239d4e5aec5446e520d099f6a6ea53a72d0156e93994b1743136b73273b6edea` |
| `compensator_einstein_phase.schema.json` | `2ba7424e30e7efceef3f72e85b81df3a07caba05996b259ed9679cc342024495` |
| `compensator_einstein_phase.json` | `b5c9f6caa05a263cdb006c33e6bbf60139139d8c30303706e073948a62e7a6b4` |
| `test_compensator_einstein_phase.py` | `af8c86276ef2e7fc318e5b3fc21e151c8a0253368d82a5010736163b7578a53d` |
| `conformal-compensator-einstein-phase.md` | `134a25a539c8276224b8547ce6f2d245678f6e0566fe266f4f99c3bb7e3a2fc8` |
| imported `flat_einstein_symplectic_restriction.json` | `8e3e690b5a1f62d79cdd587c2fa35c9f958604c01ce4f2a08749c367d5ab8f6d` |
| imported `SCALAR_CLOCK_VERTICAL_SLICE.json` | `de30ec828943d8c20be7e36bb523deb4d31f74e817bce92cf6d9374e80ab2948` |
| imported `verify_gravity_reduction.py` | `fb8445e4f590dc706f3c5b0aecc1596b3001d1bdc5e09511039b22874446fcb3` |

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile` on the generator and test | under 0.1 s | PASS |
| 0 | `python3 -m json.tool` on schema and certificate | under 0.1 s | PASS |
| 1 | `python3 -m bridge.einstein_sector.compensator_einstein_phase --verify bridge/certificates/compensator_einstein_phase.json` | 0.39 s | PASS |
| 1/2 | `python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'` | 7.63 s | PASS (55 tests) |
| 2 | `python3 d_quotient_classical/scalar_clock/conformal_scalar_clock.py --check --guards` | 0.41 s | PASS (5 guards) |
| 2 | `python3 -m bridge.einstein_sector.flat_einstein_symplectic_restriction --verify bridge/certificates/flat_einstein_symplectic_restriction.json` | 0.35 s | PASS |
| coordination | `python3 d_quotient_programme/verify_programme_status.py --check --guards` | 0.07 s | FAIL: quantum input still pins the pre-clock classical D-status hash |

The failed coordination check is not counted as a pass and supports no claim.
It arose after the concurrent classical clock commit advanced
`CLASSICAL_D_QUOTIENT_STATUS.json`; the quantum team's committed input has not
yet imported that new hash.  The compensator certificate imports the clock
certificate directly and does not depend on the stale quantum pin.

Tier 3 was not run because this is not a freeze, release, shared-core algebra
change, or Lorentzian/quantum theorem promotion.
