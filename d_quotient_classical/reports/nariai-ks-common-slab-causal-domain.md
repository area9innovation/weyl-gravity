# Common causal slabs for the exact Kantowski--Sachs family

The quotient `a=b'/epsilon` is regularized by

\[
 b=1+\epsilon y,\qquad b'=\epsilon a.
\]

The exact Einstein equation becomes the smooth first-order system

\[
 y'=a,\qquad
 a'=\frac{2y+\epsilon(y^2-a^2)}{2(1+\epsilon y)},
\]

with `y(0)=-epsilon/6` and `a(0)=1`.  At `epsilon=0` its solution is
`y=sinh(t)`, `a=cosh(t)`.  Standard smooth dependence of ODE solutions on
parameters therefore proves that, for every finite `T`, some `delta_T>0`
gives a unique exact solution on `(-T,T)` for every
`|epsilon|<delta_T`, with both scale factors positive and uniformly bounded
above and below.

Consequently every

\[
 g_\epsilon=-dt^2+a_\epsilon^2d\chi^2+b_\epsilon^2d\Omega_2^2
\]

on that open slab is globally hyperbolic with compact Cauchy slices.  The
uniform lower spatial bound supplies one wider reference cone containing all
the `g_epsilon` causal cones.  This makes a common causal support category
legitimate.

This is a domain theorem, not the causal-transfer theorem.  The next input is
the coefficient-complete six-block geometric export and the exact compressed
metric endpoint required by the typed biwave theorem.
