# Fixed-support smooth-name to rational H2 translator

**Result:** `FOUNDATIONAL_FIXED_SUPPORT_SMOOTH_TO_H2_TRANSLATOR_V1`

## Certified statement

Over RCA_0, every periodic smooth test on the unit cylinder carrying rational fixed-support advice and a supplied uniform derivative approximation rate through order two translates uniformly into the rational compact-time H2 test-code completion, with an explicit primitive-recursive index shift and without an application of choice.

## What the translator consumes

The input is not an unnamed smooth function. It includes a rational support interval, a rational collar, rational periodic approximants, and the rate `2^-m` simultaneously controlling every derivative through order two.

## Exact construction

```text
h(r) = 3r^2 - 2r^3
q_n = chi p_(n+s)
A = ceil(C_H2),  s = least integer with A <= 4^s
||q_n-phi||_H2^2 <= 4^-n
```

| collar delta | C1 | C2 | integer A | shift s |
|---:|---:|---:|---:|---:|
| 1/8 | 12/1 | 384/1 | 167622 | 9 |
| 1/16 | 24/1 | 1536/1 | 2513478 | 11 |
| 1/32 | 48/1 | 6144/1 | 38954886 | 13 |

## Logical reading

No choice principle is used by this translation: the support collar and convergence rate are fields of the input name. Removing those fields is a different mathematical problem, not a harmless change of notation.

## Reproduction

```text
python3 foundations/build_fixed_support_smooth_to_h2_translator.py --check
python3 foundations/check_fixed_support_smooth_to_h2_translator.py
python3 foundations/verify_fixed_support_smooth_to_h2_translator.py
python3 -m unittest foundations.tests.test_fixed_support_smooth_to_h2_translator
```

## Boundaries

- This does not establish a name for a bare extensional smooth function without support and rate advice.
- This does not establish a uniform selection of compact support bounds.
- This does not establish the unrestricted LF topology of compactly supported smooth tests.
- This does not establish a weakest-base reversal or equivalence.
- This does not establish strict causal support or an advanced or retarded Green operator.
- This does not establish a variable-coefficient, curved-spacetime, Weyl, or metric-BV theorem.
