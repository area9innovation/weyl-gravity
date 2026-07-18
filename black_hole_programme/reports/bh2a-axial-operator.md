# BH-2A stage 1: the axial operator and an exact branch-split theorem

## Verdict

`BH2A_AXIAL_L2_OPERATOR_AND_BRANCH_SPLIT_CLASSIFIED`
(certificate `black_hole_programme/certificates/BH2A_AXIAL_OPERATOR.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

First block of BH-2A only: the axial ℓ=2 linearized operator and its exact
branch structure.  **No flux matrix, operator domain, horizon-reach,
well-posedness, stability, or ringdown claim.**

## Exact results

1. **New machinery.**  `linearized_bach.py` computes δB_ab[h] as a linear
   operator against background covariant derivatives (~500× faster than
   ε-differentiating the nonlinear pipeline, which was intractable here).
   Controls: conformal direction → 0; family tangent → 0; an ℓ=0 mutation
   direction reproduces the ε-derivative of the exact nonlinear Bach
   tensor componentwise (nonzero) — on both the producer and the
   verifier-side curvature pipelines.
2. **Axial rows.**  For h_tφ = h0(t,r)·S, h_rφ = h1(t,r)·S
   (S = sinθ ∂_θP₂, Regge–Wheeler gauge, rational chart x = cosθ) on
   Schwarzschild: nonzero components exactly {tφ, rφ, xφ}, fourth order,
   with the exact trace identity g^{ab}δB_ab = 0 and Bianchi-type
   divergence identity ∇^aδB_ab = 0.
3. **Literature benchmark (required reproduction).**  Eliminating h0 via
   the constraint row, ψ = B h1/r satisfies exactly the Regge–Wheeler
   master equation `B(Bψ′)′ + (ω² − V)ψ = 0`, `V = B(6/r² − 6m/r³)`
   (ℓ=2), with proportionality factor −r⁶.
4. **Branch-split theorem.**  On the Ricci-flat background, exactly and
   componentwise:

   ```text
   δB_ab = ½ □(δRic)_ab + C_acbd (δRic)^{cd}.
   ```

   Consequences: the Einstein (Regge–Wheeler) branch δRic = 0 injects
   exactly into the Bach kernel; the **extra fourth-order branch is
   exactly a second-order Lichnerowicz-type wave field** with carrier
   ψ_ab := δRic_ab and equation ½□ψ + C∘ψ = 0.  The fourth-order axial
   system is the composition of two second-order problems.
5. **Non-Einstein obstruction.**  On the extra-branch fixture background
   the same two-term identity admits no constant-coefficient fit: the
   naive split is OBSTRUCTED off the Einstein subfamily, and the branch
   decomposition around non-Einstein backgrounds is open.

## What this sets up (not yet claimed)

The extra branch being second-order Lichnerowicz-type makes the two
central BH-2A questions well-posed and tractable: its ingoing-horizon
behaviour (indicial analysis of ½□+C at r = 2m) and the bilinear flux
matrix between the two branches.  General ℓ, the polar sector, operator
domains, and everything causal remain open, as does the black-hole
tangent-cone analogue, which waits on the adjoint problem.

## Receipts

```bash
python3 black_hole_programme/bh2a_axial_operator.py          # producer (~2.4 min, stage timings in certificate)
python3 black_hole_programme/verify_bh2a_axial_operator.py   # independent verifier (~25 s)
python3 -m pytest black_hole_programme/tests/ -q              # fast rail
```

The verifier re-runs the frozen linearization formulas on the
Schouten/Kulkarni–Nomizu pipeline with its own covariant-derivative code
and re-derives the controls, identities, benchmark, and split.  Higher
tiers not run: additive certificate, no existing chain touched.
