# BT separable lowest-mode curvature theorem

Certificate: `REVERSE_PHYSICS_BT_EUCLIDEAN_SEPARABLE_LOWEST_MODE_CURVATURE_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle: `SCOPED_THEOREM_PROVED`

## Result

On every periodic four-dimensional lattice with side length $L\geq4$, the
BT action retains at least two thirds of the free lowest-mode curvature on
every separable background

\[
                    \psi(t,x)=a_t+b_x.
\]

For $h_t=\cos(2\pi t/L+\alpha)$,
$\omega_L=4\sin^2(\pi/L)$, and $N=L^4$,

\[
       \operatorname{Hess}A_\psi[h,h]\geq\frac{N\omega_L^2}{3}.
\]

Since the free value is $N\omega_L^2/2$, the retained fraction is exactly
$2/3$. For $S_\lambda(\phi)=A(\lambda\phi)/\lambda^2$, the coupling
cancels from this Hessian. One-dimensional Brascamp--Lieb therefore gives

\[
             \operatorname{Var}(t\mid\psi=a+b)
             \leq\frac{3}{N\omega_L^2}.
\]

This has the exact volume scaling required of a lowest Fourier coefficient,
but only on the separable-background sector. It is not an estimate under the
full interacting Gibbs measure.

## Proof

Put $x_t=e^{u_t}$, $d_t=h_{t+1}-h_t$, and
$e_t=d_t-d_{t-1}=-\omega_Lh_t$. Direct differentiation of the one-cycle
action gives

\[
 H=2\sum_t(x_t^2+x_t^{-2}-x_t-x_t^{-1})d_t^2
   +\sum_t\frac{x_t}{x_{t-1}}e_t^2.
\]

The scalar inequalities

\[
 2\cosh(2u)-2\cosh u\geq3u^2,
 \qquad e^v\geq1+v
\]

follow from two derivatives and tangency at zero. Completing the square in
each $u_t$ leaves a relative loss

\[
 \frac{\omega_L^2\cos^2(\pi/L)}6
 =\frac83\sin^4(\pi/L)\cos^2(\pi/L)\leq\frac13.
\]

The last inequality uses $L\geq4$. Separability makes the temporal second
variation independent of the spatial point. The remaining spatial factor is
nonnegative because every undirected edge pairs as
$e^\delta+e^{-\delta}-2\geq0$.

## Exact limit of the method

The spatial argument is not valid for correlated backgrounds. The certificate
contains a centered, lowest-mode-orthogonal $4\times4$ power-of-two fixture,
repeated over the other two axes, for which the exact correlation remainder is

\[
                     -\frac{456623975}{262144}<0.
\]

The complete Hessian of this fixture is still positive; the fixture obstructs
only the proposed sign lemma. It identifies spatial--temporal correlation as
the missing term that a successful all-background or annealed proof must
absorb.

## Boundaries and next gate

This result does not establish an all-background recentered variance, an
annealed bound on the moving fiber center, the normalized interacting
lowest-mode moment, an interacting $H^{-1}$ estimate, tightness, or a
continuum measure. It has no Born, Krein, or `LORENTZIAN-CAUSAL` consequence.

The next calculation is an exact correlation-absorption inequality for the
complete Hessian, or an exact periodic counterfamily for that complete
curvature. Either outcome must then be combined with an annealed center bound.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_separable_lowest_mode_curvature.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_separable_lowest_mode_curvature.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_separable_lowest_mode_curvature
```
