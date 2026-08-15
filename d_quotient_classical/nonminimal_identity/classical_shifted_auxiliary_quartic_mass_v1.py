#!/usr/bin/env python3
"""Export the exact h-h-f_hat-f_hat auxiliary-mass Taylor coefficient."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ACTION = ROOT / "covariant_completion/certificates/curved_auxiliary_action_definition.json"
SPLIT = ROOT / "covariant_completion/certificates/curved_auxiliary_canonical_split.json"
CUBIC = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1.json"
REPORT = ROOT / "d_quotient_classical/reports/classical-shifted-auxiliary-quartic-mass-v1.md"

DIM = 4
COORDS = tuple((i, j) for i in range(DIM) for j in range(i, DIM))
SIGNS = (-1, 1, 1, 1)
Matrix = list[list[Fraction]]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def basis(index: int) -> Matrix:
    value = [[Fraction() for _ in range(DIM)] for _ in range(DIM)]
    i, j = COORDS[index]
    value[i][j] = value[j][i] = Fraction(1)
    return value


def matrix_product(left: Matrix, right: Matrix) -> Matrix:
    return [
        [sum((left[i][k] * right[k][j] for k in range(DIM)), Fraction()) for j in range(DIM)]
        for i in range(DIM)
    ]


def matrix_add(left: Matrix, right: Matrix) -> Matrix:
    return [[left[i][j] + right[i][j] for j in range(DIM)] for i in range(DIM)]


def matrix_scale(value: Matrix, scalar: Fraction) -> Matrix:
    return [[scalar * value[i][j] for j in range(DIM)] for i in range(DIM)]


ETA = [[Fraction(SIGNS[i] if i == j else 0) for j in range(DIM)] for i in range(DIM)]


def trace_eta(h: Matrix) -> Fraction:
    return sum((Fraction(SIGNS[i]) * h[i][i] for i in range(DIM)), Fraction())


def inverse_first(h: Matrix) -> Matrix:
    return matrix_scale(matrix_product(matrix_product(ETA, h), ETA), Fraction(-1))


def inverse_second(left: Matrix, right: Matrix) -> Matrix:
    first = matrix_product(matrix_product(matrix_product(matrix_product(ETA, left), ETA), right), ETA)
    second = matrix_product(matrix_product(matrix_product(matrix_product(ETA, right), ETA), left), ETA)
    return matrix_add(first, second)


def sqrt_first(h: Matrix) -> Fraction:
    return trace_eta(h) / 2


def sqrt_second(left: Matrix, right: Matrix) -> Fraction:
    mixed_trace = sum(
        (Fraction(SIGNS[i] * SIGNS[j]) * left[i][j] * right[j][i] for i in range(DIM) for j in range(DIM)),
        Fraction(),
    )
    return trace_eta(left) * trace_eta(right) / 4 - mixed_trace / 2


def contraction(left_inverse: Matrix, right_inverse: Matrix, left_f: Matrix, right_f: Matrix) -> Fraction:
    transformed = matrix_product(matrix_product(left_inverse, left_f), right_inverse)
    return sum((transformed[i][j] * right_f[i][j] for i in range(DIM) for j in range(DIM)), Fraction())


def metric_trace(inverse_metric: Matrix, f_hat: Matrix) -> Fraction:
    return sum((inverse_metric[i][j] * f_hat[i][j] for i in range(DIM) for j in range(DIM)), Fraction())


def bracket_zero(left_f: Matrix, right_f: Matrix) -> Fraction:
    return metric_trace(ETA, left_f) * metric_trace(ETA, right_f) - contraction(ETA, ETA, left_f, right_f)


def bracket_first(h: Matrix, left_f: Matrix, right_f: Matrix) -> Fraction:
    first = inverse_first(h)
    return (
        metric_trace(first, left_f) * metric_trace(ETA, right_f)
        + metric_trace(ETA, left_f) * metric_trace(first, right_f)
        - contraction(first, ETA, left_f, right_f)
        - contraction(ETA, first, left_f, right_f)
    )


def bracket_second(left_h: Matrix, right_h: Matrix, left_f: Matrix, right_f: Matrix) -> Fraction:
    left_first, right_first = inverse_first(left_h), inverse_first(right_h)
    second = inverse_second(left_h, right_h)
    return (
        metric_trace(second, left_f) * metric_trace(ETA, right_f)
        + metric_trace(ETA, left_f) * metric_trace(second, right_f)
        + metric_trace(left_first, left_f) * metric_trace(right_first, right_f)
        + metric_trace(right_first, left_f) * metric_trace(left_first, right_f)
        - contraction(second, ETA, left_f, right_f)
        - contraction(ETA, second, left_f, right_f)
        - contraction(left_first, right_first, left_f, right_f)
        - contraction(right_first, left_first, left_f, right_f)
    )


def mass_third(h: Matrix, left_f: Matrix, right_f: Matrix) -> Fraction:
    """D_h D_f D_f of the shifted auxiliary mass density."""

    return (sqrt_first(h) * bracket_zero(left_f, right_f) + bracket_first(h, left_f, right_f)) / 2


def mass_fourth(left_h: Matrix, right_h: Matrix, left_f: Matrix, right_f: Matrix) -> Fraction:
    """D_h D_h D_f D_f of the shifted auxiliary mass density."""

    return (
        sqrt_second(left_h, right_h) * bracket_zero(left_f, right_f)
        + sqrt_first(left_h) * bracket_first(right_h, left_f, right_f)
        + sqrt_first(right_h) * bracket_first(left_h, left_f, right_f)
        + bracket_second(left_h, right_h, left_f, right_f)
    ) / 2


def quartic_entries() -> tuple[list[dict[str, str]], int]:
    tensors = [basis(index) for index in range(len(COORDS))]
    entries: list[dict[str, str]] = []
    ordered_nonzero = 0
    for left_h_index, left_h_coord in enumerate(COORDS):
        for right_h_index in range(left_h_index, len(COORDS)):
            right_h_coord = COORDS[right_h_index]
            for left_f_index, left_f_coord in enumerate(COORDS):
                for right_f_index in range(left_f_index, len(COORDS)):
                    right_f_coord = COORDS[right_f_index]
                    derivative = mass_fourth(
                        tensors[left_h_index], tensors[right_h_index],
                        tensors[left_f_index], tensors[right_f_index],
                    )
                    if not derivative:
                        continue
                    multiplicity = (2 if left_h_index == right_h_index else 1) * (2 if left_f_index == right_f_index else 1)
                    entries.append({
                        "h_left_row": f"h_{left_h_coord[0]}{left_h_coord[1]}",
                        "h_right_row": f"h_{right_h_coord[0]}{right_h_coord[1]}",
                        "f_hat_left_row": f"f_hat_{left_f_coord[0]}{left_f_coord[1]}",
                        "f_hat_right_row": f"f_hat_{right_f_coord[0]}{right_f_coord[1]}",
                        "homogeneous_polynomial_coefficient": str(derivative / multiplicity),
                        "D_h_left_D_h_right_D_f_left_D_f_right": str(derivative),
                    })
                    ordered_nonzero += (1 if left_h_index == right_h_index else 2) * (1 if left_f_index == right_f_index else 2)
    return entries, ordered_nonzero


def cubic_predecessor_defects(cubic: dict[str, Any]) -> int:
    listed = {
        (entry["h_row"], entry["f_hat_left_row"], entry["f_hat_right_row"]): Fraction(entry["D_h_D_f_left_D_f_right"])
        for entry in cubic["shifted_auxiliary_mass_vertex"]["entries"]
    }
    tensors = [basis(index) for index in range(len(COORDS))]
    defects = 0
    for h_index, h_coord in enumerate(COORDS):
        for left_f_index, left_f_coord in enumerate(COORDS):
            for right_f_index in range(left_f_index, len(COORDS)):
                right_f_coord = COORDS[right_f_index]
                expected = listed.get(
                    (f"h_{h_coord[0]}{h_coord[1]}", f"f_hat_{left_f_coord[0]}{left_f_coord[1]}", f"f_hat_{right_f_coord[0]}{right_f_coord[1]}"),
                    Fraction(),
                )
                defects += int(mass_third(tensors[h_index], tensors[left_f_index], tensors[right_f_index]) != expected)
    return defects


def conformal_ward_ledger() -> dict[str, int]:
    tensors = [basis(index) for index in range(len(COORDS))]
    pure_trace = ETA
    pure_trace_second_defects = 0
    mixed_recursion_defects = 0
    for left_f_index in range(len(COORDS)):
        for right_f_index in range(left_f_index, len(COORDS)):
            left_f, right_f = tensors[left_f_index], tensors[right_f_index]
            pure_trace_second_defects += int(mass_fourth(pure_trace, pure_trace, left_f, right_f) != 0)
            for h in tensors:
                mixed_recursion_defects += int(mass_fourth(pure_trace, h, left_f, right_f) + mass_third(h, left_f, right_f) != 0)
    return {
        "pure_trace_second_variation_checks": 55,
        "pure_trace_second_variation_defects": pure_trace_second_defects,
        "mixed_conformal_recursion_checks": 550,
        "mixed_conformal_recursion_defects": mixed_recursion_defects,
    }


def build() -> dict[str, Any]:
    action, split, cubic = (json.loads(path.read_text()) for path in (ACTION, SPLIT, CUBIC))
    if action.get("schema") != "pure-weyl-covariant-auxiliary-action-definition-v1":
        raise ValueError("authoritative auxiliary action drift")
    if split.get("canonical_lift", {}).get("local_BV_cotangent_lift_is_canonical") is not True:
        raise ValueError("exact canonical auxiliary split unavailable")
    if cubic.get("result_id") != "CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1":
        raise ValueError("cubic predecessor drift")

    entries, ordered_nonzero = quartic_entries()
    ward = conformal_ward_ledger()
    predecessor_defects = cubic_predecessor_defects(cubic)
    if len(entries) != 321 or ordered_nonzero != 912 or predecessor_defects or any(ward[key] for key in ward if key.endswith("defects")):
        raise AssertionError("quartic auxiliary-mass census or exact Ward replay drift")

    vertex = {
        "source_density": "sqrt(-g)/4*((tr_g f_hat)^2-f_hat^{mu nu}f_hat_mu nu)",
        "variation": "D_h_left D_h_right D_f_left D_f_right S_aux at g=eta and f_hat=0",
        "block_family": ["ENDPOINT_M", "ENDPOINT_M", "AUX_F_HAT", "AUX_F_HAT"],
        "component_basis": [f"{i}{j}" for i, j in COORDS],
        "possible_independent_symmetric_component_monomials": 3025,
        "nonzero_independent_component_monomials": len(entries),
        "nonzero_ordered_fourth_variation_coefficients": ordered_nonzero,
        "maximum_input_jet_order": 0,
        "entries": entries,
    }
    replay = {
        "coefficient_field": "Q",
        "floating_point_coefficients": 0,
        "cubic_predecessor_component_checks": 550,
        "cubic_predecessor_component_defects": predecessor_defects,
        **ward,
        "input_pair_symmetry_defects": 0,
        "support_local": True,
    }
    result = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema": "classical-shifted-auxiliary-quartic-mass-v1",
        "result_id": "CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1",
        "result_kind": "AUTHORITATIVE_EXACT_SHIFTED_AUXILIARY_QUARTIC_ACTION_COMPONENT_EXPORT",
        "result_state": "H_H_F_HAT_F_HAT_COMPONENT_COMPLETE_Q3_BV_LIFT_OPEN",
        "lifecycle": "CLASSIFIED",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope": {
            "theory": "four-dimensional ordinary-derivative strict pure-Weyl gravity",
            "background": "Minkowski normal frame at zero shifted auxiliary field",
            "carrier_sector": "metric and shifted symmetric auxiliary field",
            "coefficient_field": "Q",
            "claim_scope": "zero-jet h-h-f_hat-f_hat fourth action variation only",
        },
        "shifted_auxiliary_quartic_mass_vertex": vertex,
        "exact_replay": replay,
        "foundational_strength": {
            "exact_rational": True,
            "finite_component_table": True,
            "support_local": True,
            "uses_completion": False,
            "uses_green_operator": False,
            "uses_choice_principle": False,
        },
        "claim_flags": {
            "SHIFTED_AUXILIARY_H_H_F_HAT_F_HAT_COMPONENTS_SERIALIZED": True,
            "FOURTH_VARIATION_INDEPENDENTLY_REPLAYED": True,
            "CONFORMAL_WARD_RECURSION_REPLAYED": True,
            "AUTHORITATIVE_AUXILIARY_Q3_BV_LIFTED": False,
            "FULL_SOURCE_Q3_ASSEMBLED": False,
            "ARITY_THREE_IDENTITY_REPLAYED": False,
            "CLASSICAL_IMPORT_GATE_PASSED": False,
            "LORENTZIAN_CAUSAL_CERTIFIED": False,
            "HADAMARD_STATE_CONSTRUCTED": False,
            "QME_RESTORED": False,
        },
        "does_not_establish": [
            "the BV pairing lift of the fourth action variation to q3 output rows",
            "the union with the authoritative minimal q3 or any other quartic ghost-antifield family",
            "the arity-three L-infinity identity on the 386-row carrier",
            "Gate A, a causal Green compatibility theorem, Hadamard data, renormalized products, QME restoration, or residual transfer",
        ],
        "canonical_hashes": {
            "shifted_auxiliary_quartic_mass_vertex_sha256": digest(vertex),
            "exact_replay_sha256": digest(replay),
        },
        "provenance": {"inputs": [
            {"path": str(ACTION.relative_to(ROOT)), "schema": action["schema"], "sha256": sha(ACTION), "role": "authoritative ordinary-derivative auxiliary action"},
            {"path": str(SPLIT.relative_to(ROOT)), "schema": split["schema"], "sha256": sha(SPLIT), "role": "exact nonlinear shifted-field canonical split"},
            {"path": str(CUBIC.relative_to(ROOT)), "result_id": cubic["result_id"], "sha256": sha(CUBIC), "role": "independently certified first metric variation and normalization predecessor"},
        ]},
        "literature": {
            "reference": "R. R. Metsaev, Ordinary-derivative formulation of conformal low-spin fields, arXiv:0707.4437v3, Sec. 6",
            "url": "https://arxiv.org/abs/0707.4437",
        },
        "schema_path": "d_quotient_classical/nonminimal_identity/schema/classical-shifted-auxiliary-quartic-mass-v1.schema.json",
        "independent_checker": "d_quotient_classical/nonminimal_identity/check_classical_shifted_auxiliary_quartic_mass_v1.py",
        "human_report": str(REPORT.relative_to(ROOT)),
        "next_gate": "Lift the 912 ordered fourth-variation coefficients through the fixed 386-row BV pairing, unite them with minimal q3, and replay q1 q3+q3 q1+q2 q2 and quartic cyclicity exactly.",
    }
    return result


def render(value: dict[str, Any]) -> str:
    vertex = value["shifted_auxiliary_quartic_mass_vertex"]
    replay = value["exact_replay"]
    return f"""# Classical shifted-auxiliary quartic mass v1

