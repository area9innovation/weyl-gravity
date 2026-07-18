# Retained mixed ell3 zero-jet ghost-shear completion

Dependency tag: `LOCAL-ALGEBRAIC`. Generality: `G0`.

The normalized ghost/antifield witness in the physical-only cotangent screen
identified the smallest missing carrier: the three retained components of the
already-certified typed Maxwell covariant-ghost shear. Adding exactly those
columns changes the target-connected rank comparison from `129 < 130` to
`132 = 132`.

An exact primitive has 67 nonzero coefficients, all in `F2`. The three ghost
shear base maps

```text
F2^26(0,28) = -1
F2^26(1,29) = -1
F2^26(2,30) = -1
```

are present with their complete typed cotangent partners. Coefficientwise
replay reconstructs all 186 canonical two-Maxwell zero-word BV coefficients
with no missing, extra, or changed entries.

Thus the earlier physical-only zero-page obstruction is diagnostic, not a
deformation obstruction. The full zero-PBW BV page is trivial once its
smallest certified ghost carrier is admitted. Positive PBW orders one and two
remain open; no full deformation-class, residual, or quantum claim is made.

## Verification receipt

All commands passed from the repository root on 2026-07-18.

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 2 | exhaustive matrix/rank/primitive writer | 103.16 s | PASS; max RSS 157,592 KB |
| 0/1 | fast certificate check | 13.35 s | PASS |
| 1 | independent primitive verifier | 13.06 s | PASS |
| 1 | scoped unit tests | 5.01 s | PASS (3 tests) |
| 0 | strict AJV Draft 2020-12 validation | 6.87 s | PASS |

The exhaustive rail is split from the fast edit rail because it exceeds sixty
seconds. Tier 3 is not required because this is a scoped filtration-page
result rather than a theorem freeze or quantum lifecycle promotion.
