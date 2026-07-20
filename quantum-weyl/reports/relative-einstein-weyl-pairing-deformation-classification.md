# Relative Einstein--Weyl pairing-deformation classification

The standard compact-product Einstein--Maxwell to Weyl--Maxwell cyclic
pushforward remains obstructed: its generic \(q\)-primary action forms have
inertia \((2,0)\) and \((1,1)\), respectively. This result classifies the
smallest ways to cross that wall after explicitly changing the reduced
pairing, quadratic action, or physical auxiliary content.

For either parity, let \(E\) be the Einstein form and \(W\) the Weyl
\(q\)-primary form. The complete real symmetric target deformation is

\[
\Delta=\begin{pmatrix}a&b\\b&c\end{pmatrix}.
\]

It repairs the fibre exactly when \(W+\Delta\) is positive definite. Modulo
real congruence, that positive region is one orbit. A rank-one deformation
\(\Delta=t vv^T\) repairs precisely when

\[
v^TW^{-1}v<0,\qquad t>-\frac1{v^TW^{-1}v};
\]

equality is the complete rank-one signature wall. Rank zero cannot change
inertia, so rank one is minimal.

## Exact minimal representatives

For \(\lambda=\ell(\ell+1)\ge6\), the axial representative is

\[
\Delta_A=\operatorname{diag}(0,9\lambda),\qquad
S_A=\begin{pmatrix}1&-3\\0&1\end{pmatrix},
\qquad
S_A^T(W_A+\Delta_A)S_A=E_A.
\]

Its wall is \(t=9\lambda-2\); the exact determinants at \(t-1,t,t+1\)
are \(-\lambda,0,\lambda\).

The polar representative is

\[
\Delta_P=\operatorname{diag}\!\left(
0,\frac34(\lambda-2)(3\lambda+2)\right),
\qquad
S_P=\begin{pmatrix}
\frac12&\frac{3\lambda-2}{4}\\0&1
\end{pmatrix},
\]

and \(S_P^T(W_P+\Delta_P)S_P=E_P\). Its wall is
\((\lambda-2)(9\lambda-2)/4\), with determinant mutations
\(-4,0,4\).

The same congruences describe the dual rank-one source-action changes
\(S^TWS=E-\Delta\). Those changes alter the Einstein reduced Hessian,
equations, and action.

## Auxiliary alternative and price

If an auxiliary cohomology form has inertia \((r,s)\), then
\(W\oplus A\) contains an Einstein-positive two-plane exactly when
\(r\ge1\). Thus one positive, same-frequency \(q\)-primary physical
direction is minimal. The certificate supplies explicit axial and polar
embeddings and types each added degree-zero field together with its
degree-one BV cotangent dual.

Contractible pairs do not alter cohomology inertia and cannot repair the
obstruction. A physical auxiliary does, but changes the equations and
residual content.

## Disposition

The minimal changed object is
`PAIRING_CHANGED_GENERIC_Q_PRIMARY_RELATIVE_COMPLEX_V1`: the mapping cone of
the displayed polynomial cyclic isomorphisms on the generic reduced
cohomology fibres. It preserves the real structure, product labels, and
separation from the unequal-frequency \(p\) shell.

This is not a repair of the standard action theory. Pairing-only repair keeps
the original equations but abandons the action-derived Weyl pairing.
Action and auxiliary repairs change the theory. No full off-shell
\(40\)-to-\(38\) chain lift or four-dimensional covariant changed action has
been constructed, so matched insertions and a relative QME remain
unauthorized.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

This result does not establish anomaly coefficients, QME restoration,
Lorentzian causality, positivity, a state, particles, scattering, or
unitarity.

CLOSE-OUT: DONE — complete generic reduced deformation regions classified and minimal changed pairing/auxiliary representatives constructed
EVIDENCE: quantum-weyl/transfer/certificates/RELATIVE_EINSTEIN_WEYL_PAIRING_DEFORMATION_CLASSIFICATION.json
