# Classical $D$-quotient challenge

This directory is the fail-closed handoff for the classical question posed in
[`notes/d-quotient-classical-team-brief.md`](../notes/d-quotient-classical-team-brief.md):
when is cylinder time translation/dilatation $D$ proper gauge, and when is it
a charged physical symmetry?

The status record deliberately separates three kinds of statement:

1. a charge verdict on a precisely declared phase space;
2. an imported theorem about the selected absolute residual complex;
3. an open comparison in a different matter, background, or boundary setting.

In particular, the Paper-VII Cartan contraction is not accepted as a proof
that $D$ has zero covariant phase-space charge.  Conversely, a nonzero
quadratic charge on the unrestricted linearized space is not accepted as a
counterexample on the Taub-zero, nonlinearly integrable phase space.

## Artifacts

- Machine-readable status:
  [`certificates/CLASSICAL_D_QUOTIENT_STATUS.json`](certificates/CLASSICAL_D_QUOTIENT_STATUS.json)
- JSON Schema:
  [`schema/classical-status-v1.schema.json`](schema/classical-status-v1.schema.json)
- Human report:
  [`reports/classical-d-quotient-status.md`](reports/classical-d-quotient-status.md)
- Dependency-free verifier:
  [`verify_classical_status.py`](verify_classical_status.py)
- Scalar-clock obstruction certificate:
  [`certificates/SCALAR_CLOCK_VERTICAL_SLICE.json`](certificates/SCALAR_CLOCK_VERTICAL_SLICE.json)
- Scalar-clock report:
  [`reports/scalar-clock-vertical-slice.md`](reports/scalar-clock-vertical-slice.md)
- Neutral two-field clock certificate:
  [`certificates/NEUTRAL_CONFORMAL_CLOCK_PAIR.json`](certificates/NEUTRAL_CONFORMAL_CLOCK_PAIR.json)
- Neutral two-field clock report:
  [`reports/neutral-conformal-clock-pair.md`](reports/neutral-conformal-clock-pair.md)
- Neutral clock BV/health obstruction:
  [`certificates/NEUTRAL_CLOCK_BV_HEALTH_AUDIT.json`](certificates/NEUTRAL_CLOCK_BV_HEALTH_AUDIT.json)
- Neutral clock BV/health report:
  [`reports/neutral-clock-bv-health-audit.md`](reports/neutral-clock-bv-health-audit.md)
- Homogeneous positive-sign stealth-clock certificate:
  [`certificates/HOMOGENEOUS_POSITIVE_CONFORMAL_STEALTH_CLOCK.json`](certificates/HOMOGENEOUS_POSITIVE_CONFORMAL_STEALTH_CLOCK.json)
- Homogeneous positive-sign stealth-clock report:
  [`reports/homogeneous-positive-conformal-stealth-clock.md`](reports/homogeneous-positive-conformal-stealth-clock.md)
- Complete standard one-field stealth-clock no-go certificate:
  [`certificates/INHOMOGENEOUS_CONFORMAL_STEALTH_CLOCK_NO_GO.json`](certificates/INHOMOGENEOUS_CONFORMAL_STEALTH_CLOCK_NO_GO.json)
- Complete standard one-field stealth-clock no-go report:
  [`reports/inhomogeneous-conformal-stealth-clock-no-go.md`](reports/inhomogeneous-conformal-stealth-clock-no-go.md)
- Positive Berger-clock background certificate:
  [`certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json`](certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json)
- Positive Berger-clock background report:
  [`reports/positive-berger-clock-background.md`](reports/positive-berger-clock-background.md)
- Berger clock reduced-charge seed:
  [`certificates/BERGER_CLOCK_REDUCED_CHARGE_SEED.json`](certificates/BERGER_CLOCK_REDUCED_CHARGE_SEED.json)
- Fixed-coupling Berger delta-charge theorem:
  [`certificates/BERGER_FIXED_COUPLING_DELTA_CHARGE.json`](certificates/BERGER_FIXED_COUPLING_DELTA_CHARGE.json)
- Fixed-coupling Berger delta-charge report:
  [`reports/berger-fixed-coupling-delta-charge.md`](reports/berger-fixed-coupling-delta-charge.md)
- Support-local minimal Berger-clock BV contraction:
  [`certificates/BERGER_MINIMAL_BV_CLOCK_SDR.json`](certificates/BERGER_MINIMAL_BV_CLOCK_SDR.json)
- Minimal Berger-clock BV contraction report:
  [`reports/berger-minimal-bv-clock-sdr.md`](reports/berger-minimal-bv-clock-sdr.md)
- Covariant minimal-BV antifield/Koszul--Tate V2 export, with the resolved
  finite-receiver obstruction retained as a regression receipt:
  [`minimal_bv_antifield/foundation/atom_basis_manifest.json`](minimal_bv_antifield/foundation/atom_basis_manifest.json),
  [`certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json`](certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2.json),
  [`certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2_RECEIVER_OBSTRUCTION.json`](certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_EXPORT_V2_RECEIVER_OBSTRUCTION.json),
  [`reports/classical-minimal-bv-antifield-export-v2-receiver-obstruction.md`](reports/classical-minimal-bv-antifield-export-v2-receiver-obstruction.md)
- Authoritative 26-component retained minimal-BV layout:
  [`certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json`](certificates/BERGER_RETAINED_MINIMAL_LAYOUT.json)
- Retained minimal-BV layout report:
  [`reports/berger-retained-minimal-layout.md`](reports/berger-retained-minimal-layout.md)
- Retained minimal-operator preflight:
  [`certificates/BERGER_RETAINED_MINIMAL_OPERATOR_PREFLIGHT.json`](certificates/BERGER_RETAINED_MINIMAL_OPERATOR_PREFLIGHT.json)
- Retained minimal-operator preflight report:
  [`reports/berger-retained-minimal-operator-preflight.md`](reports/berger-retained-minimal-operator-preflight.md)
- Complete retained 26-row minimal operator:
  [`certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json`](certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json)
- Complete retained minimal-operator report:
  [`reports/berger-retained-minimal-operator.md`](reports/berger-retained-minimal-operator.md)
- Rank-46 physical-helicity projective module and exact subprincipal filtered
  branch obstruction:
  [`certificates/BERGER_RETAINED_46_STF2_PHYSICAL_HELICITY_FILTERED_QUOTIENT_V1.json`](certificates/BERGER_RETAINED_46_STF2_PHYSICAL_HELICITY_FILTERED_QUOTIENT_V1.json),
  [`certificates/BERGER_RETAINED_46_STF2_SUBPRINCIPAL_BRANCH_ANCHOR_OR_OBSTRUCTION_V1.json`](certificates/BERGER_RETAINED_46_STF2_SUBPRINCIPAL_BRANCH_ANCHOR_OR_OBSTRUCTION_V1.json),
  [`reports/berger-retained-46-stf2-subprincipal-branch-anchor-or-obstruction.md`](reports/berger-retained-46-stf2-subprincipal-branch-anchor-or-obstruction.md)
- Berger causal-witness endpoint preflight:
  [`certificates/BERGER_CAUSAL_WITNESS_PREFLIGHT.json`](certificates/BERGER_CAUSAL_WITNESS_PREFLIGHT.json)
- Berger causal-witness preflight report:
  [`reports/berger-causal-witness-preflight.md`](reports/berger-causal-witness-preflight.md)
