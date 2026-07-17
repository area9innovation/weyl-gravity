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
| BH-1 proper | horizon/infinity phase space with falloff enlargement | open |
| BH-2+ | exterior BV complex, stability, observables | not started |

Run everything for a certificate:

```bash
python3 black_hole_programme/<producer>.py
python3 black_hole_programme/verify_<name>.py
python3 -m pytest black_hole_programme/tests/ -q
```
