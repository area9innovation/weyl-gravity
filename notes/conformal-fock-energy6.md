# C2g-E6: relative primary scalars at matter weight six

## Scope

`symbolic/verify_conformal_fock_energy6.py` extends the normalized bosonic
Fock construction from C2g-F through total matter energy six.  It includes
all one- and two-particle sectors and the first three-particle sector,
`Sym^3(H_2)`.

This is a relative free-matter diagnostic, not a new physical-state sector.
The independent C2g-N6 Cartan-localization theorem contracts the associated
absolute residual complex.  This rail neither combines the global complex
with local Diff `x` Weyl BV/BRST nor acts with the Weyl interaction.

## Exact shell inventory

At energy six the particle sectors are

\[
\begin{array}{c|c|c}
N&\text{sector}&\dim\\ \hline
1&\mathcal H_6&202\\
2&\mathcal H_2\otimes\mathcal H_4
\oplus\operatorname{Sym}^2\mathcal H_3&820+820=1640\\
3&\operatorname{Sym}^3\mathcal H_2&220.
\end{array}
\]

Therefore

\[
\boxed{\dim\mathcal F_6=2062}.
\]

The cumulative buffer dimensions are

\[
(1,10,40,137,536,2062)
\]

at energies `(0,2,3,4,5,6)`, for total dimension `2786`.

## Scalar inventory

Compact representation theory leaves no one-particle scalar.  The complete
two-particle scalar list consists, for each chirality, of

\[
E_2L_4,
\qquad
\operatorname{Sym}^2(E_3),
\qquad
\operatorname{Sym}^2(A_3).
\]

The three-particle sector contributes one scalar in each of

\[
\operatorname{Sym}^3(E_2^+),
\qquad
\operatorname{Sym}^3(E_2^-).
\]

Thus the complete compact-scalar candidate space has dimension eight.  The
script constructs all eight as exact normalized occupation vectors and
checks every compact generator directly.

## Relative primary condition

The remaining equations are

\[
K^-_M|\Psi\rangle=0
\]

for all four magnetic components.  The executable stacks their exact maps
from the eight-dimensional scalar space into the complete energy-five shell
and computes the nullspace exactly.  Particle number and chirality split the
answer into four independent sectors:

For normalized scalar candidates, one exact basis is

\[
\begin{aligned}
|P_{2,s}\rangle={}&
\frac{\sqrt{10}}4|E_2^sL_4^s\rangle_0
+\frac{\sqrt6}{8}|E_3^sE_3^s\rangle_0
+|A_3^sA_3^s\rangle_0,\\
|P_{3,s}\rangle={}&|E_2^sE_2^sE_2^s\rangle_0,
\qquad s=+,-.
\end{aligned}
\]

Thus the exact relative dimension and decomposition are

\[
\boxed{\dim\mathcal P^{\rm rel}_6=4},
\]

with one vector in each sector

\[
N=2,(+,+);\quad N=3,(+,+,+);\quad
N=2,(-,-);\quad N=3,(-,-,-).
\]

Their unnormalized restricted Gram matrix is

\[
G_{\rm rel}
=\operatorname{diag}\left(\frac{15}{32},1,\frac{15}{32},1\right).
\]

It is nondegenerate and its normalized signature is

\[
\boxed{(+,+,+,+)}.
\]

## Absolute Cartan contraction

The four relative vectors do **not** survive the absolute residual complex.
Matter weight six corresponds to residual total degree

\[
\delta=6-4=2.
\]

The independent C2g-N6 rail proves

\[
d\,\iota_D+\iota_Dd=2I.
\]

Therefore `i_D/2` is a contracting homotopy and

\[
\boxed{H_{\rm absolute}^{\delta=2}=0}
\]

sector by sector.  The present kernel is retained only as a precise
relative-versus-absolute diagnostic.

## Verification

The full sparse Fock construction verifies:

- the exact `2062`-state shell inventory;
- the multiplicative Fock fundamental symmetry;
- compact `J`-self-adjointness;
- `K^+=J K^{-\dagger}J`;
- exact compact grades; and
- the complete `[K^-,K^+]` bracket on the largest interior shell, energy
  five.

The relative kernel is additionally checked directly against all six compact
rotations and all four lowering generators.

## Fail-closed boundary

The script rejects requests for:

1. treating the relative kernel as nonzero absolute global-BRST cohomology;
2. local Diff `x` Weyl BV/BRST cohomology; and
3. interaction matrix elements or probability claims.
