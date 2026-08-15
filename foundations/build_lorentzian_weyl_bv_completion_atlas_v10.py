#!/usr/bin/env python3
"""Build atlas V10 from V9 plus the certified auxiliary-q sign repair."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V9.json"
REPAIR = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V10.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v10.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_causal_sign_transport",
        "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge",
        "strict_component_pairing_serialization", "strict_operator_portability",
        "strict_full_q1_split_sign_gate", "strict_auxiliary_q_sign_repair",
        "berger_h26_c26_decision_chain", "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def strict_branch(value: dict[str, Any]) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == "STRICT_PURE_WEYL_386")


def stage(value: dict[str, Any], stage_id: str) -> dict[str, Any]:
    return next(item for item in strict_branch(value)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous, repair = json.loads(PREDECESSOR.read_text()), json.loads(REPAIR.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V9":
        raise ValueError("V9 predecessor drift")
    if repair.get("result_id") != "STRICT_386_AUXILIARY_Q_SIGN_REPAIR_V1":
        raise ValueError("repair dependency drift")
    flags = repair["claim_flags"]
    if not all(flags[key] for key in ("STRICT_386_AUXILIARY_Q_SIGN_REPAIR_APPLIED", "STRICT_386_AUXILIARY_Q_SOURCE_LEDGER_PAIRING_CONSISTENT", "AFFECTED_CLASSICAL_CERTIFICATE_CHAIN_VERIFIED", "FULL_CLASSICAL_COVARIANT_SUITE_PASSED")):
        raise ValueError("repair positive flags drift")
    if flags["STRICT_FULL_386_Q1_PORTABLE_COMPONENT_BYTES"] or flags["CLASSICAL_IMPORT_GATE_PASSED"]:
        raise ValueError("full-q1/import promotion drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v10",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V10",
        "created": "2026-08-15",
        "repository_base_commit": "d0f09db4d46aa5a8198ef452f68443cf7380009f",
        "question": "After the exact four-row auxiliary cotangent sign conflict was isolated in atlas V9, has the preferred repair been applied consistently enough to reopen the strict 386-row full-q1 serialization route, and which acceptance boundary remains before the quantum programme may import a common classical snapshot?",
        "answer": "Atlas V10 certifies the preferred local repair identified by V9. The factorized auxiliary cotangent arrow, generalized and universal split ledgers, vector contraction, current comparison and all regenerated downstream certificates now use v_star to plus eta_star, agreeing with the executable 36-row matrix and the fixed exact odd pairing. Independent rational replay gives zero q-squared and zero cyclicity defects for the repaired plus sign, while the deliberately reconstructed minus-sign regression remains nilpotent but produces the same eight cyclicity defects diagnosed by V9. The scoped retract, vector, current, direct-pairing, dependency and final-transport rails pass, and an uninterrupted full covariant rebuild completed in 1433.50 seconds with all 82 terminal overclaim guards passing. The rebuild also exposed and repaired a deterministic orchestration bug: the canonical runner now regenerates the SHA-bound direct-pairing receipt after its prolonged-current input. This closes the source/ledger inconsistency without rewriting the historical V9 diagnosis. It does not yet close strict Gate A: the full endpoint, repaired auxiliary and curvature-cone q1 blocks have not been emitted as one receiver-readable sparse 386-row table, independently replayed against the rank-386 pairing, and bound into one accepted import snapshot. Full q1 serialization is therefore the highest-leverage next object. Support-local SDR maps, represented endpoint and full Green actions, local D, q2 compatibility, Hadamard construction, Ward identities, renormalized Lorentzian products, QME restoration and residual quantum transfer remain fail closed.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v10.md",
    })
    stage(value, "S0_CLASSICAL_AUTHORITY").update({
        "status": "FAIL_CLOSED",
        "statement": "The four-row auxiliary q1 sign conflict is repaired: source, ledgers, exact pairing replay and the complete affected classical chain agree on +I4, and the full covariant suite passes. Gate A remains closed only because a receiver-readable full 386-row q1 table and accepted common snapshot hash are not yet emitted.",
        "evidence": [*stage(value, "S0_CLASSICAL_AUTHORITY")["evidence"], repair["result_id"]],
        "boundary": "The repair certificate does not itself serialize the endpoint, auxiliary and curvature-cone blocks as one full q1 artifact or accept them into the quantum import manifest. Local SDR maps, Green actions, local D, q2 and quantum lifecycle stages remain open.",
    })
    strict_branch(value)["next_decisive_object"] = "Emit a canonical sparse 386-row q1 table on the published paired carrier, independently replay q1 squared and odd-pairing cyclicity on every block, and bind the accepted bytes into one classical import snapshot."
    value["frontier_summary"]["theory_identity_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "first_gate": "S0_CLASSICAL_AUTHORITY",
        "current_fact": "The auxiliary source/ledger inconsistency is repaired and the entire affected classical chain passes; only the combined receiver-readable q1 artifact and accepted snapshot binding remain at Gate A.",
        "best_next_object": "A canonical sparse full-386 q1 table with independent all-row nilpotency and odd-pairing replay.",
    }
    value["strict_auxiliary_q_sign_repair"] = {
        "result_id": repair["result_id"],
        "status": repair["result_state"],
        "block": repair["repair"]["block"],
        "old_declared_sign": repair["repair"]["old_declared_sign"],
        "authoritative_sign": repair["repair"]["authoritative_sign"],
        "repair_applied": repair["repair"]["repair_applied"],
        "source_and_ledgers_consistent": repair["repair"]["source_and_ledgers_consistent"],
        "affected_chain_regenerated": repair["repair"]["affected_chain_regenerated"],
        "plus_cyclicity_defects": repair["exact_replay"]["repaired_plus_sign"]["odd_pairing_cyclicity_defects"],
        "minus_regression_cyclicity_defects": repair["exact_replay"]["rejected_minus_sign_regression"]["odd_pairing_cyclicity_defects"],
        "tier_3_status": repair["verification"]["tier_3"]["status"],
        "tier_3_elapsed_seconds": repair["verification"]["tier_3"]["elapsed_seconds"],
        "terminal_overclaim_guards": 82,
        "full_q1_serialized": flags["STRICT_FULL_386_Q1_PORTABLE_COMPONENT_BYTES"],
        "classical_import_gate_passed": flags["CLASSICAL_IMPORT_GATE_PASSED"],
        "next_gate": repair["next_gate"],
    }
    value["strict_gate_a_progress"].update({
        "status": "AUXILIARY_Q_SIGN_REPAIRED_FULL_Q1_REQUIRED",
        "auxiliary_q_sign_repair_control": value["strict_auxiliary_q_sign_repair"],
        "remaining_common_carrier": repair["next_gate"],
        "boundary": "The repair and full classical rebuild pass, but Gate A still requires the combined full-q1 bytes and one receiver-accepted content-addressed snapshot.",
    })
    routes = [
        ("STRICT_386_FULL_Q1_JET_TABLE", "STRICT_PURE_WEYL_386", "VERY_HIGH", "HIGH", "LOW", "Emit endpoint, repaired auxiliary and curvature mapping-cylinder blocks as one canonical sparse 386-row q1 table and independently replay q1 squared and odd-pairing cyclicity."),
        ("STRICT_386_ACCEPTED_COMMON_SNAPSHOT", "STRICT_PURE_WEYL_386", "VERY_HIGH", "HIGH", "LOW", "Bind the verified full-q1 bytes, basis, pairing and classical dependency hashes into one receiver-accepted import snapshot without treating regeneration as independent verification."),
        ("STRICT_386_LOCAL_SDR_COMPONENT_MAPS", "STRICT_PURE_WEYL_386", "HIGH", "HIGH", "LOW", "Serialize H_alg, P_alg, P_end, i_end and p_end from exact producers and independently replay the support-local SDR and cyclic identities on the accepted carrier."),
        ("STRICT_ENDPOINT_ANALYTIC_GREEN_ACTION", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "MEDIUM", "Declare represented test and distribution spaces and import an advanced/retarded endpoint action or kernel with topology, continuity, uniqueness, support and adjoint data."),
        ("STRICT_FULL_GREEN_COMPONENT_ACTION_REPLAY", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Compose the represented endpoint Green action with accepted local SDR maps and replay full homotopy, causal support and suspended adjointness on the fixed carrier."),
        ("STRICT_386_LOCAL_D", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "MEDIUM", "Serialize cylinder-time D on the accepted operator carrier and verify its q1 commutator only after the unary carrier artifacts share one digest."),
        ("STRICT_386_Q2_GREEN_COMPATIBILITY", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Bind target-action q2 to the same paired D-equivariant causal carrier and test contraction compatibility after the complete unary action replay."),
        ("DIRECT_SPACETIME_Q26_HADAMARD", "BERGER_POSITIVE_CLOCK_54", "VERY_HIGH", "LOW", "MEDIUM", "Retain the analytically mature independent route through direct nonstationary q26-equivariant distributional state selection."),
        ("BACH_FLAT_NONLINEAR_CARTAN", "PURE_WEYL_BACH_FLAT_RANK310", "HIGH", "MEDIUM", "MEDIUM", "Use the broad curved strict causal branch as an independent nonlinear compatibility control while the target-theory portability route advances."),
    ]
    value["route_selection"] = [{"rank": index, "route": route, "branch": branch, "scientific_leverage": leverage, "tractability": tractability, "dependency_depth": depth, "recommendation": recommendation} for index, (route, branch, leverage, tractability, depth, recommendation) in enumerate(routes, 1)]
    value["research_queue"] = [{"priority": item["rank"], "branch": item["branch"], "object": item["route"], "why": item["recommendation"]} for item in value["route_selection"]]
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V9 atlas predecessor"},
        {"path": str(REPAIR.relative_to(ROOT)), "sha256": sha(REPAIR), "role": "exact auxiliary-q sign repair and full classical-suite receipt"},
    ]
    value["claim_flags"].update({
        "v9_preserved": True,
        "strict_386_auxiliary_q_sign_repair_applied": True,
        "strict_386_auxiliary_q_source_ledger_pairing_consistent": True,
        "strict_386_affected_classical_chain_verified": True,
        "strict_386_full_classical_covariant_suite_passed": True,
        "strict_full_386_q1_portable_component_bytes": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys(previous["does_not_establish"] + repair["does_not_establish"]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v10.py",
        "checks": ["V9 preservation", "77-cell closure", "strict S0-only mutation", "repair projection", "zero-versus-eight replay", "Tier-3 receipt", "full-q1/import firewall", "causal theorem preservation", "nine-route ranking", "append-only provenance", "content hashes", "canonical digest"],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    item = value["strict_auxiliary_q_sign_repair"]
    lines = [
        "# Lorentzian Weyl BV completion atlas V10", "", "## Outcome", "", value["answer"], "",
        "## Repaired auxiliary sign gate", "", "| rail | repaired `+I_4` | rejected `-I_4` regression |", "|---|---:|---:|",
        f"| odd-pairing cyclicity defects | **{item['plus_cyclicity_defects']}** | **{item['minus_regression_cyclicity_defects']}** |", "",
        f"The affected classical chain was regenerated and the full Tier-3 suite passed in {item['tier_3_elapsed_seconds']:.2f} seconds with {item['terminal_overclaim_guards']}/82 terminal overclaim guards. Full q1 serialization and quantum import acceptance remain false.", "",
        "## Updated route selection", "", "| rank | route | branch | leverage | tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(f"| {route['rank']} | `{route['route']}` | `{route['branch']}` | {route['scientific_leverage']} | {route['tractability']} |" for route in value["route_selection"])
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v10.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v10.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v10.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v10.py", "```", "", "## Boundaries", ""]
    lines.extend(f"- This does not establish {boundary}." for boundary in value["does_not_establish"])
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V10: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V10: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
