# Fixed-coupling Berger delta-charge theorem

The positive Berger background has nonzero internal clock momentum, but that
momentum is not freely variable on its fixed-coupling linearized solution
space.

Keeping the lapse before variation and fixing only the common Weyl scale gives

\[
ds^2=-N(t)^2dt^2+\sigma_1^2+\sigma_2^2+c(t)^2\sigma_3^2,
\qquad
(T_1,T_2)=\rho(t)(\cos\theta,\sin\theta).
\]

The exact reduced action is

\[
\frac{S}{16\pi^2}=\int dt\,Nc\left\{
\frac{\alpha_B}{8}C^2+
\frac{\dot\rho^2+\rho^2\dot\theta^2}{2N^2}
-\frac{R\rho^2}{12}-\frac{\lambda\rho^4}{4}
\right\}.
\]

On the positive branch, with \(\alpha_B\) and \(\lambda\) held fixed, the
linearized lapse equation is

\[
\boxed{
\delta E_N=-\frac{\alpha_Bq^{3/2}}2\frac{\delta Q_R}{Q_R}.
}
\]

The coefficient is nonzero throughout
\((5-\sqrt{21})/2<q<1/4\). Therefore every homogeneous allowed tangent obeys
\(\delta Q_R=0\).

This also excludes an inhomogeneous charged tangent.  The compact spatial
isometry group \(SU(2)_L\times U(1)_R\) preserves the background and the
linearized equations, while \(\delta Q_R\) is an invariant linear functional.
If any smooth solution had nonzero \(\delta Q_R\), its compact group average
would be a homogeneous solution with the same nonzero value, contradicting
the lapse constraint.

Combining this with the previously certified identity

\[
\Omega_{\rm total}(\delta,\mathcal L_D)=\omega\,\delta Q_R
\]

gives

\[
\boxed{
\Omega_{\rm total}(\delta,\mathcal L_D)=0,
\qquad D_{\rm compact}=D_{\rm GAUGE}
}
\]

on the declared smooth fixed-coupling linearized phase space about the
positive Berger background.

There is no contradiction with \(Q_R>0\): the background charge is nonzero,
but its pullback differential vanishes on the allowed tangent space.  The
phase is therefore a genuine rotating clock coordinate whose momentum is
fixed by the compact Hamiltonian constraint, rather than an additional freely
variable residual charge.

This theorem does not construct the support-local all-row BV contraction,
causal Green homotopies, or nonlinear stability.  Those form the next gate,
`FULL_BERGER_CLOCK_BV_AND_STABILITY_AUDIT`.
