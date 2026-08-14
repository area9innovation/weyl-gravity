#!/usr/bin/env python3
"""Independent exact receiver for STRICT_DFINITE_RESIDUAL_SDR_V1."""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from math import comb
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_DFINITE_RESIDUAL_SDR_V1.json"
ENERGIES = tuple(range(2, 7))
FALSE_FLAGS = {
    "CLASSICAL_IMPORT_GATE_PASSED",
    "FULL_SUPPORT_LOCAL_RESIDUAL_SDR_CONSTRUCTED",
    "FULL_CYCLIC_PAIRING_EXPORTED",
    "NONCOMPACT_EQUIVARIANT_REPRESENTATIVE_SDR",
    "STRICT_SUPPORT_LOCAL_Q2_D_CONSTRUCTED",
    "LORENTZIAN_QUANTUM_THEORY",
    "QME_RESTORED",
    "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
}


def canonical_hash(value: Any) -> str:
    return sha256(dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def choose(value: int, degree: int) -> int:
    return comb(value, degree) if value >= degree >= 0 else 0


def expected_dimensions(energy: int) -> dict[str, int]:
    n = energy
    return {
        "gauge": 4 * choose(n + 4, 3),
        "metric": 9 * choose(n + 3, 3),
        "chirality": 3 * n * n - 7,
        "physical": 2 * (3 * n * n - 7),
        "equation": (n - 2) * (n - 3) * (5 * n + 7) // 6,
        "bach_target": 9 * choose(n - 1, 3),
        "noether_identity": 4 * choose(n - 2, 3),
        "scalar": choose(n + 3, 3),
    }


def expected_sectors(energy: int, d: dict[str, int]) -> list[dict[str, Any]]:
    specs = (
        ("diff_ghost", d["gauge"], -1, 0, "minimal Diff ghost after CKV separation"),
        ("weyl_ghost", d["scalar"], -1, 0, "minimal Weyl ghost"),
        ("metric_trace", d["scalar"], 0, 0, "Weyl-contractible trace"),
        ("metric_tf", d["metric"], 0, 0, "trace-free metric; gauge | W+ | W- | equation"),
        ("metric_antifield", d["bach_target"], 1, 1, "Bach equation row; equation | Noether complement"),
        ("diff_ghost_antifield", d["noether_identity"], 2, 2, "Noether identity row"),
        ("trace_antifield", d["scalar"], 1, 1, "dual Weyl-contractible source"),
        ("weyl_ghost_antifield", d["scalar"], 2, 2, "dual Weyl-contractible target"),
        ("antighost", d["scalar"], -1, 0, "scalar test nonminimal source"),
        ("multiplier", d["scalar"], 0, 0, "scalar test nonminimal target"),
    )
    result: list[dict[str, Any]] = []
    cursor = 0
    for name, size, ghost, antifield, role in specs:
        result.append({"name": name, "start": cursor, "stop": cursor + size, "dimension": size, "ghost_number": ghost, "antifield_number": antifield, "role": role})
        cursor += size
    return result


Sparse = dict[tuple[int, int], Fraction]


def parse_matrix(value: dict[str, Any], expected_name: str) -> tuple[int, int, Sparse, list[str]]:
    errors: list[str] = []
    rows, columns = value.get("rows"), value.get("columns")
    if value.get("name") != expected_name or not isinstance(rows, int) or not isinstance(columns, int) or rows < 0 or columns < 0:
        return 0, 0, {}, ["matrix header " + expected_name]
    entries: Sparse = {}
    for entry in value.get("entries", []):
        if not isinstance(entry, list) or len(entry) != 3 or not isinstance(entry[0], int) or not isinstance(entry[1], int) or not isinstance(entry[2], str):
            errors.append("matrix entry type " + expected_name)
            continue
        row, column, raw = entry
        if not (0 <= row < rows and 0 <= column < columns) or (row, column) in entries:
            errors.append("matrix coordinate " + expected_name)
            continue
        try:
            coefficient = Fraction(raw)
        except (ValueError, ZeroDivisionError):
            errors.append("matrix coefficient " + expected_name)
            continue
        if coefficient == 0:
            errors.append("explicit zero " + expected_name)
        else:
            entries[row, column] = coefficient
    expected_hash = canonical_hash({key: value.get(key) for key in ("name", "rows", "columns", "entries")})
    if value.get("sha256") != expected_hash:
        errors.append("matrix hash " + expected_name)
    return rows, columns, entries, errors


def identity(size: int) -> Sparse:
    return {(index, index): Fraction(1) for index in range(size)}


def identity_entries(row_start: int, column_start: int, size: int) -> Sparse:
    return {(row_start + index, column_start + index): Fraction(1) for index in range(size)}


def merge(*values: Sparse) -> Sparse:
    result: Sparse = {}
    for value in values:
        for key, coefficient in value.items():
            if key in result:
                raise ValueError("overlapping expected matrix entries")
            result[key] = coefficient
    return result


def multiply(left: Sparse, right: Sparse) -> Sparse:
    right_rows: dict[int, list[tuple[int, Fraction]]] = {}
    for (row, column), coefficient in right.items():
        right_rows.setdefault(row, []).append((column, coefficient))
    result: Sparse = {}
    for (row, middle), coefficient in left.items():
        for column, other in right_rows.get(middle, []):
            key = (row, column)
            result[key] = result.get(key, Fraction(0)) + coefficient * other
            if result[key] == 0:
                del result[key]
    return result


def linear_combination(*terms: tuple[Fraction, Sparse]) -> Sparse:
    result: Sparse = {}
    for scalar, matrix in terms:
        for key, coefficient in matrix.items():
            result[key] = result.get(key, Fraction(0)) + scalar * coefficient
            if result[key] == 0:
                del result[key]
    return result


def expected_maps(sectors: list[dict[str, Any]], d: dict[str, int]) -> dict[str, Sparse]:
    starts = {item["name"]: item["start"] for item in sectors}
    q0 = merge(
        identity_entries(starts["metric_tf"], starts["diff_ghost"], d["gauge"]),
        identity_entries(starts["metric_trace"], starts["weyl_ghost"], d["scalar"]),
        identity_entries(starts["metric_antifield"], starts["metric_tf"] + d["gauge"] + d["physical"], d["equation"]),
        identity_entries(starts["diff_ghost_antifield"], starts["metric_antifield"] + d["equation"], d["noether_identity"]),
        identity_entries(starts["weyl_ghost_antifield"], starts["trace_antifield"], d["scalar"]),
        identity_entries(starts["multiplier"], starts["antighost"], d["scalar"]),
    )
    iota = identity_entries(starts["metric_tf"] + d["gauge"], 0, d["physical"])
    pi = identity_entries(0, starts["metric_tf"] + d["gauge"], d["physical"])
    s_cl = merge(
        identity_entries(starts["diff_ghost"], starts["metric_tf"], d["gauge"]),
        identity_entries(starts["weyl_ghost"], starts["metric_trace"], d["scalar"]),
        identity_entries(starts["metric_tf"] + d["gauge"] + d["physical"], starts["metric_antifield"], d["equation"]),
        identity_entries(starts["metric_antifield"] + d["equation"], starts["diff_ghost_antifield"], d["noether_identity"]),
        identity_entries(starts["trace_antifield"], starts["weyl_ghost_antifield"], d["scalar"]),
        identity_entries(starts["antighost"], starts["multiplier"], d["scalar"]),
    )
    return {"q0": q0, "iota_cl": iota, "pi_cl": pi, "s_cl": s_cl, "q_res_0": {}}


def digest(value: dict[str, Any]) -> str:
    return canonical_hash({
        key: value[key]
        for key in ("scope", "conventions", "global_direct_sum", "blocks", "independent_identity_contract", "foundational_strength", "gate_a_effect")
    })


def check(value: dict[str, Any] | None = None) -> tuple[list[str], dict[str, int]]:
    value = loads(RESULT.read_text()) if value is None else value
    errors: list[str] = []
    blocks = value.get("blocks", [])
    if [item.get("energy") for item in blocks] != list(ENERGIES):
        errors.append("energy block identity/order")
    full_offset = residual_offset = 0
    matrix_hashes: list[list[str]] = []
    q_hashes: list[str] = []
    all_full_basis: list[str] = []
    all_residual_basis: list[str] = []
    for item in blocks:
        energy = item.get("energy")
        if not isinstance(energy, int):
            continue
        d = expected_dimensions(energy)
        sectors = expected_sectors(energy, d)
        full_dimension = sectors[-1]["stop"]
        residual_dimension = d["physical"]
        if item.get("dimensions") != d or item.get("full_sectors") != sectors:
            errors.append(f"sector/dimension reconstruction E{energy}")
        if item.get("full_dimension") != full_dimension or item.get("residual_dimension") != residual_dimension:
            errors.append(f"block dimensions E{energy}")
        if item.get("full_offset") != full_offset or item.get("residual_offset") != residual_offset:
            errors.append(f"direct-sum offsets E{energy}")
        full_basis = [f"E{energy}:{sector['name']}:{index}" for sector in sectors for index in range(sector["dimension"])]
        residual_basis = [
            *(f"E{energy}:W_PLUS:{index}" for index in range(d["chirality"])),
            *(f"E{energy}:W_MINUS:{index}" for index in range(d["chirality"])),
        ]
        if item.get("full_basis") != full_basis or item.get("residual_basis") != residual_basis or len(set(full_basis)) != len(full_basis) or len(set(residual_basis)) != len(residual_basis):
            errors.append(f"ordered bases E{energy}")
        if item.get("basis_hashes") != {"full": canonical_hash(full_basis), "residual": canonical_hash(residual_basis)}:
            errors.append(f"basis hashes E{energy}")
        all_full_basis.extend(full_basis)
        all_residual_basis.extend(residual_basis)
        parsed: dict[str, Sparse] = {}
        shapes = {
            "q0": (full_dimension, full_dimension),
            "iota_cl": (full_dimension, residual_dimension),
            "pi_cl": (residual_dimension, full_dimension),
            "s_cl": (full_dimension, full_dimension),
            "q_res_0": (residual_dimension, residual_dimension),
        }
        matrices = item.get("matrices", {})
        if list(matrices) != list(shapes):
            errors.append(f"matrix identity/order E{energy}")
        block_hashes: list[str] = []
        for name, shape in shapes.items():
            rows, columns, entries, matrix_errors = parse_matrix(matrices.get(name, {}), name)
            errors.extend(f"E{energy} {error}" for error in matrix_errors)
            if (rows, columns) != shape:
                errors.append(f"matrix shape {name} E{energy}")
            parsed[name] = entries
            block_hashes.append(matrices.get(name, {}).get("sha256", ""))
        expected = expected_maps(sectors, d)
        for name in shapes:
            if parsed[name] != expected[name]:
                errors.append(f"independent map reconstruction {name} E{energy}")
        q0, iota, pi, s_cl, q_res = (parsed[name] for name in shapes)
        if multiply(q0, q0):
            errors.append(f"q0 squared E{energy}")
        if multiply(pi, iota) != identity(residual_dimension):
            errors.append(f"pi iota E{energy}")
        rhs = linear_combination(
            (Fraction(1), identity(full_dimension)),
            (Fraction(-1), multiply(q0, s_cl)),
            (Fraction(-1), multiply(s_cl, q0)),
        )
        if multiply(iota, pi) != rhs:
            errors.append(f"contraction identity E{energy}")
        if multiply(q0, iota) != multiply(iota, q_res):
            errors.append(f"iota intertwiner E{energy}")
        if multiply(pi, q0) != multiply(q_res, pi):
            errors.append(f"pi intertwiner E{energy}")
        if multiply(s_cl, s_cl) or multiply(s_cl, iota) or multiply(pi, s_cl):
            errors.append(f"normalized side conditions E{energy}")
        q_hashes.append(matrices.get("q0", {}).get("sha256", ""))
        matrix_hashes.append([matrices.get(name, {}).get("sha256", "") for name in ("iota_cl", "pi_cl", "s_cl", "q_res_0")])
        full_offset += full_dimension
        residual_offset += residual_dimension

    global_data = value.get("global_direct_sum", {})
    expected_global = {
        "ordered_block_energies": list(ENERGIES),
        "full_dimension": full_offset,
        "residual_dimension": residual_offset,
        "block_offsets": [{"energy": item["energy"], "full": item["full_offset"], "residual": item["residual_offset"]} for item in blocks],
        "field_dictionary_hash": canonical_hash(all_full_basis),
        "residual_basis_hash": canonical_hash(all_residual_basis),
        "differential_hash": canonical_hash(q_hashes),
        "residual_sdr_hash": canonical_hash(matrix_hashes),
    }
    if global_data != expected_global:
        errors.append("global direct-sum projection")
    gate = value.get("gate_a_effect", {})
    if gate.get("gate_a_status") != "FAIL_CLOSED" or len(gate.get("historical_missing_exports_scoped_now_portable", [])) != 3 or len(gate.get("historical_checks_scoped_now_replayed", [])) != 4 or not gate.get("remaining_m3_gap"):
        errors.append("Gate-A scope firewall")
    flags = value.get("claim_flags", {})
    if any(flags.get(key) is not False for key in FALSE_FLAGS) or flags.get("STRICT_DFINITE_RESIDUAL_SDR_PORTABLE") is not True:
        errors.append("claim flags")
    strength = value.get("foundational_strength", {})
    if strength.get("exactness_type") != "FINITE_EXACT_INTEGER_SPARSE_LINEAR_ALGEBRA" or "No choice" not in strength.get("choice_dependency", "") or "None inside" not in strength.get("infinity_dependency", ""):
        errors.append("foundational-strength boundary")
    for source in value.get("provenance", {}).get("inputs", []):
        path = ROOT / source.get("path", "")
        if not path.is_file() or sha256(path.read_bytes()).hexdigest() != source.get("sha256"):
            errors.append("provenance " + source.get("path", ""))
    expected_checker = value.get("independent_checker", {})
    if expected_checker.get("expected_blocks") != 5 or expected_checker.get("expected_full_dimension") != 4490 or expected_checker.get("expected_residual_dimension") != 470 or expected_checker.get("expected_digest") != digest(value):
        errors.append("independent checker contract/digest")
    return errors, {"blocks": len(blocks), "full_dimension": full_offset, "residual_dimension": residual_offset}


def main() -> int:
    errors, counts = check()
    print("STRICT_DFINITE_RESIDUAL_SDR_V1: " + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("  - " + error)
    else:
        print(f"  - {counts['blocks']} blocks, {counts['full_dimension']} full and {counts['residual_dimension']} residual coordinates")
        print("  - eight exact SDR identities replayed; Gate A remains fail-closed")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
