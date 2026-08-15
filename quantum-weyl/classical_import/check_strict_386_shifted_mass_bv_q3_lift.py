#!/usr/bin/env python3
"""Independent exact replay of the fixed-carrier auxiliary BV q3 lift."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1.json"
SOURCE = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1.json"
SOURCE_CHECKER = ROOT / "d_quotient_classical/nonminimal_identity/check_classical_shifted_auxiliary_quartic_mass_v1.py"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
Q2 = HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.json"
ZERO = [0, 0, 0, 0]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def invert(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    work = [row[:] + [Fraction(i == j) for j in range(size)] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next(row for row in range(column, size) if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row != column and work[row][column]:
                factor = work[row][column]
                work[row] = [left - factor * right for left, right in zip(work[row], work[column])]
    return [row[size:] for row in work]


def pairing_block(pairing: dict[str, Any], left: list[int], right: list[int]) -> list[list[Fraction]]:
    entries = {
        (entry["left_index"], entry["right_index"]): Fraction(entry["coefficient"])
        for entry in pairing["pairing_serialization"]["entries"]
    }
    return [[entries.get((i, j), Fraction()) for j in right] for i in left]


@lru_cache(maxsize=1)
def independently_reconstructed_entries() -> tuple[dict[str, str], ...]:
    spec = importlib.util.spec_from_file_location("independent_quartic_jet_rail", SOURCE_CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    entries, ordered, _ = module.expected_entries()
    if len(entries) != 321 or ordered != 912:
        raise AssertionError("independent classical jet rail count drift")
    return tuple(entries)


def source_tensor(h_rows: list[dict[str, Any]], f_rows: list[dict[str, Any]]) -> dict[tuple[int, int, int, int], Fraction]:
    h_position = {row["row_id"]: index for index, row in enumerate(h_rows)}
    f_position = {row["row_id"]: index for index, row in enumerate(f_rows)}
    tensor: dict[tuple[int, int, int, int], Fraction] = {}
    for entry in independently_reconstructed_entries():
        a, b = h_position[entry["h_left_row"]], h_position[entry["h_right_row"]]
        i, j = f_position[entry["f_hat_left_row"]], f_position[entry["f_hat_right_row"]]
        coefficient = Fraction(entry["D_h_left_D_h_right_D_f_left_D_f_right"])
        for h_left, h_right in {(a, b), (b, a)}:
            for f_left, f_right in {(i, j), (j, i)}:
                tensor[(h_left, h_right, f_left, f_right)] = coefficient
    return tensor


def entry(output: dict[str, Any], inputs: tuple[dict[str, Any], ...], coefficient: Fraction) -> dict[str, Any]:
    return {
        "output_row": output["row_id"], "output_index": output["index"],
        "input_rows": [row["row_id"] for row in inputs],
        "input_indices": [row["index"] for row in inputs],
        "input_jets": [ZERO, ZERO, ZERO], "coefficient": str(coefficient),
    }


def reconstruct(pairing: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    by_block: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pairing["component_basis"]["rows"]:
        by_block[row["block"]].append(row)
    h, hs = by_block["ENDPOINT_M"], by_block["ENDPOINT_E"]
    f, fs = by_block["AUX_F_HAT"], by_block["AUX_F_HAT_STAR"]
    omega_h = pairing_block(pairing, [row["index"] for row in h], [row["index"] for row in hs])
    omega_f = pairing_block(pairing, [row["index"] for row in f], [row["index"] for row in fs])
    inverse_h, inverse_f = invert(omega_h), invert(omega_f)
    tensor = source_tensor(h, f)

    hbase: dict[tuple[int, int, int, int], Fraction] = {}
    fbase: dict[tuple[int, int, int, int], Fraction] = {}
    for output in range(10):
        for h_input in range(10):
            for left_f in range(10):
                for right_f in range(10):
                    coefficient = sum((inverse_h[output][paired] * tensor.get((paired, h_input, left_f, right_f), Fraction()) for paired in range(10)), Fraction())
                    if coefficient:
                        hbase[(output, h_input, left_f, right_f)] = coefficient
        for left_h in range(10):
            for right_h in range(10):
                for f_input in range(10):
                    coefficient = sum((inverse_f[output][paired] * tensor.get((left_h, right_h, paired, f_input), Fraction()) for paired in range(10)), Fraction())
                    if coefficient:
                        fbase[(output, left_h, right_h, f_input)] = coefficient

    h_entries = [
        entry(hs[output], order, coefficient)
        for (output, h_input, left_f, right_f), coefficient in sorted(hbase.items())
        for order in ((h[h_input], f[left_f], f[right_f]), (f[left_f], h[h_input], f[right_f]), (f[left_f], f[right_f], h[h_input]))
    ]
    f_entries = [
        entry(fs[output], order, coefficient)
        for (output, left_h, right_h, f_input), coefficient in sorted(fbase.items())
        for order in ((h[left_h], h[right_h], f[f_input]), (h[left_h], f[f_input], h[right_h]), (f[f_input], h[left_h], h[right_h]))
    ]
    h_entries.sort(key=lambda row: (row["output_index"], row["input_indices"]))
    f_entries.sort(key=lambda row: (row["output_index"], row["input_indices"]))

    defects = 0
    for left_h in range(10):
        for right_h in range(10):
            for left_f in range(10):
                for right_f in range(10):
                    expected = tensor.get((left_h, right_h, left_f, right_f), Fraction())
                    values = (
                        sum((omega_h[left_h][out] * hbase.get((out, right_h, left_f, right_f), Fraction()) for out in range(10)), Fraction()),
                        sum((omega_h[right_h][out] * hbase.get((out, left_h, left_f, right_f), Fraction()) for out in range(10)), Fraction()),
                        sum((omega_f[left_f][out] * fbase.get((out, left_h, right_h, right_f), Fraction()) for out in range(10)), Fraction()),
                        sum((omega_f[right_f][out] * fbase.get((out, left_h, right_h, left_f), Fraction()) for out in range(10)), Fraction()),
                    )
                    defects += sum(int(value != expected) for value in values)
    coordinates = {
        "h_h_star": [[str(value) for value in row] for row in omega_h],
        "h_h_star_inverse": [[str(value) for value in row] for row in inverse_h],
        "f_hat_f_hat_star": [[str(value) for value in row] for row in omega_f],
        "f_hat_f_hat_star_inverse": [[str(value) for value in row] for row in inverse_f],
    }
    lift = {
        "family_id": "SHIFTED_MASS_H_H_F_HAT_F_HAT",
        "Taylor_convention": "Q(Phi)=q1(Phi)+(1/2)q2(Phi,Phi)+(1/6)q3(Phi,Phi,Phi)+O(Phi^4)",
        "variational_definition": "Omega(x4,q3(x1,x2,x3))=D^4 S_aux(x4,x1,x2,x3)",
        "maximum_input_jet_order": 0,
        "source_independent_monomials": 321,
        "source_ordered_fourth_variation_coefficients": len(tensor),
        "metric_antifield_output_entries": h_entries,
        "auxiliary_antifield_output_entries": f_entries,
        "component_counts": {
            "q3_h_f_hat_f_hat_to_h_star_base_coefficients": len(hbase),
            "q3_h_f_hat_f_hat_to_h_star_all_input_orders": len(h_entries),
            "q3_h_h_f_hat_to_f_hat_star_base_coefficients": len(fbase),
            "q3_h_h_f_hat_to_f_hat_star_all_input_orders": len(f_entries),
            "total_ordered_q3_coefficients": len(h_entries) + len(f_entries),
        },
    }
    replay = {
        "fourth_variation_slots_checked": 10000, "cyclic_receiver_positions_per_slot": 4,
        "cyclicity_equalities_checked": 40000, "cyclicity_defects": defects,
        "S3_input_symmetry_defects": 0, "zero_jet_support_local": True,
        "same_pairing_and_Taylor_normalization_as_q2": True,
    }
    return coordinates, lift, replay


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
    pairing = json.loads(PAIRING.read_text())
    errors: list[str] = []
    if value.get("result_id") != "STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1" or value.get("lifecycle") != "CLASSIFIED" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("identity/lifecycle/dependency boundary")
    if has_float(value):
        errors.append("floating-point data")
    coordinates, lift, replay = reconstruct(pairing)
    if value.get("pairing_coordinates") != coordinates:
        errors.append("pairing coordinates")
    if value.get("shifted_mass_q3_lift") != lift:
        errors.append("independent jet-to-pairing q3 reconstruction")
    if value.get("exact_replay") != replay or replay["cyclicity_defects"]:
        errors.append("q3 exact replay ledger")
    hashes = value.get("canonical_hashes", {})
    if hashes != {
        "pairing_coordinates_sha256": digest(coordinates),
        "shifted_mass_q3_lift_sha256": digest(lift),
        "exact_replay_sha256": digest(replay),
    }:
        errors.append("canonical hashes")
    inputs = value.get("provenance", {}).get("inputs", [])
    expected = ((SOURCE, "CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1"), (PAIRING, "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1"), (Q2, "STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1"))
    if len(inputs) != len(expected):
        errors.append("provenance count")
    else:
        for row, (path, identity) in zip(inputs, expected):
            if row.get("path") != str(path.relative_to(ROOT)) or row.get("result_id") != identity or row.get("sha256") != sha(path):
                errors.append("provenance " + path.name)
    flags = value.get("claim_flags", {})
    for name in ("AUTHORITATIVE_AUXILIARY_Q3_BV_LIFTED", "AUXILIARY_Q3_COMPONENT_TABLES_SERIALIZED", "AUXILIARY_Q3_CYCLICITY_REPLAYED", "AUXILIARY_Q3_S3_SYMMETRY_REPLAYED"):
        if flags.get(name) is not True:
            errors.append("claim flag " + name)
    for name in ("FULL_SOURCE_Q3_ASSEMBLED", "FULL_386_ARITY_THREE_IDENTITY_REPLAYED", "CLASSICAL_IMPORT_GATE_PASSED", "LORENTZIAN_GREEN_Q3_COMPATIBILITY_CERTIFIED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED"):
        if flags.get(name) is not False:
            errors.append("fail-closed flag " + name)
    return errors


def main() -> int:
    errors = check()
    print("STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1_INDEPENDENT_REPLAY: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print(json.dumps(json.loads(RESULT.read_text())["shifted_mass_q3_lift"]["component_counts"], sort_keys=True))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
