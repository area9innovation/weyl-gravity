# BH-1A: the normalized generator removes the nonintegrability — exact first law

## Verdict

`BH1_NONINTEGRABILITY_REMOVED_BY_FIELD_DEPENDENT_GENERATOR`
(certificate `black_hole_programme/certificates/BH1A_NORMALIZED_GENERATOR.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `PREFLIGHT`).

The BH-1 preflight's exact nonintegrability of the bare Lee–Wald form does
**not** survive the consistently normalized generator: it was an artifact of
the chart-fixed `∂_t`.  This is *not* the full BH-1 phase-space theorem —
everything remains on the static parameter slice.

## The normalization is forced, then everything closes

1. **Frobenius**: `F ∧ dF = 0` exactly, so an integrating factor exists.
2. **Basicness forces N**: a field-dependent generator `χ = N(β,γ,k)∂_t`
   yields the corrected charge form `N·F` (the `Q_{δχ}` term cancels the
   `dN` pieces exactly).  Descending to the residual quotient requires
   `X_c N = 0` and dilation weight −1; the invariant structure forces
   `N = u·f(J)` with `u = β(2−3βγ)`.  The `f(J)` freedom only
   reparametrizes the final charge; the component sign of `u` is fixed by
   future-directedness (`u < 0` on the fixture component, so `N = −u`
   there).
3. **Closure and basicness**: `d(uF) = 0` exactly; `uF` is horizontal and
   Lie-invariant for both residual generators.  Control: the bare `N = 1`
   form stays non-closed.

## Exact Hamiltonian, entropy, first law

- `H = −16πα β²D₂`, `D₂ = 9β²γ²k − βγ³ − 12βγk + γ² + 4k`.  Since
  `J = −u²D₁D₂`, the energy **vanishes identically on the D₂-branch of the
  degenerate-horizon (extremal) locus**, and `dH ∧ dJ = 0`: the charge is a
  function of the single residual invariant `J`, as basicness demands.
- Wald entropy (`E = 2αC`): `S = 64π²αβ(2 − 3βγ + γr_h)/r_h`.  On
  Schwarzschild it is the mass-independent constant `64π²α`, consistent
  with `H ≡ 0` there.
- **First law**: with `T = κ_N/2π = uB′(r_h)/4π`,

  ```text
  dH − T dS = 0   identically modulo B(r_h) = 0,
  ```

  in all three parameter directions and **at every simple root** — so all
  horizons satisfy it simultaneously (`T₁dS₁ = T₂dS₂ = T₃dS₃ = dH`;
  verified exactly at the fixture roots 1, 3, 8).  No pressure–volume or
  boundary source term is needed on the static family in this
  normalization.
- Einstein control ensemble (Schwarzschild–(A)dS, one AdS boundary for
  `k < 0`): `H = −64παβ²k`.

## Ensemble and admissibility audit

- The only residual `c` preserving a fixed-falloff ensemble
  `{γ, k fixed}` is `c = 0`, away from the exact locus `u(w²−3) = 0`
  (`w² = 3` is never rational; `u = 0` degenerates the normalization).
- The dilation preserves an ensemble only at `λ = 1`, except on the
  Schwarzschild sub-ensemble `γ = k = 0` where it acts freely — and
  consistently, since `H ≡ 0` and `S` is constant there.
- The `c`-map factor `Ω = 1/(1+cr)` is smooth and positive on an exterior
  `[r_h, r_out]` iff `c > −1/r_out`; on fixed-falloff ensembles the
  residual directions are frozen regardless.

## What was NOT established

- the presymplectic form and charges for time-dependent perturbations
  (the full BH-1 phase-space theorem);
- uniqueness of the normalized generator among non-static candidates;
- the physical matter/clock frame and its horizon regularity;
- any Lorentzian causal, stability, ringdown, or quantum statement.

Per the plan, BH-2 ringdown stays closed until the dynamical disposition
of this normalization is settled on the enlarged phase space.

## Receipts

```bash
python3 black_hole_programme/bh1a_normalized_generator.py          # producer (~2 s)
python3 black_hole_programme/verify_bh1a_normalized_generator.py   # independent verifier (~2 s)
python3 -m pytest black_hole_programme/tests/ -q                    # all suites
```

The verifier recomputes the entropy density on the verifier-side
Schouten/Kulkarni–Nomizu pipeline, re-derives every algebraic statement
from the independently certified BH-1 charges, and re-runs the first-law
polynomial reduction with separate code.  Higher tiers not run: additive
certificate, no existing chain touched.
