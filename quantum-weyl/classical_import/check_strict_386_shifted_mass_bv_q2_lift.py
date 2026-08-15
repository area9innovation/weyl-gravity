#!/usr/bin/env python3
"""Independent exact replay of the shifted-mass BV q2 lift."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
RESULT = HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.json"
SOURCE = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
COORDS = tuple((i, j) for i in range(4) for j in range(i, 4))
SIGNS = (-1, 1, 1, 1)


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def invert(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    n = len(matrix)
    work = [row[:] + [Fraction(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for k in range(n):
        pivot = next(i for i in range(k, n) if work[i][k])
        work[k], work[pivot] = work[pivot], work[k]
        scale = work[k][k]
        work[k] = [x / scale for x in work[k]]
        for i in range(n):
            if i != k and work[i][k]:
                factor = work[i][k]
                work[i] = [x - factor * y for x, y in zip(work[i], work[k])]
    return [row[n:] for row in work]


def tensor(index: int) -> list[list[Fraction]]:
    value = [[Fraction() for _ in range(4)] for _ in range(4)]
    i, j = COORDS[index]
    value[i][j] = value[j][i] = Fraction(1)
    return value


def add(*values: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum((value[i][j] for value in values), Fraction()) for j in range(4)] for i in range(4)]


def trace(value: list[list[Fraction]]) -> Fraction:
    return sum((Fraction(SIGNS[i]) * value[i][i] for i in range(4)), Fraction())


def inner(left: list[list[Fraction]], right: list[list[Fraction]]) -> Fraction:
    return sum((Fraction(SIGNS[i] * SIGNS[j]) * left[i][j] * right[i][j] for i in range(4) for j in range(4)), Fraction())


def raised(value: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[Fraction(SIGNS[i] * SIGNS[j]) * value[i][j] for j in range(4)] for i in range(4)]


def mass_cubic(h: list[list[Fraction]], f: list[list[Fraction]]) -> Fraction:
    h_up = raised(h)
    h_dot_f = sum((h_up[i][j] * f[i][j] for i in range(4) for j in range(4)), Fraction())
    chain = sum((h_up[mu][alpha] * Fraction(SIGNS[nu]) * f[alpha][nu] * f[mu][nu] for mu in range(4) for alpha in range(4) for nu in range(4)), Fraction())
    return Fraction(1, 8) * trace(h) * (trace(f) ** 2 - inner(f, f)) - Fraction(1, 2) * trace(f) * h_dot_f + Fraction(1, 2) * chain


def cubic_tensor() -> dict[tuple[int, int, int], Fraction]:
    result: dict[tuple[int, int, int], Fraction] = {}
    tensors = [tensor(i) for i in range(10)]
    for a, h in enumerate(tensors):
        for i, left in enumerate(tensors):
            for j, right in enumerate(tensors):
                value = mass_cubic(h, add(left, right)) - mass_cubic(h, left) - mass_cubic(h, right)
                if value:
                    result[(a, i, j)] = value
    return result


def block(pairing: dict[str, Any], left: list[int], right: list[int]) -> list[list[Fraction]]:
    entries = {(item["left_index"], item["right_index"]): Fraction(item["coefficient"]) for item in pairing["pairing_serialization"]["entries"]}
    return [[entries.get((i, j), Fraction()) for j in right] for i in left]


def listed(entries: list[dict[str, Any]]) -> dict[tuple[int, int, int], Fraction]:
    return {(item["output_index"], item["left_input_index"], item["right_input_index"]): Fraction(item["coefficient"]) for item in entries}


def check(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source, pairing, q1 = (json.loads(path.read_text()) for path in (SOURCE, PAIRING, Q1))
    basis = pairing["component_basis"]["rows"]
    by_block: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in basis:
        by_block[row["block"]].append(row)
    h, hs = by_block["ENDPOINT_M"], by_block["ENDPOINT_E"]
    f, fs = by_block["AUX_F_HAT"], by_block["AUX_F_HAT_STAR"]
    oh = block(pairing, [row["index"] for row in h], [row["index"] for row in hs])
    of = block(pairing, [row["index"] for row in f], [row["index"] for row in fs])
    ih, iff = invert(oh), invert(of)
    c = cubic_tensor()
    if len(c) != 120:
        errors.append("independent third-variation coefficient count drift")

    expected_hs: dict[tuple[int, int, int], Fraction] = {}
    for b in range(10):
        for i in range(10):
            for j in range(10):
                coefficient = sum((ih[b][a] * c.get((a, i, j), Fraction()) for a in range(10)), Fraction())
                if coefficient:
                    expected_hs[(hs[b]["index"], f[i]["index"], f[j]["index"])] = coefficient
    expected_fs: dict[tuple[int, int, int], Fraction] = {}
    for b in range(10):
        for a in range(10):
            for j in range(10):
                coefficient = sum((iff[b][i] * c.get((a, i, j), Fraction()) for i in range(10)), Fraction())
                if coefficient:
                    expected_fs[(fs[b]["index"], h[a]["index"], f[j]["index"])] = coefficient
                    expected_fs[(fs[b]["index"], f[j]["index"], h[a]["index"])] = coefficient
    lift = value.get("shifted_mass_q2_lift", {})
    if listed(lift.get("metric_antifield_output_entries", [])) != expected_hs:
        errors.append("f_hat,f_hat -> h_star variational lift mismatch")
    if listed(lift.get("auxiliary_antifield_output_entries", [])) != expected_fs:
        errors.append("h,f_hat -> f_hat_star variational lift mismatch")

    source_rows = {(item["h_row"], item["f_hat_left_row"], item["f_hat_right_row"]): Fraction(item["D_h_D_f_left_D_f_right"]) for item in source["shifted_auxiliary_mass_vertex"]["entries"]}
    independent_rows = {}
    for a in range(10):
        for i in range(10):
            for j in range(i, 10):
                coefficient = c.get((a, i, j), Fraction())
                if coefficient:
                    independent_rows[(h[a]["row_id"], f[i]["row_id"], f[j]["row_id"])] = coefficient
    if source_rows != independent_rows:
        errors.append("classical source cubic formula replay mismatch")

    q1_aux = next(table for table in q1["q1_serialization"]["tables"] if table["table_id"] == "AUXILIARY_SPLIT_Q")
    k = [[Fraction() for _ in f] for _ in fs]
    f_pos = {row["index"]: i for i, row in enumerate(f)}
    fs_pos = {row["index"]: i for i, row in enumerate(fs)}
    for output, input_, coefficient in q1_aux["coefficients"][0]["entries"]:
        if output in fs_pos and input_ in f_pos:
            k[fs_pos[output]][f_pos[input_]] = Fraction(coefficient)
    hessian = [[sum((of[i][b] * k[b][j] for b in range(10)), Fraction()) for j in range(10)] for i in range(10)]
    tensors = [tensor(i) for i in range(10)]
    direct_hessian = [[Fraction(1, 2) * (trace(tensors[i]) * trace(tensors[j]) - inner(tensors[i], tensors[j])) for j in range(10)] for i in range(10)]
    if hessian != direct_hessian:
        errors.append("unary action normalization does not match quadratic mass Hessian")

    counts = {"q2_f_hat_f_hat_to_h_star": len(expected_hs), "q2_h_f_hat_to_f_hat_star_with_Koszul_mates": len(expected_fs), "total_ordered_q2_coefficients": len(expected_hs) + len(expected_fs)}
    if lift.get("component_counts") != counts:
        errors.append("q2 component-count ledger mismatch")
    replay = value.get("exact_replay", {})
    if replay != {"q1_quadratic_action_normalization": "Omega(f_hat,q1(f_hat))=D^2 S_aux", "q1_quadratic_action_normalization_entries_checked": 100, "q1_quadratic_action_normalization_defects": 0, "third_variation_slots_checked": 1000, "cyclicity_equalities_checked": 3000, "cyclicity_defects": 0, "Koszul_symmetry_defects": 0, "zero_jet_support_local": True}:
        errors.append("exact replay ledger mismatch")
    pairing_expected = {"h_h_star": [[str(x) for x in row] for row in oh], "h_h_star_inverse": [[str(x) for x in row] for row in ih], "f_hat_f_hat_star": [[str(x) for x in row] for row in of], "f_hat_f_hat_star_inverse": [[str(x) for x in row] for row in iff]}
    if value.get("pairing_coordinates") != pairing_expected:
        errors.append("pairing-coordinate ledger mismatch")
    hashes = value.get("canonical_hashes", {})
    expected_hashes = {"pairing_coordinates_sha256": canonical_digest(value.get("pairing_coordinates")), "shifted_mass_q2_lift_sha256": canonical_digest(lift), "exact_replay_sha256": canonical_digest(replay)}
    if hashes != expected_hashes:
        errors.append("canonical digest mismatch")
    pins = {item.get("path"): item.get("sha256") for item in value.get("provenance", {}).get("inputs", [])}
    if pins != {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (SOURCE, PAIRING, Q1)}:
        errors.append("input provenance pin mismatch")
    flags = value.get("claim_flags", {})
    for name in ("SHIFTED_MASS_Q2_COMPONENT_TABLES_SERIALIZED", "SHIFTED_MASS_Q2_CYCLICITY_REPLAYED", "SHIFTED_MASS_Q2_KOSZUL_SYMMETRY_REPLAYED"):
        if flags.get(name) is not True:
            errors.append(f"claim flag drift: {name}")
    for name in ("FULL_SOURCE_Q2_ASSEMBLED", "FULL_Q1_Q2_IDENTITY_REPLAYED", "CLASSICAL_IMPORT_GATE_PASSED", "LORENTZIAN_CAUSAL_CERTIFIED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED"):
        if flags.get(name) is not False:
            errors.append(f"fail-closed flag drift: {name}")
    if value.get("result_id") != "STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("result identity or dependency boundary mismatch")
    return errors


def main() -> int:
    value = json.loads(RESULT.read_text())
    errors = check(value)
    print("STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1_INDEPENDENT_REPLAY: " + ("PASS" if not errors else "FAIL"))
    if not errors:
        print(json.dumps(value["shifted_mass_q2_lift"]["component_counts"], sort_keys=True))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
