#!/usr/bin/env python3
"""Independently replay the serialized centered C3/C4/C5 payload."""

from __future__ import annotations

import hashlib
from itertools import combinations
import json
from pathlib import Path
from typing import Any

import sympy as sp
from sympy.polys.domains import GF
from sympy.polys.matrices import DomainMatrix


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "quantum-weyl/classical_import/certificates/STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1.json"


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def add(output: dict, key: Any, value: sp.Expr) -> None:
    value = sp.cancel(value)
    if value == 0:
        return
    output[key] = sp.cancel(output.get(key, 0) + value)
    if output[key] == 0:
        del output[key]


def wedge(first: tuple[int, ...], second: tuple[int, ...]):
    if set(first).intersection(second):
        return None
    inversions = sum(left > right for left in first for right in second)
    return (-1 if inversions % 2 else 1), tuple(sorted(first + second))


def decode_matrix(payload: dict[str, Any], label: str, errors: list[str]) -> sp.SparseMatrix:
    try:
        rows, columns = payload["shape"]
        entries: dict[tuple[int, int], sp.Rational] = {}
        for row, column, raw in payload["entries"]:
            key = (row, column)
            if key in entries or not (0 <= row < rows and 0 <= column < columns):
                errors.append(f"{label} duplicate or out-of-range entry")
                continue
            value = sp.Rational(raw)
            if value == 0:
                errors.append(f"{label} explicitly stores zero")
            entries[key] = value
        body = {"shape": [rows, columns], "entries": payload["entries"]}
        if payload.get("nonzero_entries") != len(entries) or payload.get("sha256") != digest(body):
            errors.append(f"{label} count or canonical hash")
        return sp.SparseMatrix(rows, columns, entries)
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"{label} malformed: {exc}")
        return sp.SparseMatrix(0, 0, {})


def structure_from_residual(reference: dict[str, Any], errors: list[str]):
    path = ROOT / str(reference.get("path", ""))
    if not path.is_file():
        errors.append("residual structure source missing")
        return [], (), ()
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != reference.get("file_sha256"):
        errors.append("residual structure file hash")
    source = json.loads(raw)
    payload = source.get("so42_structure_constants", {})
    if payload.get("sha256") != reference.get("structure_constants_sha256"):
        errors.append("residual structure object hash link")
    names = tuple(payload.get("generator_order", ()))
    degrees = tuple(payload.get("generator_compact_degrees", ()))
    tensor = [[[sp.Rational(0) for _ in range(15)] for _ in range(15)] for _ in range(15)]
    seen = set()
    for first, second, target, raw_value in payload.get("entries", []):
        key = (first, second, target)
        if key in seen or any(not 0 <= index < 15 for index in key):
            errors.append("residual structure duplicate or range")
            continue
        seen.add(key)
        tensor[first][second][target] = sp.Rational(raw_value)
    body = {
        "convention": payload.get("convention"),
        "generator_order": payload.get("generator_order"),
        "generator_compact_degrees": payload.get("generator_compact_degrees"),
        "entries": payload.get("entries"),
        "tensor_shape": payload.get("tensor_shape"),
    }
    if payload.get("sha256") != digest(body) or len(names) != 15 or len(degrees) != 15:
        errors.append("residual structure canonical payload")
    return tensor, names, degrees


def ghost_differentials(structure) -> tuple[dict[tuple[int, int], sp.Expr], ...]:
    output = []
    for target in range(15):
        image: dict[tuple[int, int], sp.Expr] = {}
        for first in range(15):
            for second in range(15):
                product = wedge((first,), (second,))
                if product is None:
                    continue
                sign, monomial = product
                add(image, monomial, -sp.Rational(1, 2) * sign * structure[first][second][target])
        output.append(image)
    return tuple(output)


def expected_basis(
    degree: int,
    ghost_degrees: tuple[int, ...],
    sectors: dict[str, Any],
    sector_order: tuple[str, ...],
) -> list[list[Any]]:
    output: list[list[Any]] = []
    for sector in sector_order:
        states_by_energy: dict[int, list[int]] = {}
        for state in sectors[sector]["states"]:
            states_by_energy.setdefault(state["matter_energy"], []).append(state["index"])
        for monomial in combinations(range(15), degree):
            ghost_energy = sum(ghost_degrees[index] for index in monomial)
            output.extend(
                [sector, list(monomial), state]
                for state in states_by_energy.get(-ghost_energy, ())
            )
    return output


def action_columns(matrix: sp.SparseMatrix) -> tuple[dict[int, sp.Expr], ...]:
    output = [dict() for _ in range(matrix.cols)]
    for (row, column), value in matrix.todok().items():
        output[column][row] = value
    return tuple(output)


