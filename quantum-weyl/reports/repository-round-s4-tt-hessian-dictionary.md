# Repository round-S4 TT Hessian dictionary

Status: `REPOSITORY_ROUND_S4_TT_HESSIAN_FACTORIZED_AND_NORMALIZED`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

On real transverse-traceless symmetric rank-two tensors on the unit round
four-sphere, with

\[
\Delta_2^\perp(M^2)=-\nabla^2+M^2,
\]

the repository action has Hessian

\[
H_{TT}^{\rm repository}
=\frac12\Delta_2^\perp(2)\Delta_2^\perp(4).
\]

The two shifts are independently specialized from the spin-two case of the
round-\(S^4\) conformal-higher-spin factor formula in
[Beccaria--Tseytlin, equation (2.22)](https://arxiv.org/abs/1503.08143).
For \(s=2\), the depth indices \(k=0,1\) give \(M^2=4,2\). This source fixes
the monic constant-curvature operator, not the repository normalization.

The remaining factor is fixed internally. The repository identity

\[
S_{\rm red}=\int\sqrt g\,(R_{ab}R^{ab}-R^2/3)
=\frac12\int\sqrt g\,(C^2-E_4)
\]

gives \(\delta_h\delta_kS_{\rm red}=\langle C_1h,C_1k\rangle\) on a
conformally flat background. Its flat TT quadratic term is
\(\frac14\langle h,p^4h\rangle\), so in
\(S^{(2)}=\frac12\langle h,Hh\rangle\) the monic product is multiplied by
\(+\frac12\). The exact polynomial replay is

\[
\frac12(A+2)(A+4)=\frac12A^2+3A+4,
\qquad A=-\nabla^2.
\]

Both factors are real and formally self-adjoint. Their shifts are strictly
positive relative to the nonnegative rough Laplacian on the compact sphere,
so both factor kernels and the Hessian kernel are zero. The principal symbol
is \(+\frac12|\xi|^4\) on the TT bundle.

The producer and independent verifier are content-addressed by
`REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1.json`; the strict semantic
receiver also recomputes a digest binding every scientific and provenance
field.

## Claim boundary

This closes the repository physical TT operator dictionary and its local
elliptic/zero-mode statement. It does not choose the global determinant
phase, compute a regulated Slavnov breaking, decide the QME, transfer a
quantum residual differential, or establish Lorentzian quantum theory.
