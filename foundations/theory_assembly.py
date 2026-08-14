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
from typing import Any


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
        "label": "Classical-standard mixed-carrier reference",
        "aim": "Ask how far mainstream mathematics reaches when every registered carrier is available.",
        "foundations": ["CLASSICAL_STANDARD"],
        "carriers": ["FINITE_EXACT", "HILBERT_OPERATOR", "KREIN_INDEFINITE", "ALGEBRAIC_CSTAR", "SMOOTH_DISTRIBUTIONAL", "LOCALIC_SYNTHETIC"],
    },
    {
        "id": "STANDARD_ALGEBRAIC_PROFILE",
        "label": "Classical-standard algebraic profile",
        "aim": "Use the present algebraic/C* profile as a single-carrier reference case.",
        "foundations": ["CLASSICAL_STANDARD"],
        "carriers": ["ALGEBRAIC_CSTAR"],
    },
    {
        "id": "FINITE_EXACT_PROGRAMME",
        "label": "Finite exact programme",
        "aim": "Test how much of the physics chain survives in finite, exactly checkable data.",
        "foundations": ["FINITE_DISCRETE"],
        "carriers": ["FINITE_EXACT"],
    },
    {
        "id": "WEAK_BASE_FINITE_EXACT",
        "label": "Weak-base finite-exact programme",
        "aim": "Expose the arithmetic or Choice strength of finite exact constructions without identifying distinct weak bases.",
        "foundations": ["WEAK_ARITHMETIC", "WEAK_CHOICE_ZF"],
        "carriers": ["FINITE_EXACT"],
    },
    {
        "id": "KREIN_ALGEBRAIC_PROGRAMME",
        "label": "Krein and algebraic programme",
        "aim": "Explore indefinite state spaces together with algebraic state and observable constructions.",
        "foundations": ["CLASSICAL_STANDARD", "WEAK_CHOICE_ZF"],
        "carriers": ["KREIN_INDEFINITE", "ALGEBRAIC_CSTAR"],
    },
    {
        "id": "CONSTRUCTIVE_PROGRAMME",
        "label": "Constructive/computable programme",
        "aim": "Track which parts of a predictive theory can be supplied with witnesses or algorithms.",
        "foundations": ["CONSTRUCTIVE_COMPUTABLE"],
        "carriers": ["FINITE_EXACT", "HILBERT_OPERATOR", "KREIN_INDEFINITE", "ALGEBRAIC_CSTAR", "SMOOTH_DISTRIBUTIONAL", "LOCALIC_SYNTHETIC"],
    },
    {
        "id": "TOPOS_INTERNAL_PROGRAMME",
        "label": "Topos/internal programme",
        "aim": "Map a physics construction performed inside an alternative logical or geometric universe.",
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
    return {
        **config,
        "kind": "NAVIGATIONAL_PROTOTYPE",
        "selection_rule": "DETERMINISTIC_COVERAGE_ENVELOPE",
        "selected_cells": selected,
        "coverage": {"direct": direct, "assessed": assessed, "total": len(selected), "complete_direct": direct == len(selected)},
        "interfaces": interfaces,
        "hard_gates": [
            {"id": "OBLIGATION_COVERAGE", "label": "Obligation coverage", "status": "SATISFIED" if direct == len(selected) else "OPEN", "basis": f"{direct}/{len(selected)} obligations have a direct recorded result."},
            {"id": "CROSS_CELL_COMPOSITION", "label": "Cross-cell composition", "status": "BLOCKED", "basis": f"{certified_count}/{len(interfaces)} required interfaces are certified; the remainder block assembly composition."},
            {"id": "PREDICTION_DERIVATION", "label": "Prediction derivation", "status": "BLOCKED", "basis": "No registered end-to-end derivation connects the selected cells."},
            {"id": "OBSERVABLE_IDENTIFICATION", "label": "Observable identification", "status": "BLOCKED", "basis": "No assembly-level map from formal quantities to measured observables is registered."},
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
    assemblies = [_assembly(config, obligations, cell_map, certified_interfaces) for config in ASSEMBLY_CONFIGS]
    value = {
        "schema_version": "foundational-theory-assembly-atlas-v1",
        "result_id": "FOUNDATIONAL_THEORY_ASSEMBLY_ATLAS_V1",
        "result_kind": "FAIL_CLOSED_THEORY_ASSEMBLY_AND_EMPIRICAL_LEDGER",
        "lifecycle": "VERIFIED_NAVIGATION_ARTIFACT",
        "title": "Candidate theory assemblies and missing interfaces",
        "created": dataset["created"],
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "unit": "A prototype assembly is a deterministic coverage envelope over selected cells, not a composed theory.",
        "interface_vocabulary": INTERFACE_VOCABULARY,
        "certified_interface_records": certified_interfaces,
        "assemblies": assemblies,
        "empirical_ledger": {
            "record_schema": ["assembly", "benchmark", "observable_map", "dataset", "prediction", "comparison_method", "uncertainty", "parameter_fit_scope", "out_of_sample_status", "evidence"],
            "benchmarks": [{**item, "status": "NOT_REGISTERED"} for item in BENCHMARKS],
            "records": [],
        },
        "claim_flags": {
            "prototype_assemblies_generated": True,
            "selected_cells_content_addressed": True,
            "interface_and_coverage_states_separated": True,
            "at_least_one_cross_cell_interface_certified": bool(certified_interfaces),
            "empirical_record_schema_declared": True,
            "cross_cell_composability_established": False,
            "prediction_chain_established": False,
            "empirical_agreement_assessed": False,
            "complete_observationally_valid_theory_identified": False,
        },
        "does_not_establish": [
            "that selected cells concern the same physical model or scope",
            "that either certified scoped bridge supplies any unregistered carrier or foundation translation",
            "that direct coverage composes into an end-to-end prediction",
            "that a reduced or finite construction has a controlled continuum limit",
            "that any prototype agrees with observations",
            "that the benchmark catalogue is a complete set of physical tests",
            "a complete theory, a new Lorentzian-causal result, or a quantum lifecycle promotion",
        ],
        "source_atlas_digest": dataset["canonical_digest"],
    }
    value["canonical_digest"] = canonical_digest(value)
    return value
