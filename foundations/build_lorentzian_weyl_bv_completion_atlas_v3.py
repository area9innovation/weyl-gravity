#!/usr/bin/env python3
"""Build atlas V3 after the strict D-finite residual-SDR gate repair."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V2.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V3_RECONCILIATION.json"
SDR = ROOT / "quantum-weyl/classical_import/certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V3.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v3.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary", "classical_import_reconciliation",
        "strict_gate_a_progress", "berger_h26_c26_decision_chain", "route_selection",
        "research_queue",
    )
    return hashlib.sha256(
        json.dumps(
            {key: value[key] for key in keys},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode()
    ).hexdigest()


def route(branches: list[dict[str, Any]], branch_id: str) -> dict[str, Any]:
    return next(item for item in branches if item["id"] == branch_id)


def stage(branch: dict[str, Any], stage_id: str) -> dict[str, Any]:
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text())
    gate = json.loads(GATE.read_text())
    sdr = json.loads(SDR.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V2":
        raise ValueError("atlas V2 predecessor drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V3_RECONCILIATION":
        raise ValueError("Gate V3 input drift")
    if gate.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("Gate A was silently promoted")
    if sdr.get("result_id") != "STRICT_DFINITE_RESIDUAL_SDR_V1":
        raise ValueError("strict D-finite SDR input drift")
    if sdr.get("gate_a_effect", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("finite SDR was silently promoted")

    value = deepcopy(previous)
    branches = value["branches"]
    strict = route(branches, "STRICT_PURE_WEYL_386")
    stage(strict, "S0_CLASSICAL_AUTHORITY").update({
        "status": "FAIL_CLOSED",
        "statement": "The previously absent finite residual maps are now portable: a receiver replays q0, q_res^(0), iota_cl, pi_cl and s_cl on 4,490 full and 470 residual coordinates. Gate A still lacks one common full support-local strict snapshot.",
        "evidence": ["CLASSICAL_IMPORT_GATE_V3_RECONCILIATION"],
        "boundary": "The finite D x SO(4) split control has no missing serialized maps, but it is not the arbitrary-support carrier with complete nonminimal rows, full cyclic pairing, q2, D and residual SO(4,2) data.",
    })
    strict["next_decisive_object"] = (
        "Construct the common full support-local strict carrier and derive its target-action q2 and D. "
        "In parallel, extend or reconstruct iota_cl, pi_cl and s_cl on that same carrier, using the "
        "certified 4,490-by-470 finite SDR as an exact receiver control rather than as continuum evidence."
    )

    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v3",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V3",
        "created": "2026-08-15",
        "repository_base_commit": "1ffc17e215f5a5e55ce7c095bccd25210af0698c",
        "question": "After exporting and independently replaying the strict D-finite residual contraction, how has the Lorentzian Weyl BV completion frontier changed, which Gate-A defect is actually closed, and which target-theory construction should be attempted next?",
        "answer": "The strict pure-Weyl front has made a real but deliberately scoped advance. The historical absence of portable residual maps is closed on the BGG-adapted D x SO(4)-finite carrier at energies two through six: 4,490 ordered full coordinates and 470 W+/W- residual coordinates now carry exact serialized q0, q_res^(0), iota_cl, pi_cl and s_cl, and an independent standard-library receiver proves all eight SDR identities and normalized side conditions. Gate A nevertheless remains fail-closed. The finite split carrier is not the common arbitrary-support local carrier required by the twenty-export freeze; it omits the complete nonminimal domain, full cyclic pairing, target-action q2 and D, noncompact residual action and centered representatives. Thus M3 has changed character—from missing serialization to a precise full-carrier extension problem—but has not disappeared. The route ranking changes accordingly. The best next irreducible target-theory task is strict support-local q2/D on the common carrier, closely followed by lifting the now-controlled residual SDR to that carrier. Berger remains the analytic-maturity front and its eleven-step Hadamard/Ward decision chain is unchanged: several stationary, cone and fixed non-cone architectures are obstructed, while direct nonstationary q26-equivariant selection and the complete general non-cone class remain open. No Hadamard, renormalized-product, QME, residual-transfer or full Lorentzian theory claim is promoted.",
        "predecessor": {
            "result_id": previous["result_id"],
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": sha(PREDECESSOR),
            "preserved": True,
        },
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v3.md",
    })
    value["frontier_summary"]["theory_identity_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "first_gate": "S0_CLASSICAL_AUTHORITY",
        "current_fact": "Three residual maps and four historical identities are portable and replayed in the exact finite split scope; the common support-local freeze remains open.",
        "best_next_object": "M2 strict support-local q2/D on the common carrier, with the M3 full-carrier residual-SDR lift as the coupled second rail.",
    }
    value["classical_import_reconciliation"] = {
        "result_id": gate["result_id"],
        "gate": gate["gate_disposition"]["gate_a_status"],
        "claim_state": gate["gate_disposition"]["claim_state"],
        "standalone_history_replay": gate["standalone_history_replay"]["status"],
        "open_payload_families": [item["id"] for item in gate["minimal_missing_bundle"]],
        "missing_portable_objects": gate["gate_disposition"]["missing_portable_objects"],
        "receiver_verified_scoped_exports": gate["gate_disposition"]["same_theory_receiver_verified_scoped"],
        "receiver_verified_scoped_checks": gate["gate_disposition"]["freeze_checks_receiver_verified_scoped"],
        "accepted_common_snapshot_hashes": gate["gate_disposition"]["accepted_common_snapshot_hashes"],
        "rule": gate["gate_disposition"]["rule"],
    }
    value["strict_gate_a_progress"] = {
        "status": "FINITE_RESIDUAL_MAP_PORTABILITY_CLOSED_FULL_CARRIER_OPEN",
        "evidence": [gate["result_id"], sdr["result_id"]],
        "finite_control": {
            "energies": sdr["scope"]["energies"],
            "full_coordinates": sdr["global_direct_sum"]["full_dimension"],
            "residual_coordinates": sdr["global_direct_sum"]["residual_dimension"],
            "portable_maps": sdr["gate_a_effect"]["historical_missing_exports_scoped_now_portable"],
            "replayed_historical_checks": sdr["gate_a_effect"]["historical_checks_scoped_now_replayed"],
            "all_sdr_identities": len(sdr["independent_identity_contract"]),
            "foundational_strength": sdr["foundational_strength"]["exactness_type"],
            "choice_dependency": sdr["foundational_strength"]["choice_dependency"],
        },
        "remaining_common_carrier": gate["m3_scoped_resolution"]["remaining"],
        "boundary": gate["m3_scoped_resolution"]["boundary"],
    }
    value["route_selection"] = [
        {"rank": 1, "route": "STRICT_SUPPORT_LOCAL_Q2_D", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "MEDIUM", "recommendation": "Derive the strict target-action q2 and local D on the common support-local carrier; this is now the first irreducible coefficient deficit rather than a map-serialization task."},
        {"rank": 2, "route": "STRICT_FULL_SUPPORT_LOCAL_RESIDUAL_SDR", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "MEDIUM", "recommendation": "Extend or reconstruct iota_cl, pi_cl and s_cl on the same full carrier, with the finite 4,490-by-470 payload serving as an exact regression control."},
        {"rank": 3, "route": "DIRECT_SPACETIME_Q26_HADAMARD", "branch": "BERGER_POSITIVE_CLOCK_54", "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "MEDIUM", "recommendation": "Attempt a direct nonstationary q26-equivariant global distributional selection without reusing the rejected stationary A104 graph."},
        {"rank": 4, "route": "BACH_FLAT_NONLINEAR_CARTAN", "branch": "PURE_WEYL_BACH_FLAT_RANK310", "scientific_leverage": "HIGH", "tractability": "MEDIUM", "dependency_depth": "MEDIUM", "recommendation": "Test same-carrier nonlinear cyclic compatibility on the broadest curved causal strict branch."},
        {"rank": 5, "route": "GENERAL_NONCONE_104_COMPLETION", "branch": "BERGER_POSITIVE_CLOCK_54", "scientific_leverage": "HIGH", "tractability": "VERY_LOW", "dependency_depth": "HIGH", "recommendation": "Resume only with a characteristic-zero simultaneous two-free-differential, cyclic and SDR solver; bounded architecture failures remain controls, not a global no-go."},
    ]
    value["research_queue"] = [
        {"priority": 1, "branch": "STRICT_PURE_WEYL_386", "object": "M1/M2 common support-local carrier with strict q2 and D", "why": "It is the first remaining target-action coefficient task and binds the interaction data to the carrier on which Gate A must actually close."},
        {"priority": 2, "branch": "STRICT_PURE_WEYL_386", "object": "M3 full support-local residual SDR", "why": "The finite maps and eight replayed identities now provide a strong exact control, turning an unspecified absence into a sharply testable lift problem."},
        {"priority": 3, "branch": "BERGER_POSITIVE_CLOCK_54", "object": "direct spacetime q26-equivariant nonstationary Hadamard selection", "why": "It tests the strongest causal branch without committing to the heavily obstructed stationary Cauchy-graph route."},
        {"priority": 4, "branch": "PURE_WEYL_BACH_FLAT_RANK310", "object": "same-carrier nonlinear cyclic D-Cartan transfer", "why": "It is the cleanest medium-tractability test of whether curved strict causal control survives nonlinear compatibility."},
        {"priority": 5, "branch": "BERGER_POSITIVE_CLOCK_54", "object": "complete general non-cone 104-row completion", "why": "It remains decisive but requires a completeness-capable exact simultaneous solver rather than another bounded ansatz."},
    ]

    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V2 atlas predecessor"},
        {"path": str(GATE.relative_to(ROOT)), "sha256": sha(GATE), "role": "append-only Gate-A V3 reconciliation"},
        {"path": str(SDR.relative_to(ROOT)), "sha256": sha(SDR), "role": "exact finite residual-SDR map payload and receiver control"},
    ]
    value["claim_flags"].update({
        "v2_preserved": True,
        "strict_dfinite_residual_sdr_portable": True,
        "strict_dfinite_sdr_identities_replayed": True,
        "strict_full_support_local_residual_sdr_constructed": False,
    })
    value["does_not_establish"] = [
        *previous["does_not_establish"],
        "that the finite D x SO(4) residual contraction is an arbitrary-support or causal Green homotopy",
        "that zero missing serialized objects means the common full-carrier Gate A has passed",
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v3.py",
        "checks": [
            "V2 preservation", "seven-by-eleven stage closure",
            "Gate-A fail-closed firewall", "finite-versus-full-carrier SDR boundary",
            "ordered eleven-step Berger decision chain", "scoped-no-go firewall",
            "updated five-route ranking", "content hashes", "canonical digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    progress = value["strict_gate_a_progress"]["finite_control"]
    lines = [
        "# Lorentzian Weyl BV completion atlas V3", "", "## Outcome", "",
        value["answer"], "", "## Strict Gate-A progress", "",
        f"- Exact finite control: **{progress['full_coordinates']} full coordinates** and **{progress['residual_coordinates']} residual coordinates** at energies {', '.join(map(str, progress['energies']))}.",
        f"- Portable maps: {', '.join(f'`{item}`' for item in progress['portable_maps'])}.",
        f"- Historical checks replayed: {len(progress['replayed_historical_checks'])}; complete SDR identities replayed: {progress['all_sdr_identities']}.",
        "- Remaining boundary: the maps must still be constructed on the one common full support-local carrier. Gate A remains fail-closed with zero accepted common hashes.",
        "- Foundational scope: finite exact sparse integer algebra; no Choice is used inside the declared cutoff, and no all-energy or continuum transfer follows.",
        "", "## Branch-by-stage overview", "",
        "| branch | first unclosed gate | next decisive object |", "|---|---|---|",
    ]
    for item in value["branches"]:
        lines.append(f"| `{item['id']}` | `{item['first_unclosed_gate']}` | {item['next_decisive_object']} |")
    lines += ["", "## Updated route selection", "", "| rank | route | leverage | tractability | dependency depth | recommendation |", "|---:|---|---|---|---|---|"]
    for item in value["route_selection"]:
        lines.append(f"| {item['rank']} | `{item['route']}` | {item['scientific_leverage']} | {item['tractability']} | {item['dependency_depth']} | {item['recommendation']} |")
    lines += [
        "", "## Why the ranking changed", "",
        "V2 ranked residual-map serialization first. That object now exists and is independently replayable in the exact finite split scope. The unresolved M3 task is harder and more precise: construct the same contraction on the common support-local carrier. The first remaining coefficient-level target-theory deficit is therefore M2, strict `q2` and `D`, while the full-carrier SDR lift remains a coupled second rail.",
        "", "## Berger decision chain", "",
        "The eleven-step Berger H26/C26 decision chain is preserved unchanged. Its scoped obstructions do not become a general non-cone no-go, and the direct nonstationary route remains open.",
        "", "## Reproduction", "", "```text",
        "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v3.py --check",
        "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v3.py",
        "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v3.py",
        "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v3.py",
        "```", "", "## Boundaries", "",
    ]
    lines += [f"- This does not establish {item}." for item in value["does_not_establish"]]
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(),
        render(value).encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result_bytes, report_bytes = generated()
    outputs = ((RESULT, result_bytes), (REPORT, report_bytes))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V3: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V3: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
