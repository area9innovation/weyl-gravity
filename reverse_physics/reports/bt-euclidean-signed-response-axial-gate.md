# BT signed conditional-response axial gate

Dependency tags: LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL, REDUCED-MODE

Lifecycle: CLASSIFIED

## Result

Keeping the signs in the one-site conditional response is necessary, but it
is still not enough pointwise. The exact full-Gibbs averaged response has a
very small symmetry-reduced form:

\[
 \widehat R_L(p e_1)
 =\beta_L\omega(p)-a_L\omega(p)^2,
 \qquad
 \omega(p)=2(1-\cos p),
\]

where \(R=I-J\) is the positive-relaxation convention for the simultaneous
conditional-mean map, and \(a_L\) is the averaged response to one axial
distance-two site. Exact conditional covariance formulas prove

\[
 a_L<0.
\]

The coefficient of \(\omega^2\), namely \(-a_L\), is therefore strictly
positive. The whole unresolved annealed sign is concentrated in one number,
\(\beta_L\).

At the perfectly uniform off-site background, however, the weak-coupling
expansion gives

\[
 \boxed{
 \beta_{\rm vac}(\lambda)
 =-\frac{43}{5184}\lambda^2+O(\lambda^4).
 }
\]

Thus \(\beta_{\rm vac}<0\) for all sufficiently small nonzero couplings. On
sufficiently large tori the pointwise signed response is expansive at the
lowest momentum. This rules out a pointwise signed-contraction argument.
It does not determine the full-Gibbs averaged coefficient \(\beta_L\), because
background fluctuations can and must be averaged before that sign is used.

The machine-readable result is
REVERSE_PHYSICS_BT_EUCLIDEAN_SIGNED_RESPONSE_AXIAL_GATE_V1.

## Conditional response and its support

Let \(M_o(\xi)\) be the conditional mean of the log field at \(o\) when all
off-site log fields are fixed. Common shifts are understood modulo the
constant gauge. Differentiating the normalized conditional density gives

\[
 D_yM_o=-\operatorname{Cov}_{q_\xi}(\psi_o,D_yS),
 \qquad y\ne o.
\]

Only residuals at \(o\) and its eight neighbors depend on the fiber
coordinate. Hence \(D_yM_o=0\) beyond graph distance two.

For an axial endpoint \(y=o+2e\), only the residual at the intermediate site
\(o+e\) contributes a fiber-dependent term. Writing \(z\) for the fiber
coordinate,

\[
 D_{o+2e}M_o
 =-\frac{t_{o+e,o}t_{o+e,o+2e}}{\lambda^2}
   \operatorname{Cov}_{q_\xi}(z,e^z)<0.
\]

Both transfer factors are positive. The covariance is strictly positive
because \(z\) and \(e^z\) are strictly increasing under a nondegenerate
positive density.

A mixed endpoint \(o+e+f\), with \(e,f\) in distinct axes, has two
intermediate paths. Its derivative is the negative sum of the two positive
path products times the same strictly positive covariance. It is also
strictly negative.

## Symmetry reduction of the annealed kernel

After expectation under the actual translation- and hypercubic-invariant
finite-volume Gibbs measure, there are three off-site orbit coefficients:

- \(n_L\) at the eight nearest neighbors;
- \(a_L\) at the eight axial distance-two sites;
- \(m_L\) at the twenty-four mixed distance-two sites.

Shift equivariance of the conditional mean gives

\[
 8n_L+8a_L+24m_L=1.
\]

On an axial momentum, direct orbit summation gives

\[
\begin{aligned}
 \widehat J_L(pe_1)
 &=1-\beta_L\omega(p)+a_L\omega(p)^2,\\
 \widehat R_L(pe_1)
 &=\beta_L\omega(p)-a_L\omega(p)^2,\\
 \beta_L
 &=n_L+4a_L+6m_L
  =\frac18+3(a_L+m_L).
\end{aligned}
\]

The distance-two formulas prove \(a_L,m_L<0\). They do not fix the sign of
\(\beta_L\). This is now the exact annealed response gate.

## Uniform-background fiber

