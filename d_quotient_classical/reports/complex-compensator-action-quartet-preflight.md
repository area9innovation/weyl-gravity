# Complex compensator action and quartet preflight

## Result

The local action is now frozen on the formal `rho!=0` polar chart.  The
canonical branch has gauge group `Diff semidirect Weyl` and a **global**
internal U(1), so the phase remains a physical shift field rather than an
unexported gauge mode.

Modulo total derivatives and four-dimensional curvature identities, the
declared two-scalar-derivative/four-curvature-derivative action is

\[
\begin{aligned}
S_0=\int\sqrt{-g}\biggl[&
\frac{\alpha_B}8 C^2
-\frac{\kappa_r}2\left[(\nabla\rho)^2+\frac16R\rho^2\right]
-\frac{\kappa_\theta}2\rho^2(\nabla\theta)^2
-\frac\lambda4\rho^4\\
&+\left(\frac\rho f\right)^4
\left[\alpha_R R(\widehat g)^2+\alpha_EE_4(\widehat g)
+\alpha_PP_4(\widehat g)\right]\biggr],
\end{aligned}
\]

with `g_hat=(rho/f)^2 g`.  The Wess--Zumino functional remains an
order-`hbar` counterterm and is not inserted into this classical action.

## Exact BV reduction

Writing `rho=f exp(-tau)`, the canonical cotangent change is

\[
\widehat g=e^{-2\tau}g,\qquad
\widehat g^*=e^{2\tau}g^*,\qquad
\widehat\tau^*=-\rho\rho^*+2g\!\cdot\!g^*.
\]

It preserves the odd canonical one-form.  In the ordered basis
`(tau,omega,omega_star,tau_hat_star)`,

\[
Q_W\tau=\omega,\qquad Q_W\omega^*=\widehat\tau^*,
\qquad Q_Wh_W+h_WQ_W=1.
\]

The diffeomorphism and Weyl antighost/multiplier sectors have the same exact
pointwise cotangent-doublet contraction.  After projecting the quartet, the
remaining odd pairing contains the nondegenerate
`<delta theta,delta theta_star>` block.

## Einstein and phase coefficients

The reduced action contains

\[
\frac{M_P^2}2R(\widehat g)
-\frac{Z_\theta}2(\widehat\nabla\theta)^2
-\frac{\lambda f^4}4,
\qquad
M_P^2=-\frac{\kappa_r f^2}6,
\qquad
Z_\theta=\kappa_\theta f^2.
\]

The general polar theory therefore admits
`kappa_r<0`, `kappa_theta>0`; the exact fixture
`(kappa_r,kappa_theta)=(-1,1)` gives
`M_P^2=f^2/6` and `Z_theta=f^2`.  The negative radial direction is not called
healthy: it is removed by the certified Weyl quartet before the reduced
phase sign is read.

There is nevertheless a sharp obstruction for the ordinary
Cartesian-analytic complex scalar.  That subfamily forces
`kappa_r=kappa_theta=kappa_Phi`, and hence

\[
M_P^2Z_\theta=-\frac{\kappa_\Phi^2f^4}6<0.
\]

It cannot have both positive Einstein and phase residues.  The viable unequal
coefficient theory is smooth only on the declared `rho!=0` polar chart.

For global U(1), `theta` is one massless charged shift scalar.  The radial
field is absent from the reduced cohomology.  `alpha_R R(g_hat)^2` adds the
usual scalaron with `m_0^2=M_P^2/(12 alpha_R)` on the nondegenerate flat
branch; `alpha_R=0` removes that metric scalar.  Euler and Pontryagin are
topological, while `Box R` is horizontally exact.

## Boundary

`rho=f` is a Weyl gauge chart, not evidence of spontaneous Weyl breaking, and
`f` is introduced rather than dynamically generated.  Local U(1) would
require a connection and a new complete BV sector; it is not silently
declared here.  No background solution, causal Green operator, Hadamard
state, anomaly coefficient, QME, particle, scattering or unitarity theorem
follows.

## Reproduction

```bash
python3 d_quotient_classical/compensator/complex_compensator_action_quartet_preflight.py --check
python3 d_quotient_classical/compensator/verify_complex_compensator_action_quartet_preflight.py
python3 -m unittest d_quotient_classical.compensator.tests.test_complex_compensator_action_quartet_preflight
```

Core hash: `edbe931b082d36792b8afd453f1c7969bdc0ca1392c5ec936490edc0845abb0f`

CLOSE-OUT: DONE — the declared local action, BV rows and quartet reduction are frozen
EVIDENCE: d_quotient_classical/certificates/COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1.json
