#!/usr/bin/env python3
"""Derive fail-closed theory-coverage profiles from the foundations atlas.

This module deliberately does not score empirical truth.  It computes coverage
envelopes and Pareto navigation aids, while keeping theory composition and
observational agreement as separate, currently unpopulated evidence rails.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import itertools
import json
from typing import Any


DIRECT = {"LOCAL_RESULT", "LITERATURE_RESULT"}
STATUS_RANK = {
    "NOT_MAPPED": 0,
    "REVIEWED_GAP": 1,
    "PRIORITY_GAP": 1,
    "PIECES_ONLY": 2,
    "LOCAL_RESULT": 3,
    "LITERATURE_RESULT": 3,
}
STATUS_ORDER = [
    "LOCAL_RESULT",
    "LITERATURE_RESULT",
    "PIECES_ONLY",
    "PRIORITY_GAP",
    "REVIEWED_GAP",
    "NOT_MAPPED",
]

BUNDLES = [
    {
        "id": "KINEMATICS_STATES",
        "label": "Kinematics and states",
        "question": "Does the formulation say what exists, what is observable, and how states are represented?",
        "obligations": ["KINEMATICS_OBSERVABLES", "STATE_EXISTENCE", "STATE_REPRESENTATION"],
    },
    {
        "id": "PREDICTION_OBSERVATION",
        "label": "Prediction and observational bridge",
        "question": "Can it assign probabilities, select a physical state, and connect the formulation back to operational or standard predictions?",
        "obligations": ["PROBABILITY_RULE", "PHYSICAL_STATE_SELECTION", "RECONSTRUCTION_LIMITS"],
    },
    {
        "id": "DYNAMICS_CAUSALITY",
        "label": "Dynamics and causality",
        "question": "Are the generator, evolution problem, and causal response all under control?",
        "obligations": ["GENERATOR_SPECTRAL_DYNAMICS", "EVOLUTION_WELLPOSEDNESS", "CAUSAL_PROPAGATION_GREEN"],
    },
    {
        "id": "GAUGE_INTERACTION",
        "label": "Gauge structure and interactions",
        "question": "Are gauge-redundant content and genuine interactions both constructed?",
        "obligations": ["GAUGE_BV_COHOMOLOGY", "INTERACTION_CONSTRUCTION"],
    },
    {
        "id": "QUANTUM_CONSISTENCY",
        "label": "Quantum consistency chain",
        "question": "Are counterterms, anomalies, singular products, QME restoration, and residual transfer connected in the required order?",
        "obligations": [
            "COUNTERTERM_CLASSIFICATION",
            "ANOMALY_CLASSIFICATION",
            "RENORMALIZED_PRODUCTS",
            "QME_RESTORATION",
            "RESIDUAL_QUANTUM_TRANSFER",
        ],
    },
]

PRESETS = [
    {
        "id": "PREDICTIVE_PHYSICS",
        "label": "Predictive physics chain",
        "description": "A broad default for turning states and dynamics into operational predictions; it is not a definition of all physics.",
        "obligations": [
            "KINEMATICS_OBSERVABLES",
            "STATE_EXISTENCE",
            "STATE_REPRESENTATION",
            "PROBABILITY_RULE",
            "PHYSICAL_STATE_SELECTION",
            "GENERATOR_SPECTRAL_DYNAMICS",
            "EVOLUTION_WELLPOSEDNESS",
            "CAUSAL_PROPAGATION_GREEN",
            "INTERACTION_CONSTRUCTION",
            "RECONSTRUCTION_LIMITS",
        ],
    },
    {
        "id": "CAUSAL_CLASSICAL",
        "label": "Causal classical/interacting chain",
        "description": "Kinematics, states, well-posed causal dynamics, interactions, and reconstruction, without requiring the quantum-consistency tail.",
        "obligations": [
            "KINEMATICS_OBSERVABLES",
            "STATE_EXISTENCE",
            "STATE_REPRESENTATION",
            "GENERATOR_SPECTRAL_DYNAMICS",
            "EVOLUTION_WELLPOSEDNESS",
            "CAUSAL_PROPAGATION_GREEN",
            "INTERACTION_CONSTRUCTION",
            "RECONSTRUCTION_LIMITS",
        ],
    },
    {
        "id": "QUANTUM_GAUGE",
        "label": "Quantum gauge completion",
        "description": "The complete sixteen-obligation chain, including the ordered counterterm/anomaly/QME/residual-transfer requirements.",
        "obligations": [item for bundle in BUNDLES for item in bundle["obligations"]],
    },
]


def canonical_digest(value: dict[str, Any]) -> str:
    body = dict(value)
    body.pop("canonical_digest", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def _counts(cells: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(cell["status"] for cell in cells)
    return {status: counts[status] for status in STATUS_ORDER}


def _profile(foundation: str, carrier: str, cells: list[dict[str, Any]], preset: dict[str, Any]) -> dict[str, Any]:
    by_obligation = {cell["obligation"]: cell for cell in cells}
    gate_cells = [by_obligation[item] for item in preset["obligations"]]
    bundle_profiles = []
    for bundle in BUNDLES:
        selected = [by_obligation[item] for item in bundle["obligations"]]
        bundle_profiles.append({
            "bundle": bundle["id"],
            "counts": _counts(selected),
            "direct": sum(cell["status"] in DIRECT for cell in selected),
            "total": len(selected),
        })
    return {
        "foundation": foundation,
        "carrier": carrier,
        "counts": _counts(cells),
        "direct": sum(cell["status"] in DIRECT for cell in cells),
        "assessed": sum(cell["status"] != "NOT_MAPPED" for cell in cells),
        "default_gate": {
            "preset": preset["id"],
            "direct": sum(cell["status"] in DIRECT for cell in gate_cells),
            "assessed": sum(cell["status"] != "NOT_MAPPED" for cell in gate_cells),
            "total": len(gate_cells),
            "complete_direct": all(cell["status"] in DIRECT for cell in gate_cells),
            "blockers": [
                {"obligation": cell["obligation"], "status": cell["status"]}
                for cell in gate_cells if cell["status"] not in DIRECT
            ],
        },
        "reconstruction_status": by_obligation["RECONSTRUCTION_LIMITS"]["status"],
        "bundles": bundle_profiles,
    }


def _dominates(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_metrics = (
        left["default_gate"]["direct"],
        left["default_gate"]["assessed"],
        left["direct"],
        STATUS_RANK[left["reconstruction_status"]],
    )
    right_metrics = (
        right["default_gate"]["direct"],
        right["default_gate"]["assessed"],
        right["direct"],
        STATUS_RANK[right["reconstruction_status"]],
    )
    return all(a >= b for a, b in zip(left_metrics, right_metrics)) and any(
        a > b for a, b in zip(left_metrics, right_metrics)
    )


def _carrier_envelopes(
    foundations: list[str], carriers: list[str], obligations: list[str], cell_map: dict[tuple[str, str, str], dict[str, Any]]
) -> list[dict[str, Any]]:
    envelopes = []
    for foundation in foundations:
        best_maximum = -1
        minimal_subsets: list[tuple[str, ...]] = []
        for size in range(1, len(carriers) + 1):
            for subset in itertools.combinations(carriers, size):
                direct = sum(
                    max(STATUS_RANK[cell_map[(foundation, carrier, obligation)]["status"]] for carrier in subset) == 3
                    for obligation in obligations
                )
                if direct > best_maximum:
                    best_maximum = direct
                    minimal_subsets = [subset]
                elif direct == best_maximum:
                    minimal_subsets.append(subset)
        smallest = min(len(item) for item in minimal_subsets)
        minimal_subsets = [item for item in minimal_subsets if len(item) == smallest]
        all_carrier_rows = []
        for obligation in obligations:
            ranks = {
                carrier: STATUS_RANK[cell_map[(foundation, carrier, obligation)]["status"]]
                for carrier in carriers
            }
            best_rank = max(ranks.values())
            contributors = [carrier for carrier in carriers if ranks[carrier] == best_rank]
            statuses = sorted({cell_map[(foundation, carrier, obligation)]["status"] for carrier in contributors})
            all_carrier_rows.append({
                "obligation": obligation,
                "readiness_rank": best_rank,
                "statuses": statuses,
                "contributing_carriers": contributors,
            })
        envelopes.append({
            "foundation": foundation,
            "all_carriers_envelope": all_carrier_rows,
            "maximum_direct_obligations": best_maximum,
            "minimum_carriers_for_that_maximum": smallest,
            "minimal_maximum_subsets": [list(item) for item in minimal_subsets],
            "composition_status": "NOT_ASSESSED",
        })
    return envelopes


def build_assessment(dataset: dict[str, Any]) -> dict[str, Any]:
    axes = {axis["id"]: axis for axis in dataset["axes"]}
    foundations = [item["id"] for item in axes["FOUNDATION"]["keys"]]
    carriers = [item["id"] for item in axes["CARRIER"]["keys"]]
    obligations = [item["id"] for item in axes["REFINED_OBLIGATION"]["keys"]]
    cell_map = {
        (cell["foundation"], cell["carrier"], cell["obligation"]): cell
        for cell in dataset["cells"]
    }
    default = PRESETS[0]
    profiles = [
        _profile(
            foundation,
            carrier,
            [cell_map[(foundation, carrier, obligation)] for obligation in obligations],
            default,
        )
        for foundation in foundations
        for carrier in carriers
    ]
    for profile in profiles:
        profile["pareto_default"] = not any(
            other is not profile and _dominates(other, profile) for other in profiles
        )
    payload = {
        "schema_version": "foundational-theory-viability-assessment-v1",
        "result_id": "FOUNDATIONAL_THEORY_VIABILITY_ASSESSMENT_V1",
        "result_kind": "FAIL_CLOSED_THEORY_COVERAGE_AND_MISSING_RAIL_ASSESSMENT",
        "lifecycle": "VERIFIED_NAVIGATION_ARTIFACT",
        "title": "Theory coverage, composition, and observation assessment",
        "created": dataset["created"],
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "unit": "A formulation profile is one mathematical regime paired with one carrier; a carrier portfolio is a coverage envelope, not a proved integrated theory.",
        "status_semantics": {
            "direct": ["LOCAL_RESULT", "LITERATURE_RESULT"],
            "partial": ["PIECES_ONLY"],
            "explicit_gap": ["PRIORITY_GAP"],
            "reviewed_open_gap": ["REVIEWED_GAP"],
            "unknown": ["NOT_MAPPED"],
            "tie_rule": "Local and literature results are equally direct but remain visibly distinct evidence types.",
        },
        "bundles": BUNDLES,
        "presets": PRESETS,
        "profiles": profiles,
        "carrier_envelopes": _carrier_envelopes(foundations, carriers, obligations, cell_map),
        "global_rails": [
            {
                "id": "OBLIGATION_COVERAGE",
                "label": "Obligation coverage",
                "status": "COMPUTED_FROM_ATLAS",
                "meaning": "The tables can show where direct results, partial ingredients, selected priority gaps, reviewed open gaps, and unmapped cells occur.",
            },
            {
                "id": "CROSS_OBLIGATION_COMPOSITION",
                "label": "One coherent integrated theory",
                "status": "PARTIALLY_ASSESSED",
                "meaning": "Two scoped relations are certified: finite-corner state-to-probability and free ground-state-to-dynamics. The other required joins remain open, so no profile or carrier envelope composes into one jointly consistent theory.",
            },
            {
                "id": "EMPIRICAL_AGREEMENT",
                "label": "Agreement with observations",
                "status": "NOT_IN_CURRENT_SCHEMA",
                "meaning": "The atlas has no typed dataset, likelihood, residual, parameter-fit, or out-of-sample prediction record. Reconstruction coverage is only a bridge-readiness proxy, not observational validation.",
            },
        ],
        "pareto_definition": {
            "preset": default["id"],
            "maximize": [
                "direct obligations in the default gate",
                "assessed obligations in the default gate",
                "direct obligations across all sixteen",
                "reconstruction/limits readiness rank",
            ],
            "warning": "Pareto membership is a navigation aid over present coverage, not a theorem ranking, probability, or empirical verdict.",
        },
        "claim_flags": {
            "all_36_single_carrier_profiles_computed": True,
            "carrier_portfolio_envelopes_computed": True,
            "coverage_and_empirical_agreement_separated": True,
            "complete_observationally_valid_theory_identified": False,
            "cross_cell_composability_established": False,
            "empirical_agreement_assessed": False,
            "scalar_winner_score_defined": False,
        },
        "does_not_establish": [
            "that direct evidence in separate cells composes into one theory",
            "that a finite or reduced model has a controlled continuum limit",
            "that reconstruction/limits coverage demonstrates agreement with observations",
            "that NOT_MAPPED is failure, incoherence, or absence from the literature",
            "that REVIEWED_GAP is a result, selected priority, or literature-absence finding",
            "that Pareto-frontier profiles are physically preferred or more likely true",
            "a complete observationally validated theory under any regime or carrier portfolio",
        ],
        "source_atlas_digest": dataset["canonical_digest"],
    }
    payload["canonical_digest"] = canonical_digest(payload)
    return payload
