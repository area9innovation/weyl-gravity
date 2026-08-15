#!/usr/bin/env python3
"""Build atlas V5 from V4 plus the exact strict endpoint q1 bridge."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V4.json"
BRIDGE = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1.json"
WITNESS = ROOT / "quantum-weyl/classical_import/certificates/STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_WITNESS_V1.json"
RESULT = ROOT / "foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V5.json"
REPORT = ROOT / "foundations/reports/lorentzian-weyl-bv-completion-atlas-v5.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: dict[str, Any]) -> str:
    keys = (
        "stages", "branches", "frontier_summary",
        "classical_import_reconciliation", "strict_gate_a_progress",
        "strict_causal_sign_transport", "strict_endpoint_q1_content_bridge",
        "berger_h26_c26_decision_chain", "route_selection", "research_queue",
    )
    payload = {key: value[key] for key in keys}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def route(branches: list[dict[str, Any]], branch_id: str) -> dict[str, Any]:
    return next(item for item in branches if item["id"] == branch_id)


def cell(branch: dict[str, Any], stage_id: str) -> dict[str, Any]:
    return next(item for item in branch["stages"] if item["stage"] == stage_id)


def build() -> dict[str, Any]:
    previous = json.loads(PREDECESSOR.read_text())
    bridge = json.loads(BRIDGE.read_text())
    if previous.get("result_id") != "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V4":
        raise ValueError("atlas V4 predecessor drift")
    if bridge.get("result_id") != "STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1":
        raise ValueError("endpoint bridge identity drift")
    flags = bridge.get("claim_flags", {})
    if not all(flags.get(key) is True for key in (
        "UNIT_CYLINDER_30_ROW_ENDPOINT_Q1_COMMON_CONTENT_IDENTIFIED",
        "ALL_700_BACH_COLUMNS_MATCH",
        "TRANSPORTED_ENDPOINT_Q1_MATCHES_GATE_CANONICAL_Q1",
        "STRICT_386_CAUSAL_ENDPOINT_OPERATOR_LINKED",
    )):
        raise ValueError("endpoint bridge positive claims incomplete")
    if any(flags.get(key) is not False for key in (
        "SIMULTANEOUSLY_TRANSPORTED_CAUSAL_PAIRING_EQUALS_GATE_CANONICAL",
        "FULL_386_PAIRING_SERIALIZED_IN_GATE_CONVENTION",
        "STRICT_386_Q2_GREEN_COMPATIBILITY_CERTIFIED",
        "CLASSICAL_IMPORT_GATE_PASSED",
        "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED",
    )):
        raise ValueError("endpoint bridge boundary promoted")

    value = deepcopy(previous)
    strict = route(value["branches"], "STRICT_PURE_WEYL_386")
    cell(strict, "S0_CLASSICAL_AUTHORITY").update({
        "status": "FAIL_CLOSED",
        "statement": "Gate V5 remains fail closed, but its canonical thirty-row minimal q1 is now identified coefficientwise with the actual strict causal endpoint: 5/5 gauge tables, 700/700 Bach columns and 5/5 Noether tables agree over Q after the exact basis bridge.",
        "evidence": ["CLASSICAL_IMPORT_GATE_V5_RECONCILIATION", "STRICT_MINIMAL_BV_CYCLIC_SIGN_RECONCILIATION_V1", "STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1"],
        "boundary": "This establishes scoped common minimal unary content, not a common full 386-row pairing, 356-row complement, q2/D carrier, residual extension or accepted Gate-A snapshot.",
    })
    cell(strict, "S2_CAUSAL_GREEN").update({
        "status": "SCOPED_CERTIFIED",
        "statement": "The certified 386-row unary Green architecture now has an exact coefficientwise link to the Gate-V5 q1 on its thirty-row endpoint. The common q1 has 619 nonzero rational coefficients and one canonical digest.",
        "evidence": ["pure-weyl-full-prolonged-green-homotopy-assembly-v1", "STRICT_386_CAUSAL_SIGN_TRANSPORT_V1", "STRICT_386_ENDPOINT_Q1_CONTENT_BRIDGE_V1"],
        "boundary": "The simultaneously transported causal ghost pairing pulls back to -I_5 rather than the Gate-canonical I_5. The graded suspension convention and full 356-row paired Green replay remain open, as do q2/D and all quantum stages.",
    })
    strict["next_decisive_object"] = (
        "Resolve the five-row ghost/identity suspension sign and serialize one canonical pairing on the exact "
        "386-row carrier; extend it across the 356-row complement and independently replay the graded-adjoint "
        "Green identity. Then bind local D and q2 to those same bytes."
    )

    identification = bridge["coefficientwise_identification"]
    pairing = bridge["pairing_disposition"]
    value.update({
        "schema_version": "foundational-lorentzian-weyl-bv-completion-atlas-v5",
        "result_id": "FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V5",
        "created": "2026-08-15",
        "repository_base_commit": "d07ce6c0c0d621b704e319e636839bf5510b13e5",
        "question": "Does the Gate-V5 strict minimal unary complex equal the actual thirty-row endpoint of the certified 386-row Lorentzian causal architecture, and which exact obstruction is next?",
        "answer": (
            "Yes for unary operator content on the unit conformal cylinder. An exact change of ghost, field, equation and identity coordinates sends every Gate-V5 minimal q1 coefficient to the causal endpoint coefficient: all five gauge-arrow tables, all 700 independent metric four-jet Bach columns and all five Noether-arrow tables agree, for 80/80 multiindex tables and 619 nonzero common rational coefficients. The Bach comparison is not a sample: it uses a 700-column triangular coordinate-to-covariant witness satisfying 490,000 exact equations. This supersedes V4's type-only endpoint bridge and proves that the convention-stable 386-row causal architecture contains the same minimal unary operator as the authoritative Gate-side export. The remaining obstruction is narrower and more structural. Before simultaneous causal sign transport, the endpoint ghost pairing pulls back to the Gate-canonical I_5; after transporting q and the pairing together, it pulls back to -I_5. Thus no single certificate yet combines the Gate suspension convention, all 386 pairing rows and the graded-adjoint Green theorem. Gate A still accepts zero full-snapshot hashes, the 356-row complement is not expressed in the Gate convention, and local D and q2 have not been bound to the causal carrier. The next experiment is therefore a five-row suspension decision followed by an exact full-carrier paired Green replay, not another search for the endpoint operator. No Hadamard state, Ward theorem, positivity result, renormalized Lorentzian product, QME restoration, residual transfer or Lorentzian quantum theory is promoted."
        ),
        "predecessor": {
            "result_id": previous["result_id"],
            "path": str(PREDECESSOR.relative_to(ROOT)),
            "sha256": sha(PREDECESSOR),
            "preserved": True,
        },
        "human_report": "foundations/reports/lorentzian-weyl-bv-completion-atlas-v5.md",
    })
    value["frontier_summary"]["theory_identity_front"] = {
        "branch": "STRICT_PURE_WEYL_386",
        "first_gate": "S0_CLASSICAL_AUTHORITY",
        "current_fact": "The Gate-V5 and causal-endpoint minimal q1 contents are exactly identical after a rational basis bridge; the paired causal transport differs from the Gate ghost pairing by -I_5.",
        "best_next_object": "A suspension/pairing bridge on the five ghost/identity rows followed by a full 386-row graded-adjoint Green replay and 356-row complement audit.",
    }
    progress = value["strict_gate_a_progress"]
    progress.update({
        "status": "MINIMAL_Q1_ENDPOINT_CONTENT_IDENTIFIED_FULL_PAIRED_CARRIER_OPEN",
        "evidence": [*progress["evidence"], bridge["result_id"]],
        "endpoint_q1_control": {
            "dimension": bridge["scope"]["gate_carrier_dimension"],
            "arrow_tables_matching": identification["arrow_table_counts"]["total"],
            "bach_columns_matching": identification["gate_bach_columns_matching"],
            "common_nonzero_coefficients": identification["common_nonzero_coefficients"],
            "common_q1_sha256": identification["common_q1_sha256"],
            "full_pairing_open": True,
        },
        "remaining_common_carrier": bridge["next_gate"],
        "boundary": "The endpoint q1 equality is exact and common, but the causal paired transport has a five-row suspension sign mismatch and the 356-row complement, D, q2 and residual maps are not one accepted snapshot.",
    })
    value["strict_endpoint_q1_content_bridge"] = {
        "result_id": bridge["result_id"],
        "status": bridge["result_state"],
        "endpoint_dimension": bridge["scope"]["causal_endpoint_dimension"],
        "full_causal_dimension": bridge["scope"]["causal_full_dimension"],
        "arrow_tables_matching": identification["arrow_table_counts"]["total"],
        "bach_columns_matching": identification["gate_bach_columns_matching"],
        "triangular_equations": bridge["basis_bridge"]["triangular_equations"],
        "common_nonzero_coefficients": identification["common_nonzero_coefficients"],
        "common_q1_sha256": identification["common_q1_sha256"],
        "field_pairing_canonical": pairing["field_pullback_equals_gate_canonical"],
        "original_ghost_pairing_canonical": pairing["original_endpoint_ghost_pullback_equals_gate_canonical"],
        "transported_ghost_pairing_canonical": pairing["simultaneously_transported_causal_ghost_pullback_equals_gate_canonical"],
        "transported_ghost_pairing_negative_canonical": pairing["simultaneously_transported_causal_ghost_pullback_equals_negative_gate_canonical"],
        "finite_bridge_base": bridge["foundational_strength"]["finite_content_bridge_base"],
        "analytic_causal_weakest_base": bridge["foundational_strength"]["weakest_base_for_imported_analytic_causal_theorem"],
        "next_gate": bridge["next_gate"],
    }
    value["route_selection"] = [
        {"rank": 1, "route": "STRICT_386_PAIRING_SUSPENSION_BRIDGE", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "MEDIUM", "dependency_depth": "LOW", "recommendation": "Decide the five-row suspension convention and independently replay the exact graded-adjoint Green identity with one canonical pairing."},
        {"rank": 2, "route": "STRICT_386_FULL_PAIRING_D", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "MEDIUM", "recommendation": "Extend the selected pairing across the 356-row complement and serialize the background-specific local D on the same carrier."},
        {"rank": 3, "route": "STRICT_386_Q2_GREEN_COMPATIBILITY", "branch": "STRICT_PURE_WEYL_386", "scientific_leverage": "HIGH", "tractability": "LOW", "dependency_depth": "HIGH", "recommendation": "After the paired carrier and D bridge, test the target-action q2 against the same transported causal contraction."},
        {"rank": 4, "route": "DIRECT_SPACETIME_Q26_HADAMARD", "branch": "BERGER_POSITIVE_CLOCK_54", "scientific_leverage": "VERY_HIGH", "tractability": "LOW", "dependency_depth": "MEDIUM", "recommendation": "Retain the analytically mature parallel route through a direct nonstationary q26-equivariant distributional selection."},
        {"rank": 5, "route": "BACH_FLAT_NONLINEAR_CARTAN", "branch": "PURE_WEYL_BACH_FLAT_RANK310", "scientific_leverage": "HIGH", "tractability": "MEDIUM", "dependency_depth": "MEDIUM", "recommendation": "Use the broad curved strict causal branch as the independent nonlinear compatibility control."},
    ]
    value["research_queue"] = [
        {"priority": 1, "branch": "STRICT_PURE_WEYL_386", "object": "five-row pairing/suspension bridge", "why": "The unary bytes now agree exactly; the remaining endpoint discrepancy is localized to the sign of the transported ghost/identity pairing."},
        {"priority": 2, "branch": "STRICT_PURE_WEYL_386", "object": "356-row complement pairing and local D", "why": "This is the smallest route from a common endpoint to one accepted full causal carrier."},
        {"priority": 3, "branch": "STRICT_PURE_WEYL_386", "object": "same-carrier q2/Green compatibility", "why": "It is the first nonlinear admission gate after the unary carrier is paired and D-equivariant."},
        {"priority": 4, "branch": "BERGER_POSITIVE_CLOCK_54", "object": "direct spacetime q26-equivariant nonstationary Hadamard selection", "why": "Berger remains the shortest independent route toward a full-carrier Hadamard/Ward result."},
        {"priority": 5, "branch": "PURE_WEYL_BACH_FLAT_RANK310", "object": "same-carrier nonlinear cyclic D-Cartan transfer", "why": "It tests nonlinear survival on the broadest curved strict causal control."},
    ]
    value["provenance"]["inputs"] = [
        *previous["provenance"]["inputs"],
        {"path": str(PREDECESSOR.relative_to(ROOT)), "sha256": sha(PREDECESSOR), "role": "immutable V4 atlas predecessor"},
        {"path": str(BRIDGE.relative_to(ROOT)), "sha256": sha(BRIDGE), "role": "exact strict thirty-row endpoint q1 content bridge"},
        {"path": str(WITNESS.relative_to(ROOT)), "sha256": sha(WITNESS), "role": "700-column coordinate-to-covariant proof witness"},
    ]
    value["claim_flags"].update({
        "v4_preserved": True,
        "strict_386_endpoint_q1_content_identified": True,
        "strict_386_all_700_bach_columns_match": True,
        "strict_386_pairing_suspension_bridge_certified": False,
        "strict_386_common_bytes_identified": False,
        "strict_full_386_pairing_serialized": False,
        "strict_386_q2_green_compatibility_certified": False,
    })
    obsolete = "that the Gate-V5 local q1 bytes equal the 386-row causal endpoint bytes"
    value["does_not_establish"] = [
        item for item in previous["does_not_establish"] if item != obsolete
    ] + [
        "that the simultaneously transported causal pairing equals the Gate-canonical pairing on the five ghost/identity rows",
        "a canonical paired Green theorem on the entire 386-row Gate-convention carrier",
        "q2 or local D compatibility on the common causal bytes",
        "a passed Gate A, Hadamard state, Ward theorem, QME restoration, residual transfer or Lorentzian quantum theory",
    ]
    value["independent_checker"] = {
        "path": "foundations/check_lorentzian_weyl_bv_completion_atlas_v5.py",
        "checks": [
            "V4 preservation and scoped cell mutation", "seven-by-eleven stage closure",
            "80/80 unary table and 700/700 Bach-column projection",
            "common q1 digest", "five-row pairing sign firewall",
            "Gate-A and full-carrier firewalls", "unchanged Berger decision chain",
            "updated route ranking", "content hashes", "canonical digest",
        ],
        "expected_digest": "",
    }
    value["independent_checker"]["expected_digest"] = digest(value)
    return value


def render(value: dict[str, Any]) -> str:
    bridge = value["strict_endpoint_q1_content_bridge"]
    lines = [
        "# Lorentzian Weyl BV completion atlas V5", "", "## Outcome", "",
        value["answer"], "", "## Exact endpoint-content result", "",
        f"- Unary tables: **{bridge['arrow_tables_matching']}/80** match.",
        f"- Independent Bach columns: **{bridge['bach_columns_matching']}/700** match through **{bridge['triangular_equations']:,}** exact triangular equations.",
        f"- Common q1: **{bridge['common_nonzero_coefficients']}** nonzero rational coefficients; `{bridge['common_q1_sha256']}`.",
        f"- Finite bridge base: **{bridge['finite_bridge_base']}**; analytic causal weakest base: **{bridge['analytic_causal_weakest_base']}**.",
        "", "## Pairing boundary", "",
        "The field/equation pairing and the original endpoint ghost/identity pairing pull back to the Gate-canonical blocks. After simultaneous causal sign transport, the five-row ghost/identity block pulls back to **-I_5**, not **I_5**. This localizes the next test without treating the sign as already harmless.",
        "", "## Branch overview", "",
        "| branch | first unclosed gate | next decisive object |", "|---|---|---|",
    ]
    for item in value["branches"]:
        lines.append(f"| `{item['id']}` | `{item['first_unclosed_gate']}` | {item['next_decisive_object']} |")
    lines += ["", "## Updated route selection", "", "| rank | route | leverage | tractability | dependency depth |", "|---:|---|---|---|---|---|"]
    for item in value["route_selection"]:
        lines.append(f"| {item['rank']} | `{item['route']}` | {item['scientific_leverage']} | {item['tractability']} | {item['dependency_depth']} |")
    lines += [
        "", "## Why the ranking changed", "",
        "V4's first-ranked endpoint-content experiment succeeded exhaustively. Repeating the endpoint search is no longer useful. The shortest decisive route is now to determine whether the five-row sign is a graded suspension convention compatible with one full paired Green theorem; only after that should the programme spend effort on the 356-row complement and nonlinear q2/D compatibility.",
        "", "## Reproduction", "", "```text",
        "python3 foundations/build_lorentzian_weyl_bv_completion_atlas_v5.py --check",
        "python3 foundations/check_lorentzian_weyl_bv_completion_atlas_v5.py",
        "python3 foundations/verify_lorentzian_weyl_bv_completion_atlas_v5.py",
        "python3 -m unittest foundations/tests/test_lorentzian_weyl_bv_completion_atlas_v5.py",
        "```", "", "## Boundaries", "",
    ]
    lines.extend(f"- This does not establish {item}." for item in value["does_not_establish"])
    return "\n".join(lines) + "\n"


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = ((RESULT, generated()[0]), (REPORT, generated()[1]))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V5: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V5: wrote result and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
