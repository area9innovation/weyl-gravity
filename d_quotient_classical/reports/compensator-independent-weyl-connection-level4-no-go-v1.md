# Independent real-Weyl-connection Level-4 no-go

## Result

The terminal Level-3 theorem is imported by exact hash and exports no selected
action.  The complete declared Level-4 field content is

\[
(g_{ab},\Phi=\rho e^{i\theta},W_a),
\]

where \(W_a\) is one real torsion-free Weyl connection, the phase has a global
shift symmetry, and complex conjugation sends \(\theta\mapsto-\theta\).

Let the original and candidate Weyl generators act with weights

\[
(m_0,r_0)=(1,1),
\qquad
(m_1,r_1)=(a,b)
\]

on the metric scale and radial compensator.  Define

\[
\Delta=a-b.
\]

The exact result is

\[
\boxed{
\text{independent dressed-trace gauge direction}
\quad\Longleftrightarrow\quad
\Delta\ne0,
}
\]

while action invariance of the phase kinetic term gives

\[
\boxed{\Delta\kappa_\theta=0.}
\]

The frozen Berger clock requires \(\kappa_\theta\ne0\) for a nonzero phase
pairing and charge.  Hence

\[
\boxed{
\{\Delta\ne0\}\cap\{\kappa_\theta\ne0\}
\cap\{\Delta\kappa_\theta=0\}
=\varnothing.
}
\]

The full declared real-Weyl Level-4 good locus is empty.  No selected action
or nonlinear \(q_2\) is exported.

## Complete minimal action

Modulo the Euler-Weyl density, total derivatives and invertible
complex-conjugation-preserving polar redefinitions, the lowest-order
parity-even density is

\[
\begin{aligned}
\mathcal L_{\min}=\sqrt{-g}\bigg\{&
\frac{\alpha_C}{8}C^2+\alpha_0\mathcal R_W^2
+\alpha_2(\operatorname{Ric}^{\rm TF}_W)^2
-\frac{\zeta}{4}F_{ab}F^{ab}\\
&-\frac{\kappa_r}{2}(D_W\rho)^2
-\frac{\kappa_R}{12}\rho^2\mathcal R_W
-\frac{\kappa_\theta}{2}\rho^2(\nabla\theta)^2
-\frac{\lambda}{4}\rho^4
\bigg\}.
\end{aligned}
\]

Here

\[
F_{ab}=2\partial_{[a}W_{b]}.
\]

The pure geometric terms are spectators for the rank/charge separator.  The
scalar basis is exhaustive at the declared order.  A cross term
\(\rho D\rho\cdot d\theta\) is odd under complex conjugation.  An additive
local transformation of \(\theta\) is an internal \(U(1)\) or complexified
connection, not the one-real-Weyl-connection theory classified here.

## Gauge rank and reducibility

At a nonzero normalized longitudinal symbol, the two Weyl columns on

\[
(\log g\text{-scale},\log\rho,W_L)
\]

form

\[
G=
\begin{pmatrix}
1&a\\
-1&-b\\
-1&-a
\end{pmatrix}.
\]

The metric/radial minor is

\[
\det G_{\{g,\rho\}}=a-b=\Delta.
\]

The dressed metric

\[
\widehat g=(\rho/f)^2g
\]

obeys

\[
\delta_\eta\widehat g=2\Delta\eta\,\widehat g.
\]

Therefore the old dressed trace is gauged only on \(\Delta\ne0\).

On \(\Delta=0\),

\[
G
\begin{pmatrix}
-a\\1
\end{pmatrix}
=0.
\]

The candidate column is exactly \(a\) times the original column.  One may
either quotient to one irreducible ghost or retain both columns with an even
ghost-for-ghost.  Either BV presentation adds a contractible reducible sector,
not a second dressed-trace gauge direction.

## Exact Ward locus

For a constant candidate Weyl parameter, the four compensator monomials have
weights

\[
\begin{array}{c|c}
\text{term}&\text{weight}\\ \hline
(D_W\rho)^2&2\Delta\\
\rho^2\mathcal R_W&2\Delta\\
\rho^2(\nabla\theta)^2&2\Delta\\
\rho^4&4\Delta.
\end{array}
\]

Thus the exact Ward ideal contains

\[
(\Delta\kappa_r,\Delta\kappa_R,
\Delta\kappa_\theta,\Delta\lambda).
\]

No derivative improvement can cancel a nonzero constant weight.  The two
complete strata are:

1. \(\Delta=0\): compensator coefficients may be nonzero, but the proposed
   gauge generator is dependent and reducible.
2. \(\Delta\ne0\): exact Ward invariance forces
   \[
   \kappa_r=\kappa_R=\kappa_\theta=\lambda=0.
   \]
   The geometric spectator coefficients remain free, but the entire complex
   compensator has zero action at this order.

## BV and charge disposition

The action-origin kinematic rows are

\[
\begin{aligned}
Qg&=\mathcal L_\xi g+2(\omega+a\eta)g,\\
Q\rho&=\mathcal L_\xi\rho-(\omega+b\eta)\rho,\\
Q\theta&=\mathcal L_\xi\theta,\\
QW&=\mathcal L_\xi W-d(\omega+a\eta).
\end{aligned}
\]

The minimal master action is their canonical cotangent lift, with the usual
Diff semidirect-product ghost rows.  The odd pairing is the direct canonical
field--antifield pairing and the real structure is componentwise, with
complex conjugation reversing \(\theta\).

On the independent stratum,

\[
J_\theta^a=-\kappa_\theta\rho^2\nabla^a\theta=0,
\]

and the phase Hessian is zero.  Because shift symmetry forbids any other
minimal \(\theta\) row, arbitrary compact-support phase variations survive.
Consequently there is no complete scalar/longitudinal Green parent.

On the dependent stratum, the new row does not contract the old dressed trace.
This is Stueckelberg counting only after the explicit rank and reducibility
calculation; no field count is used as a cohomology proof.

## Background boundary

No earlier background is inherited automatically.  On the independent
stratum the phase stress and charge vanish, so the frozen active-clock Berger
equations are not equations of this theory.  The common rank/charge locus is
already empty, and no replacement unit-cylinder or Berger solution is
promoted.

The background Euler systems, detailed velocity inertia and characteristic
roots beyond the zero phase block are therefore explicitly `NOT_REACHED`.
This is the first invariant separator allowed by the work item.

## Claim boundary

This is a scoped no-go for one real Weyl connection and one formal-polar
complex compensator at the declared minimal derivative order.  It does not
cover an internal \(U(1)\), a complexified connection, an additional
compensator, higher phase-derivative operators, other backgrounds or general
metric-affine geometry.

It selects no action and establishes no complete Green parent, nonlinear
\(q_2\), Hadamard state, anomaly/QME result, particle space, scattering,
positivity or unitarity theorem.

## Next theory choice

The four-level minimal compensator-repair ladder is empty.  The next
enlargement must be named explicitly:

- add an internal \(U(1)\) or complexified connection with its own BV sector;
- add another compensator so two independent scale generators have two
  covariant charge directions; or
- abandon the common nonzero Berger clock-charge gate.

EVIDENCE: `d_quotient_classical/receipts/COMPENSATOR_INDEPENDENT_WEYL_CONNECTION_LEVEL4_NO_GO_V1_TIER_RECEIPT.json`

CLOSE-OUT: DONE — exact gauge-rank and constant-Ward elimination prove that
no stratum has both an independent dressed-trace gauge direction and a
nonzero complex-compensator clock charge.
