window.MATRIX_EXPLORER_DATA = {
  "schema_version": "foundational-matrix-explorer-data-v1",
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
          ]
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
          ]
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
          ]
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
          ]
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
          ]
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
          "warning": "A finite regulator, finite carrier, and foundational rejection of actual infinity are distinct and must not be conflated."
        }
      ]
    },
    {
      "id": "CARRIER",
      "question": "What mathematical object carries states, observables, fields, and evolution?",
      "keys": [
        {
          "id": "FINITE_EXACT",
          "label": "Finite exact algebra",
          "meaning": "Finite matrices, rational/integer complexes, or explicitly finite-dimensional algebraic data."
        },
        {
          "id": "HILBERT_OPERATOR",
          "label": "Hilbert/operator",
          "meaning": "Positive Hilbert spaces, operator domains, spectral data, and their completions."
        },
        {
          "id": "KREIN_INDEFINITE",
          "label": "Krein/indefinite",
          "meaning": "Indefinite inner products, fundamental symmetries, and positive companion topologies."
        },
        {
          "id": "ALGEBRAIC_CSTAR",
          "label": "Algebraic C*-system",
          "meaning": "Observable algebras, states, GNS representations, nets, and algebra-first formulations."
        },
        {
          "id": "SMOOTH_DISTRIBUTIONAL",
          "label": "Smooth/PDE/distributional",
          "meaning": "Manifolds, bundles, sections, Sobolev or distribution spaces, differential operators, and Green theory."
        },
        {
          "id": "LOCALIC_SYNTHETIC",
          "label": "Localic/synthetic/internal",
          "meaning": "Locales, internal algebra objects, formal manifolds, and synthetic smooth structures."
        }
      ]
    },
    {
      "id": "REFINED_OBLIGATION",
      "question": "Which precise physical or theorem-level job is established?",
      "keys": [
        {
          "id": "KINEMATICS_OBSERVABLES",
          "label": "Kinematics/observables",
          "meaning": "Define degrees of freedom, observables, commutation structure, and configurations."
        },
        {
          "id": "STATE_EXISTENCE",
          "label": "State existence",
          "meaning": "Construct at least one normalized or algebraically valid state in the declared carrier."
        },
        {
          "id": "STATE_REPRESENTATION",
          "label": "State representation",
          "meaning": "Relate states to vectors, density operators, measures, valuations, or GNS data."
        },
        {
          "id": "PROBABILITY_RULE",
          "label": "Probability rule",
          "meaning": "Construct or derive normalized event probabilities or a Born-type rule."
        },
        {
          "id": "PHYSICAL_STATE_SELECTION",
          "label": "Physical state selection",
          "meaning": "Select or obstruct a physically distinguished vacuum, thermal, Hadamard, or other state."
        },
        {
          "id": "GENERATOR_SPECTRAL_DYNAMICS",
          "label": "Generator/spectral dynamics",
          "meaning": "Construct generators, spectra, one-parameter groups, or algebra automorphisms."
        },
        {
          "id": "EVOLUTION_WELLPOSEDNESS",
          "label": "Evolution/well-posedness",
          "meaning": "Prove existence, uniqueness, stability, or computability of evolution in a stated topology."
        },
        {
          "id": "CAUSAL_PROPAGATION_GREEN",
          "label": "Causal propagation/Green",
          "meaning": "Construct advanced/retarded maps and prove finite propagation or causal support."
        },
        {
          "id": "GAUGE_BV_COHOMOLOGY",
          "label": "Gauge/BV/cohomology",
          "meaning": "Handle gauge symmetry, BRST/BV complexes, residual cohomology, and gauge independence."
        },
        {
          "id": "INTERACTION_CONSTRUCTION",
          "label": "Interaction construction",
          "meaning": "Construct a nontrivial interaction, deformation, or interacting product."
        },
        {
          "id": "COUNTERTERM_CLASSIFICATION",
          "label": "Counterterm classification",
          "meaning": "Classify allowed local counterterms before computing coefficients."
        },
        {
          "id": "ANOMALY_CLASSIFICATION",
          "label": "Anomaly classification",
          "meaning": "Classify possible local anomalies and consistency conditions."
        },
        {
          "id": "RENORMALIZED_PRODUCTS",
          "label": "Renormalized products",
          "meaning": "Construct renormalized time-ordered or interacting products."
        },
        {
          "id": "QME_RESTORATION",
          "label": "QME restoration",
          "meaning": "Compute or cancel the breaking and restore the local quantum master equation."
        },
        {
          "id": "RESIDUAL_QUANTUM_TRANSFER",
          "label": "Residual quantum transfer",
          "meaning": "Transfer a restored quantum correction to the residual complex."
        },
        {
          "id": "RECONSTRUCTION_LIMITS",
          "label": "Reconstruction/limits",
          "meaning": "Prove operational reconstruction, comparison, continuum-limit, or empirical-equivalence results."
        }
      ]
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
      "meaning": "A one-to-one migrated obligation retains a deliberately reviewed gap."
    },
    {
      "id": "MIGRATION_UNRESOLVED",
      "meaning": "The overloaded v0 parent was assessed, but its evidence cannot be transferred to this child without a new review."
    },
    {
      "id": "NOT_MAPPED",
      "meaning": "This coordinate has not been assessed; no absence or incoherence is inferred."
    }
  ],
  "counts": {
    "cartesian_total": 576,
    "emitted": 452,
    "qualified": 340,
    "migration_unresolved": 112,
    "not_mapped": 124,
    "status_counts": {
      "LITERATURE_RESULT": 90,
      "LOCAL_RESULT": 85,
      "MIGRATION_UNRESOLVED": 112,
      "NOT_MAPPED": 124,
      "PIECES_ONLY": 158,
      "PRIORITY_GAP": 7
    },
    "evidence_records": 51
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
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "STATE_EXISTENCE",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "grinkevich-1996",
        "barnich-brandt-henneaux-2000"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'State existence': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a physically selected Weyl state and probability interpretation.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "STATE_EXISTENCE",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009",
        "dittrich-2012"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'State existence': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a physically selected Weyl state and probability interpretation.",
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
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "STATE_REPRESENTATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'State representation': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: a physically selected Weyl state and probability interpretation.",
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
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "STATE_REPRESENTATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "grinkevich-1996",
        "barnich-brandt-henneaux-2000"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'State representation': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a physically selected Weyl state and probability interpretation.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "STATE_REPRESENTATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009",
        "dittrich-2012"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'State representation': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a physically selected Weyl state and probability interpretation.",
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
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PROBABILITY_RULE",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "barnich-brandt-henneaux-2000",
        "brunetti-fredenhagen-verch-2001",
        "fredenhagen-rejzner-2011",
        "brunetti-fredenhagen-rejzner-2013"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Probability rule': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a physically selected Weyl state and probability interpretation.",
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
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "PROBABILITY_RULE",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Probability rule': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: a physically selected Weyl state and probability interpretation.",
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
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PROBABILITY_RULE",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "grinkevich-1996",
        "barnich-brandt-henneaux-2000"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Probability rule': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a physically selected Weyl state and probability interpretation.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PROBABILITY_RULE",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009",
        "dittrich-2012"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Probability rule': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a physically selected Weyl state and probability interpretation.",
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
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "grinkevich-1996",
        "barnich-brandt-henneaux-2000"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Physical state selection': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a physically selected Weyl state and probability interpretation.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "PHYSICAL_STATE_SELECTION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "kogut-susskind-1975",
        "zohar-burrello-2014",
        "bahr-dittrich-2009",
        "dittrich-2012"
      ],
      "parent_obligation": "STATES_PROBABILITY",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Physical state selection': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Local/formal PDE data do not imply global existence, support, or microlocal renormalization. Still open here: a physically selected Weyl state and probability interpretation.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "brown-simpson-1986",
        "humphreys-simpson-1999",
        "humphreys-simpson-1996",
        "brattka-2008"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Generator/spectral dynamics': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: full interacting Lorentzian-causal propagation.",
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
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Generator/spectral dynamics': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Classical rigorous PDE is not automatically constructive PDE.",
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
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "GENERATOR_SPECTRAL_DYNAMICS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "grinkevich-1996"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Generator/spectral dynamics': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No distributional causal QFT or Green-operator theorem is supplied.",
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
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The exact checker proves no PDE existence and no full BV propagator.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "brown-simpson-1986",
        "humphreys-simpson-1999",
        "humphreys-simpson-1996",
        "brattka-2008"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Evolution/well-posedness': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: full interacting Lorentzian-causal propagation.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1",
        "weihrauch-zhong-2002"
      ],
      "summary": "An exact finite-to-coded ladder and computable Sobolev wave result identify a specific RCA_0 formalization target.",
      "boundary": "No second-order-arithmetic upper bound or reversal has been proved.",
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "REVIEWED_V1_OVERLAY",
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
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "pour-el-richards-1981",
        "neumann-pape-streicher-2018"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Evolution/well-posedness': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: full interacting Lorentzian-causal propagation.",
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
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "LITERATURE_RESULT",
      "evidence": [
        "weihrauch-zhong-2002",
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
      ],
      "summary": "Wave propagation is computable in the stated C1 and Sobolev representations reviewed by the ladder.",
      "boundary": "TTE computability is representation-sensitive and is not a Bishop-constructive or reverse-mathematical theorem.",
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "REVIEWED_V1_OVERLAY",
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
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "grinkevich-1996"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Evolution/well-posedness': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No distributional causal QFT or Green-operator theorem is supplied.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "EVOLUTION_WELLPOSEDNESS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Evolution/well-posedness': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: full interacting Lorentzian-causal propagation.",
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
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Causal propagation/Green': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No general spectral measure, determinant, or interacting dynamics.",
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
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "LOCAL_RESULT",
      "evidence": [
        "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The exact checker proves no PDE existence and no full BV propagator.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Causal propagation/Green': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: full interacting Lorentzian-causal propagation.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "brown-simpson-1986",
        "humphreys-simpson-1999",
        "humphreys-simpson-1996",
        "brattka-2008"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Causal propagation/Green': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No reverse implication over a fixed weak base is inferred unless the cited source states one. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: full interacting Lorentzian-causal propagation.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Causal propagation/Green': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. General spectral measures and interacting dynamics remain open.",
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
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Causal propagation/Green': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: full interacting Lorentzian-causal propagation.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "coquand-spitters-2009",
        "henry-2014",
        "neumann-pape-streicher-2018"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Causal propagation/Green': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. An algebraic architecture does not by itself select representations or physical states. Still open here: full interacting Lorentzian-causal propagation.",
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
        "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
      ],
      "summary": "Positive and negative computability results expose the representation and localization dependencies of wave propagation.",
      "boundary": "Neither source constructs a constructive causal Green operator for Weyl gravity.",
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "REVIEWED_V1_OVERLAY",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Causal propagation/Green': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: full interacting Lorentzian-causal propagation.",
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
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Causal propagation/Green': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: full interacting Lorentzian-causal propagation.",
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
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Causal propagation/Green': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. An algebraic architecture does not by itself select representations or physical states. Still open here: full interacting Lorentzian-causal propagation.",
      "emitted": true
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "grinkevich-1996"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Causal propagation/Green': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No distributional causal QFT or Green-operator theorem is supplied.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No finite-field dynamics, continuum convergence, regulator independence, causal propagation, or reconstruction theorem is proved.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Causal propagation/Green': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: full interacting Lorentzian-causal propagation.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "PIECES_ONLY",
      "evidence": [
        "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1",
        "zohar-burrello-2014"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "CAPABILITY_QUALIFIED",
      "summary": "Refined child 'Causal propagation/Green': registered evidence supports this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. An algebraic architecture does not by itself select representations or physical states. Still open here: full interacting Lorentzian-causal propagation.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "CAUSAL_PROPAGATION_GREEN",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "DYNAMICS_PROPAGATION",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Causal propagation/Green': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: full interacting Lorentzian-causal propagation.",
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
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "neumann-pape-streicher-2018",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Interaction construction': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Interaction construction': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Interaction construction': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Interaction construction': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is likely a high-cost programme.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Interaction construction': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Interaction construction': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Interaction construction': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No Lorentzian quantum conclusion.",
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
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "neumann-pape-streicher-2018",
        "pour-el-richards-1981",
        "bridges-svozil-2000",
        "richman-bridges-1999"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Interaction construction': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Interaction construction': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is a missing programme, not a no-go theorem.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Interaction construction': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Interaction construction': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Interaction construction': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "INTERACTION_CONSTRUCTION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Interaction construction': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "neumann-pape-streicher-2018",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Counterterm classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Counterterm classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Counterterm classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Counterterm classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is likely a high-cost programme.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Counterterm classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Counterterm classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Counterterm classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No Lorentzian quantum conclusion.",
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
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "neumann-pape-streicher-2018",
        "pour-el-richards-1981",
        "bridges-svozil-2000",
        "richman-bridges-1999"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Counterterm classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Counterterm classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is a missing programme, not a no-go theorem.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Counterterm classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Counterterm classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Counterterm classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite algebra does not remove renormalization obligations.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Counterterm classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "COUNTERTERM_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Counterterm classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "neumann-pape-streicher-2018",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Anomaly classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Anomaly classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Anomaly classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Anomaly classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is likely a high-cost programme.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Anomaly classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Anomaly classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Anomaly classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No Lorentzian quantum conclusion.",
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
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "neumann-pape-streicher-2018",
        "pour-el-richards-1981",
        "bridges-svozil-2000",
        "richman-bridges-1999"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Anomaly classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Anomaly classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is a missing programme, not a no-go theorem.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Anomaly classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Anomaly classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Anomaly classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite algebra does not remove renormalization obligations.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Anomaly classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "ANOMALY_CLASSIFICATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Anomaly classification': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "neumann-pape-streicher-2018",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Renormalized products': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Renormalized products': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Renormalized products': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Renormalized products': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is likely a high-cost programme.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Renormalized products': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Renormalized products': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Renormalized products': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No Lorentzian quantum conclusion.",
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
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "neumann-pape-streicher-2018",
        "pour-el-richards-1981",
        "bridges-svozil-2000",
        "richman-bridges-1999"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Renormalized products': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Renormalized products': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is a missing programme, not a no-go theorem.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Renormalized products': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Renormalized products': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Renormalized products': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite algebra does not remove renormalization obligations.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Renormalized products': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RENORMALIZED_PRODUCTS",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Renormalized products': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "QME_RESTORATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "neumann-pape-streicher-2018",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'QME restoration': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "QME_RESTORATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'QME restoration': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "QME_RESTORATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'QME restoration': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "QME_RESTORATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'QME restoration': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is likely a high-cost programme.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "QME_RESTORATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'QME restoration': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "QME_RESTORATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'QME restoration': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "QME_RESTORATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'QME restoration': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No Lorentzian quantum conclusion.",
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
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "QME_RESTORATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "neumann-pape-streicher-2018",
        "pour-el-richards-1981",
        "bridges-svozil-2000",
        "richman-bridges-1999"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'QME restoration': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "QME_RESTORATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'QME restoration': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is a missing programme, not a no-go theorem.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "QME_RESTORATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'QME restoration': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "QME_RESTORATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'QME restoration': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "QME_RESTORATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'QME restoration': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite algebra does not remove renormalization obligations.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "QME_RESTORATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'QME restoration': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "QME_RESTORATION",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'QME restoration': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "neumann-pape-streicher-2018",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Residual quantum transfer': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "bender-boettcher-1998",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Residual quantum transfer': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "CLASSICAL_STANDARD",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Residual quantum transfer': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. The source works in ordinary classical mathematics and is not a foundational-strength audit. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "WEAK_ARITHMETIC",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Residual quantum transfer': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is likely a high-cost programme.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "blackadar-farah-karagila-2026",
        "blackadar-farah-2026",
        "neumann-pape-streicher-2018"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Residual quantum transfer': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "KREIN_INDEFINITE",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1",
        "mostafazadeh-2001",
        "gottschalk-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Residual quantum transfer': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. An explicit finite or separable construction avoids a choice step only in its stated scope; arbitrary-family existence is not inferred. Real spectrum or J-unitarity alone does not produce a positive physical state space. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "WEAK_CHOICE_ZF",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Residual quantum transfer': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. No Lorentzian quantum conclusion.",
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
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "neumann-pape-streicher-2018",
        "pour-el-richards-1981",
        "bridges-svozil-2000",
        "richman-bridges-1999"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Residual quantum transfer': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "SMOOTH_DISTRIBUTIONAL",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Residual quantum transfer': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. This is a missing programme, not a no-go theorem.",
      "emitted": true
    },
    {
      "foundation": "CONSTRUCTIVE_COMPUTABLE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "coquand-spitters-2009",
        "heunen-landsman-spitters-2009",
        "brenna-flori-2012"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Residual quantum transfer': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Computable, Bishop-constructive, intuitionistic, and reverse-mathematical results remain distinct types. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "summary": "This Cartesian coordinate has not yet been assessed in the refined evidence projection.",
      "boundary": "NOT_MAPPED is not a literature-absence claim, a no-go theorem, or evidence that the coordinate is coherent.",
      "emitted": false
    },
    {
      "foundation": "TOPOS_INTERNAL",
      "carrier": "ALGEBRAIC_CSTAR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "heunen-landsman-spitters-2009",
        "doring-2008",
        "brenna-flori-2012",
        "harding-heunen-2019"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Residual quantum transfer': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. External Hilbert/C*-input and internal topos objects are not silently identified, and the ambient topos matters. An algebraic architecture does not by itself select representations or physical states. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "FINITE_EXACT",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Residual quantum transfer': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite algebra does not remove renormalization obligations.",
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "HILBERT_OPERATOR",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "gibbons-hoffman-wootters-2004",
        "abramsky-coecke-2004",
        "constantin-doring-2020"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Residual quantum transfer': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Domain, completion, and spectral-measure hypotheses remain part of the result. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "emitted": true
    },
    {
      "foundation": "FINITE_DISCRETE",
      "carrier": "LOCALIC_SYNTHETIC",
      "obligation": "RESIDUAL_QUANTUM_TRANSFER",
      "status": "MIGRATION_UNRESOLVED",
      "evidence": [
        "harding-heunen-2019",
        "constantin-doring-2020",
        "abramsky-coecke-2004"
      ],
      "parent_obligation": "INTERACTION_RENORMALIZATION_QME",
      "migration_relation": "NO_REGISTERED_DESCENT",
      "summary": "Refined child 'Residual quantum transfer': the overloaded parent evidence has no registered transfer to this child.",
      "boundary": "The v0 parent status is not inherited by sibling obligations. Finite dimension, lattice regularization, finite field, and finitism remain distinct; a continuum bridge is never automatic. Internal/localic reformulation does not by itself establish external empirical equivalence. Still open here: Weyl counterterm coefficients, QME restoration, and residual transfer.",
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
      "object": "Countable Fourier coefficients with an explicit energy-tail modulus",
      "status": "FORMALIZATION_TARGET",
      "candidate_upper_bound": "RCA_0 sufficiency is plausible for the chosen coded representation but is not proved here",
      "adds": [
        "coded Cauchy completion",
        "coordinatewise phase evolution",
        "uniform tail control"
      ],
      "establishes_if_formalized": [
        "completed energy state",
        "norm-conserving coordinate propagator"
      ],
      "open": [
        "exact subsystem proof",
        "representation invariance",
        "necessity or reversal"
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
        "comparison with standard distributional solutions",
        "weakest base"
      ]
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
        "statement": "Only finitely many Fourier modes are resolved."
      },
      {
        "id": "M-FINITE-LAURENT",
        "kind": "MATHEMATICAL_CONSTRUCTION",
        "statement": "A finite Gaussian-rational Laurent wave is available."
      },
      {
        "id": "P-ERROR-CONTROL",
        "kind": "PHYSICAL_ASSUMPTION",
        "statement": "Preparation supplies a cutoff for every requested energy tolerance."
      },
      {
        "id": "M-TAIL-MODULUS",
        "kind": "MATHEMATICAL_DATA",
        "statement": "A function N(k) bounds the energy tail by 2^{-k}."
      },
      {
        "id": "P-FINITE-ENERGY",
        "kind": "PHYSICAL_ASSUMPTION",
        "statement": "The state has finite total energy, without a supplied modulus."
      },
      {
        "id": "M-CODED-HILBERT",
        "kind": "MATHEMATICAL_CONSTRUCTION",
        "statement": "A coded completed energy-space element exists."
      },
      {
        "id": "M-COEFFICIENT-WEAK",
        "kind": "MATHEMATICAL_CONSTRUCTION",
        "statement": "The wave equation holds against finite Fourier tests."
      },
      {
        "id": "M-SPACETIME-DISTRIBUTION",
        "kind": "MATHEMATICAL_CONSTRUCTION",
        "statement": "A localized spacetime distribution is constructed."
      },
      {
        "id": "P-LOCAL-CAUSALITY",
        "kind": "PHYSICAL_ASSUMPTION",
        "statement": "Disturbances have finite propagation speed."
      },
      {
        "id": "M-CAUSAL-GREEN",
        "kind": "MATHEMATICAL_CONSTRUCTION",
        "statement": "Advanced and retarded Green maps with support control exist."
      },
      {
        "id": "L-WEIHRAUCH-ZHONG",
        "kind": "LITERATURE_RESULT",
        "statement": "Wave propagation is computable on stated C^1 and Sobolev representations."
      },
      {
        "id": "L-POUR-EL-RICHARDS",
        "kind": "LITERATURE_RESULT",
        "statement": "A different representation/regularity setting admits computable initial data with a noncomputable solution value."
      }
    ],
    "edges": [
      {
        "from": "P-FINITE-RESOLUTION",
        "to": "M-FINITE-LAURENT",
        "relation": "SUFFICIENT",
        "evidence": [
          "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
        ]
      },
      {
        "from": "P-ERROR-CONTROL",
        "to": "M-TAIL-MODULUS",
        "relation": "REPRESENTATION_DEPENDENT",
        "evidence": [
          "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
        ]
      },
      {
        "from": "M-TAIL-MODULUS",
        "to": "M-CODED-HILBERT",
        "relation": "CONDITIONAL_SUFFICIENT",
        "evidence": [
          "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
        ]
      },
      {
        "from": "P-FINITE-ENERGY",
        "to": "M-TAIL-MODULUS",
        "relation": "OPEN_IMPLICATION",
        "evidence": []
      },
      {
        "from": "M-CODED-HILBERT",
        "to": "M-COEFFICIENT-WEAK",
        "relation": "OPEN_IMPLICATION",
        "evidence": [
          "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1"
        ]
      },
      {
        "from": "M-COEFFICIENT-WEAK",
        "to": "M-SPACETIME-DISTRIBUTION",
        "relation": "OPEN_IMPLICATION",
        "evidence": []
      },
      {
        "from": "M-FINITE-LAURENT",
        "to": "M-CAUSAL-GREEN",
        "relation": "COUNTEREXAMPLE_TO_METHOD",
        "evidence": [
          "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"
        ],
        "meaning": "Finite spectral projection is globally nonzero and cannot certify support."
      },
      {
        "from": "M-SPACETIME-DISTRIBUTION",
        "to": "M-CAUSAL-GREEN",
        "relation": "NOT_SUFFICIENT",
        "evidence": [
          "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
        ],
        "meaning": "Energy uniqueness and support propagation are additional requirements."
      },
      {
        "from": "P-LOCAL-CAUSALITY",
        "to": "M-CAUSAL-GREEN",
        "relation": "OPEN_IMPLICATION",
        "evidence": [
          "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"
        ]
      },
      {
        "from": "L-WEIHRAUCH-ZHONG",
        "to": "L-POUR-EL-RICHARDS",
        "relation": "LITERATURE_CONTRAST",
        "evidence": [
          "weihrauch-zhong-2002",
          "pour-el-richards-1981"
        ],
        "meaning": "Computability changes with topology, regularity, and representation; the results are not contradictory."
      }
    ]
  },
  "boundaries": {
    "cube": [
      "that every refined Cartesian coordinate is coherent",
      "that a v0 result supports every refined child",
      "literature completeness",
      "a weakest mathematical base",
      "a constructive continuum Weyl theory",
      "renormalized products",
      "QME restoration",
      "residual quantum transfer",
      "a controlled continuum limit",
      "a new Lorentzian-causal result"
    ],
    "ladder": [
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
    "navigation": [
      "Colors classify evidence state, not truth or scientific importance.",
      "NOT_MAPPED and MIGRATION_UNRESOLVED are not literature-absence claims.",
      "Neighbor counts and candidate views are navigation aids, not theorem rankings."
    ]
  },
  "source_links": {
    "cube": "sources/foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V1.json",
    "ladder": "sources/foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1.json",
    "cube_report": "sources/foundations/reports/refined-intersection-cube.md",
    "ladder_report": "sources/foundations/reports/cylinder-wave-strength-ladder.md"
  },
  "canonical_digest": "ce3d52110583af9c85eece5024656d5bae9541386f7a43dba1c756e3ddbc1c6f"
};
