# Axial QNM intrinsic-deformation jet v1

This scoped exact package classifies the repeated scalar spin-two block as a
first dual-number jet.

It imports, by content hash:

- the exact nontrivial projective cocycle certificate; and
- the exact local QNM Smith-dichotomy certificate.

It proves only formal algebra:

1. \(L_\tau=L+\tau S\), \(y_\tau=y+\tau x\) gives
   \(Ly=0\) and \(Lx+Sy=0\) modulo \(\tau^2\);
2. multiplication by \(a+\epsilon b\) has matrix
   \(\left(\begin{smallmatrix}a&b\\0&a\end{smallmatrix}\right)\) in the
   ordered column basis \((\epsilon,1)\);
3. at a simple zero of an auxiliary differentiable scalar family,
   \(\omega_n'(0)=-b/a'\), hence
   \(\beta_n/\alpha_n=-\omega_n'(0)\) under compatible normalization;
4. on a declared analytic domain with distinct simple zeros,
   \[
   K_k=\frac{1}{2\pi i}\oint \omega^k\frac{b}{a}\,d\omega
   =\sum_j\omega_j^k\frac{b(\omega_j)}{a'(\omega_j)};
   \]
5. these moments are invariant under zero-free analytic endpoint
   renormalizations; and
6. the first variation of a \(2\times2\) Jost determinant is
   \[
   \det(X_H,Y_+)+\det(Y_H,X_+).
   \]

Conditionally on a contour enclosing \(N\) distinct simple zeros, the same
moments determine the finite cluster algebra:

- \(P_D=\prod_j(\omega-\omega_j)\) and
  \(Q_D(\omega_j)=\kappa_jP_D'(\omega_j)\);
- \(N_{\rm defective}=N-\deg\gcd(P_D,Q_D)\);
- the extension resolvent is \(R_D=Q_D/P_D\), reduced by that gcd;
- its Laurent coefficients are the moments \(K_k\);
- the Hankel matrix has rank equal to the number of defective roots;
- a generic Loewner pencil recovers precisely those defective roots; and
- the commuting multiplication operators recover the joint pairs
  \((\omega_j,\kappa_j)\).

The generic statements are independently audited in an exact \(N=3\) model.
Reality-symmetry consequences are recorded only conditionally.

For the partial jet
\[
C(\tau)=\begin{pmatrix}a(\tau)&d(\tau)\\0&f\end{pmatrix},
\qquad \partial_\tau f=0,
\]
the ordered basis \((\epsilon\,\mathrm{spin2},\mathrm{spin2},\mathrm{spin1})\)
gives
\[
J(C)=\begin{pmatrix}a&b&c\\0&a&d\\0&0&f\end{pmatrix}.
\]
The package verifies functoriality under products and inverses and identifies
the three inverse ratios as first variations. This does not recover \(T_+\):
physical use requires endpoint frames induced by one matching
\(\tau\)-family.

The auxiliary \(\tau\) is a bookkeeping deformation, not a new physical
coupling. The global identification \(b=\partial_\tau a|_0\) requires
analytic endpoint-compatible scalar connection frames that are not
constructed here. The differentiated scalar flux identity additionally
requires a real/self-adjoint scalar family and compatible Wronskian
normalization.

The contour-moment and Jost-determinant statements are conditional on their
declared analytic domain and endpoint-frame hypotheses. No contour or zero
count, cluster polynomial, Hankel rank, recurrence, or Loewner spectrum is
supplied or evaluated.

No physical QNM, \(\beta_n\), Smith branch, exceptional point, Fredholm
realization, resolvent pole, or flux theorem is established.

## Reproduce and verify

From the standalone `weyl-gravity` repository root:

```bash
PYTHONPATH=. python3 -m black_hole_programme.phase3.axial_qnm_intrinsic_deformation_jet_v1.produce
PYTHONPATH=. python3 -m black_hole_programme.phase3.axial_qnm_intrinsic_deformation_jet_v1.verify
PYTHONPATH=. python3 -m unittest -v black_hole_programme.phase3.axial_qnm_intrinsic_deformation_jet_v1.test_intrinsic_deformation_jet
```