def reconstruct_differential(
    source: list[list[Any]],
    target: list[list[Any]],
    ghost_d: tuple[dict[tuple[int, int], sp.Expr], ...],
    actions: dict[str, tuple[tuple[dict[int, sp.Expr], ...], ...]],
    errors: list[str],
    label: str,
) -> tuple[dict[int, sp.Expr], ...]:
    target_index = {
        (sector, tuple(monomial), state): index
        for index, (sector, monomial, state) in enumerate(target)
    }
    output = []
    for sector, raw_monomial, state in source:
        monomial = tuple(raw_monomial)
        image: dict[int, sp.Expr] = {}
        for position, ghost in enumerate(monomial):
            prefix = monomial[:position]
            suffix = monomial[position + 1 :]
            for pair, coefficient in ghost_d[ghost].items():
                first = wedge(prefix, pair)
                if first is None:
                    continue
                sign_first, partial = first
                second = wedge(partial, suffix)
                if second is None:
                    continue
                sign_second, result = second
                key = (sector, result, state)
                if key not in target_index:
                    errors.append(f"{label} ghost action left centered basis")
                    continue
                add(image, target_index[key], (-1) ** position * sign_first * sign_second * coefficient)
        for ghost, matrix in enumerate(actions[sector]):
            product = wedge((ghost,), monomial)
            if product is None:
                continue
            sign, result = product
            if not 0 <= state < len(matrix):
                errors.append(f"{label} state outside module")
                continue
            for result_state, coefficient in matrix[state].items():
                key = (sector, result, result_state)
                if key not in target_index:
                    errors.append(f"{label} coefficient action left centered basis")
                    continue
                add(image, target_index[key], sign * coefficient)
        output.append(image)
    return tuple(output)


def compose(first, second) -> tuple[dict[int, sp.Expr], ...]:
    output = []
    for column in first:
        result: dict[int, sp.Expr] = {}
        for middle, first_value in column.items():
            for row, second_value in second[middle].items():
                add(result, row, first_value * second_value)
        output.append(result)
    return tuple(output)


def modular_rank(columns, rows: int, prime: int = 1009) -> int:
    row_data: dict[int, dict[int, int]] = {}
    for column, vector in enumerate(columns):
        for row, value in vector.items():
            value = sp.cancel(value)
            if not value.is_Rational:
                raise ValueError("non-rational differential coefficient")
            reduced = int(value.p) * pow(int(value.q), -1, prime) % prime
            if reduced:
                row_data.setdefault(row, {})[column] = reduced
    return DomainMatrix.from_dict_sympy(rows, len(columns), row_data).convert_to(GF(prime)).rank()


def decode_quadratic_vector(payload: dict[str, Any], errors: list[str], label: str) -> sp.Matrix:
    try:
        dimension = payload["dimension"]
        radicand = payload["radicand"]
        output = sp.zeros(dimension, 1)
        seen = set()
        for index, raw in payload["entries"]:
            if index in seen or not 0 <= index < dimension:
                errors.append(f"{label} duplicate or range")
                continue
            seen.add(index)
            output[index] = sp.Rational(raw) * sp.sqrt(radicand)
        body = {key: payload[key] for key in ("dimension", "coefficient_field", "encoding", "radicand", "entries")}
        if payload.get("nonzero_entries") != len(seen) or payload.get("sha256") != digest(body):
            errors.append(f"{label} count or canonical hash")
        return output
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"{label} malformed: {exc}")
        return sp.zeros(0, 1)


