#!/usr/bin/env python3
"""Independent exact checks for the compact dressed scalar wavepacket."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_COMPACT_WAVEPACKET_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-scalar-dressed-source-compact-wavepacket-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def poly_add(left, right):
    out = [Fraction(0)] * max(len(left), len(right))
    for j, value in enumerate(left):
        out[j] += value
    for j, value in enumerate(right):
        out[j] += value
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def poly_mul(left, right):
    out = [Fraction(0)] * (len(left) + len(right) - 1)
    for j, a in enumerate(left):
        for k, b in enumerate(right):
            out[j + k] += a * b
    return out


def parity(permutation):
    inversions = sum(permutation[i] > permutation[j] for i in range(len(permutation)) for j in range(i + 1, len(permutation)))
    return -1 if inversions % 2 else 1


def determinant_polynomial(matrix):
    size = len(matrix)
    result = [Fraction(0)]
    for permutation in itertools.permutations(range(size)):
        term = [Fraction(parity(permutation))]
        for row, column in enumerate(permutation):
            term = poly_mul(term, matrix[row][column])
        result = poly_add(result, term)
    return result


def verify(certificate):
    zero = Fraction(0)
    profiles = [[zero] * 12 for _ in range(3)]
    profiles[0][0:2] = [Fraction(3, 5), Fraction(4, 5)]
    profiles[1][2:4] = [Fraction(5, 13), Fraction(12, 13)]
    profiles[2][4:6] = [Fraction(8, 17), Fraction(15, 17)]
    gram = [[dot(left, right) for right in profiles] for left in profiles]
    reflected = [list(reversed(row)) for row in profiles]
    antipodal = [[dot(left, right) for right in reflected] for left in profiles]

    energies = [Fraction(j + 1) for j in range(12)]
    u_profiles = [[2 * energy * value for energy, value in zip(energies, row)] for row in profiles]
    o_profiles = [[value / (2 * energy) for energy, value in zip(energies, row)] for row in profiles]
    scalar_cross = [[dot(left, right) for right in o_profiles] for left in u_profiles]
    u_norms = [dot(row, row) for row in u_profiles]
    o_norms = [dot(row, row) + 4 for row in o_profiles]

    residue = [
        [Fraction(1, 4), zero, zero, zero],
        [zero, Fraction(1, 4), Fraction(1, 4), zero],
        [zero, Fraction(1, 4), Fraction(1, 4), Fraction(1, 4)],
        [zero, Fraction(1, 4), Fraction(1, 4), Fraction(1, 4)],
    ]
    effect = [[sum(residue[k][i] * residue[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
    characteristic_matrix = [
        [[-effect[i][j], Fraction(1) if i == j else Fraction(0)] for j in range(4)]
        for i in range(4)
    ]
    characteristic = determinant_polynomial(characteristic_matrix)
    expected = poly_mul(
        poly_mul([zero, Fraction(1)], [Fraction(-1, 16), Fraction(1)]),
        [Fraction(1, 64), Fraction(-1, 2), Fraction(1)],
    )

    interpretation = certificate["interpretation"]
    boundaries = certificate["does_not_establish"]
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in certificate["provenance"]["inputs"]),
        "three_rational_step_packets_are_orthonormal": gram == [[Fraction(i == j) for j in range(3)] for i in range(3)],
        "rational_step_packets_are_nonantipodal": antipodal == [[zero] * 3 for _ in range(3)],
        "scalar_multiplier_cross_Gram_is_identity": scalar_cross == [[Fraction(i == j) for j in range(3)] for i in range(3)],
        "Upsilon_fixture_obeys_uniform_bound": all(value <= 144 for value in u_norms),
        "Omega_fixture_obeys_uniform_bound": all(value <= Fraction(17, 4) for value in o_norms),
        "effect_characteristic_polynomial_is_exact": characteristic == expected,
        "source_click_entry_is_one_sixteenth": effect[0][0] == Fraction(1, 16),
        "compact_source_is_constructed": interpretation["compact_continuum_scalar_source"] == "CONSTRUCTED",
        "common_domain_is_constructed": interpretation["common_closable_Gaussian_domain"] == "CONSTRUCTED",
        "finite_volume_limit_is_fixed_strength_only": interpretation["finite_volume_source_effect_limit"] == "CONSTRUCTED_AT_FIXED_ZETA",
        "packet_strength_is_not_claimed": interpretation["packet_BT_Hamiltonian_strength"] == "NOT_COMPUTED",
        "ordinary_Fock_boundary_is_preserved": interpretation["ordinary_massless_Fock_IR_limit"] == "OBSTRUCTED",
        "Eq19_boundary_is_preserved": interpretation["general_Eq19"] == "NOT_PROVED" and any("Eq. (19)" in row for row in boundaries),
        "gravity_boundary_is_preserved": "gravity or BRST transfer" in boundaries,
        "Lorentzian_boundary_is_preserved": "anything LORENTZIAN-CAUSAL" in boundaries,
        "support_gap_is_explicit": "epsilon<=|p|<=M" in certificate["compact_packet_carrier"]["support_hypotheses"],
        "reflected_annihilator_is_retained": "A1(R_t*f/(2E))" in certificate["compact_packet_carrier"]["Omega_creator_full"],
        "trace_norm_bound_is_recorded": certificate["finite_volume_approximation"]["rank_one_bound"] == "||Theta_(x,x)-Theta_(y,y)||_1 <= (||x||+||y||)||x-y||",
    }
    return {name: bool(value) for name, value in checks.items()}


def main():
    checks = verify(load(CERT))
    failures = [name for name, value in checks.items() if not value]
    print("checks %d/%d" % (sum(checks.values()), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
