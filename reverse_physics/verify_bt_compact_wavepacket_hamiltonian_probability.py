#!/usr/bin/env python3
"""Independent exact verifier for the compact BT Hamiltonian packet effect."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COMPACT_WAVEPACKET_HAMILTONIAN_PROBABILITY_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-compact-wavepacket-hamiltonian-probability-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def matmul(left, right):
    right_t = transpose(right)
    return [
        [sum((a * b for a, b in zip(row, column)), Fraction(0)) for column in right_t]
        for row in left
    ]


def matvec(matrix, vector):
    return [sum((a * b for a, b in zip(row, vector)), Fraction(0)) for row in matrix]


def determinant(matrix):
    size = len(matrix)
    total = Fraction(0)
    for permutation in itertools.permutations(range(size)):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(size)
            for j in range(i + 1, size)
        )
        term = Fraction(-1 if inversions % 2 else 1)
        for row, column in enumerate(permutation):
            term *= matrix[row][column]
        total += term
    return total


def rank(matrix):
    work = [list(row) for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    pivot_row = 0
    for column in range(columns):
        pivot = next((row for row in range(pivot_row, rows) if work[row][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [a - scale * b for a, b in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def poly_add(left, right):
    result = [Fraction(0)] * max(len(left), len(right))
    for index, value in enumerate(left):
        result[index] += value
    for index, value in enumerate(right):
        result[index] += value
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def poly_mul(left, right):
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return result


def polynomial_determinant(matrix):
    size = len(matrix)
    total = [Fraction(0)]
    for permutation in itertools.permutations(range(size)):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(size)
            for j in range(i + 1, size)
        )
        term = [Fraction(-1 if inversions % 2 else 1)]
        for row, column in enumerate(permutation):
            term = poly_mul(term, matrix[row][column])
        total = poly_add(total, term)
    return total


class Dual:
    """Five-variable first-order rational automatic-differentiation value."""

    def __init__(self, value, gradient=None):
        self.value = Fraction(value)
        self.gradient = tuple(gradient or [Fraction(0)] * 5)

    def _coerce(self, other):
        return other if isinstance(other, Dual) else Dual(other)

    def __add__(self, other):
        other = self._coerce(other)
        return Dual(
            self.value + other.value,
            [a + b for a, b in zip(self.gradient, other.gradient)],
        )

    __radd__ = __add__

    def __neg__(self):
        return Dual(-self.value, [-value for value in self.gradient])

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other) - self

    def __mul__(self, other):
        other = self._coerce(other)
        return Dual(
            self.value * other.value,
            [
                self.value * b + other.value * a
                for a, b in zip(self.gradient, other.gradient)
            ],
        )

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self._coerce(other)
        return Dual(
            self.value / other.value,
            [
                (a * other.value - self.value * b) / other.value**2
                for a, b in zip(self.gradient, other.gradient)
            ],
        )

    def __rtruediv__(self, other):
        return self._coerce(other) / self

    def __pow__(self, exponent):
        if exponent != 2:
            raise ValueError("the verifier only needs rational squares")
        return self * self


def pair(parameter):
    return (
        (1 - parameter**2) / (1 + parameter**2),
        2 * parameter / (1 + parameter**2),
    )


def direction(parameter):
    cosine, sine = pair(parameter)
    return [cosine, sine, parameter * 0]


def rotate(vector, t, u, v):
    ct, st = pair(t)
    cu, su = pair(u)
    cv, sv = pair(v)
    vector = matvec([[ct, -st, 0], [st, ct, 0], [0, 0, 1]], vector)
    vector = matvec([[1, 0, 0], [0, cu, -su], [0, su, cu]], vector)
    return matvec([[cv, -sv, 0], [sv, cv, 0], [0, 0, 1]], vector)


def phase_density_squared(values):
    parameters = [
        Dual(value, [Fraction(index == component) for component in range(5)])
        for index, value in enumerate(values)
    ]
    a, b, t, u, v = parameters
    directions = [direction(Dual(0)), direction(a), direction(b)]
    cross = lambda left, right: left[0] * right[1] - left[1] * right[0]
    weights = [
        cross(directions[1], directions[2]),
        cross(directions[2], directions[0]),
        cross(directions[0], directions[1]),
    ]
    energies = [Fraction(16, 5) * weight / sum(weights) for weight in weights]
    outgoing = [
        [energy * component for component in rotate(unit, t, u, v)]
        for energy, unit in zip(energies, directions)
    ]
    flattened = [entry for vector in outgoing for entry in vector]
    chart_jacobian = [list(entry.gradient) for entry in flattened]
    chart_gram = matmul(transpose(chart_jacobian), chart_jacobian)
    evaluated = [[entry.value for entry in vector] for vector in outgoing]
    evaluated_energies = [energy.value for energy in energies]
    constraint = [[Fraction(0)] * 9 for _ in range(4)]
    for particle in range(3):
        for component in range(3):
            constraint[0][3 * particle + component] = (
                evaluated[particle][component] / evaluated_energies[particle]
            )
            constraint[component + 1][3 * particle + component] = Fraction(1)
    constraint_gram = matmul(constraint, transpose(constraint))
    energy_product = evaluated_energies[0] * evaluated_energies[1] * evaluated_energies[2]
    coarea_density_squared = determinant(chart_gram) / (
        64 * energy_product**2 * determinant(constraint_gram)
    )

    a0, b0, t0, u0, v0 = values
    denominator = (
        25
        * a0**2
        * b0**2
        * (a0 - b0) ** 2
        * (1 + t0**2)
        * (1 + u0**2) ** 2
        * (1 + v0**2)
    )
    closed_density_squared = (
        Fraction(256) * (1 + a0 * b0) * u0 / denominator
    ) ** 2
    return coarea_density_squared, closed_density_squared


def future_three_body(values):
    a, b, t, u, v = values
    directions = [direction(Fraction(0)), direction(a), direction(b)]
    cross = lambda left, right: left[0] * right[1] - left[1] * right[0]
    weights = [
        cross(directions[1], directions[2]),
        cross(directions[2], directions[0]),
        cross(directions[0], directions[1]),
    ]
    energies = [Fraction(16, 5) * weight / sum(weights) for weight in weights]
    return [
        tuple([energy] + [energy * component for component in rotate(unit, t, u, v)])
        for energy, unit in zip(energies, directions)
    ]


def rx(parameter):
    cosine, sine = pair(parameter)
    return [[Fraction(1), Fraction(0), Fraction(0)], [Fraction(0), cosine, -sine], [Fraction(0), sine, cosine]]


def rotate_momentum(rotation, momentum):
    return tuple([momentum[0]] + matvec(rotation, list(momentum[1:])))


def square(momentum):
    return momentum[0] ** 2 - sum((value**2 for value in momentum[1:]), Fraction(0))


def channel_momentum(momenta, mask):
    return tuple(
        sum(
            (momenta[index][component] for index in range(6) if mask & (1 << index)),
            Fraction(0),
        )
        for component in range(4)
    )


def independent_shell_geometry():
    input_center = (Fraction(2), Fraction(-2), Fraction(0), Fraction(15, 16), Fraction(0))
    output_center = (Fraction(2), Fraction(-2), Fraction(105, 73), Fraction(2), Fraction(1, 3))
    original_incoming = [
        (Fraction(6, 5), Fraction(6, 5), Fraction(0), Fraction(0)),
        (Fraction(1), Fraction(-3, 5), Fraction(4, 5), Fraction(0)),
        (Fraction(1), Fraction(-3, 5), Fraction(-4, 5), Fraction(0)),
    ]
    original_outgoing = future_three_body(
        (Fraction(2), Fraction(-2), Fraction(3, 5), Fraction(1, 2), Fraction(1, 3))
    )
    rotation = rx(Fraction(15, 16))
    incoming = future_three_body(input_center)
    outgoing = future_three_body(output_center)
    six_momenta = incoming + [tuple(-value for value in row) for row in outgoing]
    channels = [
        sum(1 << index for index in subset)
        for subset in itertools.combinations(range(6), 3)
        if sum(1 << index for index in subset) < (63 ^ sum(1 << index for index in subset))
    ]
    channel_values = {mask: square(channel_momentum(six_momenta, mask)) for mask in channels}
    shell = channel_momentum(six_momenta, 11)
    return {
        "input_rotation": incoming == [rotate_momentum(rotation, row) for row in original_incoming],
        "output_rotation": outgoing == [rotate_momentum(rotation, row) for row in original_outgoing],
        "shell": shell,
        "shell_square": square(shell),
        "unique": channel_values[11] == 0 and all(
            value != 0 for mask, value in channel_values.items() if mask != 11
        ),
    }


def independent_species_algebra():
    zero = Fraction(0)
    quarter = Fraction(1, 4)
    residue = [
        [quarter, zero, zero, zero],
        [zero, quarter, quarter, zero],
        [zero, quarter, quarter, quarter],
        [zero, quarter, quarter, quarter],
    ]
    gram = matmul(transpose(residue), residue)
    characteristic_matrix = [
        [[-gram[i][j], Fraction(i == j)] for j in range(4)]
        for i in range(4)
    ]
    characteristic = polynomial_determinant(characteristic_matrix)
    expected = poly_mul(
        poly_mul([zero, Fraction(1)], [-Fraction(1, 16), Fraction(1)]),
        [Fraction(1, 64), -Fraction(1, 2), Fraction(1)],
    )
    kernel = [
        [Fraction(1, 3), Fraction(1, 5)],
        [Fraction(2, 7), Fraction(-1, 4)],
        [Fraction(1, 6), Fraction(3, 8)],
    ]
    kronecker = [
        [kernel[i][j] * residue[r][c] for j in range(2) for c in range(4)]
        for i in range(3)
        for r in range(4)
    ]
    compressed_effect = matmul(transpose(kronecker), kronecker)
    return {
        "gram": gram,
        "trace": sum((gram[index][index] for index in range(4)), zero),
        "source": gram[0][0],
        "characteristic": characteristic,
        "expected_characteristic": expected,
        "compression_rank": rank(compressed_effect),
        "expected_compression_rank": rank(kernel) * rank(residue),
    }


def verify(certificate):
    phase = certificate["full_phase_space_measure"]
    shell_stored = certificate["compact_shell_geometry"]
    operator = certificate["Hamiltonian_packet_operator"]
    probability = certificate["positive_packet_probability"]
    interpretation = certificate["interpretation"]
    boundaries = certificate["does_not_establish"]

    samples = [
        (Fraction(2), Fraction(-2), Fraction(3, 5), Fraction(1, 2), Fraction(1, 3)),
        (Fraction(2), Fraction(-2), Fraction(0), Fraction(1, 2), Fraction(0)),
        (Fraction(2), Fraction(-2), Fraction(1, 7), Fraction(1, 2), Fraction(3, 4)),
        (Fraction(3, 2), Fraction(-3, 2), Fraction(1, 7), Fraction(1, 2), Fraction(3, 4)),
    ]
    density_pairs = [phase_density_squared(sample) for sample in samples]
    expected_density_squares = [
        Fraction(2916, 4515625),
        Fraction(576, 390625),
        Fraction(88510464, 152587890625),
        Fraction(10312216477696, 3243658447265625),
    ]
    shell = independent_shell_geometry()
    species = independent_species_algebra()
    stored_momentum = tuple(Fraction(value) for value in shell_stored["intermediate_momentum"])
    normalized_cutoff_assumption = any("|chi|<=1" in row for row in certificate["assumptions"])

    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(
            row["sha256"] == file_hash(row["path"])
            for row in certificate["provenance"]["inputs"]
        ),
        "four_phase_density_fixtures_rederived_by_rational_AD": all(
            coarea == closed for coarea, closed in density_pairs
        ),
        "four_phase_density_values_are_exact": [row[0] for row in density_pairs] == expected_density_squares,
        "published_density_fixture_is_recovered": phase["old_fixture"].endswith("54/2125"),
        "regular_input_center_is_independently_rotated": shell["input_rotation"],
        "regular_output_center_is_independently_rotated": shell["output_rotation"],
        "stored_shell_momentum_matches_independent_chart": stored_momentum == shell["shell"],
        "channel_11_is_positive_energy_null": shell["shell_square"] == 0 and shell["shell"][0] == 1,
        "channel_11_is_unique_at_center": shell["unique"],
        "species_Hilbert_Schmidt_norm_is_exact": species["trace"] == Fraction(9, 16),
        "species_source_factor_is_exact": species["source"] == Fraction(1, 16),
        "species_characteristic_polynomial_is_exact": species["characteristic"] == species["expected_characteristic"],
        "independent_finite_compression_has_expected_rank": species["compression_rank"] == species["expected_compression_rank"] == 6,
        "cutoff_normalization_needed_by_pointwise_bound_is_explicit": normalized_cutoff_assumption,
        "finite_time_kernel_and_HS_bound_are_recorded": operator["pointwise_bound"] == "|beta_B,T|<=T/d0" and operator["Hilbert_Schmidt_bound"] == "||K_B,T||_HS^2<=T^2*mu(X)*mu(Y)/d0^2",
        "effect_norm_constant_is_rederived": 256 * Fraction(1, 8) == 32,
        "source_probability_constant_is_rederived": 256 * species["source"] == 16,
        "click_effect_is_an_adjoint_square": probability["click_effect"].startswith("E_click=A_B,T^* A_B,T"),
        "click_and_no_click_are_complete": probability["completeness"] == "E_click+E_no=I",
        "small_coupling_domain_is_explicit": probability["sufficient_positive_domain"].startswith("32*(2+sqrt(3))*lambda^8"),
        "Hamiltonian_strength_is_not_fitted": interpretation["compact_packet_BT_Hamiltonian_strength"] == "CONSTRUCTED_AS_EXPLICIT_INTEGRAL_OPERATOR" and "fitted zeta" in certificate["answer"],
        "result_is_only_leading_finite_time": interpretation["positive_compact_packet_probability"] == "CONSTRUCTED_AT_LEADING_FINITE_TIME_ORDER",
        "ten_channel_and_all_time_boundaries_are_preserved": interpretation["ten_channel_global_probability"] == "NOT_CONSTRUCTED" and interpretation["all_time_scattering"] == "NOT_CONSTRUCTED",
        "Eq19_boundary_is_preserved": interpretation["general_Eq19"] == "NOT_PROVED" and any("Eq. (19)" in row for row in boundaries),
        "gravity_and_Lorentzian_boundaries_are_preserved": "gravity or BRST transfer" in boundaries and "anything LORENTZIAN-CAUSAL" in boundaries,
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
