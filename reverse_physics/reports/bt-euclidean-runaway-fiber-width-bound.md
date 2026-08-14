# BT Euclidean runaway-fiber width bound

## Result

Certificate
`REVERSE_PHYSICS_BT_EUCLIDEAN_RUNAWAY_FIBER_WIDTH_BOUND_V1`
proves a positive statement about the exact family used by the preceding
conditional-mass escape obstruction.  On the periodic $6^4$ lattice, put

\[
 a=(-1,-1,1,-3,3,1),\qquad h=(2,1,-1,-2,-1,1)
\]

and

\[
 \psi_m(u)=\log(2)(4ma+uh),\qquad m\geq2.
\]

Although the conditional center on this family escapes to the left, the
conditional law does not become broad.  If

\[
 q_m(u)=Z_m^{-1}\exp[-1350A_m(u)],
\]

then

\[
 \operatorname{Var}_{q_m}(u)
 \leq \frac{2}{77625(\log2)^2}
 \leq \frac{8}{77625}
\]

for every integer $m\geq2$.  The centering here is the conditional mean.
Moreover, its conditional mean satisfies

\[
                    \mathbb E_{q_m}[u]<-\frac m2.
\]

The theorem is uniform in $m$ on this family only; arbitrary orthogonal
backgrounds remain open.

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

## Exact curvature calculation

Write $R=2^{4m}\geq256$ and $z=2^u>0$.  Direct differentiation of the
six-site action gives

\[
 A_m''(u)=(\log2)^2K_m(z),
\]

where the twenty-three bivariate Laurent monomials collect into

\[
 K_m(z)=16R^4z^{-4}+Az^{-2}-Bz^{-1}-Cz+Dz^2+16R^{-4}z^4
\]

with

\[
\begin{aligned}
 A&=2R^4-12R^2+2+2R^{-8}+2R^{-12},\\
 B&=R^2+1+2R^{-4}+2R^{-6},\\
 C&=2R^6+2R^4+2+2R^{-2}-R^{-6}-R^{-8},\\
 D&=2R^{12}+4R^{10}+2R^8+2-16R^{-2}+2R^{-4}.
\end{aligned}
\]

For $R\geq256$, exact power comparisons give

\[
 A\geq R^4,
 \quad 0<B\leq2R^2,
 \quad 0<C\leq3R^6,
 \quad D\geq R^{12}.
\]

Completing the two middle squares and applying AM--GM to the outer pair gives

\[
\begin{aligned}
 Az^{-2}-Bz^{-1}&\geq-1,\\
 Dz^2-Cz&\geq-\frac94,\\
 16(R^4z^{-4}+R^{-4}z^4)&\geq32.
\end{aligned}
\]

Therefore $K_m(z)\geq115/4$ at every point of every declared fiber.  The
spatial replication and coupling give the exact inverse-temperature factor
$216/(2/5)^2=1350$.  The one-dimensional Brascamp--Lieb variance inequality
then gives

\[
 \operatorname{Var}_{q_m}(u)
 \leq\frac{1}{1350(\log2)^2(115/4)}
 =\frac{2}{77625(\log2)^2}.
\]

The elementary integral bound

\[
 \log2=\int_1^2\frac{dx}{x}\geq\frac12
\]

turns this into the rational bound

\[
                 \operatorname{Var}_{q_m}(u)\leq\frac{8}{77625}.
\]

## Interpretation

The predecessor theorem showed

\[
 \mathbb E_{q_m}[u^2]\geq m^2(1-2^{-m}).
\]

The present theorem shows that this growth cannot be blamed on increasing
conditional noise.  The predecessor also gives
$q_m\{u<-m\}\geq1-2^{-m}$.  If the conditional mean were at least
$-m/2$, this event would force

\[
 \operatorname{Var}_{q_m}(u)
 \geq(1-2^{-m})\frac{m^2}{4}\geq\frac34,
\]

contradicting $8/77625<3/4$.  Hence
$\mathbb E_{q_m}[u]<-m/2$: on the same backgrounds the packet stays uniformly
narrow while its center moves to minus infinity.  Consequently the important
unresolved term in the total-variance decomposition is the Gibbs-weighted
motion of conditional centers.  A proof that controls only within-fiber
fluctuations cannot establish the integrated lowest-mode moment.

This conclusion also sharpens the foundations interface.  Finite exact
algebra and a one-dimensional analytic inequality decide the behavior of the
declared family.  They do not select a limiting state, construct a Born rule,
or provide a Krein or Lorentzian reconstruction.  Those questions still
depend on the missing annealed and volume-uniform limit objects.

## Discovery rail

A bounded exploratory search on a $6\times2\times2\times2$ periodic cell
tested genuinely time--space-correlated backgrounds.  Random scans and
gradient descent found no negative lowest-mode curvature and relaxed toward a
spatially constant period-three profile.  This is noncertifying evidence only:
it motivated the exact-family calculation and is not used to claim an
all-background curvature theorem.

## Verification

Run sequentially under a 500000 KiB virtual-memory ceiling:

```text
python3 reverse_physics/bt_euclidean_runaway_fiber_width_bound.py --check
python3 reverse_physics/verify_bt_euclidean_runaway_fiber_width_bound.py
python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_runaway_fiber_width_bound
```

The producer uses exact bivariate Laurent arithmetic.  The independent rail
reconstructs the six collected coefficients, differentiates the action
site-by-site on separate fixtures, checks the universal coefficient
comparisons, and rejects mutations of the curvature, variance normalization,
provenance, and claim boundary.

## Does not establish

This result does not establish an all-background recentered variance bound,
an annealed center moment, an integrated lowest-mode moment, an interacting
$H^{-1}$ estimate, tightness, a continuum Euclidean measure, a Born rule, a
Krein reconstruction, or anything `LORENTZIAN-CAUSAL`.
