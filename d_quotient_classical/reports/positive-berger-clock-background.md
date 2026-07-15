# Positive Berger-sphere clock background

## Outcome

There is an exact open family of smooth, compact, non-conformally-flat
backgrounds carrying a positive rotating conformal-scalar clock.

Take

\[
g=-dt^2+a^2(\sigma_1^2+\sigma_2^2)+c^2\sigma_3^2,
\qquad q=\frac{c^2}{a^2},
\]

on \(\mathbb R\times S^3\), and two standard-sign real conformal scalars

\[
T_1=\rho\cos(\omega t),
\qquad
T_2=\rho\sin(\omega t).
\]

Their target metric is positive,

\[
dT_1^2+dT_2^2=d\rho^2+\rho^2d\theta^2,
\]

and the phase \(\theta=\omega t\) has everywhere timelike gradient.  The raw
temporal-diffeomorphism/Weyl incidence determinant is

\[
\det M=\rho^2\omega\ne0.
\]

## Exact Bach-source match

In the orthonormal Berger frame the nonzero independent Bach components are

\[
\begin{aligned}
B_{00}&=\frac{(a^2-c^2)^2}{6a^8},\\
B_{11}=B_{22}&=\frac{(a^2-c^2)(a^2-3c^2)}{6a^8},\\
B_{33}&=\frac{(a^2-c^2)(5c^2-a^2)}{6a^8}.
\end{aligned}
\]

For the field equation \(\alpha_BB_{\mu\nu}=T_{\mu\nu}\), the complete
positive branch is

\[
\frac{5-\sqrt{21}}2<q<\frac14,
\]

\[
\rho^2=\frac{2\alpha_B(1-4q)}{a^2},
\qquad
\omega^2=\frac{q}{4a^2(1-4q)},
\]

\[
\lambda=-\frac{q^2-5q+1}{6\alpha_B(1-4q)^2}>0.
\]

The scalar equations and all three independent metric equations vanish
coefficientwise.

## Health of the clock matter

Throughout the interval, the scalar kinetic metric is positive and the
quartic potential is bounded below.  The energy density and principal
pressures are

\[
\varepsilon=\frac{\rho^2(1-q)^2}{12a^2(1-4q)},
\]

\[
p_h=\frac{\rho^2(1-q)(1-3q)}{12a^2(1-4q)},
\qquad
p_v=\frac{\rho^2(1-q)(5q-1)}{12a^2(1-4q)}.
\]

They are positive and obey \(\varepsilon\geq p_h,p_v\).

## Rational fixture

A compact exact representative is

\[
a=1,\quad q=\frac9{40},\quad \alpha_B=5,\quad \rho=1,
\quad \omega=\frac34,\quad \lambda=\frac{119}{480}.
\]

It satisfies the scalar equation and all independent Bach-source equations
over the rationals.

## Remaining gate

This is the first standard-sign, bounded-potential clock background to pass
the coupled field equations.  It is not yet a charge theorem.  The next gate
is

```text
FULL_BERGER_CLOCK_CHARGE_AND_BV_AUDIT
```

which must derive the normalized covariant \(D\) charge, the perturbative
phase space, the support-local all-row BV contraction, and causal propagation.
No `D_GAUGE` verdict is assigned before that audit.
