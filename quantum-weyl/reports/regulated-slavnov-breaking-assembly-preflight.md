# Regulated Slavnov-breaking assembly preflight

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The local algebraic part of the one-loop breaking problem is now finished on
the regular Bach locus. The complete minimal, nonminimal, and canonically
gauge-fixed quotient has basis

```text
ANOM_OMEGA_C2
ANOM_OMEGA_E4
ANOM_OMEGA_C_DUAL_C
```

with even/odd dimensions `2/1`. Pure Diff, independent mixed Diff--Weyl,
positive-antifield, and nonminimal additions contribute no further class.
`ANOM_OMEGA_BOX_R` is removed by the stored primitive
`-(1/12) R^2` modulo its horizontal current.

## Exact assembly

The preflight constructs the exact `3 x 4` relative-cohomology reduction
matrix. It is the identity on the three nontrivial representatives and kills
only `ANOM_OMEGA_BOX_R`.

The independently reconstructed standard conformal-spin-two background
vector therefore has quotient coordinates

\[
\left({199\over30},-{87\over20},0\right).
\]

The odd zero is derived for the declared standard parity-even determinant
regulator: its real tensor-Laplacian factors contain no orientation tensor,
Hodge star, or chiral projector, and the exact Ward equation is `2 p=0`.
This is not yet a statement about the unmatched repository regulator. Both
even coordinates evaluate nontrivially under the transported complete
quotient duals.

The standard physical TT factor pair has also been matched exactly through
an auxiliary Schur complement. With (A=\Delta_2^\perp(2)), the block
quadratic form on `(h_TT,f_TT)` has determinant
`det(-I_f) det[A(A+2)]`, reproducing
`Delta_2_perp(2) Delta_2_perp(4)`. The algebraic auxiliary determinant has no
background-dependent logarithmic coefficient under a normalized
translation-invariant measure. Repository row identification, normalization,
contour, and finite phase remain open.

The historical multiplicity preflight derives the standard bundle ranks
`(5,1,5,3)` and their signed effective rank six. The imported covariant BV
dictionary decomposes as `10=5+4+1` for the metric and `4=3+1` for the
diffeomorphism ghost. Together with the Weyl ghost, the scalar ghost input
has rank two whereas the standard scalar ghost factor has rank one. That gap
is now closed: the exact coupled Diff--Weyl FP matrix reduces to the single
`Delta_0(-4)` factor, the York/Hodge measure cancels the unwanted scalar
Jacobian, and every nonminimal quartet has unit superdeterminant. The round-S4
priming dimensions `(0,5,0,10)` and all local determinant exponents are now
bound. The physical normalized TT dictionary passes its semantic receiver with
`H_TT=(1/2) Delta_2_perp(2) Delta_2_perp(4)`, and the composed physical
full-BV multiplicity ledger independently passes exact row, factor, rank,
exponent, zero-mode, and nested-proof replay.

On round `S4` this physical ledger computes

\[
a={87\over20},\qquad [E_4]=-{87\over20}.
\]

It does not compute `c`: the background is conformally flat, so `C2=0` and
the `C2` coefficient is invisible. The standard value `199/30` remains an
independent Euclidean cross-check, not a promoted repository coefficient.
The analytic producer and frozen local-BV commits are distinct, but the new
physical compatibility bridge replays the producer Git tree and proves that
both sides use the byte-identical classical export with all five canonical
hashes equal.

This proves a useful conditional theorem: if a repository regulator, measure,
and regulated Slavnov functional match those two standard nontrivial
coordinates, and no compensating Wess--Zumino field is added, the strict
fixed-field-content QME is obstructed at one loop. The condition is not yet
established, so the theorem is deliberately inactive.

## Exact remaining gap

No further local tensor-graph or multiplicity expansion is needed for this
decision. The remaining inputs are analytic:

- a non-conformally-flat or Ricci-flat physical full-BV operator/measure
  carrier on which the `C2` coefficient is visible;
