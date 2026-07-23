# Phase-3 axial one-sided Krein scattering preflight

## Disposition

**METHOD_SHORTFALL** for a physical scattering claim; **PASS** for the
conditional exact finite-dimensional theorem.

Dependency boundary: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The committed global-channel gate remains `MISSING_GLOBAL_CONNECTION`.
Scalar outgoing Jost coefficients occur in the analytic factor expansions,
but the repository does not yet certify the typed \(3\times3\) \(T_+\)
entries, their endpoint-frame normalization, or the orientation-correct
global Stokes defect.  The result therefore does not activate a physical
one-sided \(J\)-isometry.

## Exact conditional theorem

Let \(N_-\), \(N_+\), and \(N_H\) satisfy
\[
 N_-^\dagger G_-N_-=N_+^\dagger G_+N_+
 =N_H^\dagger H_{\rm out}N_H=J,
\]
where \(J\) is either
\[
 J_\sigma=\operatorname{diag}(1,-1,-1)
 \quad\hbox{or}\quad
 J_0=\begin{pmatrix}0&1&0\\1&0&0\\0&0&-1\end{pmatrix}.
\]
They are distinct matrices.  With
\[
 Q=2^{-1/2}\begin{pmatrix}1&1&0\\1&-1&0\\0&0&\sqrt2\end{pmatrix},
 \qquad Q^\dagger J_0Q=J_\sigma,
\]
they are exactly congruent.

Assume the typed Stokes identity
\[
 H_{\rm out}+T_+^\dagger G_+T_+
 -T_-^\dagger G_-T_-=0
\]
and \(T_-\in GL(3,\mathbb C)\).  Define the normalized maps
\[
 \widehat T_-=N_-^{-1}T_-N_H,\qquad
 \widehat T_+=N_+^{-1}T_+N_H,
\]
\[
 R=\widehat T_+\widehat T_-^{-1},\qquad
 A=\widehat T_-^{-1},\qquad
 \mathsf S=\binom{R}{A}.
\]
Then
\[
 \mathsf S^\dagger(J\oplus J)\mathsf S=J,\qquad
 D:=J-R^\dagger JR=A^\dagger JA.
\]
Thus \(D\) is nonsingular with inertia \((1,2,0)\).  The embedding
\(\mathsf S:(\mathbb C^3,J)\to(\mathbb C^6,J\oplus J)\) has a nondegenerate
orthogonal complement of inertia \((1,2,0)\).  Choosing an isometry onto
that complement gives a noncanonical algebraic completion
\([\mathsf S\ C]\in U(2,4)\).  This completion is not a constructed physical
full scattering matrix.

## Determinant normalization

In the committed raw frames,
\[
 \det H_{\rm out}
 =\frac{884736}{125}
 \frac{\omega^3(4\omega^2+1)(16\omega^2+1)^2}{\omega^2+1},
\]
whereas
\[
 \det G_-=\frac{14155776}{125}\omega^3.
\]
The latter follows by undoing the factor-adapted incoming basis change,
whose determinant modulus squared is \(9\omega^2\).  Hence
\[
 \frac{\det H_{\rm out}}{\det G_-}
 =\frac{(4\omega^2+1)(16\omega^2+1)^2}
        {16(\omega^2+1)},
\]
exactly the modulus squared of the rational prefactor in \(\det T_-\).
Consequently
\[
 \det D
 =\frac{\det H_{\rm out}}
        {\det G_-\,|\det T_-^{\rm raw}|^2}
 =\frac1{|A_{{\rm in},2}|^4|A_{{\rm in},1}|^2}
 =|\det\widehat T_-|^{-2}.
\]
The bare raw-frame formula
\(\det D=|\det T_-^{\rm raw}|^{-2}\) is false: it omits the endpoint
normalizer determinant ratio.

## Triangular identities

Triangular component equations are meaningful here only in the null frame
\(J_0\).  For the declared upper-triangular convention
\[
 X=\begin{pmatrix}a_X&b_X&d_X\\0&c_X&e_X\\0&0&f_X\end{pmatrix},
 \qquad X\in\{R,A\},
\]
the independent upper-half equations of
\(R^\dagger J_0R+A^\dagger J_0A=J_0\) are
\[
\begin{aligned}
\sum_X\bar a_Xc_X&=1,&
\sum_X\bar a_Xe_X&=0,\\
\sum_X(\bar b_Xc_X+\bar c_Xb_X)&=0,&
\sum_X(\bar b_Xe_X+\bar c_Xd_X)&=0,\\
\sum_X(\bar d_Xe_X+\bar e_Xd_X-|f_X|^2)&=-1.
\end{aligned}
\]
The certificate also records the corresponding lower-triangular equations.
No imported result proves triangularity after the normalized Witt-frame
changes, and the off-diagonal entries are not eliminable from these
relations without further hypotheses.  The proposed
\((\alpha,\gamma,\mu)\) reduction is therefore refused.

## Positive-frequency horizon audit

The local exact future-horizon Gram and factor formula extend from the
printed pilot interval to every real \(\omega>0\).  This promotion is based
on the symbolic recurrence, not only on the final minors:

- the basis denominators are
  \(2\omega-i\), \(4\omega-i\), \(4\omega-3i\),
  \(4\omega-5i\), and \(\omega-i\);
- the residue eigenbasis determinant is
  \(-i(2\omega-i)/8\);
- the three integer resonances have exact zero residual;
- the committed symbolic omitted-head cross-current order is \(2\), so the
  Laurent constant is unaffected;
- all Gram pivots and factor-quotient signs are fixed on \(\omega>0\).

This is only a local horizon-algebra extension.  The scattering conclusion
remains on the pilot band and behind the missing global handoff.

## Receipts

Machine result:
`black_hole_programme/phase3/axial_one_sided_krein_scattering_preflight/certificate.json`.

Scoped producer, independent verifier, and six mutation tests pass.  Tier 2
was limited to content hashes and the exact horizon recurrence audit; Tier 3
was not run because no lifecycle state or paper theorem was promoted.

EVIDENCE: black_hole_programme/phase3/axial_one_sided_krein_scattering_preflight/certificate.json
MISSING-DEP: typed full outgoing Tplus matrix, same-frame normalization, and orientation-correct global Stokes defect on the populated channels
CLOSE-OUT: SHORTFALL — the typed conditional Krein theorem and all-positive-frequency horizon algebra pass, but the physical one-sided scattering identity remains unactivated.
