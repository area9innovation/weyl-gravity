# Refined-cube migration audit v2

**Result:** `FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2`

## Outcome

All **112** v1 migration-pending cells have explicit decisions. The audit records **88 reviewed no-transfer** decisions and **24 reviewed child gaps**. Pending after audit: **0**.

Coverage and migration are now different fields. A reviewed parent source that does not treat a child clears the migration question but leaves coverage `NOT_MAPPED`. This is not a literature-absence claim, and it does not create a gap.

## Workload decomposition

| Review class | Cells | Outcome |
|---|---:|---|
| Descendants of v0 direct results | 12 | Reviewed first; all are no-transfer under their recorded boundaries. |
| Descendants of v0 pieces-only cells | 76 | Reviewed in 18 repeated evidence batches; all are no-transfer to the listed unresolved children. |
| Evidence-free v0 parent gaps | 24 | Decomposed into explicit child priority gaps. |

## Evidence batches

| Batch | Cells | Evidence |
|---|---:|---|
| `TOPOS_CONTEXT_STATE_DYNAMICS` | 14 | heunen-landsman-spitters-2009, doring-2008, brenna-flori-2012, harding-heunen-2019 |
| `FINITE_QUANTUM_RECONSTRUCTION` | 8 | gibbons-hoffman-wootters-2004, abramsky-coecke-2004, constantin-doring-2020 |
| `CONSTRUCTIVE_TOPOS_DYNAMICS` | 7 | coquand-spitters-2009, heunen-landsman-spitters-2009, brenna-flori-2012 |
| `FINITE_CONTEXTUAL_TOPOS` | 7 | harding-heunen-2019, constantin-doring-2020, abramsky-coecke-2004 |
| `CONSTRUCTIVE_HILBERT_FOUNDATIONS` | 6 | neumann-pape-streicher-2018, pour-el-richards-1981, bridges-svozil-2000, richman-bridges-1999 |
| `EFFECTIVE_CATEGORICAL_QUANTUM` | 6 | neumann-pape-streicher-2018, abramsky-coecke-2004 |
| `PT_KREIN_QFT` | 6 | bender-boettcher-1998, mostafazadeh-2001, gottschalk-2004 |
| `ZF_KREIN_SPECTRAL_QFT` | 6 | FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1, mostafazadeh-2001, gottschalk-2004 |
| `ZF_OPERATOR_FOUNDATIONS` | 6 | blackadar-farah-karagila-2026, blackadar-farah-2026, neumann-pape-streicher-2018 |
| `LATTICE_DISCRETE_DYNAMICS` | 4 | kogut-susskind-1975, zohar-burrello-2014, bahr-dittrich-2009, dittrich-2012 |
| `SYNTHETIC_GEOMETRY_LOCAL_BRST` | 4 | grinkevich-1996, barnich-brandt-henneaux-2000 |
| `PT_PSEUDOHERMITIAN_SPECTRAL` | 3 | bender-boettcher-1998, mostafazadeh-2001 |
| `REVERSE_FUNCTIONAL_ANALYSIS` | 3 | brown-simpson-1986, humphreys-simpson-1999, humphreys-simpson-1996, brattka-2008 |
| `SYNTHETIC_GENERAL_RELATIVITY` | 3 | grinkevich-1996 |
| `ENERGY_SPECTRAL_FRAGMENT` | 2 | FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1 |
| `AQFT_BV_ARCHITECTURE` | 1 | barnich-brandt-henneaux-2000, brunetti-fredenhagen-verch-2001, fredenhagen-rejzner-2011, brunetti-fredenhagen-rejzner-2013 |
| `LOCALIC_EFFECTIVE_SPECTRAL` | 1 | coquand-spitters-2009, henry-2014, neumann-pape-streicher-2018 |
| `TOPOS_STATE_INTERNAL_DYNAMICS` | 1 | doring-2008, brenna-flori-2012, harding-heunen-2019 |

## Result-descendant reviews

