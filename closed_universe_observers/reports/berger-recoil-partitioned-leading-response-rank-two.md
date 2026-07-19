# Berger partition-refined leading response rank two

Status: `FINITE_DETECTOR_SELECTED_LEADING_RESPONSE_RANK_TWO_CERTIFIED_ON_MASS_DOMAIN`.

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The whole-support switch hull used by the first finite preparation enclosure
contains zero.  Consequently every old finite Cauchy-coordinate rectangle
contained zero, even though the underlying operator-defined preparation need
not vanish.  The refined evaluator partitions each exact positive emitter
switch into rational cells, accumulates interval switch moments, and only then
applies the massive sine/cosine matrices.  Kernel and source remainders are
propagated cellwise.

For both detector-selected preparations, the `two_j=0`, `k=0` advanced Cauchy
covector now has a coordinate rectangle excluding zero uniformly on

\[
m_0^2,m_1^2\in[1,2].
\]

The machine-readable certificate supplies strict rational coefficient-block
lower bounds.  The physical spatial pairing multiplies each by the exact
positive Peter--Weyl weight
`(two_j+1)/Vol_Berger=1/(16*pi^2*c)` at `two_j=0`, so

\[
E_a=\langle p_a,A_a p_a\rangle+\langle q_a,L_aq_a\rangle
\geq \lVert p_a\rVert^2+m_{a,\min}^2\lVert q_a\rVert^2>0.
\]

Green adjunction identifies the detector-selected diagonal response with this
positive energy.  Since `h1` is later than D0, `M_01=0`, and for nonzero
couplings the leading matrix is

\[
M=\begin{pmatrix}g_0E_0&0\\M_{10}&g_1E_1\end{pmatrix},
\qquad \det M=g_0g_1E_0E_1\neq0.
\]

Thus the selected leading response has rank two uniformly on the declared
validation mass domain.  The two-cell mutation proves that this conclusion is
not inherited from merely choosing two probes: its lower bounds are both
zero.

The interval `[1,2]` is a validation parameter family, not a declaration of
the physical emitter masses.  Arbitrary positive masses, the numerical
infinite-harmonic reconstruction, feedback recoil, four absolute-`g^3`
intervals, tangent-cone survival, fixed-background `K_Berger` descent, Bridge
3 and quantum promotion remain open.

Evidence: `BERGER_RECOIL_PARTITIONED_LEADING_RESPONSE_RANK_TWO.json`.