- Clock-reattached Berger principal witness:
  [`certificates/BERGER_CLOCK_REATTACHED_PRINCIPAL_WITNESS.json`](certificates/BERGER_CLOCK_REATTACHED_PRINCIPAL_WITNESS.json)
- Clock-reattached principal-witness report:
  [`reports/berger-clock-reattached-principal-witness.md`](reports/berger-clock-reattached-principal-witness.md)
- Authoritative 34-row curved-witness candidate export:
  [`certificates/BERGER_CURVED_CLOCK_REATTACHED_WITNESS.json`](certificates/BERGER_CURVED_CLOCK_REATTACHED_WITNESS.json)
- Curved-witness candidate report:
  [`reports/berger-curved-clock-reattached-witness.md`](reports/berger-curved-clock-reattached-witness.md)
- Submitted-candidate/principal compatibility audit:
  [`certificates/BERGER_CURVED_WITNESS_PRINCIPAL_COMPATIBILITY.json`](certificates/BERGER_CURVED_WITNESS_PRINCIPAL_COMPATIBILITY.json)
- Compatibility-audit report:
  [`reports/berger-curved-witness-principal-compatibility.md`](reports/berger-curved-witness-principal-compatibility.md)
- Coherent raw clock-reattached witness transport:
  [`certificates/BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT.json`](certificates/BERGER_RAW_CLOCK_REATTACHED_WITNESS_TRANSPORT.json)
- Raw witness-transport report:
  [`reports/berger-raw-clock-reattached-witness-transport.md`](reports/berger-raw-clock-reattached-witness-transport.md)
- Raw endpoint Green preflight:
  [`certificates/BERGER_RAW_ENDPOINT_GREEN_PREFLIGHT.json`](certificates/BERGER_RAW_ENDPOINT_GREEN_PREFLIGHT.json)
- Raw endpoint Green-preflight report:
  [`reports/berger-raw-endpoint-green-preflight.md`](reports/berger-raw-endpoint-green-preflight.md)
- Rank-one scalar-wave endpoint extension:
  [`certificates/BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION.json`](certificates/BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION.json)
- Rank-one wave-extension report:
  [`reports/berger-raw-endpoint-rank-one-wave-extension.md`](reports/berger-raw-endpoint-rank-one-wave-extension.md)
- Cyclic all-row analytic Green realization:
  [`certificates/BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION.json`](certificates/BERGER_RAW_ENDPOINT_CYCLIC_GREEN_REALIZATION.json)
- Cyclic Green-realization report:
  [`reports/berger-raw-endpoint-cyclic-green-realization.md`](reports/berger-raw-endpoint-cyclic-green-realization.md)
- Exact lower-by-two metric biwave normal form and scoped canonical-factor no-go:
  [`certificates/BERGER_METRIC_LOWER_BY_TWO_BIWAVE.json`](certificates/BERGER_METRIC_LOWER_BY_TWO_BIWAVE.json)
- Lower-by-two metric report:
  [`reports/berger-metric-lower-by-two-biwave.md`](reports/berger-metric-lower-by-two-biwave.md)
- Exact metric-cone obstruction for a Green inverse of the complete 13-row endpoint:
  [`certificates/BERGER_RAW_ENDPOINT_METRIC_CONE_NO_GO.json`](certificates/BERGER_RAW_ENDPOINT_METRIC_CONE_NO_GO.json)
- Metric-cone no-go and hybrid-chain interpretation:
  [`reports/berger-raw-endpoint-metric-cone-no-go.md`](reports/berger-raw-endpoint-metric-cone-no-go.md)
- Microlocal support proof and exact mixed-polarization correction:
  [`certificates/BERGER_EXTRA_CONE_MICROLOCAL_LOCALIZATION.json`](certificates/BERGER_EXTRA_CONE_MICROLOCAL_LOCALIZATION.json)
- Extra-cone localization report:
  [`reports/berger-extra-cone-microlocal-localization.md`](reports/berger-extra-cone-microlocal-localization.md)
- Typed retained metric causal Volterra resolvent (V2):
  [`certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2.json`](certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2.json)
- Typed Volterra construction, estimates and adjoint-reversal proof:
  [`reports/berger-retained-biwave-volterra-resolvent-v2.md`](reports/berger-retained-biwave-volterra-resolvent-v2.md)
- Background-independent typed lower-order biwave theorem:
  [`certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1.json`](certificates/TYPED_BIWAVE_VOLTERRA_GREEN_THEOREM_V1.json)
- The theorem allows distinct noncommuting normally hyperbolic factors and
  smooth time-dependent order-at-most-two remainders, provided the declared
  finite-slab wave-energy graph bound holds. It keeps source and solution
  resolvents separate, proves both inverse identities and the correctly typed
  adjoint reversal, and is independently replayed on a second rational
  noncommuting fixture:
  [`reports/typed-biwave-volterra-green-theorem.md`](reports/typed-biwave-volterra-green-theorem.md)
- Strict schema, source manifest and timed verification receipt:
  [`schema/berger-retained-biwave-volterra-resolvent-v2.schema.json`](schema/berger-retained-biwave-volterra-resolvent-v2.schema.json),
  [`manifests/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2_SOURCE_MANIFEST.json`](manifests/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2_SOURCE_MANIFEST.json),
  [`certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2_VERIFICATION_RECEIPT.json`](certificates/BERGER_RETAINED_BIWAVE_VOLTERRA_RESOLVENT_V2_VERIFICATION_RECEIPT.json)
- Complete retained 26-row causal Green homotopy pinned to Volterra V2:
  [`certificates/BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json`](certificates/BERGER_26_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json)
- Degreewise V2 assembly, support, cyclicity and D-equivariance proof:
  [`reports/berger-26-row-causal-green-homotopy-v2.md`](reports/berger-26-row-causal-green-homotopy-v2.md)
- Complete 54-row causal V2 lift:
  [`certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json`](certificates/BERGER_54_ROW_CAUSAL_GREEN_HOMOTOPY_V2.json)
- Full gauge-fixed causal-homotopy V2 proof:
  [`reports/berger-54-row-causal-green-homotopy-v2.md`](reports/berger-54-row-causal-green-homotopy-v2.md)
- Abstract cyclic causal-transfer theorem for support-local SDR lifts and
  descents, finite direct sums and finite cyclic shears:
  [`certificates/ABSTRACT_CYCLIC_CAUSAL_TRANSFER.json`](certificates/ABSTRACT_CYCLIC_CAUSAL_TRANSFER.json)
- Human-readable theorem, proof and Berger 26-to-54 / coupled 36-to-64 replay:
  [`reports/abstract-cyclic-causal-transfer.md`](reports/abstract-cyclic-causal-transfer.md)
- Global conformal-orbit consumer on \(\mathbb R\times S^3\), with the
  affine Diff--Weyl ghost/cotangent shear, transported gauge fermion, exact
  Green homotopies and one nonconstant bounded conformal factor:
  [`certificates/CONFORMALLY_RELATED_CYCLIC_CAUSAL_TRANSFER_V1.json`](certificates/CONFORMALLY_RELATED_CYCLIC_CAUSAL_TRANSFER_V1.json),
  [`reports/conformally-related-cyclic-causal-transfer.md`](reports/conformally-related-cyclic-causal-transfer.md)
