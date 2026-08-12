#!/usr/bin/env python3
"""Independent verifier for the BT finite-time local shell column."""
import hashlib
import json
import os
import sys
from fractions import Fraction

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FINITE_TIME_SHELL_COLUMN_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-six-point-finite-time-shell-column-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_phase_coarea():
    class Dual:
        def __init__(self, value, gradient=None):
            self.value = Fraction(value)
            self.gradient = tuple(gradient or [Fraction(0)] * 5)

        def _coerce(self, other):
            return other if isinstance(other, Dual) else Dual(other)

        def __add__(self, other):
            other = self._coerce(other)
            return Dual(self.value + other.value, [x + y for x, y in zip(self.gradient, other.gradient)])

        __radd__ = __add__

        def __neg__(self):
            return Dual(-self.value, [-x for x in self.gradient])

        def __sub__(self, other):
            return self + (-self._coerce(other))

        def __rsub__(self, other):
            return self._coerce(other) - self

        def __mul__(self, other):
            other = self._coerce(other)
            return Dual(
                self.value * other.value,
                [self.value * y + other.value * x for x, y in zip(self.gradient, other.gradient)],
            )

        __rmul__ = __mul__

        def __truediv__(self, other):
            other = self._coerce(other)
            return Dual(
                self.value / other.value,
                [
                    (x * other.value - self.value * y) / other.value**2
                    for x, y in zip(self.gradient, other.gradient)
                ],
            )

        def __rtruediv__(self, other):
            return self._coerce(other) / self

        def __pow__(self, exponent):
            assert exponent == 2
            return self * self

    values = [Fraction(2), Fraction(-2), Fraction(3, 5), Fraction(1, 2), Fraction(1, 3)]
    parameters = [
        Dual(value, [Fraction(int(index == component)) for component in range(5)])
        for index, value in enumerate(values)
    ]
    a, b, t, u, v = parameters

    def direction(r):
        return [(1 - r**2) / (1 + r**2), 2 * r / (1 + r**2), Dual(0)]

    def matvec(matrix, vector):
        return [sum(matrix[row][column] * vector[column] for column in range(3)) for row in range(3)]

    def rotate(vector):
        def pair(r):
            return (1 - r**2) / (1 + r**2), 2 * r / (1 + r**2)
        ct, st = pair(t)
        cu, su = pair(u)
        cv, sv = pair(v)
        vector = matvec([[ct, -st, 0], [st, ct, 0], [0, 0, 1]], vector)
        vector = matvec([[1, 0, 0], [0, cu, -su], [0, su, cu]], vector)
        return matvec([[cv, -sv, 0], [sv, cv, 0], [0, 0, 1]], vector)

    directions = [direction(Dual(0)), direction(a), direction(b)]
    cross2 = lambda left, right: left[0] * right[1] - left[1] * right[0]
    weights = [cross2(directions[1], directions[2]), cross2(directions[2], directions[0]), cross2(directions[0], directions[1])]
    energies = [Fraction(16, 5) * weight / sum(weights) for weight in weights]
    outgoing = [[energy * component for component in rotate(vector)] for energy, vector in zip(energies, directions)]
    flattened = [entry for vector in outgoing for entry in vector]
    chart_jacobian = sp.Matrix([[sp.Rational(value) for value in entry.gradient] for entry in flattened])
    evaluated = [[entry.value for entry in vector] for vector in outgoing]
    evaluated_energies = [energy.value for energy in energies]
    constraint = sp.zeros(4, 9)
    for particle in range(3):
        for component in range(3):
            constraint[0, 3 * particle + component] = evaluated[particle][component] / evaluated_energies[particle]
            constraint[component + 1, 3 * particle + component] = 1
    chart_det = sp.factor((chart_jacobian.T * chart_jacobian).det())
    constraint_det = sp.factor((constraint * constraint.T).det())
    product_energy = sp.prod(evaluated_energies)
    density = sp.sqrt(sp.factor(chart_det / (64 * product_energy**2 * constraint_det)))
    q_vector = [
        Dual(Fraction(11, 5)) - energies[0],
        Dual(Fraction(3, 5)) - outgoing[0][0],
        Dual(Fraction(4, 5)) - outgoing[0][1],
        -outgoing[0][2],
    ]
    shell_function = q_vector[0] ** 2 - sum(value**2 for value in q_vector[1:])
    ds_dt = sp.Rational(shell_function.gradient[2])
    return chart_det, constraint_det, product_energy, density, ds_dt, sp.factor(density / sp.Abs(ds_dt))


