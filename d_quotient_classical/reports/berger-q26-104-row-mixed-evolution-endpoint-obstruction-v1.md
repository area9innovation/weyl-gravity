# Berger q26: mixed-evolution correction endpoint obstruction

The bounded fully-mixed correction ansatz

\[
A_{\rm ext}=N\otimes A,\qquad
q_{\rm ext}=N\otimes q+(I-N)\otimes s,
\qquad
N=\begin{pmatrix}1&-1\\1&-1\end{pmatrix}
\]

preserves the frozen old-old blocks and makes evolution equivariance linear:

\[
A_0s=sA_{-1}.
\]

It cannot attain the required left-endpoint rank (23) over \(\mathbb Q\).
The exact intertwiner space has dimension (20).  A rank-(11)
intertwiner has a one-dimensional rational invariant kernel.  The source
characteristic polynomial has no rational root except zero, and
\(\ker A_{-1}\) is one-dimensional, so this kernel is forced to be the
unique zero-eigenline.  The frozen old differential kills the same line.
Therefore the off-diagonal contribution on \(\ker s\) vanishes and

\[
\operatorname{rank}q_{\rm ext}=2\operatorname{rank}s=22.
\]

Rank-(12) corrections give total rank (24), while rank at most (10)
cannot exceed (22).  The missing value (23) is therefore an exact
characteristic-zero obstruction, not a failed numerical search.

This closes one structured rational branch only.  General non-cone
104-row completions still require the two-free-differential/rank-stratum
solver that the partial M9c delivery explicitly does not provide.
