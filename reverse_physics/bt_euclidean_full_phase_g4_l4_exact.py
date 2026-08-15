#!/usr/bin/env python3
"""Exact L=4 full-phase BT M4 preflight with the 0,+p,-p modes removed."""

from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import sys
from collections import Counter
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from reverse_physics.bt_euclidean_complete_g4_connected_normalization import pairings
from reverse_physics.bt_euclidean_complete_g4_l4_exact import (
    ADD,
    FIBER_VARIANCE,
    KERNEL_DENOMINATOR,
    MINUS_P,
    NEG,
    OMEGA,
    P,
    PROPAGATOR_LCM,
    SQRT_VOLUME,
    gmul,
    kernel_numerator,
)


DATA_REL = "reverse_physics/data/bt_euclidean_full_phase_g4_l4_exact_v1.json"
DATA_PATH = os.path.join(ROOT, DATA_REL)
VOLUME = SQRT_VOLUME**2
ALLOWED = tuple(momentum for momentum in range(VOLUME) if momentum not in (0, P, MINUS_P))


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def scale_volume(power: int) -> Fraction:
    return Fraction(SQRT_VOLUME**power) if power >= 0 else Fraction(1, SQRT_VOLUME ** (-power))


def vertex(kind: str, sign: int = 0) -> dict:
    momentum = P if sign > 0 else MINUS_P
    if kind == "A":
        return {"degree": 3, "fixed": (momentum,), "prefactor": Fraction(3, 2)}
    if kind == "B":
        return {"degree": 4, "fixed": (momentum,), "prefactor": Fraction(2, SQRT_VOLUME)}
    if kind == "C":
        return {"degree": 5, "fixed": (momentum,), "prefactor": Fraction(5, 2 * VOLUME)}
    if kind == "U30":
        return {"degree": 3, "fixed": (), "prefactor": Fraction(1, SQRT_VOLUME)}
    if kind == "U40":
        return {"degree": 4, "fixed": (), "prefactor": Fraction(1, VOLUME)}
    if kind == "F42":
        return {"degree": 4, "fixed": (P, MINUS_P), "prefactor": Fraction(6)}
    if kind == "Q":
        return {"degree": 3, "fixed": (momentum, momentum), "prefactor": Fraction(3 * SQRT_VOLUME, 4)}
    raise ValueError(kind)


def terms() -> list[dict]:
    v = FIBER_VARIANCE
    return [
        {"name": "|B|^2", "coefficient": Fraction(4), "vertices": [vertex("B", 1), vertex("B", -1)], "cut": None},
        {"name": "2*A.C", "coefficient": Fraction(8), "vertices": [vertex("A", 1), vertex("C", -1)], "cut": None},
        {"name": "-2*U30*A.B", "coefficient": Fraction(-8), "vertices": [vertex("A", 1), vertex("B", -1), vertex("U30")], "cut": None},
        {"name": "Cov(|A|^2,U30^2/2)", "coefficient": Fraction(2), "vertices": [vertex("A", 1), vertex("A", -1), vertex("U30"), vertex("U30")], "cut": ({0, 1}, {2, 3})},
        {"name": "Cov(|A|^2,-U40)", "coefficient": Fraction(-4), "vertices": [vertex("A", 1), vertex("A", -1), vertex("U40")], "cut": ({0, 1}, {2})},
        {"name": "Cov(|A|^2,-v*F42)", "coefficient": -4 * v, "vertices": [vertex("A", 1), vertex("A", -1), vertex("F42")], "cut": ({0, 1}, {2})},
        {"name": "Cov(|A|^2,v*|A|^2/2)", "coefficient": 8 * v, "vertices": [vertex("A", 1), vertex("A", -1), vertex("A", 1), vertex("A", -1)], "cut": ({0, 1}, {2, 3})},
        {"name": "Cov(|A|^2,E[Q^2]/2)", "coefficient": 32 * v * v, "vertices": [vertex("A", 1), vertex("A", -1), vertex("Q", 1), vertex("Q", -1)], "cut": ({0, 1}, {2, 3})},
    ]