- First curvature gate beyond that orbit: the exact Nariai Weyl component
  obstructs any extension by the same zero-order conformal/tractor
  conjugation, while curved differential HPL and independent Green routes
  remain open:
  [`certificates/CONFORMALLY_EINSTEIN_TRACTOR_CURVATURE_OBSTRUCTION_V1.json`](certificates/CONFORMALLY_EINSTEIN_TRACTOR_CURVATURE_OBSTRUCTION_V1.json),
  [`reports/conformally-einstein-tractor-curvature-obstruction.md`](reports/conformally-einstein-tractor-curvature-obstruction.md)
- Curved-parent repair: the exact \(-F\!\cdot\) Yang--Mills detour correction,
  its two composition identities, and the resulting formally self-adjoint
  Nariai parent complex (without yet claiming BGG compression or Green data):
  [`certificates/CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1.json`](certificates/CONFORMALLY_EINSTEIN_YANG_MILLS_DETOUR_CORRECTION_V1.json),
  [`reports/conformally-einstein-yang-mills-detour-correction.md`](reports/conformally-einstein-yang-mills-detour-correction.md)
- First Nariai BGG-compression gate: raw pointwise compression of the tractor
  curvature action has a rank-two cyclic defect, proving that the omitted
  derivative splitting/HPL corrections are mandatory:
  [`certificates/NARIAI_POINTWISE_BGG_CURVATURE_COMPRESSION_OBSTRUCTION_V1.json`](certificates/NARIAI_POINTWISE_BGG_CURVATURE_COMPRESSION_OBSTRUCTION_V1.json),
  [`reports/nariai-pointwise-bgg-curvature-compression-obstruction.md`](reports/nariai-pointwise-bgg-curvature-compression-obstruction.md)
- First strictification screen beyond that gate: with the Nariai Schouten
  components `(-1/6,+1/6,+1/6,+1/6)` and the distinct covector/dual-vector
  curvature actions enforced, arbitrary zeroth-order corrections to both BGG
  splitting maps cannot make the first square strict.  All derivative
  equations consistently and uniquely fix the correction, after which a
  rank-four algebraic residual with twelve entries remains (normalized
  witness one).
  Genuinely derivative-dependent and homotopy-coherent curved transfer remain
  open:
  [`certificates/NARIAI_FIRST_BGG_ZEROTH_ORDER_STRICTIFICATION_OBSTRUCTION_V1.json`](certificates/NARIAI_FIRST_BGG_ZEROTH_ORDER_STRICTIFICATION_OBSTRUCTION_V1.json),
  [`reports/nariai-first-bgg-zeroth-order-strictification-obstruction.md`](reports/nariai-first-bgg-zeroth-order-strictification-obstruction.md)
- Curvature-incidence resolution of that residue: coefficient by coefficient,
  the rank-four twelve-entry term is exactly
  `d^D L0 - L1_corrected K = I_Omega`, with
  `(I_Omega xi)_a = Omega_ab xi^b`.  The independently reconstructed
  `ad(Omega)` also agrees exactly with the PBW normal-tractor square.  Thus
  the residue is the canonical curved-connection incidence, not unexplained
  cone cohomology.  The strict square remains false; its cyclic mapping-cone
  completion is the next gate:
  [`certificates/NARIAI_CURVATURE_INCIDENCE_FIRST_SQUARE_V1.json`](certificates/NARIAI_CURVATURE_INCIDENCE_FIRST_SQUARE_V1.json),
  [`reports/nariai-curvature-incidence-first-square.md`](reports/nariai-curvature-incidence-first-square.md)
- Shifted-chain continuation and saddle preflight: the incidence extends
  exactly as `Phi=(I_Omega,M^D L1_corrected)`, with
  `M^D I_Omega + Phi1 K=0`.  The factorized relative saddle
  `S=A^sharp M^D A` annihilates `(K,I_Omega)^T` in both blocks.  The generic
  post-normal-order PBW adjoint replay remains fail-closed because it does not
  yet encode the Hom-bundle covariance of two cross-form coefficient blocks;
  it leaves a scoped rank-60 algebraic verifier defect.  This is not a
  formal-adjointness no-go for the factorized Yang--Mills operator, and the
  independent checker in the following item removes it from the cone's
  theorem dependencies:
  [`certificates/NARIAI_CURVATURE_INCIDENCE_SHIFTED_CHAIN_V1.json`](certificates/NARIAI_CURVATURE_INCIDENCE_SHIFTED_CHAIN_V1.json),
  [`reports/nariai-curvature-incidence-shifted-chain.md`](reports/nariai-curvature-incidence-shifted-chain.md)
- Completed parent-relative cone: an independent factorized variational
  checker now supplies the rigorous alternative to the deficient generic PBW
  adjoint replay.  The eight-block finite-order cylinder is nilpotent and odd
  cyclic; its `L1_corrected` shear is canonical and invertible; and its
  inclusion, projection and cyclic homotopy give an exact SDR to the corrected
  Yang--Mills parent.  The endpoint ghost image is exactly
  `(K xi,I_Omega xi)`.  This does not yet identify the metric Bach endpoint
  with the cylinder or construct Nariai Green homotopies:
  [`certificates/NARIAI_CURVATURE_INCIDENCE_CYCLIC_MAPPING_CYLINDER_V1.json`](certificates/NARIAI_CURVATURE_INCIDENCE_CYCLIC_MAPPING_CYLINDER_V1.json),
  [`reports/nariai-curvature-incidence-cyclic-mapping-cylinder.md`](reports/nariai-curvature-incidence-cyclic-mapping-cylinder.md)
- All-order strict metric-graph obstruction: extending the canonical ghost
  image by a field-only graph `h -> (h,R h)` would require
  `R K=I_Omega`.  The global Nariai Killing field `partial_chi` has
  `K partial_chi=0`, while the exact incidence table gives
  `(I_Omega partial_chi)[4]=2/3`.  Hence no finite-order differential `R` of
  any order can satisfy the required square.  Curved-PBW screens through
  order four reproduce the same rank-four incompatibility but are not used
  to infer the all-order result.  The next admissible comparison is a
  relative equation-level or homotopy-coherent metric--Bach cone:
  [`certificates/NARIAI_STRICT_METRIC_GRAPH_CHAIN_MAP_OBSTRUCTION_V1.json`](certificates/NARIAI_STRICT_METRIC_GRAPH_CHAIN_MAP_OBSTRUCTION_V1.json),
  [`reports/nariai-strict-metric-graph-chain-map-obstruction.md`](reports/nariai-strict-metric-graph-chain-map-obstruction.md)
- Action-derived metric endpoint: direct variation of
  `B_ab=nabla^c nabla^d C_acbd+(1/2)R^cd C_acbd`, including all four
  connection variations against the nonzero parallel Nariai Weyl tensor,
  gives the complete trace-free Bach Hessian at orders zero, two and four.
  Its symmetry, trace, divergence and gauge defects vanish exactly.  In the
  repository normalization the corrected parent compression obeys
  `B_parent,comp+Q_unique=-2 B_action` coefficientwise; an independent
  product-scaling family fixes the algebraic normalization.  This supplies
  the operator used by the typed action-pairing theorem below:
  [`certificates/NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1.json`](certificates/NARIAI_ACTION_DERIVED_BACH_ENDPOINT_V1.json),
  [`reports/nariai-action-derived-bach-endpoint.md`](reports/nariai-action-derived-bach-endpoint.md)
