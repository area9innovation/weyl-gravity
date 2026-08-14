#!/usr/bin/env python3
"""Build fail-closed candidate assemblies over the foundations atlas.

An assembly is a navigational hypothesis: it chooses one recorded cell for
each physical obligation from a declared admissible region.  Selection does
not certify that the chosen results concern the same model or compose.  Those
claims require separately registered interfaces and empirical comparisons.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GR_CONTROL = ROOT / "foundations/standard-gr-observational-control-v1.json"
GR_CASSINI_ASSEMBLY = ROOT / "foundations/results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json"
MANNHEIM_NGC3198_ASSEMBLY = ROOT / "foundations/results/FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1.json"
NGC3198_COMMON_FIT_COMPARISON = ROOT / "foundations/results/FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1.json"


DIRECT = {"LOCAL_RESULT", "LITERATURE_RESULT"}
STATUS_RANK = {
    "NOT_MAPPED": 0,
    "REVIEWED_GAP": 1,
    "PRIORITY_GAP": 1,
    "PIECES_ONLY": 2,
    "LITERATURE_RESULT": 3,
    "LOCAL_RESULT": 3,
}

INTERFACE_VOCABULARY = [
    {"id": "IDENTICAL_OBJECT", "meaning": "Both cells have been shown to use the same mathematical object with the same scope."},
    {"id": "EXACT_TRANSLATION", "meaning": "A proved, reversible translation connects the objects used by the two cells."},
    {"id": "CONDITIONAL_BRIDGE", "meaning": "A proved bridge exists once explicitly named extra assumptions are supplied."},
    {"id": "APPROXIMATION_WITH_BOUND", "meaning": "A quantitative approximation theorem connects the cells with an explicit error bound."},
    {"id": "CONJECTURAL_INTERFACE", "meaning": "A concrete bridge has been proposed but is not certified."},
    {"id": "INCOMPATIBLE", "meaning": "A scoped obstruction proves that these particular objects cannot be joined as proposed."},
    {"id": "NOT_ASSESSED", "meaning": "No registered record currently decides how the two selected cells compose."},
]

INTERFACE_TEMPLATES = [
    ("STATE_TO_PROBABILITY", "State encoding → probability rule", ["STATE_REPRESENTATION"], ["PROBABILITY_RULE"]),
    ("SELECTION_TO_DYNAMICS", "Physical state selection → dynamics", ["PHYSICAL_STATE_SELECTION"], ["GENERATOR_SPECTRAL_DYNAMICS"]),
    ("DYNAMICS_TO_CAUSALITY", "Evolution → causal response", ["GENERATOR_SPECTRAL_DYNAMICS", "EVOLUTION_WELLPOSEDNESS"], ["CAUSAL_PROPAGATION_GREEN"]),
    ("GAUGE_TO_INTERACTION", "Gauge content → interaction", ["KINEMATICS_OBSERVABLES", "GAUGE_BV_COHOMOLOGY"], ["INTERACTION_CONSTRUCTION"]),
    ("RENORMALIZATION_TO_QME", "Classifications and products → restored QME", ["COUNTERTERM_CLASSIFICATION", "ANOMALY_CLASSIFICATION", "RENORMALIZED_PRODUCTS"], ["QME_RESTORATION"]),
    ("QME_TO_RESIDUAL", "Restored QME → residual correction", ["QME_RESTORATION"], ["RESIDUAL_QUANTUM_TRANSFER"]),
    ("PREDICTION_TO_RECONSTRUCTION", "Prediction chain → standard or operational interpretation", ["PROBABILITY_RULE", "CAUSAL_PROPAGATION_GREEN", "INTERACTION_CONSTRUCTION"], ["RECONSTRUCTION_LIMITS"]),
]

BENCHMARKS = [
    {"id": "LOCAL_GRAVITY", "label": "Local gravity and equivalence tests", "question": "Which operational observables reproduce the measured weak-field and equivalence-principle limits?"},
    {"id": "SOLAR_SYSTEM", "label": "Solar-system dynamics", "question": "What parameterized predictions are compared with orbital, ranging, and time-delay data?"},
    {"id": "COMPACT_BINARIES", "label": "Compact binaries", "question": "What conservative and radiative predictions are compared with binary-pulsar or inspiral observations?"},
    {"id": "GRAVITATIONAL_WAVES", "label": "Gravitational waves", "question": "What propagation, speed, damping, and polarization observables are identified and tested?"},
    {"id": "GALACTIC_LENSING_DYNAMICS", "label": "Galactic dynamics and lensing", "question": "Can one parameter choice account for both motion and light propagation on galactic scales?"},
    {"id": "COSMOLOGY", "label": "Cosmology and structure", "question": "What background and perturbation predictions are compared with expansion and structure data?"},
]

ASSEMBLY_CONFIGS = [
    {
        "id": "STANDARD_MIXED_REFERENCE",
        "label": "Mainstream GR and quantum-field-theory reference",
        "short_label": "Mainstream GR / QFT",
        "camp_kind": "REFERENCE_TRADITION",
        "camp_summary": "The conventional reference combines classical spacetime geometry, standard quantum mechanics, continuum field theory, and the ordinary mathematical toolkit used across modern physics.",
        "central_question": "How much of a complete predictive theory is already covered by the mainstream GR/QFT toolkit, and which joins are still merely assumed?",
        "lineage": ["Einstein–Hilbert gravity", "standard quantum mechanics", "perturbative and curved-spacetime QFT"],
        "signature_ideas": ["classical spacetime geometry", "positive Hilbert-space quantum theory", "continuum fields and local operators"],
        "atlas_window": "A deliberately broad reference envelope that may select a different carrier for each physical job.",
        "scope_note": "This is a calibration baseline, not one historical school, one model, or proof that the selected mainstream ingredients compose.",
        "aim": "Use mainstream mathematical practice as a generous reference, while exposing every unregistered composition step.",
        "foundations": ["CLASSICAL_STANDARD"],
        "carriers": ["FINITE_EXACT", "HILBERT_OPERATOR", "KREIN_INDEFINITE", "ALGEBRAIC_CSTAR", "SMOOTH_DISTRIBUTIONAL", "LOCALIC_SYNTHETIC"],
    },
    {
        "id": "STANDARD_ALGEBRAIC_PROFILE",
        "label": "Algebraic QFT and local-covariance tradition",
        "short_label": "Algebraic QFT",
        "camp_kind": "RESEARCH_TRADITION",
        "camp_summary": "Algebraic quantum field theory starts from observable algebras and their states, emphasizing locality, representation independence, and structural relations between spacetime regions.",
        "central_question": "Can a theory be built from observables, states, and locality before choosing a preferred particle or wavefunction representation?",
        "lineage": ["Haag–Kastler algebraic QFT", "locally covariant QFT", "operator-algebraic quantum theory"],
        "signature_ideas": ["observables before wavefunctions", "local nets of algebras", "states as positive expectation-value rules"],
        "atlas_window": "The classical-standard algebraic C*-carrier column only.",
        "scope_note": "A C*-algebra coverage profile does not by itself supply curved-spacetime dynamics, renormalized interactions, or a preferred physical state.",
        "aim": "Show what the present algebra-first evidence covers without silently importing Hilbert, PDE, or particle assumptions.",
        "foundations": ["CLASSICAL_STANDARD"],
        "carriers": ["ALGEBRAIC_CSTAR"],
    },
    {
        "id": "FINITE_EXACT_PROGRAMME",
        "label": "Finite, discrete, and exactly checkable models",
        "short_label": "Finite / discrete",
        "camp_kind": "METHODOLOGICAL_TRADITION",
        "camp_summary": "Finite and discrete programmes replace a continuum or infinite construction by exact matrices, graphs, modes, or algebraic data that can be exhaustively checked.",
        "central_question": "Which parts of physics are genuinely finite and algebraic, and which require a controlled passage back to a continuum?",
        "lineage": ["lattice and finite-mode models", "finite quantum systems", "exact computer-assisted mathematics"],
        "signature_ideas": ["finite carriers", "exact arithmetic", "explicit refinement or continuum-limit obligations"],
        "atlas_window": "The finite/discrete regime with the finite exact-algebra carrier.",
        "scope_note": "A finite regulator, a finite physical ontology, and a rejection of actual infinity are three different claims; this lens does not identify them.",
        "aim": "Separate exactly checkable finite physics from the additional estimates and limit theorems needed for continuum claims.",
        "foundations": ["FINITE_DISCRETE"],
        "carriers": ["FINITE_EXACT"],
    },
    {
        "id": "BT_EUCLIDEAN_LATTICE_PROGRAMME",
        "label": "Bateman–Turok hidden-ghost-parity programme",
        "short_label": "Bateman–Turok",
        "camp_kind": "NAMED_RESEARCH_PROGRAMME",
        "camp_summary": "Bateman and Turok seek a higher-derivative quantum theory whose hidden ghost-parity structure yields positive physical probabilities without simply discarding the ghost sector.",
        "central_question": "Can hidden ghost parity and a generalized Born construction make a higher-derivative interacting theory probabilistically consistent?",
        "lineage": ["Sam Bateman", "Neil Turok", "hidden ghost parity and perfect-square scalar models"],
        "signature_ideas": ["one-sided ghost charge", "generalized Born probabilities", "positive Euclidean finite-volume control"],
        "atlas_window": "The currently imported window is the positive finite Euclidean lattice and its coarse two-algorithm reproduction, not the full Lorentzian/Krein scattering proposal.",
        "scope_note": "This profile neither proves the all-order Bateman–Turok construction nor treats a Euclidean Gibbs measure as identical to the proposed Lorentzian Krein carrier.",
        "aim": "Make the certified positive Euclidean slice visible inside the broader Bateman–Turok programme while keeping its unbuilt Lorentzian and continuum bridges explicit.",
        "foundations": ["FINITE_DISCRETE"],
        "carriers": ["SMOOTH_DISTRIBUTIONAL"],
    },
    {
        "id": "WEAK_BASE_FINITE_EXACT",
        "label": "Reverse mathematics and weak-foundation programme",
        "short_label": "Reverse mathematics",
        "camp_kind": "METHODOLOGICAL_TRADITION",
        "camp_summary": "Reverse mathematics and Choice audits ask which axioms are actually needed for a theorem, rather than accepting the usual background foundation as an invisible package.",
        "central_question": "What is the weakest explicit logical or set-existence base that still proves each physical construction?",
        "lineage": ["proof theory", "reverse mathematics", "ZF without full Choice"],
        "signature_ideas": ["calibrate theorem strength", "separate sufficiency from necessity", "track representation dependence"],
        "atlas_window": "Finite exact carriers over weak arithmetic and ZF with weakened Choice.",
        "scope_note": "Combining two weak bases in one navigation lens does not identify them or prove a weakest-foundation theorem.",
        "aim": "Expose arithmetic and Choice dependencies of exact constructions without collapsing distinct foundational systems.",
        "foundations": ["WEAK_ARITHMETIC", "WEAK_CHOICE_ZF"],
        "carriers": ["FINITE_EXACT"],
    },
    {
        "id": "KREIN_ALGEBRAIC_PROGRAMME",
        "label": "Mannheim conformal-gravity programme",
        "short_label": "Mannheim conformal gravity",
        "camp_kind": "NAMED_RESEARCH_PROGRAMME",
        "camp_summary": "The Mannheim programme combines fourth-order conformal gravity, Mannheim–Kazanas phenomenology, and a Bender–Mannheim PT/quasi-Hermitian response to the ghost and unitarity problem.",
        "central_question": "Can conformal gravity provide a viable classical phenomenology and a positive quantum interpretation once the inner product is chosen dynamically?",
        "lineage": ["Philip Mannheim", "Mannheim–Kazanas phenomenology", "Bender–Mannheim PT-symmetric quantization"],
        "signature_ideas": ["Weyl-invariant fourth-order gravity", "PT/quasi-Hermitian positive metric", "galactic and cosmological phenomenology"],
        "atlas_window": "Comparison-relevant Hilbert/operator, Krein/indefinite, and smooth continuum cells under classical mathematics.",
        "scope_note": "A generic Krein fundamental symmetry is not Mannheim's field-theoretic C operator, and this mixed-carrier lens does not certify his unitarity or phenomenological claims.",
        "aim": "Display where the atlas can engage Mannheim's classical and quantum questions without identifying adjacent indefinite-space results with the programme's missing positive metric.",
        "foundations": ["CLASSICAL_STANDARD"],
        "carriers": ["HILBERT_OPERATOR", "KREIN_INDEFINITE", "SMOOTH_DISTRIBUTIONAL"],
    },
    {
        "id": "PURE_WEYL_BV_BFV_PROGRAMME",
        "label": "Pure-Weyl BV–BFV and causal programme",
        "short_label": "Pure-Weyl BV–BFV",
        "camp_kind": "REPOSITORY_PROGRAMME",
        "camp_summary": "This repository's pure-Weyl programme starts from the classical BV–BFV gauge complex, then keeps local quantum algebra, Euclidean spectral work, reduced modes, and Lorentzian causal claims on separate evidence rails.",
        "central_question": "Can pure Weyl gravity be carried from its classical gauge complex to a local quantum theory and a physically admissible Lorentzian state without crossing an uncertified bridge?",
        "lineage": ["classical BV–BFV gauge theory", "local BRST cohomology", "Euclidean spectral and Lorentzian causal analysis"],
        "signature_ideas": ["classical complex as import authority", "classify anomalies before coefficients", "restore QME before residual transfer"],
        "atlas_window": "Classical-standard smooth/PDE, Krein, and algebraic carriers that contain the programme's present classical, reduced, and local-quantum ingredients.",
        "scope_note": "Coverage across these carriers is not a full-complex Lorentzian propagator, Hadamard state, causal perturbative QFT, or restored Lorentzian QME.",
        "aim": "Expose the programme's strong local pieces and the exact typed joins still missing between classical, Euclidean, reduced-mode, and Lorentzian work.",
        "foundations": ["CLASSICAL_STANDARD"],
        "carriers": ["KREIN_INDEFINITE", "ALGEBRAIC_CSTAR", "SMOOTH_DISTRIBUTIONAL"],
    },
    {
        "id": "CONSTRUCTIVE_PROGRAMME",
        "label": "Constructive and computable physics tradition",
        "short_label": "Constructive / computable",
        "camp_kind": "METHODOLOGICAL_TRADITION",
        "camp_summary": "Constructive and computable approaches require existence claims to carry witnesses, algorithms, convergence data, or other operational mathematical content.",
        "central_question": "Which parts of a physical theory can actually be constructed or computed from represented inputs?",
        "lineage": ["Bishop-style constructivism", "computable analysis", "proof mining and represented spaces"],
        "signature_ideas": ["witness-producing existence", "algorithms with represented inputs", "explicit rates and error control"],
        "atlas_window": "All carrier types under the constructive/computable regime.",
        "scope_note": "Computability depends on representation, and a constructive upper bound is not automatically a reverse-mathematical necessity result.",
        "aim": "Track which parts of a predictive theory can be supplied with witnesses, algorithms, and controlled approximation data.",
        "foundations": ["CONSTRUCTIVE_COMPUTABLE"],
        "carriers": ["FINITE_EXACT", "HILBERT_OPERATOR", "KREIN_INDEFINITE", "ALGEBRAIC_CSTAR", "SMOOTH_DISTRIBUTIONAL", "LOCALIC_SYNTHETIC"],
    },
    {
        "id": "TOPOS_INTERNAL_PROGRAMME",
        "label": "Topos and internal quantum-foundations tradition",
        "short_label": "Topos / internal",
        "camp_kind": "RESEARCH_TRADITION",
        "camp_summary": "Topos approaches reformulate spaces, observables, and truth inside an alternative logical universe where propositions may be contextual or local rather than globally Boolean.",
        "central_question": "What changes when the logical universe of the theory is altered instead of merely changing an equation inside ordinary set theory?",
        "lineage": ["Isham–Butterfield contextual logic", "Döring–Isham topos quantum theory", "Heunen–Landsman–Spitters internal algebra"],
        "signature_ideas": ["contextual truth values", "point-free or internal spaces", "intuitionistic logic"],
        "atlas_window": "All carrier types interpreted under the topos/internal regime.",
        "scope_note": "This is a family of non-equivalent approaches; one internal construction does not transfer automatically to every topos or recover empirical quantum theory.",
        "aim": "Map what can be formulated inside alternative logical and geometric universes and which bridges back to ordinary predictions remain open.",
        "foundations": ["TOPOS_INTERNAL"],
        "carriers": ["FINITE_EXACT", "HILBERT_OPERATOR", "KREIN_INDEFINITE", "ALGEBRAIC_CSTAR", "SMOOTH_DISTRIBUTIONAL", "LOCALIC_SYNTHETIC"],
    },
]


def canonical_digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def _selection_key(cell: dict[str, Any], config: dict[str, Any]) -> tuple[int, int, int, int, int]:
    roles = set(cell.get("evidence_roles", {}).values())
    return (
        STATUS_RANK[cell["status"]],
        len(roles & {"DIRECT_LOCAL", "DIRECT_LITERATURE"}),
        cell["status"] == "LOCAL_RESULT",
        len(cell.get("evidence", [])),
        -(config["foundations"].index(cell["foundation"]) * 10 + config["carriers"].index(cell["carrier"])),
    )


def _assembly(
    config: dict[str, Any],
    obligations: list[str],
    cell_map: dict[tuple[str, str, str], dict[str, Any]],
    certified_interfaces: list[dict[str, Any]],
    numerical_records: list[dict[str, Any]],
) -> dict[str, Any]:
    selected = []
    for obligation in obligations:
        candidates = [
            cell_map[(foundation, carrier, obligation)]
            for foundation in config["foundations"]
            for carrier in config["carriers"]
        ]
        cell = max(candidates, key=lambda item: _selection_key(item, config))
        selected.append({
            "obligation": obligation,
            "foundation": cell["foundation"],
            "carrier": cell["carrier"],
            "status": cell["status"],
            "evidence": cell.get("evidence", []),
            "evidence_roles": cell.get("evidence_roles", {}),
            "selection_basis": "Strongest recorded status in the declared admissible region; ties prefer more reviewed direct kinds, local grade, more evidence, then declared order.",
        })
    selected_coordinates = {
        item["obligation"]: {
            "foundation": item["foundation"],
            "carrier": item["carrier"],
            "obligation": item["obligation"],
        }
        for item in selected
    }
    interfaces = []
    for interface_id, label, sources, targets in INTERFACE_TEMPLATES:
        expected_sources = [selected_coordinates[item] for item in sources]
        expected_targets = [selected_coordinates[item] for item in targets]
        certified = next(
            (
                item for item in certified_interfaces
                if item.get("id") == interface_id
                and item.get("status") == "CERTIFIED"
                and item.get("source_coordinates") == expected_sources
                and item.get("target_coordinates") == expected_targets
            ),
            None,
        )
        interfaces.append({
            "id": interface_id,
            "label": label,
            "source_obligations": sources,
            "target_obligations": targets,
            "relation": certified["relation"] if certified else "NOT_ASSESSED",
            "certification_status": "CERTIFIED" if certified else "NOT_ASSESSED",
            "evidence": certified.get("evidence", []) if certified else [],
            "rationale": certified.get("scope") if certified else "Coverage records do not by themselves prove that these selected objects share a model, scope, or translation.",
        })
    direct = sum(item["status"] in DIRECT for item in selected)
    assessed = sum(item["status"] != "NOT_MAPPED" for item in selected)
    certified_count = sum(item["certification_status"] == "CERTIFIED" for item in interfaces)
    numerical = next((item for item in numerical_records if item.get("assembly") == config["id"]), None)
    return {
        **config,
        "kind": "NAVIGATIONAL_PROTOTYPE",
        "selection_rule": "DETERMINISTIC_COVERAGE_ENVELOPE",
        "selected_cells": selected,
        "coverage": {"direct": direct, "assessed": assessed, "total": len(selected), "complete_direct": direct == len(selected)},
        "interfaces": interfaces,
        "maturity_rails": [
            {"id": "OBLIGATION_COVERAGE", "label": "Obligation coverage", "status": "SATISFIED" if direct == len(selected) else "OPEN", "basis": f"{direct}/{len(selected)} obligations have a direct recorded result."},
            {"id": "CROSS_CELL_COMPOSITION", "label": "Cross-cell composition", "status": "PARTIALLY_CERTIFIED" if certified_count else "NOT_ASSESSED", "basis": f"{certified_count}/{len(interfaces)} required interfaces are certified; unassessed joins are missing work, not incompatibility results."},
            {"id": "PREDICTION_DERIVATION", "label": "Prediction derivation", "status": "NOT_EVALUABLE", "basis": "An end-to-end prediction test is premature until the required cross-cell joins are registered."},
            {"id": "OBSERVABLE_IDENTIFICATION", "label": "Observable identification", "status": "NOT_REGISTERED", "basis": "No assembly-level map from formal quantities to measured observables is registered."},
            {"id": "NUMERICAL_REPRODUCIBILITY", "label": "Numerical reproducibility", "status": numerical["status"] if numerical else "NO_RECORDS", "basis": numerical["gate_passed"] + "; " + numerical["precision_gate"] + ". This is algorithmic reproduction, not empirical validation." if numerical else "No independent numerical reproduction record is registered for this assembly."},
            {"id": "EMPIRICAL_COMPARISON", "label": "Empirical comparison", "status": "NO_RECORDS", "basis": "The empirical ledger contains no comparison for this assembly."},
            {"id": "ROBUSTNESS_OUT_OF_SAMPLE", "label": "Robustness / out-of-sample", "status": "NO_RECORDS", "basis": "No robustness or held-out prediction record is registered."},
        ],
        "complete_theory": False,
        "empirically_supported": False,
    }


def build_assembly_assessment(dataset: dict[str, Any]) -> dict[str, Any]:
    axes = {axis["id"]: axis for axis in dataset["axes"]}
    obligations = [item["id"] for item in axes["REFINED_OBLIGATION"]["keys"]]
    cell_map = {(cell["foundation"], cell["carrier"], cell["obligation"]): cell for cell in dataset["cells"]}
    certified_interfaces = dataset.get("cross_cell_interfaces", [])
    carrier_interfaces = dataset.get("carrier_interfaces", [])
    numerical_records = dataset.get("numerical_reproducibility_records", [])
    assemblies = [_assembly(config, obligations, cell_map, certified_interfaces, numerical_records) for config in ASSEMBLY_CONFIGS]
    calibration_control = json.loads(GR_CONTROL.read_text())
    gr_cassini = json.loads(GR_CASSINI_ASSEMBLY.read_text())
    mannheim_ngc3198 = json.loads(MANNHEIM_NGC3198_ASSEMBLY.read_text())
    ngc3198_comparison = json.loads(NGC3198_COMMON_FIT_COMPARISON.read_text())
    value = {
        "schema_version": "foundational-theory-assembly-atlas-v1",
        "result_id": "FOUNDATIONAL_THEORY_ASSEMBLY_ATLAS_V1",
        "result_kind": "FAIL_CLOSED_THEORY_ASSEMBLY_AND_EMPIRICAL_LEDGER",
        "lifecycle": "VERIFIED_NAVIGATION_ARTIFACT",
        "title": "Model-scoped prediction assemblies, theory prototypes, maturity rails, and calibration controls",
        "created": dataset["created"],
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "unit": "A prototype assembly is a deterministic coverage envelope over selected cells, not a composed theory.",
        "interface_vocabulary": INTERFACE_VOCABULARY,
        "certified_interface_records": certified_interfaces,
        "certified_carrier_interface_records": carrier_interfaces,
        "assemblies": assemblies,
        "model_scoped_assemblies": [gr_cassini, mannheim_ngc3198],
        "model_scoped_sources": [
            {
                "path": "foundations/results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json",
                "sha256": hashlib.sha256(GR_CASSINI_ASSEMBLY.read_bytes()).hexdigest(),
            },
            {
                "path": "foundations/results/FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1.json",
                "sha256": hashlib.sha256(MANNHEIM_NGC3198_ASSEMBLY.read_bytes()).hexdigest(),
            },
        ],
        "model_comparisons": [ngc3198_comparison],
        "model_comparison_sources": [{
            "path": "foundations/results/FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1.json",
            "sha256": hashlib.sha256(NGC3198_COMMON_FIT_COMPARISON.read_bytes()).hexdigest(),
        }],
        "calibration_controls": [calibration_control],
        "calibration_source": {
            "path": "foundations/standard-gr-observational-control-v1.json",
            "sha256": hashlib.sha256(GR_CONTROL.read_bytes()).hexdigest(),
        },
        "empirical_ledger": {
            "record_schema": ["assembly", "benchmark", "observable_map", "dataset", "prediction", "comparison_method", "uncertainty", "parameter_fit_scope", "out_of_sample_status", "evidence"],
            "benchmarks": [{**item, "status": "NOT_REGISTERED"} for item in BENCHMARKS],
            "records": [],
        },
        "numerical_reproducibility_ledger": {
            "unit": "Independent algorithmic reproduction of a mathematical/numerical calculation; this is distinct from empirical comparison and out-of-sample robustness.",
            "records": numerical_records,
        },
        "claim_flags": {
            "prototype_assemblies_generated": True,
            "research_camp_lenses_declared": True,
            "selected_cells_content_addressed": True,
            "interface_and_coverage_states_separated": True,
            "at_least_one_cross_cell_interface_certified": bool(certified_interfaces),
            "scoped_carrier_interface_registered": bool(carrier_interfaces),
            "numerical_reproducibility_rail_declared": True,
            "empirical_record_schema_declared": True,
            "external_positive_control_registered": True,
            "missing_and_failed_states_separated": True,
            "model_scoped_prediction_assembly_registered": True,
            "second_model_scoped_mannheim_assembly_registered": True,
            "mixed_empirical_result_preserved": True,
            "common_protocol_model_comparison_registered": True,
            "bounded_prediction_chain_established": True,
            "bounded_empirical_agreement_assessed": True,
            "cross_cell_composability_established": False,
            "prediction_chain_established": False,
            "empirical_agreement_assessed": False,
            "complete_observationally_valid_theory_identified": False,
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
            "a complete theory, a new Lorentzian-causal result, or a quantum lifecycle promotion",
        ],
        "source_atlas_digest": dataset["canonical_digest"],
    }
    value["canonical_digest"] = canonical_digest(value)
    return value
