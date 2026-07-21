# Four-derivative Einstein–Maxwell action response

## Result

The minimal reduced source-action repair requested by the Quantum stream has
no four-dimensional lift within the complete real parity-even local
Einstein–Maxwell action basis through four derivatives.

The conclusion is an exact cokernel theorem, not a failure to guess a useful
counterterm.  After Bianchi identities, integration by parts, the Euler and
Pontryagin exclusions, and bounded action-equivalent field redefinitions, the
action quotient is

\[
  \{1,\ R,\ F^2,\ R_{abcd}F^{ab}F^{cd},\ (F^2)^2,\ (F{}^\star F)^2\}.
\]

The raw four-derivative space has ten parity-even generators.  Seven
independent relations leave the three representatives

\[
  R_{abcd}F^{ab}F^{cd},\qquad (F^2)^2,\qquad (F{}^\star F)^2.
\]

The exact relation matrix and bounded field redefinitions are stored in
`EINSTEIN_MAXWELL_FOUR_DERIVATIVE_ACTION_RESPONSE_V1`.
This quotient agrees with the parity-even Einstein--Maxwell EFT basis in
I. Davies and H. S. Reall, *Well-posed formulation of Einstein-Maxwell
effective field theory*, arXiv:2112.05603, eqs. (1)--(4).  Their curvature
representative \(R_{abcd}({}^\star F)^{ab}({}^\star F)^{cd}\) differs from
the representative used here only by the certified Ricci/\(RF^2\)
field-redefinition span.

## Frozen q-primary response

In the axial rest-frame source coordinates \((h_x,q_x)\), a general action in
the quotient has response

\[
\begin{pmatrix}
2c_R\lambda&
8c_{RFF}\lambda\\
8c_{RFF}\lambda&
-8c_F-32c_{F^4}+64c_{P^2}
\end{pmatrix}.
\]

In the polar source coordinates \((K,U)\), the response is

\[
\begin{pmatrix}
2c_R+4c_{RFF}&-4c_R-8c_{RFF}\lambda\\
-4c_R-8c_{RFF}\lambda&
-8c_F\lambda-32c_{F^4}\lambda
\end{pmatrix}.
\]

The normalization is independently anchored by

\[
\frac12 R-\frac14F^2
\quad\longmapsto\quad
E_A=\operatorname{diag}(\lambda,2),\qquad
E_P=\begin{pmatrix}1&-2\\-2&2\lambda\end{pmatrix}.
\]

The requested source-action shifts are

\[
\Delta_A=\operatorname{diag}(0,-9\lambda),\qquad
\Delta_P=\operatorname{diag}\!\left(
0,-\frac34(\lambda-2)(3\lambda+2)\right).
\]

Two exact dual witnesses separate them from the response image:

1. the coefficient of \(\lambda\) in the axial \((2,2)\) entry vanishes on
   every basis response but equals \(-9\) on \(\Delta_A\);
2. the coefficient of \(\lambda^2\) in the polar \((2,2)\) entry vanishes on
   every basis response but equals \(-9/4\) on \(\Delta_P\).

The first witness alone proves the unrestricted q-primary coefficient system
empty.

## Background and p-primary controls

Keeping the same compact magnetic product imposes the two independent
incidence rows

\[
\begin{aligned}
c_0+2c_R+2c_F+4c_{RFF}+4c_{F^4}&=0,\\
2c_0-4c_F-16c_{RFF}-24c_{F^4}&=0.
\end{aligned}
\]

These can only shrink the already empty q-primary solution set.

The covariant Hessian was also polarized between the frozen q-source
embedding and both certified p-primary representatives.  After reduction on
\(\omega^2-k^2=\lambda-2/3\), every axial and polar cross block is stored
in the certificate.  The coefficientwise zero-cross system has rank six on
the six-dimensional action quotient, hence its kernel is zero.  Thus no
nonzero action deformation in this class preserves the declared p-shell
separation.

## Noether completion

Every representative is an action density, so the completion uses the
unchanged frozen Diff \(\times U(1)\) gauge generator \(G\), its covariant
mixed Hessian \(H_c\), and the identity rows \(-G^\dagger\).  On the two-row
background incidence locus,

\[
H_cG=0,\qquad G^\dagger H_c=0.
\]

This gives the full \(5+14+14+5=38\)-row minimal carrier.  For an individual
density away from its own stationary point, the differentiated Noether
identity includes its background tadpole; the certificate does not
incorrectly assert \(H_I G=0\) there.

## Independent rail

The independent verifier constructs all six densities directly in the exact
compact-product tensor Taylor algebra.  It polarizes their second variations,
substitutes independent axial and polar harmonics, integrates exactly after
\(z=\cos\theta\), and replays the q and p response tables at four physical
fibres.  It does not import the producer matrices.

## Boundary

This is a `LOCAL-ALGEBRAIC` and `REDUCED-MODE` no-lift theorem at a declared
four-derivative and field-content bound.  It does not rule out six-derivative
actions, new physical auxiliaries, nonlocal actions, or pairing-only changes.
It supplies no anomaly, QME, positivity, causal, particle, scattering, or
unitarity conclusion.
