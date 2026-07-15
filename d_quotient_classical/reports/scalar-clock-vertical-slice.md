# Scalar-clock vertical-slice certificate

## Result

For one real conformally coupled scalar on the unit conformal cylinder,

\[
S_T=-\frac12\int\sqrt{-g}\left((\nabla T)^2+\frac16RT^2\right),
\qquad R=6,
\]

the Weyl-invariant homogeneous variable \(\chi=aT\) obeys

\[
\ddot\chi+\chi=0,
\qquad
H_D^T=\frac12(\dot\chi^2+\chi^2).
\]

Consequently, every nontrivial orbit has local monotone clock charts, but no
global monotone chart.  Each chart must declare both an interval and the sign
of \(\dot\chi\).

The local clock mechanics is exact: the certificate contains explicit
complete observables on a finite negative-sign E-like fixture, together with
their nonzero reduced Poisson bracket.  This proves that the relational
construction itself is not the obstruction.

## Exact-cylinder obstruction

The improved homogeneous stress tensor satisfies

\[
\rho=\frac{\dot\chi^2+\chi^2}{2\operatorname{Vol}(S^3)},
\qquad p=\frac{\rho}{3}.
\]

The exact cylinder is conformally flat, hence its Bach tensor vanishes.  The
coupled metric equation therefore excludes every nonzero homogeneous scalar
clock on that background.  The only compatible homogeneous background is
\(\bar T=0\), but at that background

\[
\delta_{(\xi,\sigma)}T
=\xi^0\dot{\bar T}-\sigma\bar T=0,
\]

so the linearized scalar cannot fix \(D\).

Thus

```text
SCALAR_CLOCK_VERTICAL_SLICE = OBSTRUCTED_ON_EXACT_VACUUM_CYLINDER
```

No `D_GAUGE` or `D_CHARGED` verdict is assigned to a coupled scalar-clock
phase space that has not been constructed.  The positive test-field charge
is retained only as a scoped vertical witness.

## Next admissible gate

One must now choose and certify one of:

1. a genuinely backreacted scalar--pure-Weyl background;
2. a Weyl-invariant composite or two-field clock;
3. a separately declared reference-matter clock model.

The result does not address interacting, boundary, or quantum stability.