Set every off-site field to zero and let \(z=\psi_o\). The only
fiber-dependent residuals are

\[
 r_o=8(e^{-z}-1),
 \qquad
 r_y=e^z-1
\]

at the eight neighbors. The unscaled fiber action is therefore

\[
 F(z)=32(e^{-z}-1)^2+4(e^z-1)^2.
\]

It has its unique nondegenerate minimum at \(z=0\), with \(F''(0)=72\), and

\[
 q_\lambda(z)=Z_\lambda^{-1}e^{-F(z)/\lambda^2}.
\]

For one axial endpoint and one mixed endpoint,

\[
\begin{aligned}
 a_{\rm vac}(\lambda)
 &=-\lambda^{-2}\operatorname{Cov}_{q_\lambda}(z,e^z),\\
 m_{\rm vac}(\lambda)&=2a_{\rm vac}(\lambda).
\end{aligned}
\]

The row sum then fixes

\[
 n_{\rm vac}=\frac18-7a_{\rm vac},
 \qquad
 \beta_{\rm vac}
 =\frac18-\frac9{\lambda^2}
       \operatorname{Cov}_{q_\lambda}(z,e^z).
\]

## Exact weak-coupling coefficient

Expanding the fiber action gives

\[
 F(z)=36z^2-28z^3+21z^4-7z^5+\frac{31}{10}z^6+O(z^7).
\]

Set \(z=\lambda x\). The base law is the centered Gaussian with precision
72. Exact Gaussian-moment expansion of the normalization and the three
moments in the covariance gives

\[
 \operatorname{Cov}_{q_\lambda}(z,e^z)
 =\frac{\lambda^2}{72}
  +\frac{43\lambda^4}{46656}
  +O(\lambda^6).
\]

Consequently,

\[
\begin{aligned}
 a_{\rm vac}
 &=-\frac1{72}-\frac{43}{46656}\lambda^2+O(\lambda^4),\\
 m_{\rm vac}
 &=-\frac1{36}-\frac{43}{23328}\lambda^2+O(\lambda^4),\\
 \beta_{\rm vac}
 &=-\frac{43}{5184}\lambda^2+O(\lambda^4).
\end{aligned}
\]

The producer obtains these values using the differential recurrence for the
formal exponential weight. The verifier independently expands the ordinary
power series of that weight as a bivariate polynomial and integrates every
monomial with Gaussian moments.

The unique global minimum and exponential tails justify the finite-order
Watson--Laplace expansion with a remainder. The negative leading coefficient
therefore proves the sign for some nonzero weak-coupling interval; it is not
merely a formal sign.

## Meaning in ordinary language

The free theory works because responses from nearby sites cancel with
extraordinary precision. We first tried bounding their absolute sizes; that
failed. We then kept their signs, which was the correct next move.

This calculation shows that the signs still do not cancel correctly at every
individual background. Even the completely uniform surrounding field
develops a tiny wrong-sign long-wave term once the one-site nonlinear
distribution is included. The statistical average over all backgrounds may
repair it, but that repair is now a concrete thing that must be proved—it
cannot be assumed from the vacuum.

## Next gate

Compute \(\beta_L\) under the actual interacting Gibbs measure, with the
conditional normalization retained. Its connected weak-coupling expansion
will show whether background fluctuations cancel the negative uniform-fiber
term. A useful positive result must then be connected to a Fourier-specific
heat-bath or Witten form estimate; the sign of an averaged Jacobian alone is
not yet an upper covariance bound.

## Claim boundary

This result does not prove that the annealed \(\beta_L\) is negative, that
heat-bath dynamics is unstable, or that every block or signed response method
fails. It proves neither a global Poincare/Witten theorem nor the normalized
lowest-mode or interacting \(H^{-1}\) estimate. It establishes no continuum
measure, ordinary OS reconstruction, new physical dimension, Born rule,
Krein reconstruction, or LORENTZIAN-CAUSAL statement.

Paper 21 is not changed because this is a method gate rather than a continuum
or reconstruction lifecycle promotion.

## Verification

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_signed_response_axial_gate.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_signed_response_axial_gate.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_signed_response_axial_gate
