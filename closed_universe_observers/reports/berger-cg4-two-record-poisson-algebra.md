# C-G4 two-record classical Poisson algebra

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`.

For C-G4 coordinates `F=x F_c+y F_s`, detector `D0` reads the `e01`
component and `D1` reads `e02`.  With normalized detector moments

```text
S_a=integral rho_a sin(beta t),  C_a=integral rho_a cos(beta t),
```

the memory records satisfy

```text
(m0,m1)^T = beta [[-S0,-C0],[C1,-S1]] (x,y)^T.
```

Its determinant is `beta^2(S0 S1+C0 C1)`.  On the actual windows this is a
strictly positive double average of `cos(beta(t-s))`, because
`beta|t-s| <= 7 sqrt(10)/36 < pi/2`.  Hence the two memories are coordinates
on the scoped C-G4 phase plane.

Transporting `{x,y}=-1/(32 pi^2)` gives

```text
{m0,m1}=-beta^2(S0 S1+C0 C1)/(32 pi^2) != 0.
```

Thus the localized polynomial algebra in `m0,m1` is closed under ordinary
products and this constant Poisson bracket.  The inverse detector matrix
makes every C-G4 quadrature linear in the memories and its relational
Hamiltonian/redshift energy quadratic in them.

This is the exact two-phase coefficientwise algebra.  It is not the full
apparatus Dirac bracket, a complete harmonic signal algebra, a localized
emitter theorem, finite-parameter Green hyperbolicity, or a quantum algebra.
