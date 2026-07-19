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

The Euclidean coefficient rail additionally fixes the nonzero-momentum
flat-TT logarithmic one-loop form-factor coefficient `-199/60`. Its spectral
covariantization is universal through curvature order two, while its cubic
completion, the independent nonlocal `R2` form factor, additive finite `C2`
constant and absolute dressed `R(g_hat)^2` normalization remain open. The raw
local `BoxR` coefficient and its exact one-loop strict-metric conversion to
the repository `BoxR=0` scheme are certified separately. At
bootstrap time there is no certified complete Lorentzian off-shell BV
propagator, BRST-compatible full-metric Hadamard state, renormalized
Lorentzian time-ordered product, causal perturbative AQFT construction, or
Lorentzian QME theorem. On the narrower free reduced vacuum-cylinder E/A/L
carrier, however, the same-background normalized modes, causal Green operator
and pairing now certify a compatible complex structure and microlocal
Hadamard two-point distribution. E is positive and A/L have negative Krein
sign; this is not a full-BV state or positive graviton Hilbert space.

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
| D | reduced and Euclidean coefficient ledgers | `REPOSITORY_C2_VISIBLE_FULL_BV_LOCAL_COEFFICIENT_MATCHED`; the exact factorwise local calculation gives `(C2,E4,CdualC,BoxR)=(199/30,-87/20,0,0)`. Separately, the published raw zeta/proper-time `BoxR` coefficient `(7/2)log(3/2)-159/80` is imported and independently replayed, and the exact strict-metric `R2` counterterm `(7/24)log(3/2)-53/320` converts it to the repository `BoxR=0` convention. This is a one-loop local scheme conversion, not the nonlocal `R2` form factor or an absolute dressed normalization |
| E | Euclidean elliptic or generalized block-Green/Hadamard certificate | `REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX_CERTIFIED`; the complete `5 -> 10 -> 5` physical symbol sequence, formal adjoint, Diff/Weyl nonminimal doublets and four kinetic blocks replay exactly. Separately, reduced vacuum-cylinder Bridge 4 is certified on the E/A/L Krein carrier; a global full-BV BRST Hadamard state and renormalized Lorentzian products remain open |
| F | one-loop Slavnov breaking and QME status | `STRICT_OBSTRUCTED; TAU_ADIC_EXTENDED_ONE_LOOP_LOCAL_EUCLIDEAN_QME_RESTORED`; the regulated insertion is `(199/30)[omega C2]-(87/20)[omega E4]`, nonzero in the complete strict gauge-fixed quotient. Standard unitary free matter cannot cancel it. In the formal tau-adic compensator extension the exact cotangent lift contracts the Weyl quartet, the extended quotient has `dim H04=(3 even,1 odd)` and `H14=0`, and the coefficient-bearing Wess--Zumino counterterm restores the local Euclidean QME at one loop. This is neither an all-loop nor Lorentzian theorem |
| G | residual quantum transfer and pairing correction | `FORBIDDEN`; the frozen strict residual contraction does not include the compensator. One conditional anomaly-induced Euclidean `Gamma1` representative and the relative strict-metric raw-to-`BoxR=0` scheme conversion are exact. The FV decomposition proves that a separately specifiable nonlocal `R2` form factor is not an independent datum in this scope, the zero-derivative algebraic `C3` basis is complete with one even and one odd direction, and the parity-even third-curvature manifest has five carrier-labelled functions: scalar-flat transversality enhances `I29` from source-generic `C3` to effective `S3`, giving 11 raw effective channels, and the four-dimensional symmetric relation leaves 10. The five universal CPT alpha kernels are exact on a rank-one scalar fixture. Direct minimal-CPT substitution for the generic Diff–Weyl ghost is architecture-obstructed, but the operator is exactly reduced to an Endo base plus `W=-2 Ric`. Its n=3 generic nonexceptional-momentum triangle is an exact eight-sector Feynman-simplex/Wick kernel, and its 11 raw carrier orientations are projected exactly to the ten-dimensional scalar-flat quotient. Ten numerators contain an exact `Delta` factor; after cancellation every raw row except `I10` vanishes on all open simplex edges, while the `I28` relation is pointwise. All ten pole-three rows have exact relative-IBP primitives. The exact `S3`-covariant scalar-triangle system reduces their derivative masters to `J` and two bubble-log ratios, while the only nonzero corner of each canonical primitive has equal angular weights and integrates rationally. The pole-four `I29` row is also reduced by a full exact 55-row relative-IBP identity to the same master basis, with rational corner flux and exact symmetric-point regression. Thus all eleven generic ghost `n=3` functions are complete. At `x1=x2=x3=1` all eleven coordinates are integrated exactly as rational combinations of `4 Cl2(pi/3)/sqrt(3)`. The curved n=1/n=2 nonminimal architecture is reduced exactly to five minimal vector/scalar resolvent carriers. The pure-vector physical sum is now evaluated as `6 Gamma1 S1 - 2 Gamma3 S3 - 2 Gamma14 S14` and projected to the scalar-flat quotient. The three longitudinal `D_W=delta W d` towers are resummed exactly into `S_L=I+K`. The order-`-2` correction is in `S_3`, so the canonical `det_3(I+K)` tail exists. The exact residues are `Wres(K)=(4 pi)^-2 integral(R^2+4 Ric^2)/9`, `Wres(K^2)=(4 pi)^-2 integral(R^2+2 Ric^2)/27`, and `Wres(log S_L)=(4 pi)^-2 integral(5 R^2+22 Ric^2)/54`. The finite regulated `R(K)` and `R(K^2)` rows, reference-specific scale conversion, possible local zeta multiplicative term, and generic physical fourth-order Hessian remain absent. The five complete repository form-factor functions and coefficients, parity-odd derivative manifest, absolute dressed `R(g_hat)^2` and finite `C2` normalizations, global Green data and renormalized-product data still leave complete `Gamma1/Q1` uncertified. Transfer reopens only after those data fix complete `Q1` and an extended classical contraction is certified |
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
- [`reports/four-dimensional-algebraic-cubic-weyl-carriers.md`](reports/four-dimensional-algebraic-cubic-weyl-carriers.md)
  records the exhaustive zero-derivative `C3` carrier basis, its exact
  chiral/parity crosswalk, and the fail-closed boundary to derivative-decorated
  nonlocal form factors and coefficients.