def topology_counts(vertices: list[dict]) -> Counter[tuple[tuple[tuple[int, int], int], ...]]:
    slots = tuple(
        (index, slot)
        for index, item in enumerate(vertices)
        for slot in range(item["degree"] - len(item["fixed"]))
    )
    result: Counter[tuple[tuple[tuple[int, int], int], ...]] = Counter()
    for pairing in pairings(slots):
        adjacency = Counter(tuple(sorted((left[0], right[0]))) for left, right in pairing)
        result[tuple(sorted(adjacency.items()))] += 1
    return result


def topology_edges(signature) -> list[tuple[int, int]]:
    return [edge for edge, count in signature for _ in range(count)]


def crosses_cut(signature, cut) -> bool:
    if cut is None:
        return True
    left, right = cut
    return any(
        count and ((u in left and v in right) or (v in left and u in right))
        for (u, v), count in signature
    )


def forest_structure(vertex_count: int, edges: list[tuple[int, int]]):
    parent = list(range(vertex_count))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    chords = []
    tree = []
    for index, (u, v) in enumerate(edges):
        if u == v:
            chords.append(index)
        else:
            ru, rv = find(u), find(v)
            if ru == rv:
                chords.append(index)
            else:
                parent[rv] = ru
                tree.append(index)
    adjacency = [[] for _ in range(vertex_count)]
    for index in tree:
        u, v = edges[index]
        adjacency[u].append((v, index))
        adjacency[v].append((u, index))
    parents = [-1] * vertex_count
    parent_edge = [-1] * vertex_count
    order = []
    for root in range(vertex_count):
        if parents[root] != -1:
            continue
        parents[root] = root
        stack = [root]
        while stack:
            item = stack.pop()
            order.append(item)
            for other, edge in adjacency[item]:
                if parents[other] == -1:
                    parents[other] = item
                    parent_edge[other] = edge
                    stack.append(other)
    return chords, parents, parent_edge, order


def momentum_solutions(vertex_count: int, edges: list[tuple[int, int]], sources: list[int]):
    chords, parents, parent_edge, order = forest_structure(vertex_count, edges)
    component_sources: dict[int, int] = {}
    for item, source in enumerate(sources):
        root = item
        while parents[root] != root:
            root = parents[root]
        component_sources[root] = ADD[component_sources.get(root, 0)][source]
    if any(source != 0 for source in component_sources.values()):
        return
    if len(chords) > 3:
        raise RuntimeError("unexpected four-loop topology")
    for chord_values in itertools.product(ALLOWED, repeat=len(chords)):
        values = [0] * len(edges)
        balances = list(sources)
        for edge_index, momentum in zip(chords, chord_values):
            values[edge_index] = momentum
            u, v = edges[edge_index]
            if u != v:
                balances[u] = ADD[balances[u]][momentum]
                balances[v] = ADD[balances[v]][NEG[momentum]]
        valid = True
        for item in reversed(order):
            if parents[item] == item:
                if balances[item] != 0:
                    valid = False
                continue
            edge_index = parent_edge[item]
            u, _ = edges[edge_index]
            endpoint = NEG[balances[item]]
            momentum = endpoint if item == u else NEG[endpoint]
            if momentum not in ALLOWED:
                valid = False
                break
            values[edge_index] = momentum
            parent = parents[item]
            balances[parent] = ADD[balances[parent]][balances[item]]
        if valid:
            yield len(chords), values


def evaluate_topology(vertices: list[dict], signature) -> tuple[Fraction, Counter[int]]:
    edges = topology_edges(signature)
    denominator = math.prod(KERNEL_DENOMINATOR[item["degree"]] for item in vertices) * PROPAGATOR_LCM ** len(edges)
    numerator = 0
    loops: Counter[int] = Counter()
    sources = []
    for item in vertices:
        source = 0
        for momentum in item["fixed"]:
            source = ADD[source][momentum]
        sources.append(source)
    for loop_rank, edge_values in momentum_solutions(len(vertices), edges, sources):
        momenta = [list(item["fixed"]) for item in vertices]
        propagator = 1
        for momentum, (u, v) in zip(edge_values, edges):
            momenta[u].append(momentum)
            momenta[v].append(NEG[momentum])
            propagator *= PROPAGATOR_LCM // OMEGA[momentum] ** 2
        kernel = (1, 0)
        for item, values in zip(vertices, momenta):
            total = 0
            for momentum in values:
                total = ADD[total][momentum]
            if total:
                raise AssertionError("momentum conservation failed")
            kernel = gmul(kernel, kernel_numerator(item["degree"], tuple(sorted(values))))
        if kernel[1]:
            raise AssertionError("non-real conjugate-paired term")
        contribution = propagator * kernel[0]
        numerator += contribution
        loops[loop_rank] += contribution
    return Fraction(numerator, denominator), Counter({rank: Fraction(value, denominator) for rank, value in loops.items()})


