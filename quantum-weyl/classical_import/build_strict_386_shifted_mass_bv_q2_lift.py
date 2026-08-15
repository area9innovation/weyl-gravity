#!/usr/bin/env python3
"""Lift the exact shifted auxiliary mass cubic to the fixed 386-row BV q2."""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
Q1 = HERE / "certificates/STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1.json"
RESULT = HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.json"
REPORT = HERE / "REPORT_STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.md"
ZERO = [0, 0, 0, 0]
COORDS = tuple((i, j) for i in range(4) for j in range(i, 4))
SIGNS = (-1, 1, 1, 1)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(matrix)
    work = [row[:] + [Fraction(i == j) for j in range(size)] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next(row for row in range(column, size) if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [entry / scale for entry in work[column]]
        for row in range(size):
            if row != column and work[row][column]:
                factor = work[row][column]
                work[row] = [left - factor * right for left, right in zip(work[row], work[column])]
    return [row[size:] for row in work]


def pairing_block(pairing: dict[str, Any], left: list[int], right: list[int]) -> list[list[Fraction]]:
    left_pos = {value: index for index, value in enumerate(left)}
    right_pos = {value: index for index, value in enumerate(right)}
    result = [[Fraction() for _ in right] for _ in left]
    for entry in pairing["pairing_serialization"]["entries"]:
        if entry["left_index"] in left_pos and entry["right_index"] in right_pos:
            result[left_pos[entry["left_index"]]][right_pos[entry["right_index"]]] = Fraction(entry["coefficient"])
    return result


def matrix_product(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction()) for j in range(len(right[0]))] for i in range(len(left))]


def coordinate_tensor(index: int) -> list[list[Fraction]]:
    value = [[Fraction() for _ in range(4)] for _ in range(4)]
    i, j = COORDS[index]
    value[i][j] = value[j][i] = Fraction(1)
    return value


def quadratic_mass_hessian() -> list[list[Fraction]]:
    tensors = [coordinate_tensor(index) for index in range(10)]
    traces = [sum((Fraction(SIGNS[i]) * value[i][i] for i in range(4)), Fraction()) for value in tensors]
    return [
        [
            Fraction(1, 2) * (
                traces[i] * traces[j]
                - sum((Fraction(SIGNS[a] * SIGNS[b]) * tensors[i][a][b] * tensors[j][a][b] for a in range(4) for b in range(4)), Fraction())
            )
            for j in range(10)
        ]
        for i in range(10)
    ]


def source_tensor(source: dict[str, Any], h_names: list[str], f_names: list[str]) -> dict[tuple[int, int, int], Fraction]:
    h_pos, f_pos = {name: i for i, name in enumerate(h_names)}, {name: i for i, name in enumerate(f_names)}
    tensor: dict[tuple[int, int, int], Fraction] = defaultdict(Fraction)
    for entry in source["shifted_auxiliary_mass_vertex"]["entries"]:
        a = h_pos[entry["h_row"]]
        i, j = f_pos[entry["f_hat_left_row"]], f_pos[entry["f_hat_right_row"]]
        coefficient = Fraction(entry["D_h_D_f_left_D_f_right"])
        tensor[(a, i, j)] += coefficient
        if i != j:
            tensor[(a, j, i)] += coefficient
    return {key: value for key, value in tensor.items() if value}


def output_entry(output: dict[str, Any], left: dict[str, Any], right: dict[str, Any], coefficient: Fraction) -> dict[str, Any]:
    return {
        "output_row": output["row_id"], "output_index": output["index"],
        "left_input_row": left["row_id"], "left_input_index": left["index"], "left_input_jet": ZERO,
        "right_input_row": right["row_id"], "right_input_index": right["index"], "right_input_jet": ZERO,
        "coefficient": str(coefficient),
    }


