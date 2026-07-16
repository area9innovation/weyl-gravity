# Quantum Programme for Pure Weyl Gravity

This directory asks whether the certified classical Diff `x` Weyl BV theory
survives renormalization and, only after a restored local quantum master
equation, how its quantum correction transfers to the residual cylinder
complex.

The classical target is

\[
\mathcal H_{\mathrm{cl}}=
\operatorname{Sym}(\mathcal W_+\oplus\mathcal W_-)
\otimes\Lambda^\bullet\mathfrak{so}(4,2)^*,
\]

with two centered degree-four deformation classes
`[W_+^2]` and `[W_-^2]`.  These are vertex/deformation classes, not
one-particle graviton states.

## Order of work

1. Freeze and independently verify a content-addressed classical import.
2. Classify `H^{0,4}(s|d)` counterterm and `H^{1,4}(s|d)` anomaly
   candidates using exact local algebra.
3. Restrict the classified local classes to the cylinder and compute the
   adjacent `H^3 -> H^4 -> H^5` maps.
4. Compute reduced-mode and Euclidean coefficients as separately tagged
   cross-checks.
5. Construct an adequate Euclidean elliptic or Lorentzian causal analytic
   framework and compute the actual one-loop Slavnov breaking.
6. If the local QME is restored, transfer `Q_1` and later corrections through
   the frozen classical contraction.

In parallel, `transfer/` now runs the classical nonlinear prerequisite:
import the full classical BV Taylor tensors and transfer `q_2`, `q_3`, and
higher operations through `pi_cl`, `iota_cl`, and `s_cl`.  This track does
not transfer a quantum correction and does not bypass the `QME_RESTORED`
gate in item 6.

The algebraic classification comes before determinant calculations.  A beta
function or background trace anomaly is not silently identified with a BV
master-equation obstruction.

## Dependency boundaries

Every result uses one or more exact tags:

| Tag | Meaning |
|---|---|
| `LOCAL-ALGEBRAIC` | Local jet, BRST, descent, or cohomology algebra independent of a propagator |
| `EUCLIDEAN-SPECTRAL` | Euclidean elliptic, heat-kernel, or determinant input |
| `REDUCED-MODE` | Certified cylinder mode/character calculation only |
| `LORENTZIAN-CAUSAL` | Full support and causal compatibility have been proved for the claimed object |

`REDUCED-MODE` and `EUCLIDEAN-SPECTRAL` results are never evidence by
themselves for a `LORENTZIAN-CAUSAL` claim.

At bootstrap time there is no certified complete Lorentzian off-shell BV
propagator, BRST-compatible full-metric Hadamard state, renormalized
Lorentzian time-ordered product, causal perturbative AQFT construction, or
Lorentzian QME theorem.

## Layout

```text
classical_import/   schemas, content-addressed snapshots, freeze certificates
local_bv/           fields, jets, differential, invariants, descent, cohomology
counterterms/       ghost-number-zero classes and operator mixing
anomalies/          ghost-number-one, antifield, Diff/Weyl, and parity sectors
cylinder/           background, conformal Killing data, harmonics, projection
spectral/           reduced-mode, Euclidean, and determinant bookkeeping
lorentzian/         filtration, block Green maps, Hadamard, causal products
transfer/           classical nonlinear HPL; Q1/Q2 only after restored QME
certificates/       cross-package machine certificates
reports/            human-readable claim and blocker ledger
schema/             machine-readable result contracts
```

`local_bv/` must not import from `spectral/` or `lorentzian/`.

## Gates

| Gate | Deliverable | Bootstrap status |
|---|---|---|
| A | `CLASSICAL_IMPORT_CERTIFICATE` | `FAIL_CLOSED`; artifact integrity verified, but 15 of 18 export categories remain incomplete or unavailable |
| B | counterterm/anomaly bases and descent database | `IN_PROGRESS`; generated dimension-four catalogues, universal Diff towers, explicit type-D primitives, a complete Lorentzian intrinsic Euler tower, and a mapping-cone engine, but no exhaustive production BRST-cohomology quotient or antifield completion |
| C | local-to-cylinder map and `H3_H4_H5_LEDGER` | `IN_PROGRESS` import/projection infrastructure only |
| D | reduced and Euclidean coefficient ledgers | `IN_PROGRESS` bookkeeping only; no BV coefficient claimed |
| E | Euclidean elliptic or generalized block-Green/Hadamard certificate | `INPUT_CONTRACT_READY`; physical certificate `NOT_COMPUTED` |
| F | one-loop Slavnov breaking and QME status | `WARD_INPUT_CONTRACT_READY`; physical breaking and QME `NOT_COMPUTED` |
| G | residual quantum transfer and pairing correction | `NOT_COMPUTED` |
| N | nonlinear classical transfer prerequisite | `54_ROW_LOCAL_D_AND_UNARY_COMPLETE_Q2_BLOCKED`; the full gauge-fixed unary contraction and support-local helical `D` action pass exact checks on all 54 rows; an aligned pp-wave block has zero mixed transferred `ell2`; the exact Einstein $(--+)$ MHV reference fixture and fail-closed projection contract are ready; the full four-dimensional support-local `q2`, actual Einstein projection, nonaligned/Weyl-square mixing, and complete 54-row arity-two Cartan verdict remain absent |

The precursor audits
[`verify_conformal_descent_anomaly.py`](../symbolic/verify_conformal_descent_anomaly.py)
and
[`verify_conformal_coefficient_triangle.py`](../symbolic/verify_conformal_coefficient_triangle.py)
remain exact inputs with their existing fail-closed boundaries.  They do not
constitute a local one-loop determinant, complete `H^{1,4}(s|d)` calculation,
or quantum-master-equation result.

