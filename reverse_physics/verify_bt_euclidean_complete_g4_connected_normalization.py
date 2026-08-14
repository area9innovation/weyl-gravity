#!/usr/bin/env python3
"""Independent verifier for the complete BT g^4 connected normalization."""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from collections import Counter
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from reverse_physics.verify_bt_euclidean_complete_g4_effective_hessian import (
    verify as verify_hessian_predecessor,
)


CERT_PATH = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_CONNECTED_NORMALIZATION_V1.json",
)
SCHEMA_PATH = os.path.join(
    ROOT,
    "reverse_physics/schema/reverse-physics-bt-euclidean-complete-g4-connected-normalization-v1.schema.json",
)
CUBIC_PATH = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_CUBIC_SCORE_LOG_OBSTRUCTION_V1.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def moment(power: int) -> Fraction:
    if power % 2:
        return Fraction(0)
    return Fraction(math.prod(range(1, power, 2)))


def expectation(polynomial: dict[int, Fraction]) -> Fraction:
    return sum(coefficient * moment(power) for power, coefficient in polynomial.items())


def add(*polynomials: dict[int, Fraction]) -> dict[int, Fraction]:
    powers = set().union(*(polynomial.keys() for polynomial in polynomials))
    return {power: sum(polynomial.get(power, 0) for polynomial in polynomials) for power in powers}


def scale(polynomial: dict[int, Fraction], factor: Fraction | int) -> dict[int, Fraction]:
    return {power: Fraction(factor) * coefficient for power, coefficient in polynomial.items()}


def multiply(left: dict[int, Fraction], right: dict[int, Fraction]) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            power = left_power + right_power
            result[power] = result.get(power, Fraction(0)) + left_coefficient * right_coefficient
    return result


def independent_fixture() -> dict[str, Fraction]:
    a = {0: Fraction(-1), 2: Fraction(1)}
    b = {1: Fraction(-1), 3: Fraction(1)}
    c_score = {2: Fraction(-3), 4: Fraction(1)}
    w1 = {1: Fraction(-5), 3: Fraction(2)}
    w2 = {0: Fraction(4), 2: Fraction(-4), 4: Fraction(1)}
    w1sq = multiply(w1, w1)
    r0 = add(scale(w1sq, Fraction(1, 2)), scale(w2, -1))
    z2 = expectation(r0)
    h = add(scale(w1sq, Fraction(1, 8)), scale(w2, Fraction(-1, 2)), {0: -z2 / 2})
    mean_h = expectation(h)
    aligned = -mean_h
    hc = add(h, {0: aligned})
    e = add(c_score, scale(multiply(w1, b), Fraction(-1, 2)), multiply(h, a))
    ec = add(e, scale(a, aligned))
    d = add(b, scale(multiply(w1, a), Fraction(-1, 2)))
    a2 = multiply(a, a)
    covariance = expectation(multiply(a2, r0)) - expectation(a2) * z2
    direct = expectation(
        add(
            multiply(b, b),
            scale(multiply(a, c_score), 2),
            scale(multiply(multiply(a, b), w1), -2),
            multiply(a2, add(r0, {0: -z2})),
        )
    )
    connected = expectation(multiply(b, b)) + 2 * expectation(multiply(a, c_score)) - 2 * expectation(multiply(multiply(a, b), w1)) + covariance
    norm = expectation(multiply(d, d)) + 2 * expectation(multiply(a, e))
    cancellation = expectation(w1sq) * expectation(a2) / 4
    return {
        "E_W1_squared": expectation(w1sq),
        "E_W2": expectation(w2),
        "z2": z2,
        "mean_H": mean_h,
        "aligned_coefficient": aligned,
        "mean_H_centered": expectation(hc),
        "D_norm_squared": expectation(multiply(d, d)),
        "twice_A_E": 2 * expectation(multiply(a, e)),
        "twice_A_E_connected": 2 * expectation(multiply(a, ec)),
        "disconnected_D_contribution": cancellation,
        "disconnected_cross_contribution": -cancellation,
        "M4_direct": direct,
        "M4_connected": connected,
        "M4_square_root_norm": norm,
    }


