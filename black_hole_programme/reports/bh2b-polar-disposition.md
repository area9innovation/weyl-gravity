# BH-2B stage 6: polar causal disposition — the extra branch is unavoidable

## Verdict

`BH2B_POLAR_CAUSAL_DISPOSITION_EXTRA_BRANCH_UNAVOIDABLE`
(certificate `black_hole_programme/certificates/BH2B_POLAR_DISPOSITION.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

**This closes BH-2 at the ℓ = 2 linear mode level in both parity
sectors.** Together with the axial disposition (BH-2A stage 5): pure-Weyl
black-hole exteriors cannot be causally truncated to the Einstein sector;
their radiation lives in the mixed/extra sectors.

## Exact results

Asymptotic classification of the certified polar extra-branch carrier
(traceless slice, EF chart, m = 1, symbolic real ω), ansatz
(a, bc, cc) ~ e^{iμr} r^σ v₀:

1. **Dispersion μ³(μ+2ω)³** — the t-chart (λ²−ω²)³: the polar extra
   branch propagates on exactly the Einstein characteristics
   (massless/luminal), 3-dim amplitude spaces at each sign
   (2 physical + 1 conformal-gauge).
2. **σ-spectra** (degenerate second-order solvability): t-chart
   σ ∈ {±2iω−1, ±2iω−2, ±2iω−3} — pure Coulomb log-phases with
   amplitude falloffs r⁻¹, r⁻², r⁻³. **All decaying** — strictly
   stronger than the axial case (r⁰, r⁻¹): no growing asymptotic
   solutions at real frequencies.
3. **Einstein control**: the certified 2-dim polar Einstein system
   eliminates to a K-scalar with dispersion ∝ (λ²−ω²) and σ = ±2iω —
   same characteristics; the branches are asymptotically
   indistinguishable by falloff class.
4. **Gauge control**: the conformal scalar wave has dispersion (λ²−ω²)
   and σ = ±2iω−1, matching one carrier branch — identifying the gauge
   direction inside the carrier asymptotics.

## Disposition

Combining certified facts: the polar extra branch (i) reaches the future
horizon with a two-parameter physical ingoing-regular family modulo
conformal gauge (stage 2), (ii) carries nonzero horizon flux with the
Einstein block symplectically null (stages 4–5), and (iii) is bounded
decaying oscillatory radiation on the Einstein characteristics at
infinity (this stage). No causal decay or regularity prescription at
either boundary excludes it; exclusion could only be a branch projection
on scattering data, which constrains both temporal ends and is not a
causal initial-boundary condition.

## What was NOT established

- complex-frequency structure (BH-3 vocabulary stays locked pending
  coordinator review); general ℓ, m; ω = 0;
- initial-boundary well-posedness; nonlinear/all-orders statements;
- invariant extra-block sign theory (null-quotient pairing).

## Receipts

```bash
python3 black_hole_programme/bh2b_polar_disposition.py            # producer (~1 min)
python3 black_hole_programme/verify_bh2b_polar_disposition.py     # independent verifier (~1 min)
python3 -m pytest black_hole_programme/tests/test_bh2b_polar_disposition.py -q  # fast rail (<1 s)
```

The verifier re-runs everything on the VbGeo Schouten/Kulkarni–Nomizu
pipeline and cross-checks the recorded σ-spectra. Inputs pinned by hash.
