#!/usr/bin/env python3
"""Independent exact checker for the 386-row cubic inventory and vv BV lift."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
CLASSICAL = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
CANDIDATE = HERE / "certificates/STRICT_386_STABILIZED_Q2_LIFT_PREFLIGHT_V1.json"
PREDECESSOR = HERE / "certificates/STRICT_386_QUADRATIC_AUXILIARY_ELIMINATION_CHANNEL_V1.json"
COORDS = tuple((i, j) for i in range(4) for j in range(i, 4))
SIGNS = (-1, 1, 1, 1)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def invert(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    work = [row[:] + [Fraction(int(i == j)) for j in range(size)] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next(row for row in range(column, size) if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [entry / scale for entry in work[column]]
        for row in range(size):
            if row != column:
                factor = work[row][column]
                work[row] = [left - factor * right for left, right in zip(work[row], work[column])]
    return [row[size:] for row in work]


def expected(value: dict[str, Any], pairing: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    basis = pairing["component_basis"]["rows"]
    rows = {row["row_id"]: row["index"] for row in basis}
    jf = [[Fraction(0) for _ in range(10)] for _ in range(10)]
    jv = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    for entry in pairing["pairing_serialization"]["entries"]:
        left, right, coefficient = entry["left_index"], entry["right_index"], Fraction(entry["coefficient"])
        if 34 <= left < 44 and 48 <= right < 58:
            jf[left - 34][right - 48] = coefficient
        elif 44 <= left < 48 and 58 <= right < 62:
            jv[left - 44][right - 58] = coefficient
    jvi = invert(jv)
    d2 = [[[Fraction(int(mu == a and nu == b) + int(mu == b and nu == a) - int(mu == nu and a == b) * SIGNS[mu] * SIGNS[a]) for b in range(4)] for a in range(4)] for mu, nu in COORDS]
    field_entries: list[dict[str, Any]] = []
    for output, (mu, nu) in enumerate(COORDS):
        for a in range(4):
            for b in range(a, 4):
                derivative = d2[output][a][b]
                if derivative:
                    coefficient = derivative / (2 if a == b else 1)
                    field_entries.append({"output_row": f"f_hat_{mu}{nu}", "v_left_row": f"v_{a}", "v_right_row": f"v_{b}", "homogeneous_polynomial_coefficient": str(coefficient), "second_Frechet_coefficient": str(derivative), "output_index": rows[f"f_hat_{mu}{nu}"], "v_left_index": rows[f"v_{a}"], "v_right_index": rows[f"v_{b}"]})
    cotangent: list[dict[str, Any]] = []
    for output in range(4):
        for vector_input in range(4):
            for fstar, coord in enumerate(COORDS):
                coefficient = sum((jvi[output][a] * d2[frow][a][vector_input] * jf[frow][fstar] for a in range(4) for frow in range(10)), Fraction(0))
                if coefficient:
                    cotangent.append({"output_row": f"v_star_{output}", "output_index": rows[f"v_star_{output}"], "v_input_row": f"v_{vector_input}", "v_input_index": rows[f"v_{vector_input}"], "f_hat_star_input_row": f"f_hat_star_{coord[0]}{coord[1]}", "f_hat_star_input_index": rows[f"f_hat_star_{coord[0]}{coord[1]}"], "coefficient": str(coefficient)})
    defects = 0
    for vector_input in range(4):
        c = [[Fraction(0) for _ in range(10)] for _ in range(4)]
        for entry in cotangent:
            if entry["v_input_row"] == f"v_{vector_input}":
                c[entry["output_index"] - 58][entry["f_hat_star_input_index"] - 48] = Fraction(entry["coefficient"])
        for a in range(4):
            for fstar in range(10):
                left = sum((jv[a][r] * c[r][fstar] for r in range(4)), Fraction(0))
                right = sum((d2[frow][a][vector_input] * jf[frow][fstar] for frow in range(10)), Fraction(0))
                defects += int(left != right)
    return field_entries, cotangent, defects


def has_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(has_float(item) for item in value.values())
    if isinstance(value, list):
        return any(has_float(item) for item in value)
    return False


def check(value: dict[str, Any] | None = None) -> list[str]:
    value = value or json.loads(RESULT.read_text())
    classical, pairing, candidate, predecessor = (json.loads(path.read_text()) for path in (CLASSICAL, PAIRING, CANDIDATE, PREDECESSOR))
    errors: list[str] = []
    if value.get("result_id") != "STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1" or value.get("lifecycle") != "CLASSIFIED" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("identity/lifecycle/dependency")
    if has_float(value):
        errors.append("floating-point data")
    expected_field, expected_cotangent, expected_defects = expected(value, pairing)
    lift = value.get("vv_BV_cotangent_lift", {})
    if lift.get("carrier_rows") != 386 or lift.get("quadratic_active_output_rows") != 14 or lift.get("quadratic_zero_output_rows") != 372:
        errors.append("carrier embedding")
    if lift.get("field_map_entries") != expected_field or lift.get("field_map_nonzero_component_coefficients") != 22:
        errors.append("vv field-map table")
    if lift.get("cotangent_partner_entries") != expected_cotangent or lift.get("cotangent_partner_nonzero_component_coefficients") != 16:
        errors.append("vv cotangent table")
    if lift.get("canonicality_defects") != expected_defects or expected_defects != 0 or any(row.get("nonzero_canonicality_defects") != 0 for row in lift.get("canonicality_slices", [])):
        errors.append("vv canonicality")
    families = value.get("required_cubic_family_inventory", [])
    if len(families) != 7 or sum(row.get("status") in ("COMPONENT_COEFFICIENTS_SERIALIZED", "FIELD_AND_COTANGENT_COMPONENT_COEFFICIENTS_SERIALIZED") for row in families) != 2:
        errors.append("family census")
    complete = value.get("inventory_completeness", {})
    if complete.get("vv_BV_cotangent_lift_component_complete") is not True or complete.get("hh_hv_BV_cotangent_lift_component_complete") is not False or complete.get("exhaustive_full_nonlinear_BV_family_census") is not False or complete.get("full_386_quadratic_BV_cotangent_lift_serialized") is not False:
        errors.append("completeness boundary")
    comparison = value.get("candidate_comparison", {})
    if comparison.get("previous_f_hat_v_v_channel_residual") != "0" or comparison.get("new_exact_source_candidate_component_defect_count") != 72 or comparison.get("full_nonlinear_equivalence_obstructed") is not False:
        errors.append("candidate comparison")
    flags = value.get("claim_flags", {})
    positive = ("KNOWN_REQUIRED_CUBIC_FAMILIES_ENUMERATED", "SHIFTED_MASS_H_F_HAT_F_HAT_COMPONENTS_IMPORTED", "VV_FIELD_MAP_COMPONENTS_IMPORTED", "VV_COTANGENT_PARTNER_COMPONENTS_SERIALIZED", "VV_BV_COTANGENT_LIFT_CANONICAL")
    negative = ("EXHAUSTIVE_FULL_NONLINEAR_BV_FAMILY_CENSUS", "FULL_386_BV_COTANGENT_LIFT_SERIALIZED", "FULL_SOURCE_Q2_PULLBACK_REPLAYED", "FULL_SOURCE_Q3_PULLBACK_REPLAYED", "FULL_CYCLIC_L_INFINITY_EQUIVALENCE_CONSTRUCTED", "FULL_NONLINEAR_EQUIVALENCE_OBSTRUCTED", "CLASSICAL_IMPORT_GATE_PASSED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED")
    if any(flags.get(key) is not True for key in positive) or any(flags.get(key) is not False for key in negative):
        errors.append("claim firewall")
    hashes = value.get("canonical_hashes", {})
    for key, payload in (("vv_BV_cotangent_lift_sha256", lift), ("required_cubic_family_inventory_sha256", families), ("inventory_completeness_sha256", complete), ("candidate_comparison_sha256", comparison)):
        if hashes.get(key) != digest(payload):
            errors.append("canonical hash " + key)
    expected_inputs = ((CLASSICAL, classical["result_id"]), (PAIRING, pairing["result_id"]), (CANDIDATE, candidate["result_id"]), (PREDECESSOR, predecessor["result_id"]))
    provenance = value.get("provenance", {}).get("inputs", [])
    if len(provenance) != 4:
        errors.append("provenance count")
    else:
        for row, (path, result_id) in zip(provenance, expected_inputs):
            if row.get("path") != str(path.relative_to(ROOT)) or row.get("sha256") != sha(path) or row.get("result_id") != result_id:
                errors.append("provenance " + path.name)
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
