# Berger nonlinear clock temporal field chart through F3

The physical clock fixes the coordinate retraction rather than leaving a free chart choice:

```text
y0 = x0 + Theta(x),  yi = xi,
s = x0-y0 = -Theta + Theta Theta_0 - Theta Theta_0^2 - Theta^2 Theta_00/2 + O(4).
```

Substitution in `s+Theta(y0+s,y)=0` has zero residual through total cubic field degree. The inverse Jacobian has `K00=1/(1+Theta_0)` and `K0i=-K00 Theta_i`. Pulling back the linearly dressed raw metric

```text
g_raw = eta + H - B(Theta),  B00=2 e0 Theta,  B0i=ei Theta
```

cancels every linear correction and gives exactly 36 quadratic plus 96 cubic metric-jet monomials. The generated certificate serializes them as factorial-convention `F2/F3` components with ordered Berger PBW derivative labels.

This is deliberately a field-chart subgate. Its differential Jacobian contains derivatives, so the BV cotangent lift must be obtained from the signed formal adjoint with integration by parts. Until that is certified, the full clock map and scalar apparatus interactions remain fail-closed.
