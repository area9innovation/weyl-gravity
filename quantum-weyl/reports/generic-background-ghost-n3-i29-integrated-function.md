# Generic ghost `n=3` pole-four `I29` function

## Result

The sole pole-four channel in the generic scalar-flat ghost triangle is now
integrated exactly. The certified carrier is

\[
 -\frac{16}{27}\int_{\Delta_2}
 \frac{(\alpha_0\alpha_1\alpha_2)^3}{\Delta^4},
 \qquad
 \Delta=\alpha_1\alpha_0x_1+\alpha_1\alpha_2x_2
       +\alpha_2\alpha_0x_3.
\]

This is an `EUCLIDEAN-SPECTRAL` result. Together with the ten previously
completed pole-three rows it closes all eleven generic ghost `n=3` functions,
but it does not yet assemble the full ghost determinant or any repository
Weyl-gravity form factor.

## Orbit-first quotient

For a pole-four relative-IBP primitive, use

\[
 \frac{\partial_A P+\partial_BQ}{\Delta^3}
 -3\frac{P\partial_A\Delta+Q\partial_B\Delta}{\Delta^4}.
\]

Degree-six tangent coefficients give 84 raw columns in the 55-dimensional
numerator space. Exact reduction at the fixed generic pivot fixture gives

| span | rank |
| --- | ---: |
| tangent | 46 |
| tangent plus `J,M_x1,M_x2` | 49 |
| tangent plus masters and `I29` | 49 |

Thus `I29` requires no new transcendental master.

The three master coefficients are rational functions with common denominator
\(\lambda^5\), where

\[
 \lambda=x_1^2+x_2^2+x_3^2-2x_1x_2-2x_1x_3-2x_2x_3.
\]

Their numerator degrees are respectively 7, 8 and 8. A 45-point exact
unisolvent reconstruction is checked on five independent holdout points and
then promoted by a full symbolic 55-row relative-IBP identity. The latter is
the proof step: interpolation alone is not used as a nontriviality or
membership certificate.

## Corner flux

All potentially divergent corner jets cancel. In the canonical primitive the
three finite corner numerators are linear. Only the rational moments

\[
 \int_0^1\frac{dt}{(a+(b-a)t)^3}
 =\frac{a+b}{2a^2b^2},
 \qquad
 \int_0^1\frac{t\,dt}{(a+(b-a)t)^3}
 =\frac1{2ab^2}
\]

occur. The total flux is therefore rational and symmetric. After replacing
the derivative masters by the certified scalar-triangle differential system,
the result has the form

\[
 A_J(x)J_\triangle
 +A_{21}(x)\log\frac{x_2}{x_1}
 +A_{31}(x)\log\frac{x_3}{x_1}
 +R(x),
\]

with exact rational coefficients. All six permutations act trivially on the
complete function after the two logarithmic coordinates are transformed.

At the symmetric point,

\[
 I_{29}(1,1,1)
 =-\frac{496}{6561}J_\triangle+\frac{1160}{6561},
\]

exactly reproducing the independent symmetric-simplex certificate.

## Replay

Fast stored-artifact tests:

```bash
PYTHONPATH=quantum-weyl python3 -m unittest \
  spectral.euclidean.tests.test_generic_background_ghost_n3_i29_integrated_function
```

Independent exact symbolic replay:

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_ghost_n3_i29_integrated_function
```

The producer is intentionally a slower publication-tier check because it
performs the exact unisolvent reconstruction and symbolic primitive solve:

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_ghost_n3_i29_integrated_function --check
```

## Remaining gate

The local ghost `n=3` integration problem is complete. The next
coefficient-bearing gate is assembly with the same-gauge generic-background
physical fourth-order Hessian into the five parity-even repository carriers.
The primed Green/spectral finite rows, parity-odd derivative sector, complete
renormalized `Gamma1/Q1`, residual transfer and every Lorentzian/state claim
remain separate and open.
