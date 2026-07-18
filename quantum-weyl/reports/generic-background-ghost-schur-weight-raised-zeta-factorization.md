# Generic weight-raised Schur zeta factorization

## Result

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The generic longitudinal ghost Schur operator has order zero,

\[
S_L=I+K,\qquad K\in\Psi^{-2}.
\]

There is no canonical generic numerator/denominator factorization analogous
to the accidental Einstein-background identity
\((\Delta_0-4)(\Delta_0-6)^{-1}\).  The repository does, however, already
freeze the positive order-two scalar weight

\[
Q=\Delta_0+\Pi_0.
\]

The canonical comparison available without inventing another operator is
therefore the **weight-raised factorization**

\[
A=S_LQ,\qquad B=Q.
\]

On a connected admissible stratum with a common Agmon sector, define

\[
m_Q^{\rm wr}(S_L)
=\log\det_\zeta(S_LQ)-\log\det_\zeta Q
-\operatorname{tr}^Q(\log S_L).
\]

The exact four-dimensional local defect is

\[
\boxed{
m_Q^{\rm wr}(S_L)
=-\frac14\operatorname{Wres}(K^2)
=-\frac1{(4\pi)^2}\int_M
\frac{R^2+2R_{\mu\nu}R^{\mu\nu}}{108}\,\mathrm dvol .}
\]

## BCH reduction

Put \(X=\log S_L\in\Psi^{-2}\) and \(Y=\log Q\).  Through the
four-dimensional residue order,

\[
\log(S_LQ)-\log S_L-\log Q
=\frac12[X,Y]+\frac1{12}[Y,[Y,X]]\pmod{\Psi^{-5}}.
\]

The two displayed commutators have orders \(-3\) and \(-4\); the next
independent BCH term \([X,[X,Y]]\) has order \(-6\).  The weighted trace
defect

\[
\operatorname{tr}^Q[U,V]
=-\frac1{\operatorname{ord}Q}\operatorname{Wres}
\bigl(U[V,\log Q]\bigr)
\]

kills both surviving commutators because one entry is \(Y=\log Q\).
Cross terms with \(X\) start below residue order.  Finally,
\((\log(I+K))^2=K^2\pmod{\Psi^{-6}}\), which yields the boxed formula.

## Round-\(S^4\) cross-check and convention audit

For the round unit sphere,

\[
R=12,\qquad |\operatorname{Ric}|^2=36,
\qquad \operatorname{Vol}(S^4)=\frac{8\pi^2}{3},
\]

so

\[
\operatorname{Wres}(K^2)=\frac43,
\qquad m_Q^{\rm wr}(S_L)=-\frac13.
\]

Combining this local defect with the accepted weighted modified determinant
gives

\[
\log\det_\zeta(S_L\Delta_0)-\log\det_\zeta\Delta_0
=-4.3114788189487449608087288881393202539\ldots .
\]

An independent Hurwitz-zeta continuation of the primed scalar spectrum
reproduces this value.

This \(-1/3\) does **not** contradict the separately certified \(5/3\)
defect for

\[
A_E=\Delta_0-4,\qquad B_E=\Delta_0-6.
\]

The two comparisons use different order-raising/factorization conventions;
their defects differ exactly by \(2\).  Multiplicative anomalies are local,
but they are not independent of the chosen factorization.

## Claim boundary

This closes the selected generic four-dimensional local BCH/residue term.  It
does not compute the generic global finite Schur rows, a full vector-block
zeta factorization, the physical fourth-order Hessian, complete
\(\Gamma_1\) or \(Q_1\), residual transfer, a Lorentzian QME, a state, or a
particle theorem.  Generic finite rows still require a primed Green kernel or
equivalent spectral measure.

## Receipts

- Producer:
  `quantum-weyl/spectral/euclidean/generic_background_ghost_schur_weight_raised_zeta_factorization.py`
- Certificate:
  `quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WEIGHT_RAISED_ZETA_FACTORIZATION.json`
- Independent verifier:
  `quantum-weyl/spectral/euclidean/verify_generic_background_ghost_schur_weight_raised_zeta_factorization.py`
- Schema:
  `quantum-weyl/spectral/euclidean/schema/generic-background-ghost-schur-weight-raised-zeta-factorization-v1.schema.json`
