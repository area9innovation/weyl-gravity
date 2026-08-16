#!/usr/bin/env python3
"""Independent receiver for the formal D-finite cotangent-dual comparison."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.json"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
M3R = HERE / "certificates/STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1.json"
OBSTRUCTION = HERE / "certificates/STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1.json"
LOCAL_PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"


Sparse = dict[tuple[int, int], int]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def entries(value: dict[str, Any]) -> Sparse:
    result: Sparse = {}
    for row, column, coefficient in value["entries"]:
        number = int(coefficient)
        if str(number) != coefficient or not number or (row, column) in result:
            raise ValueError(f"invalid sparse entry in {value['name']}")
        result[row, column] = number
    return result


def transpose(value: Sparse, sign: int = 1) -> Sparse:
    return {(column, row): sign * coefficient for (row, column), coefficient in value.items()}


def multiply(left: Sparse, right: Sparse) -> Sparse:
    right_by_row: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for (row, column), coefficient in right.items():
        right_by_row[row].append((column, coefficient))
    result: dict[tuple[int, int], int] = defaultdict(int)
    for (row, middle), left_coefficient in left.items():
        for column, right_coefficient in right_by_row.get(middle, []):
            result[row, column] += left_coefficient * right_coefficient
    return {key: value for key, value in result.items() if value}


def add(*values: Sparse) -> Sparse:
    result: dict[tuple[int, int], int] = defaultdict(int)
    for value in values:
        for key, coefficient in value.items():
            result[key] += coefficient
    return {key: value for key, value in result.items() if value}


def scale(value: Sparse, coefficient: int) -> Sparse:
    return {key: coefficient * entry for key, entry in value.items() if coefficient * entry}


def identity(size: int) -> Sparse:
    return {(index, index): 1 for index in range(size)}


def serialized(value: Sparse) -> list[list[Any]]:
    return [[row, column, str(coefficient)] for (row, column), coefficient in sorted(value.items())]


def degree_census(block: dict[str, Any]) -> dict[str, Any]:
    basis_degree: dict[int, int] = {}
    dimensions: Counter[int] = Counter()
    for sector in block["full_sectors"]:
        dimensions[sector["ghost_number"]] += sector["dimension"]
        for index in range(sector["start"], sector["stop"]):
            basis_degree[index] = sector["ghost_number"]
    ranks: Counter[int] = Counter()
    rows: dict[int, set[int]] = defaultdict(set)
    columns: dict[int, set[int]] = defaultdict(set)
    degree_defects = 0
    for (row, column), coefficient in entries(block["matrices"]["q0"]).items():
        source = basis_degree[column]
        target = basis_degree[row]
        if coefficient not in (-1, 1) or target != source + 1:
            degree_defects += 1
        ranks[source] += 1
        rows[source].add(row)
        columns[source].add(column)
    partial_identity_defects = sum(
        ranks[degree] - min(len(rows[degree]), len(columns[degree])) for degree in ranks
    )
    cohomology = {
        str(degree): dimensions[degree] - ranks[degree] - ranks[degree - 1]
        for degree in range(-1, 3)
    }
    return {
        "energy": block["energy"],
        "chain_dimensions_by_degree": {str(key): dimensions[key] for key in range(-1, 3)},
        "differential_ranks_by_source_degree": {str(key): ranks[key] for key in range(-1, 2)},
        "cohomology_dimensions_by_degree": cohomology,
        "degree_defects": degree_defects,
        "partial_identity_defects": partial_identity_defects,
        "declared_residual_dimension": block["residual_dimension"],
        "degree_one_residual_dimension": cohomology["1"],
        "sector_degree_dictionary": {
            sector["name"]: sector["ghost_number"] for sector in block["full_sectors"]
        },
    }


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    sources = {
        "STRICT_DFINITE_RESIDUAL_SDR_V1": DFINITE,
        "STRICT_ENDPOINT_TO_RESIDUAL_SPECTRAL_COMPARISON_V1": M3R,
        "STRICT_RESIDUAL_CYCLIC_CARRIER_OBSTRUCTION_V1": OBSTRUCTION,
        "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1": LOCAL_PAIRING,
    }
    pins = {item["result_or_artifact_id"]: item for item in value.get("provenance", {}).get("inputs", [])}
    for result_id, path in sources.items():
        require(result_id in pins, f"missing provenance pin {result_id}")
        if result_id in pins:
            require(pins[result_id]["path"] == str(path.relative_to(ROOT)), f"path drift for {result_id}")
            require(pins[result_id]["sha256"] == sha(path), f"hash drift for {result_id}")

    dfinite = load(DFINITE)
    local_pairing = load(LOCAL_PAIRING)
    require(value.get("result_id") == "STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1", "result identity drift")
    require(value.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"], "dependency tags drift")
    require(local_pairing["pairing_serialization"]["degree"] == -1, "local pairing degree drift")

    censuses = [degree_census(block) for block in dfinite["blocks"]]
    require(value.get("original_source_cohomology", {}).get("blocks") == censuses, "original cohomology census drift")
    require([item["cohomology_dimensions_by_degree"]["0"] for item in censuses] == [10, 40, 82, 136, 202], "H0 block dimensions drift")
    require(all(item["cohomology_dimensions_by_degree"]["1"] == 0 for item in censuses), "original H1 is not zero")
    require(all(not item["degree_defects"] and not item["partial_identity_defects"] for item in censuses), "original q0 partial-identity audit failed")

    formal = value.get("formal_cotangent_completion", {})
    comparisons = formal.get("block_comparisons", [])
    require(len(comparisons) == len(dfinite["blocks"]) == 5, "dual block count drift")
    global_hash_rows = []
    total_full = total_residual = 0
    for block, comparison in zip(dfinite["blocks"], comparisons, strict=False):
        n = block["full_dimension"]
        r = block["residual_dimension"]
        total_full += n
        total_residual += r
        require(comparison.get("energy") == block["energy"], f"energy alignment drift at {block['energy']}")
        require((comparison.get("cotangent_full_dimension"), comparison.get("cotangent_residual_dimension")) == (2 * n, 2 * r), f"cotangent dimensions drift at {block['energy']}")
        dual_degree_counts: Counter[int] = Counter()
        pairing_degree_defects = 0
        for sector in block["full_sectors"]:
            dual_degree = 1 - sector["ghost_number"]
            dual_degree_counts[dual_degree] += sector["dimension"]
            if sector["ghost_number"] + dual_degree != 1:
                pairing_degree_defects += sector["dimension"]
        require(
            comparison.get("dual_full_degree_counts") == {
                str(key): dual_degree_counts[key] for key in sorted(dual_degree_counts)
            },
            f"dual degree census drift at {block['energy']}",
        )

        q = entries(block["matrices"]["q0"])
        iota = entries(block["matrices"]["iota_cl"])
        pi = entries(block["matrices"]["pi_cl"])
        homotopy = entries(block["matrices"]["s_cl"])
        qd = transpose(q, -1)
        iotad = transpose(pi)
        pid = transpose(iota)
        sd = transpose(homotopy, -1)
        dual_maps = comparison.get("dual_maps", {})
        expected_maps = {
            "q_dual": (qd, n, n),
            "iota_dual": (iotad, n, r),
            "pi_dual": (pid, r, n),
            "s_dual": (sd, n, n),
            "q_res_dual": ({}, r, r),
        }
        hash_row: dict[str, str] = {}
        for name, (matrix, rows, columns) in expected_maps.items():
            spec = dual_maps.get(name, {})
            expected_hash = digest(serialized(matrix))
            require((spec.get("rows"), spec.get("columns"), spec.get("entry_count")) == (rows, columns, len(matrix)), f"{name} shape/count drift at {block['energy']}")
            require(spec.get("entries_sha256") == expected_hash, f"{name} hash drift at {block['energy']}")
            hash_row[name] = expected_hash
        global_hash_rows.append(hash_row)

        defects = {
            "q_dual_squared_defects": len(multiply(qd, qd)),
            "pi_dual_iota_dual_defects": len(add(multiply(pid, iotad), scale(identity(r), -1))),
            "cotangent_contraction_defects": len(add(multiply(iotad, pid), multiply(qd, sd), multiply(sd, qd), scale(identity(n), -1))),
            "dual_synthesis_chain_defects": len(multiply(qd, iotad)),
            "dual_analysis_chain_defects": len(multiply(pid, qd)),
            "s_dual_squared_defects": len(multiply(sd, sd)),
            "s_dual_iota_dual_defects": len(multiply(sd, iotad)),
            "pi_dual_s_dual_defects": len(multiply(pid, sd)),
            "canonical_pairing_q_cyclicity_defects": len(add(qd, scale(transpose(q, -1), -1))),
            "canonical_pairing_homotopy_skew_defects": len(add(sd, scale(transpose(homotopy, -1), -1))),
            "canonical_pairing_degree_defects": pairing_degree_defects,
            "cotangent_inclusion_isometry_defects": len(add(multiply(pi, iota), scale(identity(r), -1))),
        }
        require(comparison.get("exact_identity_replay") == defects, f"dual identity replay drift at {block['energy']}")
        require(not any(defects.values()), f"nonzero dual identity defect at {block['energy']}")

    require(formal.get("global_dual_map_hash") == digest(global_hash_rows), "global dual-map digest drift")
    require((formal.get("full_dimension"), formal.get("residual_dimension")) == (2 * total_full, 2 * total_residual) == (8980, 940), "global cotangent dimensions drift")
    require((formal.get("full_pairing_rank"), formal.get("residual_pairing_rank")) == (8980, 940), "canonical pairing ranks drift")
    require(formal.get("all_declared_identity_defects") == 0, "global identity flag drift")

    impossible = value.get("same_source_impossibility", {})
    require(impossible.get("original_source_total_cohomology_dimension") == 470, "original cohomology total drift")
    require(impossible.get("original_source_degree_one_cohomology_dimension") == 0, "original H1 summary drift")
    require(impossible.get("desired_cotangent_residual_dimension") == 940, "desired residual dimension drift")
    require(impossible.get("same_source_deformation_retract_to_940_possible") is False, "same-source impossibility firewall drift")

    support = value.get("action_support_identification", {})
    require(support.get("status") == "OPEN", "action/support identification promoted")
    require(support.get("same_endpoint_carrier_identification") is False, "same-carrier identification promoted")
    flags = value.get("claim_flags", {})
    require(flags.get("ORIGINAL_DFINITE_H1_ZERO") is True, "H1-zero flag missing")
    require(flags.get("FORMAL_8980_COTANGENT_SOURCE_CONSTRUCTED") is True, "formal cotangent source flag missing")
    require(flags.get("FORMAL_940_COTANGENT_RESIDUAL_COMPARISON_CONSTRUCTED") is True, "formal residual comparison flag missing")
    require(flags.get("FORMAL_COTANGENT_PAIRING_NONDEGENERATE") is True, "formal pairing rank flag missing")
    require(flags.get("FORMAL_COTANGENT_SDR_CYCLIC") is True, "formal cyclic-SDR flag missing")
    for key in (
        "UNCHANGED_4490_SOURCE_CAN_RETRACT_TO_940_RESIDUAL",
        "FORMAL_DUAL_IDENTIFIED_WITH_ACTION_SUPPORT_DUAL",
        "M3RC_ACTION_SUPPORT_IDENTIFICATION_COMPLETE",
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE",
        "CLASSICAL_IMPORT_GATE_PASSED",
        "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED",
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        require(flags.get(key) is False, f"firewall promoted: {key}")

    expected_digest = digest({
        key: value[key]
        for key in (
            "scope", "original_source_cohomology", "same_source_impossibility",
            "formal_cotangent_completion", "action_support_identification", "m3rc_split",
            "foundational_strength", "claim_flags",
        )
    }) if all(key in value for key in (
        "scope", "original_source_cohomology", "same_source_impossibility",
        "formal_cotangent_completion", "action_support_identification", "m3rc_split",
        "foundational_strength", "claim_flags",
    )) else ""
    require(value.get("independent_checker", {}).get("expected_digest") == expected_digest, "canonical result digest drift")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_DFINITE_COTANGENT_DUAL_COMPARISON: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - unchanged D-finite source has exact H0=470 and H1=0")
        print("  - formal 8980-to-940 cotangent SDR and canonical odd pairing replay exactly")
        print("  - action/support identification remains open")
    for error in errors:
        print("  - " + error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
