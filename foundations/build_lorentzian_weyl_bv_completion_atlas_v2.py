#!/usr/bin/env python3
"""Build completion-atlas V2 from V1 plus the resolved Gate-A/C26 evidence chain."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V2.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v2.md"

NEW_INPUTS = [
    ("quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V2_RECONCILIATION.json", "replacement Gate-A reconciliation"),
    ("quantum-weyl/lorentzian/certificates/BERGER_HOMOGENEOUS_STATIONARY_HADAMARD_NORMALIZATION_OBSTRUCTION.json", "stationary normalization no-go"),
    ("quantum-weyl/lorentzian/certificates/BERGER_C26_BIKERNEL_SUPPORT_PROFILE_NONDEFINITION.json", "unserialized Ward-remainder boundary"),
    ("d_quotient_classical/certificates/BERGER_Q26_CAUCHY_BV_CARRIER_OBSTRUCTION_V1.json", "frozen Cauchy-graph obstruction"),
    ("d_quotient_classical/certificates/BERGER_Q26_MINIMAL_SIX_ROW_CYCLIC_OBSTRUCTION_V1.json", "six-row cyclic obstruction"),
    ("d_quotient_classical/certificates/BERGER_Q26_FINITE_ROW_MODULE_CLOSURE_LOWER_BOUND_V1.json", "104-new-row free-module lower bound"),
    ("d_quotient_classical/certificates/BERGER_Q26_104_ROW_CANONICAL_CONE_LIFT_OBSTRUCTION_V1.json", "canonical doubled-cone obstruction"),
    ("d_quotient_classical/certificates/BERGER_Q26_104_ROW_CONE_NEXT_DEFECT_MODULE_V1.json", "canonical cone next-defect closure"),
    ("d_quotient_classical/certificates/BERGER_Q26_104_ROW_FULLY_MIXED_CONE_SDR_OBSTRUCTION_V1.json", "fully mixed cone SDR obstruction"),
    ("d_quotient_classical/certificates/BERGER_Q26_104_ROW_NONCONE_RATIONAL_NILPOTENCE_FEASIBILITY_V1.json", "non-cone nilpotence feasibility control"),
    ("d_quotient_classical/certificates/BERGER_Q26_104_ROW_NONCONE_EVOLUTION_EXTENSION_OBSTRUCTION_V1.json", "fixed non-cone evolution obstruction"),
    ("d_quotient_classical/certificates/BERGER_Q26_104_ROW_MIXED_EVOLUTION_CORRECTION_ENDPOINT_OBSTRUCTION_V1.json", "mixed-correction rank obstruction"),
]

CHAIN_PATHS = [path for path, _ in NEW_INPUTS[1:]]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text())


def branch(value: dict[str, Any], branch_id: str) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == branch_id)


def cell(route: dict[str, Any], stage: str) -> dict[str, Any]:
    return next(item for item in route["stages"] if item["stage"] == stage)


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "berger_h26_c26_decision_chain", "route_selection", "research_queue",
    )
    payload = {key: value[key] for key in keys}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V1":
        raise ValueError("completion-atlas predecessor drift")
    gate = load(NEW_INPUTS[0][0])
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V2_RECONCILIATION":
        raise ValueError("Gate-A V2 reconciliation missing")
    if gate["gate_disposition"]["gate_a_status"] != "FAIL_CLOSED":
        raise ValueError("Gate A was silently promoted")

    evidence = {load(path)["result_id"]: load(path) for path in CHAIN_PATHS}
    expected_states = [
        "FULL_RETAINED_STATIONARY_COMPLEX_STRUCTURE_CLASS_OBSTRUCTED_ON_POSITIVE_HOMOGENEOUS_FIXTURE",
        "C26_SYMBOLIC_SMOOTHNESS_CERTIFIED_SUPPORT_AND_PAIRING_NULL_UNDEFINED_UNTIL_NORMALIZED_H26_IS_SERIALIZED",
        "FROZEN_104_ROW_FORMAL_CAUCHY_GRAPH_LIFT_CLASS_EMPTY",
        "EXACT_SIX_ROW_EXTENSION_HAS_UNAVOIDABLE_FOUR_DIMENSIONAL_PAIRING_RADICAL",
        "DEFECT_AND_FREE_DUAL_MODULE_CLOSURE_FORCES_AT_LEAST_104_ADDED_ROWS",
        "CANONICAL_104_ROW_DOUBLED_CONE_EVOLUTION_LIFT_AND_FREE_ADJOINT_ORIENTATION_EMPTY",
        "CANONICAL_CONE_LIFT_DEFECT_REGENERATES_FULL_104_ROW_FREE_ORBIT",
        "FULLY_MIXED_CONE_EVOLUTION_EXISTS_BUT_RETAINED_SDR_IS_COHOMOLOGICALLY_OBSTRUCTED",
        "RATIONAL_TRIVIAL_REPRESENTATION_NONCONE_NILPOTENCE_AND_RETAINED_COHOMOLOGY_FEASIBLE",
        "EXACT_RATIONAL_BOUNDARY_COKERNEL_OBSTRUCTS_A104_CHAIN_EXTENSION_ON_THE_NONCONE_FEASIBILITY_WITNESS",
        "RATIONAL_FULLY_MIXED_CORRECTION_ANSATZ_MISSES_REQUIRED_LEFT_ENDPOINT_RANK",
    ]
    ordered = [load(path) for path in CHAIN_PATHS]
    if [item.get("result_state") for item in ordered] != expected_states:
        raise ValueError("Berger H26/C26 decision chain drift")

    branches = deepcopy(previous["branches"])
    strict = branch({"branches": branches}, "STRICT_PURE_WEYL_386")
    strict_s0 = cell(strict, "S0_CLASSICAL_AUTHORITY")
    strict_s0.update({
        "status": "FAIL_CLOSED",
        "statement": "Standalone replay is repaired and the historical twenty-export/ten-identity gate is reconciled into six missing payload families, but no common strict pure-Weyl snapshot passes Gate A.",
        "evidence": ["CLASSICAL_IMPORT_GATE_V2_RECONCILIATION"],
        "boundary": "Five same-theory scoped repairs and exact neighboring-theory controls do not supply the three missing residual maps or the common full snapshot.",
    })
    strict["next_decisive_object"] = (
        "First serialize the strict residual SDR iota_cl, pi_cl and s_cl on one ordered carrier, "
        "then produce strict support-local q2 and D. These are target-theory gates and must not "
        "be filled by the auxiliary retract, causal Green homotopy or Berger tensors."
    )

    berger = branch({"branches": branches}, "BERGER_POSITIVE_CLOCK_54")
    cell(berger, "S4_HADAMARD_CCR").update({
        "status": "PARTIAL_CERTIFIED",
        "statement": "All endpoint factors and the exact CCR candidate exist, but the real stationary full-carrier normalization class is empty and no content-addressed nonstationary H26_plus is constructed.",
        "evidence": [
            "BERGER_RETAINED26_HADAMARD_WARD_REDUCTION",
            "BERGER_HOMOGENEOUS_STATIONARY_HADAMARD_NORMALIZATION_OBSTRUCTION",
            "BERGER_C26_BIKERNEL_SUPPORT_PROFILE_NONDEFINITION",
        ],
        "boundary": "This is a candidate-plus-scoped-no-go, not a normalized BRST Hadamard covariance and not a no-go for every nonstationary Krein representative.",
    })
    cell(berger, "S5_BRST_WARD").update({
        "status": "OBSTRUCTED_SCOPED",
        "statement": "The smooth Ward defect is not serialized. The frozen 104-row Cauchy graph, every exactly six-row cyclic repair, canonical cone lifts, a fully mixed cone SDR and two fixed non-cone correction families are exactly obstructed; free-module closure forces at least 104 added rows.",
        "evidence": [item["result_id"] for item in ordered[1:]],
        "boundary": "These theorems do not obstruct the complete general non-cone 104-row class, non-free/projective carriers, alternative companions or a direct spacetime q26-equivariant Hadamard selection.",
    })
    berger["first_unclosed_gate"] = "S4_HADAMARD_CCR"
    berger["next_decisive_object"] = (
        "Choose between two explicitly different high-risk routes: solve the complete non-cone "
        "104-new-row simultaneous nilpotence/evolution/cyclic/SDR system with a characteristic-zero "
        "certificate, or bypass the rejected stationary Cauchy graph by constructing a direct "
        "spacetime q26-equivariant nonstationary Hadamard representative."
    )

    chain = []
    implications = [
        ("STATIONARY_NORMALIZATION_EMPTY", "No real stationary compatible complex structure exists on the full homogeneous retained carrier.", "Nonstationary Krein representatives remain open."),
        ("REPRESENTATIVE_NOT_SERIALIZED", "C26 support and pairing-null predicates are undefined without a fixed H26_plus.", "Undefined support is not a support no-go."),
        ("FROZEN_CAUCHY_GRAPH_EMPTY", "The normalized frozen 104-row solution graph cannot carry the required q_Cauchy.", "Alternative companions and enlarged carriers remain open."),
        ("SIX_ROW_CYCLIC_EMPTY", "The first factorization-size repair has an unavoidable four-dimensional pairing radical.", "Ten or more rows, or noncyclic carriers, remain open."),
        ("FREE_MODULE_BOUND_104", "Defect/free-dual closure fills the 936-dimensional spin-four representation and requires at least 104 added free rows.", "The bound is not a construction and does not cover non-free/projective modules."),
        ("CANONICAL_CONE_EMPTY", "The rank-saturating doubled cone is nilpotent but has no accepted evolution/free-adjoint lift.", "General non-cone 104-row completions remain open."),
        ("CANONICAL_TOWER_REGENERATES", "The canonical cone's next defect regenerates a full free orbit and forces another 104 rows in that architecture.", "The global lower bound remains 104, not 208."),
        ("FULLY_MIXED_CONE_SDR_EMPTY", "A fully mixed cone can be nilpotent and evolution compatible but has the wrong cohomology for a retained SDR.", "General non-cone carriers with cohomology imposed from the start remain open."),
        ("RANK_ONLY_FEASIBLE", "An exact rational non-cone matrix has nilpotence and the correct cohomology ranks.", "It is not a PBW operator, evolution lift, cyclic carrier or SDR."),
        ("FIXED_NONCONE_EVOLUTION_EMPTY", "The selected non-cone feasibility witness has an exact boundary cokernel obstructing its A104 chain extension.", "Other simultaneous non-cone differentials remain open."),
        ("MIXED_CORRECTION_RANK_MISS", "The declared mixed correction ansatz has endpoint rank 22 or 24 where rank 23 is required.", "The complete two-free-differential non-cone class remains open."),
    ]
    for index, (item, (classification, implication, boundary)) in enumerate(zip(ordered, implications), 1):
        chain.append({
            "sequence": index,
            "classification": classification,
            "result_id": item["result_id"],
            "result_state": item["result_state"],
            "implication": implication,
            "does_not_imply": boundary,
            "evidence": item["result_id"],
        })

    old_inputs = previous["provenance"]["inputs"]
    roles = {item["path"]: item["role"] for item in old_inputs}
    for path, role in NEW_INPUTS:
        roles[path] = role
    roles[str(PREDECESSOR.relative_to(ROOT))] = "immutable V1 predecessor"
    inputs = [
        {"path": path, "sha256": sha(ROOT / path), "role": role}
        for path, role in sorted(roles.items())
    ]

    value: dict[str, Any] = {
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v2",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V2",
        "result_kind": "BRANCH_BY_STAGE_COMPLETION_ATLAS",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "repository_base_commit": "940f680da46eb1d4ebecf210472ee2192e90bccc",
        "dependency_tags": previous["dependency_tags"],
        "question": "After repairing standalone classical-import replay and incorporating the complete Berger H26/C26 Cauchy-carrier decision chain, which Lorentzian Weyl BV architectures are strongest, what is actually blocked, and which next exact constructions are both scientifically decisive and tractable?",
        "answer": "Strict pure Weyl remains the theory-identity front: its 386-row scoped causal homotopy is real, standalone provenance now replays, and Gate A is reduced to six explicit missing payload families, but the common authoritative snapshot still fails closed. Berger remains the analytic-maturity front through complete 54-row causal propagation and cyclic D-Cartan closure through arity three. Its apparent short path from an exact-CCR candidate to BRST Hadamard data has, however, split into a substantial decision chain dominated by scoped obstructions. Stationary normalization is empty; the frozen Cauchy graph fails; six-row cyclic repair is impossible; free-module closure requires at least 104 added rows; and several canonical cone and fixed non-cone 104-row families fail. A rational non-cone rank-feasibility control also proves that nilpotence and cohomology ranks alone are not a global obstruction. None of these scoped results is a theorem against the complete general non-cone class, non-free carriers, alternative companions or a direct spacetime q26-equivariant selection. The best near-term target-theory task is therefore the strict residual-SDR payload, while the best high-risk analytic experiment is a direct nonstationary q26-equivariant Hadamard selection. A general 104-row completion remains important but tooling-heavy and is no longer described as low-hanging fruit.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "status_vocabulary": previous["status_vocabulary"],
        "stages": previous["stages"],
        "branches": branches,
        "frontier_summary": {
            "theory_identity_front": {"branch": "STRICT_PURE_WEYL_386", "first_gate": "S0_CLASSICAL_AUTHORITY", "current_fact": "Gate A is partially repaired and replayable but still lacks one common strict snapshot.", "best_next_object": "M3 residual iota_cl/pi_cl/s_cl payload, followed by M2 strict q2/D."},
            "analytic_maturity_front": {"branch": "BERGER_POSITIVE_CLOCK_54", "first_gate": "S4_HADAMARD_CCR", "current_fact": "Causal and arity-three classical control is strongest, while normalized BRST Hadamard completion has an 11-step scoped decision chain dominated by obstructions and containing one exact feasibility control.", "best_next_object": "Direct spacetime nonstationary q26-equivariant selection or the complete general non-cone 104-row system."},
            "curved_generality_front": previous["frontier_summary"]["curved_generality_front"],
            "state_control_front": previous["frontier_summary"]["state_control_front"],
        },
        "classical_import_reconciliation": {
            "result_id": gate["result_id"],
            "gate": gate["gate_disposition"]["gate_a_status"],
            "claim_state": gate["gate_disposition"]["claim_state"],
            "standalone_history_replay": gate["standalone_history_replay"]["status"],
            "missing_payload_families": [item["id"] for item in gate["minimal_missing_bundle"]],
            "rule": gate["gate_disposition"]["rule"],
        },
        "berger_h26_c26_decision_chain": chain,
        "route_selection": [
            {"rank": 1, "route": "STRICT_RESIDUAL_SDR", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "MEDIUM", "dependency_depth": "LOW", "recommendation": "Serialize exact iota_cl, pi_cl and s_cl on one ordered authoritative carrier and replay the four residual identities."},
            {"rank": 2, "route": "DIRECT_SPACETIME_Q26_HADAMARD", "branch": "BERGER_POSITIVE_CLOCK_54", "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "MEDIUM", "recommendation": "Attempt a direct nonstationary q26-equivariant global distributional selection without reusing the rejected stationary A104 graph."},
            {"rank": 3, "route": "STRICT_SUPPORT_LOCAL_Q2_D", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "MEDIUM", "recommendation": "Export the target-action support-local q2 and D on the common full carrier; do not import Berger coefficients."},
            {"rank": 4, "route": "BACH_FLAT_NONLINEAR_CARTAN", "branch": "PURE_WEYL_BACH_FLAT_RANK310", "scientific_leverage": "HIGH", "tractability": "MEDIUM", "dependency_depth": "MEDIUM", "recommendation": "Test same-carrier nonlinear cyclic compatibility on the broadest curved causal strict branch."},
            {"rank": 5, "route": "GENERAL_NONCONE_104_COMPLETION", "branch": "BERGER_POSITIVE_CLOCK_54", "scientific_leverage": "HIGH", "tractability": "VERY_LOW", "dependency_depth": "HIGH", "recommendation": "Resume only with a characteristic-zero simultaneous two-free-differential/cyclic/SDR solver; architecture-specific failures are controls, not a global no-go."},
        ],
        "research_queue": [
            {"priority": 1, "branch": "STRICT_PURE_WEYL_386", "object": "M3 residual SDR exact payload", "why": "It is the smallest high-leverage target-theory object and unlocks four of the five blocked common-snapshot identities without changing the action."},
            {"priority": 2, "branch": "BERGER_POSITIVE_CLOCK_54", "object": "direct spacetime q26-equivariant nonstationary Hadamard selection", "why": "It tests whether the Ward problem can be solved without committing to the now heavily obstructed stationary Cauchy-graph completion route."},
            {"priority": 3, "branch": "STRICT_PURE_WEYL_386", "object": "M2 support-local strict q2 and D", "why": "It closes the irreducible interaction-side deficit in the authoritative target theory and separates strict coefficients from the Berger control."},
            {"priority": 4, "branch": "PURE_WEYL_BACH_FLAT_RANK310", "object": "same-carrier nonlinear cyclic D-Cartan transfer", "why": "It is the cleanest medium-tractability test of whether curved strict causal control survives nonlinear compatibility."},
            {"priority": 5, "branch": "BERGER_POSITIVE_CLOCK_54", "object": "complete general non-cone 104-row completion", "why": "It remains mathematically decisive but should wait for the exact simultaneous solver required to make a completeness claim rather than another bounded ansatz obstruction."},
        ],
        "provenance": {"inputs": inputs},
        "claim_flags": {
            "v1_preserved": True,
            "standalone_classical_import_replay_recorded": True,
            "berger_h26_c26_decision_chain_classified": True,
            "general_noncone_104_row_no_go": False,
            "berger_brst_hadamard_state_constructed": False,
            "strict_pure_weyl_classical_gate_passed": False,
            "renormalized_lorentzian_products_constructed": False,
            "strict_pure_weyl_qme_restored": False,
            "residual_quantum_transfer_authorized": False,
            "lorentzian_full_theory_certified": False,
        },
        "does_not_establish": [
            "a passed strict pure-Weyl classical import gate",
            "a no-go theorem for every nonstationary Krein Hadamard representative",
            "a no-go theorem for the complete general non-cone 104-row completion class",
            "a no-finite-carrier theorem or a global lower bound above 104 added free rows",
            "that non-free or projective carrier extensions obey the free-module lower bound",
            "a normalized Berger H26_plus or serialized C26",
            "a BRST-compatible Hadamard state on a complete off-shell carrier",
            "physical positivity, particles, scattering or unitarity",
            "renormalized Lorentzian time-ordered products",
            "a Lorentzian QME theorem or residual quantum transfer",
            "equivalence between strict pure Weyl and the positive-clock Berger theory",
            "that a numerical route rank is a theorem or proof of eventual success",
        ],
        "independent_checker": {
            "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v2.py",
            "checks": ["V1 preservation", "seven-by-eleven stage closure", "Gate-A fail-closed firewall", "ordered eleven-step Berger decision chain", "scoped-no-go firewall", "route ranking identity", "content hashes", "canonical digest"],
            "expected_digest": "",
        },
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v2.md",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    lines = [
        "# Lorentzian Weyl BV completion atlas V2", "", "## Outcome", "", value["answer"], "",
        "## What changed from V1", "",
        "- Standalone classical-import replay is repaired, but Gate A remains fail-closed with six named payload families.",
        "- Berger's first unclosed gate moves from the Ward correction to the normalized Hadamard/CCR representative itself.",
        "- The C26 route is now an eleven-step scoped decision chain, not a single open cell; one step is a positive rank-feasibility control and must not be called a no-go.",
        "- Architecture-specific failures are separated from the still-open complete general non-cone class.", "",
        "## Branch-by-stage overview", "", "| branch | first unclosed gate | next decisive object |", "|---|---|---|",
    ]
    for route in value["branches"]:
        lines.append(f"| `{route['id']}` | `{route['first_unclosed_gate']}` | {route['next_decisive_object']} |")
    lines += ["", "## Berger H26/C26 decision chain", "", "| # | classification | established | does not imply |", "|---:|---|---|---|"]
    for item in value["berger_h26_c26_decision_chain"]:
        lines.append(f"| {item['sequence']} | `{item['classification']}` | {item['implication']} | {item['does_not_imply']} |")
    lines += ["", "## Route selection", "", "| rank | route | leverage | tractability | dependency depth | recommendation |", "|---:|---|---|---|---|---|"]
    for item in value["route_selection"]:
        lines.append(f"| {item['rank']} | `{item['route']}` | {item['scientific_leverage']} | {item['tractability']} | {item['dependency_depth']} | {item['recommendation']} |")
    lines += ["", "## Interpretation", "", "The rank is a programme decision aid, not a theorem. Rank 1 is the best near-term target-theory task; rank 2 is the most decisive high-risk analytic experiment. The 104-row route is retained, but its low tractability and solver dependency are made visible rather than hidden behind the phrase ‘open but seeded’.", "", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v2.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v2.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v2.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v2.py", "```", "", "## Boundaries", ""]
    lines += [f"- This does not establish {item}." for item in value["does_not_establish"]]
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    outputs = ((RESULT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V2: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V2: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