- Action-paired metric BV endpoint: the tensor Gram is applied exactly once,
  when the Bach tensor is converted into endpoint covector coordinates.  The
  resulting field/equation pairing is `I9`, the ghost/identity pairing is
  `diag(-1,1,1,1)`, and the exact four-row complex
  `H0 -> H1 -> H1dual -> H0dual` is nilpotent and odd cyclic.  An independent
  consumer reconstructs `Ksharp`, `B K=0` and the tensor divergence directly
  from the serialized coefficient tables.  The next gate is now solely the
  relative parent--metric equation/identity-row cone:
  [`certificates/NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1.json`](certificates/NARIAI_METRIC_BACH_CYCLIC_BV_COMPLEX_V1.json),
  [`reports/nariai-metric-bach-cyclic-bv-complex.md`](reports/nariai-metric-bach-cyclic-bv-complex.md)
- Global reducibility mismatch: the exact metric complex has at least six
  independent smooth ghost classes supplied by the product Killing algebra.
  A parallel normal adjoint tractor must lie in the common kernel of the
  stacked `90x15` tractor-curvature matrix, whose exact rank is fourteen, so
  the current Yang--Mills parent has ghost cohomology dimension at most one.
  The incidence cylinder retracts to that parent and cannot change the bound.
  Therefore no equation/identity-only contractible cone can establish the
  desired quasi-isomorphism; at least five noncontractible reducibility
  directions, equivalently the curvature-corrected infinitesimal-automorphism
  prolongation, must be supplied first:
  [`certificates/NARIAI_PARENT_REDUCIBILITY_MISMATCH_V1.json`](certificates/NARIAI_PARENT_REDUCIBILITY_MISMATCH_V1.json),
  [`reports/nariai-parent-reducibility-mismatch.md`](reports/nariai-parent-reducibility-mismatch.md)
- Curvature-corrected automorphism prolongation: replacing the parallel-
  tractor ghost operator by `d_aut=d^D-I_Omega p0` gives the strict local
  two-arrow complex
  `C0 -> C1+H1 -> C1dual`, with maps `(d_aut,K p0)` and `(M^D,-Phi)`.
  Both compositions vanish coefficientwise, and the corrected BGG graph
  `(L0;L1,identity)` carries every metric gauge variation and Killing
  reducibility exactly.  This resolves the ghost mismatch without yet adding
  the Bach equation or its cyclic cotangent completion:
  [`certificates/NARIAI_AUTOMORPHISM_PROLONGATION_FIRST_TWO_ROWS_V1.json`](certificates/NARIAI_AUTOMORPHISM_PROLONGATION_FIRST_TWO_ROWS_V1.json),
  [`reports/nariai-automorphism-prolongation-first-two-rows.md`](reports/nariai-automorphism-prolongation-first-two-rows.md)
- Cyclic Bach completion: the corrected constraint complex has the canonical
  288-component odd-cotangent saddle with quadratic action
  `1/2<h,B_action h>+<lambda,M^D a-Phi h>`.  Its complete differential is
  nilpotent and odd cyclic, all dual rows are forced by the displayed fibre
  pairings, and the exact four-row metric Bach complex embeds isometrically as
  the corrected BGG graph.  This is a local differential complex, not yet an
  SDR or Green theorem:
  [`certificates/NARIAI_AUTOMORPHISM_CYCLIC_BACH_EXTENSION_V1.json`](certificates/NARIAI_AUTOMORPHISM_CYCLIC_BACH_EXTENSION_V1.json),
  [`reports/nariai-automorphism-cyclic-bach-extension.md`](reports/nariai-automorphism-cyclic-bach-extension.md)
- SDR symbol obstruction for that carrier: with explicit Douglis/Rees weights
  `(0,1,1,1,3,5,5,6)`, the metric Bach symbol complex is exact at the
  timelike covector `(1,0,0,0)`, while the multiplier has no incoming arrow
  and inherits the 15-dimensional kernel of the rank-45 parent middle.  Thus
  the 288-component saddle cannot admit a finite-order filtration-compatible
  SDR onto the metric graph.  This does not obstruct the required larger
  cyclic parent-detour mapping cone:
  [`certificates/NARIAI_AUTOMORPHISM_CYCLIC_BACH_SDR_SYMBOL_OBSTRUCTION_V1.json`](certificates/NARIAI_AUTOMORPHISM_CYCLIC_BACH_SDR_SYMBOL_OBSTRUCTION_V1.json),
  [`reports/nariai-automorphism-cyclic-bach-sdr-symbol-obstruction.md`](reports/nariai-automorphism-cyclic-bach-sdr-symbol-obstruction.md)
- Parent-detour cone repair: replacing the incoming-free multiplier saddle by
  an economical 310-component cone adds the eleven-dimensional `ker(p0)`
  complement and its cyclic dual.  In split variables it is the exact direct
  sum of the metric Bach complex, a pointwise ghost-complement pair, and the
  parent saddle `[[ -M^D/2, 1 ], [ 1, 0 ]]`.  The last block has the
  finite-order local inverse `[[0,1],[1,M^D/2]]`; the resulting inclusion,
  projection and odd-cyclic homotopy satisfy `PI=1` and
  `1-IP=QH+HQ`.  The coefficientwise Schur Hessian is exactly `B_action`.
  This closes the support-local SDR, but not the Green theorem:
  [`certificates/NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1.json`](certificates/NARIAI_PARENT_DETOUR_MAPPING_CONE_REPAIR_V1.json),
  [`reports/nariai-parent-detour-mapping-cone-repair.md`](reports/nariai-parent-detour-mapping-cone-repair.md)
- Curved parent causal input: on global unit Nariai the normal
  adjoint-tractor connection is Yang--Mills.  The backward witness
  `(delta^D,1,d^D)` turns the four parent degrees into twisted Hodge wave
  operators with scalar metric principal symbol; curvature contributes only
  lower-order endomorphisms.  Standard normally-hyperbolic uniqueness gives
  chain-commuting advanced/retarded Green operators and causal parent
  homotopies with the pairing-derived complementary-degree adjoint reversal.
  The rank-310 and metric transfers remain fail-closed:
  [`certificates/NARIAI_YANG_MILLS_PARENT_GREEN_HOMOTOPY_V1.json`](certificates/NARIAI_YANG_MILLS_PARENT_GREEN_HOMOTOPY_V1.json),
  [`reports/nariai-yang-mills-parent-green-homotopy.md`](reports/nariai-yang-mills-parent-green-homotopy.md)
- Repaired-parent witness preflight: the rank-310 SDR retracts to the metric
  complex, so the parent homotopy cannot be transported by reversing the SDR.
  The correctly typed universal third-order companion nevertheless closes the
  exact leading symbols:
  `T_pr K=(zeta^2)^2 I_4` and
  `B_action+(G_H K T_pr)/2=(zeta^2)^2 G_H/2`.
  The action Bach row is evaluation-dual, so the fibre Gram `G_H` is essential.
  The tempting parent-divergence candidate `p0 delta^D L1` has zero cubic
  symbol and is rejected.  Lower-order factorization and all Green flags stay
  open:
  [`certificates/NARIAI_REPAIRED_PARENT_GREEN_WITNESS_PREFLIGHT_V1.json`](certificates/NARIAI_REPAIRED_PARENT_GREEN_WITNESS_PREFLIGHT_V1.json),
  [`reports/nariai-repaired-parent-green-witness-preflight.md`](reports/nariai-repaired-parent-green-witness-preflight.md)
