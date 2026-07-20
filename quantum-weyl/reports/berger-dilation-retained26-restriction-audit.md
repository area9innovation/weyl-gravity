# Berger dilation-to-retained-26 restriction audit

Result: `BERGER_DILATION_TO_RETAINED26_RESTRICTION_AUDIT`

Dependency tag: `LORENTZIAN-CAUSAL`.

## Exact obstruction to the naïve restriction

The transported covariance lives on the rank-40 Hermitian dilation

\[
D=\operatorname{diag}(C,C^\dagger),\qquad
H=\begin{pmatrix}0&I\\I&0\end{pmatrix}.
\]

For either canonical summand inclusion,

\[
i_1u=(u,0),\qquad i_2u=(0,u),
\]

the pulled pairing vanishes:

\[
i_1^\dagger H i_1=i_2^\dagger H i_2=0.
\]

The dilated Green operator is block diagonal, so its scalar causal form is

\[
HE_D=
\begin{pmatrix}
0&E_{C^\dagger}\\
E_C&0
\end{pmatrix}.
\]

Consequently,

\[
i_1^\dagger HE_Di_1=i_2^\dagger HE_Di_2=0.
\]

The retained causal-chain import separately certifies the retained metric
advanced/retarded Green operators. Thus direct projection to either
canonical 20-row summand cannot realize that declared retained causal/CCR
structure: the canonical pullback is identically zero. This is a scoped
obstruction to the canonical summand restriction, not a no-go theorem for
every possible restriction.

## Graph restriction contract

A graph inclusion

\[
i_Ju=(u,Ju)
\]

has pulled pairing

\[
i_J^\dagger H i_J=J+J^\dagger.
\]

It is preserved by the dilated equation precisely when

\[
C^\dagger J=JC.
\]

The graph route therefore requires an explicit support-local regular
intertwiner \(J\), nondegeneracy of \(J+J^\dagger\), and an independent
verification that the pulled covariance has the raw exact CCR and Hadamard
wavefront relation. No such \(J\) is currently supplied.

## Relation to the graded BV complex

The retained complex has twenty metric/metric-antifield companion rows and
six ghost/identity rows. Even a successful graph restriction supplies only
the first twenty. The remaining six rows need a graded covariance compatible
with the retained BRST differential.

The downstream lift is already certified conditionally:

\[
\omega_{54}=\iota_{\rm cl}\,\omega_{26}\,\pi_{\rm cl}.
\]

Therefore the 54-row lift should not be rebuilt. The exact missing object is
\(\omega_{26}\). Two admissible routes remain:

1. supply the graph intertwiner and add the six ghost/identity rows;
2. construct \(\omega_{26}\) directly from the certified retained BV pairing
   and causal homotopy.

## Claim boundary

No retained-26 or 54-row Hadamard covariance, BRST Ward identity, positive
state, physical positivity, Lorentzian time-ordered product or Lorentzian QME
is certified. The rank-40 transported Krein covariance remains valid.