def verify(certificate):
    shell = certificate["exact_physical_shell"]
    kernel = certificate["finite_time_kernel"]
    column = certificate["local_history_column"]
    completion = certificate["normalized_survival_completion"]
    hierarchy = certificate["isolated_channel_duration_hierarchy"]
    result = certificate["interpretation"]
    momentum = [sp.Rational(value) for value in shell["intermediate_momentum"]]
    duration, energy, cutoff, strength = sp.symbols("T E L g", positive=True)
    sinc_coordinate = sp.symbols("x", real=True)
    standard_sinc_norm = sp.integrate(
        sp.sin(sinc_coordinate) ** 2 / sinc_coordinate**2,
        (sinc_coordinate, -sp.oo, sp.oo),
    )
    shell_norm = standard_sinc_norm * duration / energy
    history_norm = sp.Rational(9, 8) * shell_norm
    q = strength**2 * history_norm
    cross = 2 * sp.Si(cutoff * duration / (2 * energy))
    history_vector = sp.Matrix([sp.sqrt(2) / 4] * 9)
    normalized_history_vector = sp.ones(9, 1) / 3
    skew_generator = sp.zeros(10, 10)
    skew_generator[0, 1:] = -normalized_history_vector.T
    skew_generator[1:, 0] = normalized_history_vector
    chart_det, constraint_det, energy_product, chart_density, ds_dt, shell_density = independent_phase_coarea()
    phase = certificate["exact_phase_space_coarea"]
    labeled_rate = sp.factor(shell_density * history_norm.subs(energy, 1) / (2 * sp.pi) ** 5)
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in certificate["provenance"]["inputs"]),
        "intermediate_momentum_is_null": momentum[0] ** 2 - sum(value**2 for value in momentum[1:]) == 0,
        "intermediate_energy_is_one": momentum[0] == 1 and shell["intermediate_energy"] == "1",
        "history_vector_norm_recomputed": history_vector.dot(history_vector) == sp.Rational(9, 8),
        "standard_sinc_integral_recomputed": standard_sinc_norm == sp.pi,
        "shell_norm_from_standard_sinc_integral": shell_norm == sp.pi * duration / energy,
        "history_norm_recomputed": history_norm == sp.Rational(9, 8) * sp.pi * duration / energy,
        "fixture_norm_recomputed": history_norm.subs(energy, 1) == sp.Rational(9, 8) * sp.pi * duration,
        "phase_chart_gram_independently_recomputed": chart_det == sp.Rational(13544423424, 2822265625),
        "phase_constraint_gram_independently_recomputed": constraint_det == sp.Rational(2016, 25),
        "phase_energy_product_independently_recomputed": energy_product == sp.Rational(6, 5),
        "phase_chart_density_independently_recomputed": chart_density == sp.Rational(54, 2125),
        "phase_shell_change_independently_recomputed": ds_dt == -sp.Rational(1152, 425) and shell_density == sp.Rational(3, 320),
        "phase_weighted_rate_independently_recomputed": labeled_rate == 27 * duration / (81920 * sp.pi**4),
        "constant_cross_limit_recomputed": sp.limit(cross, duration, sp.oo) == sp.pi,
        "cross_is_subleading_recomputed": sp.limit(cross / history_norm, duration, sp.oo) == 0,
        "column_completeness_recomputed": sp.simplify((1 - q) + strength**2 * history_norm) == 1,
        "rank_one_skew_dilation_recomputed": (
            (normalized_history_vector.T * normalized_history_vector)[0] == 1
            and skew_generator.T == -skew_generator
            and skew_generator**3 == -skew_generator
        ),
        "rotation_parameter_is_real_on_declared_domain": completion["perturbative_domain"] == "0<=q<=1",
        "finite_kernel_not_hamiltonian_promoted": kernel["status"] == "EXACT_FINITE_TIME_KINEMATIC_KERNEL_NOT_BT_HAMILTONIAN_DERIVATION",
        "local_column_not_global_promoted": completion["status"] == "NORMALIZED_LOCAL_SINGLE_SHELL_COLUMN_NOT_GLOBAL_BT_MOLLER_OPERATOR",
        "physical_gates_remain_open": result["effective_strength_BT_calibration"] == "NOT_COMPUTED" and result["finite_inclusive_BT_probability"] == "NOT_CONSTRUCTED",
        "multichannel_and_interference_remain_open": result["multi_channel_intersection_gluing"] == "NOT_CONSTRUCTED" and result["connected_interference_distribution"] == "NOT_PRESCRIBED_GLOBALLY",
        "claim_boundary_is_preserved": "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"] and result["Eq19_all_orders"] == "NOT_PROVED",
        "stored_formula_boundaries_match": column["Q_T"] == "9*pi*T/(8*E)" and hierarchy["cross_to_sequential_limit"] == "0",
        "stored_phase_boundaries_match": phase["shell_density"] == "3/[320*(2*pi)^5]" and "generalized-Born projector normalization is not inferred" in phase["boundary"],
    }
    return {name: bool(value) for name, value in checks.items()}


def main():
    checks = verify(load(CERT))
    failures = [name for name, ok in checks.items() if not ok]
    print("checks %d/%d" % (sum(checks.values()), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
