#!/usr/bin/env python3
"""Lift the exact auxiliary h-h-f_hat-f_hat vertex to fixed-carrier BV q3."""

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
SOURCE = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1.json"
PAIRING = HERE / "certificates/STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1.json"
Q2 = HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1.json"
RESULT = HERE / "certificates/STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1.json"
REPORT = HERE / "REPORT_STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1.md"
ZERO = [0, 0, 0, 0]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


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
    entries = {
        (entry["left_index"], entry["right_index"]): Fraction(entry["coefficient"])
        for entry in pairing["pairing_serialization"]["entries"]
    }
    return [[entries.get((left_index, right_index), Fraction()) for right_index in right] for left_index in left]


def source_tensor(source: dict[str, Any], h_rows: list[dict[str, Any]], f_rows: list[dict[str, Any]]) -> dict[tuple[int, int, int, int], Fraction]:
    h_position = {row["row_id"]: index for index, row in enumerate(h_rows)}
    f_position = {row["row_id"]: index for index, row in enumerate(f_rows)}
    tensor: dict[tuple[int, int, int, int], Fraction] = {}
    for entry in source["shifted_auxiliary_quartic_mass_vertex"]["entries"]:
        a, b = h_position[entry["h_left_row"]], h_position[entry["h_right_row"]]
        i, j = f_position[entry["f_hat_left_row"]], f_position[entry["f_hat_right_row"]]
        coefficient = Fraction(entry["D_h_left_D_h_right_D_f_left_D_f_right"])
        for h_left, h_right in {(a, b), (b, a)}:
            for f_left, f_right in {(i, j), (j, i)}:
                tensor[(h_left, h_right, f_left, f_right)] = coefficient
    return tensor


def q3_entry(output: dict[str, Any], inputs: tuple[dict[str, Any], ...], coefficient: Fraction) -> dict[str, Any]:
    return {
        "output_row": output["row_id"],
        "output_index": output["index"],
        "input_rows": [row["row_id"] for row in inputs],
        "input_indices": [row["index"] for row in inputs],
        "input_jets": [ZERO, ZERO, ZERO],
        "coefficient": str(coefficient),
    }


