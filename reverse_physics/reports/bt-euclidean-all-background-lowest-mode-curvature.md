# All-background BT lowest-mode curvature

Certificate: `REVERSE_PHYSICS_BT_EUCLIDEAN_ALL_BACKGROUND_LOWEST_MODE_CURVATURE_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle: `VOLUME_UNIFORM_CONDITIONAL_ESTIMATE_PROVED`

## Result

The signed time--space correlation term can be absorbed. On every periodic
four-dimensional lattice with $L\geq4$, for every field background and every
real phase of a lowest axial Fourier mode,

\[
 \operatorname{Hess}A_\psi[h,h]\geq\frac{2}{9}N\omega_L^2,
 \qquad \omega_L=4\sin^2(\pi/L).
\]

Consequently, for every orthogonal background $\eta$, the normalized
one-dimensional conditional law along $\eta+t h$ satisfies

\[
          \operatorname{Var}(t\mid\eta)
          \leq\frac{9}{2N\omega_L^2}.
\]

The estimate is uniform in the background, volume, phase, axis, and nonzero
coupling. It has the correct $N^{-1}\omega_L^{-2}$ scaling. This completes
the recentered-width half of the conditional-center split. The annealed motion
of those centers remains uncontrolled.

## Plaquette absorption

At one temporal edge and one spatial edge, let $U,V>0$ be the forward
temporal weights at the two spatial endpoints and let $A>0$ be the spatial
weight on the earlier slice. Expanding the action Hessian and distributing the
degree-eight linear terms over the six spatial edges gives

\[
 E=\frac13Q+C-\frac43S,
\]

where

\[
\begin{split}
 Q&=U^2+V^2+U^{-2}+V^{-2},\\
 S&=U+V+U^{-1}+V^{-1},\\
 C&=UA+V/A+VA/U^2+U/(V^2A).
\end{split}
\]

The new local inequality is

\[
 E\geq\frac15\{f(U)+f(V)\},
 \qquad f(z)=z^2+z^{-2}-z-z^{-1}.
\]

To prove it, write $U=pr$, $V=p/r$,
$P=p+p^{-1}\geq2$, and $R=r+r^{-1}\geq2$. AM--GM minimizes the
$A$-dependent terms and reduces the claim to

\[
 2(P^2-2)(R^2-2)+30\sqrt{P^2+R^4-4R^2}\geq17PR.
\]

With $Y=R^2-2$, the derivative of the left-minus-right side with respect to
$P$ is bounded below by

\[
                       8Y+60/Y-17R.
\]

For $R\geq3$, its first and last terms already give at least $5$. For
$2\leq R\leq3$, multiplication by $Y$ and $R=2+s$ gives the degree-four
polynomial with power coefficients

\[
                    (24,-42,58,47,8).
\]

Its Bernstein coefficients on $0\leq s\leq1$ are

\[
              \left(24,\frac{27}{2},\frac{38}{3},
                         \frac{133}{4},95\right),
\]

all positive. The reduced expression is therefore increasing in $P$. At
$P=2$ it equals $34(R-2)(R+1)\geq0$.

## Completion along the time cycle

Summing the plaquette inequality over the six spatial edges incident to each
site retains $6f/5$ on every temporal line. The ungrouped temporal-neighbor
cross term is also nonnegative. Thus

\[
 \operatorname{Hess}A[h,h]\geq
 \sum_{\text{spatial lines}}\left[
 \frac65\sum_t f(e^{u_t})d_t^2
 +\sum_t e^{u_t-u_{t-1}}e_t^2\right].
\]

Using $f(e^u)\geq3u^2$, $e^v\geq1+v$, and completing the square leaves a
relative loss of at most

\[
 \frac5{18}\omega_L^2\cos^2(\pi/L)\leq\frac59.
\]

Therefore at least $4/9$ of the free curvature
$N\omega_L^2/2$ survives, proving the displayed $2/9$ constant.

## Meaning and remaining gate

The earlier exact runaway family showed that raw conditional moments can
escape because their centers move. The present theorem proves that no
orthogonal background can make the packet around its own center arbitrarily
wide. The only missing part of the lowest-mode marginal is now the
Gibbs-weighted second moment of those unique centers.

This result does not establish that annealed center bound, the integrated
lowest-mode moment, an interacting $H^{-1}$ estimate, tightness, or a
continuum measure. It has no Born, Krein, or `LORENTZIAN-CAUSAL` consequence.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_all_background_lowest_mode_curvature.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_all_background_lowest_mode_curvature.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_all_background_lowest_mode_curvature
```
