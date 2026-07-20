# BH2C symbolic-ω finite-flux — Einstein/extra checkpoint (time-boxed slice)

**Work item:** `black-hole-symbolic-frequency-finite-flux-radiation-class`
**Status:** CHECKPOINT — not closed. The genuinely-new Einstein-vs-extra branch
identification at symbolic ω is **blocked on a gauge-invariant reduction**; the
exact obstruction is recorded below (it is itself the deliverable of this slice).
**No certificate is issued.** No dependency tag is promoted. **Not claimed:** any
finite-flux, radiative, spectral, dynamical-selection or physical statement at
symbolic ω.

This slice was run under an explicit 30-min-per-stage time box with a hard-stop
directive ("no repeat of the multi-hour grind; report back either way"). It was
honoured: every computation below runs in seconds; the stage was stopped when the
*method* (not the compute) walled.

## What was de-risked (fast, exact, symbolic ω)

1. **The bilinear/flux fast path works.** The certified axial Lee–Wald bilinears
   `F_t, F_r` (`BH2A_FLUX_MATRIX['bilinear']`) are driven directly by
   mode-profile substitution + 1/r expansion. Positive control (scratch
   `ff_probe.py`, ~3 s) reproduces the certified leading symbol
   `F_t = (96/5) π i α (λ−ω)² (λ+2ω)` **exactly** and derives
   `F_r = −(96/5) π i α (λ−ω)² (2λ+ω)`; both double-zero on-characteristic
   (λ=ω), so radiative pairs are decided at subleading order — where the
   certified all-orders series (`BH2C_METRIC_ALL_ORDERS`) supplies coefficients.

2. **The Einstein branches are already in closed form.** Both parities' Einstein
   (Ricci-flat / Regge–Wheeler–Zerilli) sector collapses to the certified shared
   master ODE, with exact branches `r^{−3}` (λ=0) and
   `e^{−2iωr} r^{−4iω+1}` (λ=−2iω). Confirmed here: the h-system builders
   `build_axial_M3` / `build_polar_Mh` are constructed from `dRic=0`, so the
   all-orders result governs exactly the **Einstein** sector.

3. **The full linearized-Bach axial EOM is available fast at symbolic ω — no
   composition tower.** `LinearizedBach.build(h)` on the raw axial ansatz
   (`h_{vφ}=h0·S_ax`, `h_{rφ}=h1·S_ax`, `S_ax=−3x(1−x²)`) yields, in ~8–12 s,
   the two Bach rows `dB[1,3], dB[2,3]`, which Fourier-reduce and angular-strip
   cleanly (x-independent). They are small (`count_ops ≈ 150–180`). This is a
   methodological advance over the ω=3/5 fixture (`bh2c_flux_class.py`), whose
   symbolic-ω wall was the *composed/sourced* series tower — **not needed** to
   write the 4th-order EOM.

4. **Principal exponential rates ∈ {0, −2iω}.** The extra (non-Einstein) branches
   share the Einstein *rates* and differ only in *power* σ — consistent with the
   fixture's log / "+2-power" structure at infinity.

## The exact obstruction (this is the deliverable of the slice)

Extracting the two **extra** (non-Einstein) power exponents σ from the 4th-order
Bach axial system at symbolic ω is blocked because the raw `(h0,h1)`
parametrization carries **residual axial gauge**, making the Bach **principal
symbol rank-1 degenerate**. Consequently the exponents are *not* fixed by any
leading-order balance. Three method attempts and their exact failure modes:

- **Full symbolic companion first-order form** (solve `{dB[1,3],dB[2,3]}` for the
  top derivatives `H0'''' , H1'''`, build a 7×7 `M(r)`): the coupled top-derivative
  solve stalls (>19 min, ~1 GB) — even at exact rational ω=3/5 the general solver
  does not return. (A manual triangular back-substitution avoids the solver but
  the subsequent `limit(·,r,∞)` / nested `cancel` over 49 entries did not
  complete in the box.)
- **Leading-balance indicial** (ansatz `H0=A e^{λr}r^s`, `H1=B e^{λr}r^{s+c}`,
  scan offset c): the leading 2×2 determinant is `≡0` (rank-1) for every offset —
  the degeneracy above — so s is undetermined at leading order.
- **Truncated indicial determinant** over the first 2N power-coefficient rows:
  produces a shift-ladder artifact `det ∝ s(s−1)³(s−2)⁴(s−3)⁴(s−4)⁴(s−5)³(s−6)`
  (the exponents smeared over their whole 1/r recursion ladder), so it does not
  isolate the genuine indicial roots.

**Root cause & concrete next step (well-posed, bounded, but a fresh
construction):** fix the residual axial gauge first — build the Regge–Wheeler /
Cunningham–Price–Moncrief gauge-invariant Q so the Bach axial operator becomes a
*single 4th-order scalar ODE* in Q. Its exponents then split cleanly `2 Einstein
⊕ 2 extra`; the extra σ feed the `flux_power` harness to produce the
symbolic-ω E×E / E×X / X×X table, whose ω=3/5 specialisation must reproduce the
`BH2C_FLUX_CLASS` / `BH2C_POLAR_FLUX_CLASS` fixtures. This gauge-invariant
reduction is the same "shearing" step the Einstein-sector scalar collapse let the
all-orders item avoid; for the 4th-order Bach system it appears genuinely
required and is deferred to a dedicated session rather than forced inside this
time box.

## Receipts

- Scratch harness `ff_probe.py` (positive control green, ~3 s); Bach-row builder
  and the three exponent-method probes (`bach_extra_probe.py`,
  `bach_classify.py`, `indicial2.py`) — all in the session scratchpad, all
  fast-completing except the stalling symbolic companion solve noted above.
- No repository source, certificate, schema, atlas, or note under
  `black_hole_programme/` was modified by this slice (verify with
  `git status --short black_hole_programme/`). Only this checkpoint report is new.
