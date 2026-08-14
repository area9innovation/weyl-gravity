# Support-indexed test spaces: represented union versus LF topology

**Result:** `FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1`

## Certified statement

Over RCA_0, conventional compactly supported smooth-test names with discrete support advice are uniformly equivalent to a tagged support-indexed union of fixed-support smooth names. The fixed-stage translators coherently embed every such named test into the rational H2 carrier and assemble the coded weak identity, while equality with the full locally convex LF topology remains explicitly unestablished.

## The comparison in plain language

A computational test-function name needs to say where the function is supported. Writing that information beside the smooth name or writing it as the index of a fixed-support stage are exactly reversible bookkeeping choices. The certificate proves this name-level equivalence.

It does **not** infer that the resulting represented topology is the entire classical locally convex LF topology. Nor does mapping every named smooth test into H2 make H2 the classical test-function space: H2 contains nonsmooth limits.

| stage j | support K_j | collar K_(j+1) | H2 shift |
|---:|---|---|---:|
| 0 | [1/4, 3/4] | [1/8, 7/8] | 9 |
| 1 | [1/8, 7/8] | [1/16, 15/16] | 11 |
| 2 | [1/16, 15/16] | [1/32, 31/32] | 13 |
| 3 | [1/32, 31/32] | [1/64, 63/64] | 15 |
| 4 | [1/64, 63/64] | [1/128, 127/128] | 17 |
| 5 | [1/128, 127/128] | [1/256, 255/256] | 19 |

## Status ledger

- Represented name equivalence: **proved**.
- Coherent stagewise H2 embedding: **proved**.
- Weak residual for every represented-union test: **proved**.
- Identification with the full locally convex LF topology: **not established**.
- Identification with one H2 metric completion: **excluded**.

## Reproduction

```text
python3 foundations/build_support_indexed_test_space_comparison.py --check
python3 foundations/check_support_indexed_test_space_comparison.py
python3 foundations/verify_support_indexed_test_space_comparison.py
python3 -m unittest foundations.tests.test_support_indexed_test_space_comparison
```

## Boundaries

- This does not establish a support bound selected uniformly from a bare extensional function.
- This does not establish equality between the represented quotient topology and the full classical locally convex LF topology.
- This does not establish surjectivity of the smooth-test embedding onto the H2 completion.
- This does not establish a single metrization or metric completion of the classical test-function LF space.
- This does not establish a weakest-base reversal.
- This does not establish causal Green propagation, a Weyl equation, or a metric-BV theorem.
