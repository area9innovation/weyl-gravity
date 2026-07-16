# Retained Berger biwave: typed causal Volterra resolvents

The retained metric operator has the exact normal form

\[
A_{10}=\Box_2^2+V_2,\qquad \operatorname{ord}V_2\le2.
\]

Its companion is

\[
C=C_0+N,\quad
C_0=\begin{pmatrix}\Box_2&0\\V_2&\Box_2\end{pmatrix},\qquad
N=\begin{pmatrix}0&-I\\0&0\end{pmatrix}.
\]

For every integer \(s\), on each finite causal slab \(I\) use

\[
X_s(I)=
\bigl(C^0(I;H^{s+1})\cap C^1(I;H^s)\bigr)
\oplus
\bigl(C^0(I;H^s)\cap C^1(I;H^{s-1})\bigr),
\]

\[
Y_s(I)=L^1(I;H^s)\oplus L^1(I;H^{s-1}),
\]

where every spatial Sobolev space is on \(S^3\) with values in
\(\mathrm{Sym}^2\).

The triangular Green map \(G_0^\pm:Y_s\to X_s\) is

\[
G_0^\pm=\begin{pmatrix}
G_\Box^\pm&0\\-G_\Box^\pm V_2G_\Box^\pm&G_\Box^\pm
\end{pmatrix}.
\]

The two Neumann series live on different spaces and are recorded separately
for `advanced` and `retarded` evolution. Here advanced support means
\(J^-(\operatorname{supp}f)\), while retarded support means
\(J^+(\operatorname{supp}f)\):

\[
R_{\rm sol}^\pm=(I_{X_s}+G_0^\pm N)^{-1}:X_s\to X_s,
\qquad
R_{\rm src}^\pm=(I_{Y_s}+NG_0^\pm)^{-1}:Y_s\to Y_s.
\]

With \(C_{s,T}<\infty\) determined by the wave-energy constants and the
bounded order-zero map \(N:X_s\to Y_s\), ordered-time-simplex estimates give

\[
\|(G_0^\pm N)^n\|_{X_s\to X_s}\le {C_{s,T}^n\over n!},\qquad
\|(NG_0^\pm)^n\|_{Y_s\to Y_s}\le {C_{s,T}^n\over n!}.
\]

Thus both series converge and the push-through identity is correctly typed:

\[
G_C^\pm=R_{\rm sol}^\pm G_0^\pm
=G_0^\pm R_{\rm src}^\pm:Y_s\to X_s.
\]

The exact factorizations of \(C\) yield both same-sided inverse identities.
Every partial sum is causal; convergence preserves vanishing outside the
closed causal set, and uniqueness glues compatible slab solutions globally.
The graph pullback gives \(G_A^\pm=p_{\rm sol}G_C^\pm i_{\rm src}\).

Finally, relative to the frozen metric-antifield pairing, the correctly typed
adjoint theorem is

\[
(G_{A,\mathrm{advanced}})^\sharp=G_{A^\sharp,\mathrm{retarded}},
\qquad
(G_{A,\mathrm{retarded}})^\sharp=G_{A^\sharp,\mathrm{advanced}}.
\]

This certificate does not replace the right-hand side by \(G_{A,-}\), and it
does not use an inverse Laplacian, inverse curl, harmonic projector or mode
split.
