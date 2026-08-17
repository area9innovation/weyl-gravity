# BT torus quadratic virial-density gate

Certificate:
REVERSE_PHYSICS_BT_EUCLIDEAN_TORUS_QUADRATIC_VIRIAL_DENSITY_GATE_V1

Dependency tags: LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL

## Result

A quadratic correction to the reciprocal-edge virial majorant lowers the
action-density ceiling for every possible collapsing BT four-torus family
from \(11\) to \(272/29\).  On a finite 8-regular undirected graph, use

\[
 s_x=\sum_{y\sim x}e^{\psi_y-\psi_x},\qquad
 r_x=s_x-8,\qquad
 A={1\over2}\sum_xr_x^2,
\]

and let \(g=\nabla_\psi A\).  The exact new global inequality is

\[
 \boxed{
 \langle\psi,g\rangle
 \geq {29\over16}A-17N
 ={29\over16}\left(A-{272\over29}N\right).}
\]

Consequently, on \(T_L^4\), for every \(0<\epsilon\leq32\),

\[
 \boxed{
 A\geq\left({272\over29}+\epsilon\right)L^4
 \quad\Longrightarrow\quad
 {Q\over\omega_L^2}\geq
 {841\epsilon^2\over8388608\pi^4},}
 \qquad
 Q={\|g\|_2^2\over\|r\|_2^2}.
\]

Every sequence with \(Q/\omega_L^2\to0\) must therefore satisfy

\[
 \boxed{
 \limsup_{L\to\infty}{A\over L^4}\leq{272\over29},
 \qquad
 \limsup_{L\to\infty}{W^2\over L^4}\leq{544\over29}.}
\]

Numerically, these coefficients are approximately \(9.37931\) and
\(18.75862\), but no floating-point computation enters the proof or
certificate.

This is not the all-field theorem.  The action-density-at-most-\(272/29\)
nonseparable sector remains open.

## The quadratic scalar majorant

The predecessor proved that the vertex defect \(r^2-rt\) is bounded at fixed
\(s\) by

\[
 \Phi_-(s)=(8-s)^2+(8-s)s\log s,\qquad 0<s<8,
\]

and

\[
 \Phi_+(s)=(s-8)^2-(s-8)s\log(s/8),\qquad s\geq8.
\]

The new pointwise inequality is

\[
 \boxed{
 \Phi(s)+{41\over8}(s-8)-{3\over32}(s-8)^2\leq17
 \qquad(s>0).}
\]

Unlike the preceding affine majorant, this spends a controlled fraction of
the global residual square.  Because \(3/32<1\), most of the coercive
quadratic term survives after summation.

### Negative-residual branch

For \(0<s<8\), subtracting \(17\) from the left side of the claimed
majorant gives

\[
 s f(s),\qquad
 f(s)=(8-s)\log s+{29\over32}s-{75\over8}.
\]

Its derivatives are

\[
 f'(s)={8\over s}-\log s-{3\over32},
 \qquad
 f''(s)=-{s+8\over s^2}<0.
\]

Thus \(f\) has one maximizer \(s_*\in(0,8)\).  Put

\[
 q={961\over200},\qquad
 R={8\over q}-{3\over32}={48317\over30752}.
\]

The exact sixth-order Taylor partial sum obeys

\[
 \sum_{n=0}^{6}{R^n\over n!}>{961\over200}.
\]