def evaluate_term(term: dict) -> dict:
    value = Fraction(0)
    loop_values: Counter[int] = Counter()
    topologies = 0
    labeled = 0
    for signature, multiplicity in topology_counts(term["vertices"]).items():
        if not crosses_cut(signature, term["cut"]):
            continue
        topology_value, topology_loops = evaluate_topology(term["vertices"], signature)
        value += multiplicity * topology_value
        for rank, item in topology_loops.items():
            loop_values[rank] += multiplicity * item
        topologies += 1
        labeled += multiplicity
    prefactor = term["coefficient"]
    for item in term["vertices"]:
        prefactor *= item["prefactor"]
    return {
        "name": term["name"],
        "topology_count": topologies,
        "labeled_pairings": labeled,
        "value": value * prefactor,
        "loop_values": {rank: item * prefactor for rank, item in loop_values.items()},
    }


def build() -> dict:
    rows = [evaluate_term(term) for term in terms()]
    total = sum((row["value"] for row in rows), Fraction(0))
    return {
        "result_id": "REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_G4_L4_EXACT_PREFLIGHT_V1",
        "evidence_type": "EXACT_RATIONAL_FULL_PHASE_CONNECTED_WICK_EVALUATION_PREFLIGHT",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lattice": {
            "length": 4,
            "volume": VOLUME,
            "external_momentum": [1, 0, 0, 0],
            "excluded_background_momenta": [[0, 0, 0, 0], [1, 0, 0, 0], [3, 0, 0, 0]],
            "fiber_component_variance": enc(FIBER_VARIANCE),
        },
        "fiber_reduction": {
            "W1": "U30; the isotropic U32 expectation requires either a removed zero background leg or E[zeta^2]=0",
            "W2_modulo_constants": "U40+v*F42-(v/2)*|A|^2-(1/2)*E_fiber[Q^2]",
            "Q": "same-sign two-fiber-leg cubic vertex; E[Q^2] pairs ++ with -- and E[zeta^2*conj(zeta)^2]=8*v^2",
            "connected_families": 8,
        },
        "terms": [
            {
                "name": row["name"],
                "topology_count": row["topology_count"],
                "labeled_pairings": row["labeled_pairings"],
                "value": enc(row["value"]),
                "decimal": float(row["value"]),
                "loop_sectors": [
                    {"loop_rank": rank, "value": enc(value), "decimal": float(value)}
                    for rank, value in sorted(row["loop_values"].items()) if value
                ],
            }
            for row in rows
        ],
        "M4_full": enc(total),
        "M4_full_decimal": float(total),
        "status": "EXACT_PREFLIGHT_REQUIRES_INDEPENDENT_LEDGER_VERIFICATION",
        "does_not_establish": [
            "a certified finite-volume value before independent verification of the two-dimensional fiber ledger",
            "large-volume scaling or a nonperturbative current susceptibility",
            "an interacting H^-1 theorem, continuum, Born, Krein, or Lorentzian physics",
        ],
    }


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    arguments = parser.parse_args()
    encoded = render(build())
    if arguments.stdout:
        print(encoded, end="")
        return 0
    if arguments.check:
        try:
            with open(DATA_PATH, encoding="utf-8") as handle:
                return 0 if handle.read() == encoded else 1
        except OSError:
            return 1
    with open(DATA_PATH, "w", encoding="utf-8") as handle:
        handle.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
