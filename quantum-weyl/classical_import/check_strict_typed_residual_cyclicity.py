#!/usr/bin/env python3
"""Independent receiver for the finite represented M4R cyclic contraction."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_TYPED_RESIDUAL_CYCLICITY_V1.json"
DFINITE = HERE / "certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
M3RCA = HERE / "certificates/STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1.json"
M3RCB = HERE / "certificates/STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1.json"
M4L = HERE / "certificates/STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1.json"

Sparse = dict[tuple[int, int], int]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def sparse(spec: dict[str, Any]) -> Sparse:
    result: Sparse = {}
    for row, column, coefficient in spec["entries"]:
        number = int(coefficient)
        if str(number) != coefficient or not number or (row, column) in result:
            raise ValueError(f"invalid sparse entry in {spec['name']}")
        result[row, column] = number
    return result


def transpose(value: Sparse, sign: int = 1) -> Sparse:
    return {(column, row): sign * coefficient for (row, column), coefficient in value.items()}


def add(*values: Sparse) -> Sparse:
    result: dict[tuple[int, int], int] = defaultdict(int)
    for value in values:
        for key, coefficient in value.items():
            result[key] += coefficient
    return {key: coefficient for key, coefficient in result.items() if coefficient}


def scale(value: Sparse, coefficient: int) -> Sparse:
    return {key: coefficient * entry for key, entry in value.items() if coefficient * entry}


def multiply(left: Sparse, right: Sparse) -> Sparse:
    right_by_row: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for (row, column), coefficient in right.items():
        right_by_row[row].append((column, coefficient))
    result: dict[tuple[int, int], int] = defaultdict(int)
    for (row, middle), coefficient in left.items():
        for column, right_coefficient in right_by_row.get(middle, []):
            result[row, column] += coefficient * right_coefficient
    return {key: coefficient for key, coefficient in result.items() if coefficient}


def identity(size: int) -> Sparse:
    return {(index, index): 1 for index in range(size)}


def shifted(value: Sparse, row_offset: int, column_offset: int) -> Sparse:
    return {(row + row_offset, column + column_offset): coefficient for (row, column), coefficient in value.items()}


def direct_sum(first: Sparse, second: Sparse, first_rows: int, first_columns: int) -> Sparse:
    return add(first, shifted(second, first_rows, first_columns))


def odd_pairing(size: int) -> Sparse:
    result = {(index, size + index): 1 for index in range(size)}
    result.update({(size + index, index): -1 for index in range(size)})
    return result


def serialized(value: Sparse) -> list[list[Any]]:
    return [[row, column, str(coefficient)] for (row, column), coefficient in sorted(value.items())]


def replay(block: dict[str, Any]) -> dict[str, Any]:
    n, r = block["full_dimension"], block["residual_dimension"]
    q = sparse(block["matrices"]["q0"])
    iota = sparse(block["matrices"]["iota_cl"])
    projection = sparse(block["matrices"]["pi_cl"])
    homotopy = sparse(block["matrices"]["s_cl"])
    qc = direct_sum(q, transpose(q, -1), n, n)
    ic = direct_sum(iota, transpose(projection), n, r)
    pc = direct_sum(projection, transpose(iota), r, n)
    sc = direct_sum(homotopy, transpose(homotopy, -1), n, n)
    jc, jh = odd_pairing(n), odd_pairing(r)
    defects = {
        "q_squared": len(multiply(qc, qc)),
        "projection_inclusion_identity": len(add(multiply(pc, ic), scale(identity(2 * r), -1))),
        "contraction_identity": len(add(multiply(ic, pc), multiply(qc, sc), multiply(sc, qc), scale(identity(2 * n), -1))),
        "inclusion_chain_map": len(multiply(qc, ic)),
        "projection_chain_map": len(multiply(pc, qc)),
        "homotopy_squared": len(multiply(sc, sc)),
        "homotopy_inclusion": len(multiply(sc, ic)),
        "projection_homotopy": len(multiply(pc, sc)),
        "source_q_cyclicity": len(add(multiply(transpose(qc), jc), multiply(jc, qc))),
        "residual_q_cyclicity": 0,
        "projection_equals_inclusion_sharp": len(add(multiply(transpose(pc), jh), scale(multiply(jc, ic), -1))),
        "homotopy_skew_adjoint": len(add(multiply(transpose(sc), jc), multiply(jc, sc))),
        "inclusion_isometry": len(add(multiply(transpose(ic), multiply(jc, ic)), scale(jh, -1))),
    }
    return {
        "energy": block["energy"],
        "formal_source_dimension": 2 * n,
        "action_identified_residual_dimension": 2 * r,
        "residual_primal_dimension": r,
        "residual_dual_dimension": r,
        "source_pairing_rank": 2 * n,
        "residual_pairing_rank": 2 * r,
        "map_hashes": {
            "q_cotangent": digest(serialized(qc)),
            "iota_cotangent": digest(serialized(ic)),
            "projection_cotangent": digest(serialized(pc)),
            "homotopy_cotangent": digest(serialized(sc)),
            "source_pairing": digest(serialized(jc)),
            "residual_pairing": digest(serialized(jh)),
        },
        "identity_defects": defects,
        "total_identity_defects": sum(defects.values()),
    }


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = load(RESULT) if value is None else value
    errors: list[str] = []

    def require(condition: object, message: str) -> None:
        if not condition:
            errors.append(message)

    inputs = {
        DFINITE: "STRICT_DFINITE_RESIDUAL_SDR_V1",
        M3RCA: "STRICT_DFINITE_COTANGENT_DUAL_COMPARISON_V1",
        M3RCB: "STRICT_M3RC_ACTION_SUPPORT_DUAL_IDENTIFICATION_V1",
        M4L: "STRICT_386_LOCAL_CYCLIC_PAIRING_CLOSURE_V1",
    }
    expected_pins = {
        str(path.relative_to(ROOT)): (result_id, sha(path)) for path, result_id in inputs.items()
    }
    actual_pins = {
        item.get("path"): (item.get("result_or_artifact_id"), item.get("sha256"))
        for item in value.get("provenance", {}).get("inputs", [])
    }
    require(actual_pins == expected_pins, "dependency path/identity/hash ledger drift")
    require(value.get("result_id") == "STRICT_TYPED_RESIDUAL_CYCLICITY_V1", "result identity drift")
    require(value.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE", "LORENTZIAN-CAUSAL"], "dependency tag drift")

    dfinite = load(DFINITE)
    m3rca = load(M3RCA)
    m3rcb = load(M3RCB)
    m4l = load(M4L)
    require(m3rca.get("claim_flags", {}).get("FORMAL_COTANGENT_SDR_CYCLIC") is True, "M3RC-A cyclic SDR missing")
    require(m3rcb.get("claim_flags", {}).get("M3RC_B_REPRESENTED_ACTION_SUPPORT_DUAL_IDENTIFICATION_COMPLETE") is True, "M3RC-B missing")
    require(m3rcb.get("claim_flags", {}).get("ACTION_PAIRING_EQUALS_CANONICAL_940_COTANGENT_PAIRING") is True, "action/cotangent pairing mismatch")
    require(m4l.get("claim_flags", {}).get("M4L_LOCAL_GRAPH_CYCLIC_PAIRING_COMPLETE") is True, "M4L missing")

    blocks = [replay(block) for block in dfinite.get("blocks", [])]
    declared = value.get("exact_cyclic_replay", {})
    require(declared.get("block_replays") == blocks, "independent block replay drift")
    require([block["energy"] for block in blocks] == [2, 3, 4, 5, 6], "energy coverage drift")
    require(not any(block["total_identity_defects"] for block in blocks), "nonzero cyclic contraction defect")
    require((sum(block["formal_source_dimension"] for block in blocks), sum(block["action_identified_residual_dimension"] for block in blocks)) == (8980, 940), "carrier dimension drift")
    require(declared.get("all_identity_defects") == 0, "global defect flag drift")
    require((declared.get("formal_source_dimension"), declared.get("residual_dimension"), declared.get("residual_pairing_rank")) == (8980, 940, 940), "global pairing rank drift")

    typed = value.get("typed_carrier", {})
    require((typed.get("primal_residual_coordinates"), typed.get("compact_source_dual_coordinates"), typed.get("total_residual_coordinates"), typed.get("action_pairing_rank")) == (470, 470, 940, 940), "typed residual census drift")
    require(typed.get("action_pairing_identification_defects") == 0, "action pairing crosswalk defect")
    require(typed.get("formal_source_is_authoritative_full_BV_source") is False, "formal source authority promoted")
    require(typed.get("full_continuous_all_energy_dual_identified") is False, "all-energy continuous dual promoted")
    require(m3rcb.get("action_pairing_identification", {}).get("dual_dictionary_sha256") == digest(m3rcb["action_pairing_identification"]["dual_dictionary"]), "M3RC-B dual dictionary digest drift")

    flags = value.get("claim_flags", {})
    for key in (
        "M4L_LOCAL_GRAPH_CYCLIC_PAIRING_COMPLETE",
        "M3RC_REPRESENTED_DUAL_COMPLETE",
        "M4R_REPRESENTED_Q_RES_CYCLIC",
        "M4R_REPRESENTED_PROJECTION_EQUALS_INCLUSION_SHARP",
        "M4R_REPRESENTED_HOMOTOPY_SKEW_ADJOINT",
        "M4R_REPRESENTED_NORMALIZED_CYCLIC_CONTRACTION_COMPLETE",
        "M4R_TYPED_RESIDUAL_CYCLICITY_COMPLETE",
    ):
        require(flags.get(key) is True, f"positive claim flag missing: {key}")
    for key in (
        "FORMAL_8980_SOURCE_IS_AUTHORITATIVE_ORIGINAL_BV_COMPLEX",
        "M1_COMMON_STRICT_SNAPSHOT_COMPLETE",
        "CLASSICAL_IMPORT_GATE_PASSED",
        "FULL_COMPLEX_HADAMARD_STATE_CONSTRUCTED",
        "RENORMALIZED_LORENTZIAN_PRODUCTS_CONSTRUCTED",
        "QME_RESTORED",
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
    ):
        require(flags.get(key) is False, f"firewall promoted: {key}")

    keys = ("scope", "typed_carrier", "exact_cyclic_replay", "m4r_disposition", "foundational_strength", "claim_flags")
    expected_digest = digest({key: value[key] for key in keys}) if all(key in value for key in keys) else ""
    require(value.get("independent_checker", {}).get("expected_digest") == expected_digest, "canonical result digest drift")
    return errors


def main() -> int:
    errors = check()
    print("STRICT_TYPED_RESIDUAL_CYCLICITY: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print("  - exact 8980-to-940 cotangent contraction replays blockwise")
        print("  - q_res cyclicity, pi=iota^sharp and homotopy skewness have zero defects")
        print("  - M4R closes on the represented action-identified carrier; M1 and Gate A remain open")
    for error in errors:
        print("  - " + error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