- Metric biwave Green theorem: the unique Einstein-background correction is
  `T=T_pr+div/3`.  It gives the exact factorizations
  `T K=(Box+1)(Box+1/3)I_4` and
  `G_H^-1 B_action+K T/2=(Box I+A)(Box I+B)/2`, where the two
  parallel curvature endomorphisms commute and are `G_H`-self-adjoint.
  Every primal and formal-dual factor is normally hyperbolic, so their
  same-sided Green compositions give the complete four-row metric causal
  homotopy.  This is the endpoint input used by the all-row transfer below:
  [`certificates/NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json`](certificates/NARIAI_METRIC_BIWAVE_GREEN_HOMOTOPY_V1.json),
  [`reports/nariai-metric-biwave-green-homotopy.md`](reports/nariai-metric-biwave-green-homotopy.md)
- Complete Nariai all-row causal transfer: the cyclic support-local SDR and
  metric endpoint combine as
  `Lambda_310,+/-=H+I Lambda_metric,+/- P`.  Exact operator-polynomial replay
  verifies the chain identity in split and original coordinates, the side
  conditions `H^2=HI=PH=0`, and exact descent
  `P Lambda_310,+/- I=Lambda_metric,+/-`.  All ten blocks and degree ranks
  `15,140,140,15` are enumerated; no row is dropped.  Causal support and
  complementary-degree adjoint reversal transfer from the metric endpoint:
  [`certificates/NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1.json`](certificates/NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1.json),
  [`reports/nariai-repaired-310-all-row-green-transfer.md`](reports/nariai-repaired-310-all-row-green-transfer.md)
- Bach-flat parent stability: in four dimensions Bach-flatness is the
  Yang--Mills condition for the normal tractor connection, so the universal
  detour witness gives degreewise normally hyperbolic parent blocks on every
  globally hyperbolic Bach-flat background.  An explicit ADM ball of radius
  `1/4` around Nariai has a common reference speed cone and contains the
  nonconstant, non-conformally-flat consumer
  `g_Omega=(1+1/(10(1+t^2)))^2 g_N`.  This is a genuine relative-open `G3`
  parent class; the metric SDR and metric Bach Green theorem on that class
  remain fail-closed:
  [`certificates/BACH_FLAT_PARENT_GREEN_STABILITY_V1.json`](certificates/BACH_FLAT_PARENT_GREEN_STABILITY_V1.json),
  [`reports/bach-flat-parent-green-stability.md`](reports/bach-flat-parent-green-stability.md)
- Conformal-Nariai metric/all-row class: finite Diff--Weyl BV covariance,
  including the affine Weyl-ghost term and cotangent shear, transports the
  metric complex, the rank-310 cyclic SDR, and both causal homotopies to
  `g_phi=exp(2 phi)g_N` whenever `sup|exp(phi)-1|<1/9`.  This open class stays
  inside the parent ADM radius and contains the exact nonconstant consumer.
  The transformed maps satisfy the SDR identities, causal chain identity,
  adjoint reversal, and exact metric descent.  Bach-flat directions transverse
  to this conformal orbit remain open:
  [`certificates/CONFORMAL_NARIAI_310_CAUSAL_TRANSFER_V1.json`](certificates/CONFORMAL_NARIAI_310_CAUSAL_TRANSFER_V1.json),
  [`reports/conformal-nariai-310-causal-transfer.md`](reports/conformal-nariai-310-causal-transfer.md)
- First genuinely transverse tangent: the exact Kantowski--Sachs variation
  `delta a=-(1/3)sinh(2t)`, `delta b=sinh(t)` solves all three linearized
  Einstein equations and is therefore linearized Bach-flat.  At
  `t=asinh(1)` its relative circle/sphere variations are `-4/3` and `2`, the
  Nariai Weyl-contraction map has rank four, and
  `delta(C_abcd C^abcd)=-32`.  It is transverse to the infinitesimal
  Diff--Weyl orbit and gives a normalized nonzero tractor-curvature drift,
  while the full rank-310 SDR variation remains fail-closed:
  [`certificates/NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1.json`](certificates/NARIAI_TRANSVERSE_LINEARIZED_EINSTEIN_WITNESS_V1.json),
  [`reports/nariai-transverse-linearized-einstein-witness.md`](reports/nariai-transverse-linearized-einstein-witness.md)
- Historical algebraic screen: before the action Hessian was available, the
  unique endpoint term `Q_unique` was found to be noncyclic when tested alone
  with the provisional coefficientwise Hom-bundle adjoint.  The action-derived
  result above supersedes its endpoint no-go interpretation: the old receipt
  remains useful only as a scoped diagnostic of that provisional adjoint
  convention:
  [`certificates/NARIAI_ALGEBRAIC_ENDPOINT_CURVATURE_REPAIR_OBSTRUCTION_V1.json`](certificates/NARIAI_ALGEBRAIC_ENDPOINT_CURVATURE_REPAIR_OBSTRUCTION_V1.json),
  [`reports/nariai-algebraic-endpoint-curvature-repair-obstruction.md`](reports/nariai-algebraic-endpoint-curvature-repair-obstruction.md)
- Strict portable consumer gate and accepted Berger adapter:
  [`schema/abstract-cyclic-causal-transfer-consumer-v1.schema.json`](schema/abstract-cyclic-causal-transfer-consumer-v1.schema.json),
  [`certificates/BERGER_ABSTRACT_CAUSAL_TRANSFER_CONSUMER.json`](certificates/BERGER_ABSTRACT_CAUSAL_TRANSFER_CONSUMER.json)
- Second non-cylinder consumer: doubled adjoint-tractor mixed detour on
  Minkowski with exact cyclic flavor shear and parent-to-BGG descent:
  [`certificates/MINKOWSKI_DOUBLED_ADJOINT_TRACTOR_MIXED_DETOUR.json`](certificates/MINKOWSKI_DOUBLED_ADJOINT_TRACTOR_MIXED_DETOUR.json),
  [`certificates/MINKOWSKI_DOUBLED_ADJOINT_TRACTOR_CAUSAL_TRANSFER_CONSUMER.json`](certificates/MINKOWSKI_DOUBLED_ADJOINT_TRACTOR_CAUSAL_TRANSFER_CONSUMER.json),
  [`reports/minkowski-doubled-adjoint-tractor-mixed-detour.md`](reports/minkowski-doubled-adjoint-tractor-mixed-detour.md)
- Cyclic causal D-Cartan V2 contraction through arity two:
  [`certificates/BERGER_CAUSAL_D_CARTAN_V2.json`](certificates/BERGER_CAUSAL_D_CARTAN_V2.json)
- Causal-hull and cyclic-Reynolds V2 proof:
  [`reports/berger-causal-D-Cartan-v2.md`](reports/berger-causal-D-Cartan-v2.md)
- Complete arbitrary-input four-dimensional causal D-Cartan contraction through arity three:
  [`certificates/BERGER_ARITY_THREE_D_CARTAN_FULL_4D.json`](certificates/BERGER_ARITY_THREE_D_CARTAN_FULL_4D.json)
