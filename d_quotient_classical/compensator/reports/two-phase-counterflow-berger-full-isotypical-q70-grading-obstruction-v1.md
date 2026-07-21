# Full-isotypical Berger q70 grading obstruction

## Result

The complete fixed-\((j,m)\) Peter--Weyl carrier is finite:

\[
\mathcal V_{j,m}^{70}
=\mathbb C^{70}\otimes
\operatorname{span}\{Y_{jmk}:k=-j,\ldots,j\},
\qquad
\dim_{\mathbb C}\mathcal V_{j,m}^{70}=70(2j+1).
\]

Every spatial PBW word in the imported 54-row unary preserves the fixed
irreducible \(j\)-space, the time derivative preserves it, and the added
U(1) table is algebraic.  Thus there is no infinite-band obstruction to the
*ungraded* isotypical restriction.  The normalized inclusion sends
\(e_r\otimes e_k\) to \(e_rY_{jmk}\), coefficient extraction gives the
projection, and \(\pi_{jm}\iota_{jm}=1\).

The requested graded BV block nevertheless cannot be built from the pinned
70-row parent.  The two direct-sum tables use opposite chain orientations.

## Exact grading audit

The complete 54-row certificate declares compact degrees

\[
(-1)^5,\quad 0^{22},\quad 1^{22},\quad 2^5.
\]

All 309 nonzero operator blocks obey

\[
\deg(\text{row})-\deg(\text{column})=+1.
\]

For the diagonal-U(1) changed basis

```text
chi, c_U1, A_star, B, c_U1_star, H, bar_c, b, b_star, bar_c_star
```

the original-row ghost ledger fixes compact degree to minus ghost number.
Every one of the five serialized multiplet arrows, or eight arrows after the
four-vector multiplicity is expanded, instead has degree shift \(-1\):

```text
chi       -> c_U1
A_star    -> B                 (four components)
c_U1_star -> H
bar_c     -> b
b_star    -> bar_c_star
```

Consequently

\[
q_{70}^{\rm serialized}=q_{54}\oplus q_{U(1)}^{\rm serialized}
\]

has the exact shift histogram

\[
\{+1:309,\ -1:8\}.
\]

It is nilpotent as an ungraded or \(\mathbb Z/2\)-odd matrix, but it is not a
homogeneous differential on the declared \(\mathbb Z\)-graded BV complex.
Nilpotency alone therefore does not define the requested degreewise
cohomology quotient.

## Convention-derived repair

The unique table-orientation repair is

\[
q_{U(1)}^{\rm repaired}
=(q_{U(1)}^{\rm serialized})^T,
\qquad
S_{U(1)}^{\rm repaired}
=(S_{U(1)}^{\rm serialized})^T.
\]

It sends every expanded arrow to degree \(+1\) and preserves exactly

\[
(q_{U(1)}^{\rm repaired})^2=0,
\qquad
q_{U(1)}^{\rm repaired}S_{U(1)}^{\rm repaired}
+S_{U(1)}^{\rm repaired}q_{U(1)}^{\rm repaired}=1_{16}.
\]

An independent reconstruction also produces a nondegenerate canonical odd
pairing for which the repaired table is cyclic.  The parent prose currently
lists `bar_c-b_star, b-bar_c_star`; the declared row names require the
canonical dual pairs `bar_c-bar_c_star, b-b_star`.  An explicit repaired
16-row pairing must therefore be emitted with the replacement parent.

The repair is **not** applied silently here.  Reissuing the parent must update
its exact action/chain convention, 70-row direct sum, cyclic pairing, causal
homotopy statement, receiver hashes and independent consumer.

## Weight closure and exceptional labels

For every \(j>0\), the \(e_1/e_2\) ladder graph on
\(k=-j,\ldots,j\) is connected.  Every nonempty proper weight truncation has
a nonzero boundary coupling.  In particular, for integer \(j>0\), the
right-neutral weight \(k=0\) couples to \(k=\pm1\); it is not a standalone
subcomplex.  Later exceptional analysis must be performed inside the full
integer-\(j\) isotypical block.  Only \(j=0\) is a separate one-weight block.

## Independent rail

The independent verifier does not import the producer.  It reconstructs:

- the q54 degree shifts directly from all 309 serialized blocks;
- the U(1) ghost/compact degrees and all eight expanded arrows;
- the transpose contraction and its canonical cyclic pairing;
- connected weight graphs through `two_j=6` and every proper truncation
  mutation in those blocks;
- the exact `two_j=1` Wigner realization, where the 108-row q54 matrix has
  594 nonzero polynomial entries, squares to zero, and satisfies the
  cross-\(m\) cyclic identity
  \(q(-z)^T\Omega_{m,-m}+\Omega_{m,-m}q(z)=0\).

The round mutation removes the earlier Hodge mixing but cannot change the
degree orientation.  Omitting a row fails the imported `54+16=70` inventory.

## Claim boundary

This is an exact `LOCAL-ALGEBRAIC`/`REDUCED-MODE` obstruction to the imported
graded q70 direct-sum interface.  It does not revoke the separate 54-row
causal theorem or the algebraic contractibility of the U(1) table.  It does
not compute physical cohomology, pairing inertia, characteristics, stability,
Hadamard data, observers, nonlinear brackets, anomalies, a QME, particles or
unitarity.

CLOSE-OUT: DONE — the complete stop condition is met

EVIDENCE: `TWO_PHASE_COUNTERFLOW_BERGER_FULL_ISOTYPICAL_Q70_GRADING_OBSTRUCTION_V1.json`, its payload, strict schemas, producer, independent verifier, scoped tests, receipt, and fail-closed atlas fragment.
