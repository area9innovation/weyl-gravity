# Flat-TT logarithmic one-loop form factor

Status:
`FLAT_TT_UNIVERSAL_LOGARITHMIC_GAMMA1_FORM_FACTOR_CERTIFIED_FINITE_CONSTANT_AND_CURVED_COMPLETION_OPEN`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

## Result

The anomaly-induced Paneitz/Riegert representative fixes the Weyl-orbit
response, but it does not contain the quadratic transverse-traceless form
factor on the pure flat TT slice.  On that slice (R^{(1)}=0), while both
(C^2) and (mathcal E_4) begin at quadratic order, so the displayed Riegert
bilinears begin at (O(h^4)).

The already certified repository coefficient

\[
c=\frac{199}{30},
\qquad \beta_2=2c=\frac{199}{15},
\]

does fix the universal nonlocal momentum dependence.  In the normalization
where the exact flat fixture (p=(1,0,0,0)),
(h_{11}=1,h_{22}=-1) has (C_1^2=1), the quadratic form factor is

\[
\Gamma^{(2)}_{1,TT}
=\frac1{(4\pi)^2}
\left[
-\frac{199}{60}
\langle C_1,\log(p^2/\mu^2)C_1\rangle
+z_C(\mu)\langle C_1,C_1\rangle
\right].
\]

Indeed, under the repository convention
(\delta_\sigma g_{\mu\nu}=2\sigma g_{\mu\nu}), a constant Weyl rescaling
sends (p^2\mapsto e^{-2\sigma}p^2).  Hence

\[
\delta_\sigma\log(p^2/\mu^2)=-2\sigma,
\]

and the exact coefficient identity

\[
-\frac{199}{60}=-\frac c2=-\frac{\beta_2}{4}
\]

reproduces (c=199/30).  Equivalently,

\[
\mu\frac{\partial}{\partial\mu}F_C(p^2;\mu)=\frac{199}{30}
\]

before the local coupling runs.  The scheme-independent observable content at
this gate is the difference

\[
F_C(p^2;\mu)-F_C(q^2;\mu)
=-\frac{199}{60}\log\frac{p^2}{q^2}.
\]

## Finite normalization

A reference condition (F_C(\kappa_{\rm ref}^2;\mu)=N_C) fixes

\[
z_C(\mu)=N_C+\frac{199}{60}
\log\frac{\kappa_{\rm ref}^2}{\mu^2},
\qquad
\mu\frac{d z_C}{d\mu}=-\frac{199}{30}.
\]

Neither (N_C) nor (kappa_{\rm ref}) has been selected by repository
physics, so the additive local (C^2) constant remains open.  This is a
normalization family, not a claim that the finite constant has been computed.

The separation between anomaly-induced and conformal parts, and the role of
nonlocal logarithmic curvature form factors, follows the structural analysis
of [Barvinsky--Wachowski](https://arxiv.org/abs/2306.03780).  All numerical
coefficients and normalization identities above are replayed from repository
certificates rather than imported from that paper.

## Claim boundary

The result applies only to nonzero positive Euclidean momentum on the declared
flat TT carrier.  It does not define the logarithm at (p^2=0), choose a
Lorentzian branch cut, construct the general curved-background conformal form
factor or its higher-curvature completion, fix the finite (C^2) or (R^2)
normalizations, supply renormalized time-ordered products or a BV Laplacian,
produce the compensator-inclusive classical contraction, determine complete
\(\Gamma_1\) or \(Q_1\), authorize residual transfer, or activate Bridge 4 or
Bridge 5.
