#!/usr/bin/env python3
"""Independent exact jet-algebra replay of the quartic auxiliary mass."""

from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import permutations
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1.json"
ACTION = ROOT / "covariant_completion/certificates/curved_auxiliary_action_definition.json"
SPLIT = ROOT / "covariant_completion/certificates/curved_auxiliary_canonical_split.json"
CUBIC = ROOT / "d_quotient_classical/certificates/CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1.json"
COORDS = tuple((i, j) for i in range(4) for j in range(i, 4))
SIGNS = (-1, 1, 1, 1)


class Jet:
    """Four commuting square-free variables over Q.

    The coefficient of x*y*z*w is the mixed Frechet derivative.  Giving two
    equal tensor directions distinct variables also recovers repeated-input
    derivatives without numerical polarization.
    """

    __slots__ = ("coefficients",)

    def __init__(self, coefficients: tuple[Fraction, ...] | None = None):
        self.coefficients = coefficients or (Fraction(),) * 16

    @staticmethod
    def constant(value: Fraction | int) -> "Jet":
        coefficients = [Fraction()] * 16
        coefficients[0] = Fraction(value)
        return Jet(tuple(coefficients))

    @staticmethod
    def variable(index: int) -> "Jet":
        coefficients = [Fraction()] * 16
        coefficients[1 << index] = Fraction(1)
        return Jet(tuple(coefficients))

    def __add__(self, other: "Jet | Fraction | int") -> "Jet":
        other = other if isinstance(other, Jet) else Jet.constant(other)
        return Jet(tuple(left + right for left, right in zip(self.coefficients, other.coefficients)))

    __radd__ = __add__

    def __neg__(self) -> "Jet":
        return Jet(tuple(-value for value in self.coefficients))

    def __sub__(self, other: "Jet | Fraction | int") -> "Jet":
        return self + (-other if isinstance(other, Jet) else -Fraction(other))

    def __rsub__(self, other: "Jet | Fraction | int") -> "Jet":
        return (-self) + other

    def __mul__(self, other: "Jet | Fraction | int") -> "Jet":
        other = other if isinstance(other, Jet) else Jet.constant(other)
        values = [Fraction()] * 16
        for left_mask, left in enumerate(self.coefficients):
            if not left:
                continue
            for right_mask, right in enumerate(other.coefficients):
                if right and not left_mask & right_mask:
                    values[left_mask | right_mask] += left * right
        return Jet(tuple(values))

    __rmul__ = __mul__

    def inverse(self) -> "Jet":
        constant = self.coefficients[0]
        if not constant:
            raise ZeroDivisionError("jet has no invertible constant term")
        nilpotent = self * (Fraction(1) / constant) - 1
        total = Jet.constant(1)
        power = Jet.constant(1)
        for degree in range(1, 5):
            power = power * nilpotent
            total += power * (Fraction(-1) if degree % 2 else Fraction(1))
        return total * (Fraction(1) / constant)

    def square_root_unit(self) -> "Jet":
        if self.coefficients[0] != 1:
            raise ValueError("square-root rail expects unit constant term")
        nilpotent = self - 1
        total = Jet.constant(1)
        power = Jet.constant(1)
        coefficient = Fraction(1)
        for degree in range(1, 5):
            power = power * nilpotent
            coefficient *= (Fraction(1, 2) - (degree - 1)) / degree
            total += coefficient * power
        if total * total != self:
            raise AssertionError("exact jet square root failed")
        return total

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Jet):
            return self.coefficients == other.coefficients
        if isinstance(other, (int, Fraction)):
            return self == Jet.constant(other)
        return False


ZERO = Jet.constant(0)
ONE = Jet.constant(1)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def basis(index: int) -> list[list[Fraction]]:
    value = [[Fraction() for _ in range(4)] for _ in range(4)]
    i, j = COORDS[index]
    value[i][j] = value[j][i] = Fraction(1)
    return value


def permutation_sign(value: tuple[int, ...]) -> int:
    inversions = sum(int(value[i] > value[j]) for i in range(len(value)) for j in range(i + 1, len(value)))
    return -1 if inversions % 2 else 1


def determinant(matrix: list[list[Jet]]) -> Jet:
    return sum(
        (
            permutation_sign(order)
            * matrix[0][order[0]] * matrix[1][order[1]]
            * matrix[2][order[2]] * matrix[3][order[3]]
            for order in permutations(range(4))
        ),
        ZERO,
    )


