#!/usr/bin/env python3
"""Build atlas V6 from V5 plus the strict suspended-adjoint bridge."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V5.json"
SUSPENSION = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V6.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v6.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = ("stages", "branches", "frontier_summary", "classical_import_reconciliation", "strict_gate_a_progress", "strict_causal_sign_transport", "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge", "berger_h26_c26_decision_chain", "route_selection", "research_queue")
    return hashlib.sha256(json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def branch(value: dict[str, Any]) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == "STRICT_PURE_WEYL_386")


def stage(value: dict[str, Any], stage_id: str) -> dict[str, Any]:
    return next(item for item in branch(value)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text())
    suspension = json.loads(SUSPENSION.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V5":
        raise ValueError("V5 predecessor drift")
    if suspension.get("result_id") != "STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1":
        raise ValueError("suspension bridge drift")
    flags = suspension["claim_flags"]
    if not flags["FULL_386_SUSPENDED_GREEN_ADJOINT_REPLAYED"] or flags["FULL_386_COMPONENT_PAIRING_SERIALIZED_IN_GATE_CONVENTION"]:
        raise ValueError("suspension/full-pairing boundary drift")

    value = deepcopy(previous)
    stage(value, "S0_CLASSICAL_AUTHORITY").update({
        "status": "FAIL_CLOSED",
        "statement": "Gate V5 remains fail closed. The common thirty-row q1 is exact and the former five-row pairing mismatch is now identified as the Gate suspension character R=diag(-I_5,I_10,I_10,-I_5), extended over the cyclic 356+30 decomposition.",
        "evidence": ["CLASSICAL_IMPORT_GATE_V5_RECONCILIATION", "STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1", "STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1"],
        "boundary": "The abstract full-carrier suspended adjoint is fixed, but the 356 complement's component pairing rows, one common full-carrier hash, local D, q2 and residual extension remain absent.",
    })
    stage(value, "S2_CAUSAL_GREEN").update({
        "status": "SCOPED_CERTIFIED",
        "statement": "The 386-row Green homotopy now has an exact Gate-suspended adjoint replay. With A^ddagger=R A^sharp_G R, the transported homotopies obey (Lambda'_+)^ddagger=Lambda'_-, while both homotopy identities and causal support remain unchanged.",
        "evidence": ["pure-weyl-full-prolonged-green-homotopy-assembly-v1", "STRICT_386_CAUSAL_SIGN_TRANSPORT_V1", "STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1", "STRICT_386_SUSPENDED_ADJOINT_BRIDGE_V1"],
        "boundary": "This is a projector-level full-carrier convention theorem, not a serialized 386-row Gate pairing or a nonlinear q2/D theorem.",
    })
    branch(value)["next_decisive_object"] = "Serialize the 356 complement's component basis and pairing in the now-fixed Gate suspension convention, bind those rows to P_alg/P_end and replay all component adjoints. Then add local D and q2 on exactly those bytes."
    full = suspension["full_carrier_extension"]
    endpoint = suspension["endpoint_exact_algebra"]
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v6",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V6",
        "created": "2026-08-15",
        "repository_base_commit": "f2d898b68309a437d66b3efeec6307580a4fd269",
        "question": "Does the five-row pairing sign left open by atlas V5 obstruct the strict causal architecture, and what exact object now blocks a common 386-row Gate carrier?",
        "answer": "No new unary causal obstruction remains at the sign boundary. The exact endpoint pairing has 54 nonzero ordered entries. For the already certified q1 transport T=diag(I_5,I_10,I_10,-I_5), rational matrix algebra gives T^{sharp_G}=diag(-I_5,I_10,I_10,I_5) with respect to the untransported Gate-canonical endpoint pairing. Their product R=T^{sharp_G}T=diag(-I_5,I_10,I_10,-I_5) is an involutive suspension character. For every transported operator A'=TAT, defining A^ddagger=R A^{sharp_G}R gives (A')^ddagger=T A^sharp T. It therefore transports both Gate odd cyclicity and the advanced/retarded Green adjoint relation without changing the homotopy or support identities. Because the hybrid P_alg/P_end splitting is cyclic and formally self-adjoint, R extends by I_356 to all 386 rows, with 376 positive and ten negative signs, and the full projector-level suspended Green-adjoint theorem replays. The previous five-row mismatch is thus classified as the explicit difference between ordinary and suspended adjoints, not a no-go. Gate A nevertheless remains fail closed: the 356 complement still lacks a portable component basis and pairing table in the Gate convention, so there is no accepted common full-carrier hash or componentwise replay. Local D and q2 are also absent from those causal bytes. The new first-ranked task is concrete pairing serialization rather than another convention choice. Hadamard, Ward, positivity, renormalized products, QME and residual quantum transfer remain unpromoted.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v6.md",
    })
    value["frontier_summary"]["theory_identity_front"] = {
        "branch": "STRICT_PURE_WEYL_386", "first_gate": "S0_CLASSICAL_AUTHORITY",
        "current_fact": "The endpoint q1 bytes agree and the five-row sign is exactly the Gate suspension character; the full 386-row Green adjoint theorem replays abstractly over the cyclic 356+30 split.",
        "best_next_object": "A portable 356-row component basis and pairing table in the fixed Gate suspension convention, followed by component adjoint, local-D and q2 replay.",
    }
    progress = value["strict_gate_a_progress"]
    progress.update({
        "status": "FULL_SUSPENDED_GREEN_ADJOINT_REPLAYED_COMPONENT_PAIRING_D_Q2_OPEN",
        "evidence": [*progress["evidence"], suspension["result_id"]],
        "suspended_adjoint_control": {"endpoint_pairing_entries": endpoint["gate_pairing_nonzero_entries"], "R_386_positive": full["R_386_positive"], "R_386_negative": full["R_386_negative"], "full_green_suspended_adjoint_replayed": True, "full_component_pairing_serialized": False},
        "remaining_common_carrier": suspension["next_gate"],
        "boundary": "The sign convention is no longer open. Gate A still requires the 356 component pairing bytes, common hashes, local D, q2 and residual-SDR extension.",
    })
    value["strict_suspended_adjoint_bridge"] = {
        "result_id": suspension["result_id"], "status": suspension["result_state"],
        "endpoint_pairing_entries": endpoint["gate_pairing_nonzero_entries"],
        "endpoint_T_negative": endpoint["T_diagonal"].count(-1),
        "endpoint_T_sharp_negative": endpoint["T_sharp_gate_diagonal"].count(-1),
        "endpoint_R_negative": endpoint["R_diagonal"].count(-1),
        "full_R_positive": full["R_386_positive"], "full_R_negative": full["R_386_negative"],
        "full_suspended_green_adjoint_replayed": full["full_green_suspended_adjoint_replayed"],
        "full_component_pairing_serialized": full["full_component_pairing_coefficients_serialized"],
        "finite_bridge_base": suspension["foundational_strength"]["finite_suspension_bridge_base"],
        "analytic_causal_weakest_base": suspension["foundational_strength"]["weakest_base_for_imported_analytic_causal_theorem"],
        "next_gate": suspension["next_gate"],
    }
    value["route_selection"] = [
        {"rank": 1, "route": "STRICT_386_COMPONENT_PAIRING_SERIALIZATION", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "MEDIUM", "dependency_depth": "LOW", "recommendation": "Emit the 356 complement row basis and pairing table in the fixed Gate suspension convention and replay every component adjoint."},
        {"rank": 2, "route": "STRICT_386_LOCAL_D", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "MEDIUM", "recommendation": "Serialize cylinder-time D on the common paired carrier and verify its q1 commutator before nonlinear transfer."},
        {"rank": 3, "route": "STRICT_386_Q2_GREEN_COMPATIBILITY", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "HIGH", "tractability": "LOW", "dependency_depth": "HIGH", "recommendation": "Bind the target-action q2 to the same paired D-equivariant causal carrier and test contraction compatibility."},
        {"rank": 4, "route": "DIRECT_SPACETIME_Q26_HADAMARD", "branch": "BERGER_POSITIVE_CLOCK_54", "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "MEDIUM", "recommendation": "Retain the analytically mature parallel route through direct nonstationary q26-equivariant distributional selection."},
        {"rank": 5, "route": "BACH_FLAT_NONLINEAR_CARTAN", "branch": "PURE_WEYL_BACH_FLAT_RANK310", "scientific_leverage": "HIGH", "tractability": "MEDIUM", "dependency_depth": "MEDIUM", "recommendation": "Use the broad curved strict causal branch as the independent nonlinear compatibility control."},
    ]
    value["research_queue"] = [
        {"priority": 1, "branch": "STRICT_PURE_WEYL_386", "object": "356-row component pairing serialization", "why": "The suspension convention is fixed; explicit complement bytes are now the smallest missing Gate-A object."},
        {"priority": 2, "branch": "STRICT_PURE_WEYL_386", "object": "same-carrier local D", "why": "D equivariance is the next unary admission gate once the component pairing is portable."},
        {"priority": 3, "branch": "STRICT_PURE_WEYL_386", "object": "same-carrier q2/Green compatibility", "why": "This is the first nonlinear target-theory test after pairing and D."},
        {"priority": 4, "branch": "BERGER_POSITIVE_CLOCK_54", "object": "direct spacetime q26-equivariant nonstationary Hadamard selection", "why": "Berger remains the shortest independent route toward a full-carrier Hadamard/Ward result."},
        {"priority": 5, "branch": "PURE_WEYL_BACH_FLAT_RANK310", "object": "same-carrier nonlinear cyclic D-Cartan transfer", "why": "It tests nonlinear survival on the broadest curved strict causal control."},
    ]
    value["provenance"]["inputs"] = [*previous["provenance"]["inputs"], {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V5 atlas predecessor"}, {"path": str(SUSPENSION.relative_to(ROOT)), "sha256": sha(SUSPENSION), "role": "exact full-carrier suspended-adjoint bridge"}]
    value["claim_flags"].update({"v5_preserved": True, "strict_386_pairing_suspension_bridge_certified": True, "strict_386_full_suspended_green_adjoint_replayed": True, "strict_386_component_pairing_serialized": False, "strict_386_common_bytes_identified": False, "strict_full_386_pairing_serialized": False, "strict_386_local_d_certified": False, "strict_386_q2_green_compatibility_certified": False})
    remove = ("simultaneously transported causal pairing equals", "canonical paired Green theorem on the entire 386-row")
    value["does_not_establish"] = [item for item in previous["does_not_establish"] if not any(token in item for token in remove)] + ["a serialized 356-row complement pairing or one accepted common 386-row component hash", "local D or q2 compatibility on the common causal carrier", "a passed Gate A, Hadamard state, Ward theorem, QME restoration, residual transfer or Lorentzian quantum theory"]
    value["independent_checker"] = {"path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v6.py", "checks": ["V5 preservation", "77-cell closure", "suspension matrix/count projection", "full Green-adjoint replay", "component-pairing firewall", "Gate-A/q2/D firewalls", "Berger-chain preservation", "route ranking", "content hashes", "canonical digest"], "expected_digest": ""}
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    item = value["strict_suspended_adjoint_bridge"]
    lines = ["# Lorentzian Weyl BV completion atlas V6", "", "## Outcome", "", value["answer"], "", "## Suspension-adjoint result", "", f"- Exact endpoint pairing entries: **{item['endpoint_pairing_entries']}**.", f"- Negative signs: `T_30` **{item['endpoint_T_negative']}**, `T_30^sharp` **{item['endpoint_T_sharp_negative']}**, `R_30` **{item['endpoint_R_negative']}**.", f"- Full `R_386`: **{item['full_R_positive']} positive**, **{item['full_R_negative']} negative**.", "- Full suspended Green adjoint: **replayed**; 356-row component pairing: **not serialized**.", "", "## Updated route selection", "", "| rank | route | leverage | tractability | dependency depth |", "|---:|---|---|---|---|---|"]
    for route in value["route_selection"]:
        lines.append(f"| {route['rank']} | `{route['route']}` | {route['scientific_leverage']} | {route['tractability']} | {route['dependency_depth']} |")
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v6.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v6.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v6.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v6.py", "```", "", "## Boundaries", ""]
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V6: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result); REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V6: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