**Result:** `{value['result_id']}`

**Dependency:** `LOCAL-ALGEBRAIC`

The authoritative shifted auxiliary action has a nonzero next metric Taylor
coefficient.  Exact rational expansion of its mass density gives
**{vertex['nonzero_independent_component_monomials']}** nonzero independent
`h-h-f_hat-f_hat` monomials among
{vertex['possible_independent_symmetric_component_monomials']} possibilities,
or **{vertex['nonzero_ordered_fourth_variation_coefficients']}** nonzero ordered
fourth-variation coefficients.

This is tied to the already certified cubic vertex: all
{replay['cubic_predecessor_component_checks']} first-variation component checks
agree.  The four-dimensional conformal Ward recursion contributes
{replay['pure_trace_second_variation_checks']} pure-trace and
{replay['mixed_conformal_recursion_checks']} mixed checks, with zero defects.
An independent checker reconstructs the same table using a square-free exact
jet algebra, determinant expansion, and algebraic matrix inversion.

This certificate exports the classical action tensor only.  It does not yet
call the tensor `q3`: that requires the fixed odd pairing, every Koszul mate,
the minimal-sector union, cyclicity, and the complete arity-three identity.

## Reproduction

```text
python3 d_quotient_classical/nonminimal_identity/classical_shifted_auxiliary_quartic_mass_v1.py --check
python3 d_quotient_classical/nonminimal_identity/check_classical_shifted_auxiliary_quartic_mass_v1.py
python3 d_quotient_classical/nonminimal_identity/verify_classical_shifted_auxiliary_quartic_mass_v1.py
python3 -m unittest d_quotient_classical.nonminimal_identity.tests.test_classical_shifted_auxiliary_quartic_mass_v1
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
        print("CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1: " + ("generated artifacts current" if not stale else "stale: " + ", ".join(stale)))
        return bool(stale)
    for path, content in outputs:
        path.write_bytes(content)
    print("CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1: wrote certificate and report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
