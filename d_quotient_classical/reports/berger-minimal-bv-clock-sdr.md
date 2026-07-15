# Support-local minimal BV contraction of the Berger clock

The positive Berger clock fixes the temporal-diffeomorphism and Weyl gauge
directions locally.  Normalize its two scalar fluctuations by

\[
\Theta=\frac{\delta\theta}{\omega},
\qquad
R=\frac{\delta\rho}{\bar\rho}.
\]

In the shifted BV-complex convention used here, if \(\tau\) is the temporal
diffeomorphism ghost and \(\sigma\) the Weyl ghost, then

\[
q_1\tau=\Theta,
\qquad
q_1\sigma=-R.
\]

The dressed metric

\[
\widehat h=h-\mathcal L_{\Theta n}\bar g+2R\bar g
\]

has gauge incidence

\[
K_1^{\rm dressed}(\xi_\perp,\tau,\sigma)
=\mathcal L_{\xi_\perp}\bar g
\quad\text{in the metric row}.
\]

Thus its temporal and Weyl gauge columns vanish exactly.  The transformation
is first-order and support-local.  Its inverse is

\[
h=\widehat h+\mathcal L_{\Theta n}\bar g-2R\bar g.
\]

The cotangent lift is BV canonical:

\[
\widehat h^*=h^*,
\qquad
\Theta^*=\omega\theta^*+K_t^\sharp h^*,
\qquad
R^*=\bar\rho\rho^*-2\operatorname{tr}_{\bar g}h^*,
\]

where

\[
K_t\Theta=\mathcal L_{\Theta n}\bar g,
\qquad
K_t^\sharp h^*=-2n_\nu\nabla_\mu h^{*\mu\nu}.
\]

In dressed coordinates the eight clock rows are

\[
(\tau,\sigma,\Theta,R,\Theta^*,R^*,\tau^*,\sigma^*).
\]

Their nonzero differential and homotopy maps are

\[
\begin{aligned}
q_1\tau&=\Theta,& q_1\sigma&=-R,
&q_1\Theta^*&=-\tau^*,&q_1R^*&=\sigma^*,\\
s\Theta&=\tau,&sR&=-\sigma,
&s\tau^*&=-\Theta^*,&s\sigma^*&=R^*.
\end{aligned}
\]

They satisfy exactly

\[
q_1^2=0,
\qquad
q_1s+sq_1=1_{\rm clock},
\qquad
s^2=0,
\]

and both \(q_1\) and \(s\) have the required cyclic adjoint relation.  The
full 34-dimensional minimal complex therefore retracts support-locally onto a
26-dimensional dressed-metric/spatial-diffeomorphism minimal complex.

This is the complete minimal clock-sector SDR, not the complete Berger BV
theorem.  The retained ten-component dressed-metric Hessian, nonminimal
gauge-fixed rows, stability analysis, and causal Green homotopies remain the
next gate: `BERGER_RETAINED_Q1_AND_NONMINIMAL_COMPLETION`.
