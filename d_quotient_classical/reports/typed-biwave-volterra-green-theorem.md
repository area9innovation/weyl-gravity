# Typed Volterra Green theorem for lower-order biwaves

Let (M\simeq\mathbb R\times\Sigma) be globally hyperbolic with compact
Cauchy surface, let (E\to M) be finite rank, and let (P_1,P_2) be
normally hyperbolic second-order operators on (E).  Let (V) be a smooth
differential operator of order at most two which, on every finite slab,
extends boundedly from the first wave-energy graph domain to
(L^1H^{s-1}).  This graph-domain hypothesis matters when (V) contains
second time derivatives.  No stationarity, commutativity, or formal
self-adjointness is assumed.

For

\[
A=P_2P_1+V
\]

introduce the companion

\[
C=\begin{pmatrix}P_1&-I\\V&P_2\end{pmatrix}
=C_0+N,
\quad
C_0=\begin{pmatrix}P_1&0\\V&P_2\end{pmatrix},
\quad
N=\begin{pmatrix}0&-I\\0&0\end{pmatrix}.
\]

For every integer (s), on a finite slab (I), set

\[
X_s=(C^0H^{s+1}\cap C^1H^s)\oplus
    (C^0H^s\cap C^1H^{s-1}),
\qquad
Y_s=L^1H^s\oplus L^1H^{s-1}.
\]

The triangular same-sided Green map is

\[
G_0^\pm=
\begin{pmatrix}
G_1^\pm&0\\
-G_2^\pm V G_1^\pm&G_2^\pm
\end{pmatrix}:Y_s\longrightarrow X_s.
\]

The two resolvents are different typed operators:

\[
R_{\rm sol}^\pm=(I_X+G_0^\pm N)^{-1}:X_s\to X_s,
\qquad
R_{\rm src}^\pm=(I_Y+NG_0^\pm)^{-1}:Y_s\to Y_s.
\]

If (M_{s,I}) is a common finite-slab causal energy-kernel bound, then with
(C_{s,I}=|I|M_{s,I}\lVert N\rVert), ordered-time-simplex integration gives

\[
\lVert(G_0^\pm N)^n\rVert\le {C_{s,I}^n\over n!},
\qquad
\lVert(NG_0^\pm)^n\rVert\le {C_{s,I}^n\over n!}.
\]

Consequently

\[
G_C^\pm=R_{\rm sol}^\pm G_0^\pm
=G_0^\pm R_{\rm src}^\pm
\]

exists, obeys both same-sided inverse identities, and has the declared causal
support.  Nested-slab uniqueness globalizes it.  With
(j(u)=(u,P_1u)), (i(f)=(0,f)), and (p(u,v)=u), the identity
(Cj=iA) gives

\[
G_A^\pm=pG_C^\pm i,
\qquad
AG_A^\pm=G_A^\pm A=I.
\]

For the formal adjoint, factor order reverses:

\[
A^\sharp=P_1^\sharp P_2^\sharp+V^\sharp.
\]

The correctly typed adjoint theorem is therefore

\[
(G_{A,+})^\sharp=G_{A^\sharp,-},
\qquad
(G_{A,-})^\sharp=G_{A^\sharp,+}.
\]

This theorem is conditional on the displayed energy estimates.  It proves
Green hyperbolicity of the lower-order biwave once the exact operator has the
declared form.  It does **not** produce that form, a metric/parent SDR, a
Hadamard state, nonlinear stability, or a quantum theory.  The Berger
retained metric operator is a (P_1=P_2) consumer; the factorized Nariai
metric operator is the (V=0) consumer.
