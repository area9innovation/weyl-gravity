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

## Session 2 (2026-07-21): the blocking obstruction is RESOLVED

The gauge-invariant reduction the previous slice deferred is done, and the
symbolic-`omega` **extra-branch asymptotic exponents at infinity are extracted
cleanly in ~2 s**. Still a checkpoint (no certificate): the exponents are the
unblock, but the item forbids "leading exponent alone called finite flux", so the
literal Lee–Wald current evaluation, the polar parity, the phase-space definition
and the ledger remain before a certificate can issue.

**Key idea (resolves the rank-1 gauge degeneracy).** On a Ricci-flat background
`delta Ric` is *gauge-invariant* (`L_xi Ric = L_xi 0 = 0`). So instead of the raw
`(h0, h1)` metric (whose residual axial gauge made the Bach principal symbol
rank-1 degenerate), work directly with the axial **Ricci carrier** `psi_ab`
(trace-free, divergence-free; the certified BH-2A extra-branch object). Its
operator `(1/2)Box psi + C psi = 0` at symbolic `omega`, angular-stripped and
Fourier-reduced, is small and non-degenerate, and its infinity indicial is exact.

**Result (axial l=2, symbolic real `omega`, scratch `ff_extra3.py`, ~2 s).**
The carrier infinity branches are

```
exponential-rate condition:  lambda^2 + omega^2 = 0   =>  lambda = +- i omega
power in each rate sector:    rate -i omega -> s = -2 i omega
                              rate +i omega -> s = +2 i omega
```

i.e. `psi_carrier ~ e^{+- i omega r} r^{+- 2 i omega} = e^{+- i omega r_*}`
(tortoise phase), so the **carrier amplitude is `O(1)` — real part of the
exponent is `0`, independent of `omega`.** By contrast the certified Einstein
sector (`BH2C_METRIC_ALL_ORDERS`, shared master `F = H1'`) decays: branches
`r^{-3}` and `e^{-2 i omega r} r^{-4 i omega + 1}` (amplitude real parts `-3` and
`+1` for `F`; the Einstein *metric* master `psi_E` decays).

**Why this settles the frequency dependence (the note the item flagged).** The
`omega` enters the exponents ONLY through the imaginary tortoise phase
(`e^{+- i omega r_*}`, `|r^{2 i omega}| = 1` for real `omega`); the **amplitude
real parts are `omega`-independent**. So the finite-vs-divergent split is
`omega`-independent *as a derived fact*, not an assumption: Einstein modes decay
(real part `<= -3`), extra modes do not (real part `0`), for every real
`omega != 0`, with the exponents `+- i omega, +- 2 i omega` never real or
colliding (no real exceptional frequency; `omega = 0` excluded).

**Fixture consistency (`BH2C_FLUX_CLASS`, `omega = 3/5`).** The certified flux
DENSITY powers are `E0|E0 = E2|E2 = -2` (integrable at infinity, `< -1` =>
FINITE), and every extra-involving pair `E0|X0 = 0`, `E2|X2 = 1`, `X0|X0 = 0`
(with a log), `X2|X2 = 2` (all `>= -1` => DIVERGENT). This is exactly the
qualitative split the `omega`-independent amplitude exponents predict: the less
decay of the extra branch pushes every extra-involving density above the
integrability floor. The `X0|X0` log matches the resonant/`r^{2 i omega}` tail.

**Remaining steps to a certificate (well-posed, bounded).**
1. Drive the certified literal Lee–Wald bilinears `F_t, F_r`
   (`BH2A_FLUX_MATRIX`, the working fast path from Session 1) with the
   symbolic-`omega` extra-branch metric profiles (the carrier exponents lift to
   the metric via `delta Ric[h_extra] = psi_carrier`, an `O(1/r)` inversion in
   the oscillatory sector), retaining ALL boundary/derivative-of-curvature terms
   — no leading-exponent shortcut. Produce the exact symbolic-`omega` power/log
   table and specialise to `omega = 3/5` against `BH2C_FLUX_CLASS`.
2. Repeat for the polar parity via `BH2C_POLAR_FLUX_CLASS` (same carrier method;
   the shared master already unifies the Einstein sector across parities).
3. Define the asymptotically flat finite-Lee–Wald-flux phase-space candidate in
   coordinate and regular-tetrad variables (differentiability, residual gauge,
   parity, real structure, `omega = 0` exclusion) as part of the certificate.
4. Conjugate-frequency pairing, lift invariance, exceptional-set proof,
   independent current-identity rail, boundary-condition mutations, and the
   does-not-establish ledger.

**Not claimed (unchanged):** no finite-flux, radiative, spectral, or physical
statement is certified at symbolic `omega`; this session records the exponent
structure and the obstruction resolution only.

## Receipts

- Session 1 scratch: `ff_probe.py` (positive control green, ~3 s); exponent-method
  probes (`bach_extra_probe.py`, `bach_classify.py`, `indicial2.py`).
- Session 2 scratch: `ff_extra3.py` (carrier infinity rates `+- i omega` and
  powers `+- 2 i omega`, ~2 s; built on the certified BH-2A carrier operator and
  the `delta Ric` gauge-invariance of the Ricci-flat background).
- No repository source, certificate, schema, atlas, or note under
  `black_hole_programme/` is modified by this slice other than this checkpoint
  report. Only the report is updated.