- a complete Euclidean elliptic-complex receipt with action normalization and
  an explicit `FOURTH_ORDER_METRIC` or `SECOND_ORDER_AUXILIARY` formulation;
- content-addressed regulator, zero-mode, determinant-measure, and any
  formulation-specific contour/global-phase policies;
- the regulated BV antibracket/Slavnov insertion with Wess--Zumino consistency,
  repository parity disposition, and cohomology coordinates.

The last item is essential. Matching the determinant factors and recovering
the familiar heat-kernel coefficients does not by itself compute the BV
master-equation breaking.

The preflight promotes only the physical round-S4 Euler coefficient. It does
not call the complete standard heat-kernel vector a repository BV anomaly
vector, does not activate the conditional obstruction, and makes no QME,
Cartan, residual-transfer, or Lorentzian claim.

The accepted handoff schema
`quantum-weyl-regulated-slavnov-breaking-export-v2` is executable. Version 1
remains a historical contract; version 2 adds the outputs required to decide
the actual insertion rather than only its quotient coordinates. It requires
content-addressed complex, multiplicity, auxiliary/fourth-order, zero-mode,
measure/contour, Wess--Zumino, and parity proofs, with every analytic role
explicitly marked `VERIFIED` and the classical commit equal to the frozen G2
snapshot. The null commit is accepted only by the synthetic fixture path.
The analytic operator snapshot may be newer than the frozen local-BV
cohomology snapshot. Identical commits need no bridge; distinct commits must
carry a content-addressed
`REPOSITORY_CLASSICAL_SNAPSHOT_COMPATIBILITY` proof showing that the imported
field/differential/pairing data used by the quotient have not drifted. Thus a
new TT producer commit is not rejected merely for being newer, but neither is
commit compatibility assumed.
That bridge is now replayed semantically: all five frozen generator, atom,
differential, dependency, and scope hashes must agree, and its nested
role-specific import/export proofs must verify by content hash. A JSON object
carrying only the expected `result_id` is rejected before analytic row
validation begins.
The receiver now distinguishes formulations. A `FOURTH_ORDER_METRIC` export
must mark the auxiliary-equivalence role `NOT_APPLICABLE` with a null artifact;
a `SECOND_ORDER_AUXILIARY` export must supply and verify it. This prevents an
auxiliary-only proof gate from being imposed on a genuine fourth-order route.
On the physical path each JSON proof must also carry the role-specific
`result_id` required by the receiver; an unrelated hashed artifact cannot be
reused as an ellipticity, multiplicity, auxiliary, zero-mode, measure,
Wess--Zumino, parity, QME-disposition, or counterterm proof.
The multiplicity artifact is additionally validated against its strict
schema, must share the frozen classical commit and analytic route, must use
unique integration-row and factor IDs, and must content-address every nested
proof. Complete row and factor coverage, the exact standard target ranks and
signs, and the rank-two-to-rank-one scalar ghost map are checked semantically;
status strings alone cannot satisfy the receiver.
The insertion decomposition must now include the regulated Slavnov action,
an explicit total-derivative row (including a certified zero), gauge-parameter
dependence, regularization dependence, and the complete antifield completion.
Every corresponding proof, together with the Wess--Zumino, parity,
counterterm, and QME-disposition proofs, binds the analytic commit, route,
ordered coefficient basis, and exact coefficient hash. Stale or swapped proof
objects are rejected even when their role-specific `result_id` is correct.
The complete role-to-`result_id` map is emitted as
`accepted_proof_result_ids` in the assembly certificate.
Exact receiver fixtures
verify both lifecycle branches: a nonzero quotient vector is classified as an
obstruction for strict field content, while a purely exact `omega BoxR`
breaking is classified as restorable by its local counterterm.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m anomalies.regulated_slavnov_breaking_preflight --check
PYTHONPATH=quantum-weyl python3 -m anomalies.verify_regulated_slavnov_breaking_preflight
PYTHONPATH=quantum-weyl python3 -m unittest anomalies.tests.test_regulated_slavnov_breaking_preflight
```
