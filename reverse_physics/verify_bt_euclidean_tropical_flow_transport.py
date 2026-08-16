#!/usr/bin/env python3
"""Independent verifier for the BT tropical flow-transport certificate."""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import os
import sys
from collections import deque

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERTIFICATE = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TROPICAL_FLOW_TRANSPORT_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-tropical-flow-transport-v1.schema.json",
)
PRODUCER = os.path.join(ROOT, "reverse_physics/bt_euclidean_tropical_flow_transport.py")


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def neighbors(shape: tuple[int, ...]) -> list[list[int]]:
    points = list(itertools.product(*(range(length) for length in shape)))
    locate = {point: position for position, point in enumerate(points)}
    graph: list[list[int]] = []
    for point in points:
        row: list[int] = []
        for axis, length in enumerate(shape):
            for step in (-1, 1):
                other = list(point)
                other[axis] = (other[axis] + step) % length
                row.append(locate[tuple(other)])
        graph.append(row)
    return graph


def diameter(graph: list[list[int]]) -> int:
    result = 0
    for root in range(len(graph)):
        distance = {root: 0}
        queue = deque([root])
        while queue:
            site = queue.popleft()
            for other in graph[site]:
                if other not in distance:
                    distance[other] = distance[site] + 1
                    queue.append(other)
        if len(distance) != len(graph):
            raise ValueError("disconnected graph")
        result = max(result, max(distance.values()))
    return result


def reconstruct(
    exponent: tuple[int, ...], graph: list[list[int]]
) -> tuple[int, list[tuple[int, int]], list[int], list[int], int, int]:
    jump = max(
        exponent[other] - exponent[site]
        for site, row in enumerate(graph)
        for other in row
    )
    edges = [
        (site, other)
        for site, row in enumerate(graph)
        for other in row
        if exponent[other] - exponent[site] == jump
    ]
    counts = [0] * len(graph)
    for tail, _ in edges:
        counts[tail] += 1
    divergence = [-count * count for count in counts]
    for tail, head in edges:
        divergence[head] += counts[tail]
    flow_mass = sum(count * count for count in counts)
    square_mass = sum(value * value for value in divergence)
    return jump, edges, counts, divergence, flow_mass, square_mass


def stored_path_check(row: dict) -> bool:
    capacity = {
        tuple(edge): row["max_jump_outdegrees"][edge[0]]
        for edge in row["max_jump_edges"]
    }
    supply = [max(-value, 0) for value in row["flow_divergence"]]
    demand = [max(value, 0) for value in row["flow_divergence"]]
    for path_row in row["path_decomposition"]:
        path = path_row["vertices"]
        mass = path_row["mass"]
        if path_row["length"] != len(path) - 1 or mass <= 0:
            return False
        if supply[path[0]] < mass or demand[path[-1]] < mass:
            return False
        supply[path[0]] -= mass
        demand[path[-1]] -= mass
        for edge in zip(path, path[1:]):
            if edge not in capacity or capacity[edge] < mass:
                return False
            capacity[edge] -= mass
    return not any(supply) and not any(demand) and not any(capacity.values())


def exhaustive_rail() -> tuple[bool, int]:
    cases = [((4,), range(3)), ((6,), range(2)), ((3, 3), range(2))]
    checked = 0
    for shape, values in cases:
        graph = neighbors(shape)
        graph_diameter = diameter(graph)
        for exponent in itertools.product(values, repeat=len(graph)):
            if min(exponent) != 0 or len(set(exponent)) == 1:
                continue
            jump, edges, counts, divergence, flow_mass, square_mass = reconstruct(
                exponent, graph
            )
            checked += 1
            if jump <= 0 or not edges or sum(divergence) != 0:
                return False, checked
            if any(exponent[head] <= exponent[tail] for tail, head in edges):
                return False, checked
            if square_mass * graph_diameter < 2 * flow_mass:
                return False, checked
    return checked == 636, checked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", default=DEFAULT_CERTIFICATE)
    args = parser.parse_args()
    certificate = load(args.certificate)
    schema = load(SCHEMA)
    checks: dict[str, bool] = {}

    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    checks["predecessor_hash"] = all(
        sha256(row["path"]) == row["sha256"]
        for row in certificate["provenance"]["inputs"]
    )
    with open(__file__, encoding="utf-8") as handle:
        producer_name = os.path.splitext(os.path.basename(PRODUCER))[0]
        imports = [
            node
            for node in ast.walk(ast.parse(handle.read()))
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
    checks["nonimporting_verifier"] = all(
        not (
            isinstance(node, ast.ImportFrom)
            and node.module
            and producer_name in node.module
        )
        and not (
            isinstance(node, ast.Import)
            and any(producer_name in alias.name for alias in node.names)
        )
        for node in imports
    )

    fixtures_ok = True
    for row in certificate["exact_fixtures"]:
        graph = neighbors(tuple(row["shape"]))
        data = reconstruct(tuple(row["exponents"]), graph)
        jump, edges, counts, divergence, flow_mass, square_mass = data
        fixtures_ok &= row["diameter"] == diameter(graph)
        fixtures_ok &= row["max_edge_exponent_jump"] == jump
        fixtures_ok &= row["max_jump_edges"] == [list(edge) for edge in edges]
        fixtures_ok &= row["max_jump_outdegrees"] == counts
        fixtures_ok &= row["flow_divergence"] == divergence
        fixtures_ok &= row["flow_mass"] == flow_mass
        fixtures_ok &= row["divergence_l2_squared"] == square_mass
        fixtures_ok &= sum(abs(value) for value in divergence) == row["divergence_l1"]
        fixtures_ok &= square_mass * row["diameter"] >= 2 * flow_mass
        fixtures_ok &= stored_path_check(row)
        fixtures_ok &= sum(
            path["mass"] * path["length"] for path in row["path_decomposition"]
        ) == flow_mass
        fixtures_ok &= all(
            path["length"] <= row["diameter"]
            for path in row["path_decomposition"]
        )
    checks["three_fixture_reconstructions"] = fixtures_ok

    exhaustive_ok, checked = exhaustive_rail()
    checks["complete_small_profile_rail"] = exhaustive_ok
    checks["declared_universal_bound"] = (
        certificate["theorem"]["coefficient_bound"]
        == "(sum d_x^2)/(sum c_x^2)>=2/diam(G)"
    )
    checks["four_torus_diameter_and_scale"] = (
        certificate["four_torus_corollary"]["coefficient_floor"]
        == "2/diam(T_L^4)>=1/L"
        and certificate["four_torus_corollary"]["normalized_leading_floor"]
        == "lim t^(-2D)*[||grad A||^2/(omega_L^2||r||^2)]>=L^3/(16*pi^4)"
    )
    checks["honest_boundary"] = (
        certificate["research_disposition"]["joint_L_dependent_uniform_remainder"]
        == "OPEN"
        and certificate["research_disposition"]["actual_interacting_h_minus_one"]
        == "OPEN"
        and "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"]
    )
    checks["certificate_self_check"] = certificate["checks"]["ok"] is True

    failures = [key for key, value in checks.items() if not value]
    if failures:
        print("[FAIL] independent BT tropical flow transport verifier")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "[PASS] independent BT tropical flow transport verifier "
        f"({len(checks)}/{len(checks)}; {checked} exponent classes)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
