#!/usr/bin/env python3
"""Independent verifier for the BT cubic-score logarithmic obstruction."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_PATH = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_SCORE_LOG_OBSTRUCTION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-cubic-score-log-obstruction-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def independent_coefficient(length: int) -> float:
    dispersion_1d = tuple(
        4.0 * math.sin(math.pi * index / length) ** 2
        for index in range(length)
    )
    a = dispersion_1d[1]
    summation = 0.0
    for indices in itertools.product(range(length), repeat=4):
        if indices in ((0, 0, 0, 0), (length - 1, 0, 0, 0)):
            continue
        b = math.fsum(dispersion_1d[index] for index in indices)
        shifted = ((indices[0] + 1) % length, *indices[1:])
        c = math.fsum(dispersion_1d[index] for index in shifted)
        heron = a * a + b * b + c * c - 2.0 * (a * b + a * c + b * c)
        summation += heron * heron / (b * b * c * c)
    volume = length**4
    full_coefficient = summation / (4.0 * volume * a * a)
    doubled = dispersion_1d[2]
    exceptional = a * a + a * a + doubled * doubled - 2.0 * (a * a + 2.0 * a * doubled)
    exceptional_full = exceptional * exceptional / (2.0 * volume * a**4 * doubled**2)
    return full_coefficient - (exceptional_full if length == 4 else exceptional_full / 2.0)


def block_count(length: int) -> int:
    return sum(1 for scale in (1 << exponent for exponent in range(64)) if 16 * scale <= length)


def close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=2.0e-12, abs_tol=2.0e-14)


def independent_position_cubic_fixture() -> Fraction:
    length = 4
    dimensions = 4
    volume = length**dimensions

    def coordinates(index: int) -> tuple[int, ...]:
        output = [0] * dimensions
        for axis in range(dimensions - 1, -1, -1):
            output[axis] = index % length
            index //= length
        return tuple(output)

    def index(site: tuple[int, ...]) -> int:
        output = 0
        for coordinate in site:
            output = length * output + coordinate
        return output

    cosine = (1, 0, -1, 0)
    sites = tuple(coordinates(i) for i in range(volume))
    field = tuple(
        cosine[site[0]] + cosine[site[1]] + cosine[(site[0] + site[1]) % length]
        for site in sites
    )
    twice_cubic = 0
    for site_number, site in enumerate(sites):
        differences = []
        for axis in range(dimensions):
            for step in (-1, 1):
                neighbor = list(site)
                neighbor[axis] = (neighbor[axis] + step) % length
                differences.append(field[index(tuple(neighbor))] - field[site_number])
        twice_cubic += sum(differences) * sum(value * value for value in differences)
    return Fraction(twice_cubic, 2)


def verify(path: str = CERT_PATH) -> bool:
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        if list(Draft202012Validator(schema).iter_errors(data)):
            return False
        for source in data["provenance"]["inputs"]:
            if file_hash(source["path"]) != source["sha256"]:
                return False

        cubic = data["exact_cubic_expansion"]
        fixture = cubic["exact_fixture"]
        a, b, c = map(decode, fixture["dispersions"])
        direct_vertex = a * a + b * b + c * c - 2 * (a * b + a * c + b * c)
        if (a, b, c) != (2, 2, 4) or direct_vertex != -16:
            return False
        if decode(fixture["vertex"]) != direct_vertex:
            return False
        position_fourier = cubic["position_fourier_l4_fixture"]
        direct_position = independent_position_cubic_fixture()
        fourier_value = Fraction(
            position_fourier["ordered_resonant_triples"]
            * direct_vertex
            * decode(position_fourier["fourier_amplitude_per_mode"]) ** 3,
            6 * 16,
        )
        if direct_position != -1024 or fourier_value != direct_position:
            return False
        if decode(position_fourier["position_space_half_sum_Delta_phi_times_edge_square"]) != direct_position:
            return False
        if decode(position_fourier["fourier_vertex_cubic_coefficient"]) != fourier_value:
            return False
        if cubic["status"] != "PROVED":
            return False

        # Independently check the polynomial identity used on each momentum box.
        for values in (
            (Fraction(1), Fraction(2), Fraction(3), Fraction(5)),
            (Fraction(2, 3), Fraction(7, 5), Fraction(11, 7), Fraction(13, 4)),
            (Fraction(5), Fraction(1, 9), Fraction(4, 3), Fraction(8)),
        ):
            aa, x, y, u = values
            vertex = lambda aa, bb, cc: aa**2 + bb**2 + cc**2 - 2 * (aa * bb + aa * cc + bb * cc)
            if vertex(aa, x + u, y + u) != vertex(aa, x, y) - 4 * aa * u:
                return False

        lower = data["rigorous_logarithmic_lower_bound"]
        if decode(lower["lower_bound_per_block"]) != Fraction(1, 4 * 1080**2):
            return False
        if lower["status"] != "PROVED":
            return False
        if lower["asymptotic_disposition"] != "C_L is unbounded and grows at least logarithmically in the lattice-size limit; ultraviolet-refinement versus soft-large-volume interpretation depends on scale setting":
            return False

        table = data["numerical_preflight"]["table"]
        if [row["length"] for row in table] != [4, 6, 8, 12, 16, 24, 32]:
            return False
        for row in table:
            length = row["length"]
            if row["volume"] != length**4:
                return False
            expected_omega = 4.0 * math.sin(math.pi / length) ** 2
            if not close(row["omega_external"], expected_omega):
                return False
            expected_coefficient = independent_coefficient(length)
            if not close(row["coefficient_C_L"], expected_coefficient):
                return False
            if not close(row["coefficient_over_log_L"], expected_coefficient / math.log(length)):
                return False
            if not close(row["rigorous_dyadic_lower_bound"], block_count(length) / 4_665_600):
                return False

        disposition = data["method_disposition"]
        required = {
            "leading_free_gaussian_score_coefficient_uniform_in_L": "OBSTRUCTED",
            "fixed_bare_coupling_coefficientwise_uniform_score_proof": "OBSTRUCTED_AS_FORMULATED",
            "renormalized_or_running_coupling_score_bound": "OPEN",
            "nonperturbative_annealed_zero_fiber_score_bound": "OPEN",
            "normalized_lowest_mode_second_moment": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        }
        if any(disposition.get(name) != value for name, value in required.items()):
            return False
        if not all(data["checks"].values()):
            return False
        return True
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else CERT_PATH
    raise SystemExit(0 if verify(target) else 1)
