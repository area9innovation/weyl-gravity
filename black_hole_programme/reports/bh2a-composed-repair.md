# Corrected axial composed lift and exact horizon-flux constants

## Verdict

`BH2A_COMPOSED_LIFT_CORRECTED_EXACT_CONSTANT_FLUX`
(certificate `black_hole_programme/certificates/BH2A_COMPOSED_REPAIR.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

This certificate **supersedes the fixture values and the on-shell
r-independence language of BH2A_CROSS_FLUX** (kept as an append-only
historical record; its verifier now refuses fail-closed at the
`pipeline_sha256` provenance check because the D1/D2 pipeline fixes changed
`axial_flux_modes.py` — by design it can no longer re-verify against the
corrected tree) and completes claim repair (b) of the earlier planning
directive at the axial fixture level with **exact rational constants**
replacing the controlled-numerical values.

## The three pipeline defects (documented, each with receipts)

- **D1** — the sourced first-order reduction differentiated through the
  radial source symbol as if constant, dropping the X′ term.
- **D2** — the particular recursion never imposed the n = 0 Frobenius
  balance Res·Y₀ = −[N·s]₋₁ (it started at Y₀ = 0); the exact
  cokernel-solvability scalars vanish, so the correct leading
  coefficient exists and is nonzero.
- **D3** — the reduction imposed an incomplete row system. The correct
  composition uses the Bianchi-cascade constraint (algebraic in H1)
  together with the (v,φ) row — the row the original pipeline computed
  but never imposed. The earlier exact "T(0)" constants
  (24221/8450 − 2406i/845 at ω=3/5; 23109/5537 − 340i/113 at ω=2/7)
  survive as diagnostics of the defective row pair, not as a gauge
  obstruction.

## The corrected structure (certified, both fixtures)

Level-1 cascade: K = e·Rt − a·Rr is algebraic in H1. Level-2: the
remaining (H0″, H2″) block is exactly rank 1, and its null combination
K2 = L·b has zero net coefficient on every field and vanishes exactly on
the Bianchi-constrained carrier — a pure source-compatibility identity.
Hence one second-order equation for (H0, H2) plus one function of gauge
freedom: **the lift exists in Regge–Wheeler gauge (H2 = 0)** through the
correct row combination; the composed particular has exactly zero n = 0
cokernel obstruction and is log-free; and the corrected mode satisfies
all three δRic rows with exactly zero structured residual through the
certified window (ρ⁸).

## Exact constant fluxes

t-chart sphere-integrated Lee–Wald F^r on conjugate pairs; the series
evaluation route is validated order-by-order against the independent
rational-function route; every window coefficient ρ¹…ρ⁸ is exactly zero
(true on-shell constancy — the superseded values were radius-dependent
evaluations of an off-shell pseudo-mode):

| pair | ω = 3/5 | ω = 2/7 |
|---|---|---|
| RW×RW (control) | 0 exactly | 0 exactly |
| RW×extra (cross) | −10893744/129625 + 780048 i/25925 | −15606912/844025 + 1283712 i/120575 |
| extra×extra | 284488128 i/648125 | 206883648 i/5908175 |

**Sign finding (frequency-robust):** the corrected extra-block constants
are positive-imaginary at both fixtures — opposite to the superseded
values — so under the superseded convention i·F^r/(πα) the extra-block
pairing is **negative** at the horizon at both frequencies. Conventions
are pinned by the certified BH2A_FLUX_MATRIX bilinear and the slot order;
the representative-invariant sign theory remains open.

## Verification-discipline receipts (tool-traps observed and banked)

1. global `cancel` on giant substituted trees returns wrong results;
2. `nsimplify` snaps small residuals to exact zero;
3. intermediate series products must not be truncated at the output
   window when later factors carry negative Laurent keys;
4. `.coeff` on `expand`ed giant trees returns partial coefficients (use
   `linear_eq_to_matrix`);
5. null-combination constraints must be built from the b-side of
   `linear_eq_to_matrix` (syntactic top-derivative terms do not cancel).

All certificate receipts use structured Laurent arithmetic, pointwise
exact-rational checks, and per-level fail-closed asserts.

## What was NOT established

- symbolic ω dependence; general ℓ, m; the polar composed-repair
  counterpart; outer-boundary counterparts;
- a representative-invariant sign theory for the extra block;
- any stability statement.

## Receipts

```bash
python3 black_hole_programme/bh2a_composed_repair.py            # producer (~40 min)
python3 black_hole_programme/verify_bh2a_composed_repair.py     # independent verifier (~40 min)
python3 -m pytest black_hole_programme/tests/test_bh2a_composed_repair.py -q
```