def matrix_inverse(matrix: list[list[Jet]]) -> list[list[Jet]]:
    work = [row[:] + [ONE if i == j else ZERO for j in range(4)] for i, row in enumerate(matrix)]
    for column in range(4):
        pivot = next(row for row in range(column, 4) if work[row][column].coefficients[0])
        work[column], work[pivot] = work[pivot], work[column]
        pivot_inverse = work[column][column].inverse()
        work[column] = [entry * pivot_inverse for entry in work[column]]
        for row in range(4):
            if row == column:
                continue
            factor = work[row][column]
            if factor != ZERO:
                work[row] = [left - factor * right for left, right in zip(work[row], work[column])]
    result = [row[4:] for row in work]
    for i in range(4):
        for j in range(4):
            product = sum((matrix[i][k] * result[k][j] for k in range(4)), ZERO)
            if product != (ONE if i == j else ZERO):
                raise AssertionError("exact jet matrix inverse failed")
    return result


def metric_jet(left_h: list[list[Fraction]], right_h: list[list[Fraction]]) -> tuple[list[list[Jet]], Jet]:
    x, y = Jet.variable(0), Jet.variable(1)
    metric = [
        [Jet.constant(SIGNS[i] if i == j else 0) + x * left_h[i][j] + y * right_h[i][j] for j in range(4)]
        for i in range(4)
    ]
    minus_determinant = -determinant(metric)
    return matrix_inverse(metric), minus_determinant.square_root_unit()


def fourth_variation(metric_inverse: list[list[Jet]], sqrt_minus_g: Jet, left_f: list[list[Fraction]], right_f: list[list[Fraction]]) -> Fraction:
    z, w = Jet.variable(2), Jet.variable(3)
    f_hat = [[z * left_f[i][j] + w * right_f[i][j] for j in range(4)] for i in range(4)]
    trace_f = sum((metric_inverse[i][j] * f_hat[i][j] for i in range(4) for j in range(4)), ZERO)
    norm_f = sum(
        (
            metric_inverse[mu][alpha] * metric_inverse[nu][beta]
            * f_hat[alpha][beta] * f_hat[mu][nu]
            for mu in range(4) for alpha in range(4) for nu in range(4) for beta in range(4)
        ),
        ZERO,
    )
    density = sqrt_minus_g * Fraction(1, 4) * (trace_f * trace_f - norm_f)
    return density.coefficients[15]


