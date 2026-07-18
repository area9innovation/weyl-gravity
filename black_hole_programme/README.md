# Black-hole programme

Workspace of the black-hole team.  The commissioning brief is
[`notes/d-quotient-black-hole-team-brief.md`](../notes/d-quotient-black-hole-team-brief.md);
the claim ladder and lifecycle discipline defined there are binding for
every certificate in this directory.

## Layout

- `weyl_geometry.py` — exact sympy curvature/Bach engine with the frozen
  conventions (signature, Riemann, Weyl, Bach, action).
- `lee_wald.py` — exact Iyer–Wald surface machinery (θ, Q, sphere forms)
  for `L(g, Riemann)`, GR-normalization-controlled.
- `bh0_background.py` — BH-0 producer: static spherical background
  classification.  Certificate:
  `certificates/BH0_STATIC_SPHERICAL_BACKGROUND.json`.
- `bh1_lee_wald_preflight.py` — BH-1 preflight producer: bare charges,
  static flux balance, and the exact differentiability obstruction.
  Certificate: `certificates/BH1_LEE_WALD_PREFLIGHT.json`.
- `verify_bh0_background.py`, `verify_bh1_lee_wald_preflight.py` —
  structurally independent verifiers (own curvature pipeline via
  Schouten/Kulkarni–Nomizu, own GR controls).
- `schema/` — strict JSON schemas, one per certificate.
- `tests/` — Tier-1 suites (fast rail + exhaustive rail per certificate).
- `reports/` — human-readable result-boundary reports; each states
  explicitly what was **not** proved.

## Status

| Gate | Token | State |
|---|---|---|
| BH-0 | `PURE_WEYL_STATIC_SPHERICAL_BACKGROUND_CLASSIFIED` | certified (`LOCAL-ALGEBRAIC`) |
| BH-1 preflight | `BH1_PREFLIGHT_COMPLETE_BARE_FORM_NONINTEGRABLE` | certified: bare static charges exact and r-independent; no parameter-local boundary term can restore differentiability; obstruction degenerate exactly along the residual gauge |
| BH-1A | `BH1_NONINTEGRABILITY_REMOVED_BY_FIELD_DEPENDENT_GENERATOR` | certified: normalized generator χ = u∂_t (forced by basicness) closes the charge form exactly; H = −16παβ²D₂; Wald entropy exact; first law dH = TdS at every horizon; ensemble audit closed |
| BH-1B | `BH1_DYNAMICAL_HORIZON_PHASE_SPACE_CERTIFIED` | certified (linear charge level, ℓ=0 dynamical sector complete): conformal and diffeo directions carry zero charge/flux exactly; entropy conformally invariant on the family; unique linear extension of the normalized generator; no boundary clock needed |
| BH-2A stage 1 | `BH2A_AXIAL_L2_OPERATOR_AND_BRANCH_SPLIT_CLASSIFIED` | certified: axial ℓ=2 operator; Regge–Wheeler master equation reproduced exactly; branch-split theorem δB = ½□δRic + C∘δRic (Einstein branch injects; extra branch = 2nd-order Lichnerowicz-type carrier ψ = δRic); split OBSTRUCTED off Einstein backgrounds |
| BH-2A stage 2 | `BH2A_EXTRA_BRANCH_REACHES_HORIZON_LINEAR_MODE_LEVEL` | certified: in the ingoing EF chart the extra branch has a two-parameter ingoing-regular family at every frequency (regular singular point, residue spectrum {0,0,−4imω,−2−4imω}, kernel rank 2); horizon regularity cannot exclude the extra branch |
| BH-2A stage 3 | `BH2A_FLUX_MATRIX_STAGE1_RW_BRANCH_SYMPLECTICALLY_NULL` | certified: general axial bilinear + off-shell 4α identity; RW-block flux vanishes for conjugate pairs — the Einstein branch is symplectically null; all pairing lives in the Einstein×extra cross-block |
| BH-2A stage 4 | `BH2A_CROSS_BLOCK_NONZERO_HORIZON_FLUX_FIXTURES` | certified (fixtures ω∈{3/5,2/7}, verifier adds 1/2; RW-null control < 1e-12): extra-branch horizon flux norm nonzero with i·F^r > 0 for α>0; Einstein×extra cross pairing nonzero — all horizon flux lives in the mixed/extra sectors |
| BH-2A stage 5 | `BH2A_AXIAL_CAUSAL_DISPOSITION_EXTRA_BRANCH_UNAVOIDABLE` | certified: extra branch propagates on Einstein characteristics with no growing asymptotics; no causal boundary prescription excludes it — pure-Weyl exteriors cannot truncate to the Einstein sector; **BH-2A axial ℓ=2 closed** |
| BH-2B stage 1 | `BH2B_GENERAL_BRANCH_SPLIT_IDENTITY_CLASSIFIED` | certified: δB = ½□δRic + C∘δRic − ⅙∇∇δR − (1/12)g□δR componentwise (polar ℓ=2 included; axial identity is the δR=0 case); polar extra branch = trace-coupled 2nd-order Lichnerowicz system |
| BH-2B remainder | Zerilli benchmark, polar reach/flux/disposition, general ℓ, complex-frequency, well-posedness | open — BH-3 vocabulary stays locked pending these and coordinator review |

Run everything for a certificate:

```bash
python3 black_hole_programme/<producer>.py
python3 black_hole_programme/verify_<name>.py
python3 -m pytest black_hole_programme/tests/ -q
```
