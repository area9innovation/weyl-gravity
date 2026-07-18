# Retained mixed ell3 zero-jet full-BV redefinition screen

Dependency tag: `LOCAL-ALGEBRAIC`. Generality: `G0`.

The exact two-Maxwell, zero-PBW Taylor block contains 810 physical-base `F2`
and 4,160 physical-base `F3` coefficients, each extended by the typed
super-cotangent lift. The target-connected matrix has shape `477 x 286`, rank
129, and augmented rank 130.

The obstruction has a one-coordinate normalized dual witness:

```text
output 23; inputs (1,30,35)
target coefficient = 3*sqrt(10)/10
dual weight = sqrt(10)/3
evaluation = 1
```

That row vanishes on all 4,970 admitted columns. It belongs to the
ghost/antifield completion; the separately projected degree-zero physical
action remains compatible.

This is not the final N-G4 verdict. Positive-PBW-jet redefinitions can feed
this filtration page, nonlinear ghost-coordinate redefinitions were not
admitted, and total PBW order two remains open. No cyclic deformation class,
residual interaction, or quantum conclusion is promoted.

## Verification receipt

All commands passed from the repository root on 2026-07-18.

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 2 | exhaustive matrix/rank writer | 79.83 s | PASS; max RSS 157,204 KB |
| 0/1 | fast certificate check | 6.56 s | PASS |
| 1 | independent witness verifier | 6.11 s | PASS |
| 1 | scoped unit tests | 6.81 s | PASS (3 tests) |
| 0 | strict AJV Draft 2020-12 validation | 6.82 s | PASS |

The exhaustive rail is intentionally separate from the fast per-edit witness
rail because it exceeds sixty seconds. Tier 3 was not run: this is a scoped
filtration-page result, not a theorem freeze, shared-core change, lifecycle
promotion, release, or quantum claim.
