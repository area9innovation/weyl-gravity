# Anomaly-induced nonlocal one-loop effective action

## Result

`ANOMALY_INDUCED_NONLOCAL_GAMMA1` constructs a coefficient-bearing
Paneitz/Riegert representative for the part of the Euclidean one-loop
effective action fixed by the certified trace anomaly.  Put

\[
 \mathcal E_4=E_4-\frac23\Box R,
 \qquad
 \Delta_4=\Box^2+2R^{\mu\nu}\nabla_\mu\nabla_\nu
 -\frac23R\Box+\frac13(\nabla^\mu R)\nabla_\mu .
\]

For a self-adjoint inverse or compatible generalized inverse
\(G_4=\Delta_4^{-1}\), the representative is

\[
 \Gamma_{1,\mathrm{anom}}
 =\frac1{(4\pi)^2}\left\{
 \frac18\left\langle \mathcal E_4,
 G_4\left(2cC^2-a\mathcal E_4\right)\right\rangle
 +\frac{a}{18}\int\!\sqrt g\,R^2
 \right\},
\]

with

\[
 c=\frac{199}{30},\qquad a=\frac{87}{20}.
\]

This is an anomaly-induced representative, not the complete finite effective
action.

## Exact coefficient solve

The three functional carriers

\[
 \langle\mathcal E_4,G_4C^2\rangle,
 \quad
 \langle\mathcal E_4,G_4\mathcal E_4\rangle,
 \quad
 \int\sqrt g\,R^2
\]

have Weyl-response matrix

\[
 \begin{pmatrix}
 4&0&0\\
 0&8&0\\
 0&0&-12
 \end{pmatrix}
\]

in the basis \((C^2,\mathcal E_4,\Box R)\).  The repository anomaly
\((c,-a,0)\) in the basis \((C^2,E_4,\Box R)\) becomes

\[
 \left(c,-a,-\frac{2a}{3}\right)
 =\left(\frac{199}{30},-\frac{87}{20},-\frac{29}{10}\right)
\]

in the modified basis.  Exact rational elimination gives

\[
 \left(\frac{199}{120},-\frac{87}{160},\frac{29}{120}\right).
\]

The last coordinate is not optional bookkeeping.  Since

\[
 \delta_\sigma\int\sqrt g\,R^2
 =-12\int\sqrt g\,\sigma\Box R,
\]

it cancels the \(2a/3\) type-D term introduced by replacing \(E_4\) with
\(\mathcal E_4\).  The resulting variation is exactly

\[
 \delta_\sigma\Gamma_{1,\mathrm{anom}}
 =\frac1{(4\pi)^2}\int\sqrt g\,\sigma
 \left(\frac{199}{30}C^2-\frac{87}{20}E_4\right)
\]

on the declared exact-inverse or compatible-source sector.

## Analytic scope and zero modes

The inverse is not silently assumed to exist globally.  The certificate
requires either:

1. an invertible Euclidean boundary problem for \(\Delta_4\); or
2. a self-adjoint generalized inverse satisfying
   \(\Delta_4G_4=G_4\Delta_4=1-\Pi_{\ker}\), with every displayed source in
   the compatible sector \(\Pi_{\ker}f=0\).

On a compact closed manifold the constant scalar is generally a Paneitz zero
mode.  Projecting it away does not reproduce the omitted global anomaly.
Kernel components, boundary transgressions, and homogeneous solutions are
therefore retained as open global data.

## Relation to the local Wess--Zumino primitive

For \(\widehat g=e^{-2\tau}g\), the finite difference

\[
 \Gamma_{1,\mathrm{anom}}[g]
 -\Gamma_{1,\mathrm{anom}}[\widehat g]
\]

has the same certified BRST image as

\[
 \frac1{(4\pi)^2}
 \left(\frac{199}{30}B_C-\frac{87}{20}B_E\right)
\]

modulo the horizontal differential and under the same analytic conditions.
The certificate does not assert term-by-term equality between two choices of
anomaly primitive; their difference can be Weyl invariant or carry boundary
and global data.

## What remains open

The exact decomposition is

\[
 \Gamma_1^{\mathrm{ren}}
 =\Gamma_{1,\mathrm{anom}}+\Gamma_{1,\mathrm{inv}},
 \qquad \delta_\sigma\Gamma_{1,\mathrm{inv}}=0.
\]

The repository has not computed \(\Gamma_{1,\mathrm{inv}}\), fixed the finite
\(C^2/R^2\) normalizations, selected global Paneitz kernel/boundary data, or
constructed the renormalized BV Laplacian/time-ordered product.  It also still
lacks a compensator-inclusive classical residual contraction.  Complete
\(\Gamma_1\) and \(Q_1\) remain fail-closed, residual transfer is forbidden,
and neither Bridge 4 nor Bridge 5 is activated.

## Reproduction

```bash
PYTHONPATH=quantum-weyl python3 -m transfer.anomaly_induced_nonlocal_gamma1 --check
PYTHONPATH=quantum-weyl python3 -m transfer.verify_anomaly_induced_nonlocal_gamma1
PYTHONPATH=quantum-weyl python3 -m unittest \
  quantum-weyl/transfer/tests/test_anomaly_induced_nonlocal_gamma1.py -v
```
