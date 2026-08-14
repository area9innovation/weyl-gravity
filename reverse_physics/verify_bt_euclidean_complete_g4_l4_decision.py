#!/usr/bin/env python3
"""Independent verifier for the exact L=4 complete BT g^4 decision."""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
from fractions import Fraction
from functools import lru_cache

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from reverse_physics.verify_bt_euclidean_complete_g4_connected_normalization import (
    verify as verify_connected_predecessor,
)


CERT_PATH = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_L4_DECISION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-complete-g4-l4-decision-v1.schema.json",
)
EXPECTED_NAMES = [
    "U41^2",
    "2*U31*U51",
    "-2*U31*U41*U30",
    "-2*v*U31*U41*U32",
    "Cov(U31^2,U30^2)",
    "Cov(U31^2,U30*U32)",
    "Cov(U31^2,U32^2)",
    "Cov(U31^2,-U40)",
    "Cov(U31^2,-v*U42)",
    "Cov(U31^2,-3*v^2*U44)",
    "Cov(U31^2,v*U31^2/2)",
    "Cov(U31^2,3*v^2*U31*U33)",
    "Cov(U31^2,15*v^3*U33^2/2)",
]
TERM_DEFINITIONS = [
    (Fraction(1), 0, [(4, 1), (4, 1)]),
    (Fraction(2), 0, [(3, 1), (5, 1)]),
    (Fraction(-2), 0, [(3, 1), (4, 1), (3, 0)]),
    (Fraction(-2), 1, [(3, 1), (4, 1), (3, 2)]),
    (Fraction(1, 2), 0, [(3, 1), (3, 1), (3, 0), (3, 0)]),
    (Fraction(1), 1, [(3, 1), (3, 1), (3, 0), (3, 2)]),
    (Fraction(3, 2), 2, [(3, 1), (3, 1), (3, 2), (3, 2)]),
    (Fraction(-1), 0, [(3, 1), (3, 1), (4, 0)]),
    (Fraction(-1), 1, [(3, 1), (3, 1), (4, 2)]),
    (Fraction(-3), 2, [(3, 1), (3, 1), (4, 4)]),
    (Fraction(1, 2), 1, [(3, 1), (3, 1), (3, 1), (3, 1)]),
    (Fraction(3), 2, [(3, 1), (3, 1), (3, 1), (3, 3)]),
    (Fraction(15, 2), 3, [(3, 1), (3, 1), (3, 3), (3, 3)]),
]
KERNEL_DENOMINATOR = {3: 6, 4: 24, 5: 120}
KERNEL_BOUND = {
    3: Fraction(1536, 6),
    4: Fraction(7168, 24),
    5: Fraction(30720, 120),
}
PROP_LCM = 2822400


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def is_prime_64(value: int) -> bool:
    if value < 2:
        return False
    for prime in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if value % prime == 0:
            return value == prime
    odd = value - 1
    twos = 0
    while odd % 2 == 0:
        twos += 1
        odd //= 2
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % value == 0:
            continue
        residue = pow(base, odd, value)
        if residue in (1, value - 1):
            continue
        for _ in range(twos - 1):
            residue = residue * residue % value
            if residue == value - 1:
                break
        else:
            return False
    return True


