# BH-1 preflight: bare Lee–Wald surface form on the static MK family

## Result boundary

Certificate: `black_hole_programme/certificates/BH1_LEE_WALD_PREFLIGHT.json`
(token `BH1_PREFLIGHT_COMPLETE_BARE_FORM_NONINTEGRABLE`, tags
`LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `PREFLIGHT`).

Scope: the **unrenormalized** Iyer–Wald surface form of
`L = α C_abcd C^abcd`, evaluated for the chart generator `χ = ∂_t` and the
**static parameter variations** `δβ, δγ, δk` on the BH-0 family only.  No
time-dependent perturbation, no phase-space completion, no entropy, no
first law, no stability statement.  This is the brief's overnight items 5–6,
not BH-1 proper.

## Conventions and controls

`θ^a = 2(E^{abcd}∇_d δg_{bc} − δg_{bc}∇_d E^{abcd})`,
`Q^{ab} = −E^{abcd}∇_c χ_d + 2χ_d ∇_c E^{abcd}`, sphere 2-forms
`(Q)_{θφ} = 2√-g Q^{tr}`, `(i_χθ)_{θφ} = −√-g χ^t θ^r`.

**Normalization control (certified, both stacks):** with the Einstein
tensor `E^{abcd} = ½(g^{ac}g^{bd} − g^{ad}g^{bc})` (`L = R`, `16πG = 1`)
the machinery yields `F = ∮(δQ − i_χθ) = 16π δm` exactly on Schwarzschild
**and** Schwarzschild–de Sitter — the Wald/ADM value.

## Exact bare charges (pure Weyl, `E = 2αC`)

For every static variation, `F` is **exactly r-independent** (the
individual `∮δQ` piece is r-dependent — stored witness — so this is a
nontrivial on-shell identity, and it is the exact static flux balance:
horizon and infinity surface integrals agree):

```text
F_beta  = 16 π α (12βγk − γ² − 4k)
F_gamma = 16 π α β (6βk − γ)
F_k     = −16 π α β (2 − 3βγ)
```

Notable values: at Schwarzschild (`γ = k = 0`) the mass variation is
uncharged, `F_beta = 0` (the bare zero-energy feature of conformal
gravity), while `F_k = −32παβ ≠ 0`.  At Einstein points with `βk ≠ 0` the
variation **into the extra Weyl branch** is charged:
`F_gamma|_{γ=0} = 96παβ²k`.  Fixture `(3/2, 12/19, 1/19)`:
`(−64/361, −72/19, 384/19)·πα`.

## The first differentiability obstruction (main preflight result)

The parameter-space 1-form `F = F_β dβ + F_γ dγ + F_k dk` is **not
closed**:

```text
dF = 16πα [ γ dβ∧dγ + 2(1−3βγ) dβ∧dk − 3β² dγ∧dk ] ≠ 0.
```

Therefore **no boundary/corner function `W(β,γ,k)` of the static
parameters can make the bare form a total variation** — proved exactly,
answering the brief's "or prove that no local term in the declared family
works" for this family.

The obstruction has exact structure:

- `ι_{gen_c} dF = 0` and `F(gen_c) = 0` for the residual-gauge direction
  `gen_c = (−3β², 6βγ−2, γ)` (BH-0 certificate): `ker dF = span(gen_c)`,
  so `F` and `dF` descend to the physical (residual-gauge) quotient,
  where `dF` is **nondegenerate**: the obstruction is physical, not gauge.
- Euler identity `ι_{gen_λ} dF = F` for the dilation `gen_λ = (−β, γ, 2k)`,
  and `F(gen_λ) = 0`: both residual directions are *proper gauge*
  (uncharged) on this slice, per the brief's binary criterion.
- The integrable 2-dimensional slices are exactly the parameter surfaces
  ruled by the c-direction (tangent plane must contain `ker dF`).

**Minimal ansatz returned for BH-1 proper:** the first differentiability
solve must either (i) quotient the c-direction and pair a single physical
direction at a time, or (ii) enlarge the phase space with non-parameter
boundary/falloff data.  Parameter-local corner terms are exactly excluded.

## What was NOT established

- any differentiable Hamiltonian, entropy, or first law;
- the action-derived presymplectic form for time-dependent perturbations
  (needed before any dynamical flux or stability claim);
- a preferred generator normalization (the family is not asymptotically
  flat);
- anything Lorentzian-causal or quantum.

## Receipts

```bash
python3 black_hole_programme/bh1_lee_wald_preflight.py          # producer (~7 s)
python3 black_hole_programme/verify_bh1_lee_wald_preflight.py   # independent verifier (~7 s)
python3 -m pytest black_hole_programme/tests/ -q                 # both suites
```

The verifier re-runs the GR normalization controls and the full Weyl
charge computation on the verifier-side curvature pipeline
(Schouten/Kulkarni–Nomizu), then recomputes the obstruction algebra from
the stored charges.  Higher tiers not run: new self-contained certificates,
no existing chain touched.