def perfect_matchings(items):
    if not items:
        yield ()
        return
    anchor = items[-1]
    for index, partner in enumerate(items[:-1]):
        for rest in perfect_matchings(items[:index] + items[index + 1 : -1]):
            yield rest + ((anchor, partner),)


def signed_transfers(h_legs: int) -> set[int]:
    return {-h_legs + 2 * plus for plus in range(h_legs + 1)}


def independent_classification(atoms, cut):
    if (3, 3) in atoms:
        return {"TERM_VANISHES_BY_U33_MOMENTUM": 1}
    slots = tuple(
        (vertex, slot)
        for vertex, (degree, h_legs) in enumerate(atoms)
        for slot in range(degree - h_legs)
    )
    counts = Counter()
    for matching in perfect_matchings(slots):
        active = [i for i, (degree, h_legs) in enumerate(atoms) if degree > h_legs]
        adjacency = {i: set() for i in active}
        for (left, _), (right, _) in matching:
            adjacency[left].add(right)
            adjacency[right].add(left)
        components = []
        unseen = set(active)
        while unseen:
            seed = unseen.pop()
            stack = [seed]
            vertices = {seed}
            while stack:
                vertex = stack.pop()
                for neighbor in adjacency[vertex]:
                    if neighbor in unseen:
                        unseen.remove(neighbor)
                        vertices.add(neighbor)
                        stack.append(neighbor)
            edges = sum(
                1
                for (left, _), (right, _) in matching
                if left in vertices and right in vertices
            )
            components.append((vertices, edges))
        momentum_forbidden = False
        for vertices, edges in components:
            possible = {0}
            for vertex in vertices:
                possible = {
                    left + right
                    for left in possible
                    for right in signed_transfers(atoms[vertex][1])
                }
            if 0 not in possible:
                momentum_forbidden = True
        if momentum_forbidden:
            counts["VANISHES_BY_COMPONENT_MOMENTUM"] += 1
            continue
        if cut is not None:
            left_set, right_set = cut
            crosses = any(
                (left in left_set and right in right_set)
                or (right in left_set and left in right_set)
                for (left, _), (right, _) in matching
            )
            if not crosses:
                counts["CANCELED_BY_COVARIANCE_SUBTRACTION"] += 1
                continue
        loops = sum(edges - len(vertices) + 1 for vertices, edges in components)
        counts[f"SURVIVING_LOOP_{loops}"] += 1
    return dict(sorted(counts.items()))