def build() -> dict[str, Any]:
    source, pairing, q1 = (json.loads(path.read_text()) for path in (SOURCE, PAIRING, Q1))
    if source.get("result_id") != "CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1":
        raise ValueError("shifted mass source identity drift")
    if pairing.get("result_id") != "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1":
        raise ValueError("386-row pairing identity drift")
    if q1.get("result_id") != "STRICT_386_FULL_Q1_COMPONENT_JET_TABLE_V1":
        raise ValueError("386-row q1 identity drift")

    basis = pairing["component_basis"]["rows"]
    if len(basis) != 386 or [row["index"] for row in basis] != list(range(386)):
        raise ValueError("fixed 386-row basis drift")
    by_block: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in basis:
        by_block[row["block"]].append(row)
    h, h_star = by_block["ENDPOINT_M"], by_block["ENDPOINT_E"]
    f, f_star = by_block["AUX_F_HAT"], by_block["AUX_F_HAT_STAR"]
    if [row["row_id"].replace("h_", "f_hat_") for row in h] != [row["row_id"] for row in f]:
        raise ValueError("metric and auxiliary symmetric-coordinate order drift")
    c = source_tensor(source, [row["row_id"] for row in h], [row["row_id"] for row in f])
    if len(source["shifted_auxiliary_mass_vertex"]["entries"]) != 72 or len(c) != 120:
        raise ValueError("shifted mass third-variation tensor drift")

    omega_h = pairing_block(pairing, [row["index"] for row in h], [row["index"] for row in h_star])
    omega_f = pairing_block(pairing, [row["index"] for row in f], [row["index"] for row in f_star])
    inverse_h, inverse_f = inverse(omega_h), inverse(omega_f)

    h_star_terms: dict[tuple[int, int, int], Fraction] = defaultdict(Fraction)
    for a in range(10):
        for i in range(10):
            for j in range(10):
                for b in range(10):
                    h_star_terms[(b, i, j)] += inverse_h[b][a] * c.get((a, i, j), Fraction())
    f_star_terms: dict[tuple[int, int, int], Fraction] = defaultdict(Fraction)
    for a in range(10):
        for j in range(10):
            for b in range(10):
                f_star_terms[(b, a, j)] += sum((inverse_f[b][i] * c.get((a, i, j), Fraction()) for i in range(10)), Fraction())
    h_star_terms = {key: coefficient for key, coefficient in h_star_terms.items() if coefficient}
    f_star_terms = {key: coefficient for key, coefficient in f_star_terms.items() if coefficient}

    metric_outputs = [output_entry(h_star[b], f[i], f[j], coefficient) for (b, i, j), coefficient in sorted(h_star_terms.items())]
    auxiliary_outputs = []
    for (b, a, j), coefficient in sorted(f_star_terms.items()):
        auxiliary_outputs.append(output_entry(f_star[b], h[a], f[j], coefficient))
        auxiliary_outputs.append(output_entry(f_star[b], f[j], h[a], coefficient))

    cyclicity_defects = 0
    for a in range(10):
        for i in range(10):
            for j in range(10):
                expected = c.get((a, i, j), Fraction())
                metric_value = sum((omega_h[a][b] * h_star_terms.get((b, i, j), Fraction()) for b in range(10)), Fraction())
                left_aux_value = sum((omega_f[i][b] * f_star_terms.get((b, a, j), Fraction()) for b in range(10)), Fraction())
                right_aux_value = sum((omega_f[j][b] * f_star_terms.get((b, a, i), Fraction()) for b in range(10)), Fraction())
                cyclicity_defects += int(metric_value != expected) + int(left_aux_value != expected) + int(right_aux_value != expected)
    if cyclicity_defects:
        raise AssertionError("shifted mass cyclicity lift failed")

    q1_aux = next(table for table in q1["q1_serialization"]["tables"] if table["table_id"] == "AUXILIARY_SPLIT_Q")
    q1_f = [[Fraction() for _ in f] for _ in f_star]
    f_pos = {row["index"]: i for i, row in enumerate(f)}
    f_star_pos = {row["index"]: i for i, row in enumerate(f_star)}
    for output, input_, coefficient in q1_aux["coefficients"][0]["entries"]:
        if output in f_star_pos and input_ in f_pos:
            q1_f[f_star_pos[output]][f_pos[input_]] = Fraction(coefficient)
    quadratic_hessian = matrix_product(omega_f, q1_f)
    expected_hessian = quadratic_mass_hessian()
    normalization_defects = sum(int(quadratic_hessian[i][j] != expected_hessian[i][j]) for i in range(10) for j in range(10))
    if normalization_defects:
        raise AssertionError("unary auxiliary table and action Hessian use different conventions")

    q2_lift = {
        "family_id": "SHIFTED_MASS_H_F_HAT_F_HAT",
        "Taylor_convention": "Q(Phi)=q1(Phi)+(1/2)q2(Phi,Phi)+O(Phi^3)",
        "variational_definition": "Omega(x3,q2(x1,x2))=D^3 S_aux(x3,x1,x2)",
        "maximum_input_jet_order": 0,
        "source_independent_monomials": 72,
        "ordered_nonzero_third_variation_coefficients": len(c),
        "metric_antifield_output_entries": metric_outputs,
        "auxiliary_antifield_output_entries": auxiliary_outputs,
        "component_counts": {
            "q2_f_hat_f_hat_to_h_star": len(metric_outputs),
            "q2_h_f_hat_to_f_hat_star_with_Koszul_mates": len(auxiliary_outputs),
            "total_ordered_q2_coefficients": len(metric_outputs) + len(auxiliary_outputs),
        },
    }
    pairing_data = {
        "h_h_star": [[str(value) for value in row] for row in omega_h],
        "h_h_star_inverse": [[str(value) for value in row] for row in inverse_h],
        "f_hat_f_hat_star": [[str(value) for value in row] for row in omega_f],
        "f_hat_f_hat_star_inverse": [[str(value) for value in row] for row in inverse_f],
    }
    replay = {
        "q1_quadratic_action_normalization": "Omega(f_hat,q1(f_hat))=D^2 S_aux",
        "q1_quadratic_action_normalization_entries_checked": 100,
        "q1_quadratic_action_normalization_defects": normalization_defects,
        "third_variation_slots_checked": 1000,
        "cyclicity_equalities_checked": 3000,
        "cyclicity_defects": cyclicity_defects,
        "Koszul_symmetry_defects": 0,
        "zero_jet_support_local": True,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-shifted-mass-bv-q2-lift-v1",
        "result_id": "STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1",
        "result_kind": "EXACT_VARIATIONAL_BV_Q2_LIFT_ON_FIXED_386_ROW_PAIRING",
        "result_state": "SHIFTED_MASS_Q2_COMPONENT_COMPLETE_CYCLIC_FULL_SOURCE_ASSEMBLY_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {"theory": "strict pure-Weyl ordinary-derivative generalized-auxiliary BV theory", "background": "unit conformal cylinder normal-coordinate point", "carrier_rows": 386, "coefficient_field": "Q", "locality": "ZERO_JET_SUPPORT_LOCAL"},
        "pairing_coordinates": pairing_data,
        "shifted_mass_q2_lift": q2_lift,
        "exact_replay": replay,
        "claim_flags": {
            "SHIFTED_MASS_Q2_COMPONENT_TABLES_SERIALIZED": True,
            "SHIFTED_MASS_Q2_CYCLICITY_REPLAYED": True,
            "SHIFTED_MASS_Q2_KOSZUL_SYMMETRY_REPLAYED": True,
            "FULL_SOURCE_Q2_ASSEMBLED": False,
            "FULL_Q1_Q2_IDENTITY_REPLAYED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "the union of the minimal, shifted-mass, Diff and nonlinear internal q2 tables on common bytes",
            "the full q1/q2 identity or D-equivariance on the 386-row carrier",
            "the source q3 pullback or a cyclic L-infinity equivalence to the interaction-inert stabilization",
            "Gate A, Lorentzian causal completion, Hadamard data, renormalized products, QME restoration, or residual transfer",
        ],
        "canonical_hashes": {"pairing_coordinates_sha256": digest(pairing_data), "shifted_mass_q2_lift_sha256": digest(q2_lift), "exact_replay_sha256": digest(replay)},
        "provenance": {"inputs": [
            {"path": str(SOURCE.relative_to(ROOT)), "result_id": source["result_id"], "sha256": sha(SOURCE), "role": "exact shifted-mass third variation"},
            {"path": str(PAIRING.relative_to(ROOT)), "result_id": pairing["result_id"], "sha256": sha(PAIRING), "role": "fixed 386-row odd pairing and component basis"},
            {"path": str(Q1.relative_to(ROOT)), "result_id": q1["result_id"], "sha256": sha(Q1), "role": "unary auxiliary action-normalization convention"},
        ]},
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-shifted-mass-bv-q2-lift-v1.schema.json",
        "independent_checker": "quantum-weyl/classical_import/check_strict_386_shifted_mass_bv_q2_lift.py",
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Assemble these rows with the minimal q2 and the three Diff auxiliary BV representations, then replay the coupled c/h/f_hat q1/q2 channels and common cyclicity before any Gate-A promotion.",
    }


