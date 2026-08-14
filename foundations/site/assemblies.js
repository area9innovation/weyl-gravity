window.THEORY_ASSEMBLY_DATA = {
  "schema_version": "foundational-theory-assembly-atlas-v1",
  "result_id": "FOUNDATIONAL_THEORY_ASSEMBLY_ATLAS_V1",
  "result_kind": "FAIL_CLOSED_THEORY_ASSEMBLY_AND_EMPIRICAL_LEDGER",
  "lifecycle": "VERIFIED_NAVIGATION_ARTIFACT",
  "title": "Model-scoped prediction assemblies, theory prototypes, maturity rails, and calibration controls",
  "created": "2026-08-14",
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
    }
  ],
  "model_scoped_sources": [
    {
      "path": "foundations/results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json",
      "sha256": "f87aa0453de1af594175d1c23c39b48d644064a8582a56785bd9ea4ce279a902"
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
    "that the external standard-GR control is selected from the cube or transfers empirical support to a prototype",
    "that the benchmark catalogue is a complete set of physical tests",
    "a complete theory, a new Lorentzian-causal result, or a quantum lifecycle promotion"
  ],
  "source_atlas_digest": "e4c79e8ec537c2d9f9271d9ccbd042da2a5529b0b5f0f11fa6917cc3af0386cd",
  "canonical_digest": "0911e53250de46266bf587feda146df9321d7da87bef1628eb1ccc7e028da608"
};
