# Flat scalar biwave Green construction

**Result:** `FOUNDATIONAL_SCALAR_MINKOWSKI_BIWAVE_GREEN_V1`

## Certified statement

For B=(partial_t^2-partial_x^2)^2 on flat 1+1 Minkowski spacetime, the canonical compositions H_ret=G_ret o G_ret and H_adv=G_adv o G_adv are exact two-sided Green maps on the declared rational source and global-C3 test-code domains, preserve strict retarded or advanced support, and obey adjoint duality in PRA. Over RCA_0, supplied fast L2 names, source width, and a finite observation horizon give a choice-free represented extension with an explicit two-stage energy modulus and four past-zero Cauchy data.

## Construction

```text
B = P^2
H_ret = G_ret o G_ret
H_adv = G_adv o G_adv
```

The second cone integration adds polynomial weight but no wider causal support: causal transitivity collapses the nested cone back to the original future or past cone.

## Exact fixtures

| fixture | B H_ret | B H_adv | adjoint pairing | finite-horizon bound |
|---|---:|---:|---:|---:|
| `BIWAVE_NULL_MONOMIAL_0_0_TEST_0_0` | 1 | 1 | 1/1152 | 2/1 |
| `BIWAVE_NULL_MONOMIAL_1_0_TEST_0_2` | 1 | 1 | 1/7680 | 2/3 |
| `BIWAVE_NULL_MONOMIAL_2_1_TEST_1_1` | 1 | 1 | 1/69120 | 2/15 |
| `BIWAVE_NULL_MONOMIAL_3_2_TEST_2_0` | 1 | 1 | 1/307200 | 2/35 |

## Four-data interpretation

The factorization `w=P phi`, `P w=f` exposes two ordinary zero-data wave solves. Together they select the four past-zero Cauchy data required by a fourth-order-in-time equation; this is a selection by the retarded formula, not a claim that every fourth-order theory is healthy.

## Scope firewall

The `LORENTZIAN-CAUSAL` tag applies only to the displayed flat scalar operator. No tensor, gauge, BRST/BV, Hadamard, renormalization, or QME statement transfers from it.

## Reproduction

```text
python3 foundations/build_scalar_minkowski_biwave_green.py --check
python3 foundations/check_scalar_minkowski_biwave_green.py
python3 foundations/verify_scalar_minkowski_biwave_green.py
python3 -m unittest foundations.tests.test_scalar_minkowski_biwave_green
```

## Boundaries

- This does not establish a global bounded-energy estimate for persistent retarded biwave solutions.
- This does not establish uniqueness among arbitrary distributional solutions.
- This does not establish support, horizon, or convergence data selected from a bare extensional source.
- This does not establish a curved or variable-coefficient tensor Green operator.
- This does not establish a gauge-fixed Green-hyperbolic Weyl BV complex.
- This does not establish BRST-compatible causal homotopies.
- This does not establish a Hadamard state or wavefront-set theorem.
- This does not establish renormalized Lorentzian time-ordered products, causal pAQFT, or a Lorentzian QME.
- This does not establish a weakest-base reversal.
- This does not establish empirical adequacy or a complete physical theory.