def expected_entries() -> tuple[list[dict[str, str]], int, dict[tuple[int, int, int, int], Fraction]]:
    tensors = [basis(index) for index in range(10)]
    entries: list[dict[str, str]] = []
    ordered = 0
    derivatives: dict[tuple[int, int, int, int], Fraction] = {}
    for left_h_index in range(10):
        for right_h_index in range(left_h_index, 10):
            inverse, root = metric_jet(tensors[left_h_index], tensors[right_h_index])
            for left_f_index in range(10):
                for right_f_index in range(left_f_index, 10):
                    value = fourth_variation(inverse, root, tensors[left_f_index], tensors[right_f_index])
                    derivatives[(left_h_index, right_h_index, left_f_index, right_f_index)] = value
                    if not value:
                        continue
                    left_h, right_h = COORDS[left_h_index], COORDS[right_h_index]
                    left_f, right_f = COORDS[left_f_index], COORDS[right_f_index]
                    multiplicity = (2 if left_h_index == right_h_index else 1) * (2 if left_f_index == right_f_index else 1)
                    entries.append({
                        "h_left_row": f"h_{left_h[0]}{left_h[1]}",
                        "h_right_row": f"h_{right_h[0]}{right_h[1]}",
                        "f_hat_left_row": f"f_hat_{left_f[0]}{left_f[1]}",
                        "f_hat_right_row": f"f_hat_{right_f[0]}{right_f[1]}",
                        "homogeneous_polynomial_coefficient": str(value / multiplicity),
                        "D_h_left_D_h_right_D_f_left_D_f_right": str(value),
                    })
                    ordered += (1 if left_h_index == right_h_index else 2) * (1 if left_f_index == right_f_index else 2)
    return entries, ordered, derivatives


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
    if value.get("result_id") != "CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1" or value.get("lifecycle") != "CLASSIFIED" or value.get("dependency_tags") != ["LOCAL-ALGEBRAIC"]:
        errors.append("identity/lifecycle/dependency boundary")
    if has_float(value):
        errors.append("floating-point data")

    entries, ordered, derivatives = expected_entries()
    vertex = value.get("shifted_auxiliary_quartic_mass_vertex", {})
    if vertex.get("entries") != entries:
        errors.append("independent determinant/jet component replay")
    if vertex.get("nonzero_independent_component_monomials") != 321 or vertex.get("nonzero_ordered_fourth_variation_coefficients") != ordered or ordered != 912:
        errors.append("quartic component-count ledger")

    eta_coefficients = {0: -1, 4: 1, 7: 1, 9: 1}
    cubic = json.loads(CUBIC.read_text())
    cubic_table = {
        (entry["h_row"], entry["f_hat_left_row"], entry["f_hat_right_row"]): Fraction(entry["D_h_D_f_left_D_f_right"])
        for entry in cubic["shifted_auxiliary_mass_vertex"]["entries"]
    }
    pure_defects = mixed_defects = 0
    for left_f in range(10):
        for right_f in range(left_f, 10):
            pure = sum(
                (
                    Fraction(left_weight * right_weight)
                    * derivatives[(min(left_h, right_h), max(left_h, right_h), left_f, right_f)]
                    for left_h, left_weight in eta_coefficients.items()
                    for right_h, right_weight in eta_coefficients.items()
                ),
                Fraction(),
            )
            pure_defects += int(pure != 0)
            for h_index, h_coord in enumerate(COORDS):
                mixed = sum(
                    (
                        Fraction(weight) * derivatives[(min(eta_index, h_index), max(eta_index, h_index), left_f, right_f)]
                        for eta_index, weight in eta_coefficients.items()
                    ),
                    Fraction(),
                )
                left_coord, right_coord = COORDS[left_f], COORDS[right_f]
                cubic_value = cubic_table.get(
                    (f"h_{h_coord[0]}{h_coord[1]}", f"f_hat_{left_coord[0]}{left_coord[1]}", f"f_hat_{right_coord[0]}{right_coord[1]}"),
                    Fraction(),
                )
                mixed_defects += int(mixed + cubic_value != 0)
    replay = value.get("exact_replay", {})
    expected_replay = {
        "coefficient_field": "Q", "floating_point_coefficients": 0,
        "cubic_predecessor_component_checks": 550, "cubic_predecessor_component_defects": 0,
        "pure_trace_second_variation_checks": 55, "pure_trace_second_variation_defects": pure_defects,
        "mixed_conformal_recursion_checks": 550, "mixed_conformal_recursion_defects": mixed_defects,
        "input_pair_symmetry_defects": 0, "support_local": True,
    }
    if pure_defects or mixed_defects or replay != expected_replay:
        errors.append("conformal Ward/predecessor replay ledger")

    hashes = value.get("canonical_hashes", {})
    if hashes != {
        "shifted_auxiliary_quartic_mass_vertex_sha256": digest(vertex),
        "exact_replay_sha256": digest(replay),
    }:
        errors.append("canonical hashes")
    expected_inputs = ((ACTION, "pure-weyl-covariant-auxiliary-action-definition-v1"), (SPLIT, "pure-weyl-curved-auxiliary-canonical-split-v1"), (CUBIC, "CLASSICAL_SHIFTED_AUXILIARY_CUBIC_INVENTORY_V1"))
    provenance = value.get("provenance", {}).get("inputs", [])
    if len(provenance) != 3:
        errors.append("provenance count")
    else:
        for row, (path, identity) in zip(provenance, expected_inputs):
            if row.get("path") != str(path.relative_to(ROOT)) or row.get("sha256") != sha(path) or row.get("schema", row.get("result_id")) != identity:
                errors.append("provenance " + path.name)
    flags = value.get("claim_flags", {})
    for name in ("SHIFTED_AUXILIARY_H_H_F_HAT_F_HAT_COMPONENTS_SERIALIZED", "FOURTH_VARIATION_INDEPENDENTLY_REPLAYED", "CONFORMAL_WARD_RECURSION_REPLAYED"):
        if flags.get(name) is not True:
            errors.append("claim flag " + name)
    for name in ("AUTHORITATIVE_AUXILIARY_Q3_BV_LIFTED", "FULL_SOURCE_Q3_ASSEMBLED", "ARITY_THREE_IDENTITY_REPLAYED", "CLASSICAL_IMPORT_GATE_PASSED", "LORENTZIAN_CAUSAL_CERTIFIED", "HADAMARD_STATE_CONSTRUCTED", "QME_RESTORED"):
        if flags.get(name) is not False:
            errors.append("fail-closed flag " + name)
    return errors


def main() -> int:
    errors = check()
    print("CLASSICAL_SHIFTED_AUXILIARY_QUARTIC_MASS_V1_INDEPENDENT_JET_REPLAY: " + ("PASS" if not errors else "FAIL"))
    for error in errors:
        print("  - " + error)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
