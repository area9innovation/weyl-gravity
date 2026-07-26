# Paper 18 consolidation: residual-basic charges and simultaneous first laws

## Outcome

Paper 18 is no longer a companion scaffold. It is now a focused working
manuscript proving, within the declared exact scope:

1. Laurent-class completeness of the static spherical Bach-flat family;
2. the corrected full-Laurent Einstein locus `gamma = 0, w = 1`;
3. nonintegrability of the bare chart-normalized Iyer--Wald form;
4. residual-basic normalization `chi = u f(J) d_t`;
5. the exact Hamiltonian, Wald entropy, and signed temperature;
6. one first law holding simultaneously at every simple horizon;
7. linear spherical conformal- and diffeomorphism-gauge independence.

The title is now:

> Residual-Basic Charges and Simultaneous Horizon First Laws in Static Weyl
> Gravity

The manuscript is 11 pages and includes a theorem-dependency table,
standalone algebraic derivations, an exact three-horizon non-Einstein
fixture, a certificate manifest, and explicit non-results.

## Scientific boundary

The paper does **not** claim:

- completeness beyond the declared Laurent ansatz;
- a preferred physical mass or asymptotic clock;
- a nonlinear or second-order physical-process first law;
- a bilinear radiative flux theorem;
- stability, quasinormal ringing, Hawking radiation, or a quantum result.

The underlying BH1/BH1A/BH1B certificates retain their historical
`PREFLIGHT` lifecycle labels. The paper-specific claim map promotes no
broader phase-space conclusion.

## New publication controls

- `paper/18-static-bach-flat-black-hole-thermodynamics-claim-map.json`
- `paper/generate_18_static_weyl_thermodynamics_claim_map.py`
- `paper/verify_18_static_weyl_thermodynamics_claim_map.py`

The verifier checks certificate hashes, exact positive flags, exact negative
flags, required manuscript formulas, and the working-draft release boundary.

## Verification

All commands were run from the repository root unless stated otherwise.

```text
PASS python3 black_hole_programme/verify_bh0_background.py
PASS python3 black_hole_programme/verify_bh1_lee_wald_preflight.py
PASS python3 black_hole_programme/verify_bh1a_normalized_generator.py
PASS python3 black_hole_programme/verify_bh1b_dynamical.py
PASS python3 -m pytest -q \
  black_hole_programme/tests/test_bh0_background.py \
  black_hole_programme/tests/test_bh1_lee_wald_preflight.py \
  black_hole_programme/tests/test_bh1a_normalized_generator.py \
  black_hole_programme/tests/test_bh1b_dynamical.py
  21 passed in 30.22 s
PASS python3 -m pytest -q black_hole_programme/tests/
  173 passed in 64.90 s
PASS python3 paper/generate_18_static_weyl_thermodynamics_claim_map.py --check
PASS python3 paper/verify_18_static_weyl_thermodynamics_claim_map.py
PASS python3 -m py_compile \
  paper/generate_18_static_weyl_thermodynamics_claim_map.py \
  paper/verify_18_static_weyl_thermodynamics_claim_map.py
PASS three pdflatex passes for Paper 18
PASS three pdflatex passes for Paper 00
```

Tier 0 and the affected Tier 1 chain passed. The complete 173-test
black-hole programme fast suite was run because a theorem paper replaced a
scaffold. No mathematical certificate or shared algebra input changed, so
certificate producers and unrelated classical/quantum programme suites were
not rerun. Re-running a producer would be reproduction rather than
independent verification; all four independent verifiers were run.

## Evidence hashes

```text
d08a76dd21b1c32270f6b8082c382e23561e7865c4454139fffc890ac14911e4  BH0_STATIC_SPHERICAL_BACKGROUND.json
74ff9ba44a51272472dcb2eaf50aab9759383af44ea115c6c5d11d11a08ec1f6  BH1_LEE_WALD_PREFLIGHT.json
12cd1f0746645fffa4e2d9af35b638b7eda64fb10950884a4a0b3c703043ea0b  BH1A_NORMALIZED_GENERATOR.json
8b7b0625e02dc171632de22d91734defd5e79d3ba9fee9a0772b1d12c1194b30  BH1B_DYNAMICAL_EXTENSION.json
```

## Remaining release gates

1. expert review of the residual-basic normalization and its relation to
   existing conformal-gravity thermodynamic ensembles;
2. independent reproduction outside the repository's SymPy stack;
3. immutable archival release with DOI or equivalent content address;
4. a decision on whether to retain the historical `PREFLIGHT` lifecycle
   vocabulary or issue append-only publication-promotion certificates.
