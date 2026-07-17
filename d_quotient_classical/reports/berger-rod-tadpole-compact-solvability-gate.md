# Berger rod-tadpole compact solvability gate

## Verdict

The stationary-homogeneous constant-mode screen is **solvable**, but the
scientific compact-background verdict remains `INPUT_BLOCKED`.

The perturbative equation is

\[
q_1\Phi_2=-q_0^{\rm rod},\qquad
\pi_{\operatorname{coker}q_1}q_0^{\rm rod}=0.
\]

Using the certified retained constant metric Hessian and the canonical field
order `h_hat_star_00, h_hat_star_01, h_hat_star_02, h_hat_star_03, h_hat_star_11, h_hat_star_12, h_hat_star_13, h_hat_star_22, h_hat_star_23, h_hat_star_33`, the conditional homogeneous source is

```text
['3/2', '0', '0', '0', '-1/2', '0', '0', '-1/2', '0', '-1/2']
```

The Hessian and augmented ranks are both 7. Its three adjoint-kernel
pairings are `['0', '0', '0']`, and the canonical exact
primitive (free shift entries fixed to zero) is

```text
Phi2 = ['496/63', '0', '0', '0', '-32/7', '0', '0', '-32/7', '0', '-256/63']
```

The exact residual `H Phi2 + q0` is
`['0', '0', '0', '0', '0', '0', '0', '0', '0', '0']`. Therefore there is no
stationary-homogeneous Taub obstruction from the diagonal rod stress shape.

## Why this is not yet the compact verdict

The apparatus export contains local detector-chart Cauchy germs with unit
Jacobian and invokes local normally-hyperbolic existence. It does not export
global rod fields on the compact Berger slice, their full order-
\(\epsilon_R^2\) Euler source, or an exact projector onto the adjoint
kernel of the full compact operator. A local stress matrix cannot be inserted
as though it were that global source.

The next input must therefore provide the global `q0^rod`, its harmonic or
support decomposition, and the normalized compact adjoint-kernel
witnesses. Only then can every Taub pairing be evaluated. If one is nonzero,
the combined clock/coupling/apparatus stress must cancel it; if all vanish,
construction of the perturbative branch may proceed.

This certificate is `LOCAL-ALGEBRAIC` and `REDUCED-MODE`. It does not certify
the backreacted rod branch, the 78-row unary complex, a Lorentzian causal
extension, nonlinear apparatus brackets, or a quantum result.
