# Berger vector Hodge split: exact two-way mixing obstruction

## Result

The longitudinal and coexact one-form sectors are not separate subcomplexes of
the selected gauge-fixed Berger Diff endpoint.  The anisotropic endpoint mixes
them in both directions.  Therefore the requested vector/tensor physical
quotient cannot be formed using a round-style scalar/vector Hodge split.

The minimal admissible replacement is a complete fixed-(j)
(SU(2)_L\times U(1)_R) isotypical block containing the longitudinal and
coexact one-forms together with every scalar, vector and tensor row reached by
(q_{70}).

## Exact adjoint argument

Let

\[
 A_2=[e_0^2]\,q_{54}[\bar c^*_{\rm diff},c_{\rm spatial}]
\]

be the coefficient of the second time derivative in the spatial Diff ghost
endpoint.  Direct PBW reduction gives 18 terms and verifies

\[
 A_2^\dagger=A_2
\]

under the invariant-frame convention (e_a^\dagger=-e_a).  For the
orthogonal Berger Hodge splitting

\[
 \Omega^1=\operatorname{im}d_0\oplus\ker d_0^\dagger,
 \qquad P_{\rm ex}+P_{\rm co}=1,
\]

the preceding scalar certificate proves

\[
 P_{\rm co}A_2P_{\rm ex}\ne0
\]

on every exact scalar-derived mode with right weight (k\ne0).  Formal
self-adjointness then gives

\[
 (P_{\rm co}A_2P_{\rm ex})^\dagger
 =P_{\rm ex}A_2P_{\rm co}\ne0.
\]

Thus omitting coexact modes from the scalar-derived carrier and omitting
longitudinal modes from the vector carrier both violate closure.

## Independent finite Wigner replay

For each exact finite Wigner block, the projectors are constructed without a
chosen eigenbasis:

\[
 P_{\rm ex}=d_0(d_0^\dagger d_0)^{-1}d_0^\dagger,
 \qquad P_{\rm co}=1-P_{\rm ex}.
\]

Exact replay for (2j=1,\ldots,6) gives the same rank in both cross blocks:

\[
 \operatorname{rank}(P_{\rm co}A_2P_{\rm ex})
 =\operatorname{rank}(P_{\rm ex}A_2P_{\rm co})
 =\begin{cases}
 2j+1,&2j\text{ odd},\\
 2j,&2j\text{ even}.
 \end{cases}
\]

The integer-(j) rank loss is precisely the right-neutral (k=0) direction;
it remains exceptional and does not supply a complete closed block.  A
method-distinct verifier extends the exact replay through (2j=8).

As a negative control, simultaneously replacing the geometry and endpoint by
the round values (c=u=v=1) makes both cross blocks vanish in every audited
fixture.  Merely relabelling the nonround geometry as round is not allowed.

## Fail-closed consequence

The first vector closure gate fails before the symmetric-tensor stage.  Hence
the complete vector/tensor cohomology quotient, descended pairing,
characteristic/Jordan data, gradient matrix and causal cones are
`NOT_DEFINED_BEFORE_FULL_ISOTYPICAL_ENLARGEMENT`.  The exceptional/global
successor is not activated by this result.

The full support-local, cyclic and causal 70-row parent is unchanged.  This is
exact `LOCAL-ALGEBRAIC`/`REDUCED-MODE` evidence about a proposed restriction;
it does not establish a defect of (q_{70}), a symmetric-tensor theorem, an
instability, or an observer, Hadamard, QME, particle, positivity or unitarity
claim.

CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: TWO_PHASE_COUNTERFLOW_BERGER_VECTOR_HODGE_SPLIT_OBSTRUCTION_V1_TIER_RECEIPT