- [`reports/four-dimensional-third-curvature-weyl-carrier-manifest.md`](reports/four-dimensional-third-curvature-weyl-carrier-manifest.md)
  records the five parity-even source carriers, their exact `S3/S2/C3` label
  source/effective stabilizers, the scalar-flat `I29` reversal identity, the
  `11 -> 10` effective four-dimensional functional quotient, and the
  fail-closed boundary to the actual repository functions and coefficients.
- [`reports/cpt-universal-third-curvature-kernels.md`](reports/cpt-universal-third-curvature-kernels.md)
  records the exact primary-source alpha, tree, and logarithmic kernels for
  those five rows, their rank-one scalar fixture, and the minimal missing
  generic-background full-BV trace substitution that blocks repository
  coefficients.
- [`reports/generic-background-diff-weyl-ghost-cpt-obstruction.md`](reports/generic-background-diff-weyl-ghost-cpt-obstruction.md)
  records the exact coupled FP rows, beta-independent Schur complement,
  nonminimal principal spectrum, tracefree-Ricci Hodge mixing, Einstein
  reduction, and the architecture-specific boundary to a matched nonminimal
  ghost determinant.
- [`reports/generic-background-ghost-endo-duhamel-reduction.md`](reports/generic-background-ghost-endo-duhamel-reduction.md)
  records the exact `H=H0-2 Ric` split, finite-proper-time Endo heat kernel,
  nonzero-mode determinant identity, and the finite cubic Ricci-insertion
  work table.
- [`reports/generic-background-ghost-n1-n2-hodge-resolvent-reduction.md`](reports/generic-background-ghost-n1-n2-hodge-resolvent-reduction.md)
  integrates the Endo identity to
  `G_H0=G_F-(1/3)d Delta_0^-2 delta` and reduces the curved `n=1,n=2`
  architecture to five exact minimal resolvent carriers.
- [`reports/generic-background-ghost-n1-n2-vector-cpt-projection.md`](reports/generic-background-ghost-n1-n2-vector-cpt-projection.md)
  evaluates the combined pure-vector `n=1+n=2` slice from CPT rows 1, 3 and
  14 and proves that the remaining three longitudinal carriers require
  nonminimal `D_W=delta W d` kernels.
- [`reports/generic-background-ghost-longitudinal-schur-resummation.md`](reports/generic-background-ghost-longitudinal-schur-resummation.md)
  resums those three longitudinal towers into one normalized scalar Schur
  determinant, fixes the cubic weights `(-1/3,1/9,-1/81)`, reproduces the
  Einstein scalar factor, and records the unevaluated generic finite kernel.
- [`reports/generic-background-ghost-schur-schatten-split.md`](reports/generic-background-ghost-schur-schatten-split.md)
  proves the sharp `S_3` trace-ideal disposition, defines the canonical
  modified Fredholm tail, and computes `Wres(K)`, `Wres(K^2)`, and
  `Wres(log S_L)` while retaining the two finite regulated trace rows and the
  reference-specific scale conversion.
