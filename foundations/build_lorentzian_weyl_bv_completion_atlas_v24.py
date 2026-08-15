#!/usr/bin/env python3
"""Build Atlas V24 from V23 plus the completed minimal-BV q3 package."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V23.json"
Q3_IMPORT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_PURE_WEYL_MINIMAL_BV_Q3_IMPORT_V1.json"
ARITY3 = ROOT / "quantum-weyl/classical_import/certificates/STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.json"
CYCLICITY = ROOT / "quantum-weyl/classical_import/certificates/STRICT_MINIMAL_BV_Q3_CYCLICITY_V1.json"
CLASSICAL_Q3 = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V24.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v24.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_stabilized_q2_lift_preflight",
        "strict_gate_v7_reconciliation", "strict_q2_green_composition_preflight",
        "strict_recursive_causal_tree_domains", "strict_polarized_formal_coefficients",
        "strict_field_equation_green_quotient_inverse",
        "strict_quadratic_truncation_lambda2_source_obstruction",
        "strict_pure_weyl_q3_witness", "strict_minimal_q3_completion",
        "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def branch(value: dict[str, Any], branch_id: str) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == branch_id)


def stage(value: dict[str, Any], branch_id: str, stage_id: str) -> dict[str, Any]:
    return next(item for item in branch(value, branch_id)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text())
    q3 = json.loads(Q3_IMPORT.read_text())
    arity3 = json.loads(ARITY3.read_text())
    cyclicity = json.loads(CYCLICITY.read_text())
    classical = json.loads(CLASSICAL_Q3.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V23":
        raise ValueError("V23 predecessor drift")
    if q3.get("claim_flags", {}).get("AUTHORITATIVE_MINIMAL_BV_Q3_IMPORTED") is not True:
        raise ValueError("authoritative minimal q3 import unavailable")
    if arity3.get("claim_flags", {}).get("MINIMAL_BV_ARITY_THREE_IDENTITY_CERTIFIED") is not True:
        raise ValueError("minimal arity-three identity unavailable")
    if cyclicity.get("claim_flags", {}).get("MINIMAL_BV_Q3_CYCLICITY_CERTIFIED") is not True:
        raise ValueError("minimal q3 cyclicity unavailable")
    if classical.get("claim_flags", {}).get("AUTHORITATIVE_MINIMAL_BV_Q3_EXPORTED") is not True:
        raise ValueError("classical q3 authority chain unavailable")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v24",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V24",
        "created": "2026-08-15",
        "repository_base_commit": "0950df03e512b88436ab12212d0d9a9ac820c681",
        "question": "Does the exact cubic witness extend to the authoritative arbitrary-input minimal BV bracket, and does the complete arity-three cyclic L-infinity package close on that carrier?",
        "answer": "Atlas V24 closes the minimal-carrier cubic gate. The authoritative classical action now exports all six q3 output rows: the unique nonzero component is D^3E_g on three arbitrary metric inputs and the other five rows vanish by master-action degree. An independent exact trivariate receiver reproduces the 41-term diagonal witness, S3 symmetry, polarization, covariance and multi-background checks. The complete arity-three identity is certified on arbitrary inputs through differentiated nilpotency and an exhaustive 72-channel/212-path exact replay; quartic q3 cyclicity follows from the S4-symmetric fourth variation of the same local action modulo boundary terms. The result does not yet identify this minimal cyclic L-infinity algebra with the 386-row nonminimal graph theory. The leading route is now one explicit source-certified cyclic stabilization, followed by general lambda-squared source closure on the causal carrier.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v24.md",
    })

    projection = {
        "classical_export_result_id": classical["result_id"],
        "quantum_import_result_id": q3["result_id"],
        "arity_three_result_id": arity3["result_id"],
        "cyclicity_result_id": cyclicity["result_id"],
        "minimal_carrier_generators": 6,
        "minimal_q3_nonzero_components": 1,
        "minimal_q3_zero_output_rows": 5,
        "arbitrary_three_metric_inputs": True,
        "S3_input_permutations_replayed": q3["exact_receiver_checks"]["S3_input_permutations_replayed"],
        "diagonal_witness_terms_reproduced": q3["exact_receiver_checks"]["pinned_diagonal_witness"]["metric_output_term_count"],
        "diagonal_witness_q1_q3": q3["exact_receiver_checks"]["pinned_diagonal_witness"]["q1_q3_weyl_noether"],
        "arity_three_channels": arity3["channel_inventory"]["channel_count"],
        "arity_three_paths": arity3["channel_inventory"]["composable_path_count"],
        "arity_three_identity_on_arbitrary_inputs": True,
        "quartic_cyclicity_mod_d": True,
        "quartic_permutation_group": cyclicity["cyclic_four_form"]["permutation_group"],
        "strict_386_q3_stabilized": False,
        "strict_386_authoritative_nonminimal_equivalence": False,
        "strict_386_general_lambda2_source_closed": False,
        "classical_import_gate_a_passed": False,
        "foundational_classification": arity3["foundational_strength"]["classification"],
        "next_gate": cyclicity["next_gate"],
    }
    value["strict_minimal_q3_completion"] = projection

    nonlinear = stage(value, "STRICT_PURE_WEYL_386", "S3_NONLINEAR_CARTAN")
    nonlinear.update({
        "status": "PARTIAL_CERTIFIED_WITH_COMPLETE_MINIMAL_Q3_ARITY_AND_CYCLICITY",
        "statement": "The authoritative arbitrary-input minimal q3 is imported on all six output rows. Its full arity-three identity holds on 72 typed channels and 212 composable paths, and its quartic metric vertex is S4-cyclic modulo boundary terms. The 386-row cyclic stabilization, authoritative nonminimal theory identity, and general source closure remain open.",
        "evidence": list(dict.fromkeys([*nonlinear["evidence"], classical["result_id"], q3["result_id"], arity3["result_id"], cyclicity["result_id"]])),
        "boundary": "This closes the minimal local cubic L-infinity package only. It does not identify the trivial 356-row stabilization with the authoritative nonminimal classical theory, certify q3/Green compatibility, or pass Gate A.",
    })
    strict = branch(value, "STRICT_PURE_WEYL_386")
    strict["next_decisive_object"] = "Construct and source-certify one cyclic stabilization or L-infinity equivalence carrying the accepted minimal q1/q2/q3 and pairing to all 386 rows, then replay general lambda-squared source closure."
    value["frontier_summary"]["strict_nonlinear_causal_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "stage": "S3_NONLINEAR_CARTAN",
        "current_fact": "The complete authoritative minimal q3, arbitrary-input arity-three identity, and quartic cyclicity are certified; the prior diagonal cancellation is now a regression of the general bracket.",
        "best_next_object": "A content-addressed cyclic stabilization or source-certified L-infinity equivalence from the six-generator minimal complex to the 386-row graph carrier.",
        "falsification_target": "The transported q3 must preserve the 72-channel/212-path arity-three identity and S4 cyclic form, reproduce -75760/9, and close the general lambda-squared Noether source before any Green action.",
        "foundational_boundary": "The completed minimal package is LOCAL-ALGEBRAIC: finite exact ledgers plus smooth natural variational calculus. The later Green and Hadamard layers remain distinct analytic commitments.",
    }

    routes = [
        ("STRICT_ARITY_THREE_386_CYCLIC_STABILIZATION", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Transport q1, q2, q3 and the canonical pairing through an explicit 386-row BV-canonical stabilization and replay arity three."),
        ("STRICT_NONMINIMAL_THEORY_IDENTITY", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "HIGH", "Obtain a source-certified full nonminimal export or cyclic L-infinity equivalence identifying the stabilization with the intended classical theory."),
        ("STRICT_LAMBDA2_GENERAL_SOURCE_COCYCLE_CLOSURE", "STRICT_PURE_WEYL_386", "VERY_HIGH", "HIGH", "HIGH", "After stabilization, replay N S2=0 for arbitrary q1-closed inputs before applying a Green operator."),
        ("STRICT_RESIDUAL_SDR_COMMON_CARRIER", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "HIGH", "Extend or reconstruct iota_cl, pi_cl and s_cl beyond the D-finite control and replay every common-carrier identity."),
        ("STRICT_FULL_CYCLIC_PAIRING", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Bind the full pairing/sign convention to every nonminimal, auxiliary and residual row."),
        ("STRICT_RESIDUAL_EXACT_PAYLOAD", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Serialize ordered primal/dual modes, exact SO(4,2) constants and representation matrices."),
        ("DIRECT_SPACETIME_Q26_HADAMARD", "BERGER_POSITIVE_CLOCK_54", "VERY_HIGH", "LOW", "MEDIUM", "Keep the analytically mature Berger Hadamard route as a different-theory control, not as the strict pure-Weyl carrier map."),
        ("STRICT_D_CARTAN_AND_CHARGE_DECISION", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Classify the nonlinear D-Cartan homotopy and proper-gauge/charge status on the strict carrier."),
        ("STRICT_ANALYTIC_MOLLER_CONVERGENCE", "STRICT_PURE_WEYL_386", "MEDIUM", "LOW", "HIGH", "Only after all-order source closure, derive seminorm majorants and a nonzero convergence domain."),
        ("STRICT_MIXED_WEIGHTED_CAUSAL_DOMAIN", "STRICT_PURE_WEYL_386", "MEDIUM", "MEDIUM", "MEDIUM", "Test weighted opposite-polarity domains against the scalar zero-mode witness; polarized recursion does not require this."),
        ("STRICT_GREEN_FOUNDATIONAL_CALIBRATION", "STRICT_PURE_WEYL_386", "MEDIUM", "MEDIUM", "MEDIUM", "Calibrate the weakest reverse-mathematical and choice principles behind the PC/FC Green extensions and formal sequence coding."),
    ]
    value["route_selection"] = [
        {"rank": rank, "route": route, "branch": branch_id, "scientific_leverage": leverage, "tractability": tractability, "dependency_depth": depth, "recommendation": recommendation}
        for rank, (route, branch_id, leverage, tractability, depth, recommendation) in enumerate(routes, 1)
    ]
    value["research_queue"] = [
        {"priority": item["rank"], "branch": item["branch"], "object": item["route"], "why": item["recommendation"]}
        for item in value["route_selection"]
    ]
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V23 atlas predecessor"},
        {"path": str(CLASSICAL_Q3.relative_to(ROOT)), "sha256": sha(CLASSICAL_Q3), "role": "authoritative action-derived minimal q3 export"},
        {"path": str(Q3_IMPORT.relative_to(ROOT)), "sha256": sha(Q3_IMPORT), "role": "independent arbitrary-input minimal q3 import"},
        {"path": str(ARITY3.relative_to(ROOT)), "sha256": sha(ARITY3), "role": "exhaustive minimal arity-three identity"},
        {"path": str(CYCLICITY.relative_to(ROOT)), "sha256": sha(CYCLICITY), "role": "minimal q3 quartic cyclicity"},
    ]
    value["claim_flags"].update({
        "v23_preserved": True,
        "strict_authoritative_minimal_q3_imported": True,
        "strict_minimal_arbitrary_input_q3_certified": True,
        "strict_minimal_full_bv_arity_three_identity_certified": True,
        "strict_minimal_q3_cyclicity_certified": True,
        "strict_386_authoritative_q3_imported": False,
        "strict_386_q3_stabilized": False,
        "strict_386_full_bv_arity_three_identity_certified": False,
        "strict_386_general_full_weyl_lambda2_source_closure_certified": False,
        "strict_386_authoritative_formal_moller_map_certified": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "strict_386_full_bv_hadamard_state_constructed": False,
        "strict_pure_weyl_qme_restored": False,
        "lorentzian_full_theory_certified": False,
    })
    obsolete = "an authoritative arbitrary-input pure-Weyl q3 or complete full-BV arity-three identity"
    value["does_not_establish"] = [item for item in previous["does_not_establish"] if item != obsolete]
    value["does_not_establish"] = list(dict.fromkeys([
        *value["does_not_establish"],
        "a source-certified cyclic stabilization or L-infinity equivalence from the minimal carrier to all 386 graph rows",
        "the authoritative nonminimal/auxiliary interaction theory from the mathematically valid trivial stabilization alone",
        "the 386-row arity-three identity or general lambda-squared source closure from the completed minimal package",
        "q3 compatibility with a causal Green homotopy, an analytic Moller map, Hadamard data, or QME restoration",
    ]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v24.py",
        "checks": [
            "V23 predecessor and all 77 cells preserved except the strict nonlinear stage",
            "authoritative six-row arbitrary-input q3 import projection",
            "72-channel/212-path arity-three identity projection",
            "S4 quartic cyclicity modulo-boundary result-kind boundary",
            "minimal completion versus 386-row stabilization firewall",
            "eleven-route deterministic queue",
            "Gate-A/Hadamard/QME lifecycle firewalls",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    p = value["strict_minimal_q3_completion"]
    lines = [
        "# Lorentzian Weyl BV completion atlas v24", "", "## Outcome", "", value["answer"], "",
        "## Minimal cubic completion", "",
        f"- Classical export / independent import: `{p['classical_export_result_id']}` / `{p['quantum_import_result_id']}`.",
        f"- q3 support: **{p['minimal_q3_nonzero_components']} nonzero / {p['minimal_q3_zero_output_rows']} zero output rows**.",
        f"- Arbitrary inputs / S3 permutations: **{p['arbitrary_three_metric_inputs']} / {p['S3_input_permutations_replayed']}**.",
        f"- Diagonal regression: **{p['diagonal_witness_terms_reproduced']} terms; q1 q3={p['diagonal_witness_q1_q3']}**.",
        f"- Arity-three coverage: **{p['arity_three_channels']} channels / {p['arity_three_paths']} paths**.",
        f"- Quartic cyclicity: **{p['quartic_permutation_group']} symmetric modulo d**.",
        f"- 386 stabilization / general source closure: **{p['strict_386_q3_stabilized']} / {p['strict_386_general_lambda2_source_closed']}**.", "",
        "## Ranked next routes", "", "| Rank | Route | Branch | Leverage | Tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(f"| {item['rank']} | `{item['route']}` | `{item['branch']}` | {item['scientific_leverage']} | {item['tractability']} |" for item in value["route_selection"])
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v24.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v24.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v24.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v24.py", "```", "", "## Boundaries", ""]
    lines.extend(f"- This does not establish {item}." for item in value["does_not_establish"])
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, report = generated()
    stale = [str(path.relative_to(ROOT)) for path, content in ((RESULT, result), (REPORT, report)) if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V24: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V24: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
