# Transport-free outgoing defect and abstract one-sided Stokes theorem

Dependency tags: `LORENTZIAN-CAUSAL`, `REDUCED-MODE`

Status:
`ABSTRACT_RAW_PSEUDO_ISOMETRY_ACTIVE_DET_O_INPUT_OPEN`.

## Typed orientation

The exact raw bases are

\[
\mathcal B_-=(XI0,XI1,EI0),\qquad
\mathcal B_H=(XH0a,XH0b,EH0),\qquad
\mathcal B_+=(XI2,XI3,EI2).
\]

All forms are divided by \(\pi\alpha_{\rm W}\). The past-null form has the
past-boundary minus sign, the outgoing-null form has the future-boundary
plus sign, and the future horizon is the inner boundary and therefore also
has a radial minus sign. The exact one-sided identity is

\[
H_{\rm out}+T_+^\dagger G_+T_+
-T_-^\dagger G_-T_-=0.
\]

No intuitive sign choice is used.

## Tier A: determinant route

Define

\[
O=T_-^\dagger G_-T_- - H_{\rm out}.
\]

Then Stokes gives \(O=T_+^\dagger G_+T_+\), hence

\[
\det O=\det G_+|\det T_+|^2.
\]

Because \(G_+\) is exactly nondegenerate, \(\det O\ne0\) is equivalent to
\(T_+\) being invertible.

This test is invariant under every typed endpoint basis change. If
\(B_-'=B_-N\) and \(H'=HM\), then

\[
T_-'=N^{-1}T_-M,\qquad O'=M^\dagger OM.
\]

The genuine missing input is a certified full \(3\times3\) \(T_-\) matrix
or enclosure in these bases. The analytic incoming certificate proves its
determinant and invertibility but does not provide its entries.

The old unvalidated \(\omega=1/2\) point matrix is classified here only as
`OBSERVED`. After the exact
\(R=32\) amplitude crosswalk, gives a diagnostic

\[
\det O\approx2.3811747,
\]

with inertia \((1,2)\) and smallest absolute eigenvalue about \(0.0298\).
This is not a certificate: that matrix has no enclosure and its recorded
Stokes residual is nonzero.

The machine-readable missing-object ledger records the exact remaining
artifacts: a certified full typed \(T_-\) matrix for the determinant test,
an explicit \(T_+\) matrix for evaluated outgoing population and reflection,
and explicit common-\(J\) congruence frames for a numerical signature-basis
scattering matrix.

## Tier B: abstract pseudo-isometry

Full \(T_+\) entries are not mathematically necessary for the abstract
theorem. The certified six-column infinity basis and future-regular horizon
family define the trace block \(T_+\) by unique global ODE expansion. Exact
radial-current conservation, wrong-endpoint suppression, wave-packet trace
existence and trace-limit interchange give the displayed Stokes identity.

Since \(T_-\) is invertible, the raw map

\[
\mathscr S_{\rm raw}x=
\begin{pmatrix}
T_+T_-^{-1}x\\
T_-^{-1}x
\end{pmatrix}
\]

satisfies

\[
\mathscr S_{\rm raw}^\dagger
(G_+\oplus H_{\rm out})\mathscr S_{\rm raw}=G_-.
\]

It is injective because its horizon component is invertible. Since all
three forms have inertia \((1,2,0)\), an abstract common-\(J\)
normalization exists by Hermitian Sylvester congruence. No explicit
normalizers or outgoing entries are claimed.

## Boundary

The abstract pseudo-isometric embedding is activated. Outgoing population,
\(\operatorname{rank}T_+\), \(\det O\ne0\), a numerical reflection map,
direct-integral bounds, stability and quantum claims remain open.
