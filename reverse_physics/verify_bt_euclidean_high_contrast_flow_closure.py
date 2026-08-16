#!/usr/bin/env python3
"""Independent verifier for the BT high-contrast flow closure."""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import os
import sys
from collections import deque
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERTIFICATE = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_HIGH_CONTRAST_FLOW_CLOSURE_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-high-contrast-flow-closure-v1.schema.json",
)
PRODUCER = os.path.join(
    ROOT, "reverse_physics/bt_euclidean_high_contrast_flow_closure.py"
)
EDGE_CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_EDGE_ELLIPTICITY_V1.json",
)


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def decode_array(values: list[dict[str, int]]) -> list[Fraction]:
    return [decode(value) for value in values]


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def graph_ok(neighbors: list[list[int]]) -> bool:
    size = len(neighbors)
    if size < 2 or not neighbors:
        return False
    degree = len(neighbors[0])
    if degree < 1 or any(len(row) != degree for row in neighbors):
        return False
    for site, row in enumerate(neighbors):
        if len(set(row)) != degree or site in row:
            return False
        if any(other < 0 or other >= size or site not in neighbors[other] for other in row):
            return False
    seen = {0}
    queue = deque([0])
    while queue:
        site = queue.popleft()
        for other in neighbors[site]:
            if other not in seen:
                seen.add(other)
                queue.append(other)
    return len(seen) == size


def undirected_edges(neighbors: list[list[int]]) -> list[tuple[int, int]]:
    return sorted(
        {
            (min(site, other), max(site, other))
            for site, row in enumerate(neighbors)
            for other in row
        }
    )


def path_decomposition(
    size: int,
    edges: list[tuple[int, int]],
    flow: dict[tuple[int, int], Fraction],
    divergence: list[Fraction],
) -> tuple[bool, Fraction, Fraction, int]:
    capacity = dict(flow)
    outgoing: list[list[int]] = [[] for _ in range(size)]
    for tail, head in edges:
        outgoing[tail].append(head)
    supply = [max(-value, 0) for value in divergence]
    demand = [max(value, 0) for value in divergence]
    transported = Fraction(0)
    edge_mass = Fraction(0)
    longest = 0

    def find(start: int) -> list[int] | None:
        stack = [(start, [start])]
        seen: set[int] = set()
        while stack:
            site, path = stack.pop()
            if site != start and demand[site] > 0:
                return path
            if site in seen:
                continue
            seen.add(site)
            for other in outgoing[site]:
                if capacity[(site, other)] > 0:
                    stack.append((other, path + [other]))
        return None

    while any(value > 0 for value in supply):
        source = next(site for site, value in enumerate(supply) if value > 0)
        path = find(source)
        if path is None:
            return False, transported, edge_mass, longest
        amount = min(
            supply[source],
            demand[path[-1]],
            *(capacity[edge] for edge in zip(path, path[1:])),
        )
        if amount <= 0:
            return False, transported, edge_mass, longest
        supply[source] -= amount
        demand[path[-1]] -= amount
        for edge in zip(path, path[1:]):
            capacity[edge] -= amount
        length = len(path) - 1
        transported += amount
        edge_mass += amount * length
        longest = max(longest, length)
    ok = not any(supply) and not any(demand) and not any(capacity.values())
    return ok, transported, edge_mass, longest


