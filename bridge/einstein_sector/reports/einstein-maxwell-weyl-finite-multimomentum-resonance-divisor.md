# Exact finite multi-momentum resonance divisor

Let `rho=(2*pi/L)^2`, so a compact momentum is `k_n=n*sqrt(rho)`.  For two
signed momentum carriers with positive offsets `A,B`, a target offset `C`, and
signed temporal product `tau`, the unsquared shell equation is

```text
2*tau*sqrt((n1^2*rho+A)(n2^2*rho+B))
  = 2*n1*n2*rho + C-A-B.
```

Squaring cancels the quadratic term in `rho` exactly.  The resulting divisor
is linear:

```text
4*(n1^2*B+n2^2*A-n1*n2*(C-A-B))*rho
  +4*A*B-(C-A-B)^2 = 0.
```

Thus each nonidentity channel on a declared finite harmonic carrier has at
most one positive algebraic circumference candidate, followed by the explicit
sign test that removes spurious squared roots.  The total exceptional set is
finite.  If both the linear and constant coefficients vanish, the channel is
identity-resonant for every circumference and remains an explicit source-
matrix gate.

The formula reproduces the prior `K=0` and `K=2k` one-fibre divisors and the
universal tuned `q-minus x q-minus -> p-extra(L=2ell)` family.  It computes no
quadratic source coefficient.  Consequently it is a shell-arithmetic theorem,
not a bounded-extension or obstruction theorem; zero-frequency Taub rows,
identity channels, infinite momentum support and causal propagation remain
fail-closed.
