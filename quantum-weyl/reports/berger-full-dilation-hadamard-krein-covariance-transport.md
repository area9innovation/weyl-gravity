# Berger full-dilation Hadamard Krein covariance transport

Result:
`BERGER_FULL_DILATION_HADAMARD_KREIN_CCR_COVARIANCE`

Dependency tag: `LORENTZIAN-CAUSAL`.

## Result

The normalized global Hadamard Krein covariance on the free rank-40
Hermitian dilation now transports across the two certified Cauchy GreenHyp
morphisms

\[
D_{\rm free}\longrightarrow D_\chi\longrightarrow D_{\rm full}.
\]

For a Cauchy morphism \(S:P_1\to P_2\), choose an inverse morphism
\(L:P_2\to P_1\) on the equation-of-motion quotient,
\(\widehat L=\widehat S^{-1}\). The pushed two-point distribution is

\[
W_2=W_1\circ(L^\sharp\otimes L^\sharp).
\]

The Pauli--Jordan distribution obeys the same transport law. For the
composite \(T=L_-\circ L_+\),

\[
\begin{aligned}
W_{\rm full}-W_{\rm full}^{T}
 &=(W_{\rm free}-W_{\rm free}^{T})
   \circ(T^\sharp\otimes T^\sharp)\\
 &=iE_{\rm free}\circ(T^\sharp\otimes T^\sharp)
 =iE_{\rm full}.
\end{aligned}
\]

Thus both the cutoff and full metric dilations have global Hadamard Krein
covariances with exactly normalized CCR. The inverse-morphism construction is
independent of its representative modulo the field equations.

The normal-topology convergence certificate supplies the cone action for the
inverse response morphisms. Two applications of the regular pullback theorem
therefore preserve the Hadamard wavefront relation.

## Theorem source and specialization

The construction uses [Fewster, *Hadamard states for decomposable
Green-hyperbolic operators*](https://arxiv.org/abs/2503.12537):

- Theorem 3.5(d,e) for Cauchy inverse/response morphisms;
- Lemma 5.14 for wavefront control under regular maps;
- Lemma 5.15(c) for regularity;
- Theorem 5.16 for Hadamard transport.

The repository specializes those statements to the certified rank-40
Hermitian dilation. Positivity is deliberately not imported: its fibre form
has signature \((20,20)\).

## Fail-closed boundary

This closes the global two-point-distribution gate only on the auxiliary
metric dilation. It does not yet provide:

- a two-point distribution on the undoubled raw companion;
- a covariance on the full 54-row graded BV carrier;
- the BRST Ward identity;
- a positive state or physical-cohomology positivity;
- renormalized Lorentzian products or a Lorentzian QME.

The next gate is to determine a valid raw-companion or graded-BV restriction
of the transported covariance and verify BRST compatibility. A projection to
one summand of the off-diagonal Hermitian dilation must not be assumed to
preserve the CCR.
