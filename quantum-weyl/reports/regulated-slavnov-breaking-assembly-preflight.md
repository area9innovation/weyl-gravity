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
vector therefore has partial quotient coordinates

\[
\left({199\over30},-{87\over20},p_{\rm odd}\right),
\]

where `p_odd` remains `NOT_COMPUTED`, not silently zero. Both known even
coordinates evaluate nontrivially under the transported complete quotient
duals.

This proves a useful conditional theorem: if a repository regulator, measure,
and regulated Slavnov functional match those two standard nontrivial
coordinates, and no compensating Wess--Zumino field is added, the strict
fixed-field-content QME is obstructed at one loop. The condition is not yet
established, so the theorem is deliberately inactive.

## Exact remaining gap

No further local tensor-graph expansion is needed for this decision. The
remaining inputs are analytic:

- a repository Euclidean elliptic complex with exact multiplicities and
  action normalization;
- the auxiliary/fourth-order measure Jacobian;
- zero-mode, contour, and determinant-measure policies;
- the regulated BV Slavnov action with Wess--Zumino consistency proof;
- a parity-odd coefficient or a verified regulator Ward identity.

The preflight does not call the standard heat-kernel vector a repository BV
coefficient, does not activate the conditional obstruction, and makes no QME,
Cartan, residual-transfer, or Lorentzian claim.

The accepted handoff schema
`quantum-weyl-regulated-slavnov-breaking-export-v1` is executable. It requires
content-addressed complex, multiplicity, auxiliary/fourth-order, zero-mode,
measure/contour, Wess--Zumino, and parity proofs. Exact receiver fixtures
verify both lifecycle branches: a nonzero quotient vector is classified as an
obstruction for strict field content, while a purely exact `omega BoxR`
breaking is classified as restorable by its local counterterm.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m anomalies.regulated_slavnov_breaking_preflight --check
PYTHONPATH=quantum-weyl python3 -m anomalies.verify_regulated_slavnov_breaking_preflight
PYTHONPATH=quantum-weyl python3 -m unittest anomalies.tests.test_regulated_slavnov_breaking_preflight
```