def check(value: dict[str, Any], *, algebra: bool = True) -> list[str]:
    errors: list[str] = []
    if value.get("schema") != "strict-centered-cohomology-payload-v1" or value.get("result_id") != "STRICT_CENTERED_COHOMOLOGY_PAYLOAD_V1":
        errors.append("result identity")
    if value.get("dependency_tags") != ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]:
        errors.append("dependency tags")

    flags = value.get("claim_flags", {})
    positives = (
        "STRICT_CENTERED_C3_C4_C5_BASES_SERIALIZED",
        "STRICT_CENTERED_DIFFERENTIAL_RECONSTRUCTED",
        "STRICT_NORMALIZED_WEYL_SQUARE_REPRESENTATIVES_SERIALIZED",
        "STRICT_CENTERED_H4_COHOMOLOGY_REPLAYED",
        "M6_CENTERED_REPRESENTATIVES_COMPLETE",
    )
    negatives = (
        "COMMON_GATE_A_FREEZE_BOUND",
        "CLASSICAL_IMPORT_GATE_PASSED",
        "HADAMARD_STATE_CONSTRUCTED",
        "QME_RESTORED",
        "RESIDUAL_QUANTUM_TRANSFER_AUTHORIZED",
        "LORENTZIAN_QUANTUM_THEORY",
    )
    if any(flags.get(key) is not True for key in positives):
        errors.append("positive claim flags")
    if any(flags.get(key) is not False for key in negatives):
        errors.append("fail-closed claim flags")

    structure, names, generator_degrees = structure_from_residual(value.get("residual_structure_reference", {}), errors)
    ghost_degrees = tuple(-degree for degree in generator_degrees)
    basis_payload = value.get("ordered_centered_cochain_basis", {})
    sector_order = tuple(basis_payload.get("sector_order", ()))
    module_payload = value.get("coefficient_modules", {})
    sectors = module_payload.get("sectors", {})
    if sector_order != ("vacuum", "one_particle", "two_particle_weight_four") or set(sectors) != set(sector_order):
        errors.append("sector inventory")
        return errors
    if tuple(basis_payload.get("residual_generator_order", ())) != names or tuple(basis_payload.get("residual_generator_compact_degrees", ())) != generator_degrees or tuple(basis_payload.get("residual_ghost_compact_degrees", ())) != ghost_degrees:
        errors.append("residual generator convention")

    actions: dict[str, tuple[tuple[dict[int, sp.Expr], ...], ...]] = {}
    for sector in sector_order:
        record = sectors[sector]
        states = record.get("states", [])
        if [state.get("index") for state in states] != list(range(len(states))):
            errors.append(f"{sector} state ordering")
        matrices = []
        for index, action in enumerate(record.get("generator_actions", [])):
            matrix = decode_matrix(action.get("matrix", {}), f"{sector}.rho[{index}]", errors)
            if action.get("generator_index") != index or index >= len(names) or action.get("generator") != names[index] or matrix.shape != (len(states), len(states)):
                errors.append(f"{sector} action label or shape {index}")
            matrices.append(action_columns(matrix))
        if len(matrices) != 15:
            errors.append(f"{sector} action count")
        actions[sector] = tuple(matrices)
        body = {"states": states, "generator_actions": record.get("generator_actions")}
        if record.get("sha256") != digest(body):
            errors.append(f"{sector} module hash")
    modules_body = {"convention": module_payload.get("convention"), "sectors": sectors}
    if module_payload.get("sha256") != digest(modules_body):
        errors.append("coefficient module hash")

    bases: dict[int, list[list[Any]]] = {}
    expected_dimensions = {3: 727, 4: 3084, 5: 8532}
    for degree in (3, 4, 5):
        record = basis_payload.get("degrees", {}).get(str(degree), {})
        entries = record.get("entries", [])
        expected = expected_basis(degree, ghost_degrees, sectors, sector_order)
        if entries != expected:
            errors.append(f"C{degree} ordered basis")
        body = {key: record.get(key) for key in ("ghost_number", "total_compact_degree", "ordering", "entries")}
        if record.get("dimension") != expected_dimensions[degree] or record.get("dimension") != len(entries) or record.get("sha256") != digest(body):
            errors.append(f"C{degree} dimension or hash")
        bases[degree] = entries
    basis_body = {key: basis_payload.get(key) for key in (
        "residual_generator_order", "residual_generator_compact_degrees",
        "residual_ghost_compact_degrees", "sector_order", "degrees",
    )}
    if basis_payload.get("sha256") != digest(basis_body):
        errors.append("ordered centered basis hash")

    representatives = value.get("normalized_H4_representatives", {})
    plus_local = decode_quadratic_vector(representatives.get("W_plus_squared_times_v_minus", {}), errors, "W_plus")
    minus_local = decode_quadratic_vector(representatives.get("W_minus_squared_times_v_minus", {}), errors, "W_minus")
    form = decode_matrix(representatives.get("two_particle_pairing", {}), "two-particle pairing", errors)
    parity = decode_matrix(representatives.get("two_particle_parity", {}), "two-particle parity", errors)
    rep_body = {key: representatives.get(key) for key in (
        "carrier", "ghost_vacuum", "two_particle_C4_global_offset", "construction",
        "W_plus_squared_times_v_minus", "W_minus_squared_times_v_minus",
        "two_particle_pairing", "two_particle_parity", "normalized_gram",
        "parity_action_in_chiral_basis", "interpretation",
    )}
    if representatives.get("sha256") != digest(rep_body):
        errors.append("representative payload hash")
    if plus_local.shape != (55, 1) or minus_local.shape != (55, 1) or form.shape != (55, 55) or parity.shape != (55, 55):
        errors.append("representative shapes")

    summary = value.get("centered_differential_summary", {})
    summary_body = {key: summary.get(key) for key in (
        "maps", "reconstruction", "modular_prime", "sector_ranks_d3_d4",
        "sector_nonzero_coefficients_d3_d4", "aggregate_nonzero_coefficients",
        "aggregate_ranks_d3_d4", "nilpotency_defects", "cohomology_dimension_H4",
        "rank_argument",
    )}
    if summary.get("sha256") != digest(summary_body):
        errors.append("differential summary hash")

    if algebra and not errors:
        ghost_d = ghost_differentials(structure)
        d3 = reconstruct_differential(bases[3], bases[4], ghost_d, actions, errors, "d3")
        d4 = reconstruct_differential(bases[4], bases[5], ghost_d, actions, errors, "d4")
        defects = sum(bool(column) for column in compose(d3, d4))
        ranks = [modular_rank(d3, len(bases[4])), modular_rank(d4, len(bases[5]))]
        nnz = sum(len(column) for column in d3) + sum(len(column) for column in d4)
        if defects != 0 or summary.get("nilpotency_defects") != 0:
            errors.append("d3/d4 nilpotency")
        if ranks != [636, 2446] or summary.get("aggregate_ranks_d3_d4") != ranks:
            errors.append("aggregate modular ranks")
        if nnz != 85091 or summary.get("aggregate_nonzero_coefficients") != nnz:
            errors.append("differential nonzero coefficient count")

        offset = representatives.get("two_particle_C4_global_offset")
        two_indices = [index for index, entry in enumerate(bases[4]) if entry[0] == "two_particle_weight_four"]
        if offset != 3029 or two_indices != list(range(offset, offset + 55)):
            errors.append("two-particle C4 offset")
        plus = sp.zeros(len(bases[4]), 1)
        minus = sp.zeros(len(bases[4]), 1)
        plus[offset : offset + 55, 0] = plus_local
        minus[offset : offset + 55, 0] = minus_local

        def apply(columns, vector):
            output: dict[int, sp.Expr] = {}
            for column, coefficient in enumerate(vector):
                if coefficient == 0:
                    continue
                for row, value_ in columns[column].items():
                    add(output, row, coefficient * value_)
            return output

        if apply(d4, plus) or apply(d4, minus):
            errors.append("representative cocycle")
        if sp.Matrix.hstack(plus_local, minus_local).rank() != 2:
            errors.append("representative independence")
        gram = sp.simplify(sp.Matrix.hstack(plus_local, minus_local).T * form * sp.Matrix.hstack(plus_local, minus_local))
        if gram != sp.eye(2) or representatives.get("normalized_gram") != [[1, 0], [0, 1]]:
            errors.append("representative Gram")
        if parity * plus_local != minus_local or parity * minus_local != plus_local or parity * parity != sp.eye(55):
            errors.append("representative parity exchange")
        # d3 has no two-particle target component.  Therefore both independent
        # cocycles survive modulo im(d3).  Nilpotency gives rank(d3)+rank(d4)
        # <= 3084-2, while the modular ranks give the reverse inequality.
        if ranks[0] + ranks[1] != len(bases[4]) - 2:
            errors.append("rational H4 saturation proof")

    canonical = value.get("canonical_hashes", {})
    expected_canonical = {
        "ordered_centered_basis_sha256": basis_payload.get("sha256"),
        "coefficient_modules_sha256": module_payload.get("sha256"),
        "representatives_sha256": representatives.get("sha256"),
        "differential_summary_sha256": summary.get("sha256"),
        "residual_structure_constants_sha256": value.get("residual_structure_reference", {}).get("structure_constants_sha256"),
    }
    if canonical != expected_canonical:
        errors.append("canonical hashes")
    snapshot = value.get("centered_snapshot", {})
    snapshot_body = {key: snapshot.get(key) for key in ("theory", "background", "canonical_hashes", "input_sha256")}
    if snapshot.get("sha256") != digest(snapshot_body) or snapshot.get("canonical_hashes") != canonical:
        errors.append("centered snapshot hash")
    for path, expected in snapshot.get("input_sha256", {}).items():
        source = ROOT / path
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            errors.append("input provenance " + path)
    expected_digest = digest({
        "ordered_centered_cochain_basis": basis_payload,
        "coefficient_modules": module_payload,
        "centered_differential_summary": summary,
        "normalized_H4_representatives": representatives,
        "centered_snapshot": snapshot,
        "claim_flags": flags,
    })
    if value.get("independent_checker", {}).get("expected_digest") != expected_digest:
        errors.append("independent digest")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    errors = check(value)
    print("STRICT_CENTERED_COHOMOLOGY_PAYLOAD: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
