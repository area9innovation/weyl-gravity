#!/usr/bin/env python3
"""Independent exact checker for the typed M4L cyclic-pairing closure."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json"
PATHS = {
    "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1": HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json",
    "STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1": HERE / "certificates/STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1.json",
    "STRICT_386_FULL_D_ACTION_V1": HERE / "certificates/STRICT_386_FULL_D_ACTION_V1.json",
    "STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1": HERE / "certificates/STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1.json",
    "STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1": HERE / "certificates/STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1.json",
    "STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1": HERE / "certificates/STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1.json",
    "STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1": HERE / "certificates/STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1.json",
    "CLASSICAL_IMPORT_GATE_V19_RECONCILIATION": HERE / "certificates/CLASSICAL_IMPORT_GATE_V19_RECONCILIATION.json",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def sparse_rank(entries: list[dict[str, Any]], dimension: int) -> int:
    rows: list[dict[int, Fraction]] = [dict() for _ in range(dimension)]
    for entry in entries:
        rows[entry["left_index"]][entry["right_index"]] = Fraction(entry["coefficient"])
    rank = 0
    for column in range(dimension):
        pivot = next((row for row in range(rank, dimension) if rows[row].get(column)), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        pivot_row = {key: value / scale for key, value in rows[rank].items()}
        rows[rank] = pivot_row
        for row in range(dimension):
            coefficient = rows[row].get(column)
            if row == rank or not coefficient:
                continue
            updated = dict(rows[row])
            for key, value in pivot_row.items():
                reduced = updated.get(key, Fraction(0)) - coefficient * value
                if reduced:
                    updated[key] = reduced
                else:
                    updated.pop(key, None)
            rows[row] = updated
        rank += 1
    return rank


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = json.loads(RESULT.read_text()) if value is None else value
    errors: list[str] = []
    if value.get("result_id") != "STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")

    dependencies = {result_id: json.loads(path.read_text()) for result_id, path in PATHS.items()}
    actual_pins = value.get("artifact_pins", [])
    if len(actual_pins) != len(PATHS):
        errors.append("artifact pin count")
    for item in actual_pins:
        result_id = item.get("result_or_artifact_id")
        path = PATHS.get(result_id)
        if path is None or item.get("path") != str(path.relative_to(ROOT)) or item.get("sha256") != sha(path):
            errors.append("artifact pin " + str(result_id))

    pairing = dependencies["STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1"]
    rows = pairing["component_basis"]["rows"]
    entries = pairing["pairing_serialization"]["entries"]
    matrix = {(entry["left_index"], entry["right_index"]): Fraction(entry["coefficient"]) for entry in entries}
    rank = sparse_rank(entries, 386)
    skew = sum(matrix.get((right, left), 0) != -coefficient for (left, right), coefficient in matrix.items())
    degree = sum(rows[left]["degree"] + rows[right]["degree"] != 1 for left, right in matrix)
    covered = {index for pair in matrix for index in pair}
    replay = value.get("pairing_replay", {})
    if (
        len(rows) != 386 or len({row["row_id"] for row in rows}) != 386
        or len(entries) != 410 or rank != 386 or skew or degree or len(covered) != 386
        or replay.get("carrier_rows") != 386 or replay.get("exact_rational_rank") != 386
        or replay.get("nonzero_ordered_pairing_entries") != 410
        or replay.get("rows_with_nonzero_partner") != 386
        or replay.get("odd_skew_defects") != 0 or replay.get("pairing_degree_defects") != 0
        or (replay.get("endpoint_rows"), replay.get("auxiliary_rows"), replay.get("mapping_cone_and_cotangent_rows")) != (30, 36, 320)
        or (replay.get("endpoint_pairing_entries"), replay.get("auxiliary_pairing_entries"), replay.get("mapping_cone_pairing_entries")) != (30, 60, 320)
        or replay.get("basis_sha256") != pairing["canonical_hashes"]["component_basis_sha256"]
        or replay.get("pairing_sha256") != pairing["canonical_hashes"]["pairing_serialization_sha256"]
    ):
        errors.append("independent full-pairing replay")

    graph = dependencies["STRICT_386_GRAPH_Q1_SDR_COMPONENT_JETS_V1"]
    d_action = dependencies["STRICT_386_FULL_D_ACTION_V1"]
    q2 = dependencies["STRICT_386_SOURCE_Q2_COMMON_ASSEMBLY_V1"]
    q3 = dependencies["STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1"]
    binding = dependencies["STRICT_386_COMMON_ENDPOINT_SDR_BINDING_V1"]
    expected_cyclic = {
        "pairing_rank_defects": 0,
        "odd_skew_defects": 0,
        "pairing_degree_defects": 0,
        "graph_q1_suspended_cyclicity_defects_after_PBW_reduction": graph["exact_replay"]["transported_R_PBW_reduced_cyclicity_defects"],
        "endpoint_homotopy_cyclicity_defects": graph["exact_replay"]["H_alg_graph_cyclicity_defects"],
        "endpoint_SDR_cyclicity_defects_on_common_manifest": binding["exact_replay"]["endpoint_SDR_cyclicity_defects"],
        "D_formal_skew_adjoint_pairing_entries_checked": d_action["exact_replay"]["formal_skew_adjoint_pairing_entries_checked"],
        "D_formal_skew_adjoint_defects": d_action["exact_replay"]["formal_skew_adjoint_defects"],
        "q2_cyclicity_equalities_checked": q2["q2_cyclicity_replay"]["shifted_mass_equalities_checked"] + q2["q2_cyclicity_replay"]["auxiliary_Diff_master_density_coefficients_checked"],
        "graph_q2_cyclicity_defects": q2["q2_cyclicity_replay"]["graph_386_q2_cyclicity_defects"],
        "q3_cyclicity_equalities_checked": q3["q3_cyclicity_replay"]["auxiliary_q3_equalities_checked"],
        "graph_q3_cyclicity_defects_mod_d": q3["q3_cyclicity_replay"]["graph_386_q3_cyclicity_defects_mod_d"],
        "common_manifest_compatibility_defects": binding["exact_replay"]["compatibility_defects"],
    }
    if value.get("local_cyclicity_replay") != expected_cyclic or any(
        item for key, item in expected_cyclic.items() if key.endswith("defects")
    ) or expected_cyclic["D_formal_skew_adjoint_pairing_entries_checked"] != 410:
        errors.append("local cyclicity projection")

    type_audit = dependencies["STRICT_RESIDUAL_SDR_TYPE_AND_LOCALITY_AUDIT_V1"]
    split = value.get("type_split", {})
    if (
        split.get("old_requirement_disposition") != "REJECT_AS_ONE_UNTYPED_LOCAL_AND_RESIDUAL_OBJECT"
        or split.get("M4L_LOCAL_GRAPH_CYCLIC_PAIRING", {}).get("status") != "COMPLETE"
        or split.get("M4R_TYPED_RESIDUAL_CYCLICITY", {}).get("status") != "NOT_DEFINED_BEFORE_M3R"
        or type_audit["type_census"]["dfinite_total_residual_coordinates"] != 470
        or type_audit["claim_flags"]["M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED"] is not False
    ):
        errors.append("local/residual type split")
    ledger = value.get("obligation_ledger", [])
    if len(ledger) != 7 or [item.get("status") for item in ledger[:-1]] != ["COMPLETE"] * 6 or ledger[-1].get("status") != "BLOCKED_BY_M3R_NOT_CONSTRUCTED":
        errors.append("obligation ledger")

    flags = value.get("claim_flags", {})
    for key in (
        "STRICT_386_FULL_LOCAL_ODD_PAIRING_NONDEGENERATE",
        "STRICT_386_LOCAL_Q1_SDR_D_Q2_Q3_CYCLICITY_COMPLETE",
        "M4L_LOCAL_GRAPH_CYCLIC_PAIRING_COMPLETE",
    ):
        if flags.get(key) is not True:
            errors.append("missing positive flag " + key)
    for key in (
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE", "M3R_TYPED_RESIDUAL_COMPARISON_CONSTRUCTED",
        "FULL_RESIDUAL_CYCLIC_PAIRING_CERTIFIED", "NEW_GATE_A_TOP_LEVEL_HASH_ACCEPTED",
        "CLASSICAL_IMPORT_GATE_PASSED", "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        if flags.get(key) is not False:
            errors.append("claim promotion " + key)
    if value.get("gate_disposition") != {
        "M4L_LOCAL_GRAPH_CYCLIC_PAIRING": "COMPLETE",
        "M4R_TYPED_RESIDUAL_CYCLICITY": "OPEN_BLOCKED_BY_M3R",
        "M3R_TYPED_RESIDUAL_COMPARISON": "OPEN",
        "M1_COMMON_STRICT_SNAPSHOT": "OPEN",
        "top_level_gate_a_hashes_accepted_by_this_result": 0,
        "classical_import_gate_a_status": "FAIL_CLOSED",
    }:
        errors.append("Gate disposition")
    projection = (
        "scope", "artifact_pins", "pairing_replay", "local_cyclicity_replay",
        "obligation_ledger", "type_split", "foundational_strength", "gate_disposition",
        "claim_flags", "does_not_establish", "next_gate",
    )
    try:
        expected_digest = digest({key: value[key] for key in projection})
    except KeyError as error:
        errors.append("canonical projection missing " + str(error))
    else:
        if value.get("independent_checker", {}).get("expected_digest") != expected_digest:
            errors.append("canonical digest")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