## Bootstrap receipts

- [`classical_import/REPORT.md`](classical_import/REPORT.md) inventories the
  pinned classical handoff, the executable antifield/Koszul--Tate export
  contract, and the exact missing exports keeping Gate A closed.
- [`reports/branch-a-local-bv-bootstrap.md`](reports/branch-a-local-bv-bootstrap.md)
  records the exact minimal jet/BRST substrate and its uncomputed quotients.
- [`reports/local-curvature-canonicalization.md`](reports/local-curvature-canonicalization.md)
  records the generated quadratic curvature quotient, Bianchi and IBP rails,
  and the remaining local-algebra gates.
- [`reports/local-differential-hodge-canonicalization.md`](reports/local-differential-hodge-canonicalization.md)
  records the generated once-differentiated curvature quotient, commutator
  convention, signature-aware Hodge projectors, and the six-derivative
  mixing boundary.
- [`reports/local-algebra-scaling-foundations.md`](reports/local-algebra-scaling-foundations.md)
  records explicit tensor products, contraction-aware commutators, executable
  detailed schemas, and the complete signed cubic pairing-orbit ledger.
- [`reports/local-six-derivative-curvature-quotient.md`](reports/local-six-derivative-curvature-quotient.md)
  records the cubic Bianchi quotient, second-derivative bridge, mixed
  IBP/commutator quotient, independent FKWC cross-check, and remaining
  four-dimensional specialization boundary.
- [`reports/local-specialization-foundations.md`](reports/local-specialization-foundations.md)
  records exact staged projections and kernels, relation provenance,
  five-index antisymmetrization, tracefree-Weyl reduction, and tensor-level
  epsilon-pair elimination without claiming the four-dimensional quotient.
- [`reports/local-four-dimensional-schouten-quotient.md`](reports/local-four-dimensional-schouten-quotient.md)
  records exhaustive five-index antisymmetrization, the exact `10 -> 8`
  specialization and kernel, and the remaining tracefree-Weyl/BRST boundary.
- [`reports/local-weyl-decomposition-foundations.md`](reports/local-weyl-decomposition-foundations.md)
  records the exact Weyl--Schouten--Cotton convention, derivative-safe
  specialization boundary, differential sign audit, and full-Weyl Hodge
  witnesses required before constructing the strict tracefree-Weyl image.
- [`reports/local-schouten-zero-weyl-image.md`](reports/local-schouten-zero-weyl-image.md)
  records the exact `8 -> 1` Schouten-flat Weyl image, its seven-dimensional
  kernel, the common image of all three order-six sectors, and the boundary
  separating this restriction from the unrestricted Weyl--Cotton jet algebra.
- [`reports/local-dimension-four-candidates.md`](reports/local-dimension-four-candidates.md)
  records the generated three-dimensional quadratic curvature ansatz, its
  two-dimensional Weyl-closed kernel, independent target-native even/odd
  Weyl quotients, and the scoped counterterm/anomaly candidate catalogues.
- [`reports/local-strict-density-descent.md`](reports/local-strict-density-descent.md)
  records the exact horizontal-form algebra, generated four-step universal
  Diff towers, explicit type-D primitives, the Euler variational current,
  exact ordinary-bidegree type-A connecting equations and the independent
  Lorentzian Euler-head reconstruction, together with the still-open quotient
  and antifield boundaries.
- [`reports/relative-cohomology-engine.md`](reports/relative-cohomology-engine.md)
  records the exact sparse totalization, anchored top-form projection,
  lower-only class exclusion, quotient proof fields, and the uncomputed
  production-basis boundary.
- [`reports/branch-c-spectral-bootstrap.md`](reports/branch-c-spectral-bootstrap.md)
  records the reduced `E/A/L` character, residues, and determinant boundary.
- [`reports/berger-26-row-green-hadamard-endpoint-contract.md`](reports/berger-26-row-green-hadamard-endpoint-contract.md)
  records the strict retained-endpoint Green/Hadamard import socket and its
  still-missing physical analytic data.
- [`reports/renormalized-D-ward-insertion-contract.md`](reports/renormalized-D-ward-insertion-contract.md)
  records the sourced/restored Ward-operator lifecycle and the prohibition on
  a Cartan classification before QME restoration.
- [`reports/bootstrap-integration.md`](reports/bootstrap-integration.md)
  records the integrated scoped test run and why the full classical suite was
  not triggered.
- [`reports/nonlinear-homological-transfer-bootstrap.md`](reports/nonlinear-homological-transfer-bootstrap.md)
  records the exact low-arity transfer engine, classical export contract,
  scientific question ledger, and fail-closed input blockers.
- [`reports/ht1-residual-cubic-block.md`](reports/ht1-residual-cubic-block.md)
  records the computed selected residual cubic/Kuranishi bracket and
  separates it from the still-missing support-local BV lift.

The applicable test tiers and escalation rules are in
[`TESTING.md`](TESTING.md).

## Result lifecycle

Machine results conform to [`schema/result.schema.json`](schema/result.schema.json)
and use an explicit lifecycle:

```text
CLASSIFIED
COEFFICIENT_COMPUTED
QME_RESTORED
RESIDUAL_TRANSFERRED
LORENTZIAN_CERTIFIED
```

A result is never promoted merely because a later calculation is expected to
agree with it.  Each promotion requires a new certificate, provenance, and
the appropriate dependency tag.
