window.MATRIX_EXPLORER_DATA = {
  "schema_version": "foundational-matrix-explorer-data-v2",
  "title": "Reverse Mathematics × Physics Atlas",
  "created": "2026-08-12",
  "dependency_tags": [
    "LOCAL-ALGEBRAIC",
    "REDUCED-MODE",
    "LORENTZIAN-CAUSAL"
  ],
  "axes": [
    {
      "id": "FOUNDATION",
      "question": "Under which rules may the mathematics reason and assert that objects exist?",
      "keys": [
        {
          "id": "CLASSICAL_STANDARD",
          "label": "Classical standard",
          "meaning": "Classical logic with ordinary ZFC-style analysis as the reference regime.",
          "includes": [
            "ordinary classical proofs",
            "standard completed real/complex analysis",
            "unrestricted background Choice when not audited"
          ],
          "plain_meaning": "Mainstream mathematics: classical logic, completed infinite structures, and ordinary analysis, with Choice available unless a proof explicitly avoids it."
        },
        {
          "id": "WEAK_ARITHMETIC",
          "label": "Weak formal base",
          "meaning": "Explicit weak arithmetic or second-order systems used to calibrate proof strength.",
          "includes": [
            "PRA",
            "RCA_0",
            "WKL_0",
            "ACA_0",
            "stronger comprehension when required"
          ],
          "plain_meaning": "Use a deliberately small formal system and ask exactly how much arithmetic or set existence the proof needs."
        },
        {
          "id": "WEAK_CHOICE_ZF",
          "label": "ZF with weakened Choice",
          "meaning": "Classical set theory in which full Choice or Countable Choice is absent or isolated.",
          "includes": [
            "ZF",
            "ZF + DC",
            "no Countable Choice",
            "ultrafilter/Boolean-prime-ideal fragments"
          ],
          "plain_meaning": "Keep classical set theory but remove or isolate principles that choose objects from infinitely many sets at once."
        },
        {
          "id": "CONSTRUCTIVE_COMPUTABLE",
          "label": "Constructive/computable",
          "meaning": "Existence requires constructive or computational content rather than classical existence alone.",
          "includes": [
            "Bishop constructivism",
            "computable analysis",
            "Weihrauch analysis",
            "constructive reformulations"
          ],
          "plain_meaning": "An existence claim must provide a witness, construction, or algorithm—not only show that nonexistence would be contradictory."
        },
        {
          "id": "TOPOS_INTERNAL",
          "label": "Topos/internal",
          "meaning": "Objects and truth are interpreted internally in a selected topos, often with intuitionistic logic.",
          "includes": [
            "Heyting logic",
            "locales",
            "internal algebraic quantum theory",
            "synthetic differential geometry"
          ],
          "plain_meaning": "Do the mathematics inside an alternative logical universe, where truth may be local and classical either/or reasoning may fail."
        },
        {
          "id": "FINITE_DISCRETE",
          "label": "Finite/discrete restriction",
          "meaning": "A finite carrier, finite truncation, or finitist proposal replaces or regulates an infinite structure.",
          "includes": [
            "finite fields",
            "finite modes",
            "finite-dimensional systems",
            "potential-infinity/finitist proposals"
          ],
          "warning": "A finite regulator, finite carrier, and foundational rejection of actual infinity are distinct and must not be conflated.",
          "plain_meaning": "Replace an infinite or continuous system by finite exact data or finitely many modes. This is not automatically the same as rejecting infinity as a foundation."
        }
      ],
      "plain_name": "Mathematical regime",
      "guide_question": "Which rules of reasoning and mathematical existence are we allowing?"
    },
    {
      "id": "CARRIER",
      "question": "What mathematical object carries states, observables, fields, and evolution?",
      "keys": [
        {
          "id": "FINITE_EXACT",
          "label": "Finite exact algebra",
          "meaning": "Finite matrices, rational/integer complexes, or explicitly finite-dimensional algebraic data.",
          "plain_meaning": "Finite matrices, rational arrays, or other finite algebraic data that can be checked exactly."
        },
        {
          "id": "HILBERT_OPERATOR",
          "label": "Hilbert/operator",
          "meaning": "Positive Hilbert spaces, operator domains, spectral data, and their completions.",
          "plain_meaning": "The positive-norm vector spaces and operators used in standard quantum mechanics and spectral theory."
        },
        {
          "id": "KREIN_INDEFINITE",
          "label": "Krein/indefinite",
          "meaning": "Indefinite inner products, fundamental symmetries, and positive companion topologies.",
          "plain_meaning": "A vector space whose inner product can be positive, negative, or zero, as often occurs before unphysical gauge directions are removed."
        },
        {
          "id": "ALGEBRAIC_CSTAR",
          "label": "Algebraic C*-system",
          "meaning": "Observable algebras, states, GNS representations, nets, and algebra-first formulations.",
          "plain_meaning": "Start from an algebra of observable quantities; a state is a rule assigning expectation values rather than primarily a wavefunction."
        },
        {
          "id": "SMOOTH_DISTRIBUTIONAL",
          "label": "Smooth/PDE/distributional",
          "meaning": "Manifolds, bundles, sections, Sobolev or distribution spaces, differential operators, and Green theory.",
          "plain_meaning": "Continuum fields on space or spacetime, including derivatives, PDEs, Sobolev spaces, generalized functions, and Green operators."
        },
        {
          "id": "LOCALIC_SYNTHETIC",
          "label": "Localic/synthetic/internal",
          "meaning": "Locales, internal algebra objects, formal manifolds, and synthetic smooth structures.",
          "plain_meaning": "Describe spaces through regions, logical relations, or internal geometry instead of beginning with a set of individual points."
        }
      ],
      "plain_name": "Mathematical carrier",
      "guide_question": "What kind of mathematical object holds the states, fields, and observables?"
    },
    {
      "id": "REFINED_OBLIGATION",
      "question": "Which precise physical or theorem-level job is established?",
      "keys": [
        {
          "id": "KINEMATICS_OBSERVABLES",
          "label": "Kinematics/observables",
          "meaning": "Define degrees of freedom, observables, commutation structure, and configurations.",
          "plain_meaning": "Say what the possible configurations and measurable quantities are before specifying how they evolve."
        },
        {
          "id": "STATE_EXISTENCE",
          "label": "State existence",
          "meaning": "Construct at least one normalized or algebraically valid state in the declared carrier.",
          "plain_meaning": "Show that at least one mathematically valid state actually exists."
        },
        {
          "id": "STATE_REPRESENTATION",
          "label": "State representation",
          "meaning": "Relate states to vectors, density operators, measures, valuations, or GNS data.",
          "plain_meaning": "Explain how an abstract state is encoded—for example by a vector, density matrix, measure, valuation, or GNS construction."
        },
        {
          "id": "PROBABILITY_RULE",
          "label": "Probability rule",
          "meaning": "Construct or derive normalized event probabilities or a Born-type rule.",
          "plain_meaning": "Turn states and events into normalized probabilities, such as a Born-type prediction rule."
        },
        {
          "id": "PHYSICAL_STATE_SELECTION",
          "label": "Physical state selection",
          "meaning": "Select or obstruct a physically distinguished vacuum, thermal, Hadamard, or other state.",
          "plain_meaning": "Explain why a particular vacuum, thermal, Hadamard, or other state should count as physically distinguished."
        },
        {
          "id": "GENERATOR_SPECTRAL_DYNAMICS",
          "label": "Generator/spectral dynamics",
          "meaning": "Construct generators, spectra, one-parameter groups, or algebra automorphisms.",
          "plain_meaning": "Construct what generates time evolution and, where relevant, identify its allowed frequencies or energy spectrum."
        },
        {
          "id": "EVOLUTION_WELLPOSEDNESS",
          "label": "Evolution/well-posedness",
          "meaning": "Prove existence, uniqueness, stability, or computability of evolution in a stated topology.",
          "plain_meaning": "Show that admissible initial data produce a solution that exists, is unique, and changes stably or computably with the data."
        },
        {
          "id": "CAUSAL_PROPAGATION_GREEN",
          "label": "Causal propagation/Green",
          "meaning": "Construct advanced/retarded maps and prove finite propagation or causal support.",
          "plain_meaning": "Show that disturbances propagate within the permitted causal region and construct retarded or advanced response maps."
        },
        {
          "id": "GAUGE_BV_COHOMOLOGY",
          "label": "Gauge/BV/cohomology",
          "meaning": "Handle gauge symmetry, BRST/BV complexes, residual cohomology, and gauge independence.",
          "plain_meaning": "Handle redundant gauge descriptions consistently and identify the quantities or states that remain physically meaningful."
        },
        {
          "id": "INTERACTION_CONSTRUCTION",
          "label": "Interaction construction",
          "meaning": "Construct a nontrivial interaction, deformation, or interacting product.",
          "plain_meaning": "Build a genuine coupling or nonlinear theory rather than only a collection of free, noninteracting fields."
        },
        {
          "id": "COUNTERTERM_CLASSIFICATION",
          "label": "Counterterm classification",
          "meaning": "Classify allowed local counterterms before computing coefficients.",
          "plain_meaning": "List every local correction that quantum calculations are allowed to require before attempting to calculate its coefficient."
        },
        {
          "id": "ANOMALY_CLASSIFICATION",
          "label": "Anomaly classification",
          "meaning": "Classify possible local anomalies and consistency conditions.",
          "plain_meaning": "List the possible ways a classical symmetry or consistency condition could fail after quantization."
        },
        {
          "id": "RENORMALIZED_PRODUCTS",
          "label": "Renormalized products",
          "meaning": "Construct renormalized time-ordered or interacting products.",
          "plain_meaning": "Define products and correlation functions that would otherwise be singular when fields meet at the same spacetime point."
        },
        {
          "id": "QME_RESTORATION",
          "label": "QME restoration",
          "meaning": "Compute or cancel the breaking and restore the local quantum master equation.",
          "plain_meaning": "Repair the quantum master equation, the BV consistency condition that encodes quantum gauge symmetry."
        },
        {
          "id": "RESIDUAL_QUANTUM_TRANSFER",
          "label": "Residual quantum transfer",
          "meaning": "Transfer a restored quantum correction to the residual complex.",
          "plain_meaning": "After quantum consistency is restored, transfer the correction to the smaller complex that represents the surviving physical content."
        },
        {
          "id": "RECONSTRUCTION_LIMITS",
          "label": "Reconstruction/limits",
          "meaning": "Prove operational reconstruction, comparison, continuum-limit, or empirical-equivalence results.",
          "plain_meaning": "Connect the formulation back to operational predictions, a continuum or standard theory, or a demonstrated notion of empirical equivalence."
        }
      ],
      "plain_name": "Physical obligation",
      "guide_question": "Which physical job must the theory perform?"
    }
  ],
  "groups": [
    {
      "id": "STATES",
      "label": "States and probability",
      "obligations": [
        "STATE_EXISTENCE",
        "STATE_REPRESENTATION",
        "PROBABILITY_RULE",
        "PHYSICAL_STATE_SELECTION"
      ]
    },
    {
      "id": "DYNAMICS",
      "label": "Dynamics and causality",
      "obligations": [
        "GENERATOR_SPECTRAL_DYNAMICS",
        "EVOLUTION_WELLPOSEDNESS",
        "CAUSAL_PROPAGATION_GREEN"
      ]
    },
    {
      "id": "GAUGE",
      "label": "Kinematics and gauge",
      "obligations": [
        "KINEMATICS_OBSERVABLES",
        "GAUGE_BV_COHOMOLOGY"
      ]
    },
    {
      "id": "QUANTUM",
      "label": "Interaction and quantum consistency",
      "obligations": [
        "INTERACTION_CONSTRUCTION",
        "COUNTERTERM_CLASSIFICATION",
        "ANOMALY_CLASSIFICATION",
        "RENORMALIZED_PRODUCTS",
        "QME_RESTORATION",
        "RESIDUAL_QUANTUM_TRANSFER"
      ]
    },
    {
      "id": "LIMITS",
      "label": "Reconstruction and limits",
      "obligations": [
        "RECONSTRUCTION_LIMITS"
      ]
    }
  ],
  "statuses": [
    {
      "id": "LOCAL_RESULT",
      "meaning": "A bounded local result directly supports this refined obligation."
    },
    {
      "id": "LITERATURE_RESULT",
      "meaning": "A reviewed source directly treats this refined obligation within its boundary."
    },
    {
      "id": "PIECES_ONLY",
      "meaning": "Relevant ingredients exist but do not compose the refined result."
    },
    {
      "id": "PRIORITY_GAP",
      "meaning": "A child-specific review records a coherent current-programme gap."
    },
    {
      "id": "NOT_MAPPED",
      "meaning": "No coverage classification is made; this is not a literature-absence claim."
    }
  ],
  "migration_statuses": [
    {
      "id": "EXACT_PARENT_TRANSFER",
      "meaning": "The unsplit v0 obligation transfers exactly."
    },
    {
      "id": "CAPABILITY_QUALIFIED",
      "meaning": "An explicit evidence capability supports the split child."
    },
    {
      "id": "REVIEWED_OVERLAY",
      "meaning": "A child-specific v1 overlay supplies the classification."
    },
    {
      "id": "REVIEWED_NO_TRANSFER",
      "meaning": "The named parent evidence was reviewed and does not support the child."
    },
    {
      "id": "REVIEWED_CHILD_GAP",
      "meaning": "An evidence-free broad parent gap was decomposed into this explicit child gap."
    },
    {
      "id": "NOT_REVIEWED",
      "meaning": "The coordinate was not emitted by cube v2, so no migration review was required."
    }
  ],
  "counts": {
    "cartesian_total": 576,
    "emitted": 452,
    "coverage_classified": 371,
    "qualified": 371,
    "migration_reviewed": 452,
    "migration_pending": 0,
    "migration_unresolved": 0,
    "reviewed_no_transfer": 88,
    "not_mapped": 205,
    "synthetic_not_mapped": 124,
    "status_counts": {
      "LITERATURE_RESULT": 93,
      "LOCAL_RESULT": 88,
      "NOT_MAPPED": 205,
      "PIECES_ONLY": 160,
      "PRIORITY_GAP": 30
    },
    "migration_status_counts": {
      "CAPABILITY_QUALIFIED": 257,
      "EXACT_PARENT_TRANSFER": 72,
      "NOT_REVIEWED": 124,
      "REVIEWED_CHILD_GAP": 24,
      "REVIEWED_NO_TRANSFER": 88,
      "REVIEWED_OVERLAY": 11
    },
    "evidence_records": 69
  },
  "cells": [
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "FINITE_EXACT",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "An exact two-qubit matrix model provides observables, density states, a star derivation, and an entangling interaction. For this obligation, the evidence directly defines observables, configurations, or the carrier's algebraic structure.",
      "boundary": "The source works in ordinary classical mathematics and is not a foundational-strength audit. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a full Weyl observable algebra and its domains.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "hardy-2001",
        "chiribella-dariano-perinotti-2011"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Finite-dimensional quantum carriers are reconstructed from operational postulates.",
      "boundary": "No infinite-dimensional QFT or foundational-strength classification.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "hardy-2001",
        "chiribella-dariano-perinotti-2011"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "esmeral-ferrer-wagner-2015",
        "bateman-turok-2026"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Krein geometry and ghost parity provide an indefinite carrier architecture.",
      "boundary": "State selection and operator-domain completion remain open.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "esmeral-ferrer-wagner-2015",
        "bateman-turok-2026"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "haag-kastler-1964"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Algebra-first local observables provide a kinematic formulation of QFT.",
      "boundary": "Representation, states, topology, and dynamics remain additional obligations.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "haag-kastler-1964"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "barnich-brandt-henneaux-2000",
        "brunetti-fredenhagen-verch-2001",
        "fredenhagen-rejzner-2011",
        "brunetti-fredenhagen-rejzner-2013"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Local BRST, locally covariant QFT, and perturbative BV give a standard smooth/distributional architecture across all six obligations. For this obligation, the evidence directly defines observables, configurations, or the carrier's algebraic structure.",
      "boundary": "The source works in ordinary classical mathematics and is not a foundational-strength audit. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a full Weyl observable algebra and its domains.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "barnich-brandt-henneaux-2000",
        "brunetti-fredenhagen-verch-2001",
        "fredenhagen-rejzner-2011",
        "brunetti-fredenhagen-rejzner-2013"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Topos quantum theory supplies localic spectra, state measures, internal group dynamics, and comparisons between context topoi. For this obligation, the evidence directly defines observables, configurations, or the carrier's algebraic structure.",
      "boundary": "The source works in ordinary classical mathematics and is not a foundational-strength audit. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a full Weyl observable algebra and its domains.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "FINITE_EXACT",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Every displayed operation is a finite loop over reduced rational pairs, providing a primitive-recursive sufficiency witness. For this obligation, the evidence directly defines observables, configurations, or the carrier's algebraic structure.",
      "boundary": "No reverse implication over a fixed weak base is inferred unless the cited source states one. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a full Weyl observable algebra and its domains.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "PIECES_ONLY",
      "evidence": [
        "brown-simpson-1986",
        "humphreys-simpson-1999"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Reverse functional analysis calibrates separation principles used around Hilbert/Banach carriers.",
      "boundary": "No relativistic gauge theory is encoded in the cited reversals.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "brown-simpson-1986",
        "humphreys-simpson-1999"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Every fixed Krein mode cutoff reduces to finite exact sign and positivity checks.",
      "boundary": "The infinite completion is not classified over weak arithmetic.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "FINITE_EXACT",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Named finite matrices and finite BV arrays are constructed without selecting from arbitrary families. For this obligation, the evidence directly defines observables, configurations, or the carrier's algebraic structure.",
      "boundary": "An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a full Weyl observable algebra and its domains.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "blackadar-farah-karagila-2026"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Substantial Hilbert and operator theory can be developed in ZF without Countable Choice.",
      "boundary": "Arbitrary-space pathologies must not be transferred to explicit carriers without proof.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "blackadar-farah-karagila-2026"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "The explicitly labelled Krein symmetry and Fock lift are constructible in ZF without Countable Choice.",
      "boundary": "This does not classify arbitrary Krein spaces.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LOCAL_RESULT",
      "evidence": [
        "blackadar-farah-2026",
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "A separable detector algebra and robust ZF algebraic operations are available.",
      "boundary": "The full orbit algebra and AQFT net are not certified.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "blackadar-farah-2026",
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "FINITE_EXACT",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "The explicit Gaussian-rational interaction is executable using finite data, while the finite BV result remains a separate proof artifact. For this obligation, the evidence directly defines observables, configurations, or the carrier's algebraic structure.",
      "boundary": "Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a full Weyl observable algebra and its domains.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "bridges-svozil-2000"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Constructive Hilbert subspaces, projections, and quantum logic have been studied.",
      "boundary": "No constructive dynamics or QFT.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "bridges-svozil-2000"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "coquand-spitters-2009",
        "henry-2014"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Constructive localic Gelfand duality covers commutative unital and non-unital cases.",
      "boundary": "No noncommutative interacting field algebra is constructed.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "coquand-spitters-2009",
        "henry-2014"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Constructive localic spectra, valuations, and internal one-parameter dynamics form a coherent non-point-set quantum fragment. For this obligation, the evidence directly defines observables, configurations, or the carrier's algebraic structure.",
      "boundary": "Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a full Weyl observable algebra and its domains.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "FINITE_EXACT",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Contextual topos methods internalize commutative algebra, spectra, state measures, and one-parameter dynamics from operator-algebraic input. For this obligation, the evidence directly defines observables, configurations, or the carrier's algebraic structure.",
      "boundary": "External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. An algebraic architecture does not by itself select representations or physical states. Still open here: a full Weyl observable algebra and its domains.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "grinkevich-1996",
        "barnich-brandt-henneaux-2000"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Synthetic general relativity supplies formal smooth geometry, while probability and BV/renormalization remain separate classical ingredients. For this obligation, the evidence directly defines observables, configurations, or the carrier's algebraic structure.",
      "boundary": "External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a full Weyl observable algebra and its domains.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "grinkevich-1996",
        "barnich-brandt-henneaux-2000"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "heunen-landsman-spitters-2009"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "An algebraic quantum system can be represented internally with Heyting logic and a localic spectrum.",
      "boundary": "No Weyl field theory or empirical superiority follows.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "gibbons-hoffman-wootters-2004"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Prime-power finite-field phase spaces support discrete Wigner kinematics.",
      "boundary": "The quantum carrier remains complex and no continuum theory follows.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "hardy-2001",
        "chiribella-dariano-perinotti-2011"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Finite-dimensional Hilbert kinematics is reconstructed operationally.",
      "boundary": "The complex scalar continuum remains and infinite QFT is outside scope.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "hardy-2001",
        "chiribella-dariano-perinotti-2011"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Finite Krein truncations have explicit sign, involution, and positivity witnesses.",
      "boundary": "The completed infinite carrier and physical state remain separate.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "The finite matrix algebra is a concrete C*-system, while lattice gauge work adds local constraints and truncation architecture. For this obligation, the evidence directly defines observables, configurations, or the carrier's algebraic structure.",
      "boundary": "Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. An algebraic architecture does not by itself select representations or physical states. Still open here: a full Weyl observable algebra and its domains.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009",
        "dittrich-2012"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Lattice gauge and discrete-gravity work supplies dynamics, constraints, symmetry-restoration, and explicit continuum-comparison obligations. For this obligation, the evidence directly defines observables, configurations, or the carrier's algebraic structure.",
      "boundary": "Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a full Weyl observable algebra and its domains.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009",
        "dittrich-2012"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "KINEMATICS_OBSERVABLES",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "KINEMATICS_OBSERVABLES",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Short-poset topoi, finite contextual entropy, and categorical protocols give finite internal/contextual kinematics, states, dynamics, and reconstruction. For this obligation, the evidence directly defines observables, configurations, or the carrier's algebraic structure.",
      "boundary": "Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a full Weyl observable algebra and its domains.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "FINITE_EXACT",
      "obligation": "STATE_EXISTENCE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "STATE_EXISTENCE",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "hardy-2001",
        "chiribella-dariano-perinotti-2011"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Physical state selection in Weyl QFT is not supplied.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "hardy-2001",
        "chiribella-dariano-perinotti-2011"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "STATE_EXISTENCE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
        "bateman-turok-2026"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. State existence and a conditional nonselection theorem do not supply a physical Weyl state or generalized Born rule.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
        "bateman-turok-2026"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "STATE_EXISTENCE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
        "haag-kastler-1964"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. A mathematical state/GNS result does not select a physical Weyl or thermodynamic state.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
        "haag-kastler-1964"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "STATE_EXISTENCE",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "brunetti-fredenhagen-verch-2001"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "brunetti-fredenhagen-verch-2001"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "STATE_EXISTENCE",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "harding-heunen-2019"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "FINITE_EXACT",
      "obligation": "STATE_EXISTENCE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "STATE_EXISTENCE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "STATE_EXISTENCE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "STATE_EXISTENCE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "STATE_EXISTENCE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "STATE_EXISTENCE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "FINITE_EXACT",
      "obligation": "STATE_EXISTENCE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "STATE_EXISTENCE",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "neumann-pape-streicher-2018",
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "STATE_EXISTENCE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The carrier does not select a unique physical state; singular states and dynamically selected Born functionals remain open.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "STATE_EXISTENCE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No thermodynamic or dynamically selected physical state is proved.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "STATE_EXISTENCE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "STATE_EXISTENCE",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "coquand-spitters-2009"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "coquand-spitters-2009"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "FINITE_EXACT",
      "obligation": "STATE_EXISTENCE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "STATE_EXISTENCE",
      "status": "PIECES_ONLY",
      "evidence": [
        "richman-bridges-1999"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is not a constructive derivation of all quantum probability or state selection.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "richman-bridges-1999"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "STATE_EXISTENCE",
      "status": "PIECES_ONLY",
      "evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "STATE_EXISTENCE",
      "status": "PIECES_ONLY",
      "evidence": [
        "coquand-spitters-2009",
        "richman-bridges-1999"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No physical state-selection chain joins them.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "coquand-spitters-2009",
        "richman-bridges-1999"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "STATE_EXISTENCE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "STATE_EXISTENCE",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "coquand-spitters-2009"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "coquand-spitters-2009"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "FINITE_EXACT",
      "obligation": "STATE_EXISTENCE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "STATE_EXISTENCE",
      "status": "PIECES_ONLY",
      "evidence": [
        "doring-2008",
        "harding-heunen-2019"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "doring-2008",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "STATE_EXISTENCE",
      "status": "PIECES_ONLY",
      "evidence": [
        "gottschalk-2004",
        "harding-heunen-2019"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "gottschalk-2004",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "STATE_EXISTENCE",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "harding-heunen-2019"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. An algebraic architecture does not by itself select representations or physical states. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "STATE_EXISTENCE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Synthetic classical geometry and local BRST classification do not construct or represent states, probabilities, or a physical state-selection rule. No reviewed record in the batch constructs a state in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "grinkevich-1996",
        "barnich-brandt-henneaux-2000"
      ],
      "migration_rationale": "Synthetic classical geometry and local BRST classification do not construct or represent states, probabilities, or a physical state-selection rule. No reviewed record in the batch constructs a state in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "STATE_EXISTENCE",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Logical truth values and physical probabilities must not be conflated.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "STATE_EXISTENCE",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "gibbons-hoffman-wootters-2004"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is not a general physical state-selection theorem.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "STATE_EXISTENCE",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "STATE_EXISTENCE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "STATE_EXISTENCE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. An algebraic architecture does not by itself select representations or physical states. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "STATE_EXISTENCE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Lattice constraints and continuum-comparison programmes do not by themselves construct the four unresolved state/probability children. No reviewed record in the batch constructs a state in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009",
        "dittrich-2012"
      ],
      "migration_rationale": "Lattice constraints and continuum-comparison programmes do not by themselves construct the four unresolved state/probability children. No reviewed record in the batch constructs a state in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "STATE_EXISTENCE",
      "status": "PIECES_ONLY",
      "evidence": [
        "harding-heunen-2019",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State existence': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "harding-heunen-2019",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "FINITE_EXACT",
      "obligation": "STATE_REPRESENTATION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "STATE_REPRESENTATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "hardy-2001",
        "chiribella-dariano-perinotti-2011"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Physical state selection in Weyl QFT is not supplied.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "hardy-2001",
        "chiribella-dariano-perinotti-2011"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "STATE_REPRESENTATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "bateman-turok-2026",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. State existence and a conditional nonselection theorem do not supply a physical Weyl state or generalized Born rule.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "bateman-turok-2026",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "STATE_REPRESENTATION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1",
        "haag-kastler-1964",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. A mathematical state/GNS result does not select a physical Weyl or thermodynamic state.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1",
        "haag-kastler-1964",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "STATE_REPRESENTATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "brunetti-fredenhagen-verch-2001"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "brunetti-fredenhagen-verch-2001"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "STATE_REPRESENTATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "harding-heunen-2019"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "FINITE_EXACT",
      "obligation": "STATE_REPRESENTATION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "STATE_REPRESENTATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "STATE_REPRESENTATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "STATE_REPRESENTATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "STATE_REPRESENTATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "STATE_REPRESENTATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "FINITE_EXACT",
      "obligation": "STATE_REPRESENTATION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "STATE_REPRESENTATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "neumann-pape-streicher-2018",
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "STATE_REPRESENTATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The carrier does not select a unique physical state; singular states and dynamically selected Born functionals remain open.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "STATE_REPRESENTATION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No thermodynamic or dynamically selected physical state is proved.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "STATE_REPRESENTATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "STATE_REPRESENTATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "coquand-spitters-2009"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "coquand-spitters-2009"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "FINITE_EXACT",
      "obligation": "STATE_REPRESENTATION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "STATE_REPRESENTATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "richman-bridges-1999"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is not a constructive derivation of all quantum probability or state selection.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "richman-bridges-1999"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "STATE_REPRESENTATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: PT-symmetric and pseudo-Hermitian spectral structure does not supply state representation, normalized probabilities, or causal Green propagation. No reviewed record in the batch supplies the required state representation in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001"
      ],
      "migration_rationale": "PT-symmetric and pseudo-Hermitian spectral structure does not supply state representation, normalized probabilities, or causal Green propagation. No reviewed record in the batch supplies the required state representation in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "STATE_REPRESENTATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "richman-bridges-1999",
        "coquand-spitters-2009"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No physical state-selection chain joins them.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "richman-bridges-1999",
        "coquand-spitters-2009"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "STATE_REPRESENTATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "STATE_REPRESENTATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "coquand-spitters-2009"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "coquand-spitters-2009"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "FINITE_EXACT",
      "obligation": "STATE_REPRESENTATION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "STATE_REPRESENTATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "doring-2008",
        "harding-heunen-2019"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "doring-2008",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "STATE_REPRESENTATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "harding-heunen-2019",
        "gottschalk-2004"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "harding-heunen-2019",
        "gottschalk-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "STATE_REPRESENTATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "harding-heunen-2019"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. An algebraic architecture does not by itself select representations or physical states. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "STATE_REPRESENTATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Synthetic classical geometry and local BRST classification do not construct or represent states, probabilities, or a physical state-selection rule. No reviewed record in the batch supplies the required state representation in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "grinkevich-1996",
        "barnich-brandt-henneaux-2000"
      ],
      "migration_rationale": "Synthetic classical geometry and local BRST classification do not construct or represent states, probabilities, or a physical state-selection rule. No reviewed record in the batch supplies the required state representation in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "STATE_REPRESENTATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Logical truth values and physical probabilities must not be conflated.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "STATE_REPRESENTATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "gibbons-hoffman-wootters-2004"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is not a general physical state-selection theorem.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "STATE_REPRESENTATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "gibbons-hoffman-wootters-2004",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "STATE_REPRESENTATION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "STATE_REPRESENTATION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. An algebraic architecture does not by itself select representations or physical states. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "STATE_REPRESENTATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Lattice constraints and continuum-comparison programmes do not by themselves construct the four unresolved state/probability children. No reviewed record in the batch supplies the required state representation in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009",
        "dittrich-2012"
      ],
      "migration_rationale": "Lattice constraints and continuum-comparison programmes do not by themselves construct the four unresolved state/probability children. No reviewed record in the batch supplies the required state representation in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "STATE_REPRESENTATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'State representation': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "FINITE_EXACT",
      "obligation": "PROBABILITY_RULE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "PROBABILITY_RULE",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "hardy-2001",
        "chiribella-dariano-perinotti-2011"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Physical state selection in Weyl QFT is not supplied.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "hardy-2001",
        "chiribella-dariano-perinotti-2011"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "PROBABILITY_RULE",
      "status": "PIECES_ONLY",
      "evidence": [
        "bateman-turok-2026",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. State existence and a conditional nonselection theorem do not supply a physical Weyl state or generalized Born rule.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "bateman-turok-2026",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "PROBABILITY_RULE",
      "status": "PIECES_ONLY",
      "evidence": [
        "haag-kastler-1964",
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. A mathematical state/GNS result does not select a physical Weyl or thermodynamic state.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "haag-kastler-1964",
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PROBABILITY_RULE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: AQFT state-space and BV-renormalization architecture does not derive a normalized probability rule for the Weyl metric theory. No reviewed record in the batch derives the required normalized event-probability rule.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "barnich-brandt-henneaux-2000",
        "brunetti-fredenhagen-verch-2001",
        "fredenhagen-rejzner-2011",
        "brunetti-fredenhagen-rejzner-2013"
      ],
      "migration_rationale": "AQFT state-space and BV-renormalization architecture does not derive a normalized probability rule for the Weyl metric theory. No reviewed record in the batch derives the required normalized event-probability rule.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "PROBABILITY_RULE",
      "status": "PIECES_ONLY",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "harding-heunen-2019"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "FINITE_EXACT",
      "obligation": "PROBABILITY_RULE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "PROBABILITY_RULE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "PROBABILITY_RULE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "PROBABILITY_RULE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PROBABILITY_RULE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "PROBABILITY_RULE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "FINITE_EXACT",
      "obligation": "PROBABILITY_RULE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "PROBABILITY_RULE",
      "status": "PIECES_ONLY",
      "evidence": [
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "PROBABILITY_RULE",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The carrier does not select a unique physical state; singular states and dynamically selected Born functionals remain open.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "PROBABILITY_RULE",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No thermodynamic or dynamically selected physical state is proved.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PROBABILITY_RULE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "PROBABILITY_RULE",
      "status": "PIECES_ONLY",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "coquand-spitters-2009"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "coquand-spitters-2009"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "FINITE_EXACT",
      "obligation": "PROBABILITY_RULE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "PROBABILITY_RULE",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "richman-bridges-1999"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is not a constructive derivation of all quantum probability or state selection.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "richman-bridges-1999"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "PROBABILITY_RULE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: PT-symmetric and pseudo-Hermitian spectral structure does not supply state representation, normalized probabilities, or causal Green propagation. No reviewed record in the batch derives the required normalized event-probability rule.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001"
      ],
      "migration_rationale": "PT-symmetric and pseudo-Hermitian spectral structure does not supply state representation, normalized probabilities, or causal Green propagation. No reviewed record in the batch derives the required normalized event-probability rule.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "PROBABILITY_RULE",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "richman-bridges-1999",
        "coquand-spitters-2009"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No physical state-selection chain joins them.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "richman-bridges-1999",
        "coquand-spitters-2009"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PROBABILITY_RULE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "PROBABILITY_RULE",
      "status": "PIECES_ONLY",
      "evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "FINITE_EXACT",
      "obligation": "PROBABILITY_RULE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "PROBABILITY_RULE",
      "status": "PIECES_ONLY",
      "evidence": [
        "doring-2008",
        "harding-heunen-2019"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "doring-2008",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "PROBABILITY_RULE",
      "status": "PIECES_ONLY",
      "evidence": [
        "gottschalk-2004",
        "harding-heunen-2019"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "gottschalk-2004",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "PROBABILITY_RULE",
      "status": "PIECES_ONLY",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "harding-heunen-2019"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. An algebraic architecture does not by itself select representations or physical states. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PROBABILITY_RULE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Synthetic classical geometry and local BRST classification do not construct or represent states, probabilities, or a physical state-selection rule. No reviewed record in the batch derives the required normalized event-probability rule.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "grinkevich-1996",
        "barnich-brandt-henneaux-2000"
      ],
      "migration_rationale": "Synthetic classical geometry and local BRST classification do not construct or represent states, probabilities, or a physical state-selection rule. No reviewed record in the batch derives the required normalized event-probability rule.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "PROBABILITY_RULE",
      "status": "PIECES_ONLY",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Logical truth values and physical probabilities must not be conflated.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "PROBABILITY_RULE",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "gibbons-hoffman-wootters-2004"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is not a general physical state-selection theorem.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "PROBABILITY_RULE",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "PROBABILITY_RULE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "PROBABILITY_RULE",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. An algebraic architecture does not by itself select representations or physical states. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PROBABILITY_RULE",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Lattice constraints and continuum-comparison programmes do not by themselves construct the four unresolved state/probability children. No reviewed record in the batch derives the required normalized event-probability rule.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009",
        "dittrich-2012"
      ],
      "migration_rationale": "Lattice constraints and continuum-comparison programmes do not by themselves construct the four unresolved state/probability children. No reviewed record in the batch derives the required normalized event-probability rule.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "PROBABILITY_RULE",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "abramsky-coecke-2004",
        "harding-heunen-2019",
        "constantin-doring-2020"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Probability rule': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "abramsky-coecke-2004",
        "harding-heunen-2019",
        "constantin-doring-2020"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "FINITE_EXACT",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "hardy-2001",
        "chiribella-dariano-perinotti-2011"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Physical state selection in Weyl QFT is not supplied.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "hardy-2001",
        "chiribella-dariano-perinotti-2011"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
        "bateman-turok-2026",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. State existence and a conditional nonselection theorem do not supply a physical Weyl state or generalized Born rule.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
        "bateman-turok-2026",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
        "haag-kastler-1964",
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. A mathematical state/GNS result does not select a physical Weyl or thermodynamic state.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
        "haag-kastler-1964",
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "brunetti-fredenhagen-verch-2001"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "brunetti-fredenhagen-verch-2001"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "harding-heunen-2019"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "FINITE_EXACT",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "FINITE_EXACT",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "neumann-pape-streicher-2018"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "neumann-pape-streicher-2018"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The carrier does not select a unique physical state; singular states and dynamically selected Born functionals remain open.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No thermodynamic or dynamically selected physical state is proved.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "heunen-landsman-spitters-2009"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "FINITE_EXACT",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "richman-bridges-1999"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is not a constructive derivation of all quantum probability or state selection.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "richman-bridges-1999"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "richman-bridges-1999"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No physical state-selection chain joins them.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "richman-bridges-1999"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "heunen-landsman-spitters-2009"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "FINITE_EXACT",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "doring-2008",
        "harding-heunen-2019"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "doring-2008",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "gottschalk-2004",
        "harding-heunen-2019"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "gottschalk-2004",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "harding-heunen-2019"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. An algebraic architecture does not by itself select representations or physical states. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Synthetic classical geometry and local BRST classification do not construct or represent states, probabilities, or a physical state-selection rule. No reviewed record in the batch selects a vacuum, thermal, Hadamard, or other physical state.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "grinkevich-1996",
        "barnich-brandt-henneaux-2000"
      ],
      "migration_rationale": "Synthetic classical geometry and local BRST classification do not construct or represent states, probabilities, or a physical state-selection rule. No reviewed record in the batch selects a vacuum, thermal, Hadamard, or other physical state.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Logical truth values and physical probabilities must not be conflated.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "gibbons-hoffman-wootters-2004"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is not a general physical state-selection theorem.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. An algebraic architecture does not by itself select representations or physical states. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Lattice constraints and continuum-comparison programmes do not by themselves construct the four unresolved state/probability children. No reviewed record in the batch selects a vacuum, thermal, Hadamard, or other physical state.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009",
        "dittrich-2012"
      ],
      "migration_rationale": "Lattice constraints and continuum-comparison programmes do not by themselves construct the four unresolved state/probability children. No reviewed record in the batch selects a vacuum, thermal, Hadamard, or other physical state.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Physical state selection': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a physically selected Weyl state and probability interpretation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "FINITE_EXACT",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No general spectral measure, determinant, or interacting dynamics.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1",
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No other conformal generator, interaction, causal propagation, or nonlinear Bateman-Turok dynamics is exponentiated.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1",
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This compact-cylinder C*-dynamics is not an interacting AQFT net or full-orbit dynamics.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The exact checker proves no PDE existence and no full BV propagator.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "brenna-flori-2012",
        "harding-heunen-2019",
        "heunen-landsman-spitters-2009"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "brenna-flori-2012",
        "harding-heunen-2019",
        "heunen-landsman-spitters-2009"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "FINITE_EXACT",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
      ],
      "summary": "Finite Laurent degrees give exact cylinder-wave generators.",
      "boundary": "This is a fixed finite fixture, not a completed evolution theorem.",
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "REVIEWED_V1_OVERLAY",
      "migration_status": "REVIEWED_OVERLAY",
      "migration_evidence": [
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
      ],
      "migration_rationale": "A child-specific v1 review overrides the mechanical migration.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1",
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2",
        "FOUNDATIONAL_CODED_WAVE_FRONTIER_V2"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "The declared fast-Cauchy energy carrier has an RCA_0-coded real-time isometric one-parameter group; no generator domain or spectral theorem is claimed.",
      "boundary": "The local RCA_0 upper bound is restricted to the declared fast-Cauchy polygonal energy representation; it is neither a reversal nor a spacetime causal theorem.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "brown-simpson-1986",
        "humphreys-simpson-1999",
        "humphreys-simpson-1996",
        "brattka-2008"
      ],
      "migration_rationale": "Logical-strength results for separation and Hahn-Banach principles do not construct a generator, well-posed evolution, or a causal Green operator. No reviewed record in the batch constructs the required generator or spectral dynamics in this refined coordinate.",
      "research_revision": {
        "atlas": "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "kind": "STATUS_CHANGE",
        "previous_status": "NOT_MAPPED"
      },
      "coded_wave_revision": {
        "frontier": "FOUNDATIONAL_CODED_WAVE_FRONTIER_V2",
        "status_change": true,
        "evidence_overlay": false,
        "previous_status": "PIECES_ONLY"
      },
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "PIECES_ONLY",
      "evidence": [
        "blackadar-farah-2026",
        "brunetti-fredenhagen-verch-2001"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. An algebraic architecture does not by itself select representations or physical states. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "blackadar-farah-2026",
        "brunetti-fredenhagen-verch-2001"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse-mathematical PDE theorem has been proved.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "FINITE_EXACT",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. General spectral measures and interacting dynamics remain open.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1",
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This proves no interacting, nonlinear, or Lorentzian-causal dynamics.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1",
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Nonlinear/full-orbit Bateman-Turok dynamics, local normality, and interacting evolution remain open.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No choice-free continuum PDE theorem is claimed.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "FINITE_EXACT",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "neumann-pape-streicher-2018"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "neumann-pape-streicher-2018"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "neumann-pape-streicher-2018"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. An algebraic architecture does not by itself select representations or physical states. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "neumann-pape-streicher-2018"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "PIECES_ONLY",
      "evidence": [
        "selivanova-selivanov-2013",
        "selivanova-selivanov-2018"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "A represented symmetric-hyperbolic solution operator is computable, but an explicit computable generator/domain/spectral theorem is still missing.",
      "boundary": "This classification is restricted to the cited object and foundational framework; it does not transfer to stronger causal, continuum, choice-free, or reverse-mathematical claims.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks a constructive smooth-wave generator with declared domains and representation.",
      "research_revision": {
        "atlas": "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "kind": "STATUS_CHANGE",
        "previous_status": "PRIORITY_GAP"
      },
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "brenna-flori-2012",
        "heunen-landsman-spitters-2009"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "brenna-flori-2012",
        "heunen-landsman-spitters-2009"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "FINITE_EXACT",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "gottschalk-2004",
        "harding-heunen-2019"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "gottschalk-2004",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "brenna-flori-2012",
        "harding-heunen-2019",
        "heunen-landsman-spitters-2009"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. An algebraic architecture does not by itself select representations or physical states. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "brenna-flori-2012",
        "harding-heunen-2019",
        "heunen-landsman-spitters-2009"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: The reviewed synthetic Einstein-equation formulation does not construct spectral generators, prove evolution well-posedness, or provide causal Green maps. No reviewed record in the batch constructs the required generator or spectral dynamics in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "grinkevich-1996"
      ],
      "migration_rationale": "The reviewed synthetic Einstein-equation formulation does not construct spectral generators, prove evolution well-posedness, or provide causal Green maps. No reviewed record in the batch constructs the required generator or spectral dynamics in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. A localic spectrum is not causal evolution.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No finite-field dynamics, continuum convergence, regulator independence, causal propagation, or reconstruction theorem is proved.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "PIECES_ONLY",
      "evidence": [
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. An algebraic architecture does not by itself select representations or physical states. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "dittrich-2012"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "dittrich-2012"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "harding-heunen-2019",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Generator/spectral dynamics': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "harding-heunen-2019",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "FINITE_EXACT",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No general spectral measure, determinant, or interacting dynamics.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1",
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No other conformal generator, interaction, causal propagation, or nonlinear Bateman-Turok dynamics is exponentiated.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1",
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This compact-cylinder C*-dynamics is not an interacting AQFT net or full-orbit dynamics.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1",
        "baer-2015"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child. New atlas evidence: The symmetric-hyperbolic Cauchy theorem gives existence, uniqueness and continuous dependence.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The exact checker proves no PDE existence and no full BV propagator.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "research_revision": {
        "atlas": "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "kind": "EVIDENCE_OVERLAY",
        "previous_status": "LOCAL_RESULT"
      },
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "PIECES_ONLY",
      "evidence": [
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "FINITE_EXACT",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
      ],
      "summary": "Every fixed finite Laurent fixture evolves exactly and satisfies the wave equation.",
      "boundary": "PRA sufficiency at fixed cutoff does not prove an infinite energy-space solution.",
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "REVIEWED_V1_OVERLAY",
      "migration_status": "REVIEWED_OVERLAY",
      "migration_evidence": [
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
      ],
      "migration_rationale": "A child-specific v1 review overrides the mechanical migration.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1",
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2",
        "FOUNDATIONAL_CODED_WAVE_FRONTIER_V2",
        "pischke-2025-semigroups"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "RCA_0 suffices for existence, uniqueness, continuity, and energy conservation in the declared polygonal fast-Cauchy representation. Frontier evidence: Proof mining gives adjacent formal quantitative semigroup evidence, not the local RCA_0 proof.",
      "boundary": "The local RCA_0 upper bound is restricted to the declared fast-Cauchy polygonal energy representation; it is neither a reversal nor a spacetime causal theorem.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "brown-simpson-1986",
        "humphreys-simpson-1999",
        "humphreys-simpson-1996",
        "brattka-2008"
      ],
      "migration_rationale": "Logical-strength results for separation and Hahn-Banach principles do not construct a generator, well-posed evolution, or a causal Green operator. No reviewed record in the batch proves existence, uniqueness, stability, or computability of the required evolution.",
      "research_revision": {
        "atlas": "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "kind": "STATUS_CHANGE",
        "previous_status": "NOT_MAPPED"
      },
      "coded_wave_revision": {
        "frontier": "FOUNDATIONAL_CODED_WAVE_FRONTIER_V2",
        "status_change": true,
        "evidence_overlay": true,
        "previous_status": "PIECES_ONLY"
      },
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "gottschalk-2004",
        "mostafazadeh-2001"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "gottschalk-2004",
        "mostafazadeh-2001"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "PIECES_ONLY",
      "evidence": [
        "brunetti-fredenhagen-verch-2001"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. An algebraic architecture does not by itself select representations or physical states. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "brunetti-fredenhagen-verch-2001"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1",
        "weihrauch-zhong-2002",
        "FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1",
        "simpson-1984-ode"
      ],
      "summary": "An exact finite-to-coded ladder and computable Sobolev wave result identify a specific RCA_0 formalization target. Frontier evidence: The local carrier and the ODE reversal clarify coding and strength, but no localized spacetime-distribution theorem is proved.",
      "boundary": "No second-order-arithmetic upper bound or reversal has been proved.",
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "REVIEWED_V1_OVERLAY",
      "migration_status": "REVIEWED_OVERLAY",
      "migration_evidence": [
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1",
        "weihrauch-zhong-2002"
      ],
      "migration_rationale": "A child-specific v1 review overrides the mechanical migration.",
      "coded_wave_revision": {
        "frontier": "FOUNDATIONAL_CODED_WAVE_FRONTIER_V2",
        "status_change": false,
        "evidence_overlay": true,
        "previous_status": "PIECES_ONLY"
      },
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "FINITE_EXACT",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. General spectral measures and interacting dynamics remain open.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1",
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This proves no interacting, nonlinear, or Lorentzian-causal dynamics.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1",
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Nonlinear/full-orbit Bateman-Turok dynamics, local normality, and interacting evolution remain open.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No choice-free continuum PDE theorem is claimed.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "FINITE_EXACT",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "pour-el-richards-1981",
        "neumann-pape-streicher-2018",
        "weihrauch-zhong-2007-cauchy"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child. Frontier evidence: The abstract Cauchy problem has a direct TTE computability characterization under its representations.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "pour-el-richards-1981",
        "neumann-pape-streicher-2018"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "coded_wave_revision": {
        "frontier": "FOUNDATIONAL_CODED_WAVE_FRONTIER_V2",
        "status_change": false,
        "evidence_overlay": true,
        "previous_status": "LITERATURE_RESULT"
      },
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "PIECES_ONLY",
      "evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "PIECES_ONLY",
      "evidence": [
        "neumann-pape-streicher-2018"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. An algebraic architecture does not by itself select representations or physical states. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "neumann-pape-streicher-2018"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "weihrauch-zhong-2002",
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1",
        "selivanova-selivanov-2013",
        "selivanova-selivanov-2018",
        "zhong-1999-sobolev",
        "bridges-wang-1998-dirichlet"
      ],
      "summary": "Wave propagation is computable in the stated C1 and Sobolev representations reviewed by the ladder. New atlas evidence: The represented symmetric-hyperbolic solution operator is computable with effective approximation and complexity bounds in the papers' scope. Frontier evidence: Computable Sobolev hyperbolic applications strengthen the TTE evidence; the Bishop-constructive elliptic theorem is adjacent and does not alter the classification.",
      "boundary": "TTE computability is representation-sensitive and is not a Bishop-constructive or reverse-mathematical theorem.",
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "REVIEWED_V1_OVERLAY",
      "migration_status": "REVIEWED_OVERLAY",
      "migration_evidence": [
        "weihrauch-zhong-2002",
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
      ],
      "migration_rationale": "A child-specific v1 review overrides the mechanical migration.",
      "research_revision": {
        "atlas": "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "kind": "EVIDENCE_OVERLAY",
        "previous_status": "LITERATURE_RESULT"
      },
      "coded_wave_revision": {
        "frontier": "FOUNDATIONAL_CODED_WAVE_FRONTIER_V2",
        "status_change": false,
        "evidence_overlay": true,
        "previous_status": "LITERATURE_RESULT"
      },
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "PIECES_ONLY",
      "evidence": [
        "brenna-flori-2012"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "brenna-flori-2012"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "FINITE_EXACT",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "PIECES_ONLY",
      "evidence": [
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "gottschalk-2004",
        "harding-heunen-2019"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "gottschalk-2004",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "PIECES_ONLY",
      "evidence": [
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. An algebraic architecture does not by itself select representations or physical states. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: The reviewed synthetic Einstein-equation formulation does not construct spectral generators, prove evolution well-posedness, or provide causal Green maps. No reviewed record in the batch proves existence, uniqueness, stability, or computability of the required evolution.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "grinkevich-1996"
      ],
      "migration_rationale": "The reviewed synthetic Einstein-equation formulation does not construct spectral generators, prove evolution well-posedness, or provide causal Green maps. No reviewed record in the batch proves existence, uniqueness, stability, or computability of the required evolution.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. A localic spectrum is not causal evolution.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No finite-field dynamics, continuum convergence, regulator independence, causal propagation, or reconstruction theorem is proved.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "kostrykin-potthoff-schrader-2011"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "The metric-graph theorem proves existence and uniqueness for the specified finite/network geometry.",
      "boundary": "This classification is restricted to the cited object and foundational framework; it does not transfer to stronger causal, continuum, choice-free, or reverse-mathematical claims.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "migration_rationale": "Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations. No reviewed record in the batch proves existence, uniqueness, stability, or computability of the required evolution.",
      "research_revision": {
        "atlas": "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "kind": "STATUS_CHANGE",
        "previous_status": "NOT_MAPPED"
      },
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. An algebraic architecture does not by itself select representations or physical states. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "dittrich-2012"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "dittrich-2012"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "PIECES_ONLY",
      "evidence": [
        "harding-heunen-2019"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "harding-heunen-2019"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "FINITE_EXACT",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "kostrykin-potthoff-schrader-2011"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Self-adjoint Hilbert-space Laplacians on metric graphs have well-posed wave evolution and strict finite propagation.",
      "boundary": "This classification is restricted to the cited object and foundational framework; it does not transfer to stronger causal, continuum, choice-free, or reverse-mathematical claims.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
      ],
      "migration_rationale": "The exact energy spectrum is a reduced-mode spectral result and explicitly does not establish causal support or a Green operator. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "research_revision": {
        "atlas": "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "kind": "STATUS_CHANGE",
        "previous_status": "NOT_MAPPED"
      },
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No other conformal generator, interaction, causal propagation, or nonlinear Bateman-Turok dynamics is exponentiated.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This compact-cylinder C*-dynamics is not an interacting AQFT net or full-orbit dynamics.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1",
        "baer-2015",
        "muehlhoff-2010"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child. New atlas evidence: The normally- and prenormally-hyperbolic theorems give advanced/retarded Green maps with causal support.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The exact checker proves no PDE existence and no full BV propagator.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "research_revision": {
        "atlas": "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "kind": "EVIDENCE_OVERLAY",
        "previous_status": "LOCAL_RESULT"
      },
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "FINITE_EXACT",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Classical support and effective evolution exist separately; their combination has not been formalized over a weak subsystem.",
      "boundary": "This classification is restricted to the cited object and foundational framework; it does not transfer to stronger causal, continuum, choice-free, or reverse-mathematical claims.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "brown-simpson-1986",
        "humphreys-simpson-1999",
        "humphreys-simpson-1996",
        "brattka-2008"
      ],
      "migration_rationale": "Logical-strength results for separation and Hahn-Banach principles do not construct a generator, well-posed evolution, or a causal Green operator. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "research_revision": {
        "atlas": "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "kind": "STATUS_CHANGE",
        "previous_status": "NOT_MAPPED"
      },
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "gottschalk-2004"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "gottschalk-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "brunetti-fredenhagen-verch-2001"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. An algebraic architecture does not by itself select representations or physical states. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "brunetti-fredenhagen-verch-2001"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1",
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
      ],
      "summary": "The exact antipodal obstruction separates spectral approximation from the conditional causal Green dependency shell.",
      "boundary": "No causal PDE theorem has been formalized over a weak base.",
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "REVIEWED_V1_OVERLAY",
      "migration_status": "REVIEWED_OVERLAY",
      "migration_evidence": [
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1",
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
      ],
      "migration_rationale": "A child-specific v1 review overrides the mechanical migration.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "FINITE_EXACT",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "blackadar-farah-karagila-2026"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "ZF Hilbert theory and classical causal PDE are known separately; the Sobolev/Green construction has not been proved choice-free.",
      "boundary": "This classification is restricted to the cited object and foundational framework; it does not transfer to stronger causal, continuum, choice-free, or reverse-mathematical claims.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
      ],
      "migration_rationale": "The exact energy spectrum is a reduced-mode spectral result and explicitly does not establish causal support or a Green operator. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "research_revision": {
        "atlas": "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "kind": "STATUS_CHANGE",
        "previous_status": "NOT_MAPPED"
      },
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This proves no interacting, nonlinear, or Lorentzian-causal dynamics.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Nonlinear/full-orbit Bateman-Turok dynamics, local normality, and interacting evolution remain open.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No choice-free continuum PDE theorem is claimed.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "FINITE_EXACT",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "pour-el-richards-1981"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "pour-el-richards-1981"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: PT-symmetric and pseudo-Hermitian spectral structure does not supply state representation, normalized probabilities, or causal Green propagation. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001"
      ],
      "migration_rationale": "PT-symmetric and pseudo-Hermitian spectral structure does not supply state representation, normalized probabilities, or causal Green propagation. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Localic duality and effective spectral representation do not construct localized causal Green propagation. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "coquand-spitters-2009",
        "henry-2014",
        "neumann-pape-streicher-2018"
      ],
      "migration_rationale": "Localic duality and effective spectral representation do not construct localized causal Green propagation. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "pour-el-richards-1981",
        "weihrauch-zhong-2002",
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1",
        "selivanova-selivanov-2013",
        "zhong-weihrauch-2003-distributions",
        "weihrauch-zhong-2006-fundamental"
      ],
      "summary": "Positive and negative computability results expose the representation and localization dependencies of wave propagation. New atlas evidence: Computable evolution is direct evidence for one ingredient, while strict globally-hyperbolic Green support remains outside the theorem. Frontier evidence: Computable distributional wave solutions and fundamental solutions are ingredients, but retarded/advanced selection and strict support are unverified.",
      "boundary": "Neither source constructs a constructive causal Green operator for Weyl gravity.",
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "REVIEWED_V1_OVERLAY",
      "migration_status": "REVIEWED_OVERLAY",
      "migration_evidence": [
        "pour-el-richards-1981",
        "weihrauch-zhong-2002",
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
      ],
      "migration_rationale": "A child-specific v1 review overrides the mechanical migration.",
      "research_revision": {
        "atlas": "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "kind": "EVIDENCE_OVERLAY",
        "previous_status": "PIECES_ONLY"
      },
      "coded_wave_revision": {
        "frontier": "FOUNDATIONAL_CODED_WAVE_FRONTIER_V2",
        "status_change": false,
        "evidence_overlay": true,
        "previous_status": "PIECES_ONLY"
      },
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Constructive duality and internal one-parameter dynamics do not transfer to causal Green theory or interacting/renormalized field theory. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "migration_rationale": "Constructive duality and internal one-parameter dynamics do not transfer to causal Green theory or interacting/renormalized field theory. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "FINITE_EXACT",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: State measures and internal one-parameter groups do not establish spacetime support or causal Green propagation. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "State measures and internal one-parameter groups do not establish spacetime support or causal Green propagation. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "gottschalk-2004"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "gottschalk-2004"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: The reviewed synthetic Einstein-equation formulation does not construct spectral generators, prove evolution well-posedness, or provide causal Green maps. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "grinkevich-1996"
      ],
      "migration_rationale": "The reviewed synthetic Einstein-equation formulation does not construct spectral generators, prove evolution well-posedness, or provide causal Green maps. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. A localic spectrum is not causal evolution.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1",
        "FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Exact rational retarded/advanced kernels have a certified graph-step support cone on the displayed finite fixtures.",
      "boundary": "This classification is restricted to the cited object and foundational framework; it does not transfer to stronger causal, continuum, choice-free, or reverse-mathematical claims.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "research_revision": {
        "atlas": "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "kind": "STATUS_CHANGE",
        "previous_status": "PIECES_ONLY"
      },
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "kostrykin-potthoff-schrader-2011"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "The same theorem proves strict finite propagation under its local boundary conditions.",
      "boundary": "This classification is restricted to the cited object and foundational framework; it does not transfer to stronger causal, continuum, choice-free, or reverse-mathematical claims.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "migration_rationale": "Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "research_revision": {
        "atlas": "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "kind": "STATUS_CHANGE",
        "previous_status": "NOT_MAPPED"
      },
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014",
        "nachtergaele-raz-schlein-sims-2007"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child. New atlas evidence: Lieb-Robinson decay supplies an effective lattice cone, explicitly distinguished from strict support.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. An algebraic architecture does not by itself select representations or physical states. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "research_revision": {
        "atlas": "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
        "kind": "EVIDENCE_OVERLAY",
        "previous_status": "PIECES_ONLY"
      },
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: full interacting Lorentzian-causal propagation.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Finite contextual and categorical structures do not establish causal propagation or the six quantum-consistency children. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "Finite contextual and categorical structures do not establish causal propagation or the six quantum-consistency children. No reviewed record in the batch constructs advanced/retarded maps with causal support.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "FINITE_EXACT",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "A fixed exact BV contraction and cohomology witness exists.",
      "boundary": "Only one finite energy block; not the continuum complex.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PIECES_ONLY",
      "evidence": [
        "neumann-pape-streicher-2018",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Spectral and compositional quantum results cover standard Hilbert kinematics, states, dynamics, and finite reconstruction. For this obligation, the evidence contains ingredients relevant to, but does not compose a result that treats gauge constraints, BRST/BV structure, or symmetry restoration.",
      "boundary": "The source works in ordinary classical mathematics and is not a foundational-strength audit. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: the certified full metric BV complex and its residual transfer.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PIECES_ONLY",
      "evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Pseudo-Hermitian and Krein-QFT work supplies spectral, dynamical, and relativistic indefinite-metric results under explicit hypotheses. For this obligation, the evidence contains ingredients relevant to, but does not compose a result that treats gauge constraints, BRST/BV structure, or symmetry restoration.",
      "boundary": "The source works in ordinary classical mathematics and is not a foundational-strength audit. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: the certified full metric BV complex and its residual transfer.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "brunetti-fredenhagen-verch-2001",
        "fewster-verch-2011",
        "fredenhagen-rejzner-2011"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Locally covariant AQFT and perturbative BV jointly address algebraic kinematics, states, dynamics, gauge structure, interactions, and comparison principles. For this obligation, the evidence directly treats gauge constraints, BRST/BV structure, or symmetry restoration.",
      "boundary": "The source works in ordinary classical mathematics and is not a foundational-strength audit. An algebraic architecture does not by itself select representations or physical states. Still open here: the certified full metric BV complex and its residual transfer.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "brunetti-fredenhagen-verch-2001",
        "fewster-verch-2011",
        "fredenhagen-rejzner-2011"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Gauge-fixed local BV cohomology H^{0,4}(s|d) and H^{1,4}(s|d) is complete on the regular Bach locus.",
      "boundary": "This local jet/BV result is not a complete global smooth or distributional off-shell complex, classical freeze gate, propagator, or residual-state theorem.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PIECES_ONLY",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Topos quantum theory supplies localic spectra, state measures, internal group dynamics, and comparisons between context topoi. For this obligation, the evidence contains ingredients relevant to, but does not compose a result that treats gauge constraints, BRST/BV structure, or symmetry restoration.",
      "boundary": "The source works in ordinary classical mathematics and is not a foundational-strength audit. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: the certified full metric BV complex and its residual transfer.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "FINITE_EXACT",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "PRA suffices to check the displayed finite BV contraction and explicit nontriviality witness.",
      "boundary": "Sufficiency only; no weakest-base reversal.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "The continuum BV complex has not been encoded over a weak base.",
      "boundary": "Finite certificates do not fill this cell.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "FINITE_EXACT",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Named finite matrices and finite BV arrays are constructed without selecting from arbitrary families. For this obligation, the evidence contains ingredients relevant to, but does not compose a result that treats gauge constraints, BRST/BV structure, or symmetry restoration.",
      "boundary": "An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: the certified full metric BV complex and its residual transfer.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PIECES_ONLY",
      "evidence": [
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "ZF operator theory and explicit separable representations cover substantial kinematics while isolating arbitrary-space pathologies. For this obligation, the evidence contains ingredients relevant to, but does not compose a result that treats gauge constraints, BRST/BV structure, or symmetry restoration.",
      "boundary": "An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: the certified full metric BV complex and its residual transfer.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "The repository constructs the named free Krein carrier in ZF; classical sources add interaction-adjacent and relativistic ingredients only. For this obligation, the evidence contains ingredients relevant to, but does not compose a result that treats gauge constraints, BRST/BV structure, or symmetry restoration.",
      "boundary": "An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: the certified full metric BV complex and its residual transfer.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PIECES_ONLY",
      "evidence": [
        "blackadar-farah-2026",
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1",
        "fredenhagen-rejzner-2011"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Robust separable C*-theory and an explicit state/GNS chain exist in ZF; perturbative BV remains an external classical ingredient. For this obligation, the evidence contains ingredients relevant to, but does not compose a result that treats gauge constraints, BRST/BV structure, or symmetry restoration.",
      "boundary": "An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. An algebraic architecture does not by itself select representations or physical states. Still open here: the certified full metric BV complex and its residual transfer.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "blackadar-farah-2026",
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1",
        "fredenhagen-rejzner-2011"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "No full continuum BV/BRST complex has been rebuilt in ZF without Choice.",
      "boundary": "Finite ZF carriers do not establish this cell.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "FINITE_EXACT",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "The finite checker is computationally explicit, but no constructive internal proof object has been produced.",
      "boundary": "PRA verifiability is not identical to Bishop constructivity or computability.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PIECES_ONLY",
      "evidence": [
        "neumann-pape-streicher-2018",
        "pour-el-richards-1981",
        "bridges-svozil-2000",
        "richman-bridges-1999"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Constructive quantum logic, constructive Gleason, effective spectral analysis, and a wave-equation counterexample delimit computable Hilbert physics. For this obligation, the evidence contains ingredients relevant to, but does not compose a result that treats gauge constraints, BRST/BV structure, or symmetry restoration.",
      "boundary": "Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: the certified full metric BV complex and its residual transfer.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "pour-el-richards-1981",
        "bridges-svozil-2000",
        "richman-bridges-1999"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "No constructive BV-BFV gauge-field complex is present.",
      "boundary": "Constructive Hilbert propositions do not supply gauge cohomology.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PIECES_ONLY",
      "evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Constructive localic spectra, valuations, and internal one-parameter dynamics form a coherent non-point-set quantum fragment. For this obligation, the evidence contains ingredients relevant to, but does not compose a result that treats gauge constraints, BRST/BV structure, or symmetry restoration.",
      "boundary": "Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: the certified full metric BV complex and its residual transfer.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "FINITE_EXACT",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PIECES_ONLY",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Contextual topos methods internalize commutative algebra, spectra, state measures, and one-parameter dynamics from operator-algebraic input. For this obligation, the evidence contains ingredients relevant to, but does not compose a result that treats gauge constraints, BRST/BV structure, or symmetry restoration.",
      "boundary": "External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. An algebraic architecture does not by itself select representations or physical states. Still open here: the certified full metric BV complex and its residual transfer.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PRIORITY_GAP",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Synthetic smooth geometry has not been joined to internal BV/BRST machinery.",
      "boundary": "Classical synthetic GR is not gauge-fixed Weyl BV.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PRIORITY_GAP",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "No internal Weyl BV complex or external/internal cohomology comparison exists.",
      "boundary": "Only a glossary and obstruction DAG exist.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "A finite energy-cutoff BV contraction is exact and independently checked.",
      "boundary": "A regulator at fixed cutoff is not a finite fundamental theory.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PIECES_ONLY",
      "evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Finite-dimensional phase space, categorical protocols, and contextual entropy cover Hilbert kinematics, states, operations, and reconstruction. For this obligation, the evidence contains ingredients relevant to, but does not compose a result that treats gauge constraints, BRST/BV structure, or symmetry restoration.",
      "boundary": "Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: the certified full metric BV complex and its residual transfer.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Explicit finite Krein matrices give sign, state-adjacent, J-unitary, and interacting witnesses at fixed dimension. For this obligation, the evidence contains ingredients relevant to, but does not compose a result that treats gauge constraints, BRST/BV structure, or symmetry restoration.",
      "boundary": "Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: the certified full metric BV complex and its residual transfer.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "The finite matrix algebra is a concrete C*-system, while lattice gauge work adds local constraints and truncation architecture. For this obligation, the evidence contains ingredients relevant to, but does not compose a result that treats gauge constraints, BRST/BV structure, or symmetry restoration.",
      "boundary": "Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. An algebraic architecture does not by itself select representations or physical states. Still open here: the certified full metric BV complex and its residual transfer.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009",
        "dittrich-2012"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Lattice gauge and discrete-gravity work supplies dynamics, constraints, symmetry-restoration, and explicit continuum-comparison obligations. For this obligation, the evidence directly treats gauge constraints, BRST/BV structure, or symmetry restoration.",
      "boundary": "Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: the certified full metric BV complex and its residual transfer.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009",
        "dittrich-2012"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "GAUGE_BV_COHOMOLOGY",
      "status": "PIECES_ONLY",
      "evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "GAUGE_BV_COHOMOLOGY",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Short-poset topoi, finite contextual entropy, and categorical protocols give finite internal/contextual kinematics, states, dynamics, and reconstruction. For this obligation, the evidence contains ingredients relevant to, but does not compose a result that treats gauge constraints, BRST/BV structure, or symmetry restoration.",
      "boundary": "Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: the certified full metric BV complex and its residual transfer.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "FINITE_EXACT",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "summary": "The exact two-qubit Hamiltonian constructs a nontrivial entangling interaction.",
      "boundary": "No counterterm, anomaly, renormalized-product, QME-restoration, or residual-transfer result follows.",
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "REVIEWED_V1_OVERLAY",
      "migration_status": "REVIEWED_OVERLAY",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "A child-specific v1 review overrides the mechanical migration.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Effective spectral representation and categorical protocols do not establish the unresolved field-interaction and quantum-consistency children. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "Effective spectral representation and categorical protocols do not establish the unresolved field-interaction and quantum-consistency children. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Real-spectrum and indefinite-metric QFT results do not establish the unresolved interaction or quantum-consistency children. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "migration_rationale": "Real-spectrum and indefinite-metric QFT results do not establish the unresolved interaction or quantum-consistency children. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "fredenhagen-rejzner-2011",
        "brunetti-fredenhagen-verch-2001"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Interaction construction': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "fredenhagen-rejzner-2011",
        "brunetti-fredenhagen-verch-2001"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Interaction construction': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No coefficient, regulated breaking, renormalized product, QME restoration, residual transfer, or Lorentzian quantum construction follows.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "FINITE_EXACT",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "summary": "The exact two-qubit Hamiltonian constructs a nontrivial entangling interaction.",
      "boundary": "No counterterm, anomaly, renormalized-product, QME-restoration, or residual-transfer result follows.",
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "REVIEWED_V1_OVERLAY",
      "migration_status": "REVIEWED_OVERLAY",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "A child-specific v1 review overrides the mechanical migration.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks an interaction construction in the declared foundational regime and smooth carrier.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks an interaction construction in the declared foundational regime and smooth carrier.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "FINITE_EXACT",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "summary": "The exact two-qubit Hamiltonian constructs a nontrivial entangling interaction.",
      "boundary": "No counterterm, anomaly, renormalized-product, QME-restoration, or residual-transfer result follows.",
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "REVIEWED_V1_OVERLAY",
      "migration_status": "REVIEWED_OVERLAY",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "A child-specific v1 review overrides the mechanical migration.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: ZF operator theory and effective spectral representation do not establish interacting QFT, renormalized products, anomalies, QME restoration, or residual transfer. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "migration_rationale": "ZF operator theory and effective spectral representation do not establish interacting QFT, renormalized products, anomalies, QME restoration, or residual transfer. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: The explicit Krein carrier, pseudo-Hermitian structure, and axiomatic indefinite-metric QFT do not construct the unresolved interaction or quantum-consistency children. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "migration_rationale": "The explicit Krein carrier, pseudo-Hermitian structure, and axiomatic indefinite-metric QFT do not construct the unresolved interaction or quantum-consistency children. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Interaction construction': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks an interaction construction in the declared foundational regime and smooth carrier.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks an interaction construction in the declared foundational regime and smooth carrier.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "FINITE_EXACT",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "summary": "The exact two-qubit Hamiltonian constructs a nontrivial entangling interaction.",
      "boundary": "No counterterm, anomaly, renormalized-product, QME-restoration, or residual-transfer result follows.",
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "REVIEWED_V1_OVERLAY",
      "migration_status": "REVIEWED_OVERLAY",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "A child-specific v1 review overrides the mechanical migration.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Constructive probability, Hilbert logic, effective spectra, and a representation-sensitive wave counterexample do not establish interacting or renormalized QFT children. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "pour-el-richards-1981",
        "bridges-svozil-2000",
        "richman-bridges-1999"
      ],
      "migration_rationale": "Constructive probability, Hilbert logic, effective spectra, and a representation-sensitive wave counterexample do not establish interacting or renormalized QFT children. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks an interaction construction in the declared foundational regime and smooth carrier.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks an interaction construction in the declared foundational regime and smooth carrier.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Constructive duality and internal one-parameter dynamics do not transfer to causal Green theory or interacting/renormalized field theory. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "migration_rationale": "Constructive duality and internal one-parameter dynamics do not transfer to causal Green theory or interacting/renormalized field theory. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "FINITE_EXACT",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Interaction construction': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Interaction construction': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No formal construction is claimed.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Interaction construction': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is the deepest missing corner.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "summary": "The exact two-qubit Hamiltonian constructs a nontrivial entangling interaction.",
      "boundary": "No counterterm, anomaly, renormalized-product, QME-restoration, or residual-transfer result follows.",
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "REVIEWED_V1_OVERLAY",
      "migration_status": "REVIEWED_OVERLAY",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "A child-specific v1 review overrides the mechanical migration.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "migration_rationale": "Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Interaction construction': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Interaction construction': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009",
        "dittrich-2012"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Interaction construction': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009",
        "dittrich-2012"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Finite contextual and categorical structures do not establish causal propagation or the six quantum-consistency children. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "Finite contextual and categorical structures do not establish causal propagation or the six quantum-consistency children. No reviewed record in the batch constructs the required interaction in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "FINITE_EXACT",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Counterterm classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Effective spectral representation and categorical protocols do not establish the unresolved field-interaction and quantum-consistency children. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "Effective spectral representation and categorical protocols do not establish the unresolved field-interaction and quantum-consistency children. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Real-spectrum and indefinite-metric QFT results do not establish the unresolved interaction or quantum-consistency children. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "migration_rationale": "Real-spectrum and indefinite-metric QFT results do not establish the unresolved interaction or quantum-consistency children. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Counterterm classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Counterterm classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No coefficient, regulated breaking, renormalized product, QME restoration, residual transfer, or Lorentzian quantum construction follows.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "FINITE_EXACT",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Counterterm classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks a child-specific local counterterm classification.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks a child-specific local counterterm classification.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "FINITE_EXACT",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Counterterm classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: ZF operator theory and effective spectral representation do not establish interacting QFT, renormalized products, anomalies, QME restoration, or residual transfer. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "migration_rationale": "ZF operator theory and effective spectral representation do not establish interacting QFT, renormalized products, anomalies, QME restoration, or residual transfer. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: The explicit Krein carrier, pseudo-Hermitian structure, and axiomatic indefinite-metric QFT do not construct the unresolved interaction or quantum-consistency children. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "migration_rationale": "The explicit Krein carrier, pseudo-Hermitian structure, and axiomatic indefinite-metric QFT do not construct the unresolved interaction or quantum-consistency children. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Counterterm classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks a child-specific local counterterm classification.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks a child-specific local counterterm classification.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "FINITE_EXACT",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Counterterm classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Constructive probability, Hilbert logic, effective spectra, and a representation-sensitive wave counterexample do not establish interacting or renormalized QFT children. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "pour-el-richards-1981",
        "bridges-svozil-2000",
        "richman-bridges-1999"
      ],
      "migration_rationale": "Constructive probability, Hilbert logic, effective spectra, and a representation-sensitive wave counterexample do not establish interacting or renormalized QFT children. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks a child-specific local counterterm classification.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks a child-specific local counterterm classification.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Constructive duality and internal one-parameter dynamics do not transfer to causal Green theory or interacting/renormalized field theory. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "migration_rationale": "Constructive duality and internal one-parameter dynamics do not transfer to causal Green theory or interacting/renormalized field theory. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "FINITE_EXACT",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Counterterm classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Counterterm classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No formal construction is claimed.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Counterterm classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is the deepest missing corner.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks a child-specific local counterterm classification.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks a child-specific local counterterm classification.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "migration_rationale": "Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Counterterm classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Counterterm classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Counterterm classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Finite contextual and categorical structures do not establish causal propagation or the six quantum-consistency children. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "Finite contextual and categorical structures do not establish causal propagation or the six quantum-consistency children. No reviewed record in the batch classifies counterterms in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "FINITE_EXACT",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Anomaly classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Effective spectral representation and categorical protocols do not establish the unresolved field-interaction and quantum-consistency children. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "Effective spectral representation and categorical protocols do not establish the unresolved field-interaction and quantum-consistency children. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Real-spectrum and indefinite-metric QFT results do not establish the unresolved interaction or quantum-consistency children. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "migration_rationale": "Real-spectrum and indefinite-metric QFT results do not establish the unresolved interaction or quantum-consistency children. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Anomaly classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Anomaly classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No coefficient, regulated breaking, renormalized product, QME restoration, residual transfer, or Lorentzian quantum construction follows.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "FINITE_EXACT",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Anomaly classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks a child-specific anomaly classification.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks a child-specific anomaly classification.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "FINITE_EXACT",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Anomaly classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: ZF operator theory and effective spectral representation do not establish interacting QFT, renormalized products, anomalies, QME restoration, or residual transfer. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "migration_rationale": "ZF operator theory and effective spectral representation do not establish interacting QFT, renormalized products, anomalies, QME restoration, or residual transfer. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: The explicit Krein carrier, pseudo-Hermitian structure, and axiomatic indefinite-metric QFT do not construct the unresolved interaction or quantum-consistency children. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "migration_rationale": "The explicit Krein carrier, pseudo-Hermitian structure, and axiomatic indefinite-metric QFT do not construct the unresolved interaction or quantum-consistency children. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Anomaly classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks a child-specific anomaly classification.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks a child-specific anomaly classification.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "FINITE_EXACT",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Anomaly classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Constructive probability, Hilbert logic, effective spectra, and a representation-sensitive wave counterexample do not establish interacting or renormalized QFT children. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "pour-el-richards-1981",
        "bridges-svozil-2000",
        "richman-bridges-1999"
      ],
      "migration_rationale": "Constructive probability, Hilbert logic, effective spectra, and a representation-sensitive wave counterexample do not establish interacting or renormalized QFT children. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks a child-specific anomaly classification.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks a child-specific anomaly classification.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Constructive duality and internal one-parameter dynamics do not transfer to causal Green theory or interacting/renormalized field theory. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "migration_rationale": "Constructive duality and internal one-parameter dynamics do not transfer to causal Green theory or interacting/renormalized field theory. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "FINITE_EXACT",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Anomaly classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Anomaly classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No formal construction is claimed.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Anomaly classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is the deepest missing corner.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks a child-specific anomaly classification.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks a child-specific anomaly classification.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "migration_rationale": "Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Anomaly classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Anomaly classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Anomaly classification': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Finite contextual and categorical structures do not establish causal propagation or the six quantum-consistency children. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "Finite contextual and categorical structures do not establish causal propagation or the six quantum-consistency children. No reviewed record in the batch classifies anomalies in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "FINITE_EXACT",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Renormalized products': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Effective spectral representation and categorical protocols do not establish the unresolved field-interaction and quantum-consistency children. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "Effective spectral representation and categorical protocols do not establish the unresolved field-interaction and quantum-consistency children. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Real-spectrum and indefinite-metric QFT results do not establish the unresolved interaction or quantum-consistency children. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "migration_rationale": "Real-spectrum and indefinite-metric QFT results do not establish the unresolved interaction or quantum-consistency children. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Renormalized products': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Renormalized products': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No coefficient, regulated breaking, renormalized product, QME restoration, residual transfer, or Lorentzian quantum construction follows.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "FINITE_EXACT",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Renormalized products': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks renormalized products in the declared foundational regime and carrier.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks renormalized products in the declared foundational regime and carrier.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "FINITE_EXACT",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Renormalized products': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: ZF operator theory and effective spectral representation do not establish interacting QFT, renormalized products, anomalies, QME restoration, or residual transfer. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "migration_rationale": "ZF operator theory and effective spectral representation do not establish interacting QFT, renormalized products, anomalies, QME restoration, or residual transfer. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: The explicit Krein carrier, pseudo-Hermitian structure, and axiomatic indefinite-metric QFT do not construct the unresolved interaction or quantum-consistency children. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "migration_rationale": "The explicit Krein carrier, pseudo-Hermitian structure, and axiomatic indefinite-metric QFT do not construct the unresolved interaction or quantum-consistency children. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Renormalized products': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks renormalized products in the declared foundational regime and carrier.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks renormalized products in the declared foundational regime and carrier.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "FINITE_EXACT",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Renormalized products': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Constructive probability, Hilbert logic, effective spectra, and a representation-sensitive wave counterexample do not establish interacting or renormalized QFT children. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "pour-el-richards-1981",
        "bridges-svozil-2000",
        "richman-bridges-1999"
      ],
      "migration_rationale": "Constructive probability, Hilbert logic, effective spectra, and a representation-sensitive wave counterexample do not establish interacting or renormalized QFT children. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks renormalized products in the declared foundational regime and carrier.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks renormalized products in the declared foundational regime and carrier.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Constructive duality and internal one-parameter dynamics do not transfer to causal Green theory or interacting/renormalized field theory. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "migration_rationale": "Constructive duality and internal one-parameter dynamics do not transfer to causal Green theory or interacting/renormalized field theory. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "FINITE_EXACT",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Renormalized products': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Renormalized products': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No formal construction is claimed.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Renormalized products': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is the deepest missing corner.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks renormalized products in the declared foundational regime and carrier.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks renormalized products in the declared foundational regime and carrier.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "migration_rationale": "Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Renormalized products': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Renormalized products': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "PIECES_ONLY",
      "evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "dittrich-2012"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Renormalized products': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "dittrich-2012"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Finite contextual and categorical structures do not establish causal propagation or the six quantum-consistency children. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "Finite contextual and categorical structures do not establish causal propagation or the six quantum-consistency children. No reviewed record in the batch constructs renormalized products in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "FINITE_EXACT",
      "obligation": "QME_RESTORATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'QME restoration': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Effective spectral representation and categorical protocols do not establish the unresolved field-interaction and quantum-consistency children. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "Effective spectral representation and categorical protocols do not establish the unresolved field-interaction and quantum-consistency children. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Real-spectrum and indefinite-metric QFT results do not establish the unresolved interaction or quantum-consistency children. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "migration_rationale": "Real-spectrum and indefinite-metric QFT results do not establish the unresolved interaction or quantum-consistency children. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "QME_RESTORATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'QME restoration': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "QME_RESTORATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'QME restoration': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No coefficient, regulated breaking, renormalized product, QME restoration, residual transfer, or Lorentzian quantum construction follows.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "FINITE_EXACT",
      "obligation": "QME_RESTORATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'QME restoration': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "QME_RESTORATION",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks restoration of the local quantum master equation.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks restoration of the local quantum master equation.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "FINITE_EXACT",
      "obligation": "QME_RESTORATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'QME restoration': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: ZF operator theory and effective spectral representation do not establish interacting QFT, renormalized products, anomalies, QME restoration, or residual transfer. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "migration_rationale": "ZF operator theory and effective spectral representation do not establish interacting QFT, renormalized products, anomalies, QME restoration, or residual transfer. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: The explicit Krein carrier, pseudo-Hermitian structure, and axiomatic indefinite-metric QFT do not construct the unresolved interaction or quantum-consistency children. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "migration_rationale": "The explicit Krein carrier, pseudo-Hermitian structure, and axiomatic indefinite-metric QFT do not construct the unresolved interaction or quantum-consistency children. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "QME_RESTORATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'QME restoration': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "QME_RESTORATION",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks restoration of the local quantum master equation.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks restoration of the local quantum master equation.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "FINITE_EXACT",
      "obligation": "QME_RESTORATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'QME restoration': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Constructive probability, Hilbert logic, effective spectra, and a representation-sensitive wave counterexample do not establish interacting or renormalized QFT children. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "pour-el-richards-1981",
        "bridges-svozil-2000",
        "richman-bridges-1999"
      ],
      "migration_rationale": "Constructive probability, Hilbert logic, effective spectra, and a representation-sensitive wave counterexample do not establish interacting or renormalized QFT children. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "QME_RESTORATION",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks restoration of the local quantum master equation.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks restoration of the local quantum master equation.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Constructive duality and internal one-parameter dynamics do not transfer to causal Green theory or interacting/renormalized field theory. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "migration_rationale": "Constructive duality and internal one-parameter dynamics do not transfer to causal Green theory or interacting/renormalized field theory. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "FINITE_EXACT",
      "obligation": "QME_RESTORATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'QME restoration': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "QME_RESTORATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'QME restoration': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No formal construction is claimed.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "QME_RESTORATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'QME restoration': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is the deepest missing corner.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "QME_RESTORATION",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks restoration of the local quantum master equation.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks restoration of the local quantum master equation.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "migration_rationale": "Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "QME_RESTORATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'QME restoration': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "QME_RESTORATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'QME restoration': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "QME_RESTORATION",
      "status": "PIECES_ONLY",
      "evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'QME restoration': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "QME_RESTORATION",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Finite contextual and categorical structures do not establish causal propagation or the six quantum-consistency children. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "Finite contextual and categorical structures do not establish causal propagation or the six quantum-consistency children. No reviewed record in the batch restores the quantum master equation in this refined coordinate.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "FINITE_EXACT",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Residual quantum transfer': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Effective spectral representation and categorical protocols do not establish the unresolved field-interaction and quantum-consistency children. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "Effective spectral representation and categorical protocols do not establish the unresolved field-interaction and quantum-consistency children. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Real-spectrum and indefinite-metric QFT results do not establish the unresolved interaction or quantum-consistency children. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "migration_rationale": "Real-spectrum and indefinite-metric QFT results do not establish the unresolved interaction or quantum-consistency children. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PIECES_ONLY",
      "evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Residual quantum transfer': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Residual quantum transfer': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No coefficient, regulated breaking, renormalized product, QME restoration, residual transfer, or Lorentzian quantum construction follows.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "FINITE_EXACT",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Residual quantum transfer': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks a quantum correction transferred to the residual complex after QME restoration.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks a quantum correction transferred to the residual complex after QME restoration.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "FINITE_EXACT",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Residual quantum transfer': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: ZF operator theory and effective spectral representation do not establish interacting QFT, renormalized products, anomalies, QME restoration, or residual transfer. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "migration_rationale": "ZF operator theory and effective spectral representation do not establish interacting QFT, renormalized products, anomalies, QME restoration, or residual transfer. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: The explicit Krein carrier, pseudo-Hermitian structure, and axiomatic indefinite-metric QFT do not construct the unresolved interaction or quantum-consistency children. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "migration_rationale": "The explicit Krein carrier, pseudo-Hermitian structure, and axiomatic indefinite-metric QFT do not construct the unresolved interaction or quantum-consistency children. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PIECES_ONLY",
      "evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Residual quantum transfer': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "fredenhagen-rejzner-2011"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks a quantum correction transferred to the residual complex after QME restoration.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks a quantum correction transferred to the residual complex after QME restoration.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "FINITE_EXACT",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Residual quantum transfer': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Constructive probability, Hilbert logic, effective spectra, and a representation-sensitive wave counterexample do not establish interacting or renormalized QFT children. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "pour-el-richards-1981",
        "bridges-svozil-2000",
        "richman-bridges-1999"
      ],
      "migration_rationale": "Constructive probability, Hilbert logic, effective spectra, and a representation-sensitive wave counterexample do not establish interacting or renormalized QFT children. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks a quantum correction transferred to the residual complex after QME restoration.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks a quantum correction transferred to the residual complex after QME restoration.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Constructive duality and internal one-parameter dynamics do not transfer to causal Green theory or interacting/renormalized field theory. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "migration_rationale": "Constructive duality and internal one-parameter dynamics do not transfer to causal Green theory or interacting/renormalized field theory. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "FINITE_EXACT",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Residual quantum transfer': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "Internal spectra, state measures, and one-parameter dynamics are reviewed; the records explicitly exclude causal propagation and interacting/renormalized field theory. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Residual quantum transfer': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No formal construction is claimed.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Residual quantum transfer': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is the deepest missing corner.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PRIORITY_GAP",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed child gap: The broad v0 priority gap is coherent at this child: the current corpus lacks a quantum correction transferred to the residual complex after QME restoration.",
      "boundary": "This is a reviewed programme gap in the current corpus, not proof of literature absence, impossibility, necessity, or a no-go theorem.",
      "migration_status": "REVIEWED_CHILD_GAP",
      "migration_evidence": [],
      "migration_rationale": "The broad v0 priority gap is coherent at this child: the current corpus lacks a quantum correction transferred to the residual complex after QME restoration.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "migration_rationale": "Finite phase-space, categorical protocol, and state-reconstruction results do not establish evolution well-posedness, causal propagation, or quantum field consistency obligations. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Residual quantum transfer': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Residual quantum transfer': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "PIECES_ONLY",
      "evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009",
        "dittrich-2012"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Residual quantum transfer': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "migration_status": "CAPABILITY_QUALIFIED",
      "migration_evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009",
        "dittrich-2012"
      ],
      "migration_rationale": "The explicit v1 evidence-capability registry licenses transfer to this child.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Reviewed parent-evidence transfer: Finite contextual and categorical structures do not establish causal propagation or the six quantum-consistency children. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "boundary": "This reviews only transfer of the named parent evidence. NOT_MAPPED is not a literature-absence claim and does not show that the coordinate is incoherent.",
      "migration_status": "REVIEWED_NO_TRANSFER",
      "migration_evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "Finite contextual and categorical structures do not establish causal propagation or the six quantum-consistency children. No reviewed record in the batch transfers a restored quantum correction to the residual complex.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "FINITE_EXACT",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "neumann-pape-streicher-2018",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Spectral and compositional quantum results cover standard Hilbert kinematics, states, dynamics, and finite reconstruction. For this obligation, the evidence directly supplies reconstruction, comparison, covariance, or continuum-limit obligations.",
      "boundary": "The source works in ordinary classical mathematics and is not a foundational-strength audit. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: a prediction-preserving comparison or controlled continuum theorem.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "neumann-pape-streicher-2018",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Pseudo-Hermitian and Krein-QFT work supplies spectral, dynamical, and relativistic indefinite-metric results under explicit hypotheses. For this obligation, the evidence directly supplies reconstruction, comparison, covariance, or continuum-limit obligations.",
      "boundary": "The source works in ordinary classical mathematics and is not a foundational-strength audit. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: a prediction-preserving comparison or controlled continuum theorem.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "brunetti-fredenhagen-verch-2001",
        "fewster-verch-2011",
        "fredenhagen-rejzner-2011"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Locally covariant AQFT and perturbative BV jointly address algebraic kinematics, states, dynamics, gauge structure, interactions, and comparison principles. For this obligation, the evidence directly supplies reconstruction, comparison, covariance, or continuum-limit obligations.",
      "boundary": "The source works in ordinary classical mathematics and is not a foundational-strength audit. An algebraic architecture does not by itself select representations or physical states. Still open here: a prediction-preserving comparison or controlled continuum theorem.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "brunetti-fredenhagen-verch-2001",
        "fewster-verch-2011",
        "fredenhagen-rejzner-2011"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "barnich-brandt-henneaux-2000",
        "brunetti-fredenhagen-verch-2001",
        "fredenhagen-rejzner-2011",
        "brunetti-fredenhagen-rejzner-2013"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Local BRST, locally covariant QFT, and perturbative BV give a standard smooth/distributional architecture across all six obligations. For this obligation, the evidence directly supplies reconstruction, comparison, covariance, or continuum-limit obligations.",
      "boundary": "The source works in ordinary classical mathematics and is not a foundational-strength audit. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a prediction-preserving comparison or controlled continuum theorem.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "barnich-brandt-henneaux-2000",
        "brunetti-fredenhagen-verch-2001",
        "fredenhagen-rejzner-2011",
        "brunetti-fredenhagen-rejzner-2013"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Topos quantum theory supplies localic spectra, state measures, internal group dynamics, and comparisons between context topoi. For this obligation, the evidence directly supplies reconstruction, comparison, covariance, or continuum-limit obligations.",
      "boundary": "The source works in ordinary classical mathematics and is not a foundational-strength audit. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a prediction-preserving comparison or controlled continuum theorem.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "FINITE_EXACT",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "One Hardy continuity step has an RCA_0 sufficiency route when an explicit modulus is supplied.",
      "boundary": "No full reconstruction audit or physical-to-mathematical reversal.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "brown-simpson-1986",
        "humphreys-simpson-1999",
        "humphreys-simpson-1996",
        "brattka-2008"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Reverse mathematics calibrates specific separable Hahn-Banach, separation, and weak-star closure statements, with representation-sensitive strength. For this obligation, the evidence directly supplies reconstruction, comparison, covariance, or continuum-limit obligations.",
      "boundary": "No reverse implication over a fixed weak base is inferred unless the cited source states one. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: a prediction-preserving comparison or controlled continuum theorem.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "brown-simpson-1986",
        "humphreys-simpson-1999",
        "humphreys-simpson-1996",
        "brattka-2008"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "FINITE_EXACT",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "ZF operator theory and explicit separable representations cover substantial kinematics while isolating arbitrary-space pathologies. For this obligation, the evidence directly supplies reconstruction, comparison, covariance, or continuum-limit obligations.",
      "boundary": "An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: a prediction-preserving comparison or controlled continuum theorem.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "blackadar-farah-2026",
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1",
        "fredenhagen-rejzner-2011"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Robust separable C*-theory and an explicit state/GNS chain exist in ZF; perturbative BV remains an external classical ingredient. For this obligation, the evidence directly supplies reconstruction, comparison, covariance, or continuum-limit obligations.",
      "boundary": "An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. An algebraic architecture does not by itself select representations or physical states. Still open here: a prediction-preserving comparison or controlled continuum theorem.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "blackadar-farah-2026",
        "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1",
        "fredenhagen-rejzner-2011"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "FINITE_EXACT",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "PIECES_ONLY",
      "evidence": [
        "hardy-2001",
        "chiribella-dariano-perinotti-2011",
        "brattka-2008"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Operational and computability ingredients exist, but no shared constructive reversal joins them.",
      "boundary": "A computability classification is not a reverse-mathematical or physical implication.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "hardy-2001",
        "chiribella-dariano-perinotti-2011",
        "brattka-2008"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "coquand-spitters-2009",
        "henry-2014",
        "neumann-pape-streicher-2018"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Constructive localic Gelfand duality and computable spectral representations cover commutative kinematics and state-adjacent structure. For this obligation, the evidence directly supplies reconstruction, comparison, covariance, or continuum-limit obligations.",
      "boundary": "Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. An algebraic architecture does not by itself select representations or physical states. Still open here: a prediction-preserving comparison or controlled continuum theorem.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "coquand-spitters-2009",
        "henry-2014",
        "neumann-pape-streicher-2018"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Constructive localic spectra, valuations, and internal one-parameter dynamics form a coherent non-point-set quantum fragment. For this obligation, the evidence directly supplies reconstruction, comparison, covariance, or continuum-limit obligations.",
      "boundary": "Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a prediction-preserving comparison or controlled continuum theorem.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "FINITE_EXACT",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Finite categorical and contextual-entropy constructions coexist with the exact matrix witness, but their internalization is not automatic. For this obligation, the evidence directly supplies reconstruction, comparison, covariance, or continuum-limit obligations.",
      "boundary": "External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. The evidence is bounded finite algebra, not a completed infinite carrier. Still open here: a prediction-preserving comparison or controlled continuum theorem.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Contextual topos methods internalize commutative algebra, spectra, state measures, and one-parameter dynamics from operator-algebraic input. For this obligation, the evidence directly supplies reconstruction, comparison, covariance, or continuum-limit obligations.",
      "boundary": "External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. An algebraic architecture does not by itself select representations or physical states. Still open here: a prediction-preserving comparison or controlled continuum theorem.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "grinkevich-1996",
        "barnich-brandt-henneaux-2000"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Synthetic general relativity supplies formal smooth geometry, while probability and BV/renormalization remain separate classical ingredients. For this obligation, the evidence directly supplies reconstruction, comparison, covariance, or continuum-limit obligations.",
      "boundary": "External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a prediction-preserving comparison or controlled continuum theorem.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "grinkevich-1996",
        "barnich-brandt-henneaux-2000"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "PRIORITY_GAP",
      "evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "No external comparison theorem states which physical predictions an internal construction preserves.",
      "boundary": "Internal reformulation is not empirical equivalence.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Finite field, finite mode, finite Hilbert dimension, and finitism are proved non-equivalent by type, and bridge obligations are listed.",
      "boundary": "No continuum bridge is constructed.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "One finite-dimensional reconstruction step has a representation-sensitive logical audit.",
      "boundary": "No full reconstruction or continuum limit.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "NOT_MAPPED",
      "evidence": [],
      "parent_obligation": null,
      "migration_relation": "NOT_EMITTED",
      "migration_status": "NOT_REVIEWED",
      "migration_evidence": [],
      "migration_rationale": "This coordinate was not emitted by the cube, so no parent-evidence migration decision exists.",
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "PRIORITY_GAP",
      "evidence": [
        "FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "No topology, comparison maps, error bounds, or regulator-independent continuum theorem joins finite models to smooth Weyl fields.",
      "boundary": "Cardinality resemblance is not convergence.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RECONSTRUCTION_LIMITS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "RECONSTRUCTION_LIMITS",
      "migration_relation": "EXACT_ONE_TO_ONE",
      "summary": "Short-poset topoi, finite contextual entropy, and categorical protocols give finite internal/contextual kinematics, states, dynamics, and reconstruction. For this obligation, the evidence directly supplies reconstruction, comparison, covariance, or continuum-limit obligations.",
      "boundary": "Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: a prediction-preserving comparison or controlled continuum theorem.",
      "migration_status": "EXACT_PARENT_TRANSFER",
      "migration_evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "migration_rationale": "The v0 obligation was not split, so its reviewed status and evidence transfer exactly.",
      "emitted": true
    }
  ],
  "evidence": {
    "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1": {
      "id": "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1",
      "kind": "LOCAL_RESULT",
      "result_kind": "FOUNDATIONAL_DEPENDENCY_CERTIFICATE",
      "lifecycle": "SEPARATED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC",
        "REDUCED-MODE"
      ],
      "claim_flags": {
        "separable_detector_algebra_constructed": true,
        "explicit_zf_states_constructed": true,
        "explicit_corner_gns_constructed": true,
        "semifinite_weight_is_normalized_state": false,
        "physical_thermodynamic_state_selected": false,
        "coherent_state_dynamically_selected": false,
        "full_orbit_algebra_separable": false,
        "lorentzian_claim": false
      },
      "does_not_establish": [
        "that B(l2(Z)) is separable",
        "a finite trace of the identity",
        "a canonical choice of incoming detector projection",
        "a thermodynamic normal state",
        "that the coherent CCR state is the BT physical state",
        "full nonlinear Moller dynamics or Eq. (19)",
        "a gravitational or BRST lift",
        "anything LORENTZIAN-CAUSAL"
      ],
      "result_path": "foundations/results/FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1.json",
      "report_path": "foundations/reports/bt-separable-cstar-state-chain.md",
      "report_link": "sources/foundations/reports/bt-separable-cstar-state-chain.md",
      "sha256": "08389e96d349766e29a34cde8109d4b1271288b59d44f3b29fcb456065641998"
    },
    "FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1": {
      "id": "FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1",
      "kind": "LOCAL_RESULT",
      "result_kind": "CODED_SECOND_ORDER_ARITHMETIC_UPPER_BOUND",
      "lifecycle": "CERTIFIED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC",
        "REDUCED-MODE"
      ],
      "claim_flags": {
        "rca0_upper_bound_for_declared_representation": true,
        "completed_energy_state_constructed": true,
        "real_time_solution_name_constructed": true,
        "energy_conservation_proved": true,
        "cauchy_uniqueness_in_declared_carrier": true,
        "weakest_base_proved": false,
        "reverse_lower_bound_proved": false,
        "representation_invariance_proved": false,
        "spacetime_distribution_constructed": false,
        "causal_green_operator_constructed": false,
        "choice_free_zf_theorem_proved": false,
        "new_lorentzian_claim": false
      },
      "does_not_establish": [
        "that RCA_0 is necessary or the weakest base",
        "a WKL_0, ACA_0, or Choice lower bound",
        "the same upper bound for bare finite-energy existence without a fast Cauchy name",
        "representation invariance",
        "a localized spacetime-distribution theorem",
        "finite propagation or an advanced/retarded Green map",
        "a variable-coefficient or curved-spacetime Cauchy theorem",
        "the biwave or metric-BV propagator",
        "a new LORENTZIAN-CAUSAL result"
      ],
      "result_path": "foundations/results/FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1.json",
      "report_path": "foundations/reports/coded-polygonal-wave-rca0.md",
      "report_link": "sources/foundations/reports/coded-polygonal-wave-rca0.md",
      "sha256": "4138c860c53fe85ba4fa1f2ece93cc5b6c0fce9468c7e5dfa69e314663b56ac7"
    },
    "FOUNDATIONAL_CODED_WAVE_FRONTIER_V2": {
      "id": "FOUNDATIONAL_CODED_WAVE_FRONTIER_V2",
      "kind": "LOCAL_RESULT",
      "result_kind": "CODED_UPPER_BOUND_AND_LITERATURE_FRONTIER",
      "lifecycle": "L2_UPPER_BOUND_CERTIFIED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC",
        "REDUCED-MODE",
        "LORENTZIAN-CAUSAL"
      ],
      "claim_flags": {
        "declared_representation_rca0_upper_bound": true,
        "literature_screen_completed": true,
        "weakest_base_proved": false,
        "reverse_lower_bound_proved": false,
        "bishop_hyperbolic_theorem_found": false,
        "zf_choice_free_pde_found": false,
        "computable_causal_support_proved": false,
        "new_lorentzian_claim": false
      },
      "does_not_establish": [
        "literature completeness",
        "that RCA_0 is the weakest base",
        "a reverse-mathematical equivalence for wave evolution",
        "a Bishop-constructive hyperbolic Green theorem",
        "a ZF-without-Choice PDE theorem",
        "that a distributional fundamental solution is retarded or advanced",
        "strict causal support",
        "a new Lorentzian Weyl result"
      ],
      "result_path": "foundations/results/FOUNDATIONAL_CODED_WAVE_FRONTIER_V2.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_CODED_WAVE_FRONTIER_V2.json",
      "report_path": "foundations/reports/coded-wave-frontier-v2.md",
      "report_link": "sources/foundations/reports/coded-wave-frontier-v2.md",
      "sha256": "d8832e2b5e2f8e762b885bdcd61263abd7a296bd0a4c691106331326c2397dde"
    },
    "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1": {
      "id": "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1",
      "kind": "LOCAL_RESULT",
      "result_kind": "FOUNDATIONAL_STRENGTH_LADDER",
      "lifecycle": "SEPARATED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC",
        "REDUCED-MODE",
        "LORENTZIAN-CAUSAL"
      ],
      "claim_flags": {
        "finite_cylinder_wave_exact": true,
        "explicit_tail_modulus_exact": true,
        "finite_spectral_locality_obstruction_exact": true,
        "typed_physics_to_mathematics_graph_constructed": true,
        "arbitrary_energy_completion_formalized_in_rca0": false,
        "weakest_base_proved": false,
        "choice_strength_proved": false,
        "spacetime_distribution_constructed": false,
        "causal_green_operator_constructed": false,
        "new_lorentzian_claim": false
      },
      "does_not_establish": [
        "that PRA proves an infinite completed energy-space theorem",
        "RCA_0 sufficiency for the selected representation",
        "a WKL_0, ACA_0, or stronger reversal",
        "a uniform constructive modulus extractor from bare finite-energy existence",
        "equivalence between coefficient-weak and spacetime-distributional solutions",
        "finite propagation or causal support from Fourier truncations",
        "a normally-hyperbolic Green theorem",
        "the full biwave or metric-BV propagator",
        "renormalized Lorentzian products or a QME theorem",
        "a new LORENTZIAN-CAUSAL result"
      ],
      "result_path": "foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1.json",
      "report_path": "foundations/reports/cylinder-wave-strength-ladder.md",
      "report_link": "sources/foundations/reports/cylinder-wave-strength-ladder.md",
      "sha256": "6fb1e264fe2d1b006aafe6b6ce285fcd7b01ffcd080b2b6e70631e46c93b0135"
    },
    "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2": {
      "id": "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2",
      "kind": "LOCAL_RESULT",
      "result_kind": "FOUNDATIONAL_STRENGTH_LADDER",
      "lifecycle": "L2_UPPER_BOUND_CERTIFIED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC",
        "REDUCED-MODE",
        "LORENTZIAN-CAUSAL"
      ],
      "claim_flags": {
        "finite_cylinder_wave_exact": true,
        "explicit_tail_modulus_exact": true,
        "finite_spectral_locality_obstruction_exact": true,
        "typed_physics_to_mathematics_graph_constructed": true,
        "arbitrary_energy_completion_formalized_in_rca0": true,
        "weakest_base_proved": false,
        "choice_strength_proved": false,
        "spacetime_distribution_constructed": false,
        "causal_green_operator_constructed": false,
        "new_lorentzian_claim": false,
        "declared_representation_rca0_upper_bound": true,
        "coefficient_weak_solution_formalized": false
      },
      "does_not_establish": [
        "that RCA_0 is necessary or the weakest base",
        "a WKL_0, ACA_0, or Choice reversal",
        "an upper bound for representations lacking prescribed Cauchy rates",
        "representation invariance",
        "a coefficient-weak or localized spacetime-distribution theorem",
        "finite propagation or causal support from Fourier or polygonal evolution",
        "a normally-hyperbolic Green theorem",
        "the full biwave or metric-BV propagator",
        "renormalized Lorentzian products or a QME theorem",
        "a new LORENTZIAN-CAUSAL result"
      ],
      "result_path": "foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2.json",
      "report_path": "foundations/reports/cylinder-wave-strength-ladder-v2.md",
      "report_link": "sources/foundations/reports/cylinder-wave-strength-ladder-v2.md",
      "sha256": "c043f1c8bc22344ee0fc378cb39789899009830708a6da7a4df5227cff015295"
    },
    "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1": {
      "id": "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1",
      "kind": "LOCAL_RESULT",
      "result_kind": "FOUNDATIONAL_DEPENDENCY_CERTIFICATE",
      "lifecycle": "SUFFICIENCY_PROVED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC",
        "REDUCED-MODE"
      ],
      "claim_flags": {
        "explicit_energy_self_adjointness_route_classified": true,
        "fock_fixed_energy_finiteness_route_classified": true,
        "abstract_spectral_theorem_used": false,
        "weakest_base_proved": false,
        "euclidean_spectral_measures_classified": false,
        "determinant_or_trace_constructed": false,
        "lorentzian_claim": false
      },
      "does_not_establish": [
        "ZF is the weakest base",
        "a reversal or independence theorem",
        "foundations of arbitrary self-adjoint operators",
        "Euclidean Hessian spectral measures",
        "determinants or traces",
        "an interacting Hamiltonian",
        "a LORENTZIAN-CAUSAL result"
      ],
      "result_path": "foundations/results/FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1.json",
      "report_path": "foundations/reports/explicit-energy-spectral-fragment-audit.md",
      "report_link": "sources/foundations/reports/explicit-energy-spectral-fragment-audit.md",
      "sha256": "0691b281e30ed16b1181be123116950cbd57fafffd43e0b528abcfab332c921c"
    },
    "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1": {
      "id": "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1",
      "kind": "LOCAL_RESULT",
      "result_kind": "FOUNDATIONAL_DEPENDENCY_CERTIFICATE",
      "lifecycle": "SUFFICIENCY_PROVED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC",
        "REDUCED-MODE"
      ],
      "claim_flags": {
        "explicit_strongly_continuous_unitary_group_constructed": true,
        "explicit_j_unitary_group_constructed": true,
        "explicit_point_norm_cstar_dynamics_constructed": true,
        "explicit_fock_unitary_group_constructed": true,
        "choice_or_countable_choice_used": false,
        "weakest_base_proved": false,
        "nonlinear_bt_dynamics_constructed": false,
        "interacting_dynamics_constructed": false,
        "causal_propagation_constructed": false,
        "physical_state_selected": false,
        "lorentzian_claim": false
      },
      "does_not_establish": [
        "that ZF is the weakest sufficient base",
        "exponentiation of the other unbounded conformal generators",
        "a representation of the full conformal group",
        "nonlinear Bateman-Turok Moller or full-orbit dynamics",
        "an interacting Weyl Hamiltonian or automorphism group",
        "causal Green propagation or a Lorentzian off-shell BV propagator",
        "state selection, a KMS state, or a generalized Born rule",
        "thermodynamic-limit implementability in an inequivalent representation",
        "anything LORENTZIAN-CAUSAL"
      ],
      "result_path": "foundations/results/FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1.json",
      "report_path": "foundations/reports/explicit-mode-dynamics-zf.md",
      "report_link": "sources/foundations/reports/explicit-mode-dynamics-zf.md",
      "sha256": "0880db47af0c27a0f99c2929ed6e4d42789ef03e67ff4fe6a55f1f49ba92d2f7"
    },
    "FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1": {
      "id": "FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1",
      "kind": "LOCAL_RESULT",
      "result_kind": "FOUNDATIONAL_NON_EQUIVALENCE_LEDGER",
      "lifecycle": "SEPARATED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC",
        "REDUCED-MODE"
      ],
      "claim_flags": {
        "four_objects_typed": true,
        "pairwise_non_equivalence_witnessed": true,
        "continuum_bridge_constructed": false,
        "finite_field_replaces_complex_quantum_scalars": false,
        "mode_cutoff_implies_finitism": false,
        "finitism_empirically_selected": false,
        "lorentzian_claim": false
      },
      "does_not_establish": [
        "a no-go theorem for finite-field physics",
        "a continuum limit of finite-field Wigner systems",
        "equivalence of varying prime-power dimensions",
        "convergence of Weyl mode cutoffs",
        "a finitist construction of real or complex analysis",
        "empirical evidence for or against actual infinity",
        "a finite formulation of interacting Weyl gravity",
        "anything LORENTZIAN-CAUSAL"
      ],
      "result_path": "foundations/results/FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1.json",
      "report_path": "foundations/reports/finite-field-versus-finite-mode.md",
      "report_link": "sources/foundations/reports/finite-field-versus-finite-mode.md",
      "sha256": "032680510c343485a3a786660435441b5c03defd1cecaac12ffc92553fc088af"
    },
    "FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1": {
      "id": "FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1",
      "kind": "LOCAL_RESULT",
      "result_kind": "EXACT_FINITE_DISCRETE_CAUSAL_GREEN_KERNEL",
      "lifecycle": "CERTIFIED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC",
        "REDUCED-MODE"
      ],
      "claim_flags": {
        "finite_exact_retarded_kernel_constructed": true,
        "finite_exact_advanced_kernel_constructed": true,
        "graph_step_support_certified": true,
        "continuum_green_operator_constructed": false,
        "lorentzian_causal_claim": false,
        "continuum_limit_proved": false
      },
      "does_not_establish": [
        "continuum finite propagation",
        "a Lorentzian advanced or retarded Green operator",
        "CFL stability or convergence under refinement",
        "a regulator-independent continuum limit",
        "a Weyl metric BV propagator",
        "a reverse-mathematical classification of continuum PDE"
      ],
      "result_path": "foundations/results/FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1.json",
      "report_path": "foundations/reports/finite-graph-wave-causality.md",
      "report_link": "sources/foundations/reports/finite-graph-wave-causality.md",
      "sha256": "2790e43f566c86e07f7b452fdfac516c59d319df4fd2e410664e7ff130396e79"
    },
    "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": {
      "id": "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
      "kind": "LOCAL_RESULT",
      "result_kind": "EXACT_FINITE_INTERACTION_WITNESS",
      "lifecycle": "VERIFIED_BOUNDED_MODEL",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC",
        "REDUCED-MODE"
      ],
      "claim_flags": {
        "exact_finite_interaction_model": true,
        "exact_state_and_probability_witness": true,
        "exact_entanglement_generation_witness": true,
        "exact_finite_krein_companion": true,
        "weakest_base_classified": false,
        "continuum_limit_established": false,
        "renormalization_established": false,
        "qme_restored": false,
        "lorentzian_causal_claim": false
      },
      "does_not_establish": [
        "a weakest logical or set-theoretic base",
        "that PRA, ZF without Choice, Bishop constructivism, and finitism are equivalent regimes",
        "an infinite-dimensional Hilbert, Krein, or C*-completion",
        "a continuum field theory or controlled continuum limit",
        "a Weyl-gravity interaction vertex",
        "counterterm or anomaly classification",
        "renormalization or restoration of the quantum master equation",
        "a physical selection principle for the displayed states",
        "a Lorentzian propagator, Hadamard state, or causal quantum theory"
      ],
      "result_path": "foundations/results/FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1.json",
      "report_path": "foundations/reports/finite-qubit-interaction-core.md",
      "report_link": "sources/foundations/reports/finite-qubit-interaction-core.md",
      "sha256": "8c92b0482802a4c54a6876f46fc78ff9a571a1298a5c5649014116e79872512e"
    },
    "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1": {
      "id": "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1",
      "kind": "LOCAL_RESULT",
      "result_kind": "FOUNDATIONAL_DEPENDENCY_CERTIFICATE",
      "lifecycle": "SUFFICIENCY_PROVED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC"
      ],
      "claim_flags": {
        "fixed_energy2_integer_sdr_verified": true,
        "pra_sufficiency_for_fixed_checker": true,
        "hahn_banach_avoided_for_displayed_certificate": true,
        "weakest_base_proved": false,
        "necessity_or_reversal_proved": false,
        "all_energy_bv_classified": false,
        "classical_import_freeze": false,
        "choice_free_infinite_completion": false,
        "constructive_weyl_qft": false,
        "lorentzian_claim": false
      },
      "does_not_establish": [
        "That PRA is the weakest possible base theory.",
        "A reversal or necessity theorem for any comprehension or choice principle.",
        "That the source producer, all energy levels, the Fock lift, or the complete field-derived BV complex is independently verified.",
        "That arbitrary finite-dimensional linear algebra avoids Choice without an explicit presentation and witness.",
        "A choice-free countable or infinite-dimensional Hilbert, Krein, spectral, Green-operator, state, or renormalization construction.",
        "A complete classical import freeze or any publishable quantum promotion.",
        "Any EUCLIDEAN-SPECTRAL, REDUCED-MODE, or LORENTZIAN-CAUSAL claim."
      ],
      "result_path": "foundations/results/FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1.json",
      "report_path": "foundations/reports/free-bv-energy2-pra-sdr.md",
      "report_link": "sources/foundations/reports/free-bv-energy2-pra-sdr.md",
      "sha256": "d0943e804f386155ac635f027101912b6d0c0385d1c10a6c6e0daf1c3399a3e5"
    },
    "FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1": {
      "id": "FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1",
      "kind": "LOCAL_RESULT",
      "result_kind": "FOUNDATIONAL_PROOF_DEPENDENCY_AUDIT",
      "lifecycle": "SEPARATED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC"
      ],
      "claim_flags": {
        "hardy_kn_step_audited": true,
        "rca0_sufficient_for_explicit_modulus_route": true,
        "physical_axiom_implies_rca0_or_wkl0": false,
        "weakest_base_proved": false,
        "full_hardy_reconstruction_audited": false,
        "empirical_superiority_established": false,
        "lorentzian_claim": false
      },
      "does_not_establish": [
        "a weakest-base theorem",
        "a reversal to RCA_0 or WKL_0",
        "the strength of extracting a modulus from every pointwise-continuous code",
        "the full K=N^r derivation",
        "the K=N^2 quantum reconstruction",
        "that Axiom 5 is empirically necessary",
        "infinite-dimensional quantum theory",
        "anything LORENTZIAN-CAUSAL"
      ],
      "result_path": "foundations/results/FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_HARDY_CONTINUITY_KN_AUDIT_V1.json",
      "report_path": "foundations/reports/hardy-continuity-kn-foundational-audit.md",
      "report_link": "sources/foundations/reports/hardy-continuity-kn-foundational-audit.md",
      "sha256": "225c89304bd9625ee2a08ab330b2dbb615279e277cd37410324a39b2732598be"
    },
    "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1": {
      "id": "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
      "kind": "LOCAL_RESULT",
      "result_kind": "FOUNDATIONAL_DEPENDENCY_CERTIFICATE",
      "lifecycle": "SUFFICIENCY_PROVED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC",
        "REDUCED-MODE"
      ],
      "claim_flags": {
        "finite_integral_j_verified": true,
        "explicit_mode_index_countable_in_zf": true,
        "zf_one_particle_completion_sufficient": true,
        "zf_explicit_bosonic_fock_sufficient": true,
        "choice_or_countable_choice_used_for_displayed_carriers": false,
        "weakest_base_proved": false,
        "arbitrary_krein_space_classified": false,
        "sobolev_scale_foundations_classified": false,
        "generator_domain_foundations_classified": false,
        "trace_or_state_constructed": false,
        "physical_probability_constructed": false,
        "constructive_weyl_qft": false,
        "lorentzian_claim": false
      },
      "does_not_establish": [
        "That ZF is the weakest foundation for the countable completion or Fock construction.",
        "A reverse-mathematical equivalence or necessity theorem for Infinity, comprehension, Countable Choice, or Choice.",
        "That an arbitrary indefinite inner-product space admits a fundamental decomposition without Choice.",
        "That an arbitrary Hilbert space has an orthonormal basis in ZF.",
        "Foundational classifications of the all-real-order Sobolev scale, closed generator domains, exponentiation, or the conformal group representation.",
        "A trace-class density operator, normal state, generalized Born rule, particle-unitarity theorem, or interacting implementer.",
        "A positive graviton Hilbert space, complete covariant BV propagator, Hadamard state, QME theorem, or any LORENTZIAN-CAUSAL claim."
      ],
      "result_path": "foundations/results/FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1.json",
      "report_path": "foundations/reports/krein-explicit-j-zf-audit.md",
      "report_link": "sources/foundations/reports/krein-explicit-j-zf-audit.md",
      "sha256": "bd71c8609cd6ff5d83d5f67aa86f46216f5301b377e6a437a74d197b577d9b2a"
    },
    "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1": {
      "id": "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1",
      "kind": "LOCAL_RESULT",
      "result_kind": "FOUNDATIONAL_DEPENDENCY_CERTIFICATE",
      "lifecycle": "SUFFICIENCY_PROVED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC",
        "REDUCED-MODE"
      ],
      "claim_flags": {
        "explicit_zf_krein_vector_states_constructed": true,
        "explicit_rank_one_density_witnesses_constructed": true,
        "explicit_fock_coordinate_states_constructed": true,
        "state_existence_requires_choice_here": false,
        "j_alone_selects_unique_state": false,
        "sign_permutation_invariant_density_state_exists": false,
        "singular_state_nonexistence_proved": false,
        "physical_weyl_state_selected": false,
        "generalized_born_rule_derived": false,
        "interacting_state_constructed": false,
        "lorentzian_claim": false
      },
      "does_not_establish": [
        "a unique or canonical state from J",
        "nonexistence of singular permutation-invariant states",
        "that sign-preserving coordinate permutations are a required physical symmetry",
        "a KMS, Hadamard, BRST-compatible, incoming, outgoing, or interacting state",
        "a generalized Born rule or physical probability interpretation",
        "trace-norm thermodynamic convergence of the Bateman-Turok construction",
        "positivity with respect to the Krein adjoint where Hilbert-adjoint positivity was used",
        "a weakest-base reverse-mathematics theorem",
        "anything LORENTZIAN-CAUSAL"
      ],
      "result_path": "foundations/results/FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1.json",
      "report_path": "foundations/reports/krein-state-selection-zf.md",
      "report_link": "sources/foundations/reports/krein-state-selection-zf.md",
      "sha256": "d1593c67e67a99c8b14b12dae5ac1364e26f34631c86b12cefaffd9ade9fd3ff"
    },
    "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1": {
      "id": "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1",
      "kind": "LOCAL_RESULT",
      "result_kind": "FOUNDATIONAL_SCOPE_AUDIT",
      "lifecycle": "SEPARATED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC",
        "REDUCED-MODE"
      ],
      "claim_flags": {
        "three_existing_result_closures_identified": true,
        "local_bv_cohomology_imported_with_scope": true,
        "local_counterterm_anomaly_classes_imported_with_scope": true,
        "finite_cutoff_dynamics_imported_with_scope": true,
        "remaining_assessed_open_cells_exhaustively_triaged": true,
        "classical_freeze_gate_passed": false,
        "qme_restored": false,
        "lorentzian_certified": false,
        "all_216_cells_assessed": false,
        "remaining_cells_impossible": false
      },
      "does_not_establish": [
        "a complete global smooth or distributional off-shell BV complex",
        "the classical import freeze gate",
        "a complete classification beyond the regular Bach locus and declared derivative bounds",
        "counterterm or anomaly coefficients",
        "regulated Slavnov breaking, renormalized products, or QME restoration",
        "residual transfer or a one-particle interpretation of residual classes",
        "a finite-to-continuum comparison or regulator-independent limit",
        "causal propagation or any LORENTZIAN-CAUSAL theorem",
        "that any remaining open cell is impossible or unimportant",
        "that any of the 157 NOT_MAPPED cells has been assessed"
      ],
      "result_path": "foundations/results/FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1.json",
      "report_path": "foundations/reports/low-hanging-cell-closure-audit.md",
      "report_link": "sources/foundations/reports/low-hanging-cell-closure-audit.md",
      "sha256": "b045541be48cd2210d8aa26d4e6a7df44456c8e7e6d481334165b96661ed3309"
    },
    "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1": {
      "id": "FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1",
      "kind": "LOCAL_RESULT",
      "result_kind": "LITERATURE_AND_FOUNDATIONAL_DEPENDENCY_ATLAS",
      "lifecycle": "LITERATURE_SCOPED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC",
        "REDUCED-MODE",
        "LORENTZIAN-CAUSAL"
      ],
      "claim_flags": {
        "classical_factor_theorem_identified": true,
        "computable_upper_bound_identified": true,
        "finite_exact_support_constructed": true,
        "reverse_math_strength_proved": false,
        "bishop_constructive_green_theorem_identified": false,
        "choice_free_green_theorem_proved": false,
        "full_biwave_reversal_proved": false,
        "new_weyl_bv_propagator": false
      },
      "does_not_establish": [
        "literature completeness",
        "a weakest subsystem",
        "an RCA_0, WKL_0 or ACA_0 equivalence",
        "a Bishop-constructive globally hyperbolic Green theorem",
        "Choice avoidance for Sobolev/distribution theory",
        "a continuum limit from finite graphs",
        "a full off-shell Weyl metric BV propagator",
        "a BRST-compatible Hadamard state",
        "renormalized Lorentzian products or a Lorentzian QME"
      ],
      "result_path": "foundations/results/FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1.json",
      "report_path": "foundations/reports/normal-hyperbolic-factor-foundations.md",
      "report_link": "sources/foundations/reports/normal-hyperbolic-factor-foundations.md",
      "sha256": "40836e986d2ba7b957cc51298c1bd724ace32ef59f846a7abc63b8980143a6c4"
    },
    "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0": {
      "id": "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0",
      "kind": "LOCAL_RESULT",
      "result_kind": "FOUNDATIONAL_GLOSSARY_AND_OBSTRUCTION_LEDGER",
      "lifecycle": "LITERATURE_SCOPED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC"
      ],
      "claim_flags": {
        "glossary_complete_for_first_artifact": true,
        "obstruction_dag_closed": true,
        "ambient_topos_selected": false,
        "internal_weyl_bv_constructed": false,
        "internal_green_operators_constructed": false,
        "internal_krein_completion_constructed": false,
        "internal_physical_state_selected": false,
        "internal_renormalization_constructed": false,
        "internal_qme_restored": false,
        "external_equivalence_proved": false,
        "lorentzian_claim": false
      },
      "does_not_establish": [
        "a formalized topos-internal Weyl-gravity BV complex",
        "that every ordinary Weyl-gravity construction internalizes in an arbitrary topos",
        "a constructive theory of distributions or wavefront sets",
        "internal retarded or advanced Green operators",
        "a topos-internal Krein or Hilbert completion",
        "a physical state-selection or Born-rule theorem",
        "renormalized time-ordered products",
        "restoration of the quantum master equation",
        "equivalence with the repository's external classical or quantum theory",
        "anything LORENTZIAN-CAUSAL"
      ],
      "result_path": "foundations/results/FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0.json",
      "report_path": "foundations/reports/topos-weyl-bv-obstruction-ledger.md",
      "report_link": "sources/foundations/reports/topos-weyl-bv-obstruction-ledger.md",
      "sha256": "e1cb211b884575b74cf90e5f2195eb3a32494f49c3c3e89af7a88390c5f39e24"
    },
    "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1": {
      "id": "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1",
      "kind": "LOCAL_RESULT",
      "result_kind": "FOUNDATIONAL_PROOF_DEPENDENCY_AUDIT",
      "lifecycle": "SEPARATED",
      "dependency_tags": [
        "LOCAL-ALGEBRAIC",
        "LORENTZIAN-CAUSAL"
      ],
      "claim_flags": {
        "dependency_cut_complete_for_source_theorem": true,
        "finite_resolvent_algebra_replayed": true,
        "conditional_lorentzian_theorem_imported": true,
        "weakest_base_proved": false,
        "choice_free_pde_theorem_proved": false,
        "full_bv_propagator_constructed": false,
        "hadamard_state_constructed": false,
        "renormalized_products_constructed": false,
        "lorentzian_qme_proved": false
      },
      "does_not_establish": [
        "the weakest subsystem for normally-hyperbolic PDE",
        "Choice avoidance for Sobolev or distribution theory",
        "the energy hypotheses for an arbitrary Weyl operator",
        "a full off-shell metric BV propagator",
        "a BRST-compatible Hadamard state",
        "renormalized Lorentzian time-ordered products",
        "a Lorentzian QME theorem",
        "quantum theory"
      ],
      "result_path": "foundations/results/FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1.json",
      "result_link": "sources/foundations/results/FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1.json",
      "report_path": "foundations/reports/typed-biwave-green-foundational-dependencies.md",
      "report_link": "sources/foundations/reports/typed-biwave-green-foundational-dependencies.md",
      "sha256": "f00e642c25fec883441346884467a7251c4ee61b4980b0370f124845b9cba8d6"
    },
    "abramsky-coecke-2004": {
      "id": "abramsky-coecke-2004",
      "kind": "LITERATURE",
      "citation": "Samson Abramsky and Bob Coecke, A categorical semantics of quantum protocols, 2004.",
      "year": 2004,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/quant-ph/0402130",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "c8a4380c0707eb82a84efe53748280eb313c8eda89092fe38e16a48d6e295396",
      "supported_statements": [
        "Compact closed categories with biproducts express finite quantum protocols compositionally, with scalars and a Born-rule-like probabilistic interpretation emerging from the categorical structure."
      ],
      "boundary": "Categorical semantics is not itself a selected topos, a continuum field carrier, a constructive metatheory, or a derivation of physical Hilbert space from Weyl gravity.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "baer-2015": {
      "id": "baer-2015",
      "kind": "LITERATURE",
      "citation": "Christian Bär, Green-hyperbolic operators on globally hyperbolic spacetimes, Communications in Mathematical Physics 333 (2015), 1585-1615.",
      "year": 2015,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/1310.0738",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "879948318de8b4a5a74b52179f78120d074bc7773734b82495b6db4c363f4c99",
      "supported_statements": [
        "Normally hyperbolic wave operators are Green-hyperbolic on globally hyperbolic spacetimes; advanced and retarded maps have the declared support and extend continuously to several support classes.",
        "For symmetric hyperbolic systems the paper proves Cauchy uniqueness, existence, finite propagation and continuous dependence."
      ],
      "boundary": "This is a classical smooth/distributional theorem. It does not code the proof in second-order arithmetic, eliminate Choice, give a Bishop-constructive proof, or construct the Weyl metric BV propagator.",
      "ledger": "foundations/literature-causal-green-atlas-v1.json",
      "ledger_link": "sources/foundations/literature-causal-green-atlas-v1.json"
    },
    "bahr-dittrich-2009": {
      "id": "bahr-dittrich-2009",
      "kind": "LITERATURE",
      "citation": "Benjamin Bahr and Bianca Dittrich, Breaking and restoring of diffeomorphism symmetry in discrete gravity, 2009.",
      "year": 2009,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/0909.5688",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "e80f30fb657199abd9492224dcd716607184c0bace1bbf465cb870b099bc7c9b",
      "supported_statements": [
        "Discretization can break diffeomorphism symmetry and coarse-graining or perfect-action methods can be used to study its restoration."
      ],
      "boundary": "The analysis does not give a Weyl-BV cohomology certificate, establish quantum anomaly cancellation, or prove a continuum limit for this repository.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "barnich-brandt-henneaux-2000": {
      "id": "barnich-brandt-henneaux-2000",
      "kind": "LITERATURE",
      "citation": "Glenn Barnich, Friedemann Brandt, and Marc Henneaux, Local BRST cohomology in gauge theories, Physics Reports 338 (2000), 439-569.",
      "year": 2000,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/hep-th/0002245",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "5ee9e6cfdd557a06c135bf78c8bfce93d3d5085a61d016da2dff8f543fa381bf",
      "supported_statements": [
        "Local BRST cohomology classifies the anomaly consistency condition, counterterms, and classical deformations for broad classes of gauge theories."
      ],
      "boundary": "This is a classical-standard local cohomology framework. It does not compute Weyl-gravity coefficients, restore this repository's QME, or calibrate weak, constructive, or choice-free foundations.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "bateman-turok-2026": {
      "id": "bateman-turok-2026",
      "kind": "LITERATURE",
      "citation": "Sam Bateman and Neil Turok, Escape from Ostrogradsky via Hidden Ghost Parity (2026).",
      "year": 2026,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/2607.00096",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "c3a2cf3a6c408e199f6b8d2ea8c097f3f1e5b53384ad2d26a5cb8ea6d9504d90",
      "supported_statements": [
        "The Bateman-Turok proposal changes the state-space metric and adjoint/probability structure by using a Krein carrier and a fundamental ghost parity."
      ],
      "boundary": "The paper's tree-level positivity and deferred operator claims retain the boundaries audited in the repository; no foundational-strength result follows from this citation.",
      "ledger": "foundations/literature-ledger.json",
      "ledger_link": "sources/foundations/literature-ledger.json"
    },
    "bender-boettcher-1998": {
      "id": "bender-boettcher-1998",
      "kind": "LITERATURE",
      "citation": "Carl M. Bender and Stefan Boettcher, Real spectra in non-Hermitian Hamiltonians having PT symmetry, Physical Review Letters 80 (1998), 5243-5246.",
      "year": 1998,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/physics/9712001",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "6bfed99eb3401c1acaebd3096b8681cc998ab8b318ce4cc54a7c36ec0c66804e",
      "supported_statements": [
        "Families of non-Hermitian PT-symmetric Hamiltonians can have real positive spectra in an unbroken-symmetry regime."
      ],
      "boundary": "PT symmetry is not identical to Krein self-adjointness, and real spectrum alone does not supply a positive physical inner product, unitary dynamics, or a gauge-QFT state space.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "blackadar-farah-2026": {
      "id": "blackadar-farah-2026",
      "kind": "LITERATURE",
      "citation": "Bruce Blackadar and Ilijas Farah, Separable C*-algebras Without the Countable Axiom of Choice (2026).",
      "year": 2026,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/2602.15812",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "0eaa3c5e0b2e32c5c9267902f2330eb220848a0d22c13ce75093640304382158",
      "supported_statements": [
        "A substantial theory of separable C*-algebras, including representation, polynomial spectral mapping, and continuous functional calculus for commuting normal elements, can be developed in ZF.",
        "Without Choice, nonseparable examples can break familiar state-space and commutative representation conclusions."
      ],
      "boundary": "Does not automatically remove Choice from AQFT, interacting QFT, state selection, or nonseparable operator-algebra arguments.",
      "ledger": "foundations/literature-ledger.json",
      "ledger_link": "sources/foundations/literature-ledger.json"
    },
    "blackadar-farah-karagila-2026": {
      "id": "blackadar-farah-karagila-2026",
      "kind": "LITERATURE",
      "citation": "Bruce Blackadar, Ilijas Farah, and Asaf Karagila, Hilbert Spaces Without The Countable Axiom of Choice, revised 2026.",
      "year": 2026,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/2304.09602",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "954597e0dddc7d8e1398da2993e6e79d11f8db350be829c943f347f5a50bd55e",
      "supported_statements": [
        "Hilbert spaces and their operator theory can be studied in ZF without countable Choice, and pathologies expose distinctions hidden by ZFC.",
        "The assertion that every Hilbert space has the familiar basis behaviour is not a definition-level truth independent of set theory."
      ],
      "boundary": "Foundational Hilbert-space analysis, not evidence that a particular physical Hilbert space exhibits the pathological examples.",
      "ledger": "foundations/literature-ledger.json",
      "ledger_link": "sources/foundations/literature-ledger.json"
    },
    "brattka-2008": {
      "id": "brattka-2008",
      "kind": "LITERATURE",
      "citation": "Vasco Brattka, How incomputable is the separable Hahn-Banach theorem? (2008).",
      "year": 2008,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/0808.1663",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "aa9be8d188660afd549ba87fde94d7f73c3a997eb3fb6876e8c76d4a2c96ef2a",
      "supported_statements": [
        "The separable Hahn-Banach theorem also admits a uniform computability analysis, connecting its reverse-mathematical WKL calibration to computable analysis."
      ],
      "boundary": "A Weihrauch or computability classification is not automatically the same relation as implication over RCA_0 or derivability in constructive set theory.",
      "ledger": "foundations/literature-supplement-known-attempts-v1.json",
      "ledger_link": "sources/foundations/literature-supplement-known-attempts-v1.json"
    },
    "brenna-flori-2012": {
      "id": "brenna-flori-2012",
      "kind": "LITERATURE",
      "citation": "W. Brenna and Cecilia Flori, Complex Numbers, One-Parameter of Unitary Transformations and Stone's Theorem in Topos Quantum Theory, 2012.",
      "year": 2012,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/1206.0809",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "09665e503ca0343b4deb50440962488c32c86031b235cca686e3e43923766f14",
      "supported_statements": [
        "The topos approach admits an internal treatment of one-parameter groups and a counterpart of Stone's theorem."
      ],
      "boundary": "An internal Stone theorem is not spacetime propagation, Green-hyperbolicity, renormalization, or an empirical equivalence theorem.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "bridges-svozil-2000": {
      "id": "bridges-svozil-2000",
      "kind": "LITERATURE",
      "citation": "Douglas Bridges and Karl Svozil, Constructive Mathematics and Quantum Physics, International Journal of Theoretical Physics 39 (2000), 503-515.",
      "year": 2000,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.1023/A:1003613131948",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "ff57b742a7669a1bfbcffe3840db3aa85a6b2d43451a40f7a3af27659ed2b678",
      "supported_statements": [
        "Bishop-style constructive mathematics can isolate constructive properties of Hilbert subspaces and projections and formulate a constructive quantum-logical axiom system."
      ],
      "boundary": "The paper is an attempt at constructive quantum foundations, not a complete constructive dynamics, continuum QFT, or gravity construction.",
      "ledger": "foundations/literature-supplement-known-attempts-v1.json",
      "ledger_link": "sources/foundations/literature-supplement-known-attempts-v1.json"
    },
    "bridges-wang-1998-dirichlet": {
      "id": "bridges-wang-1998-dirichlet",
      "kind": "LITERATURE",
      "citation": "Douglas Bridges and Luminiţa Vîţă Wang, Constructive aspects of the Dirichlet problem, Bulletin of the London Mathematical Society 30 (1998), 579-588.",
      "year": null,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.1112/S0024610798006243",
      "artifact_status": "METADATA_ONLY",
      "artifact_sha256": null,
      "supported_statements": [
        "The paper constructively treats weak solutions of the Dirichlet problem and dependence on boundary or domain data in its elliptic setting."
      ],
      "boundary": "This is genuine constructive PDE evidence, but it is elliptic rather than hyperbolic and supplies no causal Green maps.",
      "ledger": "foundations/literature-coded-wave-frontier-v2.json",
      "ledger_link": "sources/foundations/literature-coded-wave-frontier-v2.json"
    },
    "brown-simpson-1986": {
      "id": "brown-simpson-1986",
      "kind": "LITERATURE",
      "citation": "Douglas K. Brown and Stephen G. Simpson, Which set existence axioms are needed to prove the separable Hahn-Banach theorem?, Annals of Pure and Applied Logic 31 (1986), 123-144.",
      "year": 1986,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.1016/0168-0072(86)90066-7",
      "artifact_status": "METADATA_ONLY",
      "artifact_sha256": null,
      "supported_statements": [
        "Over RCA_0, the separable Hahn-Banach theorem studied in the paper is equivalent to WKL_0."
      ],
      "boundary": "This is a reverse-mathematical result for a coded separable theorem, not the ZF choice strength of unrestricted Hahn-Banach and not proof that a concrete physics calculation invokes it.",
      "ledger": "foundations/literature-supplement-known-attempts-v1.json",
      "ledger_link": "sources/foundations/literature-supplement-known-attempts-v1.json"
    },
    "brunetti-fredenhagen-rejzner-2013": {
      "id": "brunetti-fredenhagen-rejzner-2013",
      "kind": "LITERATURE",
      "citation": "Romeo Brunetti, Klaus Fredenhagen, and Katarzyna Rejzner, Quantum gravity from the point of view of locally covariant quantum field theory, Communications in Mathematical Physics 345 (2016), 741-779.",
      "year": 2013,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/1306.1058",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "4b4dc94875540cd997394551f44c363c2322231a66d6195aba3dfaa6369356b8",
      "supported_statements": [
        "Perturbative quantum gravity can be formulated as an effective locally covariant theory using renormalized BV methods and relational observables."
      ],
      "boundary": "This does not establish perturbative renormalizability, the Weyl-gravity QME, a nonperturbative theory, or a weak/constructive foundational calibration.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "brunetti-fredenhagen-verch-2001": {
      "id": "brunetti-fredenhagen-verch-2001",
      "kind": "LITERATURE",
      "citation": "Romeo Brunetti, Klaus Fredenhagen, and Rainer Verch, The generally covariant locality principle: A new paradigm for local quantum field theory, Communications in Mathematical Physics 237 (2003), 31-68.",
      "year": 2001,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/math-ph/0112041",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "7b3b2852a16ef2a1a6a128ba2a51b3358853ee03b7a03481490f648b353a42d4",
      "supported_statements": [
        "Locally covariant QFT is formulated as a functor from globally hyperbolic spacetimes to star-algebras, with admissible state spaces and relative Cauchy evolution."
      ],
      "boundary": "The framework supplies architecture, not a Weyl-gravity model, a preferred state, a weak-foundation audit, or the missing full metric-BV Hadamard construction.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "chiribella-dariano-perinotti-2011": {
      "id": "chiribella-dariano-perinotti-2011",
      "kind": "LITERATURE",
      "citation": "Giulio Chiribella, Giacomo Mauro D'Ariano, and Paolo Perinotti, Informational derivation of quantum theory, Physical Review A 84, 012311 (2011).",
      "year": 2011,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.1103/PhysRevA.84.012311",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "71bc890fc29e1ea180306b387ae27982735fd73243492f01ad85cc8737a31d20",
      "supported_statements": [
        "Within an operational-probabilistic framework, five informational axioms define a broad class and purification selects quantum theory without taking Hilbert space as the starting postulate."
      ],
      "boundary": "A reconstruction result in its declared operational framework; its proof has not yet been audited for logical or choice strength here.",
      "ledger": "foundations/literature-ledger.json",
      "ledger_link": "sources/foundations/literature-ledger.json"
    },
    "constantin-doring-2020": {
      "id": "constantin-doring-2020",
      "kind": "LITERATURE",
      "citation": "Carmen Maria Constantin and Andreas Doring, A topos theoretic notion of entropy, 2020.",
      "year": 2020,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/2006.03139",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "2b6230a502f03bd1176866b49b0dd96e9df59eb8c74f4e7a4ea9df63b72104f8",
      "supported_statements": [
        "For finite-dimensional systems of dimension at least three, contextual entropy determines the density matrix and the paper gives an explicit reconstruction algorithm."
      ],
      "boundary": "This is finite-dimensional mathematical state reconstruction, not physical state selection, field dynamics, or an internal renormalized gauge theory.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "coquand-spitters-2009": {
      "id": "coquand-spitters-2009",
      "kind": "LITERATURE",
      "citation": "Thierry Coquand and Bas Spitters, Constructive Gelfand duality for C*-algebras, Math. Proc. Cambridge Philos. Soc. 147 (2009), 339-344.",
      "year": 2009,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.1017/S0305004109002515",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "86ac9042dae2bb37d28e2d26fe50ca98f5e08d343827b6198b5a5a5d0c477cfd",
      "supported_statements": [
        "Commutative Gelfand duality admits a constructive formulation in which spectra are handled point-free."
      ],
      "boundary": "Constructive commutative duality is not a complete constructive formulation of interacting quantum field theory.",
      "ledger": "foundations/literature-ledger.json",
      "ledger_link": "sources/foundations/literature-ledger.json"
    },
    "dittrich-2012": {
      "id": "dittrich-2012",
      "kind": "LITERATURE",
      "citation": "Bianca Dittrich, From the discrete to the continuous: Towards a cylindrically consistent dynamics, New Journal of Physics 14 (2012), 123004.",
      "year": 2012,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/1205.6127",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "7ddf07b07db39a1cc750332b35f0b981d22f4f17b4fee8b17d0a23bee218ed68",
      "supported_statements": [
        "Cylindrical consistency, embedding maps, and coarse graining provide explicit obligations for connecting discrete dynamics to a continuum theory."
      ],
      "boundary": "This is a continuum-construction framework, not a completed continuum theorem for Weyl gravity or a foundational rejection of actual infinity.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "doring-2008": {
      "id": "doring-2008",
      "kind": "LITERATURE",
      "citation": "Andreas Doring, Quantum states and measures on the spectral presheaf, 2008.",
      "year": 2008,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/0809.4847",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "f2ba261f9e2db144fd6ec3b62cb5c810cb7cc1d5e31d86f52ba19594a491b444",
      "supported_statements": [
        "Normal states on a von Neumann algebra are related to measures on the spectral presheaf in the topos approach to quantum theory."
      ],
      "boundary": "A state-measure representation is not a physical state-selection rule, a Born-rule derivation, or an internal interacting field theory.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "esmeral-ferrer-wagner-2015": {
      "id": "esmeral-ferrer-wagner-2015",
      "kind": "LITERATURE",
      "citation": "K. Esmeral, O. Ferrer, and E. Wagner, Frames in Krein spaces arising from a non-regular W-metric, Banach Journal of Mathematical Analysis 9 (2015), 1-16.",
      "year": 2015,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.15352/bjma/09-1-1",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "5778214f73d0965dc5e1fb3d09df3f9c4a630c74c26fc389fac7d5b53d25f811",
      "supported_statements": [
        "A Krein space has an indefinite product together with a fundamental symmetry whose associated positive product supplies a Hilbert-space topology."
      ],
      "boundary": "A mathematical structural fact; it neither validates a generalized Born rule nor removes set-theoretic assumptions from infinite-dimensional analysis.",
      "ledger": "foundations/literature-ledger.json",
      "ledger_link": "sources/foundations/literature-ledger.json"
    },
    "fewster-verch-2011": {
      "id": "fewster-verch-2011",
      "kind": "LITERATURE",
      "citation": "Christopher J. Fewster and Rainer Verch, Dynamical locality of the free scalar field, Annales Henri Poincare 13 (2012), 1675-1709.",
      "year": 2011,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/1109.6732",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "237961555e9422c25a701971f1efa1c4962d8daebe0083688b22fae83899711e",
      "supported_statements": [
        "Dynamical locality compares kinematic and dynamically defined local content and is established for classical and quantized scalar models, with explicit exceptional cases."
      ],
      "boundary": "The scalar examples are not a theorem for gauge theories or Weyl gravity; the paper itself identifies gauge-theoretic complications.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "fredenhagen-rejzner-2011": {
      "id": "fredenhagen-rejzner-2011",
      "kind": "LITERATURE",
      "citation": "Klaus Fredenhagen and Katarzyna Rejzner, Batalin-Vilkovisky formalism in perturbative algebraic quantum field theory, Communications in Mathematical Physics 317 (2013), 697-725.",
      "year": 2011,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/1110.5232",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "3d7f7f555ea0ab839b3104a756d125ca490563d3bb41adc7b98e4e1809284846",
      "supported_statements": [
        "The BV formalism can be combined with perturbative AQFT, including renormalized time-ordered products and the anomalous master Ward identity."
      ],
      "boundary": "This does not instantiate the full Weyl metric complex or certify its Lorentzian QME, and it contains no reverse-mathematical or constructive strength analysis.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "gibbons-hoffman-wootters-2004": {
      "id": "gibbons-hoffman-wootters-2004",
      "kind": "LITERATURE",
      "citation": "Kathleen S. Gibbons, Matthew J. Hoffman, and William K. Wootters, Discrete phase space based on finite fields, Physical Review A 70, 062101 (2004).",
      "year": 2004,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.1103/PhysRevA.70.062101",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "56a4949865a9b62b550da45763c0239b6df218c22437c6d03077d2dacbee0470",
      "supported_statements": [
        "For finite-dimensional quantum systems of prime-power dimension, finite-field phase space supports discrete Wigner functions and mutually unbiased line-associated bases."
      ],
      "boundary": "A finite kinematics for selected dimensions is not a finite replacement for continuum dynamics, Lorentzian QFT, or a convergence theorem.",
      "ledger": "foundations/literature-supplement-known-attempts-v1.json",
      "ledger_link": "sources/foundations/literature-supplement-known-attempts-v1.json"
    },
    "gottschalk-2004": {
      "id": "gottschalk-2004",
      "kind": "LITERATURE",
      "citation": "Hanno Gottschalk, Complex velocity transformations and the Bisognano-Wichmann theorem for quantum fields acting on Krein spaces, 2004.",
      "year": 2004,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/math-ph/0408048",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "334697d3c5c66b6c1739c3e7cb10b29c9f89daee689f353a8e314b8d2d142fe0",
      "supported_statements": [
        "Relativistic local fields on Krein space admit analytic-vector and modular-theoretic results under stated axioms, extending a Bisognano-Wichmann-type characterization."
      ],
      "boundary": "This is an indefinite-metric QFT result under strong axioms, not a construction of the full Weyl metric BV theory, positive Born probabilities, or choice-free analysis.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "grinkevich-1996": {
      "id": "grinkevich-1996",
      "kind": "LITERATURE",
      "citation": "Yuri B. Grinkevich, Synthetic Differential Geometry: A Way to Intuitionistic Models of General Relativity in Toposes (1996).",
      "year": 1996,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/gr-qc/9608013",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "25a1fe2f2e3fdf7ce0b06ab99fa72c22569a2df22ca62762b6900eeaf72a6fbd",
      "supported_statements": [
        "Synthetic differential geometry in a suitable topos supports intuitionistic models of Riemannian geometry and Einstein equations on formal manifolds."
      ],
      "boundary": "This is a classical-gravity reformulation route; it does not supply a constructive quantum Weyl theory or an external equivalence theorem for every classical spacetime.",
      "ledger": "foundations/literature-supplement-known-attempts-v1.json",
      "ledger_link": "sources/foundations/literature-supplement-known-attempts-v1.json"
    },
    "haag-kastler-1964": {
      "id": "haag-kastler-1964",
      "kind": "LITERATURE",
      "citation": "Rudolf Haag and Daniel Kastler, An Algebraic Approach to Quantum Field Theory, Journal of Mathematical Physics 5 (1964), 848-861.",
      "year": 1964,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.1063/1.1704187",
      "artifact_status": "METADATA_ONLY",
      "artifact_sha256": null,
      "supported_statements": [
        "Local quantum field theory can be axiomatized algebra-first in terms of observables and locality rather than beginning with a preferred global Hilbert-space realization."
      ],
      "boundary": "Algebra-first formulation moves but does not erase representation, state-existence, topology, infinity, or set-existence questions.",
      "ledger": "foundations/literature-supplement-known-attempts-v1.json",
      "ledger_link": "sources/foundations/literature-supplement-known-attempts-v1.json"
    },
    "harding-heunen-2019": {
      "id": "harding-heunen-2019",
      "kind": "LITERATURE",
      "citation": "John Harding and Chris Heunen, Topos quantum theory with short posets, 2019.",
      "year": 2019,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/1903.01897",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "16b913fe349e433e0296d4f33fcff69ac4aee5db3d7e7db0f1683d21ccab7ad4",
      "supported_statements": [
        "A smaller context poset yields a different topos while retaining core results on Kochen-Specker obstruction, spectral representation, state measures, and dynamics."
      ],
      "boundary": "Changing the context poset changes internal logic; preservation of these core results is not a general invariance theorem for field theory, BV, or empirical predictions.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "hardy-2001": {
      "id": "hardy-2001",
      "kind": "LITERATURE",
      "citation": "Lucien Hardy, Quantum Theory From Five Reasonable Axioms (2001).",
      "year": 2001,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/quant-ph/0101012",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "f809918a4518f4b5cfca032c8fa9bd54474f129782b87e2fab5c887d14232df4",
      "supported_statements": [
        "Finite-dimensional quantum formalism can be reconstructed from operational axioms, with continuity doing explicit work in separating the quantum and classical cases in this framework."
      ],
      "boundary": "Finite-dimensional reconstruction under its stated framework; it does not establish the foundations of infinite-dimensional QFT or the set-theoretic strength of the reconstruction proof.",
      "ledger": "foundations/literature-ledger.json",
      "ledger_link": "sources/foundations/literature-ledger.json"
    },
    "henry-2014": {
      "id": "henry-2014",
      "kind": "LITERATURE",
      "citation": "Simon Henry, Constructive Gelfand duality for non-unital commutative C*-algebras (2014).",
      "year": 2014,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/1412.2009",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "cc74be6390ab431820bd7a2676d4d5c75c9f60f2d0ce61a810170984fe49d9c4",
      "supported_statements": [
        "Constructive, localic Gelfand duality extends to non-unital commutative C*-algebras and locally compact locales."
      ],
      "boundary": "Commutative localic duality does not by itself construct noncommutative interacting QFT or its states and dynamics.",
      "ledger": "foundations/literature-supplement-known-attempts-v1.json",
      "ledger_link": "sources/foundations/literature-supplement-known-attempts-v1.json"
    },
    "heunen-landsman-spitters-2009": {
      "id": "heunen-landsman-spitters-2009",
      "kind": "LITERATURE",
      "citation": "Chris Heunen, Nicolaas P. Landsman, and Bas Spitters, A topos for algebraic quantum theory, Communications in Mathematical Physics 291 (2009), 63-110.",
      "year": 2009,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/0709.4364",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "cd36e253d40e7abb6a570a87f521b7979bd702670ad20f366f823b90ea2dd53b",
      "supported_statements": [
        "An algebraic quantum system can be represented internally in a topos with an intuitionistic Heyting logic and a localic spectrum."
      ],
      "boundary": "A reformulation of algebraic quantum theory; it does not establish empirical superiority, eliminate all external classical reasoning, or construct Weyl QFT.",
      "ledger": "foundations/literature-ledger.json",
      "ledger_link": "sources/foundations/literature-ledger.json"
    },
    "humphreys-simpson-1996": {
      "id": "humphreys-simpson-1996",
      "kind": "LITERATURE",
      "citation": "A. James Humphreys and Stephen G. Simpson, Separable Banach space theory needs strong set existence axioms, Transactions of the American Mathematical Society 348 (1996), 4231-4255.",
      "year": 1996,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.1090/S0002-9947-96-01742-6",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "cc70753351643360ef4a3d31bc4c4803903a74fa717ef24dc6c4405c1a658242",
      "supported_statements": [
        "Some weak-star closure existence statements for separable Banach-space duals require Pi^1_1 comprehension, so separability alone does not guarantee uniformly weak foundational strength."
      ],
      "boundary": "This does not make every theorem about a separable Banach space strong; the coded target and its representation determine the reversal.",
      "ledger": "foundations/literature-supplement-known-attempts-v1.json",
      "ledger_link": "sources/foundations/literature-supplement-known-attempts-v1.json"
    },
    "humphreys-simpson-1999": {
      "id": "humphreys-simpson-1999",
      "kind": "LITERATURE",
      "citation": "A. James Humphreys and Stephen G. Simpson, Separation and Weak Konig's Lemma, Journal of Symbolic Logic 64 (1999), 268-278.",
      "year": 1999,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.2307/2586763",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "a6a0f3bc4f6a385beb698b127564b7da0c5c8edd497c5fd2e438341c31cdbf4b",
      "supported_statements": [
        "Over RCA_0, separation for open convex sets is equivalent to WKL_0, while separation for separably closed convex sets is equivalent to ACA_0.",
        "The representation of a closed convex set changes the logical strength of an apparently similar separation claim."
      ],
      "boundary": "The result calibrates two precise separable Banach-space statements; it does not assign one strength to every use of geometric separation.",
      "ledger": "foundations/literature-supplement-known-attempts-v1.json",
      "ledger_link": "sources/foundations/literature-supplement-known-attempts-v1.json"
    },
    "kogut-susskind-1975": {
      "id": "kogut-susskind-1975",
      "kind": "LITERATURE",
      "citation": "John Kogut and Leonard Susskind, Hamiltonian formulation of Wilson's lattice gauge theories, Physical Review D 11 (1975), 395-408.",
      "year": 1975,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.1103/PhysRevD.11.395",
      "artifact_status": "METADATA_ONLY",
      "artifact_sha256": null,
      "supported_statements": [
        "Wilson lattice gauge theory admits a Hamiltonian formulation with gauge constraints and a continuum-limit programme."
      ],
      "boundary": "The historical formulation is not finite in every mathematical sense and does not supply a controlled Weyl-gravity continuum or BV-QME certificate.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "kostrykin-potthoff-schrader-2011": {
      "id": "kostrykin-potthoff-schrader-2011",
      "kind": "LITERATURE",
      "citation": "Vadim Kostrykin, Jürgen Potthoff, and Robert Schrader, Finite propagation speed for solutions of the wave equation on metric graphs, 2011.",
      "year": 2011,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/1106.0817",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "53c5f52ca32e7b9a0839287c154109d3bc04650f1eb11ceecea195fca5d33f47",
      "supported_statements": [
        "A class of self-adjoint Laplace operators on metric graphs has existence and uniqueness for the wave equation and strict finite propagation, proved by localized energy methods."
      ],
      "boundary": "Metric graphs retain continuous edges and Hilbert/Sobolev analysis. They are not finite exact algebra, a continuum-limit theorem, or a choice-free construction.",
      "ledger": "foundations/literature-causal-green-atlas-v1.json",
      "ledger_link": "sources/foundations/literature-causal-green-atlas-v1.json"
    },
    "mostafazadeh-2001": {
      "id": "mostafazadeh-2001",
      "kind": "LITERATURE",
      "citation": "Ali Mostafazadeh, Pseudo-Hermiticity versus PT symmetry: The necessary condition for the reality of the spectrum of a non-Hermitian Hamiltonian, Journal of Mathematical Physics 43 (2002), 205-214.",
      "year": 2001,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/math-ph/0107001",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "6e605e7fe3ff9eae870d7ad2406c00f479476d054200a43c6bb61c116334588c",
      "supported_statements": [
        "Pseudo-Hermiticity is introduced and shown to be a necessary structural condition for Hamiltonians with real spectrum in the setting studied."
      ],
      "boundary": "The result assumes analytic and spectral hypotheses and does not by itself define physical probabilities, interacting QFT, or a weakest foundational base.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "muehlhoff-2010": {
      "id": "muehlhoff-2010",
      "kind": "LITERATURE",
      "citation": "Rainer Mühlhoff, Cauchy Problem and Green's Functions for First Order Differential Operators and Algebraic Quantization, Journal of Mathematical Physics 52 (2011), 022303.",
      "year": 2011,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/1001.4091",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "5854613e375d64cfddf98ced287f12a8819a21a48db4bf89f24fa8ed0040cda7",
      "supported_statements": [
        "Prenormally hyperbolic first-order operators have unique advanced and retarded Green functions and a globally well-posed Cauchy problem under the stated globally hyperbolic hypotheses."
      ],
      "boundary": "The reduction imports the normally-hyperbolic second-order theorem and remains classical; it is not a foundational-strength or Weyl-BV result.",
      "ledger": "foundations/literature-causal-green-atlas-v1.json",
      "ledger_link": "sources/foundations/literature-causal-green-atlas-v1.json"
    },
    "nachtergaele-raz-schlein-sims-2007": {
      "id": "nachtergaele-raz-schlein-sims-2007",
      "kind": "LITERATURE",
      "citation": "Bruno Nachtergaele, Hillel Raz, Benjamin Schlein, and Robert Sims, Lieb-Robinson Bounds for Harmonic and Anharmonic Lattice Systems, Communications in Mathematical Physics 286 (2009), 1073-1098.",
      "year": 2009,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/0712.3820",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "613ff5cc8af3f7b9734a2ca1912f33624b59050204e108071c4d200285179114",
      "supported_statements": [
        "Harmonic and specified anharmonic lattice systems satisfy Lieb-Robinson bounds, including exponentially small commutators outside an effective cone for Weyl observables."
      ],
      "boundary": "An exponentially small tail is not strict support and is not an advanced/retarded Green operator. The result must not be promoted to continuum Lorentzian causality.",
      "ledger": "foundations/literature-causal-green-atlas-v1.json",
      "ledger_link": "sources/foundations/literature-causal-green-atlas-v1.json"
    },
    "neumann-pape-streicher-2018": {
      "id": "neumann-pape-streicher-2018",
      "kind": "LITERATURE",
      "citation": "Eike Neumann, Martin Pape, and Thomas Streicher, Computability in Basic Quantum Mechanics, Logical Methods in Computer Science 14(2:14) (2018), 1-20.",
      "year": 2018,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/1610.09209",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "7a7d6ed24ab6790751f4562aa491167ab9ff2e64e5e9fd38a32c8d40681cd03c",
      "supported_statements": [
        "For separable infinite-dimensional Hilbert spaces, states and observables can be represented by measures and valuations so that an effective spectral-theorem analysis becomes possible."
      ],
      "boundary": "Computable representations are not equivalent to a Bishop-constructive proof or an RCA_0 reversal, and the result does not supply interacting QFT.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    },
    "pischke-2025-semigroups": {
      "id": "pischke-2025-semigroups",
      "kind": "LITERATURE",
      "citation": "Nicholas Pischke, A proof-theoretic metatheorem for nonlinear semigroups generated by an accretive operator and applications, Selecta Mathematica 31 (2025), 32.",
      "year": null,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/2304.01723",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "df22f1d13d554d99c41a0da840078f0614680171b77338aa2507601a33856877",
      "supported_statements": [
        "Logical metatheorems cover nonlinear semigroups generated by accretive operators and support extraction of quantitative convergence information in the stated systems and case studies."
      ],
      "boundary": "Proof mining in higher-type systems is not an RCA_0/WKL_0/ACA_0 reversal, and the operator and semigroup structures are encoded assumptions rather than a causal PDE construction.",
      "ledger": "foundations/literature-coded-wave-frontier-v2.json",
      "ledger_link": "sources/foundations/literature-coded-wave-frontier-v2.json"
    },
    "pour-el-richards-1981": {
      "id": "pour-el-richards-1981",
      "kind": "LITERATURE",
      "citation": "Marian B. Pour-El and J. Ian Richards, The wave equation with computable initial data such that its unique solution is not computable, Advances in Mathematics 39 (1981), 215-239.",
      "year": null,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.1016/0001-8708(81)90001-3",
      "artifact_status": "METADATA_ONLY",
      "artifact_sha256": null,
      "supported_statements": [
        "Under the paper's representations, computable initial data can evolve to a unique wave solution with noncomputable values."
      ],
      "boundary": "The result is representation-sensitive and is not a no-go theorem for computable Sobolev wave propagation or for the explicit coefficient carrier used here.",
      "ledger": "foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1.json",
      "ledger_link": "sources/foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1.json"
    },
    "richman-bridges-1999": {
      "id": "richman-bridges-1999",
      "kind": "LITERATURE",
      "citation": "Fred Richman and Douglas Bridges, A Constructive Proof of Gleason's Theorem, Journal of Functional Analysis 162 (1999), 287-312.",
      "year": 1999,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.1006/jfan.1998.3372",
      "artifact_status": "METADATA_ONLY",
      "artifact_sha256": null,
      "supported_statements": [
        "Gleason's theorem has a constructive proof after its hypotheses and conclusion are given an appropriate constructive formulation."
      ],
      "boundary": "This is a reformulation and proof of a specific probability-representation theorem; it is not a constructive derivation of all quantum mechanics.",
      "ledger": "foundations/literature-supplement-known-attempts-v1.json",
      "ledger_link": "sources/foundations/literature-supplement-known-attempts-v1.json"
    },
    "selivanova-selivanov-2013": {
      "id": "selivanova-selivanov-2013",
      "kind": "LITERATURE",
      "citation": "Svetlana Selivanova and Victor Selivanov, Computing Solution Operators of Boundary-value Problems for Some Linear Hyperbolic Systems of PDEs, Logical Methods in Computer Science 13(4:13) (2017).",
      "year": 2017,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/1305.2494",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "71a4628b9e151eeb444f4db3c2d87cd2ad2f7d86e404bea9b3662da570f568be",
      "supported_statements": [
        "For symmetric hyperbolic systems on a cube with computable coefficients, the Cauchy solution operator is computable in the stated TTE representations; dissipative boundary-value problems are also treated under additional hypotheses.",
        "The proof uses rational finite-difference approximants with effective error estimates rather than an explicit solution formula."
      ],
      "boundary": "A TTE computability theorem is not a Bishop-constructive derivation, an RCA_0 upper bound or reversal, or a theorem for globally hyperbolic manifolds and advanced/retarded Green support.",
      "ledger": "foundations/literature-causal-green-atlas-v1.json",
      "ledger_link": "sources/foundations/literature-causal-green-atlas-v1.json"
    },
    "selivanova-selivanov-2018": {
      "id": "selivanova-selivanov-2018",
      "kind": "LITERATURE",
      "citation": "Svetlana Selivanova and Victor Selivanov, Bit Complexity of Computing Solutions for Symmetric Hyperbolic Systems of PDEs with Guaranteed Precision, 2020.",
      "year": 2020,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/1807.03140",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "9943569bd492d28d2ad8c70b30e4f85a852fe0e5c9fc7b7e034186691fd5893c",
      "supported_statements": [
        "The symmetric-hyperbolic computability programme admits explicit bit-complexity upper bounds under the paper's representations and coefficient hypotheses."
      ],
      "boundary": "Complexity of represented solution operators neither supplies strict causal Green support nor calibrates a subsystem of second-order arithmetic.",
      "ledger": "foundations/literature-causal-green-atlas-v1.json",
      "ledger_link": "sources/foundations/literature-causal-green-atlas-v1.json"
    },
    "simpson-1984-ode": {
      "id": "simpson-1984-ode",
      "kind": "LITERATURE",
      "citation": "Stephen G. Simpson, Which set existence axioms are needed to prove the Cauchy/Peano theorem for ordinary differential equations?, Journal of Symbolic Logic 49 (1984), 783-802.",
      "year": null,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.2307/2274131",
      "artifact_status": "METADATA_ONLY",
      "artifact_sha256": null,
      "supported_statements": [
        "Over RCA_0, the Cauchy-Peano existence theorem for ordinary differential equations is equivalent to WKL_0; stronger related ODE solution principles reach ACA_0."
      ],
      "boundary": "This calibrates ODE existence, not a hyperbolic PDE energy theorem, finite propagation, or a Green map.",
      "ledger": "foundations/literature-coded-wave-frontier-v2.json",
      "ledger_link": "sources/foundations/literature-coded-wave-frontier-v2.json"
    },
    "weihrauch-zhong-2002": {
      "id": "weihrauch-zhong-2002",
      "kind": "LITERATURE",
      "citation": "Klaus Weihrauch and Ning Zhong, Is wave propagation computable or can wave computers beat the Turing machine?, Proceedings of the London Mathematical Society 85 (2002), 312-332.",
      "year": null,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.1112/S0024611502013643",
      "artifact_status": "METADATA_ONLY",
      "artifact_sha256": null,
      "supported_statements": [
        "The paper proves computability of the wave propagator for specified continuously differentiable and Sobolev representations, with a loss of one derivative in the former setting and no loss in the stated Sobolev setting."
      ],
      "boundary": "This is TTE computable analysis, not a reverse-mathematical RCA_0/WKL_0/ACA_0 classification and not specifically the cylinder fixture.",
      "ledger": "foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1.json",
      "ledger_link": "sources/foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1.json"
    },
    "weihrauch-zhong-2006-fundamental": {
      "id": "weihrauch-zhong-2006-fundamental",
      "kind": "LITERATURE",
      "citation": "Klaus Weihrauch and Ning Zhong, An Algorithm for Computing Fundamental Solutions, SIAM Journal on Computing 35 (2006), 1283-1294.",
      "year": null,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.1137/S0097539704446360",
      "artifact_status": "METADATA_ONLY",
      "artifact_sha256": null,
      "supported_statements": [
        "The paper computes a distributional fundamental solution for every constant-coefficient differential operator in its represented setting."
      ],
      "boundary": "A fundamental solution is not automatically a retarded or advanced Green operator and the record does not establish causal support.",
      "ledger": "foundations/literature-coded-wave-frontier-v2.json",
      "ledger_link": "sources/foundations/literature-coded-wave-frontier-v2.json"
    },
    "weihrauch-zhong-2007-cauchy": {
      "id": "weihrauch-zhong-2007-cauchy",
      "kind": "LITERATURE",
      "citation": "Klaus Weihrauch and Ning Zhong, Computable analysis of the abstract Cauchy problem in a Banach space and its applications I, Mathematical Logic Quarterly 53 (2007), 511-531.",
      "year": null,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.1002/malq.200710015",
      "artifact_status": "METADATA_ONLY",
      "artifact_sha256": null,
      "supported_statements": [
        "The paper gives necessary and sufficient conditions for computability of the solution operator of an abstract linear Cauchy problem with a possibly unbounded Banach-space operator in the representation approach."
      ],
      "boundary": "This is TTE computability, not Bishop constructivity or reverse mathematics, and it does not prove finite propagation.",
      "ledger": "foundations/literature-coded-wave-frontier-v2.json",
      "ledger_link": "sources/foundations/literature-coded-wave-frontier-v2.json"
    },
    "zhong-1999-sobolev": {
      "id": "zhong-1999-sobolev",
      "kind": "LITERATURE",
      "citation": "Ning Zhong, Computability structure of the Sobolev spaces and its applications, Theoretical Computer Science 219 (1999), 487-510.",
      "year": null,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.1016/S0304-3975(98)00302-8",
      "artifact_status": "METADATA_ONLY",
      "artifact_sha256": null,
      "supported_statements": [
        "The paper defines computability structures on Sobolev spaces and applies them to classes of second-order hyperbolic and parabolic PDEs."
      ],
      "boundary": "A computable-analysis result is not a Bishop proof, a subsystem reversal, or a causal-support theorem.",
      "ledger": "foundations/literature-coded-wave-frontier-v2.json",
      "ledger_link": "sources/foundations/literature-coded-wave-frontier-v2.json"
    },
    "zhong-weihrauch-2003-distributions": {
      "id": "zhong-weihrauch-2003-distributions",
      "kind": "LITERATURE",
      "citation": "Ning Zhong and Klaus Weihrauch, Computability theory of generalized functions, Journal of the ACM 50 (2003), 469-505.",
      "year": null,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://doi.org/10.1145/792538.792542",
      "artifact_status": "METADATA_ONLY",
      "artifact_sha256": null,
      "supported_statements": [
        "The paper defines TTE computability for test functions and distributions and proves computability of the solution operator for the distributional inhomogeneous three-dimensional wave equation."
      ],
      "boundary": "The reviewed abstract does not certify retarded or advanced selection or a strict cone-support theorem; this is therefore not direct causal-Green evidence.",
      "ledger": "foundations/literature-coded-wave-frontier-v2.json",
      "ledger_link": "sources/foundations/literature-coded-wave-frontier-v2.json"
    },
    "zohar-burrello-2014": {
      "id": "zohar-burrello-2014",
      "kind": "LITERATURE",
      "citation": "Erez Zohar and Michele Burrello, Formulation of lattice gauge theories for quantum simulations, Physical Review D 91, 054506 (2015).",
      "year": 2014,
      "source_kind": "PRIMARY_RESEARCH",
      "stable_url": "https://arxiv.org/abs/1409.3085",
      "artifact_status": "CONTENT_PINNED",
      "artifact_sha256": "ed0cf26004653004d2688ece6bbb3f754accbab1914b4679a5b38326d54f86fe",
      "supported_statements": [
        "Hamiltonian lattice gauge models can encode local gauge invariance and Gauss-law constraints for finite, compact, and truncated gauge groups."
      ],
      "boundary": "A simulator-oriented lattice Hamiltonian is not a finite Weyl-gravity BV complex, a regulator-independent continuum limit, or a QME certificate.",
      "ledger": "foundations/literature-expansion-v2.json",
      "ledger_link": "sources/foundations/literature-expansion-v2.json"
    }
  },
  "ladder": [
    {
      "level": "L0_FINITE_LAURENT",
      "object": "A labelled finite family of rational-complex chiral modes",
      "status": "CERTIFIED",
      "sufficient_base": "PRA for every fixed fixture",
      "adds": [
        "finite sums",
        "integer differentiation weights",
        "decidable rational equality"
      ],
      "establishes": [
        "exact wave-equation residual zero",
        "Galerkin nesting",
        "exact positive finite energy"
      ],
      "does_not_establish": [
        "completion",
        "spatial localization",
        "causal support"
      ]
    },
    {
      "level": "L1_NAMED_TAIL_MODULUS",
      "object": "The explicit datum c_n=1/n^2 together with N(k)=2^k",
      "status": "CERTIFIED",
      "sufficient_base": "Primitive-recursive rational inequalities plus induction for the displayed telescoping bound",
      "adds": [
        "a tolerance-to-cutoff function supplied as data"
      ],
      "establishes": [
        "a constructive Cauchy name for this named energy datum"
      ],
      "does_not_establish": [
        "a uniform modulus extractor for every classically convergent energy series"
      ]
    },
    {
      "level": "L2_CODED_ENERGY_CARRIER",
      "object": "Fast-Cauchy completion of mean-zero rational polygonal chiral pairs",
      "status": "CERTIFIED",
      "sufficient_base": "RCA_0 for the declared representation",
      "source": "FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1",
      "adds": [
        "coded Cauchy completion with prescribed rate",
        "exact rational translation group",
        "finite-code time moduli",
        "primitive-recursive diagonal for named real times"
      ],
      "establishes": [
        "completed energy state",
        "energy-conserving real-time solution name",
        "Cauchy existence and uniqueness in the declared carrier"
      ],
      "does_not_establish": [
        "necessity or reversal",
        "representation invariance",
        "localized weak equation",
        "causal support"
      ]
    },
    {
      "level": "L3_COEFFICIENT_WEAK_SOLUTION",
      "object": "An energy solution tested against finite Fourier sequences",
      "status": "FORMALIZATION_TARGET",
      "adds": [
        "finite-support test-sequence pairing",
        "termwise weak equation"
      ],
      "separation": "This coefficient-weak notion avoids claiming a spacetime distribution or localized support.",
      "open": [
        "coded localized test class",
        "coefficient-to-distribution comparison",
        "weakest base"
      ],
      "source_boundary": "L2 supplies a completed evolution name, but the present certificate does not formalize test-function integration."
    },
    {
      "level": "L4_SPACETIME_DISTRIBUTION",
      "object": "A distribution on R x S^1 tested against localized smooth functions",
      "status": "OPEN",
      "adds": [
        "coded test-function space",
        "integration or Fourier/test-function comparison",
        "continuity in the test-function topology"
      ],
      "boundary": "Neither finite Laurent algebra nor a Hilbert coefficient sequence supplies this automatically."
    },
    {
      "level": "L5_CAUSAL_GREEN_OPERATOR",
      "object": "Advanced and retarded solution maps with finite propagation and uniqueness",
      "status": "CONDITIONAL_IMPORT_ONLY",
      "adds": [
        "localized energy estimates",
        "Cauchy uniqueness",
        "support propagation",
        "slab globalization",
        "distributional duality"
      ],
      "source": "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1",
      "boundary": "The imported biwave result is conditional and its weakest base and Choice strength remain open."
    }
  ],
  "graph": {
    "relation_vocabulary": [
      "SUFFICIENT",
      "CONDITIONAL_SUFFICIENT",
      "REPRESENTATION_DEPENDENT",
      "COUNTEREXAMPLE_TO_METHOD",
      "LITERATURE_CONTRAST",
      "OPEN_IMPLICATION",
      "NOT_SUFFICIENT"
    ],
    "nodes": [
      {
        "id": "P-FINITE-RESOLUTION",
        "kind": "PHYSICAL_ASSUMPTION",
        "statement": "Only finitely many Fourier modes are resolved.",
        "label": "Finite resolution"
      },
      {
        "id": "M-FINITE-LAURENT",
        "kind": "MATHEMATICAL_CONSTRUCTION",
        "statement": "A finite Gaussian-rational Laurent wave is available.",
        "label": "Finite Laurent wave"
      },
      {
        "id": "P-ERROR-CONTROL",
        "kind": "PHYSICAL_ASSUMPTION",
        "statement": "Preparation supplies a cutoff for every requested energy tolerance.",
        "label": "Supplied error control"
      },
      {
        "id": "M-TAIL-MODULUS",
        "kind": "MATHEMATICAL_DATA",
        "statement": "A function N(k) bounds the energy tail by 2^{-k}.",
        "label": "Energy-tail modulus"
      },
      {
        "id": "P-FINITE-ENERGY",
        "kind": "PHYSICAL_ASSUMPTION",
        "statement": "The state has finite total energy, without a supplied modulus.",
        "label": "Finite total energy"
      },
      {
        "id": "M-CODED-HILBERT",
        "kind": "MATHEMATICAL_CONSTRUCTION",
        "statement": "A fast-Cauchy completed chiral energy state and its isometric evolution exist in the declared RCA_0 coding.",
        "label": "Coded Hilbert evolution"
      },
      {
        "id": "M-COEFFICIENT-WEAK",
        "kind": "MATHEMATICAL_CONSTRUCTION",
        "statement": "The wave equation holds against finite Fourier tests.",
        "label": "Finite-test wave identity"
      },
      {
        "id": "M-SPACETIME-DISTRIBUTION",
        "kind": "MATHEMATICAL_CONSTRUCTION",
        "statement": "A localized spacetime distribution is constructed.",
        "label": "Localized spacetime distribution"
      },
      {
        "id": "P-LOCAL-CAUSALITY",
        "kind": "PHYSICAL_ASSUMPTION",
        "statement": "Disturbances have finite propagation speed.",
        "label": "Finite propagation speed"
      },
      {
        "id": "M-CAUSAL-GREEN",
        "kind": "MATHEMATICAL_CONSTRUCTION",
        "statement": "Advanced and retarded Green maps with support control exist.",
        "label": "Causal Green maps"
      },
      {
        "id": "L-WEIHRAUCH-ZHONG",
        "kind": "LITERATURE_RESULT",
        "statement": "Wave propagation is computable on stated C^1 and Sobolev representations.",
        "label": "Computable wave propagation"
      },
      {
        "id": "L-POUR-EL-RICHARDS",
        "kind": "LITERATURE_RESULT",
        "statement": "A different representation/regularity setting admits computable initial data with a noncomputable solution value.",
        "label": "Noncomputable solution value"
      }
    ],
    "edges": [
      {
        "from": "P-FINITE-RESOLUTION",
        "to": "M-FINITE-LAURENT",
        "relation": "SUFFICIENT",
        "evidence": [
          "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
        ],
        "meaning": "Resolving finitely many Fourier modes is enough to construct the exact finite Laurent-wave fixture."
      },
      {
        "from": "P-ERROR-CONTROL",
        "to": "M-TAIL-MODULUS",
        "relation": "REPRESENTATION_DEPENDENT",
        "evidence": [
          "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
        ],
        "meaning": "A usable cutoff rule supplies a tail modulus only because that quantitative rule is part of the chosen representation."
      },
      {
        "from": "M-TAIL-MODULUS",
        "to": "M-CODED-HILBERT",
        "relation": "SUFFICIENT",
        "evidence": [
          "FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1"
        ],
        "meaning": "A prescribed fast Cauchy rate and finite-code time moduli support the explicit diagonal extension in RCA_0."
      },
      {
        "from": "P-FINITE-ENERGY",
        "to": "M-TAIL-MODULUS",
        "relation": "OPEN_IMPLICATION",
        "evidence": [],
        "meaning": "Finite total energy alone does not supply a rate of tail convergence; deriving one uniformly remains an open bridge."
      },
      {
        "from": "M-CODED-HILBERT",
        "to": "M-COEFFICIENT-WEAK",
        "relation": "OPEN_IMPLICATION",
        "evidence": [
          "FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1"
        ],
        "meaning": "The completed evolution name has been constructed, but verifying the wave identity against the declared finite test class remains open."
      },
      {
        "from": "M-COEFFICIENT-WEAK",
        "to": "M-SPACETIME-DISTRIBUTION",
        "relation": "OPEN_IMPLICATION",
        "evidence": [],
        "meaning": "An identity on finite Fourier tests has not yet been extended to a localized spacetime test-function class."
      },
      {
        "from": "M-FINITE-LAURENT",
        "to": "M-CAUSAL-GREEN",
        "relation": "COUNTEREXAMPLE_TO_METHOD",
        "evidence": [
          "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
        ],
        "meaning": "Finite spectral projection is globally nonzero, so this route cannot certify causal support."
      },
      {
        "from": "M-SPACETIME-DISTRIBUTION",
        "to": "M-CAUSAL-GREEN",
        "relation": "NOT_SUFFICIENT",
        "evidence": [
          "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
        ],
        "meaning": "A spacetime distribution alone is not enough: energy uniqueness and support propagation are additional requirements."
      },
      {
        "from": "P-LOCAL-CAUSALITY",
        "to": "M-CAUSAL-GREEN",
        "relation": "OPEN_IMPLICATION",
        "evidence": [
          "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
        ],
        "meaning": "Finite propagation is the physical requirement, but an explicit theorem must still construct advanced and retarded maps with controlled support."
      },
      {
        "from": "L-WEIHRAUCH-ZHONG",
        "to": "L-POUR-EL-RICHARDS",
        "relation": "LITERATURE_CONTRAST",
        "evidence": [
          "weihrauch-zhong-2002",
          "pour-el-richards-1981"
        ],
        "meaning": "Computability changes with topology, regularity, and representation; the two literature results are not contradictory."
      }
    ]
  },
  "boundaries": {
    "cube": [
      "literature completeness",
      "that RCA_0 is necessary or weakest",
      "a WKL_0 or ACA_0 reversal",
      "representation invariance",
      "a spacetime-distribution theorem",
      "causal Green support",
      "coverage for 81 still-unmapped emitted coordinates",
      "coherence of 124 synthetic coordinates",
      "a new Lorentzian Weyl result"
    ],
    "migration_audit": [
      "literature completeness",
      "that a reviewed-no-transfer coordinate has no supporting literature",
      "that every Cartesian coordinate is coherent",
      "a weakest mathematical base",
      "a new physical result",
      "a new Lorentzian-causal result"
    ],
    "ladder": [
      "that RCA_0 is necessary or the weakest base",
      "a WKL_0, ACA_0, or Choice reversal",
      "an upper bound for representations lacking prescribed Cauchy rates",
      "representation invariance",
      "a coefficient-weak or localized spacetime-distribution theorem",
      "finite propagation or causal support from Fourier or polygonal evolution",
      "a normally-hyperbolic Green theorem",
      "the full biwave or metric-BV propagator",
      "renormalized Lorentzian products or a QME theorem",
      "a new LORENTZIAN-CAUSAL result"
    ],
    "navigation": [
      "Coverage status and migration-review status answer different questions.",
      "REVIEWED_NO_TRANSFER and NOT_MAPPED are not literature-absence claims.",
      "The 124 synthetic coordinates have not received the migration review applied to the 452 emitted coordinates.",
      "Neighbor counts and candidate views are navigation aids, not theorem rankings."
    ]
  },
  "source_links": {
    "cube": "sources/foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V4.json",
    "migration_audit": "sources/foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_MIGRATION_AUDIT_V2.json",
    "ladder": "sources/foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V2.json",
    "cube_report": "sources/foundations/reports/refined-intersection-cube-v4.md",
    "migration_audit_report": "sources/foundations/reports/intersection-cube-migration-audit-v2.md",
    "ladder_report": "sources/foundations/reports/cylinder-wave-strength-ladder-v2.md"
  },
  "canonical_digest": "378a9806111aec5b00bb9b9d71e8b9bbeaad573feb163684e967aa8cc34de625"
};