Every omitted exponential coefficient is positive, so
\(e^R>q\), hence \(\log q<R\) and \(f'(q)>0\).  Therefore \(s_*>q\).
At the stationary point, substituting
\(\log s_*=8/s_*-3/32\) gives

\[
 f(s_*)=s_*+{64\over s_*}-{145\over8}.
\]

The function \(s+64/s\) decreases on \((0,8)\), and exact rational
arithmetic gives

\[
 q+{64\over q}={3483521\over192200}<{145\over8}.
\]

Consequently \(f(s_*)<0\), proving the negative branch.

### Positive-residual branch

For \(s\geq8\), write \(y=s/8-1\geq0\).  The majorant is equivalent to

\[
 H(y)=17-41y-58y^2+64y(1+y)\log(1+y)\geq0.
\]

Here

\[
 H'(y)=-41-52y+64(1+2y)\log(1+y),
\]

and

\[
 H''(y)=76+128\log(1+y)-{64\over1+y}\geq12.
\]

Thus \(H\) is strictly convex.  Its unique minimum \(y_*\) lies below
\(53/80\).  Indeed, at \(q=53/80\), positivity of \(H'(q)\) reduces to

\[
 \log{133\over80}>{503\over992}.
\]

With \(z=53/213\), the ratio is
\((1+z)/(1-z)=133/80\), and the positive \(\operatorname{atanh}\) series
gives the exact lower bound

\[
 \log{133\over80}
 =2\operatorname{atanh}z
 >2\left(z+{z^3\over3}\right)
 >{503\over992}.
\]

At the stationary point \(H'(y_*)=0\), direct substitution yields

\[
 H(y_*)={P(y_*)\over1+2y_*},\qquad
 P(y)=17+34y-47y^2-64y^3.
\]

Because \(P'(y)=34-94y-192y^2\) is strictly decreasing, \(P\) has no
interior minimum on \([0,53/80]\).  Its endpoint values are

\[
 P(0)=17,
 \qquad
 P(53/80)={9177\over32000}>0.
\]

Therefore \(H(y_*)>0\), proving the positive branch.

## Global graph inequality

The reciprocal-edge identity from the predecessor is

\[
 \sum_x(s_x-8)
 =\sum_{\{x,y\}}\left(
 {\Omega_y\over\Omega_x}+{\Omega_x\over\Omega_y}-2\right)\geq0.
\]

Summing the quadratic majorant gives

\[
 \sum_x(r_x^2-r_xt_x)
 \leq17N-{41\over8}\sum_xr_x+{3\over32}\sum_xr_x^2
 \leq17N+{3\over32}\sum_xr_x^2.
\]

Since \(\langle\psi,g\rangle=\sum_xr_xt_x\) and
\(\sum_xr_x^2=2A\), this is precisely

\[
 \langle\psi,g\rangle\geq{29\over16}A-17N.
\]

## Four-torus consequence

Write \(x=A/N\), \(N=L^4\).  In the bounded-density branch
\(272/29<x<64\), the predecessor's exact range estimate gives
\(\|\psi\|_2<4N\).  Cauchy--Schwarz and
\(\|r\|_2^2=2xN\) then yield

\[
 NQ\geq{841(x-272/29)^2\over8192x}
 \geq{841(x-272/29)^2\over524288}.
\]

Using \(\omega_L^2\leq16\pi^4/N\),

\[
 {Q\over\omega_L^2}
 \geq{841(x-272/29)^2\over8388608\pi^4}.
\]

Above \(x=64\), the already-certified larger-action branches give
\(Q/\omega_L^2\geq1/(8\pi^4)\).  The latter dominates the displayed
fixed-margin coefficient for \(0<\epsilon\leq32\), because
\(841\cdot32^2/8388608=841/8192<1/8\).

Collapse forces the positive part of \(A/L^4-272/29\) to vanish.  Finally,
the predecessor's exact contrast estimate

\[
 {W\over L^2}\leq{8\over L^2}+\sqrt{{2A\over L^4}}
\]

gives the contrast-square coefficient \(544/29\).

## What remains

Every possible counterfamily is now confined to

\[
 A\leq\left({272\over29}+o(1)\right)L^4,
 \qquad
 W\leq\left(\sqrt{{544\over29}}+o(1)\right)L^2.
\]

The result does not establish optimality of the scalar majorant, a lower
bound in this remaining low-action sector, the all-field torus scaled
Polyak--Lojasiewicz inequality, Witten/Poincare coercivity, the interacting
\(H^{-1}\) moment, a continuum measure, Born or Krein reconstruction, or
anything LORENTZIAN-CAUSAL.

The next aligned step is a superlevel/coarea decomposition inside the
remaining sector.  If it cannot provide uniform coercivity, its bottleneck
profile must be converted into an explicit nonseparable polynomial-contrast
family rather than recorded as another method failure.

## Verification

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_torus_quadratic_virial_density_gate.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_torus_quadratic_virial_density_gate.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_torus_quadratic_virial_density_gate

The exact command timings, memory ceilings, affected predecessor check,
planning import, paper claim-map/PDF checks, and higher-tier disposition are
stored in the machine certificate.
