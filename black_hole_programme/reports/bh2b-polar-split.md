# BH-2B stage 1: the general branch-split identity

## Verdict

`BH2B_GENERAL_BRANCH_SPLIT_IDENTITY_CLASSIFIED`
(certificate `black_hole_programme/certificates/BH2B_POLAR_SPLIT.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

## The theorem

On the Ricci-flat background, for the polar ℓ=2 RW-gauge perturbation
(four radial functions H0, H1, H2, K — nonzero trace sector δR ≠ 0),
exactly and componentwise:

```text
δB_ab = ½ □(δRic)_ab + C_acbd (δRic)^{cd}
        − ⅙ ∇_a∇_b(δR) − (1/12) g_ab □(δR)
```

with universal constants (½, 1, −1/6, −1/12).  The certified axial
identity is the δR = 0 special case.

## Consequences

- The Einstein branch (δRic = 0) injects exactly into the Bach kernel in
  the polar sector as well.
- The polar extra branch is the second-order **trace-coupled Lichnerowicz
  system** on (ψ_ab, δR) = (δRic_ab, δR): the fourth-order polar problem
  is again a composition of second-order problems, opening the same
  horizon-reach / flux / disposition path certified in the axial sector.

## What was NOT established

- the Zerilli reduction benchmark; polar horizon reach and asymptotics;
  polar flux blocks and signs; polar causal disposition; general ℓ;
  stability/ringdown (still locked).

## Receipts

```bash
python3 black_hole_programme/bh2b_polar_split.py          # producer (~80 s)
python3 black_hole_programme/verify_bh2b_polar_split.py   # independent verifier
python3 -m pytest black_hole_programme/tests/ -q           # fast rail
```
