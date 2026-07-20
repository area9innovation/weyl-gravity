# Symbolic-frequency indicial structure at Schwarzschild infinity

## Verdict

`BH2C_SYMBOLIC_INDICIAL_EXCEPTIONAL_SET_IS_OMEGA_ZERO`
(certificate `black_hole_programme/certificates/BH2C_SYMBOLIC_INDICIAL.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

This is the **first split** of the work item
`black-hole-asymptotic-jordan-metric-reconstruction`: the indicial layer,
at symbolic frequency, in both parities. It **extends** — and supersedes
nothing in — `BH2C_ASYMPTOTIC_JORDAN`.

Why the split is the honest unit: every existing asymptotic certificate
records this data at the ω = 3/5 fixture, and `BH2C_ASYMPTOTIC_JORDAN`
explicitly flags `polar_mu2w_symbolic_certified: false`. A fixture cannot
decide which frequencies are exceptional, because an exceptional
frequency is *by definition* one where the indicial data degenerates —
a set of measure zero that a single sampled ω will generically miss.

## 1. Polar carrier, symbolic ω

Leading matrix characteristic polynomial **λ³(λ + 2iω)³**. Both
oscillatory eigenvalues μ ∈ {0, −2iω} have geometric multiplicity 3 equal
to their algebraic multiplicity — verified by explicit nullspace
dimension, never inferred from the characteristic polynomial (the work
item forbids exactly that inference). So the two sectors split semisimply
for every ω ≠ 0. Frobenius exponents, in the producer's convention
(profiles `r^{σ₀−n}`):

| sector | exponents σ₀ |
|---|---|
| μ = 0 | −1, −2, −3 |
| μ = −2iω | −4iω−1, −4iω−2, −4iω−3 |

## 2. Axial, symbolic ω

The level-1 cascade is algebraic in `H1` with coefficient
**ω²/4 − 1/r² + 2/r³**. The level-2 (H0″, H2″) block has **identically
zero determinant** — rank 1 — reproducing symbolically the structure that
`BH2A_COMPOSED_REPAIR` certified at the two fixtures. In Regge–Wheeler
gauge a single second-order ODE closes, with leading characteristic
polynomial **λ(λ + 2iω)** and simple semisimple exponents +1 and −4iω+1
(metric-level growth `r¹`, consistent with the certified hom h-jets and
with `BH2C_METRIC_LEADING`'s one-power enhancement bound).

## 3. The resonance structure does not move with frequency

Within either sector the exponent differences are the integers {1, 2},
**independent of ω**. Across sectors the differences are 4iω + k, an
integer only for imaginary ω — never for real ω ≠ 0. Consequently no
resonance condition migrates as the frequency varies.

Furthermore, since 4iω is purely imaginary for real ω, **Re(σ₀) = −1, −2,
−3 in both oscillatory sectors of the polar carrier for every real ω**:
the curvature-level decay rates are frequency-independent. (Reality of ω
is a *declared hypothesis* applied explicitly — the frequency symbol
carried by the pipeline has no assumptions, so it is never smuggled in.)

## 4. The exceptional set is exactly {0}

For real frequencies the indicial data degenerates only at ω = 0, and it
does so in two independent ways:

- the oscillatory eigenvalues collide (0 = −2iω only at ω = 0);
- the axial cascade loses its leading coefficient (ω²/4 → 0).

ω = 0 is separately classified by `BH2_OMEGA_ZERO`. So the
exceptional-frequency exclusion demanded by the work item is:
**exceptional set (real frequencies) = {0}**.

## Cross-validation against certified data

The leading exponents −1 (μ = 0) and −4iω−1 (μ = −2ω) are *exactly* the
σ₀ values the certified BH2C producers feed to `column_jets` at the
fixture. This is the rail that anchors an independent symbolic derivation
to already-certified numbers. (My internal convention is the negation of
the producer's; that was reconciled explicitly rather than assumed.)

## Decisive mutations

- **M1.** At ω = 0 the polar leading characteristic polynomial collapses
  to λ⁶ with geometric multiplicity 3 < 6 — a genuine Jordan
  degeneration, confirming ω = 0 is exceptional rather than a coordinate
  artifact.
- **M2.** The axial cascade's leading coefficient is ω²/4, which vanishes
  exactly at ω = 0 and nowhere else.

## Verification discipline

The closed-form symbolic reduction **hangs** at symbolic ω (killed after
65 minutes); every reduction here uses exact truncated Laurent series in
u = 1/r and completes in under a second. No floating point, no
`nsimplify`. Semisimplicity is checked by explicit nullspace dimension.
Producer and independent VbGeo verifier each run in under a minute.

## What was NOT established — the remaining splits

The work item's stop condition is **not** fully met by this certificate.
Outstanding, each a successor split:

1. **all-orders metric reconstruction maps** (`BH2C_METRIC_LEADING` has
   leading order only);
2. **the symbolic-frequency finite-flux power table**. Result 3 makes a
   frequency-independent Einstein selection *plausible* — the decay rates
   that control integrability are ω-independent — but the flux table is
   **not computed here and is not claimed**;
3. **the assembled endpoint-nonselection theorem**;
4. general ℓ; Borel/analytic summability.

## Receipts

```bash
python3 black_hole_programme/bh2c_symbolic_indicial.py          # producer (~55 s)
python3 black_hole_programme/verify_bh2c_symbolic_indicial.py   # independent verifier (~56 s)
python3 -m pytest black_hole_programme/tests/test_bh2c_symbolic_indicial.py -q
```

## Close-out

```text
CLOSE-OUT: SHORTFALL — the indicial layer of the stop condition is met in full and at symbolic frequency (asymptotic first-order systems in both parities, eigenvalues, geometric multiplicities, semisimplicity, exponents, and the exceptional-frequency exclusion ω = 0), cross-validated against the certified fixture producers. The remaining three components of the stop condition — all-orders metric reconstruction maps, the symbolic-frequency finite-flux radiation class, and the assembled endpoint-nonselection theorem — are NOT established and are proposed as successor splits of this item. No part of them is claimed.
EVIDENCE: black_hole_programme/certificates/BH2C_SYMBOLIC_INDICIAL.json (producer 55 s, fast rail 6/6, independent VbGeo verifier 56 s all checks passed)
```