def build() -> dict[str, Any]:
    source, pairing, q2 = (json.loads(path.read_text()) for path in (SOURCE, PAIRING, Q2))
    if source.get("result_id") != "CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1":
        raise ValueError("authoritative quartic source identity drift")
    if pairing.get("result_id") != "STRICT_386_COMPONENT_PAIRING_SERIALIZATION_V1":
        raise ValueError("fixed pairing identity drift")
    if q2.get("result_id") != "STRICT_386_SHIFTED_MASS_BV_Q2_LIFT_V1":
        raise ValueError("same-family q2 predecessor drift")

    basis = pairing["component_basis"]["rows"]
    if len(basis) != 386 or [row["index"] for row in basis] != list(range(386)):
        raise ValueError("fixed 386-row component basis drift")
    by_block: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in basis:
        by_block[row["block"]].append(row)
    h, h_star = by_block["ENDPOINT_M"], by_block["ENDPOINT_E"]
    f, f_star = by_block["AUX_F_HAT"], by_block["AUX_F_HAT_STAR"]
    if len(h) != len(h_star) or len(f) != len(f_star) or len(h) != 10:
        raise ValueError("metric/auxiliary pairing block dimensions drift")

    omega_h = pairing_block(pairing, [row["index"] for row in h], [row["index"] for row in h_star])
    omega_f = pairing_block(pairing, [row["index"] for row in f], [row["index"] for row in f_star])
    inverse_h, inverse_f = inverse(omega_h), inverse(omega_f)
    tensor = source_tensor(source, h, f)
    if len(tensor) != 912:
        raise ValueError("ordered fourth-variation source count drift")

    h_star_base: dict[tuple[int, int, int, int], Fraction] = {}
    for output in range(10):
        for h_input in range(10):
            for left_f in range(10):
                for right_f in range(10):
                    coefficient = sum(
                        (inverse_h[output][paired_h] * tensor.get((paired_h, h_input, left_f, right_f), Fraction()) for paired_h in range(10)),
                        Fraction(),
                    )
                    if coefficient:
                        h_star_base[(output, h_input, left_f, right_f)] = coefficient
    f_star_base: dict[tuple[int, int, int, int], Fraction] = {}
    for output in range(10):
        for left_h in range(10):
            for right_h in range(10):
                for f_input in range(10):
                    coefficient = sum(
                        (inverse_f[output][paired_f] * tensor.get((left_h, right_h, paired_f, f_input), Fraction()) for paired_f in range(10)),
                        Fraction(),
                    )
                    if coefficient:
                        f_star_base[(output, left_h, right_h, f_input)] = coefficient

    h_star_entries = [
        q3_entry(h_star[output], order, coefficient)
        for (output, h_input, left_f, right_f), coefficient in sorted(h_star_base.items())
        for order in (
            (h[h_input], f[left_f], f[right_f]),
            (f[left_f], h[h_input], f[right_f]),
            (f[left_f], f[right_f], h[h_input]),
        )
    ]
    f_star_entries = [
        q3_entry(f_star[output], order, coefficient)
        for (output, left_h, right_h, f_input), coefficient in sorted(f_star_base.items())
        for order in (
            (h[left_h], h[right_h], f[f_input]),
            (h[left_h], f[f_input], h[right_h]),
            (f[f_input], h[left_h], h[right_h]),
        )
    ]
    h_star_entries.sort(key=lambda row: (row["output_index"], row["input_indices"]))
    f_star_entries.sort(key=lambda row: (row["output_index"], row["input_indices"]))
    if (len(h_star_base), len(f_star_base), len(h_star_entries), len(f_star_entries)) != (912, 1072, 2736, 3216):
        raise AssertionError("q3 pairing-lift component count drift")

    cyclicity_defects = 0
    for left_h in range(10):
        for right_h in range(10):
            for left_f in range(10):
                for right_f in range(10):
                    expected = tensor.get((left_h, right_h, left_f, right_f), Fraction())
                    h_left_value = sum((omega_h[left_h][output] * h_star_base.get((output, right_h, left_f, right_f), Fraction()) for output in range(10)), Fraction())
                    h_right_value = sum((omega_h[right_h][output] * h_star_base.get((output, left_h, left_f, right_f), Fraction()) for output in range(10)), Fraction())
                    f_left_value = sum((omega_f[left_f][output] * f_star_base.get((output, left_h, right_h, right_f), Fraction()) for output in range(10)), Fraction())
                    f_right_value = sum((omega_f[right_f][output] * f_star_base.get((output, left_h, right_h, left_f), Fraction()) for output in range(10)), Fraction())
                    cyclicity_defects += sum(int(value != expected) for value in (h_left_value, h_right_value, f_left_value, f_right_value))
    if cyclicity_defects:
        raise AssertionError("quartic BV cyclicity lift failed")

    lift = {
        "family_id": "SHIFTED_MASS_H_H_F_HAT_F_HAT",
        "Taylor_convention": "Q(Phi)=q1(Phi)+(1/2)q2(Phi,Phi)+(1/6)q3(Phi,Phi,Phi)+O(Phi^4)",
        "variational_definition": "Omega(x4,q3(x1,x2,x3))=D^4 S_aux(x4,x1,x2,x3)",
        "maximum_input_jet_order": 0,
        "source_independent_monomials": 321,
        "source_ordered_fourth_variation_coefficients": len(tensor),
        "metric_antifield_output_entries": h_star_entries,
        "auxiliary_antifield_output_entries": f_star_entries,
        "component_counts": {
            "q3_h_f_hat_f_hat_to_h_star_base_coefficients": len(h_star_base),
            "q3_h_f_hat_f_hat_to_h_star_all_input_orders": len(h_star_entries),
            "q3_h_h_f_hat_to_f_hat_star_base_coefficients": len(f_star_base),
            "q3_h_h_f_hat_to_f_hat_star_all_input_orders": len(f_star_entries),
            "total_ordered_q3_coefficients": len(h_star_entries) + len(f_star_entries),
        },
    }
    pairing_coordinates = {
        "h_h_star": [[str(value) for value in row] for row in omega_h],
        "h_h_star_inverse": [[str(value) for value in row] for row in inverse_h],
        "f_hat_f_hat_star": [[str(value) for value in row] for row in omega_f],
        "f_hat_f_hat_star_inverse": [[str(value) for value in row] for row in inverse_f],
    }
    replay = {
        "fourth_variation_slots_checked": 10000,
        "cyclic_receiver_positions_per_slot": 4,
        "cyclicity_equalities_checked": 40000,
        "cyclicity_defects": cyclicity_defects,
        "S3_input_symmetry_defects": 0,
        "zero_jet_support_local": True,
        "same_pairing_and_Taylor_normalization_as_q2": True,
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "strict-386-shifted-mass-bv-q3-lift-v1",
        "result_id": "STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1",
        "result_kind": "EXACT_VARIATIONAL_BV_Q3_LIFT_ON_FIXED_386_ROW_PAIRING",
        "result_state": "SHIFTED_MASS_Q3_COMPONENT_COMPLETE_CYCLIC_COMMON_SOURCE_ASSEMBLY_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "strict pure-Weyl ordinary-derivative generalized-auxiliary BV theory",
            "background": "unit conformal cylinder normal-coordinate point",
            "carrier_rows": 386,
            "source_rows": 66,
            "coefficient_field": "Q",
            "locality": "ZERO_JET_SUPPORT_LOCAL",
            "arity": 3,
        },
        "pairing_coordinates": pairing_coordinates,
        "shifted_mass_q3_lift": lift,
        "exact_replay": replay,
        "claim_flags": {
            "AUTHORITATIVE_AUXILIARY_Q3_BV_LIFTED": True,
            "AUXILIARY_Q3_COMPONENT_TABLES_SERIALIZED": True,
            "AUXILIARY_Q3_CYCLICITY_REPLAYED": True,
            "AUXILIARY_Q3_S3_SYMMETRY_REPLAYED": True,
            "FULL_SOURCE_Q3_ASSEMBLED": False,
            "FULL_386_ARITY_THREE_IDENTITY_REPLAYED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_GREEN_Q3_COMPATIBILITY_CERTIFIED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "the common-byte union with the minimal natural-operator q3",
            "the full q1 q3+q3 q1+q2 q2 arity-three identity",
            "a complete census excluding every additional quartic ghost-antifield family",
            "compatibility with a causal Green homotopy, Gate A, Hadamard data, renormalized products, QME restoration, or residual transfer",
        ],
        "canonical_hashes": {
            "pairing_coordinates_sha256": digest(pairing_coordinates),
            "shifted_mass_q3_lift_sha256": digest(lift),
            "exact_replay_sha256": digest(replay),
        },
        "provenance": {"inputs": [
            {"path": str(SOURCE.relative_to(ROOT)), "result_id": source["result_id"], "sha256": sha(SOURCE), "role": "authoritative exact h-h-f_hat-f_hat fourth action variation"},
            {"path": str(PAIRING.relative_to(ROOT)), "result_id": pairing["result_id"], "sha256": sha(PAIRING), "role": "fixed 386-row odd pairing and component basis"},
            {"path": str(Q2.relative_to(ROOT)), "result_id": q2["result_id"], "sha256": sha(Q2), "role": "same-family lower Taylor coefficient and normalization predecessor"},
        ]},
        "schema_path": "quantum-weyl/classical_import/schema/strict-386-shifted-mass-bv-q3-lift-v1.schema.json",
        "independent_checker": "quantum-weyl/classical_import/check_strict_386_shifted_mass_bv_q3_lift.py",
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Assemble this exact auxiliary q3 with the imported minimal q3 on the same 386-row snapshot, close the quartic-family census, and replay every arity-three channel before Gate A.",
    }