- [`reports/generic-background-ghost-schur-wodzicki-residue.md`](reports/generic-background-ghost-schur-wodzicki-residue.md)
  derives the linear and quadratic Schur residues from an exact mixed heat
  insertion, checks Einstein and isotropic specializations independently,
  and keeps the finite determinant claim open.
- [`reports/generic-background-ghost-schur-weight-raised-zeta-factorization.md`](reports/generic-background-ghost-schur-weight-raised-zeta-factorization.md)
  freezes the generic convention `A=S_L Q`, `B=Q`, proves that the BCH
  weighted trace vanishes through four-dimensional residue order, and obtains
  the exact local defect `-(1/4)Wres(K^2)`. Its round-`S4` value `-1/3` is
  crosswalked explicitly to the distinct Einstein-ratio defect `5/3`.
- [`reports/generic-background-ghost-n3-adiabatic-carrier.md`](reports/generic-background-ghost-n3-adiabatic-carrier.md)
  computes the exact three-insertion isotropic tensor numerator and its
  scalar-flat coefficient while keeping the IR-singular adiabatic radial
  integral and nonzero-momentum triangle explicitly open.
- [`reports/generic-background-ghost-n3-five-carrier-projection.md`](reports/generic-background-ghost-n3-five-carrier-projection.md)
  records the exact eleven-to-ten scalar-flat carrier projection of the
  generic ghost `n=3` triangle, its rational simplex numerators, unseen exact
  holdout replays, and the still-open `n=1/n=2`, physical-kernel and complete
  form-factor boundaries.
- [`reports/generic-background-ghost-n3-symmetric-point-simplex-integration.md`](reports/generic-background-ghost-n3-symmetric-point-simplex-integration.md)
  integrates all eleven projected ghost `n=3` coordinates at
  `x1=x2=x3=1`, reduces them to one Clausen master with exact divergence
  witnesses, and keeps the generic kinematic functions and physical kernel
  fail-closed.
- [`reports/generic-background-ghost-n3-barycentric-factorization.md`](reports/generic-background-ghost-n3-barycentric-factorization.md)
  proves ten exact generic `Delta` cancellations, all barycentric edge and
  vertex orders, the unique direct `I10` edge restriction and the pointwise
  `I28` relation.
- [`reports/generic-background-ghost-n3-pole3-relative-ibp.md`](reports/generic-background-ghost-n3-pole3-relative-ibp.md)
  reduces all ten pole-three rows to the scalar triangle and two first
  derivatives, stores four exact open-edge tangent primitives, and proves by
  normalized dual witnesses that zero punctured-corner flux is impossible in
  the declared ansatz.
- [`reports/generic-background-ghost-n3-pole3-integrated-functions.md`](reports/generic-background-ghost-n3-pole3-integrated-functions.md)
  certifies the exact `S3`-covariant scalar-triangle differential system,
  converts the two derivative masters to `J` plus two bubble-log ratios, and
  evaluates the equal-weight corner flux rationally. All ten generic pole-three
  functions are complete with exact symmetric-point regressions.
- [`reports/generic-background-ghost-n3-i29-integrated-function.md`](reports/generic-background-ghost-n3-i29-integrated-function.md)
  reduces the sole pole-four `I29` row by a full 55-row exact relative-IBP
  identity, proves that no new transcendental master is required, evaluates
  its rational corner flux, and closes all eleven generic ghost `n=3`
  functions while keeping determinant and physical-Hessian assembly open.
- [`reports/generic-background-physical-hessian-linear-curvature.md`](reports/generic-background-physical-hessian-linear-curvature.md)
  imports the same-gauge traceless metric Hessian through first curvature
  order as exact `V/N/U` ledgers, fixes the repository normalization, checks
  the scalar-flat and round-`S4` restrictions, and activates the physical
  three-linear `n=3` vertex. The projected algebraic curvature-squared block
  is also imported with an exact gauge-ordering crosswalk and round-`S4`
  normalization split. Its polarization, the mixed `H1`-`H2` trace, tensor
  triangle integration, and five form-factor assembly remain fail-closed.
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
- [`reports/wess-zumino-minimal-bv-cotangent-lift.md`](reports/wess-zumino-minimal-bv-cotangent-lift.md)
  records the exact compensator cotangent lift, dressed canonical variables,
  and contractible Weyl quartet in the formal tau-adic local algebra.
- [`reports/wess-zumino-extended-local-bv-cohomology.md`](reports/wess-zumino-extended-local-bv-cohomology.md)
  records the complete dimension-four extended `H04/H14` quotient and the
  coefficient-bearing one-loop local Euclidean QME restoration, with the
  all-loop, Lorentzian, state, and residual-transfer boundaries left open.
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
