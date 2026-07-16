# Retained Berger biwave: causal Volterra resolvent

The retained metric operator is exactly

\[
A_{10}=\Box_2^2+V_2,\qquad \operatorname{ord}V_2\le2.
\]

Introduce

\[
\mathcal C_{20}=\begin{pmatrix}\Box_2&-I\\V_2&\Box_2\end{pmatrix}
=\mathcal C_0+N,
\quad
\mathcal C_0=\begin{pmatrix}\Box_2&0\\V_2&\Box_2\end{pmatrix},
\quad
N=\begin{pmatrix}0&-I\\0&0\end{pmatrix}.
\]

The triangular base has the exact same-sided causal inverse

\[
G_{0,\pm}=
\begin{pmatrix}
G_{\Box,\pm}&0\\
-G_{\Box,\pm}V_2G_{\Box,\pm}&G_{\Box,\pm}
\end{pmatrix}.
\]

On a finite causal slab, use the graded energy scale in which the first
component carries one more spatial derivative than the second. Since
\(V_2\) has order at most two and \(N\) has order zero, the wave energy
estimate gives

\[
\|(G_{0,\pm}N)^n\|\le\frac{C_T^n}{n!}.
\]

Therefore the Volterra series converges in every Sobolev energy norm:

\[
G_{20,\pm}
=(I+G_{0,\pm}N)^{-1}G_{0,\pm}
=G_{0,\pm}(I+NG_{0,\pm})^{-1}.
\]

The finite geometric identities give both left and right inverses after
passing to the limit. Every summand is same-sided causal; closedness of the
causal support condition gives the same support for the limit. Finite-slab
solutions glue globally by uniqueness.

The exact graph SDR

\[
i_{\rm sol}(h)=(h,\Box_2h),\qquad i_{\rm src}(f)=(0,f)
\]

then yields

\[
G_{A,\pm}=p_{\rm sol}G_{20,\pm}i_{\rm src},
\qquad
A_{10}G_{A,\pm}=G_{A,\pm}A_{10}=I.
\]

No inverse Laplacian, harmonic projector or mode split occurs. The next task
is now algebraic: combine these metric operators with the certified ghost and
identity factors and the formal-adjoint metric block to obtain the complete
26-row causal BV homotopy.
