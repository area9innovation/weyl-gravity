#!/usr/bin/env python3
"""Exact low-memory L=4 evaluation of the connected BT g^4 coefficient.

The calculation groups labeled Wick pairings by multigraph topology.  Each
conditioned covariance is expanded into its translation-invariant propagator
and the real-cosine rank-one subtraction.  Momentum conservation leaves at
most two freely summed Z_4^4 momenta.  All arithmetic is rational/Gaussian
integer arithmetic; no floating point enters the result.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import sys
from collections import Counter
from fractions import Fraction
from functools import lru_cache

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from reverse_physics.bt_euclidean_complete_g4_connected_normalization import (
    connected_monomials,
    eta_degree,
    pairings,
)


DATA_REL = "reverse_physics/data/bt_euclidean_complete_g4_l4_exact_v1.json"
DATA_PATH = os.path.join(ROOT, DATA_REL)

LENGTH = 4
VOLUME = LENGTH**4
SQRT_VOLUME = 16
P = 1  # (1,0,0,0) in the base-four encoding below
MINUS_P = 3
OMEGA_P = 2
FIBER_VARIANCE = Fraction(2, VOLUME * OMEGA_P**2)


def coords(momentum: int) -> tuple[int, int, int, int]:
    return tuple((momentum >> (2 * axis)) & 3 for axis in range(4))


COORDS = tuple(coords(momentum) for momentum in range(VOLUME))


def encode(parts: tuple[int, int, int, int]) -> int:
    return sum((part & 3) << (2 * axis) for axis, part in enumerate(parts))


NEG = tuple(encode(tuple(-part for part in COORDS[q])) for q in range(VOLUME))
ADD = tuple(
    tuple(
        encode(tuple(a + b for a, b in zip(COORDS[left], COORDS[right])))
        for right in range(VOLUME)
    )
    for left in range(VOLUME)
)
OMEGA = tuple(
    sum((0, 2, 4, 2)[component] for component in COORDS[q])
    for q in range(VOLUME)
)
PROPAGATOR_LCM = math.lcm(*(value * value for value in OMEGA if value))

GaussianInteger = tuple[int, int]


def gadd(left: GaussianInteger, right: GaussianInteger) -> GaussianInteger:
    return left[0] + right[0], left[1] + right[1]


def gmul(left: GaussianInteger, right: GaussianInteger) -> GaussianInteger:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


PHASES: tuple[GaussianInteger, ...] = ((1, 0), (0, 1), (-1, 0), (0, -1))


@lru_cache(maxsize=200_000)
def b_symbol(momentums: tuple[int, ...]) -> GaussianInteger:
    result = (0, 0)
    for axis in range(4):
        for direction in (-1, 1):
            product = (1, 0)
            for momentum in momentums:
                phase = PHASES[(direction * COORDS[momentum][axis]) & 3]
                product = gmul(product, (phase[0] - 1, phase[1]))
            result = gadd(result, product)
    return result


def partitions_four() -> tuple[tuple[tuple[int, int], tuple[int, int]], ...]:
    return (
        ((0, 1), (2, 3)),
        ((0, 2), (1, 3)),
        ((0, 3), (1, 2)),
    )


@lru_cache(maxsize=200_000)
def kernel_numerator(degree: int, sorted_momenta: tuple[int, ...]) -> GaussianInteger:
    momenta = sorted_momenta
    if len(momenta) != degree:
        raise ValueError("kernel arity mismatch")
    if degree == 3:
        result = (0, 0)
        for index in range(3):
            rest = tuple(momenta[j] for j in range(3) if j != index)
            result = gadd(result, gmul(b_symbol((momenta[index],)), b_symbol(tuple(sorted(rest)))))
        return result
    if degree == 4:
        result = (0, 0)
        for index in range(4):
            rest = tuple(momenta[j] for j in range(4) if j != index)
            result = gadd(result, gmul(b_symbol((momenta[index],)), b_symbol(tuple(sorted(rest)))))
        for left, right in partitions_four():
            result = gadd(
                result,
                gmul(
                    b_symbol(tuple(sorted(momenta[j] for j in left))),
                    b_symbol(tuple(sorted(momenta[j] for j in right))),
                ),
            )
        return result
    if degree == 5:
        result = (0, 0)
        for index in range(5):
            rest = tuple(momenta[j] for j in range(5) if j != index)
            result = gadd(result, gmul(b_symbol((momenta[index],)), b_symbol(tuple(sorted(rest)))))
        for left in itertools.combinations(range(5), 2):
            left_set = set(left)
            right = tuple(index for index in range(5) if index not in left_set)
            result = gadd(
                result,
                gmul(
                    b_symbol(tuple(sorted(momenta[j] for j in left))),
                    b_symbol(tuple(sorted(momenta[j] for j in right))),
                ),
            )
        return result
    raise ValueError(f"unsupported degree {degree}")


KERNEL_DENOMINATOR = {3: 6, 4: 24, 5: 120}


def atom_prefactor(atom: tuple[int, int]) -> Fraction:
    degree, h_legs = atom
    eta_legs = degree - h_legs
    volume_power = 2 - eta_legs
    if volume_power >= 0:
        normalization = Fraction(SQRT_VOLUME**volume_power)
    else:
        normalization = Fraction(1, SQRT_VOLUME ** (-volume_power))
    return Fraction(math.comb(degree, h_legs), 2**h_legs) * normalization


def topology_counts(atoms: list[tuple[int, int]]) -> Counter[tuple[tuple[tuple[int, int], int], ...]]:
    slots = tuple(
        (vertex, slot)
        for vertex, atom in enumerate(atoms)
        for slot in range(eta_degree(atom))
    )
    result: Counter[tuple[tuple[tuple[int, int], int], ...]] = Counter()
    for pairing in pairings(slots):
        adjacency = Counter(tuple(sorted((left[0], right[0]))) for left, right in pairing)
        result[tuple(sorted(adjacency.items()))] += 1
    return result


def topology_edges(signature: tuple[tuple[tuple[int, int], int], ...]) -> list[tuple[int, int]]:
    return [edge for edge, count in signature for _ in range(count)]


def crosses_cut(signature, cut) -> bool:
    if cut is None:
        return True
    left, right = cut
    return any(
        count and ((u in left and v in right) or (v in left and u in right))
        for (u, v), count in signature
    )


def external_choices(atom: tuple[int, int]):
    _, h_legs = atom
    for plus in range(h_legs + 1):
        momenta = (P,) * plus + (MINUS_P,) * (h_legs - plus)
        total = 0
        for momentum in momenta:
            total = ADD[total][momentum]
        yield momenta, total, math.comb(h_legs, plus)


def rank_endpoint_choices(edge: tuple[int, int]):
    u, v = edge
    if u != v:
        for left in (P, MINUS_P):
            for right in (P, MINUS_P):
                yield left, right, 1
        return
    yield P, P, 1
    yield P, MINUS_P, 2
    yield MINUS_P, MINUS_P, 1


def forest_structure(vertex_count: int, bulk_edges: list[tuple[int, int]]):
    parent = list(range(vertex_count))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    tree_indices: list[int] = []
    chord_indices: list[int] = []
    for index, (u, v) in enumerate(bulk_edges):
        if u == v:
            chord_indices.append(index)
            continue
        ru, rv = find(u), find(v)
        if ru == rv:
            chord_indices.append(index)
        else:
            parent[rv] = ru
            tree_indices.append(index)

    adjacency = [[] for _ in range(vertex_count)]
    for index in tree_indices:
        u, v = bulk_edges[index]
        adjacency[u].append((v, index))
        adjacency[v].append((u, index))

    roots: list[int] = []
    tree_parent = [-1] * vertex_count
    parent_edge = [-1] * vertex_count
    order: list[int] = []
    for root in range(vertex_count):
        if tree_parent[root] != -1:
            continue
        roots.append(root)
        tree_parent[root] = root
        stack = [root]
        while stack:
            vertex = stack.pop()
            order.append(vertex)
            for neighbor, edge_index in adjacency[vertex]:
                if tree_parent[neighbor] == -1:
                    tree_parent[neighbor] = vertex
                    parent_edge[neighbor] = edge_index
                    stack.append(neighbor)
    return tree_indices, chord_indices, roots, tree_parent, parent_edge, order


def bulk_solutions(vertex_count: int, bulk_edges: list[tuple[int, int]], sources: list[int]):
    _, chord_indices, roots, tree_parent, parent_edge, order = forest_structure(vertex_count, bulk_edges)
    if len(chord_indices) > 2:
        return
    nonzero = range(1, VOLUME)
    for chord_values in itertools.product(nonzero, repeat=len(chord_indices)):
        edge_momenta = [0] * len(bulk_edges)
        balances = list(sources)
        for edge_index, momentum in zip(chord_indices, chord_values):
            edge_momenta[edge_index] = momentum
            u, v = bulk_edges[edge_index]
            if u != v:
                balances[u] = ADD[balances[u]][momentum]
                balances[v] = ADD[balances[v]][NEG[momentum]]
        valid = True
        for vertex in reversed(order):
            if tree_parent[vertex] == vertex:
                if balances[vertex] != 0:
                    valid = False
                continue
            edge_index = parent_edge[vertex]
            u, v = bulk_edges[edge_index]
            endpoint_at_child = NEG[balances[vertex]]
            momentum = endpoint_at_child if vertex == u else NEG[endpoint_at_child]
            if momentum == 0:
                valid = False
                break
            edge_momenta[edge_index] = momentum
            parent_vertex = tree_parent[vertex]
            balances[parent_vertex] = ADD[balances[parent_vertex]][balances[vertex]]
        if valid:
            yield len(chord_indices), edge_momenta


def evaluate_topology(atoms: list[tuple[int, int]], signature) -> tuple[Fraction, dict]:
    edges = topology_edges(signature)
    edge_count = len(edges)
    vertex_count = len(atoms)
    kernel_denominator = math.prod(KERNEL_DENOMINATOR[degree] for degree, _ in atoms)
    common_denominator = kernel_denominator * PROPAGATOR_LCM**edge_count
    numerator = 0
    sector_numerators: Counter[tuple[int, int]] = Counter()

    external_products = itertools.product(*(tuple(external_choices(atom)) for atom in atoms))
    for external in external_products:
        base_momenta = [list(choice[0]) for choice in external]
        base_sources = [choice[1] for choice in external]
        external_multiplicity = math.prod(choice[2] for choice in external)
        for rank_mask in range(1 << edge_count):
            rank_indices = [index for index in range(edge_count) if rank_mask & (1 << index)]
            bulk_indices = [index for index in range(edge_count) if not rank_mask & (1 << index)]
            bulk_edges = [edges[index] for index in bulk_indices]
            rank_options = [tuple(rank_endpoint_choices(edges[index])) for index in rank_indices]
            for rank_assignment in itertools.product(*rank_options):
                vertex_momenta = [list(items) for items in base_momenta]
                sources = list(base_sources)
                rank_multiplicity = 1
                for edge_index, assignment in zip(rank_indices, rank_assignment):
                    left, right, multiplicity = assignment
                    u, v = edges[edge_index]
                    vertex_momenta[u].append(left)
                    vertex_momenta[v].append(right)
                    sources[u] = ADD[sources[u]][left]
                    sources[v] = ADD[sources[v]][right]
                    rank_multiplicity *= multiplicity
                for loop_rank, bulk_momenta in bulk_solutions(vertex_count, bulk_edges, sources):
                    momenta = [list(items) for items in vertex_momenta]
                    propagator_scale = 1
                    for momentum, (u, v) in zip(bulk_momenta, bulk_edges):
                        momenta[u].append(momentum)
                        momenta[v].append(NEG[momentum])
                        propagator_scale *= PROPAGATOR_LCM // (OMEGA[momentum] ** 2)
                    for edge_index in rank_indices:
                        propagator_scale *= -(PROPAGATOR_LCM // (2 * OMEGA_P**2))
                    kernel_product = (1, 0)
                    for atom, vertex_values in zip(atoms, momenta):
                        if len(vertex_values) != atom[0]:
                            raise AssertionError("vertex leg count mismatch")
                        total = 0
                        for momentum in vertex_values:
                            total = ADD[total][momentum]
                        if total != 0:
                            raise AssertionError("vertex momentum is not conserved")
                        kernel_product = gmul(
                            kernel_product,
                            kernel_numerator(atom[0], tuple(sorted(vertex_values))),
                        )
                    if kernel_product[1] != 0:
                        raise AssertionError("complete topology has a non-real kernel product")
                    contribution = (
                        external_multiplicity
                        * rank_multiplicity
                        * propagator_scale
                        * kernel_product[0]
                    )
                    numerator += contribution
                    sector_numerators[(len(rank_indices), loop_rank)] += contribution
    return (
        Fraction(numerator, common_denominator),
        {
            sector: Fraction(value, common_denominator)
            for sector, value in sector_numerators.items()
        },
    )


def evaluate_term(term: dict) -> dict:
    atoms = list(term["atoms"])
    if (3, 3) in atoms:
        return {
            "name": term["name"],
            "topology_count": 0,
            "labeled_pairings": 0,
            "value": Fraction(0),
            "reason": "U33_IS_ZERO",
        }
    total = Fraction(0)
    sectors: Counter[tuple[int, int]] = Counter()
    topologies = 0
    labeled = 0
    for signature, multiplicity in topology_counts(atoms).items():
        if not crosses_cut(signature, term["covariance_cut"]):
            continue
        value, topology_sectors = evaluate_topology(atoms, signature)
        total += multiplicity * value
        for sector, sector_value in topology_sectors.items():
            sectors[sector] += multiplicity * sector_value
        topologies += 1
        labeled += multiplicity
    prefactor = math.prod(atom_prefactor(atom) for atom in atoms)
    outer = term["coefficient"] * FIBER_VARIANCE ** term["v_power"] * prefactor
    total *= outer
    sectors = {sector: value * outer for sector, value in sectors.items()}
    return {
        "name": term["name"],
        "topology_count": topologies,
        "labeled_pairings": labeled,
        "value": total,
        "sectors": sectors,
        "reason": "EXACT_CONDITIONED_WICK_SUM",
    }


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def build() -> dict:
    rows = [evaluate_term(term) for term in connected_monomials()]
    total = sum((row["value"] for row in rows), Fraction(0))
    return {
        "result_id": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_L4_EXACT_PREFLIGHT_V1",
        "evidence_type": "EXACT_RATIONAL_CONDITIONED_GAUSSIAN_WICK_EVALUATION",
        "created": "2026-08-14",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "lattice": {
            "length": LENGTH,
            "volume": VOLUME,
            "external_momentum": [1, 0, 0, 0],
            "external_dispersion": OMEGA_P,
            "fiber_variance": enc(FIBER_VARIANCE),
            "propagator_denominator_lcm": PROPAGATOR_LCM,
        },
        "normalization": "phi_x=N^(-1/2)*sum_k z_k exp(i*k*x); K3=V3/6, K4 as certified, K5 from S3=a*d/24+b*c/12",
        "terms": [
            {
                "name": row["name"],
                "topology_count": row["topology_count"],
                "labeled_pairings": row["labeled_pairings"],
                "value": enc(row["value"]),
                "decimal": float(row["value"]),
                "rank_loop_sectors": [
                    {
                        "rank_insertions": rank,
                        "loop_rank": loop,
                        "value": enc(value),
                        "decimal": float(value),
                    }
                    for (rank, loop), value in sorted(row.get("sectors", {}).items())
                    if value
                ],
                "reason": row["reason"],
            }
            for row in rows
        ],
        "M4": enc(total),
        "M4_decimal": float(total),
        "status": "EXACT_PREFLIGHT_NOT_YET_INDEPENDENTLY_VERIFIED",
        "does_not_establish": [
            "an all-volume cancellation or asymptotic scaling law",
            "a nonperturbative score or interacting H^-1 estimate",
            "continuum, Born, Krein, or Lorentzian physics",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()
    encoded = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.stdout:
        print(encoded, end="")
        return 0
    if args.check:
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
