#!/usr/bin/env python3
"""Independent variational replay of the 386-row auxiliary Diff BV lift."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_DIFF_AUXILIARY_BV_REPRESENTATION_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
PREDECESSOR = HERE / "certificates/STRICT_386_HH_HV_AUXILIARY_COTANGENT_LIFT_V1.json"
ZERO = (0, 0, 0, 0)


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def invert(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    n = len(matrix)
    augmented = [row[:] + [Fraction(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for k in range(n):
        pivot = next(i for i in range(k, n) if augmented[i][k])
        augmented[k], augmented[pivot] = augmented[pivot], augmented[k]
        augmented[k] = [x / augmented[k][k] for x in augmented[k]]
        for i in range(n):
            if i != k and augmented[i][k]:
                multiplier = augmented[i][k]
                augmented[i] = [x - multiplier * y for x, y in zip(augmented[i], augmented[k])]
    return [row[n:] for row in augmented]


def plus(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a + b for a, b in zip(left, right))


def minus(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a - b for a, b in zip(left, right))


def subindices(value: tuple[int, ...]):
    yield from itertools.product(*(range(item + 1) for item in value))


def choose(top: tuple[int, ...], bottom: tuple[int, ...]) -> int:
    return math.prod(math.comb(a, b) for a, b in zip(top, bottom))


def listed(entries: list[dict[str, Any]]) -> dict[tuple[Any, ...], Fraction]:
    return {
        (item["output_row"], item["left_input_row"], tuple(item["left_input_jet"]), item["right_input_row"], tuple(item["right_input_jet"])): Fraction(item["coefficient"])
        for item in entries
    }


def add_pair(
    target: dict[tuple[Any, ...], Fraction], output: str, left: str, left_jet: tuple[int, ...],
    right: str, right_jet: tuple[int, ...], coefficient: Fraction, parity: dict[str, int],
) -> None:
    target[(output, left, left_jet, right, right_jet)] += coefficient
    target[(output, right, right_jet, left, left_jet)] += coefficient * (-1 if parity[left] * parity[right] else 1)


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source, pairing = json.loads(CLASSICAL.read_text()), json.loads(PAIRING.read_text())
    basis = pairing["component_basis"]["rows"]
    by_name = {row["row_id"]: row for row in basis}
    by_block: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in basis:
        by_block[row["block"]].append(row)
    parity = {name: row["degree"] % 2 for name, row in by_name.items()}
    source_by_family = {item["family_id"]: item for item in source["representation_tables"]}
    result_by_family = {item["family_id"]: item for item in value.get("BV_representation_lifts", [])}
    family_blocks = {
        "DIFF_C_F_HAT_F_HAT_STAR": ("AUX_F_HAT", "AUX_F_HAT_STAR"),
        "DIFF_C_V_V_STAR": ("AUX_V", "AUX_V_STAR"),
        "DIFF_C_ETA_ETA_STAR": ("AUX_ETA", "AUX_ETA_STAR"),
    }
    pairing_entries = {(item["left_index"], item["right_index"]): Fraction(item["coefficient"]) for item in pairing["pairing_serialization"]["entries"]}

    for family, (field_block, star_block) in family_blocks.items():
        source_table, result = source_by_family.get(family, {}), result_by_family.get(family, {})
        fields, stars = by_block[field_block], by_block[star_block]
        field_names, star_names = [row["row_id"] for row in fields], [row["row_id"] for row in stars]
        field_pos = {name: i for i, name in enumerate(field_names)}
        form = [[pairing_entries.get((field["index"], star["index"]), Fraction(0)) for star in stars] for field in fields]
        inverse_form = invert(form)
        if result.get("pairing_matrix") != [[str(x) for x in row] for row in form] or result.get("pairing_matrix_inverse") != [[str(x) for x in row] for row in inverse_form]:
            errors.append(f"{family}: pairing coordinate replay mismatch")

        expected_field: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
        expected_master: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
        for item in source_table.get("ordered_field_action_entries", []):
            output, ghost, field = item["output_row"], item["ghost_row"], item["field_row"]
            alpha, beta, coefficient = tuple(item["ghost_jet"]), tuple(item["field_jet"]), Fraction(item["coefficient"])
            add_pair(expected_field, output, ghost, alpha, field, beta, coefficient, parity)
            for a, star in enumerate(star_names):
                if form[field_pos[output]][a]:
                    expected_master[(ghost, alpha, field, beta, star, ZERO)] += coefficient * form[field_pos[output]][a]
        expected_field = {key: item for key, item in expected_field.items() if item}
        actual_master = {
            (item["ghost_row"], tuple(item["ghost_jet"]), item["field_row"], tuple(item["field_jet"]), item["antifield_row"], tuple(item["antifield_jet"])): Fraction(item["coefficient"])
            for item in result.get("master_density_entries", [])
        }
        if listed(result.get("field_output_entries", [])) != expected_field:
            errors.append(f"{family}: field output or Koszul mate mismatch")
        if actual_master != {key: item for key, item in expected_master.items() if item}:
            errors.append(f"{family}: master-density reconstruction mismatch")

        # Derive both remaining Hamiltonian rows directly from the serialized
        # trilinear density, independently of the producer's source terms.
        expected_star: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
        expected_cstar: dict[tuple[Any, ...], Fraction] = defaultdict(Fraction)
        for (ghost, alpha, field, beta, star, _), hamiltonian in expected_master.items():
            field_local = field_pos[field]
            for gamma in subindices(beta):
                derivative = hamiltonian * (-1 if sum(beta) % 2 else 1) * choose(beta, gamma)
                for output_local, output in enumerate(star_names):
                    coefficient = -inverse_form[output_local][field_local] * derivative
                    if coefficient:
                        add_pair(expected_star, output, ghost, plus(alpha, minus(beta, gamma)), star, gamma, coefficient, parity)
            ghost_local = int(ghost.rsplit("_", 1)[1])
            for gamma in subindices(alpha):
                coefficient = hamiltonian * (-1 if sum(alpha) % 2 else 1) * choose(alpha, gamma)
                if coefficient:
                    add_pair(expected_cstar, f"c_star_{ghost_local}", field, plus(beta, minus(alpha, gamma)), star, gamma, coefficient, parity)
        expected_star = {key: item for key, item in expected_star.items() if item}
        expected_cstar = {key: item for key, item in expected_cstar.items() if item}
        if listed(result.get("antifield_output_entries", [])) != expected_star:
            errors.append(f"{family}: negative formal transpose mismatch")
        if listed(result.get("c_star_output_entries", [])) != expected_cstar:
            errors.append(f"{family}: Diff momentum-map variation mismatch")
        counts = result.get("component_counts", {})
        actual_counts = {
            "master_density": len(actual_master),
            "field_outputs_with_Koszul_mates": len(expected_field),
            "antifield_outputs_with_Koszul_mates": len(expected_star),
            "c_star_outputs_with_Koszul_mates": len(expected_cstar),
        }
        if counts != actual_counts or result.get("formal_variational_defects") != 0 or result.get("Koszul_symmetry_defects") != 0:
            errors.append(f"{family}: count or defect ledger mismatch")

    expected_summary = {
        "carrier_rows": 386, "completed_families": 3,
        "master_density_coefficients": 264, "field_output_coefficients": 336,
        "antifield_output_coefficients": 632, "c_star_output_coefficients": 704,
        "formal_variational_defects": 0, "Koszul_symmetry_defects": 0,
    }
    if value.get("component_summary") != expected_summary:
        errors.append("combined component summary mismatch")
    if value.get("canonical_hashes", {}).get("BV_representation_lifts_sha256") != canonical_digest(value.get("BV_representation_lifts", [])):
        errors.append("lift digest mismatch")
    if value.get("inventory_completeness", {}).get("component_coefficient_complete_families") != 7 or value.get("inventory_completeness", {}).get("exhaustive_full_nonlinear_BV_family_census") is not False:
        errors.append("known-family versus exhaustive-census boundary mismatch")
    pins = {item.get("path"): item.get("sha256") for item in value.get("provenance", {}).get("inputs", [])}
    expected_pins = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (CLASSICAL, PAIRING, Q1, PREDECESSOR)}
    if pins != expected_pins:
        errors.append("receiver provenance pins mismatch")
    flags = value.get("claim_flags", {})
    required_true = ("THREE_DIFF_AUXILIARY_FIELD_TABLES_IMPORTED", "THREE_DIFF_AUXILIARY_BV_COTANGENT_LIFTS_SERIALIZED", "THREE_DIFF_AUXILIARY_C_STAR_MOMENTUM_MAPS_SERIALIZED", "SEVEN_KNOWN_REQUIRED_CUBIC_FAMILIES_COMPONENT_COMPLETE")
    required_false = ("EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS", "FULL_SOURCE_Q2_PULLBACK_REPLAYED", "FULL_SOURCE_Q3_PULLBACK_REPLAYED", "FULL_Q1_Q2_IDENTITY_REPLAYED", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED")
    for name in required_true:
        if flags.get(name) is not True:
            errors.append(f"claim flag drift: {name}")
    for name in required_false:
        if flags.get(name) is not False:
            errors.append(f"fail-closed flag drift: {name}")
    if value.get("result_id") != "STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("result identity or dependency boundary mismatch")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_386_DIFF_AUXILIARY_BV_REPRESENTATION_V1_INDEPENDENT_VARIATIONAL_REPLAY: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print(json.dumps(value["component_summary"], sort_keys=True))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
