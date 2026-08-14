# BT annealed-center score reduction

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_CENTER_SCORE_REDUCTION_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle: `EXACT_REDUCTION_PROVED_WITH_FINITE_VOLUME_DIAGNOSTIC`

## Result

The all-background curvature theorem reduces the missing lowest-mode estimate
to one explicit nonlinear score bound. Let

\[
 V_\eta(t)=S_\lambda(\eta+t h),\qquad
 \kappa_L=\frac29N\omega_L^2,
\]

and let $m(\eta)$ be the unique solution of $V_\eta'(m)=0$. If $\nu$ is the
exact background marginal, then

\[
 m(\eta)^2\leq\frac{V_\eta'(0)^2}{\kappa_L^2}.
\]

Consequently the new sufficient target is

\[
 \mathbb E_\nu[V_\eta'(0)^2]
 \leq C_s N\omega_L^2.
\]

If this holds uniformly in $L$, then the exact evenness of the integrated
marginal and the conditional-width theorem give

\[
 \mathbb E_\mu[t^2]
 \leq\frac{27+81C_s}{2N\omega_L^2}.
\]

This would close the normalized lowest axial mode. The score estimate itself
is not proved here.

## Why the mode is the right center

For the normalized one-dimensional conditional law $q_\eta$, integration by
parts gives

\[
 \mathbb E_{q_\eta}[(T-m)V_\eta'(T)]=1.
\]

Strong monotonicity of the score gives

\[
 \mathbb E_{q_\eta}[(T-m)^2]\leq\kappa_L^{-1}.
\]

The conditional mean therefore lies within squared distance
$\kappa_L^{-1}$ of the mode, and the conditional variance has the same upper
bound. Thus controlling modes or controlling conditional means differs only
by another already-controlled width term.

Strong monotonicity between $0$ and $m$ also gives

\[
 |V_\eta'(0)|\geq\kappa_L|m|,
\]

which is the center-to-score reduction above.

## Exact obstruction to using the old ingredients alone

The present curvature theorem, half-period symmetry, and affine virial/action
density estimate do not logically imply center control without additional BT
structure. For $R>0$, consider

\[
 V_R(t,y)=\frac\kappa2(t-y)^2+\frac{y^2}{2R^2}.
\]

This is an even, positive-definite homogeneous quadratic potential. Every
$t$-fiber has curvature exactly $\kappa$, its conditional center is $y$, and

\[
 (t,y)\mathbin\cdot\nabla V_R=2V_R,
 \qquad \mathbb E[V_R]=1.
\]

Nevertheless $\mathbb E[m(y)^2]=R^2$ is arbitrarily large. At the exact
fixture $\kappa=2$, $R=5$, the Hessian determinant is $2/25$, conditional
variance is $1/2$, center variance is $25$, total $t$ variance is $51/2$,
and the zero-fiber score variance is $100$.

Independent centered unit-Gaussian spectator coordinates extend this example
to arbitrary dimension. The radial virial equality is preserved, the mean
action becomes proportional to dimension, and the center variance remains
arbitrarily selectable through $R$.

This counterexample is deliberately scoped. It proves that the named general
ingredients are insufficient as a matter of logic. It does not share every
BT locality or quartic-coercivity property and therefore does not obstruct a
model-specific BT score theorem.

## Finite-volume center diagnostic

The deterministic observation producer ran the already-audited independent
local Metropolis update at $\lambda=0.4$. For every retained field it removed
one lowest cosine coefficient, solved the monotone fiber-score equation by
bisection, and retained block sufficient statistics. These are binary64
observations, not an exact or statistically precise scaling result.

| $L$ | samples | $N\omega_L^2\,\mathbb E[m^2]$ | $\mathbb E[V_\eta'(0)^2]/(N\omega_L^2)$ | $\mathbb E[m^2]/\mathbb E[t^2]$ |
|---:|---:|---:|---:|---:|
| 4 | 400 | $0.03586\pm0.00438$ | $0.01006\pm0.00127$ | $0.01120\pm0.00405$ |
| 6 | 200 | $0.03997\pm0.00390$ | $0.01215\pm0.00120$ | $0.01965\pm0.00528$ |

The maximum residual in a solved mode equation was below $10^{-9}$. Both
dimensionless score and center combinations remain similar between the two
volumes, and the mode center contributes less than two percent of the raw
second moment in these chains. Autocorrelation, the two-volume range, and the
single sampling algorithm preclude a uniform or precision claim.

## Relation to the new perturbative result

[Anderson, Bateman, Herzog and Turok](https://arxiv.org/abs/2608.12210) prove
all-orders Euclidean off-shell perturbative infrared finiteness. Their graph
argument obtains positive soft-momentum degree from the derivative carried by
each interaction leg, and the perfect-square Ward identity protects the
renormalized action form. This is consistent with the extra low-momentum
factor required in the score bound.

It is not the missing theorem. Their result concerns perturbative off-shell
graphs; it does not control the nonperturbative finite-volume background
marginal $\nu$, the conditional centers, or the normalized lattice Gibbs
moment. The certificate records this source only as a perturbative guide.

## Next gate

Write $V_\eta'(0)$ as the lowest-momentum projection of the local nonlinear
residual composites. A successful proof must obtain one more factor of
$\omega_L$ in its background-marginal second moment, using BT locality,
shift-derivative cancellation, or a controlled multiscale decomposition. An
explicit BT volume sequence for which that normalized score diverges would be
an equally decisive obstruction.

This result does not establish the annealed score bound, the integrated
lowest-mode or interacting $H^{-1}$ moment, tightness, a continuum measure, a
Born rule, Krein reconstruction, or anything `LORENTZIAN-CAUSAL`.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_annealed_center_score_reduction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_annealed_center_score_reduction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_annealed_center_score_reduction
```

The observation producer is reproducible separately:

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_center_score_experiment.py
```

## Verification receipt

The recorded $L=4,6$ observation production passed in 35.44 seconds with peak
RSS 22904 KB.  On the final tree, the producer byte check passed in 0.04
seconds (20888 KB), the independent verifier passed in 0.09 seconds (29096
KB), and all nine focused tests passed in 0.41 seconds (31324 KB).  The smoke
sampler inside the tests took 0.30 seconds.

Tier 0 Python compilation passed in 0.05 seconds (19472 KB).  The first
memory-capped `git diff --check` invocation could not create Git's preload
thread and is recorded as a failure, not a pass; the deterministic retry
`git -c core.preloadindex=false diff --check` passed in 0.09 seconds (12888
KB).  The successor certificate and Paper 21 verifier are the affected Tier 2
consumer chain.  Tier 3 was not run because this is a working-draft scoped
method reduction and diagnostic, not a freeze, release, shared-core change,
or promotion of a quantum lifecycle state.
