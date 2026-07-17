# Classical minimal-BV antifield export V2

The export is pinned to classical foundation commit `3e15eafa5e0bb8cbc3eb1d2ad79a669c54ce9cca` and
contains the six minimal Diff x Weyl generators, twelve derived covariant
Koszul--Tate/Lie atoms, and exact rational `delta`, `gamma`, and total `Q`
rows.  The independently executable identities are

```text
delta^2 = 0,
delta gamma + gamma delta = 0,
Q = delta + gamma,
Q^2 = 0.
```

The Bach Euler coordinate is

```text
E_g^{mu nu} = -2 sqrt(abs(g)) B^{mu nu}
```

for `S=-integral sqrt(abs(g)) C^2`.  The ghost-antifield rows encode

```text
delta xi_star_mu = -2 nabla_nu g_star^{nu}_mu,
delta omega_star = 2 g_mu_nu g_star^{mu nu},
```

and their squares vanish by the Diff and Weyl Noether identities.  Lie atoms
are complete tensor-density Lie derivatives, not scalar placeholders.

## Boundary

This is the executable minimal-BV/Koszul--Tate interface requested by the
quantum receiver.  It is designed to merge with the existing AFN0 curvature
and lower-form bases.  It does not itself enumerate those AFN0 bases, compute
`H^{0,4}(s|d)` or `H^{1,4}(s|d)`, determine an anomaly coefficient, restore
the QME, or make a Lorentzian or quantum claim.
