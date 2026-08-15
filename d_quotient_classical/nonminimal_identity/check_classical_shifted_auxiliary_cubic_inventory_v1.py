#!/usr/bin/env python3
"""Independent exact checker for the shifted-auxiliary cubic inventory."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
ACTION = ROOT / "covariant_completion/certificates/curved_auxiliary_action_definition.json"
SPLIT = ROOT / "covariant_completion/certificates/curved_auxiliary_canonical_split.json"
QUADRATIC = ROOT / "d_quotient_classical/certificates/CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1.json"
COORDS = tuple((i, j) for i in range(4) for j in range(i, 4))
SIGNS = (-1, 1, 1, 1)


@dataclass(frozen=True)
class Dual:
    constant: Fraction
    linear: Fraction = Fraction(0)

    def __add__(self, other: "Dual | Fraction | int") -> "Dual":
        other = other if isinstance(other, Dual) else Dual(Fraction(other))
        return Dual(self.constant + other.constant, self.linear + other.linear)

    __radd__ = __add__

    def __neg__(self) -> "Dual":
        return Dual(-self.constant, -self.linear)

    def __sub__(self, other: "Dual | Fraction | int") -> "Dual":
        return self + (-other if isinstance(other, Dual) else -Fraction(other))

    def __rsub__(self, other: "Dual | Fraction | int") -> "Dual":
        return (-self) + other

    def __mul__(self, other: "Dual | Fraction | int") -> "Dual":
        other = other if isinstance(other, Dual) else Dual(Fraction(other))
        return Dual(self.constant * other.constant, self.constant * other.linear + self.linear * other.constant)

    __rmul__ = __mul__


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def basis(index: int) -> list[list[Fraction]]:
    out = [[Fraction(0) for _ in range(4)] for _ in range(4)]
    i, j = COORDS[index]
    out[i][j] = out[j][i] = Fraction(1)
    return out


def add_matrix(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[left[i][j] + right[i][j] for j in range(4)] for i in range(4)]


def density_linear(h: list[list[Fraction]], f: list[list[Fraction]]) -> Fraction:
    # Independent first-order dual-number expansion of the exact density.
    inverse = [[Dual(Fraction(SIGNS[i]) if i == j else Fraction(0), -Fraction(SIGNS[i] * SIGNS[j]) * h[i][j]) for j in range(4)] for i in range(4)]
    trace_h = sum((Fraction(SIGNS[i]) * h[i][i] for i in range(4)), Fraction(0))
    sqrt_det = Dual(Fraction(1), trace_h / 2)
    trace_f = sum((inverse[i][j] * f[i][j] for i in range(4) for j in range(4)), Dual(Fraction(0)))
    f_squared = sum((inverse[mu][alpha] * inverse[nu][beta] * f[alpha][beta] * f[mu][nu] for mu in range(4) for alpha in range(4) for nu in range(4) for beta in range(4)), Dual(Fraction(0)))
    return (sqrt_det * Fraction(1, 4) * (trace_f * trace_f - f_squared)).linear


def expected_mass_entries() -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for hi, hc in enumerate(COORDS):
        h = basis(hi)
        for fi, fc in enumerate(COORDS):
            f = basis(fi)
            diagonal = density_linear(h, f)
            for gi in range(fi, len(COORDS)):
                gc = COORDS[gi]
                coefficient = diagonal if gi == fi else density_linear(h, add_matrix(f, basis(gi))) - diagonal - density_linear(h, basis(gi))
                if coefficient:
                    out.append({"h_row": f"h_{hc[0]}{hc[1]}", "f_hat_left_row": f"f_hat_{fc[0]}{fc[1]}", "f_hat_right_row": f"f_hat_{gc[0]}{gc[1]}", "homogeneous_polynomial_coefficient": str(coefficient), "D_h_D_f_left_D_f_right": str(coefficient * (2 if fi == gi else 1))})
    return out


def expected_vv_entries() -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for mu, nu in COORDS:
        for a in range(4):
            for b in range(a, 4):
                coefficient = Fraction(int(mu == a and nu == b))
                if mu == nu and a == b:
                    coefficient -= Fraction(1, 2) * SIGNS[mu] * SIGNS[a]
                if coefficient:
                    out.append({"output_row": f"f_hat_{mu}{nu}", "v_left_row": f"v_{a}", "v_right_row": f"v_{b}", "homogeneous_polynomial_coefficient": str(coefficient), "second_Frechet_coefficient": str(coefficient * (2 if a == b else 1))})
    return out


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
    errors: list[str] = []
    if value.get("result_id") != "CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1" or value.get("lifecycle") != "CLASSIFIED" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("identity/lifecycle/dependency")
    if has_float(value):
        errors.append("floating-point data")
    mass = value.get("shifted_auxiliary_mass_vertex", {})
    vv = value.get("quadratic_vv_field_map", {})
    expected_mass, expected_vv = expected_mass_entries(), expected_vv_entries()
    if mass.get("entries") != expected_mass or mass.get("nonzero_component_monomials") != 72 or mass.get("pure_trace_h_defects") != 0:
        errors.append("shifted mass component table")
    if vv.get("entries") != expected_vv or vv.get("nonzero_homogeneous_component_coefficients") != 22:
        errors.append("vv field-map component table")
    families = value.get("required_cubic_family_inventory", [])
    if [row.get("family_id") for row in families] != ["SHIFTED_MASS_H_F_HAT_F_HAT", "TYPE_II_F_HAT_STAR_V_V", "TYPE_II_F_HAT_STAR_H_H", "TYPE_II_F_HAT_STAR_H_V", "DIFF_C_F_HAT_F_HAT_STAR", "DIFF_C_V_V_STAR", "DIFF_C_ETA_ETA_STAR"]:
        errors.append("required family inventory")
    complete = value.get("inventory_completeness", {})
    if complete.get("known_required_cubic_block_families_enumerated") != 7 or complete.get("exhaustive_full_nonlinear_BV_family_census") is not False or complete.get("full_component_coefficient_inventory") is not False:
        errors.append("inventory completeness boundary")
    comparison = value.get("candidate_comparison", {})
    if comparison.get("f_hat_v_v_mismatch_after_vv_pullback") != "CLOSED" or comparison.get("h_f_hat_f_hat_source_vertex_nonzero_coefficients") != 72 or comparison.get("h_f_hat_f_hat_candidate_vertex_nonzero_coefficients") != 0 or comparison.get("exact_auxiliary_shift_alone_identifies_source_with_trivial_stabilization") is not False or comparison.get("full_nonlinear_equivalence_obstructed") is not False:
        errors.append("candidate comparison")
    hashes = value.get("canonical_hashes", {})
    for key, payload in (("shifted_auxiliary_mass_vertex_sha256", mass), ("quadratic_vv_field_map_sha256", vv), ("required_cubic_family_inventory_sha256", families), ("candidate_comparison_sha256", comparison)):
        if hashes.get(key) != digest(payload):
            errors.append("canonical hash " + key)
    expected_inputs = ((ACTION, "pure-weyl-covariant-auxiliary-action-definition-v1"), (SPLIT, "pure-weyl-curved-auxiliary-canonical-split-v1"), (QUADRATIC, "CLASSICAL_QUADRATIC_AUXILIARY_ELIMINATION_MAP_V1"))
    provenance = value.get("provenance", {}).get("inputs", [])
    if len(provenance) != len(expected_inputs):
        errors.append("provenance count")
    else:
        for row, (path, result) in zip(provenance, expected_inputs):
            if row.get("path") != str(path.relative_to(ROOT)) or row.get("sha256") != sha(path) or row.get("schema", row.get("result_id")) != result:
                errors.append("provenance " + path.name)
    return errors


def main() -> int:
    errors = check()
    print("CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
