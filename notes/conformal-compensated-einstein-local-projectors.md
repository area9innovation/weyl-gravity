# Local Einstein/massive projectors in the compensated TT theory

## Theorem

For the flat compensated TT equation

\[
Lh=\Box(\Box+M^2)h=0,
\qquad M^2\ne0,
\]

define

\[
\Pi_E=1+\frac{\Box}{M^2},
\qquad
\Pi_M=-\frac{\Box}{M^2}.
\]

In the on-shell polynomial ring

\[
\mathbb Q(M^2)[y]/\big(y(y+M^2)\big),
\]

they obey

\[
\Pi_E+\Pi_M=1,
\qquad
\Pi_E^2=\Pi_E,
\qquad
\Pi_M^2=\Pi_M,
\qquad
\Pi_E\Pi_M=0.
\]

Their images satisfy

\[
\Box\Pi_Eh=0,
\qquad
(\Box+M^2)\Pi_Mh=0.
\]

Thus every source-free TT solution splits uniquely as

\[
h=h_E+h_M,
\qquad h_E=\Pi_Eh,
\qquad h_M=\Pi_Mh.
\]

## Cauchy realization

For

\[
X=(h,\dot h,\ddot h,\dddot h)
\]

the Einstein projector begins with

\[
\begin{pmatrix}h_E\\\dot h_E\end{pmatrix}
=
\begin{pmatrix}
(q+M^2)/M^2&0&1/M^2&0\\
0&(q+M^2)/M^2&0&1/M^2
\end{pmatrix}X.
\]

The remaining two rows are the massless wave consequences
`ddot(h_E)=-q h_E` and `d_t^3(h_E)=-q dot(h_E)`.  With `P_M=I-P_E`, the
machine certificate proves

\[
P_E^2=P_E,\quad P_M^2=P_M,\quad
P_EP_M=P_MP_E=0,\quad P_E+P_M=I,
\]

and

\[
[P_E,A_4]=[P_M,A_4]=0.
\]

The projectors therefore split the complete fourth-order Cauchy evolution,
not merely individual harmonic solutions.

## Symplectic splitting

Let `Omega` be the certified Einstein--Weyl Cauchy form.  The projectors are
symplectically self-adjoint:

\[
P_E^T\Omega=\Omega P_E,
\qquad
P_M^T\Omega=\Omega P_M.
\]

Moreover,

\[
P_E^T\Omega P_M=0.
\]

On the embedded branch coordinates,

\[
I_E^T\Omega I_E=\frac{c_1}{2}J_2,
\qquad
I_M^T\Omega I_M=-\frac{c_1}{2}J_2.
\]

This identifies the differential branch splitting with the previously
certified symplectic block decomposition.

## Locality and support

Both projectors are constant-coefficient differential operators of order two.
Consequently, for smooth fields or distributions,

\[
\operatorname{supp}(\Pi_Ef)\subseteq\operatorname{supp}(f),
\qquad
\operatorname{supp}(\Pi_Mf)\subseteq\operatorname{supp}(f).
\]

The free branch splitting creates no spacelike tail and requires no future
boundary data.

This locality statement starts after TT reduction.  Constructing a spatial TT
representative from a general metric perturbation can require inverse elliptic
operators.  The theorem therefore does not provide a local projector on the
unreduced Diff x Weyl metric BV complex.

## Zero momentum and pure-Weyl limits

The projectors contain `1/M^2`, but no `1/q` or `1/|k|`.  They are therefore
algebraically regular at `q=0` whenever `M^2 != 0`.  The earlier wave-packet
domain excludes `k=0` because a global helicity frame and radiative
polarization basis degenerate there, not because the branch projectors are
singular.

By contrast, the pure-Weyl limit is singular:

\[
M^2\to0
\quad\Longrightarrow\quad
\Pi_E,\Pi_M\text{ singular}.
\]

This is exactly the coalescence of the massless and massive roots into the
fourth-order Jordan block.

## Source audit

For

\[
\Box(\Box+M^2)h=J,
\]

the same differential operators give

\[
\Box(\Pi_Eh)=\frac{J}{M^2},
\qquad
(\Box+M^2)(\Pi_Mh)=-\frac{J}{M^2}.
\]

Thus the projectors split a sourced response into two oppositely sourced
branches.  They do not prove that a generic source preserves the Einstein-only
sector.  In this scalar TT equation, `Pi_M h=0` is compatible only when `J=0`.

For Einstein matter or nonlinear gravitational sources, the correct object is
a gauge-covariant defect measured relative to the sourced Einstein equation,
not the vacuum condition `Box h=0` imposed unchanged.

## Next object

The sourced-defect preflight is now recorded in
`notes/conformal-compensated-einstein-sourced-defect-preflight.md`.  It proves
that a conventional same-source Einstein solution lies in the linearized
Einstein--Weyl theory only when the independent tensor condition `Q(T)=0`
holds.  Conservation and the compensator trace Ward identity do not imply this
condition.

The next theorem must therefore construct **or refute** the appropriate
Einstein sector.  A fixed external source gives an affine defect-zero locus,
not a BV subcomplex.  The next constructive gate is a certified compensated
metric--scalar quadratic BV complex; only then can the defect be lifted to a
chain map and its retarded/advanced propagation tested.

Machine certificate:
`bridge/certificates/compensated_einstein_local_projectors.json`.