- Exact source-closure, odd-Darboux C4 and causal-Reynolds proof:
  [`reports/berger-causal-D-Cartan-arity-three.md`](reports/berger-causal-D-Cartan-arity-three.md)
- Portable all-row 34-component minimal contraction:
  [`certificates/BERGER_MINIMAL_34_PORTABLE_CONTRACTION.json`](certificates/BERGER_MINIMAL_34_PORTABLE_CONTRACTION.json)
- Portable minimal-contraction report:
  [`reports/berger-minimal-34-portable-contraction.md`](reports/berger-minimal-34-portable-contraction.md)
- Berger 54-row nonminimal algebraic completion:
  [`certificates/BERGER_NONMINIMAL_ALGEBRAIC_COMPLETION.json`](certificates/BERGER_NONMINIMAL_ALGEBRAIC_COMPLETION.json)
- Nonminimal algebraic-completion report:
  [`reports/berger-nonminimal-algebraic-completion.md`](reports/berger-nonminimal-algebraic-completion.md)
- Complete gauge-fixed 54-row Berger unary export:
  [`certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json`](certificates/BERGER_GAUGE_FIXED_NONMINIMAL_COMPLETION.json)
- Gauge-fixed nonminimal-completion report:
  [`reports/berger-gauge-fixed-nonminimal-completion.md`](reports/berger-gauge-fixed-nonminimal-completion.md)
- Exact rational Berger reduced-mode q2/D fixture:
  [`certificates/BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK.json`](certificates/BERGER_RATIONAL_FIXTURE_Q2_D_BLOCK.json)
- Rational Berger reduced-mode q2/D report:
  [`reports/berger-rational-fixture-q2-d-block.md`](reports/berger-rational-fixture-q2-d-block.md)
- Nonzero-D-weight finite-mode closure no-go:
  [`certificates/BERGER_NONZERO_D_WEIGHT_FINITE_BLOCK_NO_GO.json`](certificates/BERGER_NONZERO_D_WEIGHT_FINITE_BLOCK_NO_GO.json)
- Nonzero-weight no-go report:
  [`reports/berger-nonzero-D-weight-finite-block-no-go.md`](reports/berger-nonzero-D-weight-finite-block-no-go.md)
- All-weight homogeneous arity-two D-Cartan contraction:
  [`certificates/BERGER_ALL_WEIGHT_ARITY_TWO_D_CARTAN.json`](certificates/BERGER_ALL_WEIGHT_ARITY_TWO_D_CARTAN.json)
- All-weight Cartan report:
  [`reports/berger-all-weight-arity-two-D-Cartan.md`](reports/berger-all-weight-arity-two-D-Cartan.md)
- Complete 54-row local helical D action:
  [`certificates/BERGER_54_ROW_LOCAL_D_ACTION.json`](certificates/BERGER_54_ROW_LOCAL_D_ACTION.json)
- Local D-action report:
  [`reports/berger-54-row-local-D-action.md`](reports/berger-54-row-local-D-action.md)
- Complete arbitrary-input 54-row support-local classical q2:
  [`certificates/BERGER_SUPPORT_LOCAL_Q2.json`](certificates/BERGER_SUPPORT_LOCAL_Q2.json)
- Content-addressed exact PBW q2 payload:
  [`certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json`](certificates/BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json)
- Support-local q2 report:
  [`reports/berger-support-local-q2.md`](reports/berger-support-local-q2.md)
- Full four-dimensional D-Cartan dependency gate:
  [`certificates/BERGER_FULL_4D_D_CARTAN_GATE.json`](certificates/BERGER_FULL_4D_D_CARTAN_GATE.json)
- D-Cartan gate report:
  [`reports/berger-full-4d-D-Cartan-gate.md`](reports/berger-full-4d-D-Cartan-gate.md)
- Unary D-Cartan microlocal obstruction:
  [`certificates/BERGER_UNARY_D_CARTAN_MICROLOCAL_OBSTRUCTION.json`](certificates/BERGER_UNARY_D_CARTAN_MICROLOCAL_OBSTRUCTION.json)
- Unary obstruction report:
  [`reports/berger-unary-D-Cartan-microlocal-obstruction.md`](reports/berger-unary-D-Cartan-microlocal-obstruction.md)
- Conditional causal D-Cartan transfer:
  [`certificates/BERGER_CAUSAL_D_CARTAN_TRANSFER.json`](certificates/BERGER_CAUSAL_D_CARTAN_TRANSFER.json)
- Causal transfer report:
  [`reports/berger-causal-D-Cartan-transfer.md`](reports/berger-causal-D-Cartan-transfer.md)
- Exact 54-to-26 causal-homotopy reduction:
  [`certificates/BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION.json`](certificates/BERGER_54_ROW_CAUSAL_HOMOTOPY_REDUCTION.json)
- Causal-reduction report:
  [`reports/berger-54-row-causal-homotopy-reduction.md`](reports/berger-54-row-causal-homotopy-reduction.md)

The only scientific verdicts are:

```text
D_GAUGE
D_CHARGED
SECTOR_DEPENDENT
NOT_HAMILTONIAN
```

An untested setting does not receive a fifth pseudo-verdict.  It has
`assessment_status = NOT_TESTED` or `OPEN` and `verdict = null`.

## Verification

From `physics/symplectic-reconstruction/` run:

