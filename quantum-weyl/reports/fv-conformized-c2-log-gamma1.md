# Fradkin–Vilkovisky completion of the selected (C^2) logarithmic carrier

Status:
`FV_CONFORMIZED_C2_LOG_CARRIER_EXACTLY_WEYL_COMPLETED_INDEPENDENT_CUBIC_R2_AND_NORMALIZATION_DATA_OPEN`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

## Result

On an asymptotically flat or fixed-boundary Euclidean domain where

\[
 L_g=\Box_g-\frac16R_g
\]

has the declared normalized inverse, set

\[
 u_g=1+\frac16L_g^{-1}R_g,
 \qquad
 \Sigma_{\rm FV}[g]=-\log u_g,
 \qquad
 \bar g[g]=u_g^2g.
\]

The exact identities

\[
 L_g u_g=0,
 \qquad
 R[\bar g]=u_g^{-3}(R_g-6\Box_g)u_g=0
\]

show that \(\bar g\) is the normalized scalar-flat representative. For a
boundary-compatible local Weyl transformation \(g'=e^{2\sigma}g\), conformal
covariance and uniqueness give

\[
 u_{g'}=e^{-\sigma}u_g,
 \qquad
 \Sigma_{\rm FV}[g']=\Sigma_{\rm FV}[g]+\sigma,
 \qquad
 \bar g[g']=\bar g[g].
\]

Therefore the previously certified coefficient-bearing spectral carrier has
the exact Weyl-orbit-invariant completion

\[
 \Gamma^{\rm conf}_{1,C^2}[g]
 =-\frac1{(4\pi)^2}\frac{199}{60}
 \left\langle C[\bar g],\Pi_{\bar g}
 \log\frac{\Delta_C[\bar g]}{\mu^2}
 \Pi_{\bar g}C[\bar g]\right\rangle_{\bar g}.
\]

Every tensor, pairing, projector, operator domain and logarithm is evaluated
on the same representative. This is a nonlocal functional invariant under
local Weyl transformations; “local-Weyl completion” does not mean that the
functional itself is local.

## Curvature filtration

Since

\[
 \Sigma_{\rm FV}=-\frac16\Box^{-1}R+O(\mathcal R^2),
\]

the conformized carrier agrees with the prior curvature-squared logarithm
through \(O(\mathcal R^2)\). Its first forced correction has curvature order
three. The certificate identifies that correction through the Fréchet
derivative

\[
 D\log(\Delta)[\delta\Delta]
 =\int_0^\infty(\Delta+s)^{-1}\delta\Delta(\Delta+s)^{-1}\,ds
\]

together with transport of the pairing and kernel projector. It does not
decompose the result into a cubic invariant basis and does not calculate the
independent \(W^{(3)}\) form factors of the full one-loop action. This is the
conformization construction described by
[Barvinsky–Wachowski](https://arxiv.org/abs/2306.03780).

## Carrier crosswalk

The two dressed metrics used by the programme are deliberately not
identified:

- \(\bar g[g]=e^{-2\Sigma_{\rm FV}[g]}g\) is a nonlocal functional of the
  strict metric selected by scalar-flat conformal gauge fixing.
- \(\widehat g[g,\tau]=e^{-2\tau}g\) is a local field redefinition in the
  formally enlarged \(\tau\)-adic BV theory, where \(\tau\) is independent.

They answer different questions and cannot be substituted for each other.

## Claim boundary

Existence and uniqueness are conditional on the declared inverse domain. A
kernel requires an explicit projector and an orbit-compatible normalization.
This receipt does not compute independent cubic Weyl-invariant form factors,
the independent nonlocal \(R^2\) form factor, finite \(C^2\) or absolute
\(R(\widehat g)^2\) normalizations, a complete \(\Gamma_1\) or \(Q_1\),
renormalized products, residual transfer, or any Lorentzian, Hadamard,
positivity, particle, scattering or unitarity theorem.
