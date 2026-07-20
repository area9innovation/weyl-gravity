# Berger retained-26 Cauchy BV carrier obstruction

The normalized retained-26 companion solution map does **not** descend to a
BRST differential on the frozen 104-row stationary Cauchy carrier.

## Complete declared class

The class consists of finite-order support-local degree-\(+1\) PBW
differential operators on the frozen 104 rows satisfying

\[
q_C=\operatorname{ev}_0\,q_{52}^{\rm normalized}\,
       \operatorname{Sol}_{A_{104}}
\]

on every formal Cauchy datum.  Since evaluation at the initial slice is the
identity on those data, this compatibility identity fixes \(q_C\) uniquely.
It therefore closes the search over this declared class at every finite
differential order; it is not merely a bounded ansatz search.

The unique operator is the already serialized canonical graph candidate.
An independent classical consumer reproduces exactly

\[
\#\operatorname{supp}(q_C^2)=157,\qquad
\#\operatorname{supp}([A_{104},q_C])=207.
\]

Both required identities fail.  Adding cyclic-pairing, real-involution or
graded-adjoint requirements cannot repair an already empty class.

## Rigorous enlargement bound

The Berger derivative algebra is noncommutative, so a scalar symbol
substitution is not multiplicative and cannot justify a factorization-rank
claim.  The certificate instead uses its exact three-dimensional adjoint
representation at

\[
\alpha_B=2,\qquad u=1,\qquad v=3.
\]

The represented square has ranks \(13\) in degree \(-1\to+1\) and \(3\) in
degree \(0\to+2\).  If an enlarged degree-\(+1\) differential cancels the old
square through new rows, the old block factors through the new intermediate
degree.  Hence it needs at least five new degree-zero rows and one new
degree-\(+1\) row: at least six rows in total.

This bound is necessary, not sufficient.  No six-row construction or
evolution-compatible extension is claimed.

## Consequence for the Quantum request

The frozen 104-row normalized graph cannot be the requested BRST-compatible
Cauchy/Krein carrier.  The next construction must either change the
normalized companion/\(A_{104}\) data or enlarge the carrier subject to the
certified degreewise lower bound.  This result does not construct a Krein
form, real structure, Hadamard state, positivity, a QME or a quantum theory.

CLOSE-OUT: the exact first obstruction in the complete declared frozen-graph lift class is supplied; alternative companions and larger carriers remain open.
EVIDENCE: d_quotient_classical/certificates/BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1.json
