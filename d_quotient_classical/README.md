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