def expected_connected_terms():
    direct = [
        ("U41^2", Fraction(1), 0, [(4, 1), (4, 1)], None),
        ("2*U31*U51", Fraction(2), 0, [(3, 1), (5, 1)], None),
        ("-2*U31*U41*U30", Fraction(-2), 0, [(3, 1), (4, 1), (3, 0)], None),
        ("-2*v*U31*U41*U32", Fraction(-2), 1, [(3, 1), (4, 1), (3, 2)], None),
    ]
    r0 = [
        ("U30^2", Fraction(1, 2), 0, [(3, 0), (3, 0)]),
        ("U30*U32", Fraction(1), 1, [(3, 0), (3, 2)]),
        ("U32^2", Fraction(3, 2), 2, [(3, 2), (3, 2)]),
        ("-U40", Fraction(-1), 0, [(4, 0)]),
        ("-v*U42", Fraction(-1), 1, [(4, 2)]),
        ("-3*v^2*U44", Fraction(-3), 2, [(4, 4)]),
        ("v*U31^2/2", Fraction(1, 2), 1, [(3, 1), (3, 1)]),
        ("3*v^2*U31*U33", Fraction(3), 2, [(3, 1), (3, 3)]),
        ("15*v^3*U33^2/2", Fraction(15, 2), 3, [(3, 3), (3, 3)]),
    ]
    result = list(direct)
    for name, coefficient, v_power, atoms in r0:
        all_atoms = [(3, 1), (3, 1)] + atoms
        result.append(
            (
                "Cov(U31^2," + name + ")",
                coefficient,
                v_power,
                all_atoms,
                ({0, 1}, set(range(2, len(all_atoms)))),
            )
        )
    return result


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
        if not verify_hessian_predecessor():
            return False

        exact = independent_fixture()
        values = data["exact_gaussian_fixture"]["values"]
        if any(decode(values[name]) != value for name, value in exact.items()):
            return False
        if exact["mean_H"] != -exact["E_W1_squared"] / 8:
            return False
        if exact["disconnected_D_contribution"] != -exact["disconnected_cross_contribution"]:
            return False
        if not (exact["M4_direct"] == exact["M4_connected"] == exact["M4_square_root_norm"] == 590):
            return False

        preflight = data["numerical_preflight"]
        if file_hash(preflight["source"]) != preflight["source_sha256"]:
            return False
        if file_hash(preflight["data"]) != preflight["data_sha256"]:
            return False
        with open(os.path.join(ROOT, preflight["data"]), encoding="utf-8") as handle:
            raw_preflight = json.load(handle)
        if preflight["rows"] != raw_preflight["rows"]:
            return False
        if any(abs(row["M4_z_score"]) > 2 for row in preflight["rows"]):
            return False
        if any(abs(row["cross_over_D2"] + 1) > Fraction(3, 100) for row in preflight["rows"]):
            return False

        pairing_rows = data["connected_pairing_audit"]["labeled_pairing_table"]
        if len(pairing_rows) != 13:
            return False
        for row, expected in zip(pairing_rows, expected_connected_terms()):
            name, coefficient, v_power, atoms, cut = expected
            if row["name"] != name or decode(row["coefficient"]) != coefficient or row["v_power"] != v_power:
                return False
            if row["atoms"] != [f"U{degree}{h_legs}" for degree, h_legs in atoms]:
                return False
            if row["classification"] != independent_classification(atoms, cut):
                return False
        loop_ranks = {
            int(label.rsplit("_", 1)[1])
            for row in pairing_rows
            for label, count in row["classification"].items()
            if label.startswith("SURVIVING_LOOP_") and count
        }
        if loop_ranks != {0, 1, 2}:
            return False

        with open(CUBIC_PATH, encoding="utf-8") as handle:
            cubic = json.load(handle)
        fixture = cubic["exact_cubic_expansion"]["position_fourier_l4_fixture"]
        if decode(fixture["position_space_half_sum_Delta_phi_times_edge_square"]) != -1024:
            return False
        if decode(cubic["exact_cubic_expansion"]["exact_fixture"]["vertex"]) != -16:
            return False

        required = {
            "complete_M4_connected_covariance_reorganization": "PROVED",
            "normalization_aligned_A_sector": "PROVED_EXTENSIVE",
            "complete_connected_M4_maximum_loop_rank": "TWO",
            "separate_or_triangle_bound_on_aligned_sector": "OBSTRUCTED_AS_FORMULATED",
            "full_combined_Pi2E_norm_bound": "OPEN_INTERNAL_CANCELLATION_REQUIRED",
            "exact_whole_lattice_M4_cancellation": "OPEN_NUMERICALLY_SUPPORTED",
            "whole_lattice_order_g_four_power_survival": "OPEN",
            "actual_interacting_h_minus_one_second_moment": "OPEN",
            "continuum_limit": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        }
        disposition = data["method_disposition"]
        if any(disposition.get(key) != value for key, value in required.items()):
            return False
        return all(data["checks"].values())
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else CERT_PATH
    raise SystemExit(0 if verify(target) else 1)
