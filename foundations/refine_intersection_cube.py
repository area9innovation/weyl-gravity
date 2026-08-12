#!/usr/bin/env python3
"""Generate the backward-compatible refined foundations cube.

V0 remains immutable.  V1 splits overloaded state, dynamics, and quantum-
interaction obligations.  Evidence descends only through this explicit
capability registry; an overloaded parent status is never copied to every
child.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
V0 = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V0.json"
CYLINDER = ROOT / "foundations/results/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1.json"
FINITE_QUBIT = ROOT / "foundations/results/FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1.json"
OUTPUT = ROOT / "foundations/results/FOUNDATIONAL_INTERSECTION_CUBE_V1.json"
REPORT = ROOT / "foundations/reports/refined-intersection-cube.md"

K = "KINEMATICS_OBSERVABLES"
SE = "STATE_EXISTENCE"
SR = "STATE_REPRESENTATION"
PR = "PROBABILITY_RULE"
PS = "PHYSICAL_STATE_SELECTION"
GD = "GENERATOR_SPECTRAL_DYNAMICS"
EW = "EVOLUTION_WELLPOSEDNESS"
CG = "CAUSAL_PROPAGATION_GREEN"
G = "GAUGE_BV_COHOMOLOGY"
IC = "INTERACTION_CONSTRUCTION"
CT = "COUNTERTERM_CLASSIFICATION"
AN = "ANOMALY_CLASSIFICATION"
RP = "RENORMALIZED_PRODUCTS"
QM = "QME_RESTORATION"
RT = "RESIDUAL_QUANTUM_TRANSFER"
R = "RECONSTRUCTION_LIMITS"

REFINEMENT = {
    K: [K],
    "STATES_PROBABILITY": [SE, SR, PR, PS],
    "DYNAMICS_PROPAGATION": [GD, EW, CG],
    G: [G],
    "INTERACTION_RENORMALIZATION_QME": [IC, CT, AN, RP, QM, RT],
    R: [R],
}

OBLIGATION_META = {
    K: ("Kinematics/observables", "Define degrees of freedom, observables, commutation structure, and configurations."),
    SE: ("State existence", "Construct at least one normalized or algebraically valid state in the declared carrier."),
    SR: ("State representation", "Relate states to vectors, density operators, measures, valuations, or GNS data."),
    PR: ("Probability rule", "Construct or derive normalized event probabilities or a Born-type rule."),
    PS: ("Physical state selection", "Select or obstruct a physically distinguished vacuum, thermal, Hadamard, or other state."),
    GD: ("Generator/spectral dynamics", "Construct generators, spectra, one-parameter groups, or algebra automorphisms."),
    EW: ("Evolution/well-posedness", "Prove existence, uniqueness, stability, or computability of evolution in a stated topology."),
    CG: ("Causal propagation/Green", "Construct advanced/retarded maps and prove finite propagation or causal support."),
    G: ("Gauge/BV/cohomology", "Handle gauge symmetry, BRST/BV complexes, residual cohomology, and gauge independence."),
    IC: ("Interaction construction", "Construct a nontrivial interaction, deformation, or interacting product."),
    CT: ("Counterterm classification", "Classify allowed local counterterms before computing coefficients."),
    AN: ("Anomaly classification", "Classify possible local anomalies and consistency conditions."),
    RP: ("Renormalized products", "Construct renormalized time-ordered or interacting products."),
    QM: ("QME restoration", "Compute or cancel the breaking and restore the local quantum master equation."),
    RT: ("Residual quantum transfer", "Transfer a restored quantum correction to the residual complex."),
    R: ("Reconstruction/limits", "Prove operational reconstruction, comparison, continuum-limit, or empirical-equivalence results."),
}


def cap(direct: str = "", pieces: str = "") -> dict[str, set[str]]:
    return {"direct": set(direct.split()) if direct else set(), "pieces": set(pieces.split()) if pieces else set()}


# Only the split children occur here.  Missing registration means no transfer.
CAPABILITIES: dict[str, dict[str, set[str]]] = {
    "FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1": cap(f"{SE} {SR} {PR} {GD} {EW} {IC}", f"{PS} {CT} {AN} {RP} {QM} {RT} {CG}"),
    "FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1": cap(f"{SE} {SR}", f"{PR} {PS}"),
    "FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1": cap(SE, f"{SR} {PR} {PS} {GD}"),
    "FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1": cap(f"{SE} {PS}", f"{SR} {PR}"),
    "FOUNDATIONAL_EXPLICIT_MODE_DYNAMICS_ZF_V1": cap(f"{GD} {EW}", CG),
    "FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1": cap(GD, EW),
    "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1": cap(f"{EW} {CG}", GD),
    "FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1": cap(f"{CT} {AN}", f"{IC} {RP} {QM} {RT}"),
    "FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1": cap("", f"{IC} {CT} {AN} {QM} {RT}"),
    "FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0": cap("", f"{SE} {SR} {PR} {PS} {GD} {EW} {CG} {IC} {CT} {AN} {RP} {QM} {RT}"),
    "hardy-2001": cap(f"{SE} {SR} {PR}", PS),
    "chiribella-dariano-perinotti-2011": cap(f"{SE} {SR} {PR}", PS),
    "richman-bridges-1999": cap(f"{SR} {PR}", f"{SE} {PS}"),
    "bridges-svozil-2000": cap(SE, f"{SR} {PR} {PS}"),
    "doring-2008": cap(SR, f"{SE} {PR} {PS}"),
    "heunen-landsman-spitters-2009": cap(f"{SE} {SR}", f"{PR} {PS} {GD}"),
    "constantin-doring-2020": cap(SR, f"{PR} {PS}"),
    "gibbons-hoffman-wootters-2004": cap(f"{SE} {SR} {PR}", PS),
    "neumann-pape-streicher-2018": cap(f"{SE} {SR} {GD}", f"{PR} {PS} {EW}"),
    "haag-kastler-1964": cap(SE, f"{SR} {PR} {PS} {GD} {EW} {CG}"),
    "brunetti-fredenhagen-verch-2001": cap(f"{SE} {SR}", f"{PS} {GD} {EW} {CG} {IC}"),
    "gottschalk-2004": cap(f"{GD} {EW} {PS}", f"{SE} {SR} {PR} {CG}"),
    "bateman-turok-2026": cap(SE, f"{SR} {PR} {PS} {GD} {EW}"),
    "abramsky-coecke-2004": cap(PR, f"{SE} {SR} {PS} {GD}"),
    "coquand-spitters-2009": cap("", f"{SE} {SR} {PR}"),
    "blackadar-farah-2026": cap("", f"{SE} {SR} {PR} {GD}"),
    "blackadar-farah-karagila-2026": cap("", f"{SE} {SR} {GD} {EW}"),
    "bender-boettcher-1998": cap(GD, f"{EW} {SE} {PS}"),
    "mostafazadeh-2001": cap(GD, f"{EW} {SE} {PS}"),
    "brenna-flori-2012": cap(GD, EW),
    "flori-2011": cap(GD, EW),
    "harding-heunen-2019": cap(f"{SR} {GD}", f"{SE} {PR} {PS} {EW}"),
    "pour-el-richards-1981": cap(EW, CG),
    "fewster-verch-2011": cap(f"{EW} {CG}", GD),
    "zohar-burrello-2014": cap(f"{GD} {EW} {IC}", f"{CG} {CT} {AN} {RP} {QM} {RT}"),
    "kogut-susskind-1975": cap(f"{GD} {EW} {IC}", f"{CG} {CT} {AN} {RP} {QM} {RT}"),
    "bahr-dittrich-2009": cap("", f"{IC} {CT} {AN} {QM} {RT}"),
    "dittrich-2012": cap("", f"{GD} {EW} {IC} {RP} {RT}"),
    "barnich-brandt-henneaux-2000": cap(f"{IC} {CT} {AN}", f"{RP} {QM} {RT}"),
    "fredenhagen-rejzner-2011": cap(f"{IC} {CT} {AN} {RP}", f"{QM} {RT}"),
    "brunetti-fredenhagen-rejzner-2013": cap(f"{IC} {RP}", f"{CT} {AN} {QM} {RT}"),
}

OVERLAYS = [
    # The finite exact witness fills interaction only, not the other five former siblings.
    *[
        {"foundation": foundation, "carrier": "FINITE_EXACT", "obligation": IC, "status": "LOCAL_RESULT", "evidence": ["FOUNDATIONAL_FINITE_QUBIT_INTERACTION_CORE_V1"], "summary": "The exact two-qubit Hamiltonian constructs a nontrivial entangling interaction.", "boundary": "No counterterm, anomaly, renormalized-product, QME-restoration, or residual-transfer result follows."}
        for foundation in ("CLASSICAL_STANDARD", "WEAK_ARITHMETIC", "WEAK_CHOICE_ZF", "CONSTRUCTIVE_COMPUTABLE", "FINITE_DISCRETE")
    ],
    {"foundation": "WEAK_ARITHMETIC", "carrier": "FINITE_EXACT", "obligation": GD, "status": "LOCAL_RESULT", "evidence": ["FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"], "summary": "Finite Laurent degrees give exact cylinder-wave generators.", "boundary": "This is a fixed finite fixture, not a completed evolution theorem."},
    {"foundation": "WEAK_ARITHMETIC", "carrier": "FINITE_EXACT", "obligation": EW, "status": "LOCAL_RESULT", "evidence": ["FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"], "summary": "Every fixed finite Laurent fixture evolves exactly and satisfies the wave equation.", "boundary": "PRA sufficiency at fixed cutoff does not prove an infinite energy-space solution."},
    {"foundation": "WEAK_ARITHMETIC", "carrier": "SMOOTH_DISTRIBUTIONAL", "obligation": EW, "status": "PIECES_ONLY", "evidence": ["FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1", "weihrauch-zhong-2002"], "summary": "An exact finite-to-coded ladder and computable Sobolev wave result identify a specific RCA_0 formalization target.", "boundary": "No second-order-arithmetic upper bound or reversal has been proved."},
    {"foundation": "WEAK_ARITHMETIC", "carrier": "SMOOTH_DISTRIBUTIONAL", "obligation": CG, "status": "PIECES_ONLY", "evidence": ["FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1", "FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1"], "summary": "The exact antipodal obstruction separates spectral approximation from the conditional causal Green dependency shell.", "boundary": "No causal PDE theorem has been formalized over a weak base."},
    {"foundation": "CONSTRUCTIVE_COMPUTABLE", "carrier": "SMOOTH_DISTRIBUTIONAL", "obligation": EW, "status": "LITERATURE_RESULT", "evidence": ["weihrauch-zhong-2002", "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"], "summary": "Wave propagation is computable in the stated C1 and Sobolev representations reviewed by the ladder.", "boundary": "TTE computability is representation-sensitive and is not a Bishop-constructive or reverse-mathematical theorem."},
    {"foundation": "CONSTRUCTIVE_COMPUTABLE", "carrier": "SMOOTH_DISTRIBUTIONAL", "obligation": CG, "status": "PIECES_ONLY", "evidence": ["pour-el-richards-1981", "weihrauch-zhong-2002", "FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1"], "summary": "Positive and negative computability results expose the representation and localization dependencies of wave propagation.", "boundary": "Neither source constructs a constructive causal Green operator for Weyl gravity."},
]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capability_digest() -> str:
    payload = {key: {kind: sorted(values) for kind, values in value.items()} for key, value in sorted(CAPABILITIES.items())}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def migrate_child(parent: dict[str, Any], child: str) -> dict[str, Any]:
    parent_obligation = parent["obligation"]
    coordinate = {key: parent[key] for key in ("foundation", "carrier")}
    if len(REFINEMENT[parent_obligation]) == 1:
        return {
            **coordinate, "obligation": child, "status": parent["status"], "evidence": parent["evidence"],
            "parent_obligation": parent_obligation, "migration_relation": "EXACT_ONE_TO_ONE",
            "summary": parent["summary"], "boundary": parent["boundary"],
        }
    local_direct, literature_direct, pieces = [], [], []
    for evidence in parent["evidence"]:
        registration = CAPABILITIES.get(evidence, {"direct": set(), "pieces": set()})
        if child in registration["direct"]:
            (local_direct if evidence.startswith("FOUNDATIONAL_") else literature_direct).append(evidence)
        elif child in registration["pieces"]:
            pieces.append(evidence)
    if local_direct:
        status, supporting = "LOCAL_RESULT", local_direct + literature_direct + pieces
    elif literature_direct:
        status, supporting = "LITERATURE_RESULT", literature_direct + pieces
    elif pieces:
        status, supporting = "PIECES_ONLY", pieces
    else:
        status, supporting = "MIGRATION_UNRESOLVED", parent["evidence"]
    label = OBLIGATION_META[child][0]
    return {
        **coordinate, "obligation": child, "status": status, "evidence": supporting,
        "parent_obligation": parent_obligation, "migration_relation": "CAPABILITY_QUALIFIED" if status != "MIGRATION_UNRESOLVED" else "NO_REGISTERED_DESCENT",
        "summary": f"Refined child '{label}': " + ("registered evidence supports this child." if status != "MIGRATION_UNRESOLVED" else "the overloaded parent evidence has no registered transfer to this child."),
        "boundary": "The v0 parent status is not inherited by sibling obligations. " + parent["boundary"],
    }


def canonical_digest(cells: list[dict[str, Any]]) -> str:
    payload = [(x["foundation"], x["carrier"], x["obligation"], x["status"], x["migration_relation"], x["evidence"]) for x in cells]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build() -> dict[str, Any]:
    v0 = load(V0)
    axes = {axis["id"]: axis for axis in v0["axes"]}
    obligation_keys = [{"id": key, "label": OBLIGATION_META[key][0], "meaning": OBLIGATION_META[key][1]} for key in OBLIGATION_META]
    cells = [migrate_child(parent, child) for parent in v0["cells"] for child in REFINEMENT[parent["obligation"]]]
    by_coordinate = {(x["foundation"], x["carrier"], x["obligation"]): x for x in cells}
    for overlay in OVERLAYS:
        coordinate = (overlay["foundation"], overlay["carrier"], overlay["obligation"])
        parent = next(parent for parent, children in REFINEMENT.items() if overlay["obligation"] in children)
        by_coordinate[coordinate] = {**overlay, "parent_obligation": parent, "migration_relation": "REVIEWED_V1_OVERLAY"}
    cells = sorted(by_coordinate.values(), key=lambda x: (x["foundation"], x["carrier"], x["obligation"]))
    counts = Counter(x["status"] for x in cells)
    split_counts = Counter(x["parent_obligation"] for x in cells)
    qualified = len(cells) - counts["MIGRATION_UNRESOLVED"]
    return {
        "schema_version": "foundational-intersection-cube-v1",
        "result_id": "FOUNDATIONAL_INTERSECTION_CUBE_V1",
        "result_kind": "REFINED_FOUNDATIONAL_NAVIGATION_CUBE",
        "lifecycle": "LITERATURE_SCOPED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"],
        "created": "2026-08-12",
        "repository_base_commit": "50b3749e02fe3d86064a40766b0e54f10366b4f4",
        "purpose": "Preserve v0 while decomposing state, dynamics, interaction, counterterm, anomaly, renormalization, QME, and residual-transfer claims into independently assessable obligations.",
        "compatibility": {
            "v0_result": "FOUNDATIONAL_INTERSECTION_CUBE_V0",
            "v0_unchanged": True,
            "foundation_keys_preserved": True,
            "carrier_keys_preserved": True,
            "one_to_one_obligations": [K, G, R],
            "refinement_map": REFINEMENT,
            "migration_rule": "One-to-one obligations retain their exact cell. Split obligations descend only through the explicit evidence-capability registry; otherwise they become MIGRATION_UNRESOLVED.",
        },
        "axes": [axes["FOUNDATION"], axes["CARRIER"], {"id": "REFINED_OBLIGATION", "question": "Which precise physical or theorem-level job is established?", "keys": obligation_keys}],
        "cell_statuses": [
            {"id": "LOCAL_RESULT", "meaning": "A bounded local result directly supports this refined obligation."},
            {"id": "LITERATURE_RESULT", "meaning": "A reviewed source directly treats this refined obligation within its boundary."},
            {"id": "PIECES_ONLY", "meaning": "Relevant ingredients exist but do not compose the refined result."},
            {"id": "PRIORITY_GAP", "meaning": "A one-to-one migrated obligation retains a deliberately reviewed gap."},
            {"id": "MIGRATION_UNRESOLVED", "meaning": "The overloaded v0 parent was assessed, but its evidence cannot be transferred to this child without a new review."}
        ],
        "dimensions": {
            "axis_sizes": [6, 6, len(obligation_keys)],
            "cartesian_total": 6 * 6 * len(obligation_keys),
            "migrated_or_overlaid_cells": len(cells),
            "qualified_cells": qualified,
            "migration_unresolved_cells": counts["MIGRATION_UNRESOLVED"],
            "status_counts": dict(sorted(counts.items())),
            "descendant_counts_by_v0_obligation": dict(sorted(split_counts.items())),
        },
        "cells": cells,
        "capability_registry": {
            "producer_path": "foundations/refine_intersection_cube.py",
            "registered_evidence_ids": len(CAPABILITIES),
            "digest": capability_digest(),
            "boundary": "A missing capability registration forbids descent; it is not evidence that the child claim is false."
        },
        "provenance": {"inputs": [
            {"path": str(V0.relative_to(ROOT)), "sha256": sha(V0)},
            {"path": str(CYLINDER.relative_to(ROOT)), "sha256": sha(CYLINDER)},
            {"path": str(FINITE_QUBIT.relative_to(ROOT)), "sha256": sha(FINITE_QUBIT)},
        ]},
        "independent_checker": {"path": "foundations/check_refined_intersection_cube.py", "checks": ["axis closure", "unique refined coordinates", "exact one-to-one migration", "no blind split inheritance", "overlay set", "status and evidence closure", "canonical digest"], "expected_digest": canonical_digest(cells)},
        "claim_flags": {"v0_preserved": True, "overloaded_obligations_decomposed": True, "blind_parent_status_inheritance_forbidden": True, "cylinder_ladder_integrated": True, "all_576_cells_assessed": False, "literature_complete": False, "weakest_base_proved": False, "new_lorentzian_claim": False},
        "does_not_establish": ["that every refined Cartesian coordinate is coherent", "that a v0 result supports every refined child", "literature completeness", "a weakest mathematical base", "a constructive continuum Weyl theory", "renormalized products", "QME restoration", "residual quantum transfer", "a controlled continuum limit", "a new Lorentzian-causal result"],
        "human_report": "foundations/reports/refined-intersection-cube.md",
    }


def cell(value: Any) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")


def render(result: dict[str, Any]) -> str:
    dimensions = result["dimensions"]
    axes = {axis["id"]: axis for axis in result["axes"]}
    foundation_labels = {x["id"]: x["label"] for x in axes["FOUNDATION"]["keys"]}
    obligation_labels = {x["id"]: x["label"] for x in axes["REFINED_OBLIGATION"]["keys"]}
    lines = [
        "<!-- Generated by foundations/refine_intersection_cube.py; do not edit by hand. -->",
        "# Refined foundations intersection cube",
        "",
        f"**Result:** `{result['result_id']}`",
        "",
        "## Outcome",
        "",
        f"V0 remains unchanged at 6 × 6 × 6. V1 has **6 mathematical regimes × 6 carriers × {dimensions['axis_sizes'][2]} precise obligations = {dimensions['cartesian_total']} possible coordinates**.",
        "",
        f"The migration emits **{dimensions['migrated_or_overlaid_cells']} cells**: **{dimensions['qualified_cells']} qualified** and **{dimensions['migration_unresolved_cells']} migration-unresolved**. Unresolved means the old parent evidence was not licensed to descend; it is not a scientific gap or an absence claim.",
        "",
        "## Why v1 exists",
        "",
        "V0 combined state existence with representation, probability, and physical selection. It also combined spectral dynamics with well-posed evolution and causal Green propagation, and combined a finite interaction with counterterms, anomalies, renormalized products, QME restoration, and residual transfer. Those combinations distorted rankings. V1 makes each obligation independently auditable.",
        "",
        "## Refined obligation keys",
        "",
        "| Key | Plain-language question | V0 parent |",
        "|---|---|---|",
    ]
    for parent, children in REFINEMENT.items():
        for child in children:
            label, meaning = OBLIGATION_META[child]
            lines.append(f"| **{cell(label)}** | {cell(meaning)} | `{parent}` |")
    lines += [
        "",
        "## Migration status",
        "",
        "| Status | Cells | Meaning |",
        "|---|---:|---|",
    ]
    status_meaning = {x["id"]: x["meaning"] for x in result["cell_statuses"]}
    for status, count in sorted(dimensions["status_counts"].items()):
        lines.append(f"| `{status}` | {count} | {cell(status_meaning[status])} |")
    lines += [
        "",
        "## Coverage by mathematical regime",
        "",
        "| Regime | Local | Literature | Pieces | Priority gap | Migration unresolved | Emitted |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for foundation in axes["FOUNDATION"]["keys"]:
        counts = Counter(x["status"] for x in result["cells"] if x["foundation"] == foundation["id"])
        lines.append(f"| {cell(foundation['label'])} | {counts['LOCAL_RESULT']} | {counts['LITERATURE_RESULT']} | {counts['PIECES_ONLY']} | {counts['PRIORITY_GAP']} | {counts['MIGRATION_UNRESOLVED']} | {sum(counts.values())} |")
    lines += [
        "",
        "## Three semantic corrections",
        "",
        "1. **Finite interaction is no longer finite renormalization.** The exact qubit Hamiltonian fills `INTERACTION_CONSTRUCTION`; its five quantum siblings remain independently open or unresolved.",
        "2. **Internal or spectral dynamics is no longer causal propagation.** A one-parameter group can fill `GENERATOR_SPECTRAL_DYNAMICS` without filling `CAUSAL_PROPAGATION_GREEN`.",
        "3. **A state is not a selected physical state.** Vector, density, measure, valuation, or GNS representations do not automatically fill `PHYSICAL_STATE_SELECTION`.",
        "",
        "## Cylinder-wave insertion",
        "",
        "The cylinder ladder adds exact finite generator/evolution cells, a computable-Sobolev literature result, and pieces-only weak-base/causal cells. Its antipodal Dirichlet-kernel witness is recorded as a counterexample to the method of deriving causal support from finite spectral truncation.",
        "",
        "## Selected refined cells",
        "",
        "| Regime | Carrier | Obligation | Status | Evidence | Boundary |",
        "|---|---|---|---|---|---|",
    ]
    selected = [x for x in result["cells"] if x["migration_relation"] == "REVIEWED_V1_OVERLAY"]
    carrier_labels = {x["id"]: x["label"] for x in axes["CARRIER"]["keys"]}
    for item in selected:
        lines.append(f"| {cell(foundation_labels[item['foundation']])} | {cell(carrier_labels[item['carrier']])} | {cell(obligation_labels[item['obligation']])} | `{item['status']}` | {cell(', '.join(item['evidence']))} | {cell(item['boundary'])} |")
    lines += [
        "",
        "## Reproduction",
        "",
        "```text",
        "python3 foundations/refine_intersection_cube.py --check",
        "python3 foundations/check_refined_intersection_cube.py",
        "python3 foundations/verify_refined_intersection_cube.py",
        "python3 -m unittest foundations.tests.test_refined_intersection_cube",
        "```",
        "",
        "## Boundaries",
        "",
    ]
    lines.extend(f"- This does not establish {item}." for item in result["does_not_establish"])
    return "\n".join(lines) + "\n"


def generated() -> tuple[str, str]:
    result = build()
    return json.dumps(result, indent=2, ensure_ascii=False) + "\n", render(result)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_text, report_text = generated()
    expected = ((OUTPUT, result_text), (REPORT, report_text))
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, text in expected if not path.is_file() or path.read_text() != text]
        if stale:
            print("stale generated artifacts: " + ", ".join(stale), file=sys.stderr)
            return 1
        print("FOUNDATIONAL_INTERSECTION_CUBE_V1: generated artifacts current")
        return 0
    for path, text in expected:
        path.write_text(text)
        print("wrote " + str(path.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