```bash
python3 d_quotient_classical/verify_classical_status.py --guards
python3 symbolic/verify_compact_cylinder_d_charge_audit.py --check
python3 -m unittest bridge.taub_moment_map.tests.test_compact_d_charge
python3 symbolic/verify_conformal_d_global_alternatives.py --check-result
python3 d_quotient_classical/scalar_clock/conformal_scalar_clock.py --check --guards
python3 -m unittest d_quotient_classical.scalar_clock.tests.test_conformal_scalar_clock
python3 d_quotient_classical/composite_clock/neutral_conformal_clock.py --check --guards
python3 -m unittest d_quotient_classical.composite_clock.tests.test_neutral_conformal_clock
python3 d_quotient_classical/composite_clock/neutral_clock_bv_health.py --check --guards
python3 -m unittest d_quotient_classical.composite_clock.tests.test_neutral_clock_bv_health
python3 d_quotient_classical/scalar_clock/homogeneous_stealth_clock.py --check --guards
python3 -m unittest d_quotient_classical.scalar_clock.tests.test_homogeneous_stealth_clock
python3 d_quotient_classical/scalar_clock/inhomogeneous_stealth_clock.py --check --guards
python3 -m unittest d_quotient_classical.scalar_clock.tests.test_inhomogeneous_stealth_clock
python3 d_quotient_classical/backreacted_clock/positive_berger_clock.py --check --guards
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_positive_berger_clock
python3 d_quotient_classical/backreacted_clock/berger_clock_charge_seed.py --check --guards
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_clock_charge_seed
python3 d_quotient_classical/backreacted_clock/fixed_coupling_delta_charge.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_fixed_coupling_delta_charge_independent.py
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_fixed_coupling_delta_charge
python3 d_quotient_classical/backreacted_clock/berger_minimal_bv_clock_sdr.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_berger_minimal_bv_clock_sdr_independent.py
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_minimal_bv_clock_sdr
python3 d_quotient_classical/backreacted_clock/berger_retained_minimal_layout.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_berger_retained_minimal_layout_independent.py
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_minimal_layout
python3 d_quotient_classical/backreacted_clock/berger_retained_minimal_operator.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_berger_retained_minimal_operator_independent.py
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_minimal_operator
python3 d_quotient_classical/backreacted_clock/berger_linearized_bach_pbw.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_berger_retained_minimal_operator.py
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_linearized_bach_pbw
python3 d_quotient_classical/backreacted_clock/berger_causal_witness_preflight.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_berger_causal_witness_preflight.py
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_causal_witness_preflight
python3 d_quotient_classical/backreacted_clock/berger_nonminimal_algebraic_completion.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_berger_nonminimal_algebraic_completion.py
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_nonminimal_algebraic_completion
python3 d_quotient_classical/backreacted_clock/berger_gauge_fixed_nonminimal_completion.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_berger_gauge_fixed_nonminimal_completion.py
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_gauge_fixed_nonminimal_completion
python3 d_quotient_classical/backreacted_clock/berger_rational_fixture_q2_d_block.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_berger_rational_fixture_q2_d_block.py
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_rational_fixture_q2_d_block
python3 d_quotient_classical/backreacted_clock/berger_nonzero_weight_finite_block_no_go.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_berger_nonzero_weight_finite_block_no_go.py
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_nonzero_weight_finite_block_no_go
python3 d_quotient_classical/backreacted_clock/berger_all_weight_arity_two_d_cartan.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_berger_all_weight_arity_two_d_cartan.py
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_all_weight_arity_two_d_cartan
python3 d_quotient_classical/backreacted_clock/berger_54_row_local_d_action.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_berger_54_row_local_d_action.py
python3 -m pytest -q d_quotient_classical/backreacted_clock/tests/test_berger_54_row_local_d_action.py
python3 d_quotient_classical/backreacted_clock/berger_support_local_q2_export.py --check
python3 d_quotient_classical/backreacted_clock/verify_berger_support_local_q2_independent.py
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_support_local_q2
python3 d_quotient_classical/backreacted_clock/berger_54_row_causal_homotopy_reduction.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_berger_54_row_causal_homotopy_reduction.py
python3 -m pytest -q d_quotient_classical/backreacted_clock/tests/test_berger_54_row_causal_homotopy_reduction.py
python3 -m d_quotient_classical.backreacted_clock.berger_extended_rod_memory_maxwell_unary_gate --check
python3 -m d_quotient_classical.backreacted_clock.verify_berger_extended_rod_memory_maxwell_unary_gate
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_extended_rod_memory_maxwell_unary_gate -v
python3 -m d_quotient_classical.backreacted_clock.berger_rod_tadpole_compact_solvability_gate --check
python3 -m d_quotient_classical.backreacted_clock.verify_berger_rod_tadpole_compact_solvability_gate
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_rod_tadpole_compact_solvability_gate -v
```

The first command checks evidence hashes, dependency tags, exact setting and
complex inventories, verdict prerequisites, and mutation guards. It does not
rerun the mathematical producers. The remaining commands are the scoped
producer checks for the compact charge, alternative residual complexes, and
the one-real-scalar obstruction, neutral two-field replacement, its local
positive-health obstruction, the homogeneous positive-sign stealth
classification, and the complete standard one-field inhomogeneous stealth
no-go. The final pair certifies the exact positive-matter Berger-clock
background while keeping the covariant charge and all-row BV verdict open.
The charge-seed pair additionally proves that the phase carries nonzero
conserved internal momentum and derives
\(\Omega_{\rm total}(\delta,\mathcal L_D)=\omega\delta Q_R\). The fixed-coupling
audit then closes the decisive tangent gate.  The exact lapse equation is

\[
\delta E_N=-\frac{\alpha_Bq^{3/2}}2\frac{\delta Q_R}{Q_R},
\]

so every homogeneous allowed tangent has \(\delta Q_R=0\). Compact spatial
averaging proves the same for every smooth fixed-coupling linearized tangent.
Thus `D_GAUGE` holds on this declared Berger phase space.  The temporal/Weyl
clock doublets and all four minimal BV-dual rows now also admit an exact
first-order support-local cyclic contraction: 8 of the 34 minimal rows
contract, leaving a 26-row dressed-metric/spatial-diffeomorphism complex.
Its component IDs, degree ranks, duality, pairing conventions, support rules,
and three allowed (q_1) blocks are now frozen by one authoritative layout.
The retained operator is now complete. Its Bach block is expanded through all
orders in the exact invariant-frame PBW algebra on the nonzero-Weyl Berger
background; no round-cylinder lower-order term is reused. Exact composition
proves the spatial Noether identities, formal self-adjointness, cyclicity, and
the full 26-row relation (q_1^2=0). The immediate gate is now the separate
`BERGER_NONMINIMAL_COMPLETION`, followed by the causal Green contraction.
The arbitrary-input four-dimensional classical (q_2) is now complete on all
54 gauge-fixed rows.  It is derived from the common action and nonlinear gauge
action, contains every antifield and ghost-antifield mate, and satisfies the
arity-two (L_infinity) identity, Koszul symmetry, local-functional cyclicity,
and the local (D)-derivation identity exactly.  The separate nonlinear
(D)-Cartan contraction and retained causal Green theorem remain open.

The retained causal witness is fixed as `T=alpha_B Box_1 F_spatial`. Its ghost
and dual identity blocks factor exactly into two normally hyperbolic vector
operators. The retained metric block has rank eight and a two-dimensional
clock/constraint kernel, but that is no longer a principal obstruction.
Support-locally reattaching the certified temporal/Weyl clock doublets and
using the full diffeomorphism/Weyl companion gives the exact principal
identities

```text
J H_4 + K_1 T = (zeta^2)^2 I_10
T K_1           = (zeta^2)^2 I_5.
```

The first submitted curved witness is algebraically exact but uses an
untransported identity middle map in dressed coordinates.  An independent
comparison finds the resulting ten-row dressed principal rank to be eight;
that rejects only that submitted presentation.  Coherently transporting the
entire BV package resolves the mismatch.  In raw coordinates the corrected
ghost, metric, metric-antifield, and identity principal blocks are exactly
\(I_5,I_{10},I_{10},I_5\), while the clock diagonal remains algebraic and the
metric-to-clock term is triangular.  The immediate gate is now
`BERGER_RAW_ENDPOINT_RANK_ONE_WAVE_EXTENSION`: exhibit an exact
Green-hyperbolic factor or finite filtered extension for the complete
lower-order raw endpoint operator. Principal agreement alone still does not
promote the causal theorem.

### Unary-operator naming and audit boundary

The historical JSON key `q1_blocks` denotes the **classical unary BV
differential** \(\ell^{\rm cl}_1\). It is not the quantum loop correction
often written \(\hbar Q_1\). Cross-team adapters and the eventual authoritative
support-local export must expose it as `classical_unary_q1` (alias
`ell_1_cl`) while retaining the historical key only for certificate
compatibility.

The producing Berger calculation derives the Bach PBW coefficients from the
classical action and curved invariant-frame geometry. The independent
consumer deliberately starts from the frozen PBW coefficient table and
checks digests, adjoints, Noether compositions, cyclicity, and nilpotency. It
does **not** independently rederive the Bach expansion from the action. These
are two distinct audit layers and must not be conflated.

