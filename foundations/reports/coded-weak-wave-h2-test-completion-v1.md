# Named H2 test completion for the coded weak wave

**Result:** `FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1`

## Theorem

Over RCA_0, rational periodic compact-time C1 piecewise-polynomial test codes admit a named H2 completion. The coded-circle energy solution defines a continuous spacetime functional on that completion, and the exact finite-code transport and scalar weak-wave identities extend to every supplied fast H2 test name with an explicit primitive-recursive cutoff.

## Why this is the right next gate

The previous ten localized tests proved exact finite compatibility but did not justify the phrase ‘for every smooth test’. This result enlarges the test carrier to all fast H2 names of rational periodic compact-time C1 piecewise-polynomial codes. The convergence rate is mathematical input, so RCA₀ can extend the residual without selecting a modulus from bare convergence.

That distinction is substantive. The global classical space of compactly supported smooth tests is not metrizable; fixing the unit slab and declaring an H2 name chooses a particular represented carrier rather than silently recovering the entire classical test-function topology.

## Exact continuity rail

```text
|R_plus(r;delta phi)|^2<=2 E_right ||delta phi||_H2^2
|R_minus(l;delta phi)|^2<=2 E_left ||delta phi||_H2^2
|W(u;delta phi)|^2<=4 E_total ||delta phi||_H2^2
```

If A is the integer ceiling of the relevant factor, `N_F(k)=k+ell(A)` forces squared error at most `4^-k`. Every rational approximant has residual exactly zero, hence every named limit does too.

## Fixture cutoffs

| Fixture | right offset | left offset | wave offset | distribution offset |
|---|---:|---:|---:|---:|
| `TRIANGLE_RIGHT` | 1 | 0 | 2 | 1 |
| `QUARTER_MIXED` | 2 | 1 | 4 | 3 |
| `NONUNIFORM_MIXED` | 3 | 4 | 5 | 4 |

## What now counts as a test

A test is a fast H2 Cauchy name of rational finite codes. A conventional smooth periodic compact-time test is included when such a name is supplied. The theorem does not manufacture that name from an otherwise unspecified smooth function.

## Literature placement

Pauly and Steinberg make the representation issue explicit: names determine effective topology, while compact support requires extra advice. Van Schaftingen supplies classical context for direct piecewise-polynomial approximation in Sobolev norms. Neither reference is treated as proving this exact RCA₀ certificate.

## Reproduction

```text
python3 foundations/build_coded_weak_wave_h2_test_completion.py --check
python3 foundations/check_coded_weak_wave_h2_test_completion.py
python3 foundations/verify_coded_weak_wave_h2_test_completion.py
python3 -m unittest foundations.tests.test_coded_weak_wave_h2_test_completion
```

## Boundaries

- This does not establish a uniform algorithm assigning an H2 name to every bare extensional smooth test.
- This does not establish the nonmetrizable LF topology of the unrestricted classical test-function space.
- This does not establish a representation-independent distribution theory or weakest-base reversal.
- This does not establish uniqueness among arbitrary distributional weak solutions outside the coded energy image.
- This does not establish pointwise differentiability of the step chiral derivatives.
- This does not establish strict finite propagation or causal support.
- This does not establish an advanced or retarded Green operator.
- This does not establish a variable-coefficient, curved-spacetime, Weyl, or metric-BV equation.
- This does not establish a probability rule or empirical calibration.
- This does not establish a new LORENTZIAN-CAUSAL result.