| Coordinate | Parent status | Decision | Rationale |
|---|---|---|---|
| `CLASSICAL_STANDARD|HILBERT_OPERATOR|CAUSAL_PROPAGATION_GREEN` | `LOCAL_RESULT` | `REVIEWED_NO_TRANSFER` | The exact energy spectrum is a reduced-mode spectral result and explicitly does not establish causal support or a Green operator. No reviewed record in the batch constructs advanced/retarded maps with causal support. |
| `CLASSICAL_STANDARD|LOCALIC_SYNTHETIC|CAUSAL_PROPAGATION_GREEN` | `LITERATURE_RESULT` | `REVIEWED_NO_TRANSFER` | Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch constructs advanced/retarded maps with causal support. |
| `CLASSICAL_STANDARD|SMOOTH_DISTRIBUTIONAL|PROBABILITY_RULE` | `LITERATURE_RESULT` | `REVIEWED_NO_TRANSFER` | AQFT state-space and BV-renormalization architecture does not derive a normalized probability rule for the Weyl metric theory. No reviewed record in the batch derives the required normalized event-probability rule. |
| `CONSTRUCTIVE_COMPUTABLE|LOCALIC_SYNTHETIC|CAUSAL_PROPAGATION_GREEN` | `LITERATURE_RESULT` | `REVIEWED_NO_TRANSFER` | Constructive duality and internal one-parameter dynamics do not transfer to causal Green theory or interacting/renormalized field theory. No reviewed record in the batch constructs advanced/retarded maps with causal support. |
| `FINITE_DISCRETE|HILBERT_OPERATOR|CAUSAL_PROPAGATION_GREEN` | `LITERATURE_RESULT` | `REVIEWED_NO_TRANSFER` | Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations. No reviewed record in the batch constructs advanced/retarded maps with causal support. |
| `FINITE_DISCRETE|HILBERT_OPERATOR|EVOLUTION_WELLPOSEDNESS` | `LITERATURE_RESULT` | `REVIEWED_NO_TRANSFER` | Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations. No reviewed record in the batch proves existence, uniqueness, stability, or computability of the required evolution. |
| `FINITE_DISCRETE|LOCALIC_SYNTHETIC|CAUSAL_PROPAGATION_GREEN` | `LITERATURE_RESULT` | `REVIEWED_NO_TRANSFER` | Finite contextual and categorical structures do not establish causal propagation or the six quantum-consistency children. No reviewed record in the batch constructs advanced/retarded maps with causal support. |
| `TOPOS_INTERNAL|ALGEBRAIC_CSTAR|CAUSAL_PROPAGATION_GREEN` | `LITERATURE_RESULT` | `REVIEWED_NO_TRANSFER` | Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch constructs advanced/retarded maps with causal support. |
| `TOPOS_INTERNAL|SMOOTH_DISTRIBUTIONAL|CAUSAL_PROPAGATION_GREEN` | `LITERATURE_RESULT` | `REVIEWED_NO_TRANSFER` | The reviewed synthetic Einstein-equation formulation does not construct spectral generators, prove evolution well-posedness, or provide causal Green maps. No reviewed record in the batch constructs advanced/retarded maps with causal support. |
| `TOPOS_INTERNAL|SMOOTH_DISTRIBUTIONAL|EVOLUTION_WELLPOSEDNESS` | `LITERATURE_RESULT` | `REVIEWED_NO_TRANSFER` | The reviewed synthetic Einstein-equation formulation does not construct spectral generators, prove evolution well-posedness, or provide causal Green maps. No reviewed record in the batch proves existence, uniqueness, stability, or computability of the required evolution. |
| `TOPOS_INTERNAL|SMOOTH_DISTRIBUTIONAL|GENERATOR_SPECTRAL_DYNAMICS` | `LITERATURE_RESULT` | `REVIEWED_NO_TRANSFER` | The reviewed synthetic Einstein-equation formulation does not construct spectral generators, prove evolution well-posedness, or provide causal Green maps. No reviewed record in the batch constructs the required generator or spectral dynamics in this refined coordinate. |
| `WEAK_CHOICE_ZF|HILBERT_OPERATOR|CAUSAL_PROPAGATION_GREEN` | `LOCAL_RESULT` | `REVIEWED_NO_TRANSFER` | The exact energy spectrum is a reduced-mode spectral result and explicitly does not establish causal support or a Green operator. No reviewed record in the batch constructs advanced/retarded maps with causal support. |

## Reproduction

```text
python3 foundations/audit_intersection_migrations.py --check
python3 foundations/check_intersection_migration_audit.py
python3 foundations/verify_intersection_migration_audit.py
```

## Boundaries

- This does not establish literature completeness.
- This does not establish that a reviewed-no-transfer coordinate has no supporting literature.
- This does not establish that every Cartesian coordinate is coherent.
- This does not establish a weakest mathematical base.
- This does not establish a new physical result.
- This does not establish a new Lorentzian-causal result.
