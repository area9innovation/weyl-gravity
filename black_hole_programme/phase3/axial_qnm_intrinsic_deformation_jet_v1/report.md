# Intrinsic scalar deformation jet — exact scoped result

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`
Lifecycle: `CLASSIFIED`

## Established

The repeated scalar spin-two equations

\[
Ly=0,\qquad Lx+Sy=0
\]

are exactly the first dual-number jet of the auxiliary family
\[
L_\tau=L+\tau S.
\]

In the ordered column basis \((\epsilon,1)\), multiplication by the scalar
connection coefficient \(a+\epsilon b\) is
\[
\begin{pmatrix}a&b\\0&a\end{pmatrix}.
\]

For any differentiable local zero branch of an auxiliary scalar connection
coefficient, at a simple zero,
\[
\omega_n'(0)=-\frac{b(\omega_n)}{a'(\omega_n)}.
\]
Under a compatible operator/connection normalization this reads
\[
\frac{\beta_n}{\alpha_n}=-\omega_n'(0).
\]

This gives an exact interpretation of the still-unevaluated Smith selector as
the first sensitivity of a scalar zero to an intrinsic bookkeeping
deformation.

## Conditional contour moments

On a bounded analytic domain \(D\) whose boundary contains no zero of \(a\),
and assuming the enclosed zeros \(\omega_j\) are distinct and simple, the
local residue calculation gives
\[
N_D=\frac{1}{2\pi i}\oint_{\partial D}\frac{a'}a\,d\omega,
\]
and
\[
K_k=\frac{1}{2\pi i}\oint_{\partial D}
\omega^k\frac ba\,d\omega
=\sum_j\omega_j^k\frac{b(\omega_j)}{a'(\omega_j)}.
\]
For one zero,
\[
K_0=\frac{\beta_n}{\alpha_n}=-\omega_n'(0)
\]
under the compatible normalization already declared above.

If \(\widetilde a=u a\) with \(u\) analytic and zero-free on a neighborhood of
\(\overline D\), then
\[
\frac{\widetilde b}{\widetilde a}
=\frac ba+\frac{u_\tau}{u}.
\]
The added term is analytic, so every \(K_k\) is unchanged. The analogous
\(u'/u\) term leaves \(N_D\) unchanged.

No domain, contour, zero count, or moment is evaluated in this package.

## Conditional finite-cluster algebra

For \(N\) distinct simple zeros, the classes
\[
\kappa_j=\frac{b(\omega_j)}{a'(\omega_j)}
\]
are completely determined by \(K_0,\ldots,K_{N-1}\), because their moment
matrix is the invertible Vandermonde matrix. Define
\[
P_D=\prod_j(\omega-\omega_j),\qquad
Q_D=\sum_j\kappa_j\prod_{m\ne j}(\omega-\omega_m).
\]
Then
\[
Q_D(\omega_j)=\kappa_jP_D'(\omega_j),
\]
so
\[
N_{\rm defective}=N-\deg\gcd(P_D,Q_D),
\]
and \(\operatorname{Res}(P_D,Q_D)\ne0\) precisely when every root is
defective.

The extension resolvent
\[
R_D(z)=\frac{1}{2\pi i}\oint_{\partial D}
\frac{b(\omega)}{(z-\omega)a(\omega)}\,d\omega
=\frac{Q_D(z)}{P_D(z)}
\]
has reduced denominator \(P_D/\gcd(P_D,Q_D)\) and Laurent coefficients
\(K_k\). Its Hankel matrix satisfies
\[
H_N=V\operatorname{diag}(\kappa_j)V^T,
\]
so its rank is the number of defective roots and its radical dimension is
the number of semisimple roots. The reduced denominator supplies the minimal
moment recurrence.

Equivalently, with
\[
G=VV^T,\quad G_1=V\Omega V^T,\quad
H=VKV^T,\quad H_1=VK\Omega V^T,
\]
the commuting operators
\[
M_\omega=G^{-1}G_1,\qquad M_\kappa=G^{-1}H
\]
have joint eigenpairs \((\omega_j,\kappa_j)\), and
\[
H_1=G_1G^{-1}H.
\]
A generic Loewner/shifted-Loewner pencil gives the same defective roots after
rank compression.

These formulas, the resultant sign, recurrence ranks, commuting operators,
and Loewner pencil are independently checked in an exact \(N=3\) model.
Newton identities and centered moments give root-free reconstruction.
Conditional reality consequences are recorded but their physical
hypotheses are not certified.

## Partial jet and the three extension ratios

For
\[
C(\tau)=\begin{pmatrix}a(\tau)&d(\tau)\\0&f\end{pmatrix},
\qquad \partial_\tau f=0,
\]
the partial dual-number functor in the ordered basis
\((\epsilon\,\mathrm{spin2},\mathrm{spin2},\mathrm{spin1})\) is
\[
J(C)=\begin{pmatrix}a&b&c\\0&a&d\\0&0&f\end{pmatrix}.
\]
Exact multiplication and inversion give
\[
J(C_1C_2)=J(C_1)J(C_2),\qquad
J(C^{-1})=J(C)^{-1},
\]
and
\[
-\frac{b}{a^2}=\partial_\tau(a^{-1}),\qquad
M=-\frac{d}{af},\qquad
\partial_\tau M=\frac{bd-ac}{a^2f}.
\]
These identities organize the three extension ratios. Applying them to
\(T_-\), \(T_+\), or a scattering identity requires compatible endpoint
partial-jet frames induced by the same \(\tau\)-family. No outgoing map is
recovered here.

## Conditional Jost determinant tangent

For analytic columns
\[
X_H(\tau)=X_H+\tau Y_H,\qquad
X_+(\tau)=X_++\tau Y_+,
\]
the exact finite determinant identity is
\[
\left.\partial_\tau\det(X_H(\tau),X_+(\tau))\right|_0
=\det(X_H,Y_+)+\det(Y_H,X_+).
\]
Identifying these columns with physical horizon and infinity Jost frames
requires the endpoint-compatible analytic construction that remains open.

## Conditional global statements

The identification \(b(\omega)=\partial_\tau a(\omega,\tau)|_0\) requires an
analytic scalar family on a common radial domain and analytic
endpoint-compatible horizon/infinity frames. Those objects are not
constructed by this package.

Differentiating the scalar flux law is exact once a real/self-adjoint
\(L_\tau\) family and compatible Wronskian normalization are supplied. These
hypotheses are not certified here.

## Claim boundary

The result does not evaluate \(b\) or \(\beta_n\) at a physical QNM and does
not select a Smith branch. It establishes no exceptional point, physical
Fredholm realization, resolvent pole, generalized ringdown term, scattering
map, evaluated contour moment, certified QNM zero count, physical cluster
polynomial, Hankel rank, recurrence, Loewner spectrum, or flux theorem. The
auxiliary \(\tau\) is not asserted to be a physical parameter or a changed
fundamental theory.

CLOSE-OUT: DONE — exact dual-number jet and conditional simple-zero sensitivity identities certified without promoting a physical QNM result.
EVIDENCE: black_hole_programme/phase3/axial_qnm_intrinsic_deformation_jet_v1/certificate.json