def reconstruct(
    omega: list[Fraction], neighbors: list[list[int]]
) -> tuple[bool, dict[str, object]]:
    if not graph_ok(neighbors) or len(omega) != len(neighbors):
        return False, {}
    size = len(omega)
    degree = len(neighbors[0])
    if any(value <= 0 for value in omega) or len(set(omega)) == 1:
        return False, {}
    edges = undirected_edges(neighbors)
    maximum = max(
        max(omega[head] / omega[tail], omega[tail] / omega[head])
        for tail, head in edges
    )
    residual = [
        sum((omega[other] / omega[site] for other in row), Fraction(0)) - degree
        for site, row in enumerate(neighbors)
    ]
    gradient = []
    for site, row in enumerate(neighbors):
        gradient.append(
            sum(
                (residual[other] * omega[site] / omega[other] for other in row),
                Fraction(0),
            )
            - residual[site]
            * sum((omega[other] / omega[site] for other in row), Fraction(0))
        )

    c = [Fraction(0) for _ in omega]
    orientation: list[tuple[int, int, bool, Fraction, Fraction]] = []
    for left, right in edges:
        if omega[left] == omega[right]:
            orientation.append((left, right, True, Fraction(1), Fraction(0)))
        else:
            tail, head = (left, right) if omega[left] < omega[right] else (right, left)
            ratio = omega[head] / omega[tail]
            alpha = ratio / maximum
            c[tail] += alpha
            orientation.append((tail, head, False, ratio, alpha))
    h = [residual[site] - maximum * c[site] for site in range(size)]
    d = [Fraction(0) for _ in omega]
    current_div = [Fraction(0) for _ in omega]
    error_div = [Fraction(0) for _ in omega]
    flow: dict[tuple[int, int], Fraction] = {}
    rows = []
    edge_errors: list[Fraction] = []
    for tail, head, equal, ratio, alpha in orientation:
        if equal:
            current = residual[tail] - residual[head]
            main = Fraction(0)
        else:
            current = residual[tail] * ratio - residual[head] / ratio
            flow[(tail, head)] = c[tail] * alpha
            d[tail] -= flow[(tail, head)]
            d[head] += flow[(tail, head)]
            main = maximum**2 * flow[(tail, head)]
        error = current - main
        edge_errors.append(error)
        current_div[tail] -= current
        current_div[head] += current
        rows.append((tail, head, equal, ratio, alpha, current, main, error))
    for site in range(size):
        error_div[site] = gradient[site] - maximum**2 * d[site]

    flow_mass = sum((value * value for value in c), Fraction(0))
    divergence_l1 = sum((abs(value) for value in d), Fraction(0))
    divergence_l2 = sum((value * value for value in d), Fraction(0))
    error_l2 = sum((value * value for value in error_div), Fraction(0))
    residual_l2 = sum((value * value for value in residual), Fraction(0))
    gradient_l2 = sum((value * value for value in gradient), Fraction(0))
    path_ok, transported, edge_mass, longest = path_decomposition(
        size,
        [(tail, head) for tail, head, equal, _, _ in orientation if not equal],
        flow,
        d,
    )
    universal = (
        all(-degree <= value <= 0 for value in h)
        and current_div == gradient
        and flow_mass >= 1
        and path_ok
        and edge_mass == flow_mass
        and 2 * transported == divergence_l1
        and longest <= size - 1
        and (size - 1) * divergence_l1 >= 2 * flow_mass
        and all(abs(value) <= 3 * degree * maximum for value in edge_errors)
        and error_l2 <= 9 * size * degree**4 * maximum**2
        and sum(gradient, Fraction(0)) == 0
    )
    return universal, {
        "maximum": maximum,
        "residual": residual,
        "gradient": gradient,
        "c": c,
        "h": h,
        "d": d,
        "error_div": error_div,
        "rows": rows,
        "norms": [
            flow_mass,
            divergence_l1,
            divergence_l2,
            error_l2,
            residual_l2,
            gradient_l2,
        ],
    }


