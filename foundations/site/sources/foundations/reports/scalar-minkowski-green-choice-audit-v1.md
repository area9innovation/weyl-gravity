# Scalar 1+1 Minkowski Green operators: exact choice audit

**Result:** `FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1`

## Certified statement

For the scalar wave operator on flat 1+1 Minkowski spacetime, rational compact-source codes admit canonical exact retarded and advanced Green maps with two-sided test-code identities, causal support, and adjoint duality in PRA; over RCA_0 these maps extend, with an explicit energy modulus and supplied support tags, to the represented source completion without an application of choice.

## Why this benchmark matters

This is the first cell in the programme where causal support is constructed rather than merely listed as a missing dependency. The formula is canonical, so no theorem saying that some Green operator exists is used as a hidden selection step.

```text
(G_ret f)(t,x)=1/2 integral_{s=-infinity}^t integral_{y=x-(t-s)}^{x+(t-s)} f(s,y) dy ds
(G_adv f)(t,x)=1/2 integral_{s=t}^{infinity} integral_{y=x-(s-t)}^{x+(s-t)} f(s,y) dy ds
```

## Exact fixture audit

| fixture | P G_ret | P G_adv | dual pairing | energy bound |
|---|---:|---:|---:|---:|
| `NULL_MONOMIAL_0_0_TEST_0_0` | 1 | 1 | 1/32 | 1/2 |
| `NULL_MONOMIAL_1_0_TEST_0_2` | 1 | 1 | 1/192 | 1/6 |
| `NULL_MONOMIAL_2_1_TEST_1_1` | 1 | 1 | 1/960 | 1/30 |
| `NULL_MONOMIAL_3_2_TEST_2_0` | 1 | 1 | 1/2688 | 1/70 |

## Choice ledger

| step | base | choice | why |
|---|---|---|---|
| encode finite rational sources and tests | `PRA` | `NONE` | all partitions and coefficients are finite input data |
| construct retarded and advanced code | `PRA` | `NONE` | a fixed cone-integral formula and deterministic chamber refinement are used |
| verify inverse identities and causal support | `PRA` | `NONE` | finite polynomial identities, endpoint jets, and rational inequalities |
| verify adjoint duality | `PRA` | `NONE` | finite exact Fubini reversal |
| extend to fast source names | `RCA_0` | `NONE` | the convergence modulus and time-support bound are supplied |
| assemble support stages | `RCA_0` | `NONE` | support tags are copied from names |
| start from a bare extensional source | `UNRESOLVED` | `NOT_AUDITED` | neither a support tag nor an effective convergence modulus has been supplied |
| general variable-coefficient or Weyl/BV operator | `UNRESOLVED` | `NOT_AUDITED` | the canonical scalar cone formula is unavailable |

## Scope firewall

The `LORENTZIAN-CAUSAL` tag applies only to the flat scalar 1+1 operator displayed here. It is not evidence for a Weyl/BV propagator, Hadamard state, causal perturbative QFT, or quantum master equation.

## Reproduction

```text
python3 foundations/build_scalar_minkowski_green_choice_audit.py --check
python3 foundations/check_scalar_minkowski_green_choice_audit.py
python3 foundations/verify_scalar_minkowski_green_choice_audit.py
python3 -m unittest foundations.tests.test_scalar_minkowski_green_choice_audit
```

## Boundaries

- This does not establish uniqueness among all arbitrary distributional solutions.
- This does not establish support or convergence data selected from a bare extensional source.
- This does not establish a variable-coefficient or curved-spacetime Green operator.
- This does not establish a Green operator for conformal Weyl gravity or the metric BV complex.
- This does not establish a BRST-compatible Hadamard state or renormalized time-ordered products.
- This does not establish a causal perturbative AQFT construction or Lorentzian quantum master equation.
- This does not establish a weakest-base reversal.
- This does not establish empirical adequacy or a complete physical theory.
