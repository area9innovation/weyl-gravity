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
classical_import/   schemas, content-addressed snapshots, freeze/import certificates
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
| B | counterterm/anomaly bases and descent database | `FULL_LOCAL_BV_G2_COMPLETE_ON_REGULAR_BACH_LOCUS_ANALYTIC_QME_OPEN`; the ghost-zero and ghost-one quotients both have even/odd dimensions `2/1`; the exact small-algebra calculation eliminates independent pure-Diff and mixed Diff--Weyl classes, ten general nonminimal pairs contract, and exact BV-canonical transport proves gauge-fixed invariance |
| C | local-to-cylinder map and `H3_H4_H5_LEDGER` | `STRUCTURAL_PREFLIGHT_VERIFIED_PROJECTION_BLOCKED`; conformal-flat order counting and even/odd support are exact, but normalized `pi_cl` projection and adjacent H3/H5 bases remain unavailable |
| D | reduced and Euclidean coefficient ledgers | `REPOSITORY_C2_VISIBLE_FULL_BV_LOCAL_COEFFICIENT_MATCHED`; the exact factorwise local calculation gives `(C2,E4,CdualC,BoxR)=(199/30,-87/20,0,0)` with a Ricci-flat `C2` carrier, independent round-`S4` Euler carrier, parity Ward identity, measure, zero-mode, contour and regulator receipts |
| E | Euclidean elliptic or generalized block-Green/Hadamard certificate | `REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED`; the complete `5 -> 10 -> 5` physical symbol sequence, formal adjoint, Diff/Weyl nonminimal doublets and four kinetic blocks replay exactly. The curvature CCR/causal propagator remains certified separately; a global BRST Hadamard state and renormalized Lorentzian products remain open |
| F | one-loop Slavnov breaking and QME status | `OBSTRUCTED_STRICT_FIELD_CONTENT`; the regulated insertion is `(199/30)[omega C2]-(87/20)[omega E4]`, nonzero in the complete gauge-fixed quotient. Standard unitary free matter cannot cancel it. A shifting-scalar Wess--Zumino primitive makes both coordinates exact in the declared AFN0 extended sector, but the compensator cotangent lift and full extended `H04/H14` recomputation remain open |
| G | residual quantum transfer and pairing correction | `FORBIDDEN`; neither AFN0 compensator exactness nor the independent causal carrier restores the full extended BV QME. Transfer reopens only after the cotangent lift, extended quotient, and QME certificate pass |
| N | nonlinear classical transfer prerequisite | `REPAIRED_Q2_Q3_AND_RETAINED_FULL_BV_ELL3_ACCEPTED`; the support-local cyclic repair, typed mixed `q3`, retained contact/exchange replay, and all 26,238 retained BV `ell3` coefficients are independently accepted; this remains classical nonlinear input and does not bypass the local QME gate |

The precursor audits
[`verify_conformal_descent_anomaly.py`](../symbolic/verify_conformal_descent_anomaly.py)
and
[`verify_conformal_coefficient_triangle.py`](../symbolic/verify_conformal_coefficient_triangle.py)
remain exact inputs with their existing fail-closed boundaries.  They do not
constitute a local one-loop determinant, complete `H^{1,4}(s|d)` calculation,
or quantum-master-equation result.

## Bootstrap receipts

- [`classical_import/REPORT.md`](classical_import/REPORT.md) inventories the
  pinned classical handoff, the historical v1 metadata preflight, the active
  executable v2 antifield/Koszul--Tate receiving contract, and the exact
  missing export keeping Gate A closed. The v2 consumer independently replays
  `delta`, `gamma`, and `Q` and dry-runs the filtered-complex adapter before
  any production quotient is authorized.
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
- [`reports/afn0-h04-canonical-quotient.md`](reports/afn0-h04-canonical-quotient.md)
  records the complete covariant ghost-zero AFN0 candidate quotient, the
  exact `Box R` boundary, the nonclosed `R^2` carrier, normalized dual
  witnesses, and the global-topological scope of Euler and Pontryagin.
- [`reports/afn0-cylinder-restriction-preflight.md`](reports/afn0-cylinder-restriction-preflight.md)
  records the exact conformal-flat expansion orders, quadratic `C1` carriers,
  parity support matrix, and the deliberately null normalization/projection
  fields pending the frozen classical handoff.
- [`reports/relative-cohomology-engine.md`](reports/relative-cohomology-engine.md)
  records the exact sparse totalization, anchored top-form projection,
  lower-only class exclusion, quotient proof fields, and the uncomputed
  production-basis boundary.
- [`reports/branch-c-spectral-bootstrap.md`](reports/branch-c-spectral-bootstrap.md)
  records the reduced `E/A/L` character, residues, and determinant boundary.
- [`reports/berger-26-row-green-hadamard-endpoint-contract.md`](reports/berger-26-row-green-hadamard-endpoint-contract.md)
  records the strict retained-endpoint Green/Hadamard import socket and its
  still-missing physical analytic data.
- [`reports/curvature-image-presymplectic-ccr.md`](reports/curvature-image-presymplectic-ccr.md)
  records the `LORENTZIAN-CAUSAL` curvature-presentation presymplectic graded
  CCR algebra and its fail-closed direct-kernel, Hadamard, positivity and QME
  boundaries.
- [`reports/curvature-observable-causal-propagator.md`](reports/curvature-observable-causal-propagator.md)
  records the exact support-local transport
  \(\Delta_C^{\rm obs}=R_C\Delta_\Lambda J_C\), its gauge invariance and
  causal support, while leaving autonomous curvature Green inverses and the
  wavefront/Hadamard stage open.
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
