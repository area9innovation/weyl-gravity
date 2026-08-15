#!/usr/bin/env python3
"""Build atlas V4 after Gate V5 and strict 386-row sign transport."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V3.json"
GATE = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_IMPORT_GATE_V5_RECONCILIATION.json"
CYCLIC = ROOT / "quantum-weyl/classical_import/certificates/STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1.json"
TRANSPORT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_CAUSAL_SIGN_TRANSPORT_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V4.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v4.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages",
        "branches",
        "frontier_summary",
        "classical_import_reconciliation",
        "strict_gate_a_progress",
        "strict_causal_sign_transport",
        "berger_h26_c26_decision_chain",
        "route_selection",
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
    cyclic = json.loads(CYCLIC.read_text())
    transport = json.loads(TRANSPORT.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V3":
        raise ValueError("atlas V3 predecessor drift")
    if gate.get("result_id") != "CLASSICAL_IMPORT_GATE_V5_RECONCILIATION":
        raise ValueError("Gate V5 input drift")
    if gate.get("gate_disposition", {}).get("gate_a_status") != "FAIL_CLOSED":
        raise ValueError("Gate A was silently promoted")
    if cyclic.get("result_id") != "STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1":
        raise ValueError("minimal cyclicity input drift")
    if transport.get("result_id") != "STRICT_386_CAUSAL_SIGN_TRANSPORT_V1":
        raise ValueError("causal sign transport input drift")
    if transport["claim_flags"]["GATE_V5_TO_386_COMMON_BYTES_IDENTIFIED"]:
        raise ValueError("type bridge was silently promoted to common bytes")

    value = deepcopy(previous)
    branches = value["branches"]
    strict = route(branches, "STRICT_PURE_WEYL_386")
    stage(strict, "S0_CLASSICAL_AUTHORITY").update(
        {
            "status": "FAIL_CLOSED",
            "statement": "Gate V5 now certifies the canonical rank-30 minimal pairing, the translated q1/q2 convention and minimal cyclicity, in addition to the V3 finite residual SDR. It has ten scoped exports and seven scoped checks, but still accepts zero common full-carrier hashes.",
            "evidence": ["CLASSICAL_IMPORT_GATE_V5_RECONCILIATION", "STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1"],
            "boundary": "The minimal and finite-split repairs live on proper scoped carriers. The complete 386-row pairing/convention, local D, same-carrier q2/Green compatibility, residual extension and one common snapshot remain unverified.",
        }
    )
    stage(strict, "S2_CAUSAL_GREEN").update(
        {
            "status": "SCOPED_CERTIFIED",
            "statement": "The 386-row unary causal Green homotopy remains certified, and an exact 381-plus/5-minus pointwise involution proves that the Gate-V5 ghost-antifield sign repair does not invalidate its causal identities or support.",
            "evidence": ["pure-weyl-full-prolonged-green-homotopy-assembly-v1", "STRICT_386_CAUSAL_SIGN_TRANSPORT_V1"],
            "boundary": "This is convention stability under exact conjugation, not coefficientwise common-byte identification or nonlinear q2/D compatibility.",
        }
    )
    strict["next_decisive_object"] = (
        "Serialize the exact endpoint inclusion/permutation and canonical pairing on the 386-row bytes, "
        "identify translated Gate-V5 q1 coefficientwise, and extend the sign/pairing convention across "
        "the 356-row complement. Then add local D and test q2 compatibility with the same causal contraction."
    )

    answer = (
        "Gate V5 and the causal crosswalk change the strict target-theory route in two ways. First, the "
        "canonical odd pairing and q1/q2 cyclicity are no longer an unspecified gap on the minimal carrier: "
        "the exact thirty-component receiver finds 540 defects in the landed convention and zero among 932 "
        "expanded non-Bach coefficients after the involution that flips c_star and omega_star. Together with "
        "the earlier 4,490-by-470 finite residual SDR, this raises the strict front from seven to ten scoped "
        "exports and from five to seven scoped freeze checks. Second, the repair does not force a rebuild of "
        "the certified 386-row causal architecture. The minimal generator groups have dimensions 5,10,10,5, "
        "exactly matching its causal endpoint. Extending the sign map by the identity on the 356 algebraically "
        "contracted rows gives an involution with 381 positive and five negative entries; exact conjugation "
        "preserves nilpotency, both Green-homotopy identities, causal support, advanced/retarded orientation "
        "and the adjoint relation with the transported pairing. The surprise is therefore positive but narrow: "
        "strict pure Weyl has a convention-stable causal survivor, not yet a common imported carrier. Gate A "
        "still accepts zero hashes because a type-and-dimension match is not coefficientwise byte identity, the "
        "full 386-row canonical pairing is not serialized, local D is absent, and no q2/Green compatibility "
        "theorem exists. This sharpens the next task into a relatively bounded endpoint content bridge before "
        "the harder 356-row complement and nonlinear work. Berger remains the analytic-maturity leader toward "
        "Hadamard/Ward completion, but the strict target route is no longer threatened by the sign repair. No "
        "Hadamard state, renormalized product, QME, residual quantum transfer or completed Lorentzian theory is promoted."
    )
    value.update(
        {
            "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v4",
            "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V4",
            "created": "2026-08-15",
            "repository_base_commit": "2a9cee847c55c951c6653eb555a0b84be79bea78",
            "question": "After repairing strict minimal BV cyclicity, does the sign convention invalidate the existing 386-row causal route, and what is now the smallest decisive bridge toward a common Lorentzian carrier?",
            "answer": answer,
            "predecessor": {
                "result_id": previous["result_id"],
                "path": str(PREDECESSOR.relative_to(ROOT)),
                "sha256": sha(PREDECESSOR),
                "preserved": True,
            },
            "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v4.md",
        }
    )
    value["frontier_summary"]["theory_identity_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "first_gate": "S0_CLASSICAL_AUTHORITY",
        "current_fact": "The minimal q1/q2 pairing convention is cyclic after an exact sign repair, and the 386-row unary causal architecture is stable under its 381-plus/5-minus extension; common bytes and the full carrier remain open.",
        "best_next_object": "A content-addressed 30-row endpoint bridge, followed by the 356-row pairing/D extension and same-carrier q2/Green compatibility.",
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
    finite_control = previous["strict_gate_a_progress"]["finite_control"]
    value["strict_gate_a_progress"] = {
        "status": "MINIMAL_CYCLICITY_AND_CAUSAL_CONVENTION_STABILITY_CERTIFIED_FULL_CARRIER_OPEN",
        "evidence": [gate["result_id"], cyclic["result_id"], transport["result_id"]],
        "finite_control": finite_control,
        "minimal_cyclic_control": {
            "basis_dimension": cyclic["canonical_pairing"]["component_basis_dimension"],
            "pairing_rank": cyclic["canonical_pairing"]["rank"],
            "source_defects": cyclic["cyclicity_receiver"]["source_convention_defect"]["coefficient_count"],
            "expanded_coefficients": cyclic["cyclicity_receiver"]["expanded_q2_coefficient_count"],
            "translated_defects": cyclic["cyclicity_receiver"]["translated_convention_defect"]["coefficient_count"],
            "changed_q1_rows": cyclic["sign_translation"]["changed_q1_component_ids"],
            "changed_q2_rows": cyclic["sign_translation"]["changed_q2_component_ids"],
        },
        "remaining_common_carrier": gate["next_gate"],
        "boundary": "The finite SDR, minimal cyclic carrier and abstract causal convention transport are three scoped controls, not one common 386-row content-addressed Gate-A snapshot.",
    }
    value["strict_causal_sign_transport"] = {
        "result_id": transport["result_id"],
        "status": transport["result_state"],
        "endpoint_dimension": transport["carrier_bridge"]["causal_endpoint_dimension"],
        "algebraic_complement_dimension": transport["carrier_bridge"]["causal_algebraic_complement_dimension"],
        "full_dimension": transport["carrier_bridge"]["causal_full_dimension"],
        "positive_signs": transport["transport"]["positive_eigenvalue_multiplicity"],
        "negative_signs": transport["transport"]["negative_eigenvalue_multiplicity"],
        "causal_stage_preserved": transport["architecture_disposition"]["causal_stage_preserved"],
        "common_bytes_identified": transport["architecture_disposition"]["same_operator_bytes_established"],
        "nonlinear_stage_preserved": transport["architecture_disposition"]["nonlinear_stage_preserved"],
        "fixed_carrier_transport_base": transport["foundational_strength"]["fixed_carrier_transport_base"],
        "analytic_causal_weakest_base": transport["foundational_strength"]["weakest_base_for_imported_causal_theorem"],
        "next_gate": transport["next_gate"],
    }
    value["route_selection"] = [
        {"rank": 1, "route": "STRICT_386_ENDPOINT_CONTENT_BRIDGE", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "MEDIUM", "dependency_depth": "LOW", "recommendation": "Materialize the 5/10/10/5 endpoint inclusion, permutation and pairing on exact bytes and compare translated Gate-V5 q1 coefficientwise."},
        {"rank": 2, "route": "STRICT_386_FULL_PAIRING_D", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "MEDIUM", "recommendation": "Extend the canonical convention across the 356-row complement and select the background-specific local D on the same carrier."},
        {"rank": 3, "route": "STRICT_386_Q2_GREEN_COMPATIBILITY", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "HIGH", "tractability": "LOW", "dependency_depth": "HIGH", "recommendation": "After the byte bridge and D extension, test whether strict target-action q2 is compatible with the transported causal contraction."},
        {"rank": 4, "route": "DIRECT_SPACETIME_Q26_HADAMARD", "branch": "BERGER_POSITIVE_CLOCK_54", "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "MEDIUM", "recommendation": "In parallel, attempt a direct nonstationary q26-equivariant global distributional selection on the analytically strongest branch."},
        {"rank": 5, "route": "BACH_FLAT_NONLINEAR_CARTAN", "branch": "PURE_WEYL_BACH_FLAT_RANK310", "scientific_leverage": "HIGH", "tractability": "MEDIUM", "dependency_depth": "MEDIUM", "recommendation": "Use the broadest curved strict causal branch as the medium-tractability nonlinear compatibility control."},
    ]
    value["research_queue"] = [
        {"priority": 1, "branch": "STRICT_PURE_WEYL_386", "object": "content-addressed 30-row endpoint bridge", "why": "The type and dimension match is exact, making byte identification the smallest remaining experiment that can falsify or connect the strict causal route."},
        {"priority": 2, "branch": "STRICT_PURE_WEYL_386", "object": "356-row complement pairing and local D", "why": "This closes the largest remaining Gate-V5 convention and equivariance gap after the endpoint is fixed."},
        {"priority": 3, "branch": "STRICT_PURE_WEYL_386", "object": "same-carrier q2/Green compatibility", "why": "It is the first nonlinear test that can advance the strict causal architecture beyond unary stability."},
        {"priority": 4, "branch": "BERGER_POSITIVE_CLOCK_54", "object": "direct spacetime q26-equivariant nonstationary Hadamard selection", "why": "Berger remains the shortest current route toward a full-carrier Hadamard/Ward result."},
        {"priority": 5, "branch": "PURE_WEYL_BACH_FLAT_RANK310", "object": "same-carrier nonlinear cyclic D-Cartan transfer", "why": "It tests nonlinear survival on the broadest curved strict causal control."},
    ]
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V3 atlas predecessor"},
        {"path": str(GATE.relative_to(ROOT)), "sha256": sha(GATE), "role": "Gate-A V5 minimal cyclicity reconciliation"},
        {"path": str(CYCLIC.relative_to(ROOT)), "sha256": sha(CYCLIC), "role": "exact canonical minimal pairing and cyclic sign repair"},
        {"path": str(TRANSPORT.relative_to(ROOT)), "sha256": sha(TRANSPORT), "role": "strict 386-row causal convention-stability theorem"},
    ]
    value["claim_flags"].update(
        {
            "v3_preserved": True,
            "strict_minimal_pairing_cyclicity_certified": True,
            "strict_386_sign_transport_certified": True,
            "strict_386_causal_stage_preserved_under_sign_transport": True,
            "strict_386_common_bytes_identified": False,
            "strict_full_386_pairing_serialized": False,
            "strict_386_q2_green_compatibility_certified": False,
        }
    )
    value["does_not_establish"] = [
        *previous["does_not_establish"],
        "that the Gate-V5 local q1 bytes equal the 386-row causal endpoint bytes",
        "a canonical odd pairing and cyclic convention on all 386 rows",
        "that the PRA classification of the finite sign wrapper calibrates the imported analytic causal theorem",
        "compatibility of strict q2 or D with the transported 386-row Green homotopy",
        "that convention stability is a passed Gate A, Hadamard state or Lorentzian quantum completion",
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v4.py",
        "checks": [
            "V3 preservation",
            "seven-by-eleven stage closure",
            "Gate-V5 fail-closed firewall",
            "minimal-versus-full-carrier cyclicity boundary",
            "386-row sign-transport arithmetic",
            "common-byte and nonlinear firewalls",
            "unchanged eleven-step Berger chain",
            "updated five-route ranking",
            "content hashes",
            "canonical digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    progress = value["strict_gate_a_progress"]
    minimal = progress["minimal_cyclic_control"]
    causal = value["strict_causal_sign_transport"]
    lines = [
        "# Lorentzian Weyl BV completion atlas V4",
        "",
        "## Outcome",
        "",
        value["answer"],
        "",
        "## Strict Gate-A progress",
        "",
        f"- Minimal cyclic control: rank **{minimal['pairing_rank']}** pairing; **{minimal['source_defects']} -> {minimal['translated_defects']}** defects among {minimal['expanded_coefficients']} expanded non-Bach coefficients.",
        f"- Current scoped Gate-V5 evidence: **{value['classical_import_reconciliation']['receiver_verified_scoped_exports']} exports** and **{value['classical_import_reconciliation']['receiver_verified_scoped_checks']} checks**; accepted common hashes: **{value['classical_import_reconciliation']['accepted_common_snapshot_hashes']}**.",
        f"- Finite residual control retained: **{progress['finite_control']['full_coordinates']} full** and **{progress['finite_control']['residual_coordinates']} residual** coordinates.",
        "- Boundary: these are scoped controls on different carriers; Gate A remains fail closed.",
        "",
        "## Causal convention-stability result",
        "",
        f"The strict causal carrier splits as {causal['full_dimension']}={causal['algebraic_complement_dimension']}+{causal['endpoint_dimension']}. The extended involution has {causal['positive_signs']} positive and {causal['negative_signs']} negative signs. It preserves the unary causal stage by exact conjugation, but common bytes and nonlinear compatibility remain false.",
        "",
        "The fixed-carrier wrapper is PRA finite algebra and adds no Choice. The weakest base of the imported analytic Green theorem remains `NOT_ESTABLISHED`.",
        "",
        "## Branch overview",
        "",
        "| branch | first unclosed gate | next decisive object |",
        "|---|---|---|",
    ]
    for item in value["branches"]:
        lines.append(f"| `{item['id']}` | `{item['first_unclosed_gate']}` | {item['next_decisive_object']} |")
    lines += [
        "",
        "## Updated route selection",
        "",
        "| rank | route | leverage | tractability | dependency depth | recommendation |",
        "|---:|---|---|---|---|---|",
    ]
    for item in value["route_selection"]:
        lines.append(f"| {item['rank']} | `{item['route']}` | {item['scientific_leverage']} | {item['tractability']} | {item['dependency_depth']} | {item['recommendation']} |")
    lines += [
        "",
        "## Why the ranking changed",
        "",
        "The exact endpoint type match makes byte identification a smaller and more falsifiable task than attacking the whole support-local carrier at once. If it fails, the mismatch is localized. If it succeeds, the 356-row complement and q2/D compatibility become well-typed follow-on problems. Berger remains the parallel analytic-maturity route rather than evidence for the strict theory.",
        "",
        "## Reproduction",
        "",
        "```text",
        "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v4.py --check",
        "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v4.py",
        "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v4.py",
        "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v4.py",
        "```",
        "",
        "## Boundaries",
        "",
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
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V4: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V4: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
