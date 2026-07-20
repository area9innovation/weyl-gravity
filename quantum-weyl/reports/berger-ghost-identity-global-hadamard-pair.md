# Berger ghost/identity global Hadamard pair

Result: `BERGER_GHOST_IDENTITY_GLOBAL_HADAMARD_PAIR`

Dependency tag: `LORENTZIAN-CAUSAL`.

The certified ghost endpoint is

\[
P_g=P_{g,2}P_{g,1},
\]

where both factors are rank-three normally hyperbolic operators. The identity
endpoint is the formal adjoint \(P_g^\dagger\). Introduce the rank-six graph
companion

\[
C_g=
\begin{pmatrix}
P_{g,1}&-I_3\\
0&P_{g,2}
\end{pmatrix}
\]

and the rank-twelve dilation

\[
D_{gi}=\operatorname{diag}(C_g,C_g^\dagger),\qquad
H_6=
\begin{pmatrix}
0&I_6\\
I_6&0
\end{pmatrix}.
\]

Its principal symbol is \(qI_{12}\), \(H_6\) is nondegenerate with signature
\((6,6)\), and \(D_{gi}\) is formally \(H_6\)-self-adjoint. The same global
Feynman/Hadamard theorem already certified for the metric dilation therefore
applies. Transpose symmetrization and the frozen project sign convention give
an exact-CCR global Hadamard Krein covariance on the dilation.

The endpoint pullback must use different source inclusions on the two
companion blocks:

\[
K_{gi}=\operatorname{diag}(i_{\rm src},p_{\rm sol}^\dagger).
\]

It gives

\[
W_{gi}=K_{gi}^\dagger W_{D_{gi}}K_{gi},
\qquad
K_{gi}^\dagger H_6E_{D_{gi}}K_{gi}
=
\begin{pmatrix}
0&E_g^\dagger\\
E_g&0
\end{pmatrix}.
\]

Thus the three ghost and three identity endpoint rows now have a global
Hadamard pair with exact graded CCR.

This result is not yet the retained 26-row BRST covariance. The certified
20-row metric/formal-adjoint kernel and this six-row pair must be assembled,
their exact \(q_{26}\) Ward defect computed, and any smooth defect completed
before a 26-to-54 lift is permitted. No positivity statement is attached to
the ghost/identity pair.
