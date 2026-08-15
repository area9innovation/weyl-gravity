window.THEORY_ASSEMBLY_DATA = {
  "schema_version": "foundational-theory-assembly-atlas-v1",
  "result_id": "FOUNDATIONAL_THEORY_ASSEMBLY_ATLAS_V1",
  "result_kind": "FAIL_CLOSED_THEORY_ASSEMBLY_AND_EMPIRICAL_LEDGER",
  "lifecycle": "VERIFIED_NAVIGATION_ARTIFACT",
  "title": "Model-scoped prediction assemblies, theory prototypes, maturity rails, and calibration controls",
  "created": "2026-08-15",
  "dependency_tags": [
    "LOCAL-ALGEBRAIC",
    "EUCLIDEAN-SPECTRAL",
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
  "certified_carrier_interface_records": [
    {
      "id": "EUCLIDEAN_TO_KREIN_CARRIER",
      "label": "Positive Euclidean lattice carrier versus BT Krein carrier",
      "status": "CERTIFIED",
      "relation": "INCOMPATIBLE",
      "source_coordinates": [
        {
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "obligation": "STATE_REPRESENTATION"
        }
      ],
      "target_coordinates": [
        {
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "obligation": "STATE_REPRESENTATION"
        }
      ],
      "scope": "The positive-Omega Euclidean lattice path integral and the all-real-Omega two-field BT path integral cannot be identified as the same full nonperturbative configuration space and measure.",
      "witness": {
        "source_domain": "Omega_x=exp(lambda*phi_x)>0",
        "target_domain_caveat": "the phi and (Omega,Upsilon) path integrals are inequivalent, 'the former integrates over Omega > 0 whereas the latter integrates over all Omega' -- a statement about the vacuum, not the action"
      },
      "evidence": [
        "REVERSE_PHYSICS_BT_EUCLIDEAN_LATTICE_PILOT_V1",
        "REVERSE_PHYSICS_GHOST_PARITY_DOUBLE_POLE_V1",
        "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1"
      ],
      "does_not_establish": "No obstruction is proved to a conditional perturbative, Osterwalder-Schrader, analytic-continuation, or other explicitly constructed bridge."
    }
  ],
  "assemblies": [
    {
      "id": "STANDARD_MIXED_REFERENCE",
      "label": "Mainstream GR and quantum-field-theory reference",
      "short_label": "Mainstream GR / QFT",
      "camp_kind": "REFERENCE_TRADITION",
      "camp_summary": "The conventional reference combines classical spacetime geometry, standard quantum mechanics, continuum field theory, and the ordinary mathematical toolkit used across modern physics.",
      "central_question": "How much of a complete predictive theory is already covered by the mainstream GR/QFT toolkit, and which joins are still merely assumed?",
      "lineage": [
        "Einstein–Hilbert gravity",
        "standard quantum mechanics",
        "perturbative and curved-spacetime QFT"
      ],
      "signature_ideas": [
        "classical spacetime geometry",
        "positive Hilbert-space quantum theory",
        "continuum fields and local operators"
      ],
      "atlas_window": "A deliberately broad reference envelope that may select a different carrier for each physical job.",
      "scope_note": "This is a calibration baseline, not one historical school, one model, or proof that the selected mainstream ingredients compose.",
      "aim": "Use mainstream mathematical practice as a generous reference, while exposing every unregistered composition step.",
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
          "carrier": "HILBERT_OPERATOR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "ANOMALY_CLASSIFICATION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "HILBERT_OPERATOR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1": "DIRECT_LOCAL"
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
          "carrier": "HILBERT_OPERATOR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RESIDUAL_QUANTUM_TRANSFER",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "HILBERT_OPERATOR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1": "DIRECT_LOCAL"
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
        "direct": 16,
        "assessed": 16,
        "total": 16,
        "complete_direct": true
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
      "maturity_rails": [
        {
          "id": "OBLIGATION_COVERAGE",
          "label": "Obligation coverage",
          "status": "SATISFIED",
          "basis": "16/16 obligations have a direct recorded result."
        },
        {
          "id": "CROSS_CELL_COMPOSITION",
          "label": "Cross-cell composition",
          "status": "PARTIALLY_CERTIFIED",
          "basis": "2/7 required interfaces are certified; unassessed joins are missing work, not incompatibility results."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "label": "Prediction derivation",
          "status": "NOT_EVALUABLE",
          "basis": "An end-to-end prediction test is premature until the required cross-cell joins are registered."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "label": "Observable identification",
          "status": "NOT_REGISTERED",
          "basis": "No assembly-level map from formal quantities to measured observables is registered."
        },
        {
          "id": "NUMERICAL_REPRODUCIBILITY",
          "label": "Numerical reproducibility",
          "status": "NO_RECORDS",
          "basis": "No independent numerical reproduction record is registered for this assembly."
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
      "label": "Algebraic QFT and local-covariance tradition",
      "short_label": "Algebraic QFT",
      "camp_kind": "RESEARCH_TRADITION",
      "camp_summary": "Algebraic quantum field theory starts from observable algebras and their states, emphasizing locality, representation independence, and structural relations between spacetime regions.",
      "central_question": "Can a theory be built from observables, states, and locality before choosing a preferred particle or wavefunction representation?",
      "lineage": [
        "Haag–Kastler algebraic QFT",
        "locally covariant QFT",
        "operator-algebraic quantum theory"
      ],
      "signature_ideas": [
        "observables before wavefunctions",
        "local nets of algebras",
        "states as positive expectation-value rules"
      ],
      "atlas_window": "The classical-standard algebraic C*-carrier column only.",
      "scope_note": "A C*-algebra coverage profile does not by itself supply curved-spacetime dynamics, renormalized interactions, or a preferred physical state.",
      "aim": "Show what the present algebra-first evidence covers without silently importing Hilbert, PDE, or particle assumptions.",
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
      "maturity_rails": [
        {
          "id": "OBLIGATION_COVERAGE",
          "label": "Obligation coverage",
          "status": "OPEN",
          "basis": "12/16 obligations have a direct recorded result."
        },
        {
          "id": "CROSS_CELL_COMPOSITION",
          "label": "Cross-cell composition",
          "status": "NOT_ASSESSED",
          "basis": "0/7 required interfaces are certified; unassessed joins are missing work, not incompatibility results."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "label": "Prediction derivation",
          "status": "NOT_EVALUABLE",
          "basis": "An end-to-end prediction test is premature until the required cross-cell joins are registered."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "label": "Observable identification",
          "status": "NOT_REGISTERED",
          "basis": "No assembly-level map from formal quantities to measured observables is registered."
        },
        {
          "id": "NUMERICAL_REPRODUCIBILITY",
          "label": "Numerical reproducibility",
          "status": "NO_RECORDS",
          "basis": "No independent numerical reproduction record is registered for this assembly."
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
      "label": "Finite, discrete, and exactly checkable models",
      "short_label": "Finite / discrete",
      "camp_kind": "METHODOLOGICAL_TRADITION",
      "camp_summary": "Finite and discrete programmes replace a continuum or infinite construction by exact matrices, graphs, modes, or algebraic data that can be exhaustively checked.",
      "central_question": "Which parts of physics are genuinely finite and algebraic, and which require a controlled passage back to a continuum?",
      "lineage": [
        "lattice and finite-mode models",
        "finite quantum systems",
        "exact computer-assisted mathematics"
      ],
      "signature_ideas": [
        "finite carriers",
        "exact arithmetic",
        "explicit refinement or continuum-limit obligations"
      ],
      "atlas_window": "The finite/discrete regime with the finite exact-algebra carrier.",
      "scope_note": "A finite regulator, a finite physical ontology, and a rejection of actual infinity are three different claims; this lens does not identify them.",
      "aim": "Separate exactly checkable finite physics from the additional estimates and limit theorems needed for continuum claims.",
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
      "maturity_rails": [
        {
          "id": "OBLIGATION_COVERAGE",
          "label": "Obligation coverage",
          "status": "OPEN",
          "basis": "10/16 obligations have a direct recorded result."
        },
        {
          "id": "CROSS_CELL_COMPOSITION",
          "label": "Cross-cell composition",
          "status": "NOT_ASSESSED",
          "basis": "0/7 required interfaces are certified; unassessed joins are missing work, not incompatibility results."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "label": "Prediction derivation",
          "status": "NOT_EVALUABLE",
          "basis": "An end-to-end prediction test is premature until the required cross-cell joins are registered."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "label": "Observable identification",
          "status": "NOT_REGISTERED",
          "basis": "No assembly-level map from formal quantities to measured observables is registered."
        },
        {
          "id": "NUMERICAL_REPRODUCIBILITY",
          "label": "Numerical reproducibility",
          "status": "NO_RECORDS",
          "basis": "No independent numerical reproduction record is registered for this assembly."
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
      "id": "BT_EUCLIDEAN_LATTICE_PROGRAMME",
      "label": "Bateman–Turok hidden-ghost-parity programme",
      "short_label": "Bateman–Turok",
      "camp_kind": "NAMED_RESEARCH_PROGRAMME",
      "camp_summary": "Bateman and Turok seek a higher-derivative quantum theory whose hidden ghost-parity structure yields positive physical probabilities without simply discarding the ghost sector.",
      "central_question": "Can hidden ghost parity and a generalized Born construction make a higher-derivative interacting theory probabilistically consistent?",
      "lineage": [
        "Sam Bateman",
        "Neil Turok",
        "hidden ghost parity and perfect-square scalar models"
      ],
      "signature_ideas": [
        "one-sided ghost charge",
        "generalized Born probabilities",
        "positive Euclidean finite-volume control"
      ],
      "atlas_window": "The currently imported window is the positive finite Euclidean lattice and its coarse two-algorithm reproduction, not the full Lorentzian/Krein scattering proposal.",
      "scope_note": "This profile neither proves the all-order Bateman–Turok construction nor treats a Euclidean Gibbs measure as identical to the proposed Lorentzian Krein carrier.",
      "aim": "Make the certified positive Euclidean slice visible inside the broader Bateman–Turok programme while keeping its unbuilt Lorentzian and continuum bridges explicit.",
      "foundations": [
        "FINITE_DISCRETE"
      ],
      "carriers": [
        "SMOOTH_DISTRIBUTIONAL"
      ],
      "kind": "NAVIGATIONAL_PROTOTYPE",
      "selection_rule": "DETERMINISTIC_COVERAGE_ENVELOPE",
      "selected_cells": [
        {
          "obligation": "KINEMATICS_OBSERVABLES",
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "LOCAL_RESULT",
          "evidence": [
            "kogut-susskind-1975",
            "zohar-burrello-2014",
            "bahr-dittrich-2009",
            "dittrich-2012",
            "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1"
          ],
          "evidence_roles": {
            "kogut-susskind-1975": "UNREVIEWED",
            "zohar-burrello-2014": "UNREVIEWED",
            "bahr-dittrich-2009": "UNREVIEWED",
            "dittrich-2012": "UNREVIEWED",
            "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "STATE_EXISTENCE",
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1",
            "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1": "SUPPORTING",
            "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "STATE_REPRESENTATION",
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1",
            "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1": "SUPPORTING",
            "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "PROBABILITY_RULE",
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1",
            "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1": "SUPPORTING",
            "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "PHYSICAL_STATE_SELECTION",
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "REVIEWED_GAP",
          "evidence": [
            "FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "kogut-susskind-1975",
            "zohar-burrello-2014",
            "dittrich-2012"
          ],
          "evidence_roles": {
            "kogut-susskind-1975": "DIRECT_LITERATURE",
            "zohar-burrello-2014": "DIRECT_LITERATURE",
            "dittrich-2012": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "EVOLUTION_WELLPOSEDNESS",
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "kogut-susskind-1975",
            "zohar-burrello-2014",
            "dittrich-2012"
          ],
          "evidence_roles": {
            "kogut-susskind-1975": "DIRECT_LITERATURE",
            "zohar-burrello-2014": "DIRECT_LITERATURE",
            "dittrich-2012": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "CAUSAL_PROPAGATION_GREEN",
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "PIECES_ONLY",
          "evidence": [
            "kogut-susskind-1975",
            "zohar-burrello-2014"
          ],
          "evidence_roles": {
            "kogut-susskind-1975": "SUPPORTING",
            "zohar-burrello-2014": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "GAUGE_BV_COHOMOLOGY",
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "kogut-susskind-1975",
            "zohar-burrello-2014",
            "bahr-dittrich-2009",
            "dittrich-2012"
          ],
          "evidence_roles": {
            "kogut-susskind-1975": "UNREVIEWED",
            "zohar-burrello-2014": "UNREVIEWED",
            "bahr-dittrich-2009": "UNREVIEWED",
            "dittrich-2012": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "INTERACTION_CONSTRUCTION",
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "LOCAL_RESULT",
          "evidence": [
            "kogut-susskind-1975",
            "zohar-burrello-2014",
            "bahr-dittrich-2009",
            "dittrich-2012",
            "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1"
          ],
          "evidence_roles": {
            "kogut-susskind-1975": "DIRECT_LITERATURE",
            "zohar-burrello-2014": "DIRECT_LITERATURE",
            "bahr-dittrich-2009": "SUPPORTING",
            "dittrich-2012": "SUPPORTING",
            "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "COUNTERTERM_CLASSIFICATION",
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "PIECES_ONLY",
          "evidence": [
            "kogut-susskind-1975",
            "zohar-burrello-2014",
            "bahr-dittrich-2009"
          ],
          "evidence_roles": {
            "kogut-susskind-1975": "SUPPORTING",
            "zohar-burrello-2014": "SUPPORTING",
            "bahr-dittrich-2009": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "ANOMALY_CLASSIFICATION",
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "PIECES_ONLY",
          "evidence": [
            "kogut-susskind-1975",
            "zohar-burrello-2014",
            "bahr-dittrich-2009"
          ],
          "evidence_roles": {
            "kogut-susskind-1975": "SUPPORTING",
            "zohar-burrello-2014": "SUPPORTING",
            "bahr-dittrich-2009": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RENORMALIZED_PRODUCTS",
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "PIECES_ONLY",
          "evidence": [
            "kogut-susskind-1975",
            "zohar-burrello-2014",
            "dittrich-2012"
          ],
          "evidence_roles": {
            "kogut-susskind-1975": "SUPPORTING",
            "zohar-burrello-2014": "SUPPORTING",
            "dittrich-2012": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "QME_RESTORATION",
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "PIECES_ONLY",
          "evidence": [
            "kogut-susskind-1975",
            "zohar-burrello-2014",
            "bahr-dittrich-2009"
          ],
          "evidence_roles": {
            "kogut-susskind-1975": "SUPPORTING",
            "zohar-burrello-2014": "SUPPORTING",
            "bahr-dittrich-2009": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RESIDUAL_QUANTUM_TRANSFER",
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "PIECES_ONLY",
          "evidence": [
            "kogut-susskind-1975",
            "zohar-burrello-2014",
            "bahr-dittrich-2009",
            "dittrich-2012"
          ],
          "evidence_roles": {
            "kogut-susskind-1975": "SUPPORTING",
            "zohar-burrello-2014": "SUPPORTING",
            "bahr-dittrich-2009": "SUPPORTING",
            "dittrich-2012": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RECONSTRUCTION_LIMITS",
          "foundation": "FINITE_DISCRETE",
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "PRIORITY_GAP",
          "evidence": [
            "FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1",
            "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1": "UNREVIEWED",
            "FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1": "SUPPORTING"
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
      "maturity_rails": [
        {
          "id": "OBLIGATION_COVERAGE",
          "label": "Obligation coverage",
          "status": "OPEN",
          "basis": "8/16 obligations have a direct recorded result."
        },
        {
          "id": "CROSS_CELL_COMPOSITION",
          "label": "Cross-cell composition",
          "status": "NOT_ASSESSED",
          "basis": "0/7 required interfaces are certified; unassessed joins are missing work, not incompatibility results."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "label": "Prediction derivation",
          "status": "NOT_EVALUABLE",
          "basis": "An end-to-end prediction test is premature until the required cross-cell joins are registered."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "label": "Observable identification",
          "status": "NOT_REGISTERED",
          "basis": "No assembly-level map from formal quantities to measured observables is registered."
        },
        {
          "id": "NUMERICAL_REPRODUCIBILITY",
          "label": "Numerical reproducibility",
          "status": "COARSE_REPRODUCTION_ONLY",
          "basis": "all declared finite-volume observables agree within four combined standard errors; not all declared observables agree within two combined standard errors. This is algorithmic reproduction, not empirical validation."
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
      "label": "Reverse mathematics and weak-foundation programme",
      "short_label": "Reverse mathematics",
      "camp_kind": "METHODOLOGICAL_TRADITION",
      "camp_summary": "Reverse mathematics and Choice audits ask which axioms are actually needed for a theorem, rather than accepting the usual background foundation as an invisible package.",
      "central_question": "What is the weakest explicit logical or set-existence base that still proves each physical construction?",
      "lineage": [
        "proof theory",
        "reverse mathematics",
        "ZF without full Choice"
      ],
      "signature_ideas": [
        "calibrate theorem strength",
        "separate sufficiency from necessity",
        "track representation dependence"
      ],
      "atlas_window": "Finite exact carriers over weak arithmetic and ZF with weakened Choice.",
      "scope_note": "Combining two weak bases in one navigation lens does not identify them or prove a weakest-foundation theorem.",
      "aim": "Expose arithmetic and Choice dependencies of exact constructions without collapsing distinct foundational systems.",
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
      "maturity_rails": [
        {
          "id": "OBLIGATION_COVERAGE",
          "label": "Obligation coverage",
          "status": "OPEN",
          "basis": "9/16 obligations have a direct recorded result."
        },
        {
          "id": "CROSS_CELL_COMPOSITION",
          "label": "Cross-cell composition",
          "status": "NOT_ASSESSED",
          "basis": "0/7 required interfaces are certified; unassessed joins are missing work, not incompatibility results."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "label": "Prediction derivation",
          "status": "NOT_EVALUABLE",
          "basis": "An end-to-end prediction test is premature until the required cross-cell joins are registered."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "label": "Observable identification",
          "status": "NOT_REGISTERED",
          "basis": "No assembly-level map from formal quantities to measured observables is registered."
        },
        {
          "id": "NUMERICAL_REPRODUCIBILITY",
          "label": "Numerical reproducibility",
          "status": "NO_RECORDS",
          "basis": "No independent numerical reproduction record is registered for this assembly."
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
      "label": "Mannheim conformal-gravity programme",
      "short_label": "Mannheim conformal gravity",
      "camp_kind": "NAMED_RESEARCH_PROGRAMME",
      "camp_summary": "The Mannheim programme combines fourth-order conformal gravity, Mannheim–Kazanas phenomenology, and a Bender–Mannheim PT/quasi-Hermitian response to the ghost and unitarity problem.",
      "central_question": "Can conformal gravity provide a viable classical phenomenology and a positive quantum interpretation once the inner product is chosen dynamically?",
      "lineage": [
        "Philip Mannheim",
        "Mannheim–Kazanas phenomenology",
        "Bender–Mannheim PT-symmetric quantization"
      ],
      "signature_ideas": [
        "Weyl-invariant fourth-order gravity",
        "PT/quasi-Hermitian positive metric",
        "galactic and cosmological phenomenology"
      ],
      "atlas_window": "Comparison-relevant Hilbert/operator, Krein/indefinite, and smooth continuum cells under classical mathematics.",
      "scope_note": "A generic Krein fundamental symmetry is not Mannheim's field-theoretic C operator, and this mixed-carrier lens does not certify his unitarity or phenomenological claims.",
      "aim": "Display where the atlas can engage Mannheim's classical and quantum questions without identifying adjacent indefinite-space results with the programme's missing positive metric.",
      "foundations": [
        "CLASSICAL_STANDARD"
      ],
      "carriers": [
        "HILBERT_OPERATOR",
        "KREIN_INDEFINITE",
        "SMOOTH_DISTRIBUTIONAL"
      ],
      "kind": "NAVIGATIONAL_PROTOTYPE",
      "selection_rule": "DETERMINISTIC_COVERAGE_ENVELOPE",
      "selected_cells": [
        {
          "obligation": "KINEMATICS_OBSERVABLES",
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
          "carrier": "HILBERT_OPERATOR",
          "status": "LITERATURE_RESULT",
          "evidence": [
            "hardy-2001",
            "chiribella-dariano-perinotti-2011"
          ],
          "evidence_roles": {
            "hardy-2001": "DIRECT_LITERATURE",
            "chiribella-dariano-perinotti-2011": "DIRECT_LITERATURE"
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
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "INTERACTION_CONSTRUCTION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "HILBERT_OPERATOR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "COUNTERTERM_CLASSIFICATION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "HILBERT_OPERATOR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "ANOMALY_CLASSIFICATION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "HILBERT_OPERATOR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RENORMALIZED_PRODUCTS",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "HILBERT_OPERATOR",
          "status": "PIECES_ONLY",
          "evidence": [
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1": "SUPPORTING"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "QME_RESTORATION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "HILBERT_OPERATOR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RESIDUAL_QUANTUM_TRANSFER",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "HILBERT_OPERATOR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1": "DIRECT_LOCAL"
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
        "direct": 15,
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
      "maturity_rails": [
        {
          "id": "OBLIGATION_COVERAGE",
          "label": "Obligation coverage",
          "status": "OPEN",
          "basis": "15/16 obligations have a direct recorded result."
        },
        {
          "id": "CROSS_CELL_COMPOSITION",
          "label": "Cross-cell composition",
          "status": "PARTIALLY_CERTIFIED",
          "basis": "1/7 required interfaces are certified; unassessed joins are missing work, not incompatibility results."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "label": "Prediction derivation",
          "status": "NOT_EVALUABLE",
          "basis": "An end-to-end prediction test is premature until the required cross-cell joins are registered."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "label": "Observable identification",
          "status": "NOT_REGISTERED",
          "basis": "No assembly-level map from formal quantities to measured observables is registered."
        },
        {
          "id": "NUMERICAL_REPRODUCIBILITY",
          "label": "Numerical reproducibility",
          "status": "NO_RECORDS",
          "basis": "No independent numerical reproduction record is registered for this assembly."
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
      "id": "PURE_WEYL_BV_BFV_PROGRAMME",
      "label": "Pure-Weyl BV–BFV and causal programme",
      "short_label": "Pure-Weyl BV–BFV",
      "camp_kind": "REPOSITORY_PROGRAMME",
      "camp_summary": "This repository's pure-Weyl programme starts from the classical BV–BFV gauge complex, then keeps local quantum algebra, Euclidean spectral work, reduced modes, and Lorentzian causal claims on separate evidence rails.",
      "central_question": "Can pure Weyl gravity be carried from its classical gauge complex to a local quantum theory and a physically admissible Lorentzian state without crossing an uncertified bridge?",
      "lineage": [
        "classical BV–BFV gauge theory",
        "local BRST cohomology",
        "Euclidean spectral and Lorentzian causal analysis"
      ],
      "signature_ideas": [
        "classical complex as import authority",
        "classify anomalies before coefficients",
        "restore QME before residual transfer"
      ],
      "atlas_window": "Classical-standard smooth/PDE, Krein, and algebraic carriers that contain the programme's present classical, reduced, and local-quantum ingredients.",
      "scope_note": "Coverage across these carriers is not a full-complex Lorentzian propagator, Hadamard state, causal perturbative QFT, or restored Lorentzian QME.",
      "aim": "Expose the programme's strong local pieces and the exact typed joins still missing between classical, Euclidean, reduced-mode, and Lorentzian work.",
      "foundations": [
        "CLASSICAL_STANDARD"
      ],
      "carriers": [
        "KREIN_INDEFINITE",
        "ALGEBRAIC_CSTAR",
        "SMOOTH_DISTRIBUTIONAL"
      ],
      "kind": "NAVIGATIONAL_PROTOTYPE",
      "selection_rule": "DETERMINISTIC_COVERAGE_ENVELOPE",
      "selected_cells": [
        {
          "obligation": "KINEMATICS_OBSERVABLES",
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
          "carrier": "SMOOTH_DISTRIBUTIONAL",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1": "UNREVIEWED"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "INTERACTION_CONSTRUCTION",
          "foundation": "CLASSICAL_STANDARD",
          "carrier": "KREIN_INDEFINITE",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1": "DIRECT_LOCAL"
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
          "carrier": "KREIN_INDEFINITE",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1": "DIRECT_LOCAL"
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
        "direct": 15,
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
      "maturity_rails": [
        {
          "id": "OBLIGATION_COVERAGE",
          "label": "Obligation coverage",
          "status": "OPEN",
          "basis": "15/16 obligations have a direct recorded result."
        },
        {
          "id": "CROSS_CELL_COMPOSITION",
          "label": "Cross-cell composition",
          "status": "PARTIALLY_CERTIFIED",
          "basis": "2/7 required interfaces are certified; unassessed joins are missing work, not incompatibility results."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "label": "Prediction derivation",
          "status": "NOT_EVALUABLE",
          "basis": "An end-to-end prediction test is premature until the required cross-cell joins are registered."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "label": "Observable identification",
          "status": "NOT_REGISTERED",
          "basis": "No assembly-level map from formal quantities to measured observables is registered."
        },
        {
          "id": "NUMERICAL_REPRODUCIBILITY",
          "label": "Numerical reproducibility",
          "status": "NO_RECORDS",
          "basis": "No independent numerical reproduction record is registered for this assembly."
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
      "label": "Constructive and computable physics tradition",
      "short_label": "Constructive / computable",
      "camp_kind": "METHODOLOGICAL_TRADITION",
      "camp_summary": "Constructive and computable approaches require existence claims to carry witnesses, algorithms, convergence data, or other operational mathematical content.",
      "central_question": "Which parts of a physical theory can actually be constructed or computed from represented inputs?",
      "lineage": [
        "Bishop-style constructivism",
        "computable analysis",
        "proof mining and represented spaces"
      ],
      "signature_ideas": [
        "witness-producing existence",
        "algorithms with represented inputs",
        "explicit rates and error control"
      ],
      "atlas_window": "All carrier types under the constructive/computable regime.",
      "scope_note": "Computability depends on representation, and a constructive upper bound is not automatically a reverse-mathematical necessity result.",
      "aim": "Track which parts of a predictive theory can be supplied with witnesses, algorithms, and controlled approximation data.",
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
          "carrier": "HILBERT_OPERATOR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "ANOMALY_CLASSIFICATION",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "HILBERT_OPERATOR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1": "DIRECT_LOCAL"
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
          "carrier": "HILBERT_OPERATOR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1": "DIRECT_LOCAL"
          },
          "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order."
        },
        {
          "obligation": "RESIDUAL_QUANTUM_TRANSFER",
          "foundation": "CONSTRUCTIVE_COMPUTABLE",
          "carrier": "HILBERT_OPERATOR",
          "status": "LOCAL_RESULT",
          "evidence": [
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1"
          ],
          "evidence_roles": {
            "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1": "DIRECT_LOCAL"
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
      "maturity_rails": [
        {
          "id": "OBLIGATION_COVERAGE",
          "label": "Obligation coverage",
          "status": "OPEN",
          "basis": "12/16 obligations have a direct recorded result."
        },
        {
          "id": "CROSS_CELL_COMPOSITION",
          "label": "Cross-cell composition",
          "status": "NOT_ASSESSED",
          "basis": "0/7 required interfaces are certified; unassessed joins are missing work, not incompatibility results."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "label": "Prediction derivation",
          "status": "NOT_EVALUABLE",
          "basis": "An end-to-end prediction test is premature until the required cross-cell joins are registered."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "label": "Observable identification",
          "status": "NOT_REGISTERED",
          "basis": "No assembly-level map from formal quantities to measured observables is registered."
        },
        {
          "id": "NUMERICAL_REPRODUCIBILITY",
          "label": "Numerical reproducibility",
          "status": "NO_RECORDS",
          "basis": "No independent numerical reproduction record is registered for this assembly."
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
      "label": "Topos and internal quantum-foundations tradition",
      "short_label": "Topos / internal",
      "camp_kind": "RESEARCH_TRADITION",
      "camp_summary": "Topos approaches reformulate spaces, observables, and truth inside an alternative logical universe where propositions may be contextual or local rather than globally Boolean.",
      "central_question": "What changes when the logical universe of the theory is altered instead of merely changing an equation inside ordinary set theory?",
      "lineage": [
        "Isham–Butterfield contextual logic",
        "Döring–Isham topos quantum theory",
        "Heunen–Landsman–Spitters internal algebra"
      ],
      "signature_ideas": [
        "contextual truth values",
        "point-free or internal spaces",
        "intuitionistic logic"
      ],
      "atlas_window": "All carrier types interpreted under the topos/internal regime.",
      "scope_note": "This is a family of non-equivalent approaches; one internal construction does not transfer automatically to every topos or recover empirical quantum theory.",
      "aim": "Map what can be formulated inside alternative logical and geometric universes and which bridges back to ordinary predictions remain open.",
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
      "maturity_rails": [
        {
          "id": "OBLIGATION_COVERAGE",
          "label": "Obligation coverage",
          "status": "OPEN",
          "basis": "9/16 obligations have a direct recorded result."
        },
        {
          "id": "CROSS_CELL_COMPOSITION",
          "label": "Cross-cell composition",
          "status": "NOT_ASSESSED",
          "basis": "0/7 required interfaces are certified; unassessed joins are missing work, not incompatibility results."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "label": "Prediction derivation",
          "status": "NOT_EVALUABLE",
          "basis": "An end-to-end prediction test is premature until the required cross-cell joins are registered."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "label": "Observable identification",
          "status": "NOT_REGISTERED",
          "basis": "No assembly-level map from formal quantities to measured observables is registered."
        },
        {
          "id": "NUMERICAL_REPRODUCIBILITY",
          "label": "Numerical reproducibility",
          "status": "NO_RECORDS",
          "basis": "No independent numerical reproduction record is registered for this assembly."
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
  "model_scoped_assemblies": [
    {
      "schema_version": "foundational-gr-cassini-model-assembly-v1",
      "result_id": "FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1",
      "result_kind": "MODEL_SCOPED_END_TO_END_PREDICTION_ASSEMBLY",
      "lifecycle": "MODEL_SCOPED_EMPIRICAL_COMPARISON_REGISTERED",
      "created": "2026-08-14",
      "repository_base_commit": "be5b23b72ea73f6b5dd099e9a3bd3126e6778922",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC",
        "LORENTZIAN-CAUSAL"
      ],
      "title": "Standard GR solar-system prediction assembly: field equations to Cassini",
      "model_identity": {
        "id": "STANDARD_GR_VACUUM_SOLAR_EXTERIOR",
        "theory": "Four-dimensional standard general relativity",
        "sector": "Static, spherically symmetric, asymptotically flat vacuum exterior of the Sun",
        "field_equations": "G_mu_nu=0 with Lambda=0 outside the source",
        "matter_coupling": "Radio photons are minimally coupled and follow null geodesics of the same metric",
        "approximation": "Exact exterior solution followed by a first post-Newtonian expansion for the observable map",
        "benchmark": "SOLAR_SYSTEM",
        "comparison_id": "GR_CASSINI_SHAPIRO_2003"
      },
      "applicability_mask": [
        {
          "obligation": "KINEMATICS_OBSERVABLES",
          "status": "IN_SCOPE_REQUIRED",
          "reason": "The metric, null paths, PPN gamma, and radio time/frequency response are the declared configurations and observables."
        },
        {
          "obligation": "STATE_EXISTENCE",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "STATE_REPRESENTATION",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "PROBABILITY_RULE",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "PHYSICAL_STATE_SELECTION",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "EVOLUTION_WELLPOSEDNESS",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "CAUSAL_PROPAGATION_GREEN",
          "status": "TOUCHED_NOT_REQUIRED",
          "reason": "A null-geodesic propagation law is used, but no retarded/advanced Green operator or Cauchy-support theorem is required or established."
        },
        {
          "obligation": "GAUGE_BV_COHOMOLOGY",
          "status": "TOUCHED_NOT_REQUIRED",
          "reason": "Areal and isotropic coordinate gauges are related exactly, but no BV complex or gauge cohomology is required or established."
        },
        {
          "obligation": "INTERACTION_CONSTRUCTION",
          "status": "IN_SCOPE_REQUIRED",
          "reason": "The nonlinear Einstein vacuum field equation and its exact Schwarzschild exterior solution define the gravitational model used by the prediction."
        },
        {
          "obligation": "COUNTERTERM_CLASSIFICATION",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "ANOMALY_CLASSIFICATION",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "RENORMALIZED_PRODUCTS",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "QME_RESTORATION",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "RESIDUAL_QUANTUM_TRANSFER",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded classical static prediction does not require this quantum, state-selection, spectral, Cauchy-evolution, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "RECONSTRUCTION_LIMITS",
          "status": "IN_SCOPE_REQUIRED",
          "reason": "The isotropic weak-field map identifies the formal metric coefficient with the operational PPN gamma fitted by Cassini."
        }
      ],
      "applicability_summary": {
        "total_atlas_obligations": 16,
        "required": 3,
        "required_satisfied": 3,
        "touched_not_required": 2,
        "out_of_scope": 11
      },
      "shared_object_ledger": [
        {
          "id": "MODEL",
          "object": "STANDARD_GR_VACUUM_SOLAR_EXTERIOR",
          "used_by": [
            "FIELD_EQUATIONS",
            "EXTERIOR_SOLUTION",
            "PPN_REDUCTION",
            "NULL_OBSERVABLE"
          ],
          "identity_status": "IDENTICAL_MODEL"
        },
        {
          "id": "MASS_M",
          "object": "m=G M_sun in c=1 units",
          "used_by": [
            "EXTERIOR_SOLUTION",
            "PPN_REDUCTION",
            "NULL_OBSERVABLE"
          ],
          "identity_status": "IDENTICAL_PARAMETER"
        },
        {
          "id": "PPN_GAMMA",
          "object": "the spatial-curvature parameter gamma",
          "used_by": [
            "PPN_REDUCTION",
            "NULL_OBSERVABLE",
            "CASSINI_PARAMETER_MAP",
            "EMPIRICAL_COMPARISON"
          ],
          "identity_status": "EXACT_TO_OPERATIONAL_TRANSLATION"
        },
        {
          "id": "RADIO_NULL_SIGNAL",
          "object": "Cassini radio photons near solar conjunction",
          "used_by": [
            "NULL_OBSERVABLE",
            "CASSINI_PARAMETER_MAP"
          ],
          "identity_status": "CONDITIONAL_OPERATIONAL_IDENTIFICATION"
        }
      ],
      "stages": [
        {
          "id": "FIELD_EQUATIONS",
          "label": "Vacuum Einstein equations",
          "status": "CERTIFIED_EXACT",
          "establishes": "The declared model uses G_mu_nu=0 in the exterior sector."
        },
        {
          "id": "EXTERIOR_SOLUTION",
          "label": "Static spherical exterior",
          "status": "CERTIFIED_EXACT",
          "establishes": "The field equations integrate to f(r)=1-2m/r under the declared boundary normalization."
        },
        {
          "id": "PPN_REDUCTION",
          "label": "Isotropic weak-field reduction",
          "status": "CERTIFIED_EXACT",
          "establishes": "Exact coordinate translation and formal series give beta=gamma=1."
        },
        {
          "id": "NULL_OBSERVABLE",
          "label": "Null-delay observable",
          "status": "CERTIFIED_EXACT",
          "establishes": "The first-order delay coefficient is 1+gamma=2."
        },
        {
          "id": "CASSINI_PARAMETER_MAP",
          "label": "Cassini fitted parameter",
          "status": "LITERATURE_SCOPED",
          "establishes": "The publisher abstract identifies bending/delay and the measured frequency shift with gamma+1."
        },
        {
          "id": "EMPIRICAL_COMPARISON",
          "label": "Published Cassini comparison",
          "status": "SUPPORTED_REPORTED_BAND",
          "establishes": "The exact prediction gamma-1=0 lies inside the displayed reported plus-minus band."
        }
      ],
      "interfaces": [
        {
          "id": "FIELD_EQUATION_TO_SOLUTION",
          "from": "FIELD_EQUATIONS",
          "to": "EXTERIOR_SOLUTION",
          "relation": "EXACT_DERIVATION",
          "status": "CERTIFIED",
          "basis": "The reduced Einstein equation is an exact first-order ODE and the angular residual vanishes after substitution."
        },
        {
          "id": "SOLUTION_TO_PPN",
          "from": "EXTERIOR_SOLUTION",
          "to": "PPN_REDUCTION",
          "relation": "EXACT_TRANSLATION",
          "status": "CERTIFIED",
          "basis": "The areal-to-isotropic coordinate map is exact and the series coefficients are rational."
        },
        {
          "id": "PPN_TO_NULL_DELAY",
          "from": "PPN_REDUCTION",
          "to": "NULL_OBSERVABLE",
          "relation": "EXACT_ASYMPTOTIC_DERIVATION",
          "status": "CERTIFIED",
          "basis": "The Lorentzian null condition fixes the first-order coefficient 1+gamma."
        },
        {
          "id": "NULL_DELAY_TO_CASSINI_PARAMETER",
          "from": "NULL_OBSERVABLE",
          "to": "CASSINI_PARAMETER_MAP",
          "relation": "CONDITIONAL_OPERATIONAL_BRIDGE",
          "status": "REGISTERED",
          "basis": "Assumes minimally coupled radio photons follow metric null geodesics and imports the experiment's identification of its fitted gamma parameter."
        },
        {
          "id": "PREDICTION_TO_REPORTED_ESTIMATE",
          "from": "CASSINI_PARAMETER_MAP",
          "to": "EMPIRICAL_COMPARISON",
          "relation": "LITERATURE_SCOPED_COMPARISON",
          "status": "REGISTERED",
          "basis": "Compares the exact theoretical value only with the publisher's displayed estimate; no raw-data or likelihood reconstruction is claimed."
        }
      ],
      "exact_prediction_rail": {
        "arithmetic": "EXACT_RATIONAL_AND_FORMAL_SERIES",
        "conventions": {
          "dimension": 4,
          "signature": "(-,+,+,+)",
          "units": "c=1",
          "mass_length": "m=G M_sun",
          "weak_field_variable": "x=m/rho"
        },
        "field_equation_derivation": {
          "starting_equations": "G_mu_nu=0 in the vacuum exterior; Lambda=0",
          "ansatz": "ds^2=-f(r)dt^2+f(r)^(-1)dr^2+r^2 dOmega^2",
          "independent_equations": [
            "G^t_t=G^r_r=(r f'(r)+f(r)-1)/r^2=0",
            "G^theta_theta=G^phi_phi=f'(r)/r+f''(r)/2=0"
          ],
          "integration": "(r f)'=1, hence f=1+C/r; Newtonian normalization fixes C=-2m",
          "solution": "f(r)=1-2m/r",
          "substitution_residuals": {
            "r_fprime_plus_f_minus_1": {
              "numerator": 0,
              "denominator": 1
            },
            "fprime_over_r_plus_half_fsecond": {
              "numerator": 0,
              "denominator": 1
            }
          },
          "scope": "Exact within the static, spherically symmetric, asymptotically flat vacuum ansatz."
        },
        "isotropic_translation": {
          "coordinate_map": "r=rho(1+m/(2rho))^2=rho(1+x/2)^2",
          "lapse_factor": "A(x)=((1-x/2)/(1+x/2))^2",
          "spatial_factor": "B(x)=(1+x/2)^4",
          "coordinate_identity": "(dr/drho)^2/A=B and r^2=rho^2 B",
          "A_coefficients_through_x2": [
            {
              "numerator": 1,
              "denominator": 1
            },
            {
              "numerator": -2,
              "denominator": 1
            },
            {
              "numerator": 2,
              "denominator": 1
            }
          ],
          "B_coefficients_through_x2": [
            {
              "numerator": 1,
              "denominator": 1
            },
            {
              "numerator": 2,
              "denominator": 1
            },
            {
              "numerator": 3,
              "denominator": 2
            }
          ],
          "gtt_coefficients_through_x2": [
            {
              "numerator": -1,
              "denominator": 1
            },
            {
              "numerator": 2,
              "denominator": 1
            },
            {
              "numerator": -2,
              "denominator": 1
            }
          ]
        },
        "ppn_identification": {
          "template": "g_tt=-1+2U-2 beta U^2+O(U^3); g_ij=(1+2 gamma U+O(U^2))delta_ij",
          "potential_identification": "U=x=m/rho",
          "beta": {
            "numerator": 1,
            "denominator": 1
          },
          "gamma": {
            "numerator": 1,
            "denominator": 1
          },
          "gamma_minus_one": {
            "numerator": 0,
            "denominator": 1
          }
        },
        "null_delay": {
          "null_condition": "dt/dl=sqrt(B/A)=1+(1+gamma)U+O(U^2)",
          "sqrt_B_over_A_coefficients_through_x2": [
            {
              "numerator": 1,
              "denominator": 1
            },
            {
              "numerator": 2,
              "denominator": 1
            },
            {
              "numerator": 7,
              "denominator": 4
            }
          ],
          "first_order_delay_coefficient": {
            "numerator": 2,
            "denominator": 1
          },
          "one_way_excess": "Delta t=(1+gamma)m[asinh(z_receiver/b)+asinh(z_emitter/b)]+O(m^2)",
          "observable_parameter": "gamma+1"
        }
      },
      "empirical_comparison_rail": {
        "type": "IMPORTED_REPORTED_ESTIMATE_WITH_EXACT_ARITHMETIC_COMPARISON",
        "source_record_id": "GR_CASSINI_SHAPIRO_2003",
        "citation": "B. Bertotti, L. Iess, and P. Tortora, A test of general relativity using radio links with the Cassini spacecraft, Nature 425, 374-376 (2003).",
        "stable_url": "https://doi.org/10.1038/nature01997",
        "publisher_reported_expression": "gamma=1+(2.1+/-2.3)e-5",
        "reported_gamma_minus_one": {
          "numerator": 21,
          "denominator": 1000000
        },
        "reported_plus_minus_uncertainty": {
          "numerator": 23,
          "denominator": 1000000
        },
        "reported_band": {
          "lower": {
            "numerator": -1,
            "denominator": 500000
          },
          "upper": {
            "numerator": 11,
            "denominator": 250000
          }
        },
        "exact_prediction_gamma_minus_one": {
          "numerator": 0,
          "denominator": 1
        },
        "prediction_inside_reported_band": true,
        "absolute_standardized_distance": {
          "numerator": 21,
          "denominator": 23
        },
        "comparison_status": "SUPPORTED_WITHIN_REPORTED_PLUS_MINUS_BAND",
        "data_lifecycle": "LITERATURE_TRANSCRIPTION_NOT_RAW_DATA_REANALYSIS",
        "boundary": "The arithmetic comparison is exact after transcription. The spacecraft data reduction, plasma correction, covariance model, and likelihood are imported from the paper and are not reproduced."
      },
      "maturity_rails": [
        {
          "id": "MODEL_IDENTITY",
          "status": "SATISFIED",
          "basis": "Every exact stage uses the same declared standard-GR solar-exterior model and mass parameter."
        },
        {
          "id": "APPLICABILITY",
          "status": "SATISFIED",
          "basis": "All 3 obligations required by this bounded prediction are satisfied; other obligations are explicitly masked."
        },
        {
          "id": "CROSS_STAGE_COMPOSITION",
          "status": "SATISFIED_WITH_TYPED_BOUNDARY",
          "basis": "All 5 joins are registered: 3 exact and 2 literature-scoped operational/comparison joins."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "status": "SATISFIED",
          "basis": "The exact field-equation, coordinate, PPN, and null-condition chain gives gamma=1 and gamma+1=2."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "status": "SATISFIED_WITH_TYPED_BOUNDARY",
          "basis": "The fitted Cassini gamma is connected to the null-delay coefficient under the declared photon-coupling and experimental-model assumptions."
        },
        {
          "id": "EMPIRICAL_COMPARISON",
          "status": "SUPPORTED_IN_DECLARED_SCOPE",
          "basis": "gamma-1=0 lies in the publisher's displayed (2.1+/-2.3)e-5 band."
        },
        {
          "id": "ROBUSTNESS_OUT_OF_SAMPLE",
          "status": "NOT_ASSESSED",
          "basis": "No second solar-system dataset or held-out comparison is included in this assembly."
        }
      ],
      "assembly_disposition": {
        "status": "BOUNDED_PREDICTION_ASSEMBLY_COMPLETE",
        "complete_within_declared_scope": true,
        "empirically_supported_within_declared_scope": true,
        "complete_theory": false
      },
      "provenance": {
        "inputs": [
          {
            "path": "reverse_physics/certificates/REVERSE_PHYSICS_EINSTEIN_CLASSIFICATION_V1.json",
            "sha256": "2d833db3fd07390c75f0693fba124f86d83910a93a650e688f2cbe7bac1482f3",
            "role": "local exact D=4 Einstein field-equation classification and Schwarzschild vacuum control"
          },
          {
            "path": "foundations/standard-gr-observational-control-v1.json",
            "sha256": "b65311888e0852aaf36ae9f95568e0b9aaeeb97758752eeffd02e4ba1d0b26e7",
            "role": "typed Cassini primary-source comparison record"
          }
        ],
        "remote_source": {
          "locator": "https://doi.org/10.1038/nature01997",
          "artifact_status": "PUBLISHER_METADATA_LIVE_SOURCE",
          "retrieved": "2026-08-14",
          "reported_fact": "gamma=1+(2.1+/-2.3)e-5 and bending/delay proportional to gamma+1",
          "pinning_boundary": "The evolving publisher HTML is not treated as a stable byte artifact; the local typed control ledger is the content-addressed transcription authority."
        }
      },
      "independent_checker": {
        "path": "foundations/check_gr_cassini_assembly.py",
        "method": "Direct rational coefficient identities, ODE residual checks, source-pin closure, applicability closure, and comparison-band arithmetic; it does not reuse the producer's series routines."
      },
      "claim_flags": {
        "single_model_identity_declared": true,
        "applicability_mask_complete": true,
        "vacuum_field_equation_to_solution_derived": true,
        "isotropic_coordinate_translation_exact": true,
        "ppn_gamma_equals_one_derived_exactly": true,
        "null_delay_gamma_plus_one_coefficient_derived": true,
        "cassini_observable_map_registered": true,
        "prediction_inside_reported_band": true,
        "bounded_prediction_assembly_complete": true,
        "raw_cassini_data_reanalysed": false,
        "cassini_likelihood_reproduced": false,
        "robustness_out_of_sample_assessed": false,
        "all_solar_system_tests_covered": false,
        "complete_standard_gr_theory_established": false,
        "weyl_gravity_empirically_supported": false,
        "quantum_lifecycle_promoted": false
      },
      "does_not_establish": [
        "the Einstein equations outside the declared four-dimensional local metric and vacuum exterior assumptions",
        "solar interior structure, multipoles, rotation, plasma physics, spacecraft dynamics, or the Cassini data-reduction pipeline",
        "a retarded or advanced Green operator, full Cauchy well-posedness theorem, or BV gauge construction",
        "reproduction of the Cassini likelihood, covariance analysis, or systematic-error budget",
        "robustness against a second or held-out solar-system dataset",
        "agreement of standard GR in the other five benchmark families",
        "a complete classical, quantum, cosmological, or ultraviolet theory",
        "any empirical support for Mannheim--Kazanas or another Weyl-gravity model"
      ],
      "human_report": "foundations/reports/gr-cassini-model-assembly-v1.md",
      "canonical_digest": "bdbe75d140525fa6b1a83c4ca1d5ca9298fb9ce2cbf5322e32869361ee4f2603"
    },
    {
      "schema_version": "foundational-mannheim-ngc3198-model-assembly-v1",
      "result_id": "FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1",
      "result_kind": "MODEL_SCOPED_PREDICTION_AND_CROSS_DATASET_ASSEMBLY",
      "lifecycle": "NUMERICAL_REPRODUCTION_WITH_MIXED_EMPIRICAL_COMPARISON",
      "created": "2026-08-14",
      "repository_base_commit": "a1980849c6e7c18802a0392cc21c9f3da199f9d3",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC"
      ],
      "title": "Mannheim conformal-gravity NGC 3198 assembly: field equation to rotation curve",
      "model_identity": {
        "id": "MANNHEIM_OBRIEN_NGC3198_THIN_DISK",
        "theory": "Four-dimensional pure metric conformal gravity in the Mannheim--Kazanas phenomenological branch",
        "sector": "Static weak-field circular motion for the NGC 3198 stellar and gas disks",
        "field_equations": "B_mu_nu=0 in the exterior, with published thin-disk convolution and global gamma_0/kappa terms",
        "matter_coupling": "Massive tracers are assumed to respond to the displayed metric; the macroscopic-versus-microscopic scalar dispute is not resolved",
        "approximation": "Leading weak field, infinitesimally thin exponential stellar and gas disks, gas scale length 4 R0, no bulge",
        "benchmark": "GALACTIC_DYNAMICS",
        "comparison_id": "MANNHEIM_OBRIEN_2012_NGC3198_AND_SPARC_2016"
      },
      "applicability_mask": [
        {
          "obligation": "KINEMATICS_OBSERVABLES",
          "status": "IN_SCOPE_REQUIRED",
          "reason": "The static metric, circular speed, disk light/mass model, and measured rotation curve are the declared configurations and observables."
        },
        {
          "obligation": "STATE_EXISTENCE",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded static classical comparison does not require this state, quantum, spectral, Cauchy, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "STATE_REPRESENTATION",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded static classical comparison does not require this state, quantum, spectral, Cauchy, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "PROBABILITY_RULE",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded static classical comparison does not require this state, quantum, spectral, Cauchy, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "PHYSICAL_STATE_SELECTION",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded static classical comparison does not require this state, quantum, spectral, Cauchy, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded static classical comparison does not require this state, quantum, spectral, Cauchy, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "EVOLUTION_WELLPOSEDNESS",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded static classical comparison does not require this state, quantum, spectral, Cauchy, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "CAUSAL_PROPAGATION_GREEN",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded static classical comparison does not require this state, quantum, spectral, Cauchy, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "GAUGE_BV_COHOMOLOGY",
          "status": "TOUCHED_NOT_REQUIRED",
          "reason": "The exact predecessor uses a conformal and radial gauge, but no BV complex or gauge cohomology is required or established."
        },
        {
          "obligation": "INTERACTION_CONSTRUCTION",
          "status": "IN_SCOPE_REQUIRED",
          "reason": "The nonlinear Bach equation and its static spherical vacuum family define the gravitational model feeding the weak-field prediction."
        },
        {
          "obligation": "COUNTERTERM_CLASSIFICATION",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded static classical comparison does not require this state, quantum, spectral, Cauchy, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "ANOMALY_CLASSIFICATION",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded static classical comparison does not require this state, quantum, spectral, Cauchy, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "RENORMALIZED_PRODUCTS",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded static classical comparison does not require this state, quantum, spectral, Cauchy, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "QME_RESTORATION",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded static classical comparison does not require this state, quantum, spectral, Cauchy, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "RESIDUAL_QUANTUM_TRANSFER",
          "status": "OUT_OF_SCOPE",
          "reason": "This bounded static classical comparison does not require this state, quantum, spectral, Cauchy, renormalization, or residual-transfer obligation."
        },
        {
          "obligation": "RECONSTRUCTION_LIMITS",
          "status": "IN_SCOPE_REQUIRED",
          "reason": "The weak-field circular-orbit and disk integrations connect the metric coefficients to the observed velocity-radius curve."
        }
      ],
      "applicability_summary": {
        "total_atlas_obligations": 16,
        "required": 3,
        "required_satisfied": 3,
        "touched_not_required": 1,
        "out_of_scope": 12
      },
      "stages": [
        {
          "id": "WEYL_FIELD_EQUATION",
          "label": "Weyl action and Bach equation",
          "status": "DECLARED_MODEL_INPUT",
          "establishes": "The classical model is four-dimensional pure metric conformal gravity with Bach equation B_mu_nu=0 in the exterior."
        },
        {
          "id": "STATIC_VACUUM_FAMILY",
          "label": "Mannheim--Kazanas vacuum family",
          "status": "CERTIFIED_LOCAL_PREDECESSOR",
          "establishes": "The local BH0B certificate derives the complete static spherical Bach-flat family in the declared conformal gauge."
        },
        {
          "id": "CIRCULAR_ORBIT_LAW",
          "label": "Weak-field circular-orbit law",
          "status": "CERTIFIED_LOCAL_PREDECESSOR",
          "establishes": "The local BH0C certificate derives the leading weak-field beta/r + gamma r/2 - k r^2 circular-speed law and records its exact-family correction."
        },
        {
          "id": "EXPONENTIAL_DISK_MODEL",
          "label": "Luminous exponential-disk prediction",
          "status": "PUBLISHED_MODEL_TRANSCRIPTION",
          "establishes": "Mannheim--O'Brien Eqs. (5) and (20) integrate the Newtonian and linear kernels over thin stellar and gas disks and add universal linear and quadratic terms."
        },
        {
          "id": "NGC3198_PARAMETER_ROW",
          "label": "Published NGC 3198 parameters",
          "status": "CONTENT_PINNED_TRANSCRIPTION",
          "establishes": "The model uses the paper's distance, scale length, stellar and HI masses, fitted M/L, endpoint radius, and fixed universal constants without refitting."
        },
        {
          "id": "PUBLISHED_ENDPOINT",
          "label": "Published endpoint reproduction",
          "status": "COARSE_NUMERICAL_REPRODUCTION",
          "establishes": "Independent evaluation of the displayed equations predicts the endpoint velocity within the declared five-percent coarse gate of the velocity reconstructed from the paper's endpoint acceleration."
        },
        {
          "id": "SPARC_CROSS_DATASET",
          "label": "Independent SPARC curve comparison",
          "status": "MIXED_RANDOM_ERROR_GATE_FAILED",
          "establishes": "Without refitting, the curve passes the declared five km/s RMS shape gate but fails the reduced-chi-squared gate based on SPARC random errors alone."
        }
      ],
      "interfaces": [
        {
          "id": "ACTION_TO_BACH",
          "from": "WEYL_FIELD_EQUATION",
          "to": "STATIC_VACUUM_FAMILY",
          "relation": "DECLARED_THEORY_TO_CERTIFIED_SECTOR",
          "status": "CERTIFIED_WITH_SCOPE",
          "basis": "BH0B verifies the static spherical exterior classification in conformal gauge, not the full matter-coupled theory."
        },
        {
          "id": "VACUUM_TO_ORBIT",
          "from": "STATIC_VACUUM_FAMILY",
          "to": "CIRCULAR_ORBIT_LAW",
          "relation": "EXACT_TO_LEADING_WEAK_FIELD",
          "status": "CERTIFIED_WITH_SCOPE",
          "basis": "BH0C derives the orbit law and explicitly records the O(beta gamma) correction from the exact Bach-flat family."
        },
        {
          "id": "ORBIT_TO_DISK",
          "from": "CIRCULAR_ORBIT_LAW",
          "to": "EXPONENTIAL_DISK_MODEL",
          "relation": "PUBLISHED_THIN_DISK_INTEGRATION",
          "status": "REGISTERED",
          "basis": "Imports the paper's thin exponential stellar/gas geometry and Bessel-kernel integration; it does not solve a galactic interior matter sector."
        },
        {
          "id": "DISK_TO_PARAMETERS",
          "from": "EXPONENTIAL_DISK_MODEL",
          "to": "NGC3198_PARAMETER_ROW",
          "relation": "PUBLISHED_FIT_PARAMETER_INSTANTIATION",
          "status": "REGISTERED",
          "basis": "The reported stellar mass-to-light ratio is a fitted input; all other displayed parameters are transcribed as fixed model/data inputs."
        },
        {
          "id": "PARAMETERS_TO_ENDPOINT",
          "from": "NGC3198_PARAMETER_ROW",
          "to": "PUBLISHED_ENDPOINT",
          "relation": "INDEPENDENT_NUMERICAL_EVALUATION",
          "status": "CERTIFIED_NUMERIC",
          "basis": "The producer evaluates Bessel integrals directly and the checker uses std::cyl_bessel_i/k; agreement is tested independently."
        },
        {
          "id": "ENDPOINT_TO_SPARC",
          "from": "PUBLISHED_ENDPOINT",
          "to": "SPARC_CROSS_DATASET",
          "relation": "NONIDENTICAL_DATASET_COMPARISON",
          "status": "REGISTERED_WITH_WARNING",
          "basis": "SPARC observations are from the same galaxy and observational lineage but a later, non-identical photometric/data reduction; no empirical support is transferred automatically."
        }
      ],
      "published_parameter_rail": {
        "source": {
          "citation": "P. D. Mannheim and J. G. O'Brien, Fitting galactic rotation curves with conformal gravity and a global quadratic potential, Phys. Rev. D 85 (2012) 124020",
          "arxiv": "https://arxiv.org/abs/1011.3495",
          "source_archive": "https://export.arxiv.org/e-print/1011.3495",
          "source_archive_sha256": "e366db37bc99ce08c96609f751d9b0ffb779dd4ce1c0140a2e226c1aefc075c1",
          "source_member": "fitting5.tex",
          "parameter_table": "Table 1, NGC 3198 row",
          "equations": [
            "(5)",
            "(20)"
          ],
          "retrieved": "2026-08-14"
        },
        "constants_cgs": {
          "beta_star_cm": "1.48e5",
          "gamma_star_per_cm": "5.42e-41",
          "gamma_0_per_cm": "3.06e-30",
          "kappa_per_cm2": "9.54e-54",
          "speed_of_light_cm_per_s": "2.99792458e10",
          "kpc_cm": "3.0856775814913673e21"
        },
        "ngc3198_row": {
          "distance_mpc": "14.1",
          "blue_luminosity_1e10_solar": "3.241",
          "stellar_scale_length_kpc": "4.0",
          "last_radius_kpc": "38.6",
          "hi_mass_1e10_solar": "1.06",
          "stellar_disk_mass_1e10_solar": "3.644",
          "stellar_mass_to_blue_light": "1.12",
          "observed_last_v2_over_c2r_1e30_per_cm": "2.09"
        },
        "modelling_assumptions": {
          "stellar_geometry": "infinitesimally thin exponential disk",
          "gas_geometry": "infinitesimally thin exponential disk with scale length four times the optical scale length",
          "gas_helium_multiplier": "1.4",
          "bulge": "none for NGC 3198",
          "free_parameter": "stellar mass-to-blue-light ratio; the table reports the fitted value 1.12",
          "universal_parameters": "beta_star, gamma_star, gamma_0, and kappa are held fixed at the published values"
        },
        "parameter_fit_scope": "The stellar M/L=1.12 is imported from the published fit; this assembly performs no fit."
      },
      "numerical_reproduction_rail": {
        "arithmetic": "BINARY64_NUMERIC_DISTINCT_FROM_EXACT_LOCAL_PREDECESSORS",
        "producer_method": "I_0/I_1 power series and K_0/K_1 integral definitions with 4096-panel composite Simpson quadrature",
        "independent_method": "C++17 std::cyl_bessel_i and std::cyl_bessel_k",
        "published_last_radius_kpc": 38.6,
        "published_observed_endpoint_acceleration_per_cm": 2.09e-30,
        "observed_endpoint_velocity_reconstructed_km_s": 149.5762947830398,
        "predicted_endpoint": {
          "radius_kpc": 38.6,
          "velocity_km_s": 153.90402121008415,
          "v2_over_c2r_per_cm": 2.2126905381295745e-30,
          "components_v2_km2_s2": {
            "stellar_newtonian": 4328.92141015455,
            "stellar_linear": 10392.09897333534,
            "gas_newtonian": 1533.9591136164609,
            "gas_linear": 3216.791759864909,
            "global_linear": 16378.37032553345,
            "global_quadratic": -12163.693837870676
          }
        },
        "producer_refinement_absolute_velocity_difference_km_s": 0.0,
        "endpoint_residual_km_s": 4.327726427044354,
        "endpoint_relative_velocity_residual": 0.02893323727079692,
        "declared_relative_gate": 0.05,
        "gate_passed": true,
        "status": "COARSE_ENDPOINT_REPRODUCED",
        "boundary": "The table endpoint carries no pointwise uncertainty and is not the full curve. The five-percent gate is an audit threshold chosen here, not a publisher confidence interval."
      },
      "empirical_comparison_rail": {
        "type": "NO_REFIT_NONIDENTICAL_SPARC_CROSS_DATASET_CHECK",
        "protocol": {
          "fit_performed": false,
          "radius_rescaling": "Multiply each SPARC radius by 14.1/13.8 to use the distance adopted in the published conformal-gravity fit",
          "velocity_rescaling": "None",
          "comparison_window": "Rescaled radius less than or equal to the published last radius 38.6 kpc",
          "uncertainty": "SPARC e_Vobs random errors only; inclination and other systematic uncertainties are not included",
          "coarse_rms_gate_km_per_s": "5.0",
          "random_error_reduced_chi2_gate": "2.0",
          "endpoint_relative_velocity_gate": "0.05"
        },
        "source": {
          "citation": "F. Lelli, S. S. McGaugh, and J. M. Schombert, SPARC: Mass Models for 175 Disk Galaxies with Spitzer Photometry and Accurate Rotation Curves, Astron. J. 152 (2016) 157",
          "url": "https://astroweb.case.edu/SPARC/MassModels_Lelli2016c.mrt",
          "full_source_sha256": "9108994b12cc401b94a1768beca61c53ec354779385c9c9cc571049f3043244c",
          "local_extract": "foundations/data/ngc3198-sparc-mass-model-v1.tsv",
          "selection": "All 43 rows whose fixed-width ID field is NGC3198, copied without numerical alteration",
          "retrieved": "2026-08-14"
        },
        "points_total_source": 43,
        "points_inside_published_radius": 39,
        "points": [
          {
            "source_radius_kpc": 0.32,
            "rescaled_radius_kpc": 0.32695652173913037,
            "observed_velocity_km_s": 24.4,
            "random_error_km_s": 35.9,
            "predicted_velocity_km_s": 22.695284849168115,
            "residual_km_s": -1.704715150831884,
            "standardized_residual": -0.04748510169448145
          },
          {
            "source_radius_kpc": 0.64,
            "rescaled_radius_kpc": 0.6539130434782607,
            "observed_velocity_km_s": 43.3,
            "random_error_km_s": 16.3,
            "predicted_velocity_km_s": 37.71262210737579,
            "residual_km_s": -5.587377892624204,
            "standardized_residual": -0.3427839197928959
          },
          {
            "source_radius_kpc": 0.96,
            "rescaled_radius_kpc": 0.9808695652173912,
            "observed_velocity_km_s": 45.5,
            "random_error_km_s": 16.1,
            "predicted_velocity_km_s": 50.26965048714948,
            "residual_km_s": 4.769650487149477,
            "standardized_residual": 0.2962515830527625
          },
          {
            "source_radius_kpc": 1.28,
            "rescaled_radius_kpc": 1.3078260869565215,
            "observed_velocity_km_s": 58.5,
            "random_error_km_s": 15.4,
            "predicted_velocity_km_s": 61.12273955986217,
            "residual_km_s": 2.6227395598621683,
            "standardized_residual": 0.1703077636274135
          },
          {
            "source_radius_kpc": 1.61,
            "rescaled_radius_kpc": 1.645,
            "observed_velocity_km_s": 68.8,
            "random_error_km_s": 7.61,
            "predicted_velocity_km_s": 70.92994886870265,
            "residual_km_s": 2.1299488687026553,
            "standardized_residual": 0.27988815620271423
          },
          {
            "source_radius_kpc": 1.93,
            "rescaled_radius_kpc": 1.9719565217391302,
            "observed_velocity_km_s": 76.9,
            "random_error_km_s": 10.3,
            "predicted_velocity_km_s": 79.33925448367964,
            "residual_km_s": 2.4392544836796333,
            "standardized_residual": 0.2368208236582168
          },
          {
            "source_radius_kpc": 2.24,
            "rescaled_radius_kpc": 2.2886956521739132,
            "observed_velocity_km_s": 82.0,
            "random_error_km_s": 8.09,
            "predicted_velocity_km_s": 86.61061492371104,
            "residual_km_s": 4.61061492371104,
            "standardized_residual": 0.5699153181348628
          },
          {
            "source_radius_kpc": 2.57,
            "rescaled_radius_kpc": 2.625869565217391,
            "observed_velocity_km_s": 86.9,
            "random_error_km_s": 7.6,
            "predicted_velocity_km_s": 93.53356046050949,
            "residual_km_s": 6.633560460509486,
            "standardized_residual": 0.8728369026986166
          },
          {
            "source_radius_kpc": 2.89,
            "rescaled_radius_kpc": 2.952826086956522,
            "observed_velocity_km_s": 97.6,
            "random_error_km_s": 3.03,
            "predicted_velocity_km_s": 99.54187558333885,
            "residual_km_s": 1.941875583338856,
            "standardized_residual": 0.6408830308049029
          },
          {
            "source_radius_kpc": 3.21,
            "rescaled_radius_kpc": 3.2797826086956516,
            "observed_velocity_km_s": 100.0,
            "random_error_km_s": 5.31,
            "predicted_velocity_km_s": 104.93767792995632,
            "residual_km_s": 4.9376779299563225,
            "standardized_residual": 0.9298828493326409
          },
          {
            "source_radius_kpc": 3.54,
            "rescaled_radius_kpc": 3.61695652173913,
            "observed_velocity_km_s": 107.0,
            "random_error_km_s": 7.51,
            "predicted_velocity_km_s": 109.93177621379725,
            "residual_km_s": 2.9317762137972494,
            "standardized_residual": 0.3903829845269307
          },
          {
            "source_radius_kpc": 3.85,
            "rescaled_radius_kpc": 3.933695652173913,
            "observed_velocity_km_s": 113.0,
            "random_error_km_s": 7.32,
            "predicted_velocity_km_s": 114.15122495736566,
            "residual_km_s": 1.151224957365656,
            "standardized_residual": 0.15727116903902405
          },
          {
            "source_radius_kpc": 4.17,
            "rescaled_radius_kpc": 4.260652173913043,
            "observed_velocity_km_s": 117.0,
            "random_error_km_s": 5.21,
            "predicted_velocity_km_s": 118.07597178121802,
            "residual_km_s": 1.0759717812180156,
            "standardized_residual": 0.2065204954353197
          },
          {
            "source_radius_kpc": 4.5,
            "rescaled_radius_kpc": 4.5978260869565215,
            "observed_velocity_km_s": 119.0,
            "random_error_km_s": 5.67,
            "predicted_velocity_km_s": 121.71030504955321,
            "residual_km_s": 2.710305049553213,
            "standardized_residual": 0.47800794524748025
          },
          {
            "source_radius_kpc": 4.82,
            "rescaled_radius_kpc": 4.9247826086956525,
            "observed_velocity_km_s": 127.0,
            "random_error_km_s": 5.39,
            "predicted_velocity_km_s": 124.87313039095174,
            "residual_km_s": -2.1268696090482564,
            "standardized_residual": -0.39459547477704204
          },
          {
            "source_radius_kpc": 5.15,
            "rescaled_radius_kpc": 5.261956521739131,
            "observed_velocity_km_s": 132.0,
            "random_error_km_s": 4.34,
            "predicted_velocity_km_s": 127.79831856541175,
            "residual_km_s": -4.201681434588252,
            "standardized_residual": -0.968129362808353
          },
          {
            "source_radius_kpc": 5.46,
            "rescaled_radius_kpc": 5.578695652173913,
            "observed_velocity_km_s": 134.0,
            "random_error_km_s": 2.36,
            "predicted_velocity_km_s": 130.26428954441386,
            "residual_km_s": -3.735710455586144,
            "standardized_residual": -1.5829281591466713
          },
          {
            "source_radius_kpc": 5.78,
            "rescaled_radius_kpc": 5.905652173913044,
            "observed_velocity_km_s": 137.0,
            "random_error_km_s": 0.89,
            "predicted_velocity_km_s": 132.55006014537616,
            "residual_km_s": -4.449939854623835,
            "standardized_residual": -4.999932420925657
          },
          {
            "source_radius_kpc": 6.1,
            "rescaled_radius_kpc": 6.232608695652173,
            "observed_velocity_km_s": 140.0,
            "random_error_km_s": 2.84,
            "predicted_velocity_km_s": 134.59619845925477,
            "residual_km_s": -5.403801540745235,
            "standardized_residual": -1.9027470213891673
          },
          {
            "source_radius_kpc": 6.43,
            "rescaled_radius_kpc": 6.569782608695651,
            "observed_velocity_km_s": 142.0,
            "random_error_km_s": 0.88,
            "predicted_velocity_km_s": 136.47875611873224,
            "residual_km_s": -5.521243881267765,
            "standardized_residual": -6.274140774167915
          },
          {
            "source_radius_kpc": 6.74,
            "rescaled_radius_kpc": 6.886521739130435,
            "observed_velocity_km_s": 144.0,
            "random_error_km_s": 1.23,
            "predicted_velocity_km_s": 138.0562628209297,
            "residual_km_s": -5.943737179070297,
            "standardized_residual": -4.832306649650648
          },
          {
            "source_radius_kpc": 7.06,
            "rescaled_radius_kpc": 7.2134782608695645,
            "observed_velocity_km_s": 146.0,
            "random_error_km_s": 1.57,
            "predicted_velocity_km_s": 139.50863277470748,
            "residual_km_s": -6.491367225292521,
            "standardized_residual": -4.134628805918803
          },
          {
            "source_radius_kpc": 8.04,
            "rescaled_radius_kpc": 8.214782608695652,
            "observed_velocity_km_s": 147.0,
            "random_error_km_s": 3.0,
            "predicted_velocity_km_s": 143.01044768437725,
            "residual_km_s": -3.9895523156227455,
            "standardized_residual": -1.3298507718742485
          },
          {
            "source_radius_kpc": 9.04,
            "rescaled_radius_kpc": 9.236521739130433,
            "observed_velocity_km_s": 148.0,
            "random_error_km_s": 3.0,
            "predicted_velocity_km_s": 145.4217740958412,
            "residual_km_s": -2.5782259041588134,
            "standardized_residual": -0.8594086347196045
          },
          {
            "source_radius_kpc": 10.04,
            "rescaled_radius_kpc": 10.258260869565216,
            "observed_velocity_km_s": 152.0,
            "random_error_km_s": 2.0,
            "predicted_velocity_km_s": 146.98181845017842,
            "residual_km_s": -5.018181549821577,
            "standardized_residual": -2.5090907749107885
          },
          {
            "source_radius_kpc": 11.04,
            "rescaled_radius_kpc": 11.28,
            "observed_velocity_km_s": 155.0,
            "random_error_km_s": 2.0,
            "predicted_velocity_km_s": 147.93769799904186,
            "residual_km_s": -7.062302000958141,
            "standardized_residual": -3.5311510004790705
          },
          {
            "source_radius_kpc": 12.05,
            "rescaled_radius_kpc": 12.31195652173913,
            "observed_velocity_km_s": 156.0,
            "random_error_km_s": 2.0,
            "predicted_velocity_km_s": 148.48067304063485,
            "residual_km_s": -7.519326959365145,
            "standardized_residual": -3.7596634796825725
          },
          {
            "source_radius_kpc": 14.05,
            "rescaled_radius_kpc": 14.355434782608697,
            "observed_velocity_km_s": 157.0,
            "random_error_km_s": 2.0,
            "predicted_velocity_km_s": 148.8342950027545,
            "residual_km_s": -8.165704997245513,
            "standardized_residual": -4.082852498622756
          },
          {
            "source_radius_kpc": 16.07,
            "rescaled_radius_kpc": 16.419347826086955,
            "observed_velocity_km_s": 153.0,
            "random_error_km_s": 2.0,
            "predicted_velocity_km_s": 148.7943158054567,
            "residual_km_s": -4.205684194543295,
            "standardized_residual": -2.1028420972716475
          },
          {
            "source_radius_kpc": 18.13,
            "rescaled_radius_kpc": 18.524130434782606,
            "observed_velocity_km_s": 153.0,
            "random_error_km_s": 2.0,
            "predicted_velocity_km_s": 148.7435126019058,
            "residual_km_s": -4.256487398094208,
            "standardized_residual": -2.128243699047104
          },
          {
            "source_radius_kpc": 20.05,
            "rescaled_radius_kpc": 20.48586956521739,
            "observed_velocity_km_s": 154.0,
            "random_error_km_s": 2.0,
            "predicted_velocity_km_s": 148.84322679172308,
            "residual_km_s": -5.156773208276917,
            "standardized_residual": -2.5783866041384584
          },
          {
            "source_radius_kpc": 22.12,
            "rescaled_radius_kpc": 22.60086956521739,
            "observed_velocity_km_s": 153.0,
            "random_error_km_s": 2.0,
            "predicted_velocity_km_s": 149.1540792931556,
            "residual_km_s": -3.845920706844396,
            "standardized_residual": -1.922960353422198
          },
          {
            "source_radius_kpc": 24.03,
            "rescaled_radius_kpc": 24.55239130434782,
            "observed_velocity_km_s": 150.0,
            "random_error_km_s": 2.0,
            "predicted_velocity_km_s": 149.6103288441686,
            "residual_km_s": -0.3896711558313939,
            "standardized_residual": -0.19483557791569694
          },
          {
            "source_radius_kpc": 26.1,
            "rescaled_radius_kpc": 26.667391304347824,
            "observed_velocity_km_s": 149.0,
            "random_error_km_s": 2.0,
            "predicted_velocity_km_s": 150.2405966591556,
            "residual_km_s": 1.2405966591556137,
            "standardized_residual": 0.6202983295778068
          },
          {
            "source_radius_kpc": 28.16,
            "rescaled_radius_kpc": 28.772173913043474,
            "observed_velocity_km_s": 148.0,
            "random_error_km_s": 2.0,
            "predicted_velocity_km_s": 150.95035978604338,
            "residual_km_s": 2.9503597860433786,
            "standardized_residual": 1.4751798930216893
          },
          {
            "source_radius_kpc": 30.08,
            "rescaled_radius_kpc": 30.733913043478257,
            "observed_velocity_km_s": 146.0,
            "random_error_km_s": 2.0,
            "predicted_velocity_km_s": 151.63623091118765,
            "residual_km_s": 5.636230911187653,
            "standardized_residual": 2.8181154555938264
          },
          {
            "source_radius_kpc": 32.14,
            "rescaled_radius_kpc": 32.83869565217391,
            "observed_velocity_km_s": 147.0,
            "random_error_km_s": 2.0,
            "predicted_velocity_km_s": 152.3516637104803,
            "residual_km_s": 5.351663710480295,
            "standardized_residual": 2.6758318552401477
          },
          {
            "source_radius_kpc": 34.06,
            "rescaled_radius_kpc": 34.8004347826087,
            "observed_velocity_km_s": 148.0,
            "random_error_km_s": 2.0,
            "predicted_velocity_km_s": 152.96416864659454,
            "residual_km_s": 4.964168646594544,
            "standardized_residual": 2.482084323297272
          },
          {
            "source_radius_kpc": 36.12,
            "rescaled_radius_kpc": 36.90521739130435,
            "observed_velocity_km_s": 148.0,
            "random_error_km_s": 2.0,
            "predicted_velocity_km_s": 153.53182764986138,
            "residual_km_s": 5.531827649861384,
            "standardized_residual": 2.765913824930692
          }
        ],
        "unweighted_rms_residual_km_s": 4.538271969550304,
        "maximum_absolute_residual_km_s": 8.165704997245513,
        "chi_squared_random_errors_only": 218.0962642661716,
        "reduced_chi_squared_no_refit": 5.59221190426081,
        "coarse_rms_gate_passed": true,
        "random_error_reduced_chi2_gate_passed": false,
        "comparison_status": "MIXED_COARSE_SHAPE_PASS_RANDOM_ERROR_GATE_FAILED",
        "data_lifecycle": "CONTENT_PINNED_EXTRACT_DIFFERENT_PHOTOMETRIC_REDUCTION",
        "boundary": "SPARC supplies a later 3.6-micron photometric reduction, whereas the published fit used heterogeneous blue-band luminosities and its own gas approximation. Random errors exclude inclination and other systematics. This is an external no-refit stress test, not a reproduction of the original likelihood."
      },
      "maturity_rails": [
        {
          "id": "MODEL_IDENTITY",
          "status": "SATISFIED_WITH_MATTER_BOUNDARY",
          "basis": "All stages retain the Mannheim--O'Brien NGC 3198 thin-disk model; the disputed massive-tracer coupling is declared, not resolved."
        },
        {
          "id": "APPLICABILITY",
          "status": "SATISFIED",
          "basis": "All three obligations required by this bounded prediction are present; quantum and causal-PDE obligations are explicitly out of scope."
        },
        {
          "id": "CROSS_STAGE_COMPOSITION",
          "status": "PARTIALLY_CERTIFIED",
          "basis": "The local metric/orbit and numerical joins are checked; thin-disk, fitted-parameter, and non-identical-dataset joins remain typed imports."
        },
        {
          "id": "PREDICTION_DERIVATION",
          "status": "SATISFIED_WITH_PUBLISHED_MODEL_INPUT",
          "basis": "The local exact predecessors and published disk equations determine a curve after the table parameters are supplied."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "status": "SATISFIED_WITH_MATTER_BOUNDARY",
          "basis": "Circular speed is the displayed observable only under the declared massive-tracer response assumption."
        },
        {
          "id": "NUMERICAL_REPRODUCIBILITY",
          "status": "COARSE_ENDPOINT_REPRODUCED",
          "basis": "Endpoint relative velocity residual 0.0289 is below the declared 0.05 audit gate."
        },
        {
          "id": "EMPIRICAL_COMPARISON",
          "status": "MIXED_RANDOM_ERROR_GATE_FAILED",
          "basis": "No-refit SPARC RMS is 4.538 km/s, while reduced chi-squared using random errors alone is 5.592 and exceeds 2.0."
        },
        {
          "id": "ROBUSTNESS_OUT_OF_SAMPLE",
          "status": "NOT_ASSESSED",
          "basis": "One galaxy and one later cross-dataset are insufficient for robustness or the published 111-galaxy population claim."
        }
      ],
      "assembly_disposition": {
        "status": "BOUNDED_ASSEMBLY_PARTIAL_MIXED_COMPARISON",
        "complete_within_declared_scope": false,
        "formula_endpoint_coarsely_reproduced": true,
        "cross_dataset_coarse_shape_gate_passed": true,
        "cross_dataset_random_error_gate_passed": false,
        "empirically_supported_within_declared_scope": false,
        "complete_theory": false
      },
      "provenance": {
        "inputs": [
          {
            "path": "foundations/data/mannheim-ngc3198-parameters-v1.json",
            "sha256": "4297b3bdf9c1bf1fff0a1d44a26941aacdb3d98bd3729b9134b8f187a924f6e5",
            "role": "content-addressed literature/data transcription and comparison protocol"
          },
          {
            "path": "foundations/data/ngc3198-sparc-mass-model-v1.tsv",
            "sha256": "0c84615d0df5792dfbb0d7ee4f1ed71bffc180a7b8505e0a6614d6947a4f6315",
            "role": "43-row content-pinned NGC 3198 SPARC extract"
          },
          {
            "path": "black_hole_programme/certificates/BH0B_GENERAL_STATIC_SPHERICAL_COMPLETENESS.json",
            "sha256": "12f20c69f42681bd49d4117bd27273576519327c49e36ff807aaabf0d5b97b0b",
            "role": "unchanged exact static spherical Bach-vacuum classification"
          },
          {
            "path": "black_hole_programme/certificates/BH0C_TULLY_FISHER_SCALING.json",
            "sha256": "1b58887d9ffdbeda4e7393565d0f0eaaee10e09303830ef00448725da080f5a9",
            "role": "unchanged local circular-orbit and Tully--Fisher conditional with correction ledger"
          }
        ],
        "remote_source_pins": [
          {
            "citation": "P. D. Mannheim and J. G. O'Brien, Fitting galactic rotation curves with conformal gravity and a global quadratic potential, Phys. Rev. D 85 (2012) 124020",
            "arxiv": "https://arxiv.org/abs/1011.3495",
            "source_archive": "https://export.arxiv.org/e-print/1011.3495",
            "source_archive_sha256": "e366db37bc99ce08c96609f751d9b0ffb779dd4ce1c0140a2e226c1aefc075c1",
            "source_member": "fitting5.tex",
            "parameter_table": "Table 1, NGC 3198 row",
            "equations": [
              "(5)",
              "(20)"
            ],
            "retrieved": "2026-08-14"
          },
          {
            "citation": "F. Lelli, S. S. McGaugh, and J. M. Schombert, SPARC: Mass Models for 175 Disk Galaxies with Spitzer Photometry and Accurate Rotation Curves, Astron. J. 152 (2016) 157",
            "url": "https://astroweb.case.edu/SPARC/MassModels_Lelli2016c.mrt",
            "full_source_sha256": "9108994b12cc401b94a1768beca61c53ec354779385c9c9cc571049f3043244c",
            "local_extract": "foundations/data/ngc3198-sparc-mass-model-v1.tsv",
            "selection": "All 43 rows whose fixed-width ID field is NGC3198, copied without numerical alteration",
            "retrieved": "2026-08-14"
          }
        ]
      },
      "independent_checker": {
        "path": "foundations/check_mannheim_ngc3198_assembly.py",
        "numeric_source": "foundations/mannheim_ngc3198_numeric_checker.cpp",
        "method": "Independent C++17 Bessel evaluation, source/data hash closure, stage/interface/applicability audit, and fail-closed gate recomputation."
      },
      "claim_flags": {
        "single_model_identity_declared": true,
        "applicability_mask_complete": true,
        "exact_local_predecessors_imported_by_hash": true,
        "published_parameters_content_pinned": true,
        "independent_numeric_bessel_rail": true,
        "published_endpoint_coarsely_reproduced": true,
        "sparc_cross_dataset_coarse_shape_gate_passed": true,
        "sparc_cross_dataset_random_error_gate_passed": false,
        "original_full_curve_digitized": false,
        "original_fit_likelihood_reproduced": false,
        "mass_to_light_ratio_refit": false,
        "matter_coupling_dispute_resolved": false,
        "galaxy_population_claim_assessed": false,
        "empirical_support_established": false,
        "bounded_prediction_assembly_complete": false,
        "complete_conformal_gravity_theory_established": false,
        "quantum_lifecycle_promoted": false
      },
      "does_not_establish": [
        "that the macroscopic scalar conformal frame is irrelevant to massive-particle trajectories or that Mannheim's matter-sector response is correct",
        "an interior galactic solution of the Bach equation with baryonic matter",
        "identity of the 2012 heterogeneous blue-band fit data with the 2016 SPARC 3.6-micron reduction",
        "reproduction of the original pointwise curve, fitting algorithm, likelihood, covariance model, distance uncertainty, or systematic-error budget",
        "that the fitted stellar mass-to-light ratio is independently preferred; it is imported without refitting",
        "empirical support under the SPARC random-error gate, which fails",
        "the published 111- or 141-galaxy population claims, lensing, cosmology, or another observational sector",
        "ghost freedom, quantum unitarity, a Mannheim C operator, or any quantum lifecycle promotion",
        "a complete observationally validated conformal-gravity theory"
      ],
      "human_report": "foundations/reports/mannheim-ngc3198-model-assembly-v1.md",
      "canonical_digest": "73895aeee6238a689d3f38e2bbd5ef241fd5cf5d37735d2deed879f9b63b5740"
    }
  ],
  "model_scoped_sources": [
    {
      "path": "foundations/results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json",
      "sha256": "f87aa0453de1af594175d1c23c39b48d644064a8582a56785bd9ea4ce279a902"
    },
    {
      "path": "foundations/results/FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1.json",
      "sha256": "d4e7b8774f6593136b512453108a2d39396cd91969fdfc73681ee14d936e0154"
    }
  ],
  "model_comparisons": [
    {
      "schema_version": "foundational-ngc3198-common-fit-comparison-v1",
      "result_id": "FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1",
      "result_kind": "BOUNDED_SINGLE_GALAXY_COMMON_PROTOCOL_MODEL_COMPARISON",
      "created": "2026-08-14",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC"
      ],
      "protocol": "foundations/data/ngc3198-common-fit-protocol-v1.json",
      "protocol_sha256": "670bba7e3fbda35af0a7566d05c9263da110f681de555bef9dbb44055cb43752",
      "input_hashes": {
        "mannheim_parameters": "4297b3bdf9c1bf1fff0a1d44a26941aacdb3d98bd3729b9134b8f187a924f6e5",
        "sparc_extract": "0c84615d0df5792dfbb0d7ee4f1ed71bffc180a7b8505e0a6614d6947a4f6315"
      },
      "models": [
        {
          "model_id": "NEWTONIAN_BARYONS_ONLY",
          "fitted_parameters": {
            "q_star": 1.6321223695494784
          },
          "parameter_count": 1,
          "metrics": {
            "point_count": 39,
            "chi_squared": 4891.449347513035,
            "degrees_of_freedom": 38,
            "reduced_chi_squared": 128.72235125034302,
            "unweighted_rms_residual_km_s": 23.896205433040972,
            "maximum_absolute_residual_km_s": 53.21867393486717,
            "AIC": 4893.449347513035,
            "AICc": 4893.557455621143,
            "BIC": 4895.112909159165
          },
          "random_error_gate": {
            "threshold_reduced_chi_squared": 2.0,
            "passed": false
          },
          "parameter_boundary_hit": false,
          "predictions": [
            {
              "radius_kpc": 0.32695652173913037,
              "observed_km_s": 24.4,
              "error_km_s": 35.9,
              "predicted_km_s": 24.635059275766015,
              "residual_km_s": 0.23505927576601593,
              "standardized_residual": 0.006547612138329135
            },
            {
              "radius_kpc": 0.6539130434782607,
              "observed_km_s": 43.3,
              "error_km_s": 16.3,
              "predicted_km_s": 42.90247218246211,
              "residual_km_s": -0.3975278175378847,
              "standardized_residual": -0.0243882096649009
            },
            {
              "radius_kpc": 0.9808695652173912,
              "observed_km_s": 45.5,
              "error_km_s": 16.1,
              "predicted_km_s": 58.18090411751911,
              "residual_km_s": 12.680904117519113,
              "standardized_residual": 0.7876337961191995
            },
            {
              "radius_kpc": 1.3078260869565215,
              "observed_km_s": 58.5,
              "error_km_s": 15.4,
              "predicted_km_s": 71.33318336665288,
              "residual_km_s": 12.833183366652875,
              "standardized_residual": 0.8333235952371997
            },
            {
              "radius_kpc": 1.645,
              "observed_km_s": 68.8,
              "error_km_s": 7.61,
              "predicted_km_s": 83.14647565762453,
              "residual_km_s": 14.346475657624538,
              "standardized_residual": 1.8852136212384412
            },
            {
              "radius_kpc": 1.9719565217391302,
              "observed_km_s": 76.9,
              "error_km_s": 10.3,
              "predicted_km_s": 93.20015897323863,
              "residual_km_s": 16.300158973238624,
              "standardized_residual": 1.582539706139672
            },
            {
              "radius_kpc": 2.2886956521739132,
              "observed_km_s": 82.0,
              "error_km_s": 8.09,
              "predicted_km_s": 101.81897470219266,
              "residual_km_s": 19.818974702192662,
              "standardized_residual": 2.4498114588618867
            },
            {
              "radius_kpc": 2.625869565217391,
              "observed_km_s": 86.9,
              "error_km_s": 7.6,
              "predicted_km_s": 109.9422032627559,
              "residual_km_s": 23.04220326275589,
              "standardized_residual": 3.0318688503626174
            },
            {
              "radius_kpc": 2.952826086956522,
              "observed_km_s": 97.6,
              "error_km_s": 3.03,
              "predicted_km_s": 116.90904797897753,
              "residual_km_s": 19.30904797897753,
              "standardized_residual": 6.3726230953721235
            },
            {
              "radius_kpc": 3.2797826086956516,
              "observed_km_s": 100.0,
              "error_km_s": 5.31,
              "predicted_km_s": 123.08205486043,
              "residual_km_s": 23.082054860430006,
              "standardized_residual": 4.346902986898306
            },
            {
              "radius_kpc": 3.61695652173913,
              "observed_km_s": 107.0,
              "error_km_s": 7.51,
              "predicted_km_s": 128.70630074609912,
              "residual_km_s": 21.706300746099117,
              "standardized_residual": 2.890319673248884
            },
            {
              "radius_kpc": 3.933695652173913,
              "observed_km_s": 113.0,
              "error_km_s": 7.32,
              "predicted_km_s": 133.37390218648676,
              "residual_km_s": 20.37390218648676,
              "standardized_residual": 2.7833199708315246
            },
            {
              "radius_kpc": 4.260652173913043,
              "observed_km_s": 117.0,
              "error_km_s": 5.21,
              "predicted_km_s": 137.6281736136232,
              "residual_km_s": 20.628173613623204,
              "standardized_residual": 3.9593423442654903
            },
            {
              "radius_kpc": 4.5978260869565215,
              "observed_km_s": 119.0,
              "error_km_s": 5.67,
              "predicted_km_s": 141.4729649627296,
              "residual_km_s": 22.472964962729606,
              "standardized_residual": 3.9634858840792955
            },
            {
              "radius_kpc": 4.9247826086956525,
              "observed_km_s": 127.0,
              "error_km_s": 5.39,
              "predicted_km_s": 144.72509879917337,
              "residual_km_s": 17.725098799173367,
              "standardized_residual": 3.288515547156469
            },
            {
              "radius_kpc": 5.261956521739131,
              "observed_km_s": 132.0,
              "error_km_s": 4.34,
              "predicted_km_s": 147.63397567747444,
              "residual_km_s": 15.633975677474439,
              "standardized_residual": 3.6022985431968753
            },
            {
              "radius_kpc": 5.578695652173913,
              "observed_km_s": 134.0,
              "error_km_s": 2.36,
              "predicted_km_s": 149.99246857518287,
              "residual_km_s": 15.992468575182869,
              "standardized_residual": 6.7764697352469785
            },
            {
              "radius_kpc": 5.905652173913044,
              "observed_km_s": 137.0,
              "error_km_s": 0.89,
              "predicted_km_s": 152.08112559712916,
              "residual_km_s": 15.081125597129159,
              "standardized_residual": 16.945084940594562
            },
            {
              "radius_kpc": 6.232608695652173,
              "observed_km_s": 140.0,
              "error_km_s": 2.84,
              "predicted_km_s": 153.84944979119678,
              "residual_km_s": 13.849449791196776,
              "standardized_residual": 4.8765668278861884
            },
            {
              "radius_kpc": 6.569782608695651,
              "observed_km_s": 142.0,
              "error_km_s": 0.88,
              "predicted_km_s": 155.36766602844185,
              "residual_km_s": 13.367666028441846,
              "standardized_residual": 15.190529577774825
            },
            {
              "radius_kpc": 6.886521739130435,
              "observed_km_s": 144.0,
              "error_km_s": 1.23,
              "predicted_km_s": 156.53651156066957,
              "residual_km_s": 12.536511560669567,
              "standardized_residual": 10.192285821682574
            },
            {
              "radius_kpc": 7.2134782608695645,
              "observed_km_s": 146.0,
              "error_km_s": 1.57,
              "predicted_km_s": 157.50479799090945,
              "residual_km_s": 11.504797990909452,
              "standardized_residual": 7.327896809496466
            },
            {
              "radius_kpc": 8.214782608695652,
              "observed_km_s": 147.0,
              "error_km_s": 3.0,
              "predicted_km_s": 159.17994627809028,
              "residual_km_s": 12.179946278090284,
              "standardized_residual": 4.059982092696761
            },
            {
              "radius_kpc": 9.236521739130433,
              "observed_km_s": 148.0,
              "error_km_s": 3.0,
              "predicted_km_s": 159.28611142401292,
              "residual_km_s": 11.286111424012915,
              "standardized_residual": 3.7620371413376383
            },
            {
              "radius_kpc": 10.258260869565216,
              "observed_km_s": 152.0,
              "error_km_s": 2.0,
              "predicted_km_s": 158.19741896595403,
              "residual_km_s": 6.197418965954029,
              "standardized_residual": 3.0987094829770143
            },
            {
              "radius_kpc": 11.28,
              "observed_km_s": 155.0,
              "error_km_s": 2.0,
              "predicted_km_s": 156.24439619913315,
              "residual_km_s": 1.2443961991331491,
              "standardized_residual": 0.6221980995665746
            },
            {
              "radius_kpc": 12.31195652173913,
              "observed_km_s": 156.0,
              "error_km_s": 2.0,
              "predicted_km_s": 153.65509476859765,
              "residual_km_s": -2.3449052314023504,
              "standardized_residual": -1.1724526157011752
            },
            {
              "radius_kpc": 14.355434782608697,
              "observed_km_s": 157.0,
              "error_km_s": 2.0,
              "predicted_km_s": 147.44974842625,
              "residual_km_s": -9.55025157374999,
              "standardized_residual": -4.775125786874995
            },
            {
              "radius_kpc": 16.419347826086955,
              "observed_km_s": 153.0,
              "error_km_s": 2.0,
              "predicted_km_s": 140.59078327084842,
              "residual_km_s": -12.40921672915158,
              "standardized_residual": -6.20460836457579
            },
            {
              "radius_kpc": 18.524130434782606,
              "observed_km_s": 153.0,
              "error_km_s": 2.0,
              "predicted_km_s": 133.64809988473834,
              "residual_km_s": -19.351900115261657,
              "standardized_residual": -9.675950057630828
            },
            {
              "radius_kpc": 20.48586956521739,
              "observed_km_s": 154.0,
              "error_km_s": 2.0,
              "predicted_km_s": 127.54303237975964,
              "residual_km_s": -26.456967620240363,
              "standardized_residual": -13.228483810120181
            },
            {
              "radius_kpc": 22.60086956521739,
              "observed_km_s": 153.0,
              "error_km_s": 2.0,
              "predicted_km_s": 121.51473142939496,
              "residual_km_s": -31.485268570605044,
              "standardized_residual": -15.742634285302522
            },
            {
              "radius_kpc": 24.55239130434782,
              "observed_km_s": 150.0,
              "error_km_s": 2.0,
              "predicted_km_s": 116.50382669401974,
              "residual_km_s": -33.496173305980264,
              "standardized_residual": -16.748086652990132
            },
            {
              "radius_kpc": 26.667391304347824,
              "observed_km_s": 149.0,
              "error_km_s": 2.0,
              "predicted_km_s": 111.65402074243386,
              "residual_km_s": -37.34597925756614,
              "standardized_residual": -18.67298962878307
            },
            {
              "radius_kpc": 28.772173913043474,
              "observed_km_s": 148.0,
              "error_km_s": 2.0,
              "predicted_km_s": 107.37631061501929,
              "residual_km_s": -40.62368938498071,
              "standardized_residual": -20.311844692490354
            },
            {
              "radius_kpc": 30.733913043478257,
              "observed_km_s": 146.0,
              "error_km_s": 2.0,
              "predicted_km_s": 103.82394944739879,
              "residual_km_s": -42.17605055260121,
              "standardized_residual": -21.088025276300606
            },
            {
              "radius_kpc": 32.83869565217391,
              "observed_km_s": 147.0,
              "error_km_s": 2.0,
              "predicted_km_s": 100.41465445425571,
              "residual_km_s": -46.58534554574429,
              "standardized_residual": -23.292672772872145
            },
            {
              "radius_kpc": 34.8004347826087,
              "observed_km_s": 148.0,
              "error_km_s": 2.0,
              "predicted_km_s": 97.55710349220688,
              "residual_km_s": -50.44289650779312,
              "standardized_residual": -25.22144825389656
            },
            {
              "radius_kpc": 36.90521739130435,
              "observed_km_s": 148.0,
              "error_km_s": 2.0,
              "predicted_km_s": 94.78132606513283,
              "residual_km_s": -53.21867393486717,
              "standardized_residual": -26.609336967433585
            }
          ]
        },
        {
          "model_id": "GR_NFW_DARK_HALO",
          "fitted_parameters": {
            "q_star": 0.8253897969532975,
            "V200_km_s": 116.31597312471598,
            "concentration_c200": 6.802200504154277
          },
          "parameter_count": 3,
          "metrics": {
            "point_count": 39,
            "chi_squared": 34.749485687661654,
            "degrees_of_freedom": 36,
            "reduced_chi_squared": 0.9652634913239349,
            "unweighted_rms_residual_km_s": 5.147987363846723,
            "maximum_absolute_residual_km_s": 12.184058969636808,
            "AIC": 40.749485687661654,
            "AICc": 41.43519997337594,
            "BIC": 45.74017062605059
          },
          "random_error_gate": {
            "threshold_reduced_chi_squared": 2.0,
            "passed": true
          },
          "parameter_boundary_hit": false,
          "predictions": [
            {
              "radius_kpc": 0.32695652173913037,
              "observed_km_s": 24.4,
              "error_km_s": 35.9,
              "predicted_km_s": 28.640614105516736,
              "residual_km_s": 4.2406141055167375,
              "standardized_residual": 0.11812295558542445
            },
            {
              "radius_kpc": 0.6539130434782607,
              "observed_km_s": 43.3,
              "error_km_s": 16.3,
              "predicted_km_s": 44.069551394892095,
              "residual_km_s": 0.7695513948920976,
              "standardized_residual": 0.0472117420179201
            },
            {
              "radius_kpc": 0.9808695652173912,
              "observed_km_s": 45.5,
              "error_km_s": 16.1,
              "predicted_km_s": 56.619321123541106,
              "residual_km_s": 11.119321123541106,
              "standardized_residual": 0.6906410635739817
            },
            {
              "radius_kpc": 1.3078260869565215,
              "observed_km_s": 58.5,
              "error_km_s": 15.4,
              "predicted_km_s": 67.34130008517072,
              "residual_km_s": 8.841300085170715,
              "standardized_residual": 0.5741103951409555
            },
            {
              "radius_kpc": 1.645,
              "observed_km_s": 68.8,
              "error_km_s": 7.61,
              "predicted_km_s": 76.97311920415785,
              "residual_km_s": 8.173119204157857,
              "standardized_residual": 1.0739972673006382
            },
            {
              "radius_kpc": 1.9719565217391302,
              "observed_km_s": 76.9,
              "error_km_s": 10.3,
              "predicted_km_s": 85.20693913029743,
              "residual_km_s": 8.306939130297422,
              "standardized_residual": 0.8064989446890701
            },
            {
              "radius_kpc": 2.2886956521739132,
              "observed_km_s": 82.0,
              "error_km_s": 8.09,
              "predicted_km_s": 92.31692039622249,
              "residual_km_s": 10.316920396222486,
              "standardized_residual": 1.2752682813624827
            },
            {
              "radius_kpc": 2.625869565217391,
              "observed_km_s": 86.9,
              "error_km_s": 7.6,
              "predicted_km_s": 99.08405896963681,
              "residual_km_s": 12.184058969636808,
              "standardized_residual": 1.6031656538995802
            },
            {
              "radius_kpc": 2.952826086956522,
              "observed_km_s": 97.6,
              "error_km_s": 3.03,
              "predicted_km_s": 104.95975877917017,
              "residual_km_s": 7.359758779170178,
              "standardized_residual": 2.4289632934555048
            },
            {
              "radius_kpc": 3.2797826086956516,
              "observed_km_s": 100.0,
              "error_km_s": 5.31,
              "predicted_km_s": 110.24186854152782,
              "residual_km_s": 10.241868541527822,
              "standardized_residual": 1.9287888025476125
            },
            {
              "radius_kpc": 3.61695652173913,
              "observed_km_s": 107.0,
              "error_km_s": 7.51,
              "predicted_km_s": 115.13817635633879,
              "residual_km_s": 8.13817635633879,
              "standardized_residual": 1.083645320417948
            },
            {
              "radius_kpc": 3.933695652173913,
              "observed_km_s": 113.0,
              "error_km_s": 7.32,
              "predicted_km_s": 119.28286291887446,
              "residual_km_s": 6.282862918874457,
              "standardized_residual": 0.8583146064036143
            },
            {
              "radius_kpc": 4.260652173913043,
              "observed_km_s": 117.0,
              "error_km_s": 5.21,
              "predicted_km_s": 123.14659738249361,
              "residual_km_s": 6.14659738249361,
              "standardized_residual": 1.1797691713039558
            },
            {
              "radius_kpc": 4.5978260869565215,
              "observed_km_s": 119.0,
              "error_km_s": 5.67,
              "predicted_km_s": 126.73374600762067,
              "residual_km_s": 7.733746007620667,
              "standardized_residual": 1.3639763681870665
            },
            {
              "radius_kpc": 4.9247826086956525,
              "observed_km_s": 127.0,
              "error_km_s": 5.39,
              "predicted_km_s": 129.86457394541065,
              "residual_km_s": 2.8645739454106547,
              "standardized_residual": 0.5314608433043887
            },
            {
              "radius_kpc": 5.261956521739131,
              "observed_km_s": 132.0,
              "error_km_s": 4.34,
              "predicted_km_s": 132.7693773882881,
              "residual_km_s": 0.7693773882880919,
              "standardized_residual": 0.17727589591891518
            },
            {
              "radius_kpc": 5.578695652173913,
              "observed_km_s": 134.0,
              "error_km_s": 2.36,
              "predicted_km_s": 135.22646109299808,
              "residual_km_s": 1.226461092998079,
              "standardized_residual": 0.5196869038127454
            },
            {
              "radius_kpc": 5.905652173913044,
              "observed_km_s": 137.0,
              "error_km_s": 0.89,
              "predicted_km_s": 137.5121024640442,
              "residual_km_s": 0.5121024640442045,
              "standardized_residual": 0.57539602701596
            },
            {
              "radius_kpc": 6.232608695652173,
              "observed_km_s": 140.0,
              "error_km_s": 2.84,
              "predicted_km_s": 139.56596606445848,
              "residual_km_s": -0.43403393554152103,
              "standardized_residual": -0.1528288505427891
            },
            {
              "radius_kpc": 6.569782608695651,
              "observed_km_s": 142.0,
              "error_km_s": 0.88,
              "predicted_km_s": 141.4633585303677,
              "residual_km_s": -0.5366414696322863,
              "standardized_residual": -0.6098198518548709
            },
            {
              "radius_kpc": 6.886521739130435,
              "observed_km_s": 144.0,
              "error_km_s": 1.23,
              "predicted_km_s": 143.0599759074669,
              "residual_km_s": -0.9400240925330934,
              "standardized_residual": -0.7642472297017019
            },
            {
              "radius_kpc": 7.2134782608695645,
              "observed_km_s": 146.0,
              "error_km_s": 1.57,
              "predicted_km_s": 144.5362033014006,
              "residual_km_s": -1.4637966985993955,
              "standardized_residual": -0.9323545850951563
            },
            {
              "radius_kpc": 8.214782608695652,
              "observed_km_s": 147.0,
              "error_km_s": 3.0,
              "predicted_km_s": 148.12632447093137,
              "residual_km_s": 1.1263244709313653,
              "standardized_residual": 0.3754414903104551
            },
            {
              "radius_kpc": 9.236521739130433,
              "observed_km_s": 148.0,
              "error_km_s": 3.0,
              "predicted_km_s": 150.6305094640626,
              "residual_km_s": 2.6305094640626123,
              "standardized_residual": 0.8768364880208708
            },
            {
              "radius_kpc": 10.258260869565216,
              "observed_km_s": 152.0,
              "error_km_s": 2.0,
              "predicted_km_s": 152.26369368605663,
              "residual_km_s": 0.2636936860566266,
              "standardized_residual": 0.1318468430283133
            },
            {
              "radius_kpc": 11.28,
              "observed_km_s": 155.0,
              "error_km_s": 2.0,
              "predicted_km_s": 153.25576000802099,
              "residual_km_s": -1.7442399919790148,
              "standardized_residual": -0.8721199959895074
            },
            {
              "radius_kpc": 12.31195652173913,
              "observed_km_s": 156.0,
              "error_km_s": 2.0,
              "predicted_km_s": 153.78511895949384,
              "residual_km_s": -2.2148810405061568,
              "standardized_residual": -1.1074405202530784
            },
            {
              "radius_kpc": 14.355434782608697,
              "observed_km_s": 157.0,
              "error_km_s": 2.0,
              "predicted_km_s": 153.93343130726507,
              "residual_km_s": -3.0665686927349327,
              "standardized_residual": -1.5332843463674664
            },
            {
              "radius_kpc": 16.419347826086955,
              "observed_km_s": 153.0,
              "error_km_s": 2.0,
              "predicted_km_s": 153.4285420989113,
              "residual_km_s": 0.4285420989112936,
              "standardized_residual": 0.2142710494556468
            },
            {
              "radius_kpc": 18.524130434782606,
              "observed_km_s": 153.0,
              "error_km_s": 2.0,
              "predicted_km_s": 152.6512337395939,
              "residual_km_s": -0.3487662604061086,
              "standardized_residual": -0.1743831302030543
            },
            {
              "radius_kpc": 20.48586956521739,
              "observed_km_s": 154.0,
              "error_km_s": 2.0,
              "predicted_km_s": 151.87972335927432,
              "residual_km_s": -2.1202766407256775,
              "standardized_residual": -1.0601383203628387
            },
            {
              "radius_kpc": 22.60086956521739,
              "observed_km_s": 153.0,
              "error_km_s": 2.0,
              "predicted_km_s": 151.09187991532278,
              "residual_km_s": -1.908120084677222,
              "standardized_residual": -0.954060042338611
            },
            {
              "radius_kpc": 24.55239130434782,
              "observed_km_s": 150.0,
              "error_km_s": 2.0,
              "predicted_km_s": 150.4351873003968,
              "residual_km_s": 0.435187300396791,
              "standardized_residual": 0.2175936501983955
            },
            {
              "radius_kpc": 26.667391304347824,
              "observed_km_s": 149.0,
              "error_km_s": 2.0,
              "predicted_km_s": 149.80169126323196,
              "residual_km_s": 0.8016912632319588,
              "standardized_residual": 0.4008456316159794
            },
            {
              "radius_kpc": 28.772173913043474,
              "observed_km_s": 148.0,
              "error_km_s": 2.0,
              "predicted_km_s": 149.23977953009046,
              "residual_km_s": 1.239779530090459,
              "standardized_residual": 0.6198897650452295
            },
            {
              "radius_kpc": 30.733913043478257,
              "observed_km_s": 146.0,
              "error_km_s": 2.0,
              "predicted_km_s": 148.76263533238168,
              "residual_km_s": 2.7626353323816772,
              "standardized_residual": 1.3813176661908386
            },
            {
              "radius_kpc": 32.83869565217391,
              "observed_km_s": 147.0,
              "error_km_s": 2.0,
              "predicted_km_s": 148.28503141796443,
              "residual_km_s": 1.2850314179644329,
              "standardized_residual": 0.6425157089822164
            },
            {
              "radius_kpc": 34.8004347826087,
              "observed_km_s": 148.0,
              "error_km_s": 2.0,
              "predicted_km_s": 147.85979468472232,
              "residual_km_s": -0.14020531527768298,
              "standardized_residual": -0.07010265763884149
            },
            {
              "radius_kpc": 36.90521739130435,
              "observed_km_s": 148.0,
              "error_km_s": 2.0,
              "predicted_km_s": 147.41455073348493,
              "residual_km_s": -0.5854492665150701,
              "standardized_residual": -0.29272463325753506
            }
          ]
        },
        {
          "model_id": "MANNHEIM_CONFORMAL_GRAVITY",
          "fitted_parameters": {
            "q_star": 1.0645429990794995
          },
          "parameter_count": 1,
          "metrics": {
            "point_count": 39,
            "chi_squared": 121.66755195704582,
            "degrees_of_freedom": 38,
            "reduced_chi_squared": 3.201777683080153,
            "unweighted_rms_residual_km_s": 4.694475967312153,
            "maximum_absolute_residual_km_s": 9.20389962213413,
            "AIC": 123.66755195704582,
            "AICc": 123.77566006515393,
            "BIC": 125.33111360317547
          },
          "random_error_gate": {
            "threshold_reduced_chi_squared": 2.0,
            "passed": false
          },
          "parameter_boundary_hit": false,
          "predictions": [
            {
              "radius_kpc": 0.32695652173913037,
              "observed_km_s": 24.4,
              "error_km_s": 35.9,
              "predicted_km_s": 23.22008570676307,
              "residual_km_s": -1.17991429323693,
              "standardized_residual": -0.03286669340492841
            },
            {
              "radius_kpc": 0.6539130434782607,
              "observed_km_s": 43.3,
              "error_km_s": 16.3,
              "predicted_km_s": 38.67172864923142,
              "residual_km_s": -4.628271350768578,
              "standardized_residual": -0.283943027654514
            },
            {
              "radius_kpc": 0.9808695652173912,
              "observed_km_s": 45.5,
              "error_km_s": 16.1,
              "predicted_km_s": 51.5951919577991,
              "residual_km_s": 6.095191957799102,
              "standardized_residual": 0.3785833514160933
            },
            {
              "radius_kpc": 1.3078260869565215,
              "observed_km_s": 58.5,
              "error_km_s": 15.4,
              "predicted_km_s": 62.76458481640087,
              "residual_km_s": 4.26458481640087,
              "standardized_residual": 0.27692109197408243
            },
            {
              "radius_kpc": 1.645,
              "observed_km_s": 68.8,
              "error_km_s": 7.61,
              "predicted_km_s": 72.85611139999047,
              "residual_km_s": 4.0561113999904705,
              "standardized_residual": 0.5329975558463167
            },
            {
              "radius_kpc": 1.9719565217391302,
              "observed_km_s": 76.9,
              "error_km_s": 10.3,
              "predicted_km_s": 81.50732876555263,
              "residual_km_s": 4.607328765552623,
              "standardized_residual": 0.44731347238374974
            },
            {
              "radius_kpc": 2.2886956521739132,
              "observed_km_s": 82.0,
              "error_km_s": 8.09,
              "predicted_km_s": 88.98590474554521,
              "residual_km_s": 6.985904745545213,
              "standardized_residual": 0.8635234543319176
            },
            {
              "radius_kpc": 2.625869565217391,
              "observed_km_s": 86.9,
              "error_km_s": 7.6,
              "predicted_km_s": 96.10389962213414,
              "residual_km_s": 9.20389962213413,
              "standardized_residual": 1.2110394239650173
            },
            {
              "radius_kpc": 2.952826086956522,
              "observed_km_s": 97.6,
              "error_km_s": 3.03,
              "predicted_km_s": 102.2792129381094,
              "residual_km_s": 4.679212938109401,
              "standardized_residual": 1.5442946990460071
            },
            {
              "radius_kpc": 3.2797826086956516,
              "observed_km_s": 100.0,
              "error_km_s": 5.31,
              "predicted_km_s": 107.82268233785022,
              "residual_km_s": 7.822682337850225,
              "standardized_residual": 1.4731981803861065
            },
            {
              "radius_kpc": 3.61695652173913,
              "observed_km_s": 107.0,
              "error_km_s": 7.51,
              "predicted_km_s": 112.95099065460846,
              "residual_km_s": 5.950990654608461,
              "standardized_residual": 0.7924088754471985
            },
            {
              "radius_kpc": 3.933695652173913,
              "observed_km_s": 113.0,
              "error_km_s": 7.32,
              "predicted_km_s": 117.28150839458051,
              "residual_km_s": 4.281508394580513,
              "standardized_residual": 0.5849055183853159
            },
            {
              "radius_kpc": 4.260652173913043,
              "observed_km_s": 117.0,
              "error_km_s": 5.21,
              "predicted_km_s": 121.30716673765663,
              "residual_km_s": 4.30716673765663,
              "standardized_residual": 0.8267114659609653
            },
            {
              "radius_kpc": 4.5978260869565215,
              "observed_km_s": 119.0,
              "error_km_s": 5.67,
              "predicted_km_s": 125.03235453142864,
              "residual_km_s": 6.032354531428638,
              "standardized_residual": 1.0639073247669555
            },
            {
              "radius_kpc": 4.9247826086956525,
              "observed_km_s": 127.0,
              "error_km_s": 5.39,
              "predicted_km_s": 128.27169468912834,
              "residual_km_s": 1.2716946891283385,
              "standardized_residual": 0.2359359349032168
            },
            {
              "radius_kpc": 5.261956521739131,
              "observed_km_s": 132.0,
              "error_km_s": 4.34,
              "predicted_km_s": 131.26497600132072,
              "residual_km_s": -0.7350239986792815,
              "standardized_residual": -0.16936036835928145
            },
            {
              "radius_kpc": 5.578695652173913,
              "observed_km_s": 134.0,
              "error_km_s": 2.36,
              "predicted_km_s": 133.78583521938884,
              "residual_km_s": -0.2141647806111564,
              "standardized_residual": -0.0907477883945578
            },
            {
              "radius_kpc": 5.905652173913044,
              "observed_km_s": 137.0,
              "error_km_s": 0.89,
              "predicted_km_s": 136.11988645307852,
              "residual_km_s": -0.8801135469214785,
              "standardized_residual": -0.9888916257544702
            },
            {
              "radius_kpc": 6.232608695652173,
              "observed_km_s": 140.0,
              "error_km_s": 2.84,
              "predicted_km_s": 138.20656489366135,
              "residual_km_s": -1.7934351063386487,
              "standardized_residual": -0.6314912346262848
            },
            {
              "radius_kpc": 6.569782608695651,
              "observed_km_s": 142.0,
              "error_km_s": 0.88,
              "predicted_km_s": 140.12357169037406,
              "residual_km_s": -1.8764283096259362,
              "standardized_residual": -2.1323048973022
            },
            {
              "radius_kpc": 6.886521739130435,
              "observed_km_s": 144.0,
              "error_km_s": 1.23,
              "predicted_km_s": 141.72725941867765,
              "residual_km_s": -2.2727405813223527,
              "standardized_residual": -1.8477565701807745
            },
            {
              "radius_kpc": 7.2134782608695645,
              "observed_km_s": 146.0,
              "error_km_s": 1.57,
              "predicted_km_s": 143.2009557332161,
              "residual_km_s": -2.799044266783909,
              "standardized_residual": -1.7828307431744643
            },
            {
              "radius_kpc": 8.214782608695652,
              "observed_km_s": 147.0,
              "error_km_s": 3.0,
              "predicted_km_s": 146.73746973182466,
              "residual_km_s": -0.26253026817533964,
              "standardized_residual": -0.08751008939177989
            },
            {
              "radius_kpc": 9.236521739130433,
              "observed_km_s": 148.0,
              "error_km_s": 3.0,
              "predicted_km_s": 149.14675699611286,
              "residual_km_s": 1.146756996112856,
              "standardized_residual": 0.3822523320376187
            },
            {
              "radius_kpc": 10.258260869565216,
              "observed_km_s": 152.0,
              "error_km_s": 2.0,
              "predicted_km_s": 150.67769891354834,
              "residual_km_s": -1.3223010864516596,
              "standardized_residual": -0.6611505432258298
            },
            {
              "radius_kpc": 11.28,
              "observed_km_s": 155.0,
              "error_km_s": 2.0,
              "predicted_km_s": 151.5858482028868,
              "residual_km_s": -3.414151797113192,
              "standardized_residual": -1.707075898556596
            },
            {
              "radius_kpc": 12.31195652173913,
              "observed_km_s": 156.0,
              "error_km_s": 2.0,
              "predicted_km_s": 152.06839156416927,
              "residual_km_s": -3.931608435830725,
              "standardized_residual": -1.9658042179153625
            },
            {
              "radius_kpc": 14.355434782608697,
              "observed_km_s": 157.0,
              "error_km_s": 2.0,
              "predicted_km_s": 152.28538374915263,
              "residual_km_s": -4.714616250847371,
              "standardized_residual": -2.3573081254236854
            },
            {
              "radius_kpc": 16.419347826086955,
              "observed_km_s": 153.0,
              "error_km_s": 2.0,
              "predicted_km_s": 152.10647345789886,
              "residual_km_s": -0.8935265421011422,
              "standardized_residual": -0.4467632710505711
            },
            {
              "radius_kpc": 18.524130434782606,
              "observed_km_s": 153.0,
              "error_km_s": 2.0,
              "predicted_km_s": 151.92930932729809,
              "residual_km_s": -1.0706906727019145,
              "standardized_residual": -0.5353453363509573
            },
            {
              "radius_kpc": 20.48586956521739,
              "observed_km_s": 154.0,
              "error_km_s": 2.0,
              "predicted_km_s": 151.93215644466378,
              "residual_km_s": -2.067843555336225,
              "standardized_residual": -1.0339217776681124
            },
            {
              "radius_kpc": 22.60086956521739,
              "observed_km_s": 153.0,
              "error_km_s": 2.0,
              "predicted_km_s": 152.16358476138154,
              "residual_km_s": -0.8364152386184571,
              "standardized_residual": -0.41820761930922856
            },
            {
              "radius_kpc": 24.55239130434782,
              "observed_km_s": 150.0,
              "error_km_s": 2.0,
              "predicted_km_s": 152.56909241268085,
              "residual_km_s": 2.5690924126808454,
              "standardized_residual": 1.2845462063404227
            },
            {
              "radius_kpc": 26.667391304347824,
              "observed_km_s": 149.0,
              "error_km_s": 2.0,
              "predicted_km_s": 153.16678722823352,
              "residual_km_s": 4.166787228233517,
              "standardized_residual": 2.0833936141167584
            },
            {
              "radius_kpc": 28.772173913043474,
              "observed_km_s": 148.0,
              "error_km_s": 2.0,
              "predicted_km_s": 153.86461877884227,
              "residual_km_s": 5.864618778842271,
              "standardized_residual": 2.9323093894211354
            },
            {
              "radius_kpc": 30.733913043478257,
              "observed_km_s": 146.0,
              "error_km_s": 2.0,
              "predicted_km_s": 154.55533680128204,
              "residual_km_s": 8.555336801282039,
              "standardized_residual": 4.277668400641019
            },
            {
              "radius_kpc": 32.83869565217391,
              "observed_km_s": 147.0,
              "error_km_s": 2.0,
              "predicted_km_s": 155.29073993927597,
              "residual_km_s": 8.290739939275966,
              "standardized_residual": 4.145369969637983
            },
            {
              "radius_kpc": 34.8004347826087,
              "observed_km_s": 148.0,
              "error_km_s": 2.0,
              "predicted_km_s": 155.9337930175309,
              "residual_km_s": 7.933793017530888,
              "standardized_residual": 3.966896508765444
            },
            {
              "radius_kpc": 36.90521739130435,
              "observed_km_s": 148.0,
              "error_km_s": 2.0,
              "predicted_km_s": 156.54539474050685,
              "residual_km_s": 8.54539474050685,
              "standardized_residual": 4.272697370253425
            }
          ]
        }
      ],
      "ranking_by_AICc": [
        "GR_NFW_DARK_HALO",
        "MANNHEIM_CONFORMAL_GRAVITY",
        "NEWTONIAN_BARYONS_ONLY"
      ],
      "scoped_finding": "GR_NFW_DARK_HALO has the lowest AICc and is the only family that passes the declared random-error gate within this common analytic, single-galaxy protocol.",
      "does_not_establish": [
        "a likelihood with distance, inclination, beam-smearing, stellar-population, gas-profile, or other systematic uncertainties",
        "identity of the analytic baryonic geometry with the SPARC numerical mass components or the original Mannheim fitting data",
        "a cosmological concentration--mass prior or a posterior probability for an NFW halo",
        "population-level performance, held-out prediction, or model selection beyond NGC 3198",
        "that the best score in this bounded protocol validates a complete theory or refutes another theory"
      ],
      "claim_flags": {
        "common_observations_used": true,
        "common_baryonic_geometry_used": true,
        "independent_optimizer_agreement_required": true,
        "single_galaxy_only": true,
        "systematic_uncertainties_marginalized": false,
        "population_or_heldout_validation": false,
        "complete_theory_selected": false
      },
      "human_report": "foundations/reports/ngc3198-common-fit-comparison-v1.md",
      "independent_checker": "foundations/check_ngc3198_common_fit_comparison.py",
      "canonical_digest": "82974c6b7f17b8a2a4cc715013ca63d7a170d21aec7c74a1174d9a063b7592b4"
    }
  ],
  "model_comparison_sources": [
    {
      "path": "foundations/results/FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1.json",
      "sha256": "e9c9ecd8e6778a98cf15754970ac2e8fa6c117edca630f3a89b30aea1a03eaeb"
    }
  ],
  "calibration_controls": [
    {
      "schema_version": "standard-gr-observational-control-v1",
      "control_id": "STANDARD_GENERAL_RELATIVITY_DOMAIN_CONTROL",
      "created": "2026-08-14",
      "kind": "EXTERNAL_POSITIVE_CONTROL",
      "label": "Standard general relativity: observational-domain control",
      "scope": "A calibration control showing that the atlas can distinguish registered predictions and successful empirical comparisons from missing records. It is not selected from the foundations cube and is not a candidate Weyl-gravity assembly.",
      "dependency_tags": [
        "LORENTZIAN-CAUSAL"
      ],
      "rail_summary": [
        {
          "id": "PREDICTION_DERIVATION",
          "status": "REGISTERED_IN_DOMAINS",
          "basis": "Four primary-source records identify a GR prediction in three benchmark families."
        },
        {
          "id": "OBSERVABLE_IDENTIFICATION",
          "status": "REGISTERED_IN_DOMAINS",
          "basis": "Each record names the measured observable and comparison domain."
        },
        {
          "id": "EMPIRICAL_COMPARISON",
          "status": "SUPPORTED_IN_DOMAINS",
          "basis": "The cited analyses report consistency with the tested GR prediction within their stated scope."
        },
        {
          "id": "ROBUSTNESS_OUT_OF_SAMPLE",
          "status": "MULTI_DOMAIN_SUPPORT",
          "basis": "Independent solar-system, binary-pulsar, gravitational-wave, and multimessenger analyses test distinct regimes; this is not a universal out-of-sample theorem."
        }
      ],
      "records": [
        {
          "id": "GR_CASSINI_SHAPIRO_2003",
          "benchmark": "SOLAR_SYSTEM",
          "citation": "B. Bertotti, L. Iess, and P. Tortora, A test of general relativity using radio links with the Cassini spacecraft, Nature 425, 374-376 (2003).",
          "stable_url": "https://doi.org/10.1038/nature01997",
          "artifact": {
            "status": "METADATA_ONLY",
            "locator": "https://doi.org/10.1038/nature01997",
            "sha256": null
          },
          "observable_map": "Radio-frequency shifts during solar conjunction constrain the post-Newtonian light-time-delay parameter gamma.",
          "dataset": "Cassini spacecraft radio links around the 2002 solar conjunction.",
          "prediction": "The standard-GR value of the post-Newtonian parameter gamma.",
          "comparison_method": "Relativistic Doppler/time-delay fit with plasma-noise suppression.",
          "uncertainty": "Use the uncertainty and systematic model reported by the source; this ledger does not recompute the fit.",
          "parameter_fit_scope": "Solar-system weak-field propagation with nuisance/systematic modelling as specified in the source.",
          "out_of_sample_status": "INDEPENDENT_DOMAIN_TEST",
          "finding": "The reported estimate is consistent with the standard-GR prediction within the experiment's stated uncertainty.",
          "boundary": "Does not test strong-field dynamics, gravitational radiation, galactic phenomenology, cosmology, quantum gravity, or a foundations-cube composition map."
        },
        {
          "id": "GR_DOUBLE_PULSAR_2021",
          "benchmark": "COMPACT_BINARIES",
          "citation": "M. Kramer et al., Strong-Field Gravity Tests with the Double Pulsar, Physical Review X 11, 041050 (2021).",
          "stable_url": "https://doi.org/10.1103/PhysRevX.11.041050",
          "artifact": {
            "status": "CONTENT_PINNED",
            "locator": "https://arxiv.org/pdf/2112.06795v2",
            "sha256": "9d1b5b4dc304b1d6b1b11059a26d96ca97d1c0d43857523058f973c12bddc6a4"
          },
          "observable_map": "Relativistic timing parameters and orbital decay map to conservative and radiative strong-field predictions.",
          "dataset": "Sixteen years of timing observations of PSR J0737-3039A/B.",
          "prediction": "Multiple post-Keplerian relations and the GR quadrupolar gravitational-radiation prediction for the double-pulsar system.",
          "comparison_method": "Joint pulsar-timing model with propagation, kinematic, and mass-loss corrections described in the source.",
          "uncertainty": "The source reports validation of the GR quadrupolar radiation prediction at 1.3e-4 (95% confidence).",
          "parameter_fit_scope": "A specific relativistic binary system under the timing and correction model in the paper.",
          "out_of_sample_status": "INDEPENDENT_DOMAIN_TEST",
          "finding": "The tested post-Keplerian and radiative predictions are mutually consistent with GR at the reported precision.",
          "boundary": "A high-precision strong-field binary test, not a proof of GR in arbitrary compact objects, cosmology, or the quantum domain."
        },
        {
          "id": "GR_GWTC3_TESTS_2021",
          "benchmark": "GRAVITATIONAL_WAVES",
          "citation": "LIGO Scientific Collaboration, Virgo Collaboration, and KAGRA Collaboration, Tests of General Relativity with GWTC-3, arXiv:2112.06861 (2021).",
          "stable_url": "https://arxiv.org/abs/2112.06861",
          "artifact": {
            "status": "CONTENT_PINNED",
            "locator": "https://arxiv.org/pdf/2112.06861v3",
            "sha256": "10451d67f3cefd425d52e12f78269891f6b1b9a2c25ef83dbca519d2f8b9c1c2"
          },
          "observable_map": "Compact-binary gravitational-wave phase, amplitude, residual, polarization, dispersion, and remnant-consistency observables map to parameterized deviations from GR.",
          "dataset": "The confident compact-binary coalescences used by the GWTC-3 general-relativity tests.",
          "prediction": "GR waveform generation and propagation, tested through multiple parameterized and residual analyses.",
          "comparison_method": "A suite of waveform-consistency, residual, polarization, dispersion, and parameterized-deviation analyses.",
          "uncertainty": "Analysis-specific credible intervals and systematic qualifications are those reported in the source.",
          "parameter_fit_scope": "The event populations, waveform models, priors, and analysis selections specified in the source.",
          "out_of_sample_status": "MULTI_EVENT_DOMAIN_TEST",
          "finding": "The reported tests find no evidence for deviations from GR in the analysed GWTC-3 signals.",
          "boundary": "Consistency within the analysed catalogue and waveform systematics is not proof of GR for every source, propagation environment, polarization model, or cosmological history."
        },
        {
          "id": "GR_GW170817_SPEED_2017",
          "benchmark": "GRAVITATIONAL_WAVES",
          "citation": "B. P. Abbott et al., Gravitational Waves and Gamma-rays from a Binary Neutron Star Merger: GW170817 and GRB 170817A, Astrophysical Journal Letters 848, L13 (2017).",
          "stable_url": "https://arxiv.org/abs/1710.05834",
          "artifact": {
            "status": "CONTENT_PINNED",
            "locator": "https://arxiv.org/pdf/1710.05834v2",
            "sha256": "bf06bd2ae6a23cf7f7092307677c2b681ce02abab3b5bbe37bbce76a8960140a"
          },
          "observable_map": "The gravitational-wave/gamma-ray arrival-time difference constrains relative propagation speed and violations of gravitational versus electromagnetic propagation.",
          "dataset": "GW170817 and GRB 170817A multimessenger observations.",
          "prediction": "Near-luminal gravitational-wave propagation and the associated arrival-time relation, modulo source-emission delay.",
          "comparison_method": "Bound propagation differences using the observed arrival delay and stated assumptions about emission timing and distance.",
          "uncertainty": "The source's bounds are conditional on the stated source-delay and propagation assumptions.",
          "parameter_fit_scope": "One multimessenger binary-neutron-star event and its source-model assumptions.",
          "out_of_sample_status": "INDEPENDENT_MESSENGER_TEST",
          "finding": "The observed delay yields stringent bounds compatible with standard luminal GR propagation in the tested setting.",
          "boundary": "Does not isolate all modified-gravity effects, determine waveform generation by itself, or provide a universal propagation theorem."
        }
      ],
      "benchmark_coverage": [
        {
          "benchmark": "LOCAL_GRAVITY",
          "status": "NOT_REGISTERED",
          "record_ids": []
        },
        {
          "benchmark": "SOLAR_SYSTEM",
          "status": "SUPPORTED_CONTROL",
          "record_ids": [
            "GR_CASSINI_SHAPIRO_2003"
          ]
        },
        {
          "benchmark": "COMPACT_BINARIES",
          "status": "SUPPORTED_CONTROL",
          "record_ids": [
            "GR_DOUBLE_PULSAR_2021"
          ]
        },
        {
          "benchmark": "GRAVITATIONAL_WAVES",
          "status": "SUPPORTED_CONTROL",
          "record_ids": [
            "GR_GWTC3_TESTS_2021",
            "GR_GW170817_SPEED_2017"
          ]
        },
        {
          "benchmark": "GALACTIC_LENSING_DYNAMICS",
          "status": "NOT_REGISTERED",
          "record_ids": []
        },
        {
          "benchmark": "COSMOLOGY",
          "status": "NOT_REGISTERED",
          "record_ids": []
        }
      ],
      "claim_flags": {
        "positive_control_registered": true,
        "prediction_records_registered": true,
        "empirical_comparisons_registered": true,
        "three_benchmark_families_supported": true,
        "selected_from_foundations_cube": false,
        "all_benchmark_families_supported": false,
        "complete_theory_established": false,
        "evidence_for_weyl_gravity": false
      },
      "does_not_establish": [
        "that standard general relativity is complete across all six benchmark families",
        "that the observational papers certify the foundations-cube obligation or interface structure",
        "that agreement in these domains excludes every alternative theory",
        "that standard general relativity is ultraviolet complete or quantum complete",
        "that any candidate Weyl-gravity assembly inherits this empirical support"
      ]
    }
  ],
  "calibration_source": {
    "path": "foundations/standard-gr-observational-control-v1.json",
    "sha256": "b65311888e0852aaf36ae9f95568e0b9aaeeb97758752eeffd02e4ba1d0b26e7"
  },
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
  "numerical_reproducibility_ledger": {
    "unit": "Independent algorithmic reproduction of a mathematical/numerical calculation; this is distinct from empirical comparison and out-of-sample robustness.",
    "records": [
      {
        "id": "BT_L4_L6_INDEPENDENT_SAMPLER_REPRODUCTION",
        "assembly": "BT_EUCLIDEAN_LATTICE_PROGRAMME",
        "dependency_tag": "EUCLIDEAN-SPECTRAL",
        "status": "COARSE_REPRODUCTION_ONLY",
        "algorithms": [
          "zero-mode-projected HMC",
          "independent local random-scan Metropolis"
        ],
        "gate_passed": "all declared finite-volume observables agree within four combined standard errors",
        "precision_gate": "not all declared observables agree within two combined standard errors",
        "maximum_absolute_cross_sampler_z": 3.0404583746200773,
        "finite_size_change_cross_algorithm_z": 1.577545278876236,
        "continuum_status": "NOT_ESTABLISHED",
        "evidence": [
          "REVERSE_PHYSICS_BT_EUCLIDEAN_STEP_SCALING_PREFLIGHT_V1"
        ]
      }
    ]
  },
  "claim_flags": {
    "prototype_assemblies_generated": true,
    "research_camp_lenses_declared": true,
    "selected_cells_content_addressed": true,
    "interface_and_coverage_states_separated": true,
    "at_least_one_cross_cell_interface_certified": true,
    "scoped_carrier_interface_registered": true,
    "numerical_reproducibility_rail_declared": true,
    "empirical_record_schema_declared": true,
    "external_positive_control_registered": true,
    "missing_and_failed_states_separated": true,
    "model_scoped_prediction_assembly_registered": true,
    "second_model_scoped_mannheim_assembly_registered": true,
    "mixed_empirical_result_preserved": true,
    "common_protocol_model_comparison_registered": true,
    "bounded_prediction_chain_established": true,
    "bounded_empirical_agreement_assessed": true,
    "cross_cell_composability_established": false,
    "prediction_chain_established": false,
    "empirical_agreement_assessed": false,
    "complete_observationally_valid_theory_identified": false
  },
  "does_not_establish": [
    "that a research tradition is exhausted by its displayed atlas window or that every researcher named in a lineage endorses every selected cell",
    "that selected cells concern the same physical model or scope",
    "that either certified scoped bridge supplies any unregistered carrier or foundation translation",
    "that direct coverage composes into an end-to-end prediction",
    "that a reduced or finite construction has a controlled continuum limit",
    "that coarse independent-sampler compatibility is precision equivalence, empirical validation, or out-of-sample robustness",
    "that the scoped Euclidean/Krein carrier non-identity forbids every conditional bridge",
    "that any prototype agrees with observations",
    "that the Mannheim NGC 3198 coarse endpoint reproduction or RMS gate overrules its failed SPARC random-error gate",
    "that the NGC 3198 common-protocol ranking selects a complete theory, includes observational systematics, or generalizes beyond one galaxy",
    "that the external standard-GR control is selected from the cube or transfers empirical support to a prototype",
    "that the benchmark catalogue is a complete set of physical tests",
    "a complete theory, a new Lorentzian-causal result, or a quantum lifecycle promotion"
  ],
  "source_atlas_digest": "ff4162c82c7c747ec33ae0ac517ed7370e3bf2547eb77e381e099ebe4d4afce1",
  "canonical_digest": "f3a4640417406185c0b7b526e994be2c3f69b4b2a5b6f37d32d011abcead2eaf"
};