The portable 34-row certificate closes the combined minimal contraction
requested by downstream teams. The twenty nonminimal antighost--multiplier
rows are now also enumerated and contract pointwise and cyclically, giving an
exact unfixed 54-to-26 contraction and a coefficientwise curved companion.
The selected gauge fermion has now been applied as an exact finite-order
BV-canonical shear. The resulting complete 54-row gauge-fixed
`classical_unary_q1`, cyclic pairing, and transformed
`iota_cl`, `pi_cl`, and `S_cl` are portable. The decisive remaining handoff
requires `classical_binary_q2`, local `D_action_cl`, the general nonlinear
Koszul--Tate package, and causal/Hadamard data.

The rational Berger fixture now supplies the smallest action-derived input
that can exercise the arity-two ND2 machinery. Its six rows are the three
stationary homogeneous variations \(\delta u,\delta N,\delta\rho\), with
\(c=c_0(1+u)\), and their Euler--Lagrange rows. The Hessian and cubic Taylor
tensor are derived from the exact action normalized by the constant
background factor \(c_0\), so every exported coefficient is rational. The
cyclic pairing is canonical, and all declared
\(D\)-weights are zero. Exact checks prove \([q_1,D]=0\), the arity-two
\(q^2\) identity, cyclicity, and block closure. This is deliberately tagged
`REDUCED-MODE`: it is an ingestion and identity fixture, not the full
support-local \(q_2\) and not a nonzero-weight \(D\)-equivariance theorem.

The natural finite nonzero-weight extension is now ruled out exactly. The
action-derived square map \(Q(x)=q_2(x,x)\) has no nonzero zero over either
\(\mathbb R\) or \(\mathbb C\). A short real certificate is the
positive-definite combination \(-2Q_u-2Q_N+Q_\rho\); exact ideal-membership
identities certify the complex statement. Consequently cyclic
nondegeneracy and q2 closure force the unbounded weight sequence
\(w,-2w,4w,-8w,\ldots\). The smallest \((-1,0,+1)\) block first leaks at
\(E_{u,+2}\) with coefficient \(27/80\) and normalized dual witness
\((80/27,0,0)\). This is a finite-mode closure obstruction, not a Cartan
cohomology obstruction. The next honest target is the infinite all-weight
completion or the full support-local complex.

The infinite homogeneous weight lattice supplies the positive counterpart.
With all \(k\in\mathbb Z\) retained, q2 closes by convolution and the local
linear homotopy \(\iota_D^{(1)}E_k=kH^{-1}E_k\) produces a generically
nonzero arity-two Cartan source. The explicit first-order correction

\[
\iota_D^{(2)}(E_k,x_l)
=-\frac{2k+l}{3}H^{-1}C(H^{-1}E,x)_{k+l},
\]

together with its equation--equation component, kills that source exactly.
Coefficientwise checks prove graded symmetry, graded cyclicity, D derivation,
q-nilpotency, and the Cartan identity on every weight. This is the first
genuine nonzero-weight nonlinear result, but it remains spatially homogeneous
and `REDUCED-MODE`; the full four-dimensional and complete 54-row gates stay
open.

The helical (D)-action is no longer part of that open gate. In the dressed
stationary invariant frame it is exactly (e_0) on every one of the 54
field, ghost, antifield, and nonminimal rows. Coefficientwise PBW composition
proves ([q_1,D]=0), equivariance of (iota_{m cl},pi_{m cl},S_{m cl}),
formal skew-adjointness, and preservation of the cyclic pairing. The complete
four-dimensional support-local \(q_2\) is now exported on all 54 rows and its
local \(D\)-derivation identity is exact. A support-local unary Cartan
homotopy on the bare complex is now ruled out microlocally: at an exact null
covector where \(\sigma(D)=1\), the retained Douglis symbol complex has
cohomology dimensions \((0,6,6,0)\). The D-equivariant SDR transfers the
obstruction to all 54 bare rows. The extension routes are now separated. The
causal route is selected first: a (D)-equivariant retained homotopy gives
(iota^{(1)}_{D,\pm}=\Lambda_{26,\pm}D_{26}), and the resulting arity-two
source is automatically (q_1)-closed. The raw causal primitive is exact;
its cyclic completion remains a separate gate. Thus the immediate nonlinear
and analytic target is the retained 26-row Green homotopy, while residual/BFV
extension remains an alternative.

The minimal causal handoff now also freezes one authoritative
\((W_{34},P_{34},\operatorname{pairing}_{34})\) candidate, with
\(P_{34}=q_{34}W_{34}+W_{34}q_{34}\) and exact cyclicity. This supplies the
previously missing consumer input; it does not prove causal invertibility. A
failed downstream test rejects this candidate only and is not a global
nonexistence theorem for all curved witnesses.

That downstream test has now been run. It exposes a coordinate mismatch in
the first candidate, not a propagation obstruction. The replacement export
uses the certified first-order BV-canonical raw/dressed clock map and the
action-normalized raw fibre identification. Exact PBW replay proves raw
\(q^2=0\), cyclicity, \(P=qW+Wq\), all transport identities, and the full
scalar-biwave principal blocks. Advanced/retarded inversion of the complete
lower-order raw operator is still open and is the remaining analytic gate
before the retained 26-row causal homotopy can be promoted.

The exact \(10+2\) block preflight further shows that the clock diagonal is
\(I_2\). Naive clock elimination is not the answer: its Schur correction is
nonzero and raises the metric operator from order four to order six. The
order-six symbol is nevertheless rank one off characteristic and divisible
by the metric wave symbol, hence vanishes on the null stratum. That extension
is now explicit: \(C_R=-\Box_0F_2\), with
\(F_2=(\Box_0\operatorname{tr}-\operatorname{div}\operatorname{div})/6\).
Adding one scalar \(y=F_2h\) replaces the order-six Schur presentation by a
13-row support-local operator of maximum order four. Exact triangular maps
give \(E_{13}L_{13}U_{13}^{-1}=L_{12}\oplus I_1\). The remaining gate is
`BERGER_RAW_ENDPOINT_EXTENSION_GREEN_OPERATORS`, not a generic sixth-order
inversion.

The prolongation is also complete on the paired analytic presentation. The
authoritative BV complex remains \([5,12,12,5]\); the Green realization has
ranks \([5,13,13,5]\), adding only \(y\) and its pairing-dual \(y^*\).
Exact solution/source graph contractions, the formal-adjoint antifield block,
and the extended cyclic pairing are certified. The eventual Green operators
must obey \(G_{13,+}^\sharp=G_{13,-}\). Scalar zero modes are handled by
causal Cauchy evolution—no inverse Laplacian or spatial projector is allowed.

The full causal problem has also been reduced exactly. The same 54-to-26 SDR
proves that a retained causal homotopy lifts by

\[
\Lambda_{54,\pm}=S_{\rm cl}+\iota_{\rm cl}\Lambda_{26,\pm}\pi_{\rm cl}.
\]

Twenty-eight rows therefore contribute no independent analytic obstruction.
The total causal flag remains false because the retained 26-row mixed-order
metric endpoint still needs its advanced/retarded Green realization.

## Promotion rule

A setting may move to `CERTIFIED` only when its field space, allowed
variations, boundary/corner conditions, charge variation, integrability,
flux, conservation, and reference normalization are recorded.  A
`LORENTZIAN_BOUNDARY` or `COVARIANT_SMOOTH` verdict additionally requires the
`LORENTZIAN-CAUSAL` dependency tag.  Reduced-mode evidence remains explicitly
reduced-mode evidence.
