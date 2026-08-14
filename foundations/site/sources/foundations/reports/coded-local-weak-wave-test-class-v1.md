# Localized coded weak-wave test class v1

**Result:** `FOUNDATIONAL_CODED_LOCAL_WEAK_WAVE_TEST_CLASS_V1`

## Theorem

PRA certifies a ten-element characteristic-localized rational polynomial test family that separates the declared labelled finite chiral coefficient carrier and annihilates every coefficient of its two weak transport equations and derived scalar weak wave equation. RCA_0 transfers those finitely many bounded weak identities to the represented fast-Cauchy energy completion.

## What is separated

The carrier retains the right/left labels present in the source representation; it is not a scalar-field quotient or a gauge-invariant observable algebra.

The common partition has five spatial cells. The labelled carrier has dimension 10; imposing the two mean-zero equations leaves dimension 8.

The ten localized tests give a `10 x 10` diagonal rational measurement matrix of rank **10**. Its determinant is nonzero, so the tests separate every declared labelled coefficient before and after the mean-zero restriction.

## Localized tests

`B_[a,b](s)=((s-a)(b-s))^2 for a<=s<=b and 0 otherwise`

All finite rational linear combinations of the ten displayed basis tests.

Each basis element is compact in the time interval `[1/8,3/8]` and in one right- or left-characteristic spatial strip. It is a finite periodic `C1` rational polynomial code, not a point detector.

## Coefficient-wise weak equation

`R_plus(r;phi)=integral r(t,x)(phi_t+phi_x) dt dx=0`

`R_minus(l;phi)=integral l(t,x)(phi_t-phi_x) dt dx=0`

`W(u;phi)=integral u(t,x)(phi_tt-phi_xx) dt dx=R_plus-R_minus=0`

For every basis test, the characteristic chain rule turns each transport residual into a temporal boundary term. The temporal bump vanishes at both endpoints. Thus all twenty transport coefficients and all ten derived scalar-wave coefficients vanish exactly for each fixture; rational linear combinations follow by linearity.

PRA checks the finite polynomial, rank, pairing, and residual arithmetic. RCA₀ transfers the finitely many bounded identities to the represented fast-Cauchy completion. This is not a claim for every smooth test function.

## Exact fixture summary

| Fixture | Local measurements | Transport residuals | Scalar residuals |
|---|---:|---:|---:|
| `TRIANGLE_RIGHT` | 10 | 20 | 10 |
| `QUARTER_MIXED` | 10 | 20 | 10 |
| `NONUNIFORM_MIXED` | 10 | 20 | 10 |

## Reproduction

```text
python3 foundations/build_coded_local_weak_wave_test_class.py --check
python3 foundations/check_coded_local_weak_wave_test_class.py
python3 foundations/verify_coded_local_weak_wave_test_class.py
python3 -m unittest foundations.tests.test_coded_local_weak_wave_test_class
```

## Boundaries

- This does not establish separation after forgetting the declared right/left chiral labels.
- This does not establish a separating algebra for arbitrary completed L2 states or gauge equivalence classes.
- This does not establish the weak wave equation against every smooth compactly supported test.
- This does not establish a representation-independent distributional solution theorem.
- This does not establish pointwise differentiability of the step components.
- This does not establish strict finite propagation or causal support.
- This does not establish an advanced or retarded Green operator.
- This does not establish a variable-coefficient, curved-spacetime, Weyl, or metric-BV equation.
- This does not establish a probability rule or empirically calibrated detector.
- This does not establish a new LORENTZIAN-CAUSAL result.
