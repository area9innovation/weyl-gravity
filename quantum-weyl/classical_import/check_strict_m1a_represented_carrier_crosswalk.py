#!/usr/bin/env python3
"""Independent receiver for the M1A3 represented-carrier crosswalk."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1.json"
REPORT = HERE / "REPORT_STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1.md"
GRADING = HERE / "certificates/STRICT_M1A_CARRIER_GRADING_CONVENTION_AUDIT_V1.json"
LOCAL_EXTENSION = HERE / "certificates/STRICT_M1A_LOCAL_SEMANTIC_EXTENSION_V1.json"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
REPRESENTED = HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
ACTION_DUAL = HERE / "certificates/STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.json"
RESIDUAL_CYCLICITY = HERE / "certificates/STRICT_TYPED_RESIDUAL_CYCLICITY_V1.json"
INPUTS = (GRADING, LOCAL_EXTENSION, DFINITE, REPRESENTED, ACTION_DUAL, RESIDUAL_CYCLICITY)

SECTOR_TO_SPECIES = {
    "diff_ghost": "xi", "weyl_ghost": "omega", "metric_trace": "g", "metric_tf": "g",
    "metric_antifield": "g_star", "diff_ghost_antifield": "xi_star",
    "trace_antifield": "g_star", "weyl_ghost_antifield": "omega_star",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    grading, local_extension, dfinite, represented, action, cyclicity = [load(path) for path in INPUTS]
    if value.get("result_id") != "STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1" or value.get("lifecycle") != "CLASSIFIED":
        errors.append("identity/lifecycle")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"]:
        errors.append("dependency tags")
    provenance = {row.get("path"): row for row in value.get("provenance", {}).get("inputs", [])}
    for path in INPUTS:
        relative = str(path.relative_to(ROOT))
        if provenance.get(relative, {}).get("sha256") != file_hash(path):
            errors.append(f"input hash {relative}")
    if local_extension["counts"]["local_386_rows_fully_namespaced_after_this_result"] != 386:
        errors.append("M1A2 prerequisite")

    species_rows: dict[str, list[dict[str, Any]]] = {}
    for row in grading["local_endpoint_typed_rows"]:
        species = row["authority"]["generator"].rsplit("/", 1)[-1]
        species_rows.setdefault(species, []).append(row)
    species_semantics = {
        species: {field: rows[0][field] for field in (
            "chain_degree", "bv_ghost_number", "antifield_number", "form_degree",
            "Grassmann_parity", "mass_dimension", "Weyl_weight",
        )}
        for species, rows in species_rows.items()
    }

    represented_rows = value.get("represented_endpoint_rows", [])
    test_rows = value.get("test_nonminimal_rows", [])
    primal_rows = value.get("action_residual_primal_rows", [])
    dual_rows = value.get("action_residual_dual_rows", [])
    if (len(represented_rows), len(test_rows), len(primal_rows), len(dual_rows)) != (4080, 410, 470, 470):
        errors.append("carrier row counts")

    represented_cursor = test_cursor = 0
    partitions: dict[int, str] = {}
    degrees: dict[int, int] = {}
    represented_label_to_index: dict[str, int] = {}
    for block in dfinite["blocks"]:
        for sector in block["full_sectors"]:
            for sector_index in range(sector["dimension"]):
                block_index = sector["start"] + sector_index
                global_index = block["full_offset"] + block_index
                label = block["full_basis"][block_index]
                if sector["name"] in {"antighost", "multiplier"}:
                    if test_cursor >= len(test_rows):
                        errors.append("test row truncation")
                        break
                    row = test_rows[test_cursor]
                    test_cursor += 1
                    partitions[global_index] = "test"
                    degrees[global_index] = sector["ghost_number"]
                    partner_name = "multiplier" if sector["name"] == "antighost" else "antighost"
                    partner = next(item for item in block["full_sectors"] if item["name"] == partner_name)
                    expected = {
                        "comparison_index": test_cursor - 1,
                        "source_label": label,
                        "energy": block["energy"],
                        "dfinite_global_index": global_index,
                        "dfinite_block_index": block_index,
                        "dfinite_sector": sector["name"],
                        "sector_index": sector_index,
                        "chain_degree": sector["ghost_number"],
                        "doublet_partner_label": block["full_basis"][partner["start"] + sector_index],
                        "doublet_partner_global_index": block["full_offset"] + partner["start"] + sector_index,
                        "q0_doublet_role": "SOURCE" if sector["name"] == "antighost" else "TARGET",
                        "source_disposition": "EXCLUDED_FROM_AUTHORITATIVE_LOCAL_GRAPH_BV_386",
                    }
                    if any(row.get(key) != expected_value for key, expected_value in expected.items()):
                        errors.append(f"test row crosswalk {label}")
                    for field in ("bv_ghost_number", "antifield_number", "form_degree", "Grassmann_parity", "mass_dimension", "Weyl_weight", "intrinsic_jet_order_bound"):
                        tagged = row.get(field)
                        if not isinstance(tagged, dict) or tagged.get("status") != "NOT_APPLICABLE":
                            errors.append(f"test local field applicability {label}:{field}")
                    continue

                if represented_cursor >= len(represented_rows):
                    errors.append("represented row truncation")
                    break
                row = represented_rows[represented_cursor]
                represented_cursor += 1
                partitions[global_index] = "represented"
                degrees[global_index] = sector["ghost_number"]
                represented_label_to_index[label] = represented_cursor - 1
                species = SECTOR_TO_SPECIES[sector["name"]]
                semantics = species_semantics[species]
                expected = {
                    "represented_index": represented_cursor - 1,
                    "source_label": label,
                    "energy": block["energy"],
                    "dfinite_global_index": global_index,
                    "dfinite_block_index": block_index,
                    "dfinite_sector": sector["name"],
                    "sector_index": sector_index,
                    "local_species_id": species,
                    "local_endpoint_row_ids": [item["row_id"] for item in species_rows[species]],
                    "local_endpoint_row_indices": [item["index"] for item in species_rows[species]],
                    **semantics,
                }
                if any(row.get(key) != expected_value for key, expected_value in expected.items()):
                    errors.append(f"represented row crosswalk {label}")
                if row.get("conformal_compact_weight") != block["energy"]:
                    errors.append(f"represented compact weight {label}")

    if represented_cursor != 4080 or test_cursor != 410 or len(partitions) != 4490:
        errors.append("exhaustive partition")
    q_cross = q_degree = 0
    for block in dfinite["blocks"]:
        for target, source_index, coefficient in block["matrices"]["q0"]["entries"]:
            target_global = block["full_offset"] + target
            source_global = block["full_offset"] + source_index
            q_cross += int(partitions.get(target_global) != partitions.get(source_global))
            q_degree += int(degrees.get(target_global) != degrees.get(source_global, 0) + 1)
            if coefficient != "1":
                errors.append("q0 coefficient")
    if q_cross or q_degree:
        errors.append("q0 partition/degree replay")

    basis = represented["ordered_residual_basis"]
    action_rows = action["action_pairing_identification"]["dual_dictionary"]
    physical = {row["energy"]: row for row in represented["comparison"]["physical_offsets"]}
    blocks = {row["energy"]: row for row in dfinite["blocks"]}
    for index, (basis_row, action_row, primal, dual) in enumerate(zip(basis, action_rows, primal_rows, dual_rows, strict=True)):
        block = blocks[basis_row["energy"]]
        chirality_size = block["dimensions"]["chirality"]
        offset = basis_row["chirality_index"] + (0 if basis_row["chirality"] == "W_PLUS" else chirality_size)
        block_index = physical[basis_row["energy"]]["metric_tf_physical_start"] + offset
        source_label = block["full_basis"][block_index]
        common = {
            "pair_index": index,
            "energy": basis_row["energy"],
            "chirality": basis_row["chirality"],
            "family": basis_row["family"],
            "two_m_left": basis_row["two_m_left"],
            "two_m_right": basis_row["two_m_right"],
            "source_represented_endpoint_index": represented_label_to_index[source_label],
            "source_coordinate_label": source_label,
            "source_dfinite_global_index": block["full_offset"] + block_index,
        }
        if any(primal.get(key) != expected for key, expected in common.items()) or primal.get("residual_index") != index or primal.get("residual_label") != basis_row["represented_residual_label"]:
            errors.append(f"primal residual crosswalk {index}")
        if (primal.get("chain_degree"), primal.get("bv_ghost_number"), primal.get("local_species_id"), primal.get("conformal_compact_weight")) != (0, 0, "g", basis_row["energy"]):
            errors.append(f"primal residual typing {index}")
        if any(dual.get(key) != expected for key, expected in common.items()) or dual.get("residual_index") != 470 + index or dual.get("residual_label") != action_row["formal_dual_label"]:
            errors.append(f"dual residual crosswalk {index}")
        if (dual.get("chain_degree"), dual.get("bv_ghost_number"), dual.get("local_species_id"), dual.get("conformal_compact_weight")) != (1, -1, "g_star", -basis_row["energy"]):
            errors.append(f"dual residual typing {index}")
        if dual.get("compact_source_representative") != action_row["compact_source_representative"] or dual.get("compact_source_support") is not True:
            errors.append(f"dual action source {index}")

    expected_counts = {
        "represented_endpoint_coordinates": 4080,
        "represented_endpoint_sectors": 8,
        "local_endpoint_species_crosswalked": 6,
        "test_nonminimal_coordinates_excluded": 410,
        "test_nonminimal_doublets": 205,
        "action_residual_primal_coordinates": 470,
        "action_residual_dual_coordinates": 470,
        "action_residual_total_coordinates": 940,
        "dfinite_partition_coordinates": 4490,
        "q0_cross_partition_defects": 0,
        "q0_chain_degree_defects": 0,
        "residual_crosswalk_defects": 0,
        "compact_source_support_defects": 0,
        "rows_with_unresolved_disposition": 0,
    }
    if value.get("counts") != expected_counts:
        errors.append("summary counts")
    hashes = value.get("row_payload_hashes", {})
    expected_hashes = {
        "represented_endpoint_rows_sha256": canonical_digest(represented_rows),
        "test_nonminimal_rows_sha256": canonical_digest(test_rows),
        "action_residual_primal_rows_sha256": canonical_digest(primal_rows),
        "action_residual_dual_rows_sha256": canonical_digest(dual_rows),
        "combined_typed_crosswalk_sha256": canonical_digest([represented_rows, test_rows, primal_rows, dual_rows]),
    }
    if hashes != expected_hashes:
        errors.append("row payload hashes")

    flags = value.get("claim_flags", {})
    for flag in (
        "M1A3_REPRESENTED_ENDPOINT_4080_FULLY_NAMESPACED",
        "M1A3_TEST_NONMINIMAL_410_DISPOSITION_COMPLETE",
        "M1A3_ACTION_RESIDUAL_940_FULLY_NAMESPACED",
        "M1A3_REPRESENTED_CROSSWALK_COMPLETE",
    ):
        if flags.get(flag) is not True:
            errors.append(f"positive flag {flag}")
    for flag in (
        "M1A4_IMMUTABLE_LEDGER_FREEZE_COMPLETE", "M1A_FULL_TYPED_CARRIER_LEDGER_COMPLETE",
        "M1B_REPRESENTED_COMPOSITE_CONTRACTION_COMPLETE", "M1C_COMMON_MANIFEST_REPLAY_COMPLETE",
        "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX", "FULL_CONTINUOUS_ALL_ENERGY_DUAL_IDENTIFIED",
        "CLASSICAL_IMPORT_GATE_PASSED", "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
        "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED", "QME_RESTORED", "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        if flags.get(flag) is not False:
            errors.append(f"fail-closed flag {flag}")

    replay = copy.deepcopy(value)
    expected_digest = replay.get("independent_checker", {}).get("expected_digest")
    replay.setdefault("independent_checker", {})["expected_digest"] = ""
    if expected_digest != canonical_digest(replay):
        errors.append("certificate digest")
    if not REPORT.exists():
        errors.append("human report absent")
    else:
        report = REPORT.read_text(encoding="utf-8")
        for token in ("4,080", "410", "205 exact scalar test doublets", "470 positive-frequency", "470 compact-source", "Gate A", "Hadamard", "QME"):
            if token not in report:
                errors.append(f"report token {token}")
    return errors


def main() -> int:
    errors = check(load(RESULT))
    if errors:
        print("STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("STRICT_M1A_REPRESENTED_CARRIER_CROSSWALK_V1: PASS")
    print("  - 4,080 represented endpoint coordinates crosswalked to six local species")
    print("  - 410 comparison-only coordinates classified as 205 excluded test doublets")
    print("  - 470 primal plus 470 compact-source action-dual residual rows fully namespaced")
    print("  - M1A4, Gate A, Hadamard and QME remain fail closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
