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

The multiplicity preflight now derives the standard bundle ranks
`(5,1,5,3)` and their signed effective rank six. The imported covariant BV
dictionary decomposes as `10=5+4+1` for the metric and `4=3+1` for the
diffeomorphism ghost. Together with the Weyl ghost, the scalar ghost input
has rank two whereas the standard scalar ghost factor has rank one. Thus the
unknown multiplicity content is no longer an unspecified counting problem:
it is exactly a rank-one scalar cancellation plus the analytic
row/operator/Berezinian map proving that cancellation.

This proves a useful conditional theorem: if a repository regulator, measure,
and regulated Slavnov functional match those two standard nontrivial
coordinates, and no compensating Wess--Zumino field is added, the strict
fixed-field-content QME is obstructed at one loop. The condition is not yet
established, so the theorem is deliberately inactive.

## Exact remaining gap

No further local tensor-graph expansion is needed for this decision. The
remaining inputs are analytic:

- a repository Euclidean elliptic complex with a gauge-fixed Lagrangian
  integration slice and action normalization;
- a full-BV multiplicity ledger resolving the rank-two longitudinal
  Diff/Weyl scalar ghost sector to the rank-one standard scalar factor and
  proving all nonminimal Berezinian cancellations;
- the full repository BV-row/operator match and the auxiliary normalization,
  contour, and finite phase;
- zero-mode, contour, and determinant-measure policies;
- the regulated BV Slavnov action with Wess--Zumino consistency proof.

The preflight does not call the standard heat-kernel vector a repository BV
coefficient, does not activate the conditional obstruction, and makes no QME,
Cartan, residual-transfer, or Lorentzian claim.

The accepted handoff schema
`quantum-weyl-regulated-slavnov-breaking-export-v1` is executable. It requires
content-addressed complex, multiplicity, auxiliary/fourth-order, zero-mode,
measure/contour, Wess--Zumino, and parity proofs, with every analytic role
explicitly marked `VERIFIED` and the classical commit equal to the frozen G2
snapshot. The null commit is accepted only by the synthetic fixture path.
On the physical path each JSON proof must also carry the role-specific
`result_id` required by the receiver; an unrelated hashed artifact cannot be
reused as an ellipticity, multiplicity, auxiliary, zero-mode, measure,
Wess--Zumino, parity, QME-disposition, or counterterm proof.
The multiplicity artifact is additionally validated against its strict
schema, must share the frozen classical commit and analytic route, must use
unique integration-row and factor IDs, and must content-address every nested
proof.
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
