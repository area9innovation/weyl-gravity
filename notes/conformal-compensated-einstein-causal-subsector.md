# Linear causal Einstein subsector in the compensated phase

## Result

The constant-compensator phase has a genuine free Einstein graviton Cauchy
sector on flat space.

For either transverse-traceless helicity, let

\[
D_q=\partial_t^2+q,\qquad q=|\mathbf k|^2,
\qquad M^2=\frac{c_1}{\alpha}>0.
\]

The Einstein--Weyl equation factorizes as

\[
D_q(D_q+M^2)h=0.
\]

Define the Einstein defect

\[
\chi=D_qh.
\]

It obeys the normally hyperbolic equation

\[
(D_q+M^2)\chi=0.
\]

Consequently the two local Cauchy conditions

\[
\chi|_\Sigma=0,
\qquad n^\mu\nabla_\mu\chi|_\Sigma=0
\]

imply `chi=0` throughout the domain of dependence.  No future boundary
condition or nonlocal frequency projection is required.

## Exact Cauchy-data calculation

For one Fourier mode, the fourth-order Cauchy vector is

\[
X=(h,\dot h,\ddot h,\dddot h).
\]

The two constraints are

\[
C X=
\begin{pmatrix}
q&0&1&0\\
0&q&0&1
\end{pmatrix}X=0.
\]

They have rank two.  Their kernel is exactly the embedded Einstein data

\[
I_E(h,\dot h)=(h,\dot h,-qh,-q\dot h).
\]

The machine certificate proves both intertwining identities

\[
C A_4=A_\chi C,
\qquad
A_4I_E=I_EA_E.
\]

Thus the constraint propagates under the fourth-order flow, and the induced
flow is precisely the ordinary massless wave flow.

The massive branch has embedding

\[
I_M(h,\dot h)=
(h,\dot h,-(q+M^2)h,-(q+M^2)\dot h)
\]

and satisfies

\[
C I_M=-M^2 I_2.
\]

It is therefore removed by the local Einstein constraints when `M^2 != 0`.
The determinant

\[
\det[I_E\ I_M]=M^4
\]

shows that the massless and massive data form complementary Cauchy branches.

## Symplectic restriction

The action-derived current is

\[
\begin{split}
\omega^\mu={}&\frac\alpha2\left[
 \chi_1\nabla^\mu h_2-(\nabla^\mu\chi_1)h_2
-\chi_2\nabla^\mu h_1+(\nabla^\mu\chi_2)h_1\right]\\
&+\frac{c_1}{2}\left[
h_1\nabla^\mu h_2-h_2\nabla^\mu h_1\right].
\end{split}
\]

On two Einstein tangents, `chi_1=chi_2=0`, so

\[
\omega^\mu\big|_E=\frac{c_1}{2}\omega^\mu_{EH}.
\]

In the Cauchy coordinates `(h,d_t h)`, the restricted matrix is

\[
\Omega_E=\frac{c_1}{2}
\begin{pmatrix}0&1\\-1&0\end{pmatrix},
\]

which has rank two.  The massive branch has the negative of this matrix, and
the cross pairing between the two branches vanishes.  The selected massless
sector is therefore symplectic, while the full split theory retains the
opposite-sign massive sector.

For the repository healthy sign `c1=-1`, the time-translation Hamiltonian is

\[
H_{P_0}=-\frac{c_1}{4}\int_\Sigma
\left[(\partial_t h)^2+|\nabla h|^2\right]>0
\]

per nonzero wave packet.  This agrees exactly with the Einstein-Hilbert
normalization inherited from `c1 R`.

## Where the graviton is

Before selection, each TT helicity contains a massless Einstein root and a
massive spin-2 root.  The two local defect conditions leave one ordinary
massless Cauchy pair for each helicity.  Their direct sum is the conventional
classical helicity-`+/-2` gravitational-wave phase space with a nondegenerate
Einstein-Hilbert pairing and positive `P_0` energy for `c1=-1`.

In the pure-Weyl limit `c1->0`, the restricted matrix goes to zero and the two
simple roots coalesce.  The graviton has not been deleted as a solution; its
separate Einstein-Hilbert normalization disappears in the degenerate
fourth-order theory.

## Precise scope

The theorem is `LORENTZIAN-CAUSAL` only for the source-free flat TT Schwartz
Cauchy problem.  It does not say that the massive branch is absent from the
full Einstein--Weyl theory.

For a generic source,

\[
D_q(D_q+M^2)h=J
\quad\Longrightarrow\quad
(D_q+M^2)\chi=J,
\]

so the defect can be excited.  A source-compatible subcomplex, projected
retarded Green operator, full Diff x Weyl BV--BFV lift, null-infinity charge
theorem, nonlinear constraint propagation theorem, and scattering
equivalence remain open.

Machine certificate:
`bridge/certificates/compensated_einstein_causal_subsector.json`.
