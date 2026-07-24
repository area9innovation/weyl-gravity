# Phase 4 channel-factorized fundamental-symmetry pullback test

Date: 2026-07-24  
Dependency tags: `REDUCED-MODE`, `LORENTZIAN-CAUSAL`  
Lifecycle: `CLASSIFIED`

## Exact theorem

Let \(G\), \(H_{\mathcal H^+}\), and \(G_+\) be nondegenerate Hermitian
forms, and suppose \(T_-\) and \(T_+\) are invertible.  Put
\[
A=T_-^{-1},\qquad R=T_+T_-^{-1},
\]
\[
K_H=A^\dagger H_{\mathcal H^+}A,\qquad
K_+=R^\dagger G_+R=G-K_H,
\qquad L_H=G^{-1}K_H.
\]
Then a common incoming fundamental symmetry \(C_-\), transported to separate
positive horizon and outgoing fundamental symmetries, exists if and only if
\[
\boxed{L_H\ \text{is diagonalizable and}\ 
\operatorname{spec}(L_H)\subset(0,1).}
\]

Necessity follows because common self-adjointness implies
\([C_-,L_H]=0\).  With \(H_0=GC_->0\),
\[
K_HC_-=H_0L_H>0,\qquad K_+C_-=H_0(I-L_H)>0.
\]
Thus \(L_H\) is positive-self-adjoint and lies strictly between zero and one.

Conversely, the real eigenspaces of a diagonalizable \(G\)-self-adjoint
\(L_H\) are mutually \(G\)-orthogonal and nondegenerate.  Choosing a
fundamental symmetry on each eigenspace gives a direct-sum \(C_-\) commuting
with \(L_H\); eigenvalues in \((0,1)\) make both channel pullback metrics
positive.  The channel symmetries are
\[
C_H=AC_-A^{-1},\qquad C_+=RC_-R^{-1}.
\]

Exact positive, negative-eigenvalue, nonreal-pair, and Jordan-block fixtures
independently test every clause.

## Physical-cell audit

On \(I_0=[0.49995,0.50005]\), the committed authorities provide:

- the exact incoming Gram \(G_-\), of rank three;
- the exact future-horizon outward Gram, of rank three;
- analytic invertibility of \(T_-\);
- certified invertibility of \(T_+\) throughout \(I_0\).

They do **not** provide the full typed entries of
\[
T_-:(XH0a,XH0b,EH0)\longrightarrow(XI0,XI1,EI0).
\]
The earlier transport-free certificate explicitly records
`certified_full_typed_Tminus_matrix_available=false`.  A diagnostic point
matrix is not an interval enclosure and has a nonzero old Stokes residual, so
it is inadmissible.

Consequently \(K_H=A^\dagger H_{\mathcal H^+}A\) cannot yet be assembled, and
the physical generalized spectrum is neither certified positive nor
certified obstructed.

The determinant audit is
\[
\det L_H=
|\det A|^2\frac{\det H_{\mathcal H^+}}{\det G_-},
\]
not merely \(|\det A|^2\).  In the certified normalization the endpoint ratio
cancels the rational prefactor in \(\det T_-\), leaving
\[
\det L_H=
\frac1{|A_{{\rm in},2}|^4|A_{{\rm in},1}|^2}.
\]
The scalar cell bounds imply
\[
0<\det L_H<0.9786517263238609335725310374971461731.
\]
This product constraint is compatible with the desired spectrum but does not
determine the three eigenvalues or diagonalizability.

## Disposition

The spectral criterion is theorem-level and transport-free.  Its physical
evaluation is a fail-closed shortfall pending one full typed \(3\times3\)
\(T_-\) enclosure on the cell, or an explicitly conjugated equivalent with a
certified basis crosswalk.  No explicit \(T_+\) entries are required.

## Verification

```bash
python3 -m black_hole_programme.phase4.channel_factorized_c_pullback_test_v1.produce
python3 -m black_hole_programme.phase4.channel_factorized_c_pullback_test_v1.verify
python3 -m unittest -v black_hole_programme.phase4.channel_factorized_c_pullback_test_v1.test_pullback
```

## Does not establish

- existence or obstruction of a channel-factorized \(C\) on the physical cell;
- the generalized eigenvalues of \((K_H,G_-)\);
- a full typed \(T_-\) or explicit \(T_+\) matrix;
- canonical, causal, covariant, BRST, time-domain, or quantum positivity.

CLOSE-OUT: SHORTFALL — the exact criterion and decisive input audit are
complete, but the physical pencil is undefined without full typed
\(T_-\) entries.

EVIDENCE:
`black_hole_programme/phase4/channel_factorized_c_pullback_test_v1/certificate.json`

MISSING-DEP: `CERTIFIED_FULL_TYPED_TMINUS_MATRIX_ON_CELL`
