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
Nonlinear (q_2), arity-two (D)-Cartan stability, and the combined classical
support-local export remain open.

The causal witness is now fixed as
`T=alpha_B Box_1 F_spatial`. Its ghost and dual identity blocks factor exactly
into two normally hyperbolic vector operators and are Green hyperbolic. The
metric block is the sole remaining analytic carrier: its fourth-order symbol
has rank eight and an exact two-dimensional polynomial clock/constraint
kernel. The immediate gate is `BERGER_METRIC_MIXED_ORDER_GREEN_REALIZATION`;
the total causal homotopy remains false until that block has sourced causal
propagation.

## Promotion rule

A setting may move to `CERTIFIED` only when its field space, allowed
variations, boundary/corner conditions, charge variation, integrability,
flux, conservation, and reference normalization are recorded.  A
`LORENTZIAN_BOUNDARY` or `COVARIANT_SMOOTH` verdict additionally requires the
`LORENTZIAN-CAUSAL` dependency tag.  Reduced-mode evidence remains explicitly
reduced-mode evidence.
