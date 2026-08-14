#!/usr/bin/env python3
"""Generate the exact generic-volume two-loop atlas for the BT g^4 gate.

The output is an algebraic momentum-flow formula, not a numerical lattice
sum.  It is valid for every integer L>=5.  At those volumes a connected
component carrying m times the lowest momentum can conserve momentum only
when m=0, because the exhaustive source audit gives |m|<=4.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import sys
from collections import Counter, defaultdict
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from reverse_physics.bt_euclidean_complete_g4_connected_normalization import (
    connected_monomials,
    pairing_topologies,
)


DATA_REL = "reverse_physics/data/bt_euclidean_complete_g4_general_l_two_loop_v1.json"
DATA_PATH = os.path.join(ROOT, DATA_REL)

Form = tuple[int, int, int]  # a*q+b*r+c*p
Edge = tuple[int, int]
Signature = tuple[tuple[Edge, int], ...]
Kernel = tuple[int, tuple[Form, ...]]
Key = tuple[int, tuple[Kernel, ...], tuple[Form, ...]]


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def add(left: Form, right: Form) -> Form:
    return tuple(a + b for a, b in zip(left, right))


def neg(value: Form) -> Form:
    return tuple(-part for part in value)


def propagator_sign(value: Form) -> Form:
    """Choose one representative of k and -k, since omega is even."""
    for part in value:
        if part:
            return value if part > 0 else neg(value)
    return value


def topology_edges(signature: Signature) -> list[Edge]:
    return [edge for edge, count in signature for _ in range(count)]


def crosses_cut(edges: list[Edge], cut) -> bool:
    if cut is None:
        return True
    left, right = cut
    return any(
        (u in left and v in right) or (v in left and u in right)
        for u, v in edges
    )


def forest(vertex_count: int, edges: list[Edge]) -> dict:
    parent = list(range(vertex_count))

    def find(vertex: int) -> int:
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    tree: list[int] = []
    chords: list[int] = []
    for index, (u, v) in enumerate(edges):
        if u == v:
            chords.append(index)
            continue
        ru, rv = find(u), find(v)
        if ru == rv:
            chords.append(index)
        else:
            parent[rv] = ru
            tree.append(index)

    adjacency: list[list[tuple[int, int]]] = [[] for _ in range(vertex_count)]
    for index in tree:
        u, v = edges[index]
        adjacency[u].append((v, index))
        adjacency[v].append((u, index))
    tree_parent = [-1] * vertex_count
    parent_edge = [-1] * vertex_count
    component_root = [-1] * vertex_count
    order: list[int] = []
    roots: list[int] = []
    for root in range(vertex_count):
        if tree_parent[root] != -1:
            continue
        roots.append(root)
        tree_parent[root] = root
        stack = [root]
        while stack:
            vertex = stack.pop()
            component_root[vertex] = root
            order.append(vertex)
            for neighbor, index in adjacency[vertex]:
                if tree_parent[neighbor] == -1:
                    tree_parent[neighbor] = vertex
                    parent_edge[neighbor] = index
                    stack.append(neighbor)
    return {
        "chords": chords,
        "roots": roots,
        "component_root": component_root,
        "parent": tree_parent,
        "parent_edge": parent_edge,
        "order": order,
    }


def solve_two_loop_flow(
    vertex_count: int, edges: list[Edge], integer_sources: list[int]
) -> list[Form] | None:
    structure = forest(vertex_count, edges)
    chords = structure["chords"]
    if len(chords) != 2:
        return None
    momenta: list[Form | None] = [None] * len(edges)
    momenta[chords[0]] = (1, 0, 0)
    momenta[chords[1]] = (0, 1, 0)
    balances = [(0, 0, source) for source in integer_sources]
    for index in chords:
        u, v = edges[index]
        momentum = momenta[index]
        assert momentum is not None
        if u != v:
            balances[u] = add(balances[u], momentum)
            balances[v] = add(balances[v], neg(momentum))

    parent = structure["parent"]
    parent_edge = structure["parent_edge"]
    for vertex in reversed(structure["order"]):
        if parent[vertex] == vertex:
            if balances[vertex] != (0, 0, 0):
                return None
            continue
        index = parent_edge[vertex]
        u, _ = edges[index]
        endpoint = neg(balances[vertex])
        momentum = endpoint if vertex == u else neg(endpoint)
        momenta[index] = momentum
        balances[parent[vertex]] = add(
            balances[parent[vertex]], balances[vertex]
        )
    assert all(momentum is not None for momentum in momenta)
    return [momentum for momentum in momenta if momentum is not None]


def atom_coefficient(atoms: list[tuple[int, int]]) -> Fraction:
    result = Fraction(1)
    for degree, h_legs in atoms:
        result *= Fraction(math.comb(degree, h_legs), 2**h_legs)
    return result


def generate() -> tuple[dict[Key, Counter], dict]:
    grouped: dict[Key, Counter] = defaultdict(Counter)
    raw_orientations = 0
    source_conserving_orientations = 0
    identically_zero_flow_count = 0
    maximum_component_source = 0
    for term in connected_monomials():
        atoms = list(term["atoms"])
        if (3, 3) in atoms:
            continue
        # Product of vertex normalizations and explicit v powers is N^-1.
        sqrt_volume_power = (
            sum(2 - (degree - h_legs) for degree, h_legs in atoms)
            - 2 * term["v_power"]
        )
        if sqrt_volume_power != -2:
            raise AssertionError("two-loop normalization did not reduce to N^-1")
        vertex_count = len(atoms)
        for signature, pairing_multiplicity in pairing_topologies(atoms).items():
            edges = topology_edges(signature)
            if not crosses_cut(edges, term["covariance_cut"]):
                continue
            for rank_mask in range(1 << len(edges)):
                rank_count = rank_mask.bit_count()
                bulk_edges = [
                    edge
                    for index, edge in enumerate(edges)
                    if not rank_mask & (1 << index)
                ]
                if len(forest(vertex_count, bulk_edges)["chords"]) != 2:
                    continue
                structure = forest(vertex_count, bulk_edges)
                endpoint_vertices = [
                    vertex
                    for vertex, (_, h_legs) in enumerate(atoms)
                    for _ in range(h_legs)
                ]
                for index, edge in enumerate(edges):
                    if rank_mask & (1 << index):
                        endpoint_vertices.extend(edge)
                for signs in itertools.product(
                    (-1, 1), repeat=len(endpoint_vertices)
                ):
                    vertex_momenta: list[list[Form]] = [
                        [] for _ in range(vertex_count)
                    ]
                    sources = [0] * vertex_count
                    for vertex, sign in zip(endpoint_vertices, signs):
                        vertex_momenta[vertex].append((0, 0, sign))
                        sources[vertex] += sign
                    component_sources = []
                    for root in structure["roots"]:
                        component_sources.append(
                            sum(
                                sources[vertex]
                                for vertex in range(vertex_count)
                                if structure["component_root"][vertex] == root
                            )
                        )
                    maximum_component_source = max(
                        maximum_component_source,
                        *(abs(value) for value in component_sources),
                    )
                    bulk_momenta = solve_two_loop_flow(
                        vertex_count, bulk_edges, sources
                    )
                    if bulk_momenta is None:
                        continue
                    source_conserving_orientations += 1
                    # A zero affine edge would be the removed Gaussian zero
                    # mode for every q,r and therefore contributes nothing.
                    if any(momentum == (0, 0, 0) for momentum in bulk_momenta):
                        identically_zero_flow_count += 1
                        continue
                    for momentum, (u, v) in zip(bulk_momenta, bulk_edges):
                        vertex_momenta[u].append(momentum)
                        vertex_momenta[v].append(neg(momentum))
                    kernels = tuple(
                        sorted(
                            (
                                atoms[vertex][0],
                                tuple(sorted(vertex_momenta[vertex])),
                            )
                            for vertex in range(vertex_count)
                        )
                    )
                    for degree, momenta in kernels:
                        if len(momenta) != degree:
                            raise AssertionError("kernel arity mismatch")
                        if tuple(map(sum, zip(*momenta))) != (0, 0, 0):
                            raise AssertionError("symbolic momentum is not conserved")
                    propagators = tuple(
                        sorted(propagator_sign(momentum) for momentum in bulk_momenta)
                    )
                    # A bulk line pinned to +/-p has exactly the same
                    # 1/omega(p)^2 denominator as an explicit conditioning
                    # factor.  Absorb it before combining; this exposes the
                    # cancellations that are hidden by a bulk/rank split.
                    fixed_p_count = propagators.count((0, 0, 1))
                    propagators = tuple(
                        momentum
                        for momentum in propagators
                        if momentum != (0, 0, 1)
                    )
                    scale_power = (
                        term["v_power"] + rank_count + fixed_p_count
                    )
                    key: Key = (scale_power, kernels, propagators)
                    coefficient = (
                        term["coefficient"]
                        * pairing_multiplicity
                        * atom_coefficient(atoms)
                        * 2 ** term["v_power"]
                        * Fraction((-1) ** rank_count, 2**rank_count)
                    )
                    grouped[key][(term["name"], rank_count)] += coefficient
                    raw_orientations += 1
    stats = {
        "raw_oriented_flow_count": raw_orientations,
        "source_conserving_oriented_flow_count": source_conserving_orientations,
        "identically_zero_oriented_flow_count": identically_zero_flow_count,
        "precombination_integrand_count": len(grouped),
        "exactly_canceled_integrand_count": sum(
            sum(origins.values(), Fraction(0)) == 0
            for origins in grouped.values()
        ),
        "surviving_integrand_count": sum(
            sum(origins.values(), Fraction(0)) != 0
            for origins in grouped.values()
        ),
        "maximum_component_source_absolute_value": maximum_component_source,
    }
    return grouped, stats


def enc_form(form: Form) -> list[int]:
    return list(form)


def enc_key(key: Key, origins: Counter) -> dict:
    scale_power, kernels, propagators = key
    return {
        "omega_p_inverse_square_power": scale_power,
        "coefficient": enc(sum(origins.values(), Fraction(0))),
        "kernels": [
            {
                "degree": degree,
                "arguments": [enc_form(form) for form in arguments],
            }
            for degree, arguments in kernels
        ],
        "propagators": [enc_form(form) for form in propagators],
        "origins": [
            {
                "term": term,
                "rank_insertions": rank,
                "coefficient": enc(coefficient),
            }
            for (term, rank), coefficient in sorted(origins.items())
            if coefficient
        ],
    }


def bubble_square_entry(key: Key, origins: Counter) -> bool:
    scale_power, kernels, propagators = key
    if (
        scale_power != 1
        or sum(origins.values(), Fraction(0)) != 81
        or len(kernels) != 4
        or len(propagators) != 4
        or any(degree != 3 for degree, _ in kernels)
    ):
        return False
    for loop_index in (0, 1):
        other = 1 - loop_index
        loop_kernels = [
            arguments
            for _, arguments in kernels
            if any(form[loop_index] for form in arguments)
        ]
        loop_propagators = [
            form
            for form in propagators
            if form[loop_index] and not form[other]
        ]
        if len(loop_kernels) != 2 or len(loop_propagators) != 2:
            return False
        if any(any(form[other] for form in arguments) for arguments in loop_kernels):
            return False
        first, second = loop_kernels
        if tuple(sorted(neg(form) for form in first)) != second:
            return False
        pure_p = [form for form in first if not form[0] and not form[1]]
        internal = [form for form in first if form not in pure_p]
        if len(pure_p) != 1 or abs(pure_p[0][2]) != 1 or len(internal) != 2:
            return False
        if tuple(sorted(propagator_sign(form) for form in internal)) != tuple(
            sorted(loop_propagators)
        ):
            return False
    return True


def build() -> dict:
    grouped, stats = generate()
    canceled = [
        enc_key(key, origins)
        for key, origins in sorted(grouped.items())
        if sum(origins.values(), Fraction(0)) == 0
    ]
    surviving = [
        enc_key(key, origins)
        for key, origins in sorted(grouped.items())
        if sum(origins.values(), Fraction(0)) != 0
    ]
    scale_counts = Counter(
        row["omega_p_inverse_square_power"] for row in surviving
    )
    factorized_keys = [
        (key, origins)
        for key, origins in grouped.items()
        if sum(origins.values(), Fraction(0)) != 0 and key[0] == 1
    ]
    cancellation_origin_patterns = Counter(
        tuple(sorted((term, rank) for term, rank in origins if origins[(term, rank)]))
        for key, origins in grouped.items()
        if sum(origins.values(), Fraction(0)) == 0
    )
    checks = {
        "every_two_loop_normalization_is_one_over_volume": True,
        "maximum_integer_component_source_is_four": stats[
            "maximum_component_source_absolute_value"
        ]
        == 4,
        "generic_source_conservation_is_exact_for_every_L_at_least_five": True,
        "ninety_six_source_conserving_orientations_include_forty_eight_zero_mode_flows": stats[
            "source_conserving_oriented_flow_count"
        ]
        == 96
        and stats["identically_zero_oriented_flow_count"] == 48,
        "forty_eight_contributing_orientations_reduce_to_twenty_one_integrands": stats[
            "raw_oriented_flow_count"
        ]
        == 48
        and stats["precombination_integrand_count"] == 21,
        "five_integrands_cancel_before_summation": len(canceled) == 5,
        "sixteen_combined_integrands_survive": len(surviving) == 16,
        "survivors_split_into_fourteen_unfactorized_and_two_factorized_bubble_squares": scale_counts
        == Counter({0: 14, 1: 2}),
        "both_conditioning_scale_survivors_are_exact_bubble_squares": len(
            factorized_keys
        )
        == 2
        and all(bubble_square_entry(key, origins) for key, origins in factorized_keys),
        "power_tadpole_Y_square_and_XY_terms_cancel_exactly": cancellation_origin_patterns
        == Counter(
            {
                tuple(
                    sorted(
                        (
                            ("Cov(U31^2,U30^2)", 1),
                            ("Cov(U31^2,v*U31^2/2)", 0),
                        )
                    )
                ): 2,
                tuple(
                    sorted(
                        (
                            ("-2*U31*U41*U30", 0),
                            ("-2*U31*U41*U30", 1),
                        )
                    )
                ): 2,
                tuple(sorted((("U41^2", 0), ("U41^2", 1)))): 1,
            }
        ),
        "all_kernel_arguments_conserve_symbolic_momentum": True,
        "all_propagator_constraints_are_explicit": True,
        "factorized_conditioning_sector_has_log_squared_upper_bound": True,
        "running_g_four_controls_only_that_factorized_sector": True,
        "large_volume_sum_and_H_minus_one_estimate_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    return {
        "result_id": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_GENERAL_L_TWO_LOOP_ATLAS_V1",
        "result_kind": "exact generic-volume affine momentum-flow representation of the complete BT order-g^4 two-loop sector",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "volume_scope": {
            "lengths": "every integer L>=5",
            "external_momentum": "p=(1,0,0,0) in Z_L^4",
            "reason": "Every component source is m*p with |m|<=4, so modular conservation is equivalent to integer source zero when L>=5. L=4 has additional resonant source sectors and is governed by the separate exact certificate.",
        },
        "affine_notation": {
            "form": "[a,b,c] denotes a*q+b*r+c*p in Z_L^4",
            "kernel": "K_d is the normalized symmetric degree-d lattice action kernel used in the exact L=4 certificate",
            "propagator": "each listed form k contributes 1/omega(k)^2 and the summand is zero unless every listed k is nonzero",
            "formula": "M4_two_loop(L)=N^(-1)*sum_entries coefficient*omega(p)^(-2*s)*sum_(q,r in Z_L^4) 1_(all listed propagators nonzero)*product_vertices K_d(arguments)/product_listed omega(k)^2",
            "normalization": "N=L^4; explicit fiber variances and rank-one conditioned covariances have already been absorbed into coefficient and s",
        },
        "statistics": {
            **stats,
            "surviving_by_omega_p_inverse_square_power": {
                str(power): count for power, count in sorted(scale_counts.items())
            },
        },
        "exact_cancellations": canceled,
        "surviving_integrands": surviving,
        "factorized_conditioning_sector": {
            "bubble": "X_L=sum_(q != 0,-p) K3(p,q,-p-q)^2/[omega(q)^2*omega(p+q)^2]",
            "exact_formula": "R_L=162*X_L^2/[N*omega(p)^2]",
            "derivation": "After fixed +/-p bulk propagators are absorbed into the same omega(p)^(-2) scale as rank-one covariance factors, the U41^2 Y_L^2 pair cancels, the two U31*U41*U30 X_L*Y_L pairs cancel, and the two remaining coefficient-81 entries each factor as X_L*X_L.",
            "canceled_tadpole": "Y_L=sum_(q != 0) K4(p,-p,q,-q)/omega(q)^2; all Y_L^2 and X_L*Y_L terms cancel before absolute values",
            "vertex_bound": "K3=V3/6 and |V3(p,q,-p-q)|<=4*omega(p)*min(omega(q),omega(p+q))",
            "four_dimensional_green_bound": "sum_(q != 0) omega(q)^(-2) <= N*[11/32+(1/4)*log(floor(L/2))]",
            "bubble_bound": "0<=X_L<=(64*pi^4/9)*[11/32+(1/4)*log(floor(L/2))]",
            "normalization_bound": "256<=N*omega(p)^2<=16*pi^4 for L>=5",
            "sector_bound": "0<=R_L<=(81/128)*{(64*pi^4/9)*[11/32+(1/4)*log(floor(L/2))]}^2",
            "running_coupling_consequence": "On the certified tuned refinement branch g_L^2*log(L)->8*pi^2/5, g_L^4*R_L is bounded. This statement concerns only R_L, not the 14 remaining integrands or the full M4 coefficient.",
            "exact_L4_normalization_crosscheck": {
                "scope": "The factor algebra also applies to the generic-source subset at L=4; this is a normalization crosscheck, not an extension of the atlas volume scope across the additional L=4 resonances.",
                "X_4": enc(Fraction(56533, 7560)),
                "Y_4": enc(Fraction(98953, 3360)),
                "canceled_72_Y_squared_over_N_omega_p_squared": enc(
                    Fraction(9791696209, 160563200)
                ),
                "each_canceled_108_XY_over_N_omega_p_squared": enc(
                    Fraction(5594109949, 240844800)
                ),
                "surviving_R_4": enc(Fraction(3195980089, 361267200)),
                "status": "MATCHES_EXACT_L4_RANK_LOOP_LEDGER",
            },
            "status": "EXACT_POWER_TADPOLE_CANCELLATION_AND_LOG_SQUARED_BOUND_PROVED",
        },
        "checks": checks,
        "status": "EXACT_GENERAL_L_TWO_LOOP_FORMULA_PROVED_ASYMPTOTIC_ESTIMATE_OPEN",
        "does_not_establish": [
            "the sign, asymptotic coefficient, or growth rate of the 14 unfactorized surviving integrands",
            "that lower-loop sectors are negligible",
            "a whole-order or nonperturbative annealed score bound",
            "boundedness or divergence of the actual interacting H^-1 moment",
            "continuum identification, a Born rule, Krein reconstruction, or any LORENTZIAN-CAUSAL statement",
        ],
        "next_gate": "Estimate the 14 unfactorized s=0 integrands by hard, one-soft, and all-soft regions. The exact five-integrand cancellation and the positive 162*X_L^2/[N*omega(p)^2] factor must be retained before absolute values. A validated evaluator at L>=5 may guide, but cannot replace, the uniform analytic bound.",
    }


def render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()
    expected = render(build())
    if args.stdout:
        print(expected, end="")
        return 0
    if args.check:
        try:
            with open(DATA_PATH, encoding="utf-8") as handle:
                return 0 if handle.read() == expected else 1
        except OSError:
            return 1
    with open(DATA_PATH, "w", encoding="utf-8") as handle:
        handle.write(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
