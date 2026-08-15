# Strict 386-row polarized formal Møller-coefficient gate

## Outcome

The coefficients do assemble uniquely. For each orientation the quadratic Yang-Feldman fixed-point equation has a unique lambda-adic formal inverse whose m-th coefficient is the exact sum of the Catalan(m) plane binary response trees with weight (-1/2)^m. Every coefficient is defined on the certified PC/FC support domain and is continuous on fixed support steps. This is formal convergence only. More importantly, it is not yet a Weyl-BV Moller theorem: the first BV equation coefficient closes, but at lambda squared the available identities leave an explicit B(q2) residual whose vanishing is not certified. The candidate lacks authoritative q2 identity, a typed field-equation Green inverse, and q3/higher source data.

## Explicit convention

```text
R_sigma,lambda(x)=x-(lambda/2) B_sigma(R_sigma,lambda(x),R_sigma,lambda(x))
r_sigma,m(x)=-(1/2) sum_{i+j=m-1} B_sigma(r_sigma,i(x),r_sigma,j(x)) for m>=1
```

The word *Møller* is conditional here: the exact object is the candidate formal Yang--Feldman inverse defined by the displayed equation.

## Exact coefficient census

| Coupling power | Leaves | Plane trees | Weight per tree | Scalar collapse |
|---:|---:|---:|---:|---:|
| 0 | 1 | 1 | `1` | `1` |
| 1 | 2 | 1 | `-1/2` | `-1/2` |
| 2 | 3 | 2 | `1/4` | `1/2` |
| 3 | 4 | 5 | `-1/8` | `-5/8` |
| 4 | 5 | 14 | `1/16` | `7/8` |
| 5 | 6 | 42 | `-1/32` | `-21/16` |
| 6 | 7 | 132 | `1/64` | `33/16` |
| 7 | 8 | 429 | `-1/128` | `-429/128` |
| 8 | 9 | 1430 | `1/256` | `715/128` |

## The promotion gate discovered

For a q1-closed degree-zero input:

```text
q1(r_1)+(1/2)q2(x,x)=0
(1/4)(B_sigma(x,q2(x,x))+B_sigma(q2(x,x),x))
```

The first line closes exactly. The second expression is not certified to vanish and is not claimed nonzero. This is the first point where a formal response-tree inverse stops being automatically identifiable with a Weyl-BV Maurer--Cartan/Møller map.

## Foundations

For each requested m, the tree set, exact rational weights, residual check and support proof are finite primitive-recursive data.

A formal-series type is a countable coefficient sequence; lambda-adic stabilization is not metric or analytic convergence.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_polarized_formal_moller_coefficients.py --check
python3 quantum-weyl/classical_import/check_strict_386_polarized_formal_moller_coefficients.py
python3 quantum-weyl/classical_import/verify_strict_386_polarized_formal_moller_coefficients.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_polarized_formal_moller_coefficients.py
```

## Boundaries

- This does not establish that the stabilized q2 candidate is the authoritative nonlinear classical Weyl BV operation.
- This does not establish that the action-derived hypotheses of the pinned Moller theorem hold for the candidate.
- This does not establish a typed inverse of the full Weyl-BV field-equation operator.
- This does not establish vanishing or nonvanishing of the displayed lambda-squared BV residual.
- This does not establish a Maurer-Cartan solution or a source-certified q2/q3/higher L-infinity solution.
- This does not establish analytic convergence, summability, a convergence radius, a nonperturbative inverse or a selected classical solution.
- This does not establish mixed-sign causal-difference recursion.
- This does not establish an accepted Gate-A q2 or formal-map hash.
- This does not establish a Hadamard state, positivity, renormalized Lorentzian products, QME restoration, residual transfer, unitarity or a Lorentzian quantum theory.

## Next gate

Source-certify the authoritative nonlinear brackets and type the Green homotopy on the actual field-equation sector. Replay the lambda-squared BV residual with q2/q3 identities; only if every coefficient of the interacting equation closes may these formal fixed-point coefficients be promoted to a Weyl-BV Moller map. Analytic convergence remains a later, independent gate.