@lru_cache(maxsize=4)
def run_modular(source_hash: str) -> dict:
    source = os.path.join(
        ROOT, "reverse_physics/bt_euclidean_complete_g4_l4_modular_verify.cpp"
    )
    if file_hash(os.path.relpath(source, ROOT)) != source_hash:
        raise ValueError("modular source hash drift")
    with tempfile.TemporaryDirectory(prefix="bt-g4-l4-modular-") as directory:
        executable = os.path.join(directory, "verify")
        subprocess.run(
            [
                "g++", "-std=c++17", "-O3", "-Wall", "-Wextra", "-Werror",
                source, "-o", executable,
            ],
            check=True,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        completed = subprocess.run(
            [executable], check=True, cwd=ROOT, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True,
        )
    return json.loads(completed.stdout)


def atom_prefactor(atom: tuple[int, int]) -> Fraction:
    degree, h_legs = atom
    eta_legs = degree - h_legs
    normalization = Fraction(16 ** (2 - eta_legs)) if eta_legs <= 2 else Fraction(1, 16 ** (eta_legs - 2))
    return Fraction(math.comb(degree, h_legs), 2**h_legs) * normalization


def exact_modular_bound(m4: Fraction):
    one_dimensional = (0, 2, 4, 2)
    omegas = [
        one_dimensional[q0] + one_dimensional[q1] + one_dimensional[q2] + one_dimensional[q3]
        for q0 in range(4) for q1 in range(4) for q2 in range(4) for q3 in range(4)
    ]
    covariance_sum = sum((Fraction(1, value * value) for value in omegas if value), Fraction(1, 2))
    common_denominator = 1
    expression_bound = Fraction(0)
    term_bounds = []
    for name, (coefficient, v_power, atoms) in zip(EXPECTED_NAMES, TERM_DEFINITIONS):
        edges = sum(degree - h_legs for degree, h_legs in atoms) // 2
        outer = abs(coefficient) * Fraction(1, 512) ** v_power
        for atom in atoms:
            outer *= abs(atom_prefactor(atom))
        common_denominator = math.lcm(
            common_denominator,
            outer.denominator
            * math.prod(KERNEL_DENOMINATOR[degree] for degree, _ in atoms)
            * PROP_LCM**edges,
        )
        pairing_count = math.prod(range(1, 2 * edges, 2)) if edges else 1
        bound = outer * pairing_count * 2 ** sum(h for _, h in atoms) * covariance_sum**edges
        for degree, _ in atoms:
            bound *= KERNEL_BOUND[degree]
        expression_bound += bound
        term_bounds.append((name, bound))
    difference_bound = (
        m4.denominator * common_denominator * expression_bound
        + abs(m4.numerator) * common_denominator
    )
    return covariance_sum, common_denominator, expression_bound, term_bounds, difference_bound


def independent_A2() -> Fraction:
    one = (0, 2, 4, 2)
    external = 2
    total = Fraction(0)
    for q0 in range(4):
        for q1 in range(4):
            for q2 in range(4):
                for q3 in range(4):
                    if (q0, q1, q2, q3) in ((0, 0, 0, 0), (3, 0, 0, 0)):
                        continue
                    b = one[q0] + one[q1] + one[q2] + one[q3]
                    c = one[(q0 + 1) % 4] + one[q1] + one[q2] + one[q3]
                    vertex = external**2 + b**2 + c**2 - 2 * (external * b + external * c + b * c)
                    total += Fraction(vertex**2, b**2 * c**2)
    exceptional_vertex = external**2 + external**2 + 4**2 - 2 * (external**2 + 2 * external * 4)
    correction = Fraction(exceptional_vertex**2, 2 * 256 * external**4 * 4**2)
    coefficient = total / (4 * 256 * external**2) - correction
    return coefficient * 256 * external**2


def residues(value: Fraction, primes: list[int]) -> list[int]:
    return [value.numerator % prime * pow(value.denominator, -1, prime) % prime for prime in primes]


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
        if file_hash(data["data"]) != data["data_sha256"]:
            return False
        if not verify_connected_predecessor():
            return False

        exact = data["exact_L4_decision"]
        m4 = decode(exact["M4"])
        if m4 != Fraction(-338835474713437, 204838502400000) or m4 >= 0:
            return False
        rows = exact["term_ledger"]
        if [row["name"] for row in rows] != EXPECTED_NAMES:
            return False
        if sum((decode(row["value"]) for row in rows), Fraction(0)) != m4:
            return False
        if any(
            sum((decode(sector["value"]) for sector in row["rank_loop_sectors"]), Fraction(0))
            != decode(row["value"])
            for row in rows
            if row["reason"] != "U33_IS_ZERO"
        ):
            return False
        computed_sector_totals = {}
        for row in rows:
            for sector in row["rank_loop_sectors"]:
                key = sector["rank_insertions"], sector["loop_rank"]
                computed_sector_totals[key] = computed_sector_totals.get(key, Fraction(0)) + decode(sector["value"])
        declared_sector_totals = {
            (sector["rank_insertions"], sector["loop_rank"]): decode(sector["value"])
            for sector in exact["rank_loop_sector_totals"]
        }
        if declared_sector_totals != {key: value for key, value in computed_sector_totals.items() if value}:
            return False
        sector_sum = sum(
            (decode(sector["value"]) for row in rows for sector in row["rank_loop_sectors"]),
            Fraction(0),
        )
        if sector_sum != m4:
            return False
        if any(sector["loop_rank"] > 2 for row in rows for sector in row["rank_loop_sectors"]):
            return False

        modular = data["independent_modular_verification"]
        if file_hash(modular["source"]) != modular["source_sha256"]:
            return False
        primes = modular["primes"]
        if len(set(primes)) != 4 or not all(is_prime_64(prime) for prime in primes):
            return False
        output = run_modular(modular["source_sha256"])
        if output["primes"] != primes or len(output["terms"]) != len(rows):
            return False
        if any(residues(decode(row["value"]), primes) != result for row, result in zip(rows, output["terms"])):
            return False
        if residues(m4, primes) != output["M4"]:
            return False

        covariance_sum, common_denominator, expression_bound, term_bounds, difference_bound = exact_modular_bound(m4)
        if decode(modular["covariance_expansion_absolute_sum"]) != covariance_sum:
            return False
        if modular["common_expression_denominator"] != common_denominator:
            return False
        if decode(modular["expression_absolute_bound"]) != expression_bound:
            return False
        if [(row["name"], decode(row["absolute_bound"])) for row in modular["term_bounds"]] != term_bounds:
            return False
        if modular["integer_difference_bound"] != difference_bound or difference_bound.denominator != 1:
            return False
        prime_product = math.prod(primes)
        if modular["prime_product"] != prime_product or not prime_product > 2 * difference_bound:
            return False

        cross = data["normalization_crosschecks"]
        if not (
            independent_A2()
            == decode(cross["A2_from_independent_certified_cubic_sum"])
            == Fraction(54853, 840)
        ):
            return False
        if decode(cross["B2_from_exact_quartic_Wick_sum"]) != decode(rows[0]["value"]):
            return False
        if abs(cross["exact_minus_numerical_in_standard_errors"]) >= 1:
            return False
        required = {
            "finite_L4_complete_M4": "NEGATIVE_NONZERO_EXACT",
            "all_volume_exact_M4_zero_identity": "OBSTRUCTED_BY_L4_COUNTEREXAMPLE",
            "conditioned_connected_maximum_loop_rank": "TWO",
            "large_volume_M4_sign_and_scaling": "OPEN",
            "whole_lattice_order_g_four_power_survival": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        }
        if any(data["method_disposition"].get(key) != value for key, value in required.items()):
            return False
        return all(data["checks"].values())
    except (
        KeyError, OSError, TypeError, ValueError, json.JSONDecodeError,
        subprocess.CalledProcessError,
    ):
        return False


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else CERT_PATH
    raise SystemExit(0 if verify(target) else 1)
