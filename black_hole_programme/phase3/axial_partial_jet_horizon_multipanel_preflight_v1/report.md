# Regular partial-jet multipanel transport report

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

Status: `CERTIFIED_MULTIPANEL_REGULAR_PARTIAL_JET_SHORTFALL`.

## Method

The selected horizon column starts at

\[
\rho_0=2^{-22}
\]

with the certified Frobenius/Levelt base and intrinsic-tangent tails. Each
geometric shell doubles \(\rho\) using four equal panels. On every panel,
an order-24 interval Taylor transport is constructed for:

- the correlated four-state base/tangent system over dual numbers; and
- the direct regular-frame twelve-state six-state realization.

Both use the same fourth-order frequency model. The only reconditioning is
the already certified moving spin-two phase and spin-one Levelt scaling.

## Certified refusal

The direct and partial-jet hulls overlap through 27 panels. Six complete
shells end at

\[
\rho=2^{-16}.
\]

At shell 6, panel 3, the rail reports

\[
\begin{aligned}
\text{state width}&=1164043.0305228343,\\
h\|\widehat{\mathcal B}\|_\infty&=0.9053473012862264,\\
\text{order-24 operator tail}&=
5.560665403823773\times10^{-27}.
\end{aligned}
\]

The direct/jet overlap remains true. The declared state-width ceiling is
\(10^6\), so the computation refuses before completing shell 6.

This separates two effects. The phase-factored local transport is
well-resolved: the operator tail is negligible. The obstruction is the
growth of cumulative interval dependency in an unreconditioned state
column.

## Boundary

This package does not establish a bounded matching-radius column or
transport to \(r=4\). A successor needs a validated correlation-preserving
reconditioning, such as a midpoint-preconditioned affine column chart or a
projective/Riccati chart that preserves the partial-jet identity.

The endpoint normalizer shear \(K_H\) is not computed. Nothing here
establishes \(T_+\), H4, scattering, or bounded global transport.
