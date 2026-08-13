window.THEORY_ASSEMBLY_DATA = {
  "schema_version": "foundational-theory-assembly-atlas-v1",
  "result_id": "FOUNDATIONAL_THEORY_ASSEMBLY_ATLAS_V1",
  "result_kind": "FAIL_CLOSED_THEORY_ASSEMBLY_AND_EMPIRICAL_LEDGER",
  "lifecycle": "VERIFIED_NAVIGATION_ARTIFACT",
  "title": "Candidate theory assemblies and missing interfaces",
  "created": "2026-08-12",
  "dependency_tags": [
    "LOCAL-ALGEBRAIC",
    "REDUCED-MODE",
    "LORENTZIAN-CAUSAL"
  ],
  "unit": "A prototype assembly is a deterministic coverage envelope over selected cells, not a composed theory.",
  "interface_vocabulary": [
    {
      "id": "IDENTICAL_OBJECT",
      "meaning": "Both cells have been shown to use the same mathematical object with the same scope."
    },
    {
      "id": "EXACT_TRANSLATION",
      "meaning": "A proved, reversible translation connects the objects used by the two cells."
    },
    {
      "id": "CONDITIONAL_BRIDGE",
      "meaning": "A proved bridge exists once explicitly named extra assumptions are supplied."
    },
    {
      "id": "APPROXIMATION_WITH_BOUND",
      "meaning": "A quantitative approximation theorem connects the cells with an explicit error bound."
    },
    {
      "id": "CONJECTURAL_INTERFACE",
      "meaning": "A concrete bridge has been proposed but is not certified."
    },
    {
      "id": "INCOMPATIBLE",
      "meaning": "A scoped obstruction proves that these particular objects cannot be joined as proposed."
    },
    {
      "id": "NOT_ASSESSED",
      "meaning": "No registered record currently decides how the two selected cells compose."
    }
  ],
  "certified_interface_records": [
    {
      "id": "STATE_TO_PROBABILITY",
      "label": "Finite detector-corner state representation to conditional Krein Born rule",
      "status": "CERTIFIED",
      "relation": "CONDITIONAL_BRIDGE",
      "source_coordinates": [
        {
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "obligation": "STATE_REPRESENTATION"
        }
      ],
      "target_coordinates": [
        {
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "obligation": "PROBABILITY_RULE"
        }
      ],
      "carrier_transition": "ALGEBRAIC_CSTAR_TO_KREIN_INDEFINITE_VIA_SHARED_FINITE_COMPANION_CORNER",
      "scope": "Finite-trace detector corners and finite exhaustive output partitions satisfying the five displayed hypotheses.",
      "evidence": [
        "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1"
      ]
    },
    {
      "id": "SELECTION_TO_DYNAMICS",
      "label": "Free energy ground-state selection to invariant Krein--Fock dynamics",
      "status": "CERTIFIED",
      "relation": "CONDITIONAL_BRIDGE",
      "source_coordinates": [
        {
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "obligation": "PHYSICAL_STATE_SELECTION"
        }
      ],
      "target_coordinates": [
        {
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "obligation": "GENERATOR_SPECTRAL_DYNAMICS"
        }
      ],
      "carrier_transition": "IDENTICAL_FREE_KREIN_FOCK_CARRIER",
      "scope": "The explicit free reduced-mode bosonic Fock carrier, its diagonal total-occupation energy, and normal zero-energy states.",
      "evidence": [
        "FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1"
      ]
    }
  ],
  "assemblies": [
    {
      "id": "STANDARD_MIXED_REFERENCE",
      "label": "Classical-standard mixed-carrier reference",
      "aim": "Ask how far mainstream mathematics reaches when every registered carrier is available.",
      "foundations": [
        "CLASSICAL_STANDARD"
      ],
      "carriers": [
        "FINITE_EXACT",
        "HILBERT_OPERATOR",
        "KREIN_INDEFINITE",
        "ALGEBRAIC_CSTAR",
        "SMOOTH_DISTRIBUTIONAL",
        "LOCALIC_SYNTHETIC"
      ],
      "kind": "NAVIGATIONAL_PROTOTYPE",
      "selection_rule": "DETERMINISTIC_COVERAGE_ENVELOPE",
      "selected_cells": [
        {
          "obligation": "KINEMATICS_OBSERVABLES",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "STATE_EXISTENCE",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
            "bateman-turok-2026"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1": "DIRECT_LOCAL",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1": "DIRECT_LOCAL",
            "bateman-turok-2026": "DIRECT_LITERATURE"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "STATE_REPRESENTATION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1",
            "haag-kastler-1964",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
            "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1": "DIRECT_LOCAL",
            "haag-kastler-1964": "SUPPORTING",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1": "SUPPORTING",
            "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "PROBABILITY_RULE",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "status": "LOCAL_RESULT",
          "evidence": [
            "bateman-turok-2026",
            "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
            "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1"
          ],
          "evidence_roles": {
            "bateman-turok-2026": "SUPPORTING",
            "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1": "SUPPORTING",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1": "SUPPORTING",
            "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "PHYSICAL_STATE_SELECTION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
            "bateman-turok-2026",
            "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
            "FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1": "DIRECT_LOCAL",
            "bateman-turok-2026": "SUPPORTING",
            "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1": "SUPPORTING",
            "FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1",
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1",
            "FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1": "DIRECT_LOCAL",
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1": "DIRECT_LOCAL",
            "FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "EVOLUTION_WELLPOSEDNESS",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1",
            "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1": "DIRECT_LOCAL",
            "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "CAUSAL_PROPAGATION_GREEN",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1",
            "baer-2015",
            "muehlhoff-2010"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1": "DIRECT_LOCAL",
            "baer-2015": "UNREVIEWED",
            "muehlhoff-2010": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "GAUGE_BV_COHOMOLOGY",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "INTERACTION_CONSTRUCTION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "COUNTERTERM_CLASSIFICATION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "ANOMALY_CLASSIFICATION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RENORMALIZED_PRODUCTS",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "fredenhagen-rejzner-2011"
          ],
          "evidence_roles": {
            "fredenhagen-rejzner-2011": "DIRECT_LITERATURE"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "QME_RESTORATION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RESIDUAL_QUANTUM_TRANSFER",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RECONSTRUCTION_LIMITS",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "barnich-brandt-henneaux-2000",
            "brunetti-fredenhagen-verch-2001",
            "fredenhagen-rejzner-2011",
            "brunetti-fredenhagen-rejzner-2013"
          ],
          "evidence_roles": {
            "barnich-brandt-henneaux-2000": "UNREVIEWED",
            "brunetti-fredenhagen-verch-2001": "UNREVIEWED",
            "fredenhagen-rejzner-2011": "UNREVIEWED",
            "brunetti-fredenhagen-rejzner-2013": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        }
      ],
      "coverage": {
        "direct": 14,
        "assessed": 16,
        "total": 16,
        "complete_direct": false
      },
      "interfaces": [
        {
          "id": "STATE_TO_PROBABILITY",
          "label": "State encoding → probability rule",
          "source_obligations": [
            "STATE_REPRESENTATION"
          ],
          "target_obligations": [
            "PROBABILITY_RULE"
          ],
          "relation": "CONDITIONAL_BRIDGE",
          "certification_status": "CERTIFIED",
          "evidence": [
            "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1"
          ],
          "rationale": "Finite-trace detector corners and finite exhaustive output partitions satisfying the five displayed hypotheses."
        },
        {
          "id": "SELECTION_TO_DYNAMICS",
          "label": "Physical state selection → dynamics",
          "source_obligations": [
            "PHYSICAL_STATE_SELECTION"
          ],
          "target_obligations": [
            "GENERATOR_SPECTRAL_DYNAMICS"
          ],
          "relation": "CONDITIONAL_BRIDGE",
          "certification_status": "CERTIFIED",
          "evidence": [
            "FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1"
          ],
          "rationale": "The explicit free reduced-mode bosonic Fock carrier, its diagonal total-occupation energy, and normal zero-energy states."
        },
        {
          "id": "DYNAMICS_TO_CAUSALITY",
          "label": "Evolution → causal response",
          "source_obligations": [
            "GENERATOR_SPECTRAL_DYNAMICS",
            "EVOLUTION_WELLPOSEDNESS"
          ],
          "target_obligations": [
            "CAUSAL_PROPAGATION_GREEN"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "GAUGE_TO_INTERACTION",
          "label": "Gauge content → interaction",
          "source_obligations": [
            "KINEMATICS_OBSERVABLES",
            "GAUGE_BV_COHOMOLOGY"
          ],
          "target_obligations": [
            "INTERACTION_CONSTRUCTION"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "RENORMALIZATION_TO_QME",
          "label": "Classifications and products → restored QME",
          "source_obligations": [
            "COUNTERTERM_CLASSIFICATION",
            "ANOMALY_CLASSIFICATION",
            "RENORMALIZED_PRODUCTS"
          ],
          "target_obligations": [
            "QME_RESTORATION"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "QME_TO_RESIDUAL",
          "label": "Restored QME → residual correction",
          "source_obligations": [
            "QME_RESTORATION"
          ],
          "target_obligations": [
            "RESIDUAL_QUANTUM_TRANSFER"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "PREDICTION_TO_RECONSTRUCTION",
          "label": "Prediction chain → standard or operational interpretation",
          "source_obligations": [
            "PROBABILITY_RULE",
            "CAUSAL_PROPAGATION_GREEN",
            "INTERACTION_CONSTRUCTION"
          ],
          "target_obligations": [
            "RECONSTRUCTION_LIMITS"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        }
      ],
      "hard_gates": [
        {
          "id": "OBLIGATION_COVERAGE",
          "label": "Obligation coverage",
          "status": "OPEN",
          "basis": "14/16 obligations have a direct recorded result."
        },
        {
          "id": "CROSS_CELL_COMPOSITION",
          "label": "Cross-cell composition",
          "status": "BLOCKED",
          "basis": "2/7 required interfaces are certified; the remainder block assembly composition."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "label": "Prediction derivation",
          "status": "BLOCKED",
          "basis": "No registered end-to-end derivation connects the selected cells."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "label": "Observable identification",
          "status": "BLOCKED",
          "basis": "No assembly-level map from formal quantities to measured observables is registered."
        },
        {
          "id": "EMPIRICAL_COMPARISON",
          "label": "Empirical comparison",
          "status": "NO_RECORDS",
          "basis": "The empirical ledger contains no comparison for this assembly."
        },
        {
          "id": "ROBUSTNESS_OUT_OF_SAMPLE",
          "label": "Robustness / out-of-sample",
          "status": "NO_RECORDS",
          "basis": "No robustness or held-out prediction record is registered."
        }
      ],
      "complete_theory": false,
      "empirically_supported": false
    },
    {
      "id": "STANDARD_ALGEBRAIC_PROFILE",
      "label": "Classical-standard algebraic profile",
      "aim": "Use the present algebraic/C* profile as a single-carrier reference case.",
      "foundations": [
        "CLASSICAL_STANDARD"
      ],
      "carriers": [
        "ALGEBRAIC_CSTAR"
      ],
      "kind": "NAVIGATIONAL_PROTOTYPE",
      "selection_rule": "DETERMINISTIC_COVERAGE_ENVELOPE",
      "selected_cells": [
        {
          "obligation": "KINEMATICS_OBSERVABLES",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "haag-kastler-1964"
          ],
          "evidence_roles": {
            "haag-kastler-1964": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "STATE_EXISTENCE",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
            "haag-kastler-1964"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1": "DIRECT_LOCAL",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1": "DIRECT_LOCAL",
            "haag-kastler-1964": "DIRECT_LITERATURE"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "STATE_REPRESENTATION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1",
            "haag-kastler-1964",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
            "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1": "DIRECT_LOCAL",
            "haag-kastler-1964": "SUPPORTING",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1": "SUPPORTING",
            "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "PROBABILITY_RULE",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "PIECES_ONLY",
          "evidence": [
            "haag-kastler-1964",
            "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1"
          ],
          "evidence_roles": {
            "haag-kastler-1964": "SUPPORTING",
            "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1": "SUPPORTING",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "PHYSICAL_STATE_SELECTION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
            "haag-kastler-1964",
            "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1": "DIRECT_LOCAL",
            "haag-kastler-1964": "SUPPORTING",
            "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "EVOLUTION_WELLPOSEDNESS",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "CAUSAL_PROPAGATION_GREEN",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "GAUGE_BV_COHOMOLOGY",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "brunetti-fredenhagen-verch-2001",
            "fewster-verch-2011",
            "fredenhagen-rejzner-2011"
          ],
          "evidence_roles": {
            "brunetti-fredenhagen-verch-2001": "UNREVIEWED",
            "fewster-verch-2011": "UNREVIEWED",
            "fredenhagen-rejzner-2011": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "INTERACTION_CONSTRUCTION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "fredenhagen-rejzner-2011",
            "brunetti-fredenhagen-verch-2001"
          ],
          "evidence_roles": {
            "fredenhagen-rejzner-2011": "DIRECT_LITERATURE",
            "brunetti-fredenhagen-verch-2001": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "COUNTERTERM_CLASSIFICATION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "fredenhagen-rejzner-2011"
          ],
          "evidence_roles": {
            "fredenhagen-rejzner-2011": "DIRECT_LITERATURE"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "ANOMALY_CLASSIFICATION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "fredenhagen-rejzner-2011"
          ],
          "evidence_roles": {
            "fredenhagen-rejzner-2011": "DIRECT_LITERATURE"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RENORMALIZED_PRODUCTS",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "fredenhagen-rejzner-2011"
          ],
          "evidence_roles": {
            "fredenhagen-rejzner-2011": "DIRECT_LITERATURE"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "QME_RESTORATION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "PIECES_ONLY",
          "evidence": [
            "fredenhagen-rejzner-2011"
          ],
          "evidence_roles": {
            "fredenhagen-rejzner-2011": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RESIDUAL_QUANTUM_TRANSFER",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "PIECES_ONLY",
          "evidence": [
            "fredenhagen-rejzner-2011"
          ],
          "evidence_roles": {
            "fredenhagen-rejzner-2011": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RECONSTRUCTION_LIMITS",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "brunetti-fredenhagen-verch-2001",
            "fewster-verch-2011",
            "fredenhagen-rejzner-2011"
          ],
          "evidence_roles": {
            "brunetti-fredenhagen-verch-2001": "UNREVIEWED",
            "fewster-verch-2011": "UNREVIEWED",
            "fredenhagen-rejzner-2011": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        }
      ],
      "coverage": {
        "direct": 12,
        "assessed": 16,
        "total": 16,
        "complete_direct": false
      },
      "interfaces": [
        {
          "id": "STATE_TO_PROBABILITY",
          "label": "State encoding → probability rule",
          "source_obligations": [
            "STATE_REPRESENTATION"
          ],
          "target_obligations": [
            "PROBABILITY_RULE"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "SELECTION_TO_DYNAMICS",
          "label": "Physical state selection → dynamics",
          "source_obligations": [
            "PHYSICAL_STATE_SELECTION"
          ],
          "target_obligations": [
            "GENERATOR_SPECTRAL_DYNAMICS"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "DYNAMICS_TO_CAUSALITY",
          "label": "Evolution → causal response",
          "source_obligations": [
            "GENERATOR_SPECTRAL_DYNAMICS",
            "EVOLUTION_WELLPOSEDNESS"
          ],
          "target_obligations": [
            "CAUSAL_PROPAGATION_GREEN"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "GAUGE_TO_INTERACTION",
          "label": "Gauge content → interaction",
          "source_obligations": [
            "KINEMATICS_OBSERVABLES",
            "GAUGE_BV_COHOMOLOGY"
          ],
          "target_obligations": [
            "INTERACTION_CONSTRUCTION"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "RENORMALIZATION_TO_QME",
          "label": "Classifications and products → restored QME",
          "source_obligations": [
            "COUNTERTERM_CLASSIFICATION",
            "ANOMALY_CLASSIFICATION",
            "RENORMALIZED_PRODUCTS"
          ],
          "target_obligations": [
            "QME_RESTORATION"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "QME_TO_RESIDUAL",
          "label": "Restored QME → residual correction",
          "source_obligations": [
            "QME_RESTORATION"
          ],
          "target_obligations": [
            "RESIDUAL_QUANTUM_TRANSFER"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "PREDICTION_TO_RECONSTRUCTION",
          "label": "Prediction chain → standard or operational interpretation",
          "source_obligations": [
            "PROBABILITY_RULE",
            "CAUSAL_PROPAGATION_GREEN",
            "INTERACTION_CONSTRUCTION"
          ],
          "target_obligations": [
            "RECONSTRUCTION_LIMITS"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        }
      ],
      "hard_gates": [
        {
          "id": "OBLIGATION_COVERAGE",
          "label": "Obligation coverage",
          "status": "OPEN",
          "basis": "12/16 obligations have a direct recorded result."
        },
        {
          "id": "CROSS_CELL_COMPOSITION",
          "label": "Cross-cell composition",
          "status": "BLOCKED",
          "basis": "0/7 required interfaces are certified; the remainder block assembly composition."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "label": "Prediction derivation",
          "status": "BLOCKED",
          "basis": "No registered end-to-end derivation connects the selected cells."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "label": "Observable identification",
          "status": "BLOCKED",
          "basis": "No assembly-level map from formal quantities to measured observables is registered."
        },
        {
          "id": "EMPIRICAL_COMPARISON",
          "label": "Empirical comparison",
          "status": "NO_RECORDS",
          "basis": "The empirical ledger contains no comparison for this assembly."
        },
        {
          "id": "ROBUSTNESS_OUT_OF_SAMPLE",
          "label": "Robustness / out-of-sample",
          "status": "NO_RECORDS",
          "basis": "No robustness or held-out prediction record is registered."
        }
      ],
      "complete_theory": false,
      "empirically_supported": false
    },
    {
      "id": "FINITE_EXACT_PROGRAMME",
      "label": "Finite exact programme",
      "aim": "Test how much of the physics chain survives in finite, exactly checkable data.",
      "foundations": [
        "FINITE_DISCRETE"
      ],
      "carriers": [
        "FINITE_EXACT"
      ],
      "kind": "NAVIGATIONAL_PROTOTYPE",
      "selection_rule": "DETERMINISTIC_COVERAGE_ENVELOPE",
      "selected_cells": [
        {
          "obligation": "KINEMATICS_OBSERVABLES",
          "foundation": "FINITE_DISCRETE",
          "carrier": "FINITE_EXACT",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "gibbons-hoffman-wootters-2004"
          ],
          "evidence_roles": {
            "gibbons-hoffman-wootters-2004": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "STATE_EXISTENCE",
          "foundation": "FINITE_DISCRETE",
          "carrier": "FINITE_EXACT",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "gibbons-hoffman-wootters-2004"
          ],
          "evidence_roles": {
            "gibbons-hoffman-wootters-2004": "DIRECT_LITERATURE"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "STATE_REPRESENTATION",
          "foundation": "FINITE_DISCRETE",
          "carrier": "FINITE_EXACT",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "gibbons-hoffman-wootters-2004"
          ],
          "evidence_roles": {
            "gibbons-hoffman-wootters-2004": "DIRECT_LITERATURE"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "PROBABILITY_RULE",
          "foundation": "FINITE_DISCRETE",
          "carrier": "FINITE_EXACT",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "gibbons-hoffman-wootters-2004"
          ],
          "evidence_roles": {
            "gibbons-hoffman-wootters-2004": "DIRECT_LITERATURE"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "PHYSICAL_STATE_SELECTION",
          "foundation": "FINITE_DISCRETE",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "gibbons-hoffman-wootters-2004"
          ],
          "evidence_roles": {
            "gibbons-hoffman-wootters-2004": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
          "foundation": "FINITE_DISCRETE",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "EVOLUTION_WELLPOSEDNESS",
          "foundation": "FINITE_DISCRETE",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "CAUSAL_PROPAGATION_GREEN",
          "foundation": "FINITE_DISCRETE",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1",
            "FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1": "SUPPORTING",
            "FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "GAUGE_BV_COHOMOLOGY",
          "foundation": "FINITE_DISCRETE",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "INTERACTION_CONSTRUCTION",
          "foundation": "FINITE_DISCRETE",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "COUNTERTERM_CLASSIFICATION",
          "foundation": "FINITE_DISCRETE",
          "carrier": "FINITE_EXACT",
          "status": "PRIORITY_GAP",
          "evidence": [],
          "evidence_roles": {},
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "ANOMALY_CLASSIFICATION",
          "foundation": "FINITE_DISCRETE",
          "carrier": "FINITE_EXACT",
          "status": "PRIORITY_GAP",
          "evidence": [],
          "evidence_roles": {},
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RENORMALIZED_PRODUCTS",
          "foundation": "FINITE_DISCRETE",
          "carrier": "FINITE_EXACT",
          "status": "PRIORITY_GAP",
          "evidence": [],
          "evidence_roles": {},
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "QME_RESTORATION",
          "foundation": "FINITE_DISCRETE",
          "carrier": "FINITE_EXACT",
          "status": "PRIORITY_GAP",
          "evidence": [],
          "evidence_roles": {},
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RESIDUAL_QUANTUM_TRANSFER",
          "foundation": "FINITE_DISCRETE",
          "carrier": "FINITE_EXACT",
          "status": "PRIORITY_GAP",
          "evidence": [],
          "evidence_roles": {},
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RECONSTRUCTION_LIMITS",
          "foundation": "FINITE_DISCRETE",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        }
      ],
      "coverage": {
        "direct": 10,
        "assessed": 16,
        "total": 16,
        "complete_direct": false
      },
      "interfaces": [
        {
          "id": "STATE_TO_PROBABILITY",
          "label": "State encoding → probability rule",
          "source_obligations": [
            "STATE_REPRESENTATION"
          ],
          "target_obligations": [
            "PROBABILITY_RULE"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "SELECTION_TO_DYNAMICS",
          "label": "Physical state selection → dynamics",
          "source_obligations": [
            "PHYSICAL_STATE_SELECTION"
          ],
          "target_obligations": [
            "GENERATOR_SPECTRAL_DYNAMICS"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "DYNAMICS_TO_CAUSALITY",
          "label": "Evolution → causal response",
          "source_obligations": [
            "GENERATOR_SPECTRAL_DYNAMICS",
            "EVOLUTION_WELLPOSEDNESS"
          ],
          "target_obligations": [
            "CAUSAL_PROPAGATION_GREEN"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "GAUGE_TO_INTERACTION",
          "label": "Gauge content → interaction",
          "source_obligations": [
            "KINEMATICS_OBSERVABLES",
            "GAUGE_BV_COHOMOLOGY"
          ],
          "target_obligations": [
            "INTERACTION_CONSTRUCTION"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "RENORMALIZATION_TO_QME",
          "label": "Classifications and products → restored QME",
          "source_obligations": [
            "COUNTERTERM_CLASSIFICATION",
            "ANOMALY_CLASSIFICATION",
            "RENORMALIZED_PRODUCTS"
          ],
          "target_obligations": [
            "QME_RESTORATION"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "QME_TO_RESIDUAL",
          "label": "Restored QME → residual correction",
          "source_obligations": [
            "QME_RESTORATION"
          ],
          "target_obligations": [
            "RESIDUAL_QUANTUM_TRANSFER"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "PREDICTION_TO_RECONSTRUCTION",
          "label": "Prediction chain → standard or operational interpretation",
          "source_obligations": [
            "PROBABILITY_RULE",
            "CAUSAL_PROPAGATION_GREEN",
            "INTERACTION_CONSTRUCTION"
          ],
          "target_obligations": [
            "RECONSTRUCTION_LIMITS"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        }
      ],
      "hard_gates": [
        {
          "id": "OBLIGATION_COVERAGE",
          "label": "Obligation coverage",
          "status": "OPEN",
          "basis": "10/16 obligations have a direct recorded result."
        },
        {
          "id": "CROSS_CELL_COMPOSITION",
          "label": "Cross-cell composition",
          "status": "BLOCKED",
          "basis": "0/7 required interfaces are certified; the remainder block assembly composition."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "label": "Prediction derivation",
          "status": "BLOCKED",
          "basis": "No registered end-to-end derivation connects the selected cells."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "label": "Observable identification",
          "status": "BLOCKED",
          "basis": "No assembly-level map from formal quantities to measured observables is registered."
        },
        {
          "id": "EMPIRICAL_COMPARISON",
          "label": "Empirical comparison",
          "status": "NO_RECORDS",
          "basis": "The empirical ledger contains no comparison for this assembly."
        },
        {
          "id": "ROBUSTNESS_OUT_OF_SAMPLE",
          "label": "Robustness / out-of-sample",
          "status": "NO_RECORDS",
          "basis": "No robustness or held-out prediction record is registered."
        }
      ],
      "complete_theory": false,
      "empirically_supported": false
    },
    {
      "id": "WEAK_BASE_FINITE_EXACT",
      "label": "Weak-base finite-exact programme",
      "aim": "Expose the arithmetic or Choice strength of finite exact constructions without identifying distinct weak bases.",
      "foundations": [
        "WEAK_ARITHMETIC",
        "WEAK_CHOICE_ZF"
      ],
      "carriers": [
        "FINITE_EXACT"
      ],
      "kind": "NAVIGATIONAL_PROTOTYPE",
      "selection_rule": "DETERMINISTIC_COVERAGE_ENVELOPE",
      "selected_cells": [
        {
          "obligation": "KINEMATICS_OBSERVABLES",
          "foundation": "WEAK_CHOICE_ZF",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "UNREVIEWED",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "STATE_EXISTENCE",
          "foundation": "WEAK_ARITHMETIC",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "STATE_REPRESENTATION",
          "foundation": "WEAK_ARITHMETIC",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "PROBABILITY_RULE",
          "foundation": "WEAK_ARITHMETIC",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "PHYSICAL_STATE_SELECTION",
          "foundation": "WEAK_ARITHMETIC",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
          "foundation": "WEAK_ARITHMETIC",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "EVOLUTION_WELLPOSEDNESS",
          "foundation": "WEAK_ARITHMETIC",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "CAUSAL_PROPAGATION_GREEN",
          "foundation": "WEAK_ARITHMETIC",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "GAUGE_BV_COHOMOLOGY",
          "foundation": "WEAK_ARITHMETIC",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "INTERACTION_CONSTRUCTION",
          "foundation": "WEAK_ARITHMETIC",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "COUNTERTERM_CLASSIFICATION",
          "foundation": "WEAK_CHOICE_ZF",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "ANOMALY_CLASSIFICATION",
          "foundation": "WEAK_CHOICE_ZF",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RENORMALIZED_PRODUCTS",
          "foundation": "WEAK_ARITHMETIC",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "QME_RESTORATION",
          "foundation": "WEAK_CHOICE_ZF",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RESIDUAL_QUANTUM_TRANSFER",
          "foundation": "WEAK_CHOICE_ZF",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RECONSTRUCTION_LIMITS",
          "foundation": "WEAK_ARITHMETIC",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        }
      ],
      "coverage": {
        "direct": 9,
        "assessed": 16,
        "total": 16,
        "complete_direct": false
      },
      "interfaces": [
        {
          "id": "STATE_TO_PROBABILITY",
          "label": "State encoding → probability rule",
          "source_obligations": [
            "STATE_REPRESENTATION"
          ],
          "target_obligations": [
            "PROBABILITY_RULE"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "SELECTION_TO_DYNAMICS",
          "label": "Physical state selection → dynamics",
          "source_obligations": [
            "PHYSICAL_STATE_SELECTION"
          ],
          "target_obligations": [
            "GENERATOR_SPECTRAL_DYNAMICS"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "DYNAMICS_TO_CAUSALITY",
          "label": "Evolution → causal response",
          "source_obligations": [
            "GENERATOR_SPECTRAL_DYNAMICS",
            "EVOLUTION_WELLPOSEDNESS"
          ],
          "target_obligations": [
            "CAUSAL_PROPAGATION_GREEN"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "GAUGE_TO_INTERACTION",
          "label": "Gauge content → interaction",
          "source_obligations": [
            "KINEMATICS_OBSERVABLES",
            "GAUGE_BV_COHOMOLOGY"
          ],
          "target_obligations": [
            "INTERACTION_CONSTRUCTION"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "RENORMALIZATION_TO_QME",
          "label": "Classifications and products → restored QME",
          "source_obligations": [
            "COUNTERTERM_CLASSIFICATION",
            "ANOMALY_CLASSIFICATION",
            "RENORMALIZED_PRODUCTS"
          ],
          "target_obligations": [
            "QME_RESTORATION"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "QME_TO_RESIDUAL",
          "label": "Restored QME → residual correction",
          "source_obligations": [
            "QME_RESTORATION"
          ],
          "target_obligations": [
            "RESIDUAL_QUANTUM_TRANSFER"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "PREDICTION_TO_RECONSTRUCTION",
          "label": "Prediction chain → standard or operational interpretation",
          "source_obligations": [
            "PROBABILITY_RULE",
            "CAUSAL_PROPAGATION_GREEN",
            "INTERACTION_CONSTRUCTION"
          ],
          "target_obligations": [
            "RECONSTRUCTION_LIMITS"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        }
      ],
      "hard_gates": [
        {
          "id": "OBLIGATION_COVERAGE",
          "label": "Obligation coverage",
          "status": "OPEN",
          "basis": "9/16 obligations have a direct recorded result."
        },
        {
          "id": "CROSS_CELL_COMPOSITION",
          "label": "Cross-cell composition",
          "status": "BLOCKED",
          "basis": "0/7 required interfaces are certified; the remainder block assembly composition."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "label": "Prediction derivation",
          "status": "BLOCKED",
          "basis": "No registered end-to-end derivation connects the selected cells."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "label": "Observable identification",
          "status": "BLOCKED",
          "basis": "No assembly-level map from formal quantities to measured observables is registered."
        },
        {
          "id": "EMPIRICAL_COMPARISON",
          "label": "Empirical comparison",
          "status": "NO_RECORDS",
          "basis": "The empirical ledger contains no comparison for this assembly."
        },
        {
          "id": "ROBUSTNESS_OUT_OF_SAMPLE",
          "label": "Robustness / out-of-sample",
          "status": "NO_RECORDS",
          "basis": "No robustness or held-out prediction record is registered."
        }
      ],
      "complete_theory": false,
      "empirically_supported": false
    },
    {
      "id": "KREIN_ALGEBRAIC_PROGRAMME",
      "label": "Krein and algebraic programme",
      "aim": "Explore indefinite state spaces together with algebraic state and observable constructions.",
      "foundations": [
        "CLASSICAL_STANDARD",
        "WEAK_CHOICE_ZF"
      ],
      "carriers": [
        "KREIN_INDEFINITE",
        "ALGEBRAIC_CSTAR"
      ],
      "kind": "NAVIGATIONAL_PROTOTYPE",
      "selection_rule": "DETERMINISTIC_COVERAGE_ENVELOPE",
      "selected_cells": [
        {
          "obligation": "KINEMATICS_OBSERVABLES",
          "foundation": "WEAK_CHOICE_ZF",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "blackadar-farah-2026",
            "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1"
          ],
          "evidence_roles": {
            "blackadar-farah-2026": "UNREVIEWED",
            "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "STATE_EXISTENCE",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
            "bateman-turok-2026"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1": "DIRECT_LOCAL",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1": "DIRECT_LOCAL",
            "bateman-turok-2026": "DIRECT_LITERATURE"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "STATE_REPRESENTATION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1",
            "haag-kastler-1964",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
            "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1": "DIRECT_LOCAL",
            "haag-kastler-1964": "SUPPORTING",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1": "SUPPORTING",
            "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "PROBABILITY_RULE",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "status": "LOCAL_RESULT",
          "evidence": [
            "bateman-turok-2026",
            "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
            "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1"
          ],
          "evidence_roles": {
            "bateman-turok-2026": "SUPPORTING",
            "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1": "SUPPORTING",
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1": "SUPPORTING",
            "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "PHYSICAL_STATE_SELECTION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
            "bateman-turok-2026",
            "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
            "FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1": "DIRECT_LOCAL",
            "bateman-turok-2026": "SUPPORTING",
            "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1": "SUPPORTING",
            "FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1",
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1",
            "FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1": "DIRECT_LOCAL",
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1": "DIRECT_LOCAL",
            "FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "EVOLUTION_WELLPOSEDNESS",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1",
            "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1": "DIRECT_LOCAL",
            "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "CAUSAL_PROPAGATION_GREEN",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "GAUGE_BV_COHOMOLOGY",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "brunetti-fredenhagen-verch-2001",
            "fewster-verch-2011",
            "fredenhagen-rejzner-2011"
          ],
          "evidence_roles": {
            "brunetti-fredenhagen-verch-2001": "UNREVIEWED",
            "fewster-verch-2011": "UNREVIEWED",
            "fredenhagen-rejzner-2011": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "INTERACTION_CONSTRUCTION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "fredenhagen-rejzner-2011",
            "brunetti-fredenhagen-verch-2001"
          ],
          "evidence_roles": {
            "fredenhagen-rejzner-2011": "DIRECT_LITERATURE",
            "brunetti-fredenhagen-verch-2001": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "COUNTERTERM_CLASSIFICATION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "fredenhagen-rejzner-2011"
          ],
          "evidence_roles": {
            "fredenhagen-rejzner-2011": "DIRECT_LITERATURE"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "ANOMALY_CLASSIFICATION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "fredenhagen-rejzner-2011"
          ],
          "evidence_roles": {
            "fredenhagen-rejzner-2011": "DIRECT_LITERATURE"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RENORMALIZED_PRODUCTS",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "fredenhagen-rejzner-2011"
          ],
          "evidence_roles": {
            "fredenhagen-rejzner-2011": "DIRECT_LITERATURE"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "QME_RESTORATION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "PIECES_ONLY",
          "evidence": [
            "fredenhagen-rejzner-2011"
          ],
          "evidence_roles": {
            "fredenhagen-rejzner-2011": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RESIDUAL_QUANTUM_TRANSFER",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "PIECES_ONLY",
          "evidence": [
            "fredenhagen-rejzner-2011"
          ],
          "evidence_roles": {
            "fredenhagen-rejzner-2011": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RECONSTRUCTION_LIMITS",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "bender-boettcher-1998",
            "mostafazadeh-2001",
            "gottschalk-2004"
          ],
          "evidence_roles": {
            "bender-boettcher-1998": "UNREVIEWED",
            "mostafazadeh-2001": "UNREVIEWED",
            "gottschalk-2004": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        }
      ],
      "coverage": {
        "direct": 13,
        "assessed": 16,
        "total": 16,
        "complete_direct": false
      },
      "interfaces": [
        {
          "id": "STATE_TO_PROBABILITY",
          "label": "State encoding → probability rule",
          "source_obligations": [
            "STATE_REPRESENTATION"
          ],
          "target_obligations": [
            "PROBABILITY_RULE"
          ],
          "relation": "CONDITIONAL_BRIDGE",
          "certification_status": "CERTIFIED",
          "evidence": [
            "FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1"
          ],
          "rationale": "Finite-trace detector corners and finite exhaustive output partitions satisfying the five displayed hypotheses."
        },
        {
          "id": "SELECTION_TO_DYNAMICS",
          "label": "Physical state selection → dynamics",
          "source_obligations": [
            "PHYSICAL_STATE_SELECTION"
          ],
          "target_obligations": [
            "GENERATOR_SPECTRAL_DYNAMICS"
          ],
          "relation": "CONDITIONAL_BRIDGE",
          "certification_status": "CERTIFIED",
          "evidence": [
            "FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1"
          ],
          "rationale": "The explicit free reduced-mode bosonic Fock carrier, its diagonal total-occupation energy, and normal zero-energy states."
        },
        {
          "id": "DYNAMICS_TO_CAUSALITY",
          "label": "Evolution → causal response",
          "source_obligations": [
            "GENERATOR_SPECTRAL_DYNAMICS",
            "EVOLUTION_WELLPOSEDNESS"
          ],
          "target_obligations": [
            "CAUSAL_PROPAGATION_GREEN"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "GAUGE_TO_INTERACTION",
          "label": "Gauge content → interaction",
          "source_obligations": [
            "KINEMATICS_OBSERVABLES",
            "GAUGE_BV_COHOMOLOGY"
          ],
          "target_obligations": [
            "INTERACTION_CONSTRUCTION"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "RENORMALIZATION_TO_QME",
          "label": "Classifications and products → restored QME",
          "source_obligations": [
            "COUNTERTERM_CLASSIFICATION",
            "ANOMALY_CLASSIFICATION",
            "RENORMALIZED_PRODUCTS"
          ],
          "target_obligations": [
            "QME_RESTORATION"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "QME_TO_RESIDUAL",
          "label": "Restored QME → residual correction",
          "source_obligations": [
            "QME_RESTORATION"
          ],
          "target_obligations": [
            "RESIDUAL_QUANTUM_TRANSFER"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "PREDICTION_TO_RECONSTRUCTION",
          "label": "Prediction chain → standard or operational interpretation",
          "source_obligations": [
            "PROBABILITY_RULE",
            "CAUSAL_PROPAGATION_GREEN",
            "INTERACTION_CONSTRUCTION"
          ],
          "target_obligations": [
            "RECONSTRUCTION_LIMITS"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        }
      ],
      "hard_gates": [
        {
          "id": "OBLIGATION_COVERAGE",
          "label": "Obligation coverage",
          "status": "OPEN",
          "basis": "13/16 obligations have a direct recorded result."
        },
        {
          "id": "CROSS_CELL_COMPOSITION",
          "label": "Cross-cell composition",
          "status": "BLOCKED",
          "basis": "2/7 required interfaces are certified; the remainder block assembly composition."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "label": "Prediction derivation",
          "status": "BLOCKED",
          "basis": "No registered end-to-end derivation connects the selected cells."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "label": "Observable identification",
          "status": "BLOCKED",
          "basis": "No assembly-level map from formal quantities to measured observables is registered."
        },
        {
          "id": "EMPIRICAL_COMPARISON",
          "label": "Empirical comparison",
          "status": "NO_RECORDS",
          "basis": "The empirical ledger contains no comparison for this assembly."
        },
        {
          "id": "ROBUSTNESS_OUT_OF_SAMPLE",
          "label": "Robustness / out-of-sample",
          "status": "NO_RECORDS",
          "basis": "No robustness or held-out prediction record is registered."
        }
      ],
      "complete_theory": false,
      "empirically_supported": false
    },
    {
      "id": "CONSTRUCTIVE_PROGRAMME",
      "label": "Constructive/computable programme",
      "aim": "Track which parts of a predictive theory can be supplied with witnesses or algorithms.",
      "foundations": [
        "CONSTRUCTIVE_COMPUTABLE"
      ],
      "carriers": [
        "FINITE_EXACT",
        "HILBERT_OPERATOR",
        "KREIN_INDEFINITE",
        "ALGEBRAIC_CSTAR",
        "SMOOTH_DISTRIBUTIONAL",
        "LOCALIC_SYNTHETIC"
      ],
      "kind": "NAVIGATIONAL_PROTOTYPE",
      "selection_rule": "DETERMINISTIC_COVERAGE_ENVELOPE",
      "selected_cells": [
        {
          "obligation": "KINEMATICS_OBSERVABLES",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "UNREVIEWED",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "STATE_EXISTENCE",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "STATE_REPRESENTATION",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "PROBABILITY_RULE",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "PHYSICAL_STATE_SELECTION",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "KREIN_INDEFINITE",
          "status": "PIECES_ONLY",
          "evidence": [
            "bender-boettcher-1998",
            "mostafazadeh-2001"
          ],
          "evidence_roles": {
            "bender-boettcher-1998": "SUPPORTING",
            "mostafazadeh-2001": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "EVOLUTION_WELLPOSEDNESS",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "CAUSAL_PROPAGATION_GREEN",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "PIECES_ONLY",
          "evidence": [
            "pour-el-richards-1981",
            "weihrauch-zhong-2002",
            "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1",
            "selivanova-selivanov-2013",
            "zhong-weihrauch-2003-distributions",
            "weihrauch-zhong-2006-fundamental"
          ],
          "evidence_roles": {
            "pour-el-richards-1981": "SUPPORTING",
            "weihrauch-zhong-2002": "SUPPORTING",
            "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1": "SUPPORTING",
            "selivanova-selivanov-2013": "UNREVIEWED",
            "zhong-weihrauch-2003-distributions": "UNREVIEWED",
            "weihrauch-zhong-2006-fundamental": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "GAUGE_BV_COHOMOLOGY",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "HILBERT_OPERATOR",
          "status": "PIECES_ONLY",
          "evidence": [
            "neumann-pape-streicher-2018",
            "pour-el-richards-1981",
            "bridges-svozil-2000",
            "richman-bridges-1999"
          ],
          "evidence_roles": {
            "neumann-pape-streicher-2018": "UNREVIEWED",
            "pour-el-richards-1981": "UNREVIEWED",
            "bridges-svozil-2000": "UNREVIEWED",
            "richman-bridges-1999": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "INTERACTION_CONSTRUCTION",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "COUNTERTERM_CLASSIFICATION",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "ANOMALY_CLASSIFICATION",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RENORMALIZED_PRODUCTS",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "QME_RESTORATION",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RESIDUAL_QUANTUM_TRANSFER",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING",
            "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RECONSTRUCTION_LIMITS",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "coquand-spitters-2009",
            "henry-2014",
            "neumann-pape-streicher-2018"
          ],
          "evidence_roles": {
            "coquand-spitters-2009": "UNREVIEWED",
            "henry-2014": "UNREVIEWED",
            "neumann-pape-streicher-2018": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        }
      ],
      "coverage": {
        "direct": 8,
        "assessed": 16,
        "total": 16,
        "complete_direct": false
      },
      "interfaces": [
        {
          "id": "STATE_TO_PROBABILITY",
          "label": "State encoding → probability rule",
          "source_obligations": [
            "STATE_REPRESENTATION"
          ],
          "target_obligations": [
            "PROBABILITY_RULE"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "SELECTION_TO_DYNAMICS",
          "label": "Physical state selection → dynamics",
          "source_obligations": [
            "PHYSICAL_STATE_SELECTION"
          ],
          "target_obligations": [
            "GENERATOR_SPECTRAL_DYNAMICS"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "DYNAMICS_TO_CAUSALITY",
          "label": "Evolution → causal response",
          "source_obligations": [
            "GENERATOR_SPECTRAL_DYNAMICS",
            "EVOLUTION_WELLPOSEDNESS"
          ],
          "target_obligations": [
            "CAUSAL_PROPAGATION_GREEN"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "GAUGE_TO_INTERACTION",
          "label": "Gauge content → interaction",
          "source_obligations": [
            "KINEMATICS_OBSERVABLES",
            "GAUGE_BV_COHOMOLOGY"
          ],
          "target_obligations": [
            "INTERACTION_CONSTRUCTION"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "RENORMALIZATION_TO_QME",
          "label": "Classifications and products → restored QME",
          "source_obligations": [
            "COUNTERTERM_CLASSIFICATION",
            "ANOMALY_CLASSIFICATION",
            "RENORMALIZED_PRODUCTS"
          ],
          "target_obligations": [
            "QME_RESTORATION"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "QME_TO_RESIDUAL",
          "label": "Restored QME → residual correction",
          "source_obligations": [
            "QME_RESTORATION"
          ],
          "target_obligations": [
            "RESIDUAL_QUANTUM_TRANSFER"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "PREDICTION_TO_RECONSTRUCTION",
          "label": "Prediction chain → standard or operational interpretation",
          "source_obligations": [
            "PROBABILITY_RULE",
            "CAUSAL_PROPAGATION_GREEN",
            "INTERACTION_CONSTRUCTION"
          ],
          "target_obligations": [
            "RECONSTRUCTION_LIMITS"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        }
      ],
      "hard_gates": [
        {
          "id": "OBLIGATION_COVERAGE",
          "label": "Obligation coverage",
          "status": "OPEN",
          "basis": "8/16 obligations have a direct recorded result."
        },
        {
          "id": "CROSS_CELL_COMPOSITION",
          "label": "Cross-cell composition",
          "status": "BLOCKED",
          "basis": "0/7 required interfaces are certified; the remainder block assembly composition."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "label": "Prediction derivation",
          "status": "BLOCKED",
          "basis": "No registered end-to-end derivation connects the selected cells."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "label": "Observable identification",
          "status": "BLOCKED",
          "basis": "No assembly-level map from formal quantities to measured observables is registered."
        },
        {
          "id": "EMPIRICAL_COMPARISON",
          "label": "Empirical comparison",
          "status": "NO_RECORDS",
          "basis": "The empirical ledger contains no comparison for this assembly."
        },
        {
          "id": "ROBUSTNESS_OUT_OF_SAMPLE",
          "label": "Robustness / out-of-sample",
          "status": "NO_RECORDS",
          "basis": "No robustness or held-out prediction record is registered."
        }
      ],
      "complete_theory": false,
      "empirically_supported": false
    },
    {
      "id": "TOPOS_INTERNAL_PROGRAMME",
      "label": "Topos/internal programme",
      "aim": "Map a physics construction performed inside an alternative logical or geometric universe.",
      "foundations": [
        "TOPOS_INTERNAL"
      ],
      "carriers": [
        "FINITE_EXACT",
        "HILBERT_OPERATOR",
        "KREIN_INDEFINITE",
        "ALGEBRAIC_CSTAR",
        "SMOOTH_DISTRIBUTIONAL",
        "LOCALIC_SYNTHETIC"
      ],
      "kind": "NAVIGATIONAL_PROTOTYPE",
      "selection_rule": "DETERMINISTIC_COVERAGE_ENVELOPE",
      "selected_cells": [
        {
          "obligation": "KINEMATICS_OBSERVABLES",
          "foundation": "TOPOS_INTERNAL",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "heunen-landsman-spitters-2009",
            "doring-2008",
            "brenna-flori-2012",
            "harding-heunen-2019"
          ],
          "evidence_roles": {
            "heunen-landsman-spitters-2009": "UNREVIEWED",
            "doring-2008": "UNREVIEWED",
            "brenna-flori-2012": "UNREVIEWED",
            "harding-heunen-2019": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "STATE_EXISTENCE",
          "foundation": "TOPOS_INTERNAL",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
            "abramsky-coecke-2004"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL",
            "abramsky-coecke-2004": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "STATE_REPRESENTATION",
          "foundation": "TOPOS_INTERNAL",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
            "constantin-doring-2020",
            "abramsky-coecke-2004"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL",
            "constantin-doring-2020": "DIRECT_LITERATURE",
            "abramsky-coecke-2004": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "PROBABILITY_RULE",
          "foundation": "TOPOS_INTERNAL",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
            "abramsky-coecke-2004",
            "constantin-doring-2020"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL",
            "abramsky-coecke-2004": "DIRECT_LITERATURE",
            "constantin-doring-2020": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "PHYSICAL_STATE_SELECTION",
          "foundation": "TOPOS_INTERNAL",
          "carrier": "KREIN_INDEFINITE",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "gottschalk-2004",
            "harding-heunen-2019"
          ],
          "evidence_roles": {
            "gottschalk-2004": "DIRECT_LITERATURE",
            "harding-heunen-2019": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
          "foundation": "TOPOS_INTERNAL",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
            "abramsky-coecke-2004"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL",
            "abramsky-coecke-2004": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "EVOLUTION_WELLPOSEDNESS",
          "foundation": "TOPOS_INTERNAL",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "CAUSAL_PROPAGATION_GREEN",
          "foundation": "TOPOS_INTERNAL",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "GAUGE_BV_COHOMOLOGY",
          "foundation": "TOPOS_INTERNAL",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "PIECES_ONLY",
          "evidence": [
            "heunen-landsman-spitters-2009",
            "doring-2008",
            "brenna-flori-2012",
            "harding-heunen-2019"
          ],
          "evidence_roles": {
            "heunen-landsman-spitters-2009": "UNREVIEWED",
            "doring-2008": "UNREVIEWED",
            "brenna-flori-2012": "UNREVIEWED",
            "harding-heunen-2019": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "INTERACTION_CONSTRUCTION",
          "foundation": "TOPOS_INTERNAL",
          "carrier": "FINITE_EXACT",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "COUNTERTERM_CLASSIFICATION",
          "foundation": "TOPOS_INTERNAL",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "ANOMALY_CLASSIFICATION",
          "foundation": "TOPOS_INTERNAL",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RENORMALIZED_PRODUCTS",
          "foundation": "TOPOS_INTERNAL",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "QME_RESTORATION",
          "foundation": "TOPOS_INTERNAL",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RESIDUAL_QUANTUM_TRANSFER",
          "foundation": "TOPOS_INTERNAL",
          "carrier": "FINITE_EXACT",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RECONSTRUCTION_LIMITS",
          "foundation": "TOPOS_INTERNAL",
          "carrier": "ALGEBRAIC_CSTAR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "heunen-landsman-spitters-2009",
            "doring-2008",
            "brenna-flori-2012",
            "harding-heunen-2019"
          ],
          "evidence_roles": {
            "heunen-landsman-spitters-2009": "UNREVIEWED",
            "doring-2008": "UNREVIEWED",
            "brenna-flori-2012": "UNREVIEWED",
            "harding-heunen-2019": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        }
      ],
      "coverage": {
        "direct": 9,
        "assessed": 16,
        "total": 16,
        "complete_direct": false
      },
      "interfaces": [
        {
          "id": "STATE_TO_PROBABILITY",
          "label": "State encoding → probability rule",
          "source_obligations": [
            "STATE_REPRESENTATION"
          ],
          "target_obligations": [
            "PROBABILITY_RULE"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "SELECTION_TO_DYNAMICS",
          "label": "Physical state selection → dynamics",
          "source_obligations": [
            "PHYSICAL_STATE_SELECTION"
          ],
          "target_obligations": [
            "GENERATOR_SPECTRAL_DYNAMICS"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "DYNAMICS_TO_CAUSALITY",
          "label": "Evolution → causal response",
          "source_obligations": [
            "GENERATOR_SPECTRAL_DYNAMICS",
            "EVOLUTION_WELLPOSEDNESS"
          ],
          "target_obligations": [
            "CAUSAL_PROPAGATION_GREEN"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "GAUGE_TO_INTERACTION",
          "label": "Gauge content → interaction",
          "source_obligations": [
            "KINEMATICS_OBSERVABLES",
            "GAUGE_BV_COHOMOLOGY"
          ],
          "target_obligations": [
            "INTERACTION_CONSTRUCTION"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "RENORMALIZATION_TO_QME",
          "label": "Classifications and products → restored QME",
          "source_obligations": [
            "COUNTERTERM_CLASSIFICATION",
            "ANOMALY_CLASSIFICATION",
            "RENORMALIZED_PRODUCTS"
          ],
          "target_obligations": [
            "QME_RESTORATION"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "QME_TO_RESIDUAL",
          "label": "Restored QME → residual correction",
          "source_obligations": [
            "QME_RESTORATION"
          ],
          "target_obligations": [
            "RESIDUAL_QUANTUM_TRANSFER"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        },
        {
          "id": "PREDICTION_TO_RECONSTRUCTION",
          "label": "Prediction chain → standard or operational interpretation",
          "source_obligations": [
            "PROBABILITY_RULE",
            "CAUSAL_PROPAGATION_GREEN",
            "INTERACTION_CONSTRUCTION"
          ],
          "target_obligations": [
            "RECONSTRUCTION_LIMITS"
          ],
          "relation": "NOT_ASSESSED",
          "certification_status": "NOT_ASSESSED",
          "evidence": [],
          "rationale": "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation."
        }
      ],
      "hard_gates": [
        {
          "id": "OBLIGATION_COVERAGE",
          "label": "Obligation coverage",
          "status": "OPEN",
          "basis": "9/16 obligations have a direct recorded result."
        },
        {
          "id": "CROSS_CELL_COMPOSITION",
          "label": "Cross-cell composition",
          "status": "BLOCKED",
          "basis": "0/7 required interfaces are certified; the remainder block assembly composition."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "label": "Prediction derivation",
          "status": "BLOCKED",
          "basis": "No registered end-to-end derivation connects the selected cells."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "label": "Observable identification",
          "status": "BLOCKED",
          "basis": "No assembly-level map from formal quantities to measured observables is registered."
        },
        {
          "id": "EMPIRICAL_COMPARISON",
          "label": "Empirical comparison",
          "status": "NO_RECORDS",
          "basis": "The empirical ledger contains no comparison for this assembly."
        },
        {
          "id": "ROBUSTNESS_OUT_OF_SAMPLE",
          "label": "Robustness / out-of-sample",
          "status": "NO_RECORDS",
          "basis": "No robustness or held-out prediction record is registered."
        }
      ],
      "complete_theory": false,
      "empirically_supported": false
    }
  ],
  "empirical_ledger": {
    "record_schema": [
      "assembly",
      "benchmark",
      "observable_map",
      "dataset",
      "prediction",
      "comparison_method",
      "uncertainty",
      "parameter_fit_scope",
      "out_of_sample_status",
      "evidence"
    ],
    "benchmarks": [
      {
        "id": "LOCAL_GRAVITY",
        "label": "Local gravity and equivalence tests",
        "question": "Which operational observables reproduce the measured weak-field and equivalence-principle limits?",
        "status": "NOT_REGISTERED"
      },
      {
        "id": "SOLAR_SYSTEM",
        "label": "Solar-system dynamics",
        "question": "What parameterized predictions are compared with orbital, ranging, and time-delay data?",
        "status": "NOT_REGISTERED"
      },
      {
        "id": "COMPACT_BINARIES",
        "label": "Compact binaries",
        "question": "What conservative and radiative predictions are compared with binary-pulsar or inspiral observations?",
        "status": "NOT_REGISTERED"
      },
      {
        "id": "GRAVITATIONAL_WAVES",
        "label": "Gravitational waves",
        "question": "What propagation, speed, damping, and polarization observables are identified and tested?",
        "status": "NOT_REGISTERED"
      },
      {
        "id": "GALACTIC_LENSING_DYNAMICS",
        "label": "Galactic dynamics and lensing",
        "question": "Can one parameter choice account for both motion and light propagation on galactic scales?",
        "status": "NOT_REGISTERED"
      },
      {
        "id": "COSMOLOGY",
        "label": "Cosmology and structure",
        "question": "What background and perturbation predictions are compared with expansion and structure data?",
        "status": "NOT_REGISTERED"
      }
    ],
    "records": []
  },
  "claim_flags": {
    "prototype_assemblies_generated": true,
    "selected_cells_content_addressed": true,
    "interface_and_coverage_states_separated": true,
    "at_least_one_cross_cell_interface_certified": true,
    "empirical_record_schema_declared": true,
    "cross_cell_composability_established": false,
    "prediction_chain_established": false,
    "empirical_agreement_assessed": false,
    "complete_observationally_valid_theory_identified": false
  },
  "does_not_establish": [
    "that selected cells concern the same physical model or scope",
    "that either certified scoped bridge supplies any unregistered carrier or foundation translation",
    "that direct coverage composes into an end-to-end prediction",
    "that a reduced or finite construction has a controlled continuum limit",
    "that any prototype agrees with observations",
    "that the benchmark catalogue is a complete set of physical tests",
    "a complete theory, a new Lorentzian-causal result, or a quantum lifecycle promotion"
  ],
  "source_atlas_digest": "0feeede6101f7539fcb73f5e4c0f740533448021bb5a226fd9d515880db2d00d",
  "canonical_digest": "caa72886481b90682ee5f738feb6b4b2d31a59d2d812d308d43e54ec1c85338e"
};
