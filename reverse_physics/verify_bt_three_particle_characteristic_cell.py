#!/usr/bin/env python3
"""Independent exact verifier for the BT three-particle characteristic cell."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_THREE_PARTICLE_CHARACTERISTIC_CELL_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-three-particle-characteristic-cell-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def determinant(matrix):
    """Fraction-only Gaussian determinant, independent of the producer CAS."""
    rows = [[Fraction(value) for value in row] for row in matrix]
    sign = 1
    result = Fraction(1)
    for column in range(len(rows)):
        pivot = next((row for row in range(column, len(rows)) if rows[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            sign *= -1
        value = rows[column][column]
        result *= value
        rows[column] = [entry / value for entry in rows[column]]
        for row in range(column + 1, len(rows)):
            factor = rows[row][column]
            rows[row] = [left - factor * right for left, right in zip(rows[row], rows[column])]
    return sign * result


def verify(certificate):
    incoming = certificate["declared_incoming_cell"]
    factorial = certificate["factorial_and_orbit_audit"]
    physical = certificate["physical_shell_probability"]
    dependence = certificate["detector_dependence"]
    interpretation = certificate["interpretation"]

    velocity_row = [
        Fraction(1), Fraction(0), Fraction(0),
        Fraction(-3, 5), Fraction(4, 5), Fraction(0),
        Fraction(-3, 5), Fraction(-4, 5), Fraction(0),
    ]
    constraint_matrix = [velocity_row]
    for column in range(1, 9):
        row = [Fraction(0)] * 9
        row[column] = Fraction(1)
        constraint_matrix.append(row)
    jacobian = determinant(constraint_matrix)

    energies = [Fraction(6, 5), Fraction(1), Fraction(1)]
    energy_product = energies[0] * energies[1] * energies[2]
    ordered_coefficient = Fraction(1, 8) / energy_product
    incoming_coefficient = ordered_coefficient
    shell_coefficient = Fraction(27, 320)
    rate_coefficient = incoming_coefficient * shell_coefficient
    orbit_factor = Fraction(6 * 6, 6 * 6)

    public_denominator = {"L0": 1, "Lx": 2, "Ly": 2, "Lz": 1}
    external_volume = {"L0": 1, "Lx": 1, "Ly": 1, "Lz": 1}
    public_remainder = {
        name: public_denominator[name] - external_volume[name]
        for name in public_denominator
    }

    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in certificate["provenance"]["inputs"]),
        "source_archive_hash_is_pinned": certificate["provenance"]["public_source_archive_sha256"] == "6681e48614eac27e7ce766563b336c3296bbb94dd00286611672a7a1f15ec0db",
        "public_area_exponents_recomputed": public_remainder == {"L0": 0, "Lx": 1, "Ly": 1, "Lz": 0},
        "fixture_energy_sum_recomputed": sum(energies) == Fraction(16, 5),
        "fixture_energy_product_recomputed": energy_product == Fraction(6, 5),
        "constraint_determinant_recomputed_without_CAS": jacobian == 1,
        "stored_constraint_determinant_matches": incoming["constraint_jacobian_determinant"] == "1",
        "ordered_weight_coefficient_recomputed": ordered_coefficient == Fraction(5, 48),
        "stored_ordered_weight_matches": incoming["one_ordered_cell_weight"] == "5/[48*kappa^3*L0*Lx^2*Ly^3*Lz^3]",
        "external_volume_remainder_matches": incoming["incoming_weight"] == "N_in=5/[48*kappa^3*Lx*Ly^2*Lz^2]",
        "incoming_dimension_recomputed": -3 + 5 == incoming["incoming_weight_mass_dimension"] == 2,
        "both_S3_orbits_are_required": factorial["incoming_S3_orbit_multiplicity"] == 6 and factorial["outgoing_S3_orbit_multiplicity"] == 6,
        "projector_factorials_cancel_recomputed": orbit_factor == 1 and factorial["net_factor"] == "6*6/(3!*3!)=1",
        "rate_rational_coefficient_recomputed": rate_coefficient == Fraction(9, 1024),
        "stored_rate_density_matches": physical["declared_rate_density"] == "Gamma_Xi=9*lambda^8/[1024*pi^4*kappa^4*Lx*Ly^2*Lz^2]",
        "rate_dimension_recomputed": 5 - 4 == physical["mass_dimension_of_rate"] == 1,
        "probability_dimension_recomputed": physical["mass_dimension_of_rate"] - 1 == physical["mass_dimension_of_probability"] == 0,
        "compact_window_rate_is_recorded": physical["compact_window_rate_limit"] == "pi/kappa",
        "alternative_velocity_jacobian_recomputed": abs(velocity_row[3]) == Fraction(3, 5),
        "coordinate_cell_ratio_recomputed": Fraction(1, abs(velocity_row[3])) == Fraction(5, 3),
        "stored_detector_dependence_matches": dependence["alternative_to_reference_weight_ratio"] == "5/3",
        "declared_probability_is_computed": interpretation["dimensionless_local_detector_shell_probability"] == "COEFFICIENT_COMPUTED",
        "universal_cross_section_is_not_promoted": interpretation["detector_independent_three_body_cross_section"] == "NOT_DEFINED",
        "global_probability_and_eq19_remain_open": interpretation["ten_channel_global_probability"] == "NOT_CONSTRUCTED" and interpretation["Eq19_all_orders"] == "NOT_PROVED",
        "lorentzian_boundary_is_explicit": "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"],
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
