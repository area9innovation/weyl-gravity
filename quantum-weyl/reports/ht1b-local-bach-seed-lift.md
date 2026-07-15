# HT1b local quadratic-Bach seed lift

Date: 2026-07-15

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

Result state: `LOCAL_METRIC_SEEDS_COMPUTED_FULL_BV_LIFT_BLOCKED`

## Result

The local-to-residual comparison has begun from the curvature side.  The fast
certificate imports content-addressed exact expressions retained by two
independent proper-conformal curvature regressions for the mixed coefficient of

```text
E(gbar + a h1 + b h2) = a b E^(2)[h1,h2] + ...
```

as an exact stereographic radial density before the `S^3` integral.  For the
selected magnetic component, the negative-frequency `A3 -> E2` density
integrates to `-sqrt(5)/(5*pi)`, while the positive-frequency `A3 -> L4`
density integrates to `sqrt(10)/(5*pi)`.

After the already-certified raw-CK/canonical conversion, these values equal
the checked-in HT1 residual entries

```text
K-_1/2_-1/2 [0,17]
K+_1/2_-1/2 [127,83]
```

exactly.  Thus two mode-specialized local metric-sector regression outputs
reach the portable residual `q2` tensor without fitting their values.  The fast
certificate independently verifies the density/measure identity, performs the
radial integrals, verifies the raw/canonical normalization, and resolves both
coordinates in the HT1 matrix payload.  It does not execute the curvature
engine.

A separate Tier-2 audit does execute that engine.  Six direct probes—the slice
and two gauge directions on each frequency side—reconstruct the two certified
local Taub densities.  Two additional reverse slice probes establish the exact
density-level adjoint relation.  The four integrated forward/reverse entries
also obey the exact dagger relation, and the parity-related seed currents agree.

## Claim boundary

These are mode-specialized local radial densities, not a serialization of
the arbitrary-support tensor `B^(2)_{mu nu}[h1,h2]`.  The reverse channels
have directly reevaluated slice densities but no local Taub density because
the reverse gauge probes have not been exported.  The
remaining thirteen residual moment-map components follow from conformal
equivariance; they have not been evaluated pointwise by this certificate.

No Diff/Weyl ghost-metric row or antifield row has been exported.  Therefore

```text
q1 q2 + q2(q1,-) + q2(-,q1) = 0
```

is not yet an executable local identity.  HT1b is not complete, HT2 remains
blocked, and this result is neither quantum nor `LORENTZIAN-CAUSAL`.

## Next exact target

Generate an arbitrary-input bilinear Bach tensor in a finite portable local
basis, then obtain the ghost and antifield rows from the classical master
action.  The promotion criterion is an exact arity-two chain identity and a
full comparison of

```text
pi_cl q2(iota_cl(-),iota_cl(-))
```

with all fifteen certified residual components.

## Machine receipt

`quantum-weyl/transfer/certificates/HT1B_LOCAL_BACH_SEED_LIFT.json`

`quantum-weyl/transfer/certificates/HT1B_DIRECT_CURVATURE_AUDIT.json`

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| `python3 quantum-weyl/transfer/local_bach_seed_certificate.py --emit` | 3.77 | PASS | 1 |
| `python3 quantum-weyl/transfer/local_bach_seed_direct_audit.py --emit --jobs 4` | 665.68 | PASS (8 direct probes) | 2 |
| `python3 -m unittest quantum-weyl/transfer/tests/test_local_bach_seed_direct_audit.py -v` | 1.23 | PASS (5 tests) | 1 |
| `python3 -m unittest discover -s quantum-weyl/transfer/tests -v` | 39.53 | PASS (34 tests) | 1 |
| Compile, JSON/YAML parsing, and scoped `git diff --check` | 0.24 | PASS | 0 |

Tier 3 was not run.  No upstream classical tensor, shared core algebra,
lifecycle state, paper theorem, quantum coefficient, or Lorentzian claim was
changed.  The affected nonlinear bootstrap consumer was regenerated as the
Tier-2 certificate-chain check.  Draft-2020-12 meta-schema validation was not
run because `jsonschema` is unavailable; deterministic JSON parsing and the
custom semantic validators passed.