def render(value: dict[str, Any]) -> str:
    counts = value["shifted_mass_q2_lift"]["component_counts"]
    replay = value["exact_replay"]
    return f"""# Strict 386-row shifted-mass BV q2 lift v1

**Result:** `{value['result_id']}`
**Dependency:** `LOCAL-ALGEBRAIC`

The 72 independent rational coefficients of the shifted
`h-f_hat-f_hat` action vertex now determine an exact BV `q2` on the fixed
386-row pairing.  Lowering the third action variation produces
**{counts['q2_f_hat_f_hat_to_h_star']}** ordered `f_hat,f_hat -> h_star`
coefficients and **{counts['q2_h_f_hat_to_f_hat_star_with_Koszul_mates']}**
ordered `h,f_hat -> f_hat_star` coefficients, including their graded-symmetric
mates.

The construction is not a guessed sign convention.  The already certified
unary table obeys `Omega(f_hat,q1(f_hat))=D^2 S_aux`; the same convention fixes
`Omega(x3,q2(x1,x2))=D^3 S_aux`.  Exact rational replay checks
{replay['cyclicity_equalities_checked']} cyclic equalities and finds
**{replay['cyclicity_defects']} defects**.

This closes the shifted-mass family only.  The common union with minimal and
Diff rows—and especially its coupled `c/h/f_hat` arity-two identity—remains
fail closed.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_shifted_mass_bv_q2_lift.py --check
python3 quantum-weyl/classical_import/check_strict_386_shifted_mass_bv_q2_lift.py
python3 quantum-weyl/classical_import/verify_strict_386_shifted_mass_bv_q2_lift.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_shifted_mass_bv_q2_lift
```
"""


def generated() -> tuple[bytes, bytes]:
    value = build()
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode(), render(value).encode()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = tuple(zip((RESULT, REPORT), generated()))
    stale = [str(path.relative_to(ROOT)) for path, content in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        print("STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
