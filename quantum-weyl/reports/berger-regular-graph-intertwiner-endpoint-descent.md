# Berger regular graph obstruction and endpoint descent

Result:
`BERGER_REGULAR_GRAPH_INTERTWINER_OBSTRUCTION_AND_ENDPOINT_DESCENT`

Dependency tag: `LORENTZIAN-CAUSAL`.

## Complete regular graph class

The companion solution space uses the certified anisotropic Sobolev scale

\[
X_s=H^{s+1}(\operatorname{Sym}^2)\oplus
H^s(\operatorname{Sym}^2).
\]

A support-local differential map \(J:X_s\to X_s\), bounded for every \(s\),
has block orders

```text
J11 <= 0,   J12 = 0,
J21 <= 1,   J22 <= 0.
```

The upper-right block vanishes because a differential operator cannot map
\(H^s\) continuously into \(H^{s+1}\). A pseudodifferential operator of order
\(-1\) could do so, but it is not support-local and is outside this ticket.

Write \(L(\xi)=\sigma_1(J_{21})(\xi)\). At differential order three, the
intertwiner equation

\[
C^\dagger J=JC
\]

gives

\[
\sigma_2(V_2)(\xi)^\dagger L(\xi)=0.
\]

The exact lower-by-two certificate proves that \(\sigma_2(V_2)\) has generic
rank ten. Hence it is invertible on a nonempty open conic set, so the
polynomial symbol \(L\) vanishes identically.

At order two the same equation gives

\[
\sigma_2(V_2)^\dagger J_{21}=0,\qquad
\sigma_2(V_2)^\dagger J_{22}=0,\qquad
J_{22}\sigma_2(V_2)=0.
\]

These are pointwise principal-symbol statements, so smooth coefficient
dependence in \(J\) does not evade them. Thus \(J_{21}=J_{22}=0\). The
remaining lower-left block equation is then

\[
-J_{11}=0.
\]

Therefore \(J=0\): no nonzero, and hence no nondegenerate, graph restriction
exists in the complete smooth support-local differential class bounded on
the certified graph spaces.

## Correct direct endpoint descent

The graph SDR already provides

\[
C\,i_{\rm sol}=i_{\rm src}A,\qquad
i_{\rm src}=(0,I)^T,\qquad p_{\rm sol}=(I,0).
\]

After formal adjunction, the source inclusion for the \(A^\dagger\) endpoint
is \(p_{\rm sol}^\dagger=(I,0)^T\), not a second copy of \(i_{\rm src}\).
Define

\[
K_{\rm src}=\operatorname{diag}
(i_{\rm src},p_{\rm sol}^\dagger).
\]

Then the endpoint kernel is

\[
W_{A\oplus A^\dagger}
=K_{\rm src}^\dagger W_D K_{\rm src}.
\]

The exact causal block is

\[
K_{\rm src}^\dagger H E_D K_{\rm src}
=
\begin{pmatrix}
0&(p_{\rm sol}E_Ci_{\rm src})^\dagger\\
p_{\rm sol}E_Ci_{\rm src}&0
\end{pmatrix}.
\]

Thus the metric cross block is precisely the certified endpoint
Pauli--Jordan operator. The same source map acts on the covariance and causal
kernel, so the exact CCR descends. The maps are order-zero bundle maps and
the finite graph wavefront theorem applies, so the Hadamard wavefront
inclusion is preserved.

## Remaining gate

This supplies the twenty metric and metric-adjoint endpoint rows as an
analytic Hadamard/CCR kernel. It is not yet a graded retained-26 covariance.
The missing objects are:

1. a global exact Hadamard pair for the three ghost and three identity rows;
2. a smooth completion making the full kernel compatible with \(q_{26}\);
3. an independent verification of the BRST Ward identity.

Only after those pass may the already-certified conditional 26-to-54 lift be
applied. Positivity, particles, interacting products and a Lorentzian QME
remain separate.
