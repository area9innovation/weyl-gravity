# Berger free-dilation Hadamard bisolution seed

Dependency tag: `LORENTZIAN-CAUSAL`

## Result

The free rank-20 metric companion

\[
C_{\rm free}=
\begin{pmatrix}
\Box_2&-I_{10}\\
0&\Box_2
\end{pmatrix}
\]

has scalar normally-hyperbolic principal symbol.  Its rank-40 adjoint dilation

\[
D_{\rm free}=\operatorname{diag}(C_{\rm free},C_{\rm free}^{\dagger})
\]

is formally self-adjoint for the nondegenerate off-diagonal Hermitian form

\[
H=\begin{pmatrix}0&I_{20}\\I_{20}&0\end{pmatrix}.
\]

The hypotheses of Islam--Strohmaier, Theorem 1.4, therefore hold.  A global
Feynman propagator \(G_{F,D_{\rm free}}\) exists and

\[
\omega_{D_{\rm free}}
=-i(G_{F,D_{\rm free}}-G_{{\rm adv},D_{\rm free}})
\]

is an exact, formally self-adjoint global Hadamard bisolution.  This closes
the previously independent free global-bisolution gate.

## Positivity boundary

The form \(H\) has signature \((20,20)\).  Moreover, the nonzero `-I`
incidence makes the modewise free companion a Jordan block
\(\left(\begin{smallmatrix}\lambda&-1\\0&\lambda\end{smallmatrix}\right)\).
A self-adjoint operator for a positive-definite fibre metric would be
diagonalizable, so no such metric symmetrizes this same auxiliary carrier.
Consequently the theorem supplies a Hadamard bisolution here, not a positive
state.

The next physical gates are:

1. prove convergence of the cutoff Volterra kernels and their formal
   transposes in the fixed \(\mathcal D'_{\Gamma_\pm}\) normal topology;
2. transport the free bisolution through the certified regular Cauchy
   morphisms;
3. normalize the transported distribution against the graded CCR/Krein
   pairing;
4. restrict to the raw companion and full graded BV carrier and verify the
   BRST Ward identity;
5. test positivity on physical BRST cohomology.

No interacting companion Hadamard function, positive state, full-BV
Hadamard state, renormalized Lorentzian product, QME or quantum theory is
certified.

## Primary source

Onirban Islam and Alexander Strohmaier, *On microlocalisation and the
construction of Feynman Propagators for normally hyperbolic operators*,
arXiv:2012.09767v4, Theorem 1.4, DOI 10.4310/CAG.241204020919.
