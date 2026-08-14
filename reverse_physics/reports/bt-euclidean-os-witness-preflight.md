# BT interacting reflected-witness preflight

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_OS_WITNESS_PREFLIGHT_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

**Lifecycle:** `CLASSIFIED`

## Result

At $\lambda=0.4$ on the periodic $6^4$ lattice, both HMC and an
independently implemented local Metropolis sampler support a negative value
for the exact free reflected witness.  This is numerical support, not an
exact reflection-positivity obstruction at the interacting coupling.

The retained observable is

\[
 F=-A_1+2A_2-A_3,\qquad
 \theta F=-A_0+2A_5-A_4,
\]

where $A_t$ is the spatial slice average.  Every retained configuration stores
$F$, $\theta F$, and their product.  Four independent seeds were run for each
algorithm.

| algorithm | replicas | retained per replica | equal-replica mean | replica SE | sign score |
|---|---:|---:|---:|---:|---:|
| local Metropolis | 4 | 1,600 | $-0.0007507$ | $0.0002964$ | $-2.53\sigma$ |
| HMC | 4 | 800 | $-0.0005516$ | $0.0000882$ | $-6.25\sigma$ |

All eight individual chain means are negative.  The two algorithm means differ
by only $0.64$ combined standard errors.  The central values therefore point
the same way, and sampler disagreement is not the present barrier.

The local integrated autocorrelation times range from 16.8 to 34.7 retained
samples.  HMC ranges from 1.2 to 2.5.  The local replica rail clears two
standard errors but not three, so the result is classified as
`TWO_SAMPLER_NEGATIVE_SIGN_SUPPORT_NOT_EXACT`.

## Meaning

The numerical result makes it plausible that the strict near-free obstruction
continues as far as $\lambda=0.4$.  It does not prove that statement.  A
negative expectation for this one observable would refute ordinary reflection
positivity if established rigorously, but finite statistical significance is
not a rigorous sign bound.

The appropriate next step is analytic or validated-numeric interval control,
not repeated significance chasing.  The other main reconstruction gate
remains an interacting, volume-uniform negative-Sobolev estimate.

## Verification

```text
python3 reverse_physics/bt_euclidean_os_witness_preflight.py --check
python3 reverse_physics/verify_bt_euclidean_os_witness_preflight.py
python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_os_witness_preflight
```

The producer computes an initial-positive-sequence autocorrelation estimate.
The independent verifier reconstructs every raw product, every chain and
replica mean, the cross-sampler score, and a separate twenty-block sign rail.
Six certificate mutations must be rejected.

## Verification receipt

The eight production chains ran sequentially under a 500,000 KiB virtual
memory ceiling and single-thread numerical-library settings.  Their recorded
wall times sum to 577.81 seconds.  Peak RSS was not recorded for the production
process, so the memory ceiling is a bound rather than a measured peak.

| tier or rail | result | elapsed | peak RSS |
|---|---:|---:|---:|
| Tier 0 parse, JSON, schema and scoped diff | pass | below 1 s | below 38 MiB |
| deterministic producer | 14/14 pass | 0.36 s | 25,572 KiB |
| independent raw-data verifier | 14/14 pass | 0.14 s | 34,468 KiB |
| unit and six-mutation suite | 9 tests pass | 0.73 s | 37,252 KiB |

Tier 2 checks the unchanged exact predecessor by content hash; it does not
reproduce that proof.  Tier 3 was not run because this is a `CLASSIFIED`
finite-volume numerical preflight with no shared operator, continuum theorem,
quantum lifecycle, or Lorentzian promotion.

## Boundaries

- This does not establish an exact sign at $\lambda=0.4$.
- This does not decide reflection positivity for every positive-time observable.
- This does not establish a continuum or infinite-volume limit.
- This does not construct a Krein-compatible reconstruction.
- This does not establish a Born rule, scattering probability, or event rate.
- This does not establish anything tagged `LORENTZIAN-CAUSAL`.

CLOSE-OUT: SHORTFALL -- two samplers support a negative interacting witness, but lambda=0.4 remains open as an exact sign and all-observable theorem.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_OS_WITNESS_PREFLIGHT_V1.json`
