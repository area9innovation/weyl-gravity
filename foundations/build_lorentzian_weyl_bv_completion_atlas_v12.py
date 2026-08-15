#!/usr/bin/env python3
"""Build atlas V12 from V11 plus the exact strict split local SDR maps."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V11.json"
SDR = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V12.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v12.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "strict_causal_sign_transport",
        "strict_endpoint_q1_content_bridge", "strict_suspended_adjoint_bridge",
        "strict_component_pairing_serialization", "strict_operator_portability",
        "strict_full_q1_split_sign_gate", "strict_auxiliary_q_sign_repair",
        "strict_full_q1_component_jet_table", "strict_local_sdr_component_maps",
        "berger_h26_c26_decision_chain", "route_selection", "research_queue",
    )
    payload = json.dumps({key: value[key] for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def strict_branch(value: dict[str, Any]) -> dict[str, Any]:
    return next(item for item in value["branches"] if item["id"] == "STRICT_PURE_WEYL_386")


def stage(value: dict[str, Any], stage_id: str) -> dict[str, Any]:
    return next(item for item in strict_branch(value)["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous, sdr = json.loads(PREDECESSOR.read_text()), json.loads(SDR.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V11":
        raise ValueError("V11 predecessor drift")
    if sdr.get("result_id") != "STRICT_386_LOCAL_SDR_COMPONENT_MAPS_V1":
        raise ValueError("local SDR dependency drift")
    flags = sdr["claim_flags"]
    for key in ("STRICT_386_SPLIT_LOCAL_SDR_COMPONENT_MAPS_SERIALIZED", "STRICT_386_LOCAL_SDR_IDENTITIES_REPLAYED", "STRICT_386_LOCAL_SDR_CYCLICITY_REPLAYED"):
        if flags.get(key) is not True:
            raise ValueError("local SDR positive flag drift: " + key)
    if flags["STRICT_386_CANONICAL_SHEAR_COMPONENT_JET_TABLE_SERIALIZED"] or flags["STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED"] or flags["CLASSICAL_IMPORT_GATE_PASSED"]:
        raise ValueError("shear/Green/import promotion drift")

    value = deepcopy(previous)
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v12",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V12",
        "created": "2026-08-15",
        "repository_base_commit": "da2521d7017e55e001ff1bb868c7ae7bbcdbdbed",
        "question": "After Atlas V11 fixed the complete 386-row unary snapshot, can its local contraction and endpoint retract be serialized and replayed componentwise without conflating the split presentation with the unshifted curvature graph or a nonlocal causal Green action?",
        "answer": "Atlas V12 closes the first-ranked V11 local-SDR route on the exact split unary snapshot. The retained thirty Gate rows embed and project by thirty identity entries each. The complementary generalized-auxiliary and curvature-cone rows carry a single order-zero H_alg with 190 rational entries; P_end is the rank-thirty endpoint diagonal and P_alg is its rank-356 complement. Across every one of the 70 derivative multiindices in the full q1 snapshot, the receiver obtains q1 H_alg+H_alg q1=P_alg with zero defects. It also replays p_end i_end=I_30, i_end p_end=P_end, both chain-map identities, commuting complementary idempotents, H_alg squared and every normalized side condition, and the exact cyclic identity H_alg^T Omega-D Omega H_alg=0. These maps are finite, support-local and PRA-formalizable, with no choice or infinite selection. The result is deliberately coordinate-scoped. Primitive q1 and the new SDR use the certified split presentation. The finite-order degree-zero T/A/B canonical shear that transports this data to the unshifted curvature graph is not part of q1 and has not yet been emitted as a Gate-basis component-jet table. Atlas V12 therefore splits the next work into two falsifiable finite tasks: serialize the shear and inverse, then conjugate q1 and the SDR and replay the graph-coordinate identities. Only after that should the programme import represented endpoint advanced/retarded actions on declared test and distribution spaces and assemble the full Green homotopy. Gate A still accepts no common snapshot. Local D, same-carrier q2, Hadamard construction, Ward identities, renormalized Lorentzian products, QME restoration and residual transfer remain downstream and unpromoted.",
        "predecessor": {"result_id": previous["result_id"], "path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "preserved": True},
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v12.md",
    })
    maps = sdr["component_maps"]
    projection = {
        "result_id": sdr["result_id"],
        "status": sdr["result_state"],
        "carrier_dimension": sdr["scope"]["carrier_dimension"],
        "retained_endpoint_dimension": sdr["scope"]["retained_endpoint_dimension"],
        "contracted_dimension": sdr["scope"]["contracted_dimension"],
        "map_count": len(maps),
        "H_alg_nonzero_entries": maps["H_alg"]["nonzero_entries"],
        "P_alg_nonzero_entries": maps["P_alg"]["nonzero_entries"],
        "P_end_nonzero_entries": maps["P_end"]["nonzero_entries"],
        "i_end_nonzero_entries": maps["i_end"]["nonzero_entries"],
        "p_end_nonzero_entries": maps["p_end"]["nonzero_entries"],
        "maximum_order": sdr["support_and_foundations"]["maximum_differential_order"],
        "derivative_multiindices_checked": sdr["exact_replay"]["derivative_multiindices_checked"],
        "homotopy_identity_defects": sdr["exact_replay"]["qH_plus_Hq_defects"],
        "cyclicity_defects": sdr["exact_replay"]["H_alg_cyclicity_defects"],
        "local_sdr_snapshot_sha256": sdr["local_sdr_snapshot"]["snapshot_sha256"],
        "split_SDR_complete": sdr["coordinate_transport_boundary"]["split_SDR_complete"],
        "canonical_shear_serialized": sdr["coordinate_transport_boundary"]["T_A_B_canonical_shear_serialized"],
        "represented_green_actions_serialized": flags["STRICT_386_REPRESENTED_GREEN_ACTIONS_SERIALIZED"],
        "classical_import_gate_passed": flags["CLASSICAL_IMPORT_GATE_PASSED"],
        "next_gate": sdr["next_gate"],
    }
    value["strict_local_sdr_component_maps"] = projection
    stage(value, "S0_CLASSICAL_AUTHORITY").update({
        "status": "FAIL_CLOSED",
        "statement": "The split 386-row q1, pairing and local SDR are now one exact receiver-readable bundle: H_alg has 190 entries, all five maps are serialized, and the homotopy, chain-map, side-condition and cyclic identities have zero defects. Gate A remains closed pending the canonical shear, graph-coordinate replay and represented Green actions.",
        "evidence": [*stage(value, "S0_CLASSICAL_AUTHORITY")["evidence"], sdr["result_id"]],
        "boundary": "The split local SDR is not the unshifted graph-coordinate SDR and contains no nonlocal Green action. T/A/B shear bytes, conjugation replay, represented endpoint/full Green actions, local D and q2 remain outside the accepted common object.",
    })
    strict_branch(value)["next_decisive_object"] = "Serialize the finite-order T/A/B canonical shear and inverse on the fixed Gate basis, then replay the split-to-unshifted graph conjugation before importing represented endpoint Green actions."
    value["frontier_summary"]["theory_identity_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "first_gate": "S0_CLASSICAL_AUTHORITY",
        "current_fact": "The full q1 and its split local SDR are content-addressed exact component data with all local identities replayed; the remaining finite coordinate gate is the T/A/B canonical shear and graph-coordinate conjugation.",
        "best_next_object": "A Gate-basis component-jet table for the T/A/B shear and inverse, followed by an independent conjugation and cyclicity replay.",
    }
    value["strict_gate_a_progress"].update({
        "status": "FULL_Q1_AND_SPLIT_SDR_SERIALIZED_SHEAR_GREEN_COMMON_SNAPSHOT_REQUIRED",
        "local_sdr_component_map_control": projection,
        "remaining_common_carrier": sdr["next_gate"],
        "boundary": "The unary and split local-SDR snapshots pass exact tests. Gate A still requires canonical-shear bytes, graph-coordinate replay, represented Green actions and one receiver-accepted common snapshot before q2 or D are bound.",
    })
    routes = [
        ("STRICT_386_CANONICAL_SHEAR_COMPONENT_JETS", "STRICT_PURE_WEYL_386", "VERY_HIGH", "HIGH", "LOW", "Emit T, A, B and their BV-forced formal adjoints as finite parallel-coefficient component-jet tables, together with the exact inverse, on the fixed 386-row Gate basis."),
        ("STRICT_386_SPLIT_TO_GRAPH_SDR_REPLAY", "STRICT_PURE_WEYL_386", "VERY_HIGH", "HIGH", "LOW", "Conjugate q1, H_alg, i_end and p_end by the serialized shear and replay inverse, chain-map, homotopy, pairing-canonical and cyclic identities in unshifted graph coordinates."),
        ("STRICT_ENDPOINT_ANALYTIC_GREEN_ACTION", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "MEDIUM", "Declare represented test/distribution spaces and import advanced/retarded endpoint actions with topology, continuity, uniqueness, support and adjoint data."),
        ("STRICT_FULL_GREEN_COMPONENT_ACTION_REPLAY", "STRICT_PURE_WEYL_386", "VERY_HIGH", "MEDIUM", "HIGH", "Compose the represented endpoint action with the graph-coordinate SDR and replay full homotopy, causal support and suspended adjointness on the fixed carrier."),
        ("STRICT_386_ACCEPTED_COMMON_SNAPSHOT", "STRICT_PURE_WEYL_386", "VERY_HIGH", "HIGH", "LOW", "Bind basis, pairing, q1, SDR, shear and represented Green actions into one receiver-accepted import snapshot without treating producer regeneration as independent verification."),
        ("STRICT_386_LOCAL_D", "STRICT_PURE_WEYL_386", "VERY_HIGH", "LOW", "MEDIUM", "Serialize cylinder-time D on the accepted common carrier and verify its q1 commutator before any nonlinear promotion."),
        ("STRICT_386_Q2_GREEN_COMPATIBILITY", "STRICT_PURE_WEYL_386", "HIGH", "LOW", "HIGH", "Bind target-action q2 to the same paired D-equivariant causal carrier and test contraction compatibility after the complete unary action replay."),
        ("DIRECT_SPACETIME_Q26_HADAMARD", "BERGER_POSITIVE_CLOCK_54", "VERY_HIGH", "LOW", "MEDIUM", "Retain the analytically mature independent route through direct nonstationary q26-equivariant distributional state selection."),
        ("BACH_FLAT_NONLINEAR_CARTAN", "PURE_WEYL_BACH_FLAT_RANK310", "HIGH", "MEDIUM", "MEDIUM", "Use the broad curved strict causal branch as an independent nonlinear compatibility control while the target-theory import route advances."),
    ]
    value["route_selection"] = [
        {"rank": rank, "route": route, "branch": branch, "scientific_leverage": leverage, "tractability": tractability, "dependency_depth": depth, "recommendation": recommendation}
        for rank, (route, branch, leverage, tractability, depth, recommendation) in enumerate(routes, 1)
    ]
    value["research_queue"] = [{"priority": item["rank"], "branch": item["branch"], "object": item["route"], "why": item["recommendation"]} for item in value["route_selection"]]
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V11 atlas predecessor"},
        {"path": str(SDR.relative_to(ROOT)), "sha256": sha(SDR), "role": "exact split local SDR component maps and replay"},
    ]
    value["claim_flags"].update({
        "v11_preserved": True,
        "strict_386_split_local_sdr_component_maps_serialized": True,
        "strict_386_split_local_sdr_identities_replayed": True,
        "strict_386_split_local_sdr_cyclicity_replayed": True,
        "strict_386_canonical_shear_component_jets_serialized": False,
        "strict_386_unshifted_graph_sdr_snapshot_complete": False,
        "strict_386_represented_green_actions_serialized": False,
        "strict_pure_weyl_classical_gate_passed": False,
        "lorentzian_full_theory_certified": False,
    })
    value["does_not_establish"] = list(dict.fromkeys(previous["does_not_establish"] + sdr["does_not_establish"]))
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v12.py",
        "checks": ["V11 preservation", "77-cell closure", "strict S0-only mutation", "local-SDR projection", "190-entry H_alg inventory", "zero homotopy/cyclicity defects", "split-coordinate boundary", "shear/Green/import firewall", "causal theorem preservation", "nine-route ranking", "append-only provenance", "content hashes", "canonical digest"],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    item = value["strict_local_sdr_component_maps"]
    lines = [
        "# Lorentzian Weyl BV completion atlas V12", "", "## Outcome", "", value["answer"], "",
        "## Exact split local SDR", "", "| map | nonzero exact entries |", "|---|---:|",
        f"| `H_alg` | {item['H_alg_nonzero_entries']} |", f"| `P_alg` | {item['P_alg_nonzero_entries']} |",
        f"| `P_end` | {item['P_end_nonzero_entries']} |", f"| `i_end` | {item['i_end_nonzero_entries']} |", f"| `p_end` | {item['p_end_nonzero_entries']} |", "",
        f"All {item['derivative_multiindices_checked']} q1 multiindices replay with {item['homotopy_identity_defects']} homotopy defects and {item['cyclicity_defects']} cyclicity defects.", "",
        f"Local SDR snapshot: `{item['local_sdr_snapshot_sha256']}`.", "",
        "## Updated route selection", "", "| rank | route | branch | leverage | tractability |", "|---:|---|---|---|---|",
    ]
    lines.extend(f"| {route['rank']} | `{route['route']}` | `{route['branch']}` | {route['scientific_leverage']} | {route['tractability']} |" for route in value["route_selection"])
    lines += ["", "## Reproduction", "", "```text", "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v12.py --check", "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v12.py", "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v12.py", "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v12.py", "```", "", "## Boundaries", ""]
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V12: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    RESULT.write_bytes(result)
    REPORT.write_bytes(report)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V12: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