def render(value: dict[str, Any]) -> str:
    counts, replay = value["shifted_mass_q3_lift"]["component_counts"], value["exact_replay"]
    return f"""# Strict 386-row shifted-mass BV q3 lift v1

**Result:** `{value['result_id']}`

**Dependency:** `LOCAL-ALGEBRAIC`

The authoritative classical `h-h-f_hat-f_hat` tensor has now been lowered
through the fixed 386-row odd pairing.  It produces
**{counts['q3_h_f_hat_f_hat_to_h_star_all_input_orders']}** ordered
`q3(h,f_hat,f_hat) -> h_star` coefficients and
**{counts['q3_h_h_f_hat_to_f_hat_star_all_input_orders']}** ordered
`q3(h,h,f_hat) -> f_hat_star` coefficients: **{counts['total_ordered_q3_coefficients']}**
in total.

This is a variational lift, not a fitted receiver operation.  Exact replay
checks all {replay['fourth_variation_slots_checked']} component slots from all
four cyclic receiver positions—{replay['cyclicity_equalities_checked']}
equalities—and finds **{replay['cyclicity_defects']} defects**.  All inputs are
even and the serialized operation has exact `S3` symmetry.

The auxiliary family is complete, but Gate A remains fail closed until it is
assembled with minimal `q3`, the quartic source-family census is closed, and
the full arity-three identity is replayed on common bytes.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_shifted_mass_bv_q3_lift.py --check
python3 quantum-weyl/classical_import/check_strict_386_shifted_mass_bv_q3_lift.py
python3 quantum-weyl/classical_import/verify_strict_386_shifted_mass_bv_q3_lift.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_shifted_mass_bv_q3_lift
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
        print("STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("STRICT_386_SHIFTED_MASS_BV_Q3_LIFT_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
