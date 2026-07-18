# BH-1B: the normalized charge survives shaking — dynamical extension certified

## Verdict

`BH1_DYNAMICAL_HORIZON_PHASE_SPACE_CERTIFIED`
(certificate `black_hole_programme/certificates/BH1B_DYNAMICAL_EXTENSION.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `PREFLIGHT`), **scoped to
the linear charge level with the spherical (ℓ = 0) dynamical sector
complete**.  In ordinary language: letting the fields vary in time in every
spherically symmetric way — including arbitrary time-dependent Weyl
rescalings and diffeomorphisms — the BH-1A energy, entropy, and temperature
remain exactly consistent, with no boundary clock or conformal frame choice
needed at this order.

## Exact results

1. **θ audit.**  The Iyer–Wald θ satisfies its defining identity exactly:
   `div θ[2ωg] = 0` (the C² density is conformally invariant) and
   `δ(√-g αC²) = div(√-g θ)` for on-shell parameter variations.
2. **Conformal (frame) sector** — δg = 2ω(t,r)g, arbitrary ω, on-shell by
   exact conformal covariance:
   - the full charge 2-form `k = δQ_χ − i_χΘ(δ)` vanishes **identically,
     componentwise** (Schwarzschild with symbolic mass, and the
     three-horizon extra-branch fixture);
   - the Wald entropy is exactly invariant on the **symbolic MK family**:
     `δ_ω S = 0`;
   - the corrected presymplectic current `ω_symp(δ_conf, δ_param) = 0`
     identically: conformal directions are exact **null directions**.
   The static BH-1A result is therefore physical, not frame-selected, and
   **no boundary clock is required at the linear charge level**.
3. **Diffeo sector** — δg = L_ξg, ξ = a(t,r)∂_t + b(t,r)∂_r arbitrary:
   - the on-shell Noether identity `Θ(L_ξg) − i_ξ(Lε) = dQ_ξ` holds
     exactly, componentwise, on both backgrounds;
   - the charge form `k(δ_ξ) ≡ 0` via the background-only identity route
     `L_ξQ_χ + Q_{[χ,ξ]} − L_χQ_ξ − i_χi_ξ(Lε) + d(i_χQ_ξ)`,
     cross-validated against a direct ε-geometry computation on a
     polynomial witness (and, during development, against a 50-minute
     brute-force run for the temporal component with arbitrary a(t,r));
   - time-dependent ℓ = 0 diffeos are proper gauge: zero charge, zero flux.
4. **Machinery controls.**  The parameter mode reproduces the certified
   static charge `u·F_β` through the fully dynamical pipeline.  The
   presymplectic current must be assembled as the variation of the
   **density** `√-g θ^a` (the ½·tr(h)·θ^a terms are essential — without
   them conservation fails); the corrected current is exactly conserved,
   with the nonzero static-pair value `ω^r(δβ,δγ) = 48α/(19r²)`.
5. **Unique generator extension.**  The bare Noether aperture `∮Q` is
   nonzero at the fixture, so any extension of `N` with `δN ≠ 0` on a
   gauge direction would give that direction a nonzero charge —
   contradicting 2 and 3.  With `δN = du` on parameter directions (BH-1A)
   and `δN = 0` on ℓ ≥ 1 modes (N is a spherical boundary scalar), the
   linear extension of the field-dependent generator is **unique**.
6. **Linearized first law.**  In every certified sector,
   `δH = TδS + (radiative flux)` holds: gauge and conformal sectors give
   `0 = 0 + 0`; the parameter sector is the exact BH-1A first law; ℓ ≥ 1
   linear charges and entropy variations vanish by parity.

## What was NOT established

- the **bilinear radiative symplectic flux matrix** for ℓ ≥ 2 modes — that
  is BH-2A's flux matrix, and with it any statement about waves carrying
  energy across the horizon at second order;
- the second-order / physical-process first law;
- a machine check of the harmonic-orthogonality argument for ℓ ≥ 1 linear
  charges (analytic parity argument only — flagged);
- nonlinear dynamics, stability, or any ringdown-adjacent statement.

## Receipts

```bash
python3 black_hole_programme/bh1b_dynamical.py           # producer (~20-30 min, stage timings in certificate)
python3 black_hole_programme/verify_bh1b_dynamical.py    # independent verifier (~3-5 min)
python3 -m pytest black_hole_programme/tests/ -q          # fast rail only
```

The verifier recomputes the Noether identity, diffeo annihilation,
Schwarzschild conformal annihilation, entropy invariance, θ audit, and the
bare aperture on the verifier-side Schouten/Kulkarni–Nomizu pipeline with
its own form assembly.  The producer's per-stage timings are recorded in
the certificate (`stage_seconds`).  Higher tiers not run: additive
certificate, no existing chain touched.