def fixture_matches(row: dict) -> bool:
    omega = decode_array(row["omega"])
    ok, data = reconstruct(omega, row["neighbors"])
    if not ok:
        return False
    stored_rows = row["edges"]
    rebuilt_rows = data["rows"]
    if len(stored_rows) != len(rebuilt_rows):
        return False
    for stored, rebuilt in zip(stored_rows, rebuilt_rows):
        tail, head, equal, ratio, alpha, current, main, error = rebuilt
        if not (
            stored["tail"] == tail
            and stored["head"] == head
            and stored["equal_edge"] is equal
            and decode(stored["ratio"]) == ratio
            and decode(stored["normalized_ratio"]) == alpha
            and decode(stored["current"]) == current
            and decode(stored["main_current"]) == main
            and decode(stored["error_current"]) == error
        ):
            return False
    stored_norms = row["norms"]
    norm_keys = [
        "flow_mass",
        "divergence_l1",
        "divergence_l2_squared",
        "error_divergence_norm_squared",
        "residual_norm_squared",
        "gradient_norm_squared",
    ]
    return (
        row["vertex_count"] == len(omega)
        and row["degree"] == len(row["neighbors"][0])
        and decode(row["maximum_edge_ratio"]) == data["maximum"]
        and decode_array(row["residual"]) == data["residual"]
        and decode_array(row["gradient"]) == data["gradient"]
        and decode_array(row["normalized_outgoing_mass"]) == data["c"]
        and decode_array(row["bounded_remainder"]) == data["h"]
        and decode_array(row["main_flow_divergence"]) == data["d"]
        and decode_array(row["error_divergence"]) == data["error_div"]
        and [decode(stored_norms[key]) for key in norm_keys] == data["norms"]
        and all(row["checks"].values())
    )


def exhaustive_rail() -> tuple[bool, int]:
    graphs = [
        [[3, 1], [0, 2], [1, 3], [2, 0]],
        [[4, 1], [0, 2], [1, 3], [2, 4], [3, 0]],
    ]
    checked = 0
    for graph in graphs:
        for values in itertools.product((1, 2, 3), repeat=len(graph)):
            if len(set(values)) == 1:
                continue
            ok, _ = reconstruct([Fraction(value) for value in values], graph)
            checked += 1
            if not ok:
                return False, checked
    return checked == (3**4 - 3) + (3**5 - 3), checked


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", default=DEFAULT_CERTIFICATE)
    args = parser.parse_args()
    certificate = load(args.certificate)
    schema = load(SCHEMA)
    checks: dict[str, bool] = {}
    checks["strict_schema"] = not list(
        Draft202012Validator(schema).iter_errors(certificate)
    )
    checks["predecessor_hashes"] = all(
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
    checks["three_exact_fixture_reconstructions"] = all(
        fixture_matches(row) for row in certificate["exact_fixtures"]
    )
    exhaustive_ok, checked = exhaustive_rail()
    checks["complete_small_rational_field_rail"] = exhaustive_ok

    theorem = certificate["finite_amplitude_theorem"]
    checks["sharp_declared_constants"] = (
        theorem["threshold"] == "W>=3*q^2*N*(N-1)"
        and theorem["quotient_floor"]
        == "||grad A||_2^2/||r||_2^2>=W^2/[q^2*N^2*(N-1)^2]>=9*q^2"
        and Fraction((3 * 8**2) ** 2, 8**2) == 9 * 8**2
        and 9 * 8**2 > (2 * 8) ** 2
    )
    edge_certificate = load(EDGE_CERT)
    imported_bound = edge_certificate["theorem"]["bounds"][
        "absolute_jump_exponential_moment"
    ]
    tail_constant = Fraction(4 * Fraction(16176, 25), (3 * 8**2) ** 2)
    checks["actual_gibbs_tail_rederived"] = (
        imported_bound == "E[exp(2|d_xy|)]<=16176/25"
        and tail_constant == Fraction(337, 4800)
        and certificate["actual_gibbs_corollary"]["union_markov_bound"]
        == "mu(W>=192*N*(N-1))<=337/[4800*N*(N-1)^2]"
    )
    disposition = certificate["research_disposition"]
    checks["honest_boundary"] = (
        disposition["polynomial_contrast_dense_multiscale_sector"] == "OPEN"
        and disposition["actual_interacting_h_minus_one"] == "OPEN"
        and disposition["continuum_measure"] == "NOT_ESTABLISHED"
        and "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"]
    )
    checks["certificate_self_check"] = certificate["checks"]["ok"] is True

    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        print("[FAIL] independent BT high-contrast flow verifier")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(
        "[PASS] independent BT high-contrast flow verifier "
        f"({len(checks)}/{len(checks)}; {checked} rational fields)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
