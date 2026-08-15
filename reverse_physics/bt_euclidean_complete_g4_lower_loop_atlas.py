#!/usr/bin/env python3
"""Generate the missing zero- and one-loop BT complete-g4 affine atlas."""

from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from collections import Counter, defaultdict
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from reverse_physics.bt_euclidean_complete_g4_connected_normalization import (  # noqa: E402
    connected_monomials,
    pairing_topologies,
)
from reverse_physics.bt_euclidean_complete_g4_general_l_two_loop import (  # noqa: E402
    add,
    atom_coefficient,
    crosses_cut,
    forest,
    neg,
    propagator_sign,
    topology_edges,
)


DATA_REL = "reverse_physics/data/bt_euclidean_complete_g4_lower_loop_atlas_v1.json"
DATA_PATH = os.path.join(ROOT, DATA_REL)
Form = tuple[int, int, int]
Key = tuple[int, int, tuple, tuple]


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def solve_flow(
    vertex_count: int,
    edges: list[tuple[int, int]],
    integer_sources: list[int],
    loop_rank: int,
) -> list[Form] | None:
    structure = forest(vertex_count, edges)
    chords = structure["chords"]
    if len(chords) != loop_rank:
        return None
    momenta: list[Form | None] = [None] * len(edges)
    for loop_index, edge_index in enumerate(chords):
        basis = [0, 0, 0]
        basis[loop_index] = 1
        momenta[edge_index] = tuple(basis)
    balances = [(0, 0, source) for source in integer_sources]
    for edge_index in chords:
        u, v = edges[edge_index]
        momentum = momenta[edge_index]
        assert momentum is not None
        if u != v:
            balances[u] = add(balances[u], momentum)
            balances[v] = add(balances[v], neg(momentum))
    for vertex in reversed(structure["order"]):
        if structure["parent"][vertex] == vertex:
            if balances[vertex] != (0, 0, 0):
                return None
            continue
        edge_index = structure["parent_edge"][vertex]
        u, _ = edges[edge_index]
        endpoint = neg(balances[vertex])
        momentum = endpoint if vertex == u else neg(endpoint)
        momenta[edge_index] = momentum
        parent = structure["parent"][vertex]
        balances[parent] = add(balances[parent], balances[vertex])
    assert all(momentum is not None for momentum in momenta)
    return [momentum for momentum in momenta if momentum is not None]


def generate_rank(loop_rank: int) -> tuple[dict[Key, Counter], dict]:
    grouped: dict[Key, Counter] = defaultdict(Counter)
    candidate_orientations = 0
    source_conserving_orientations = 0
    identically_zero_flows = 0
    contributing_orientations = 0
    maximum_component_source = 0
    for term in connected_monomials():
        atoms = list(term["atoms"])
        if (3, 3) in atoms:
            continue
        vertex_count = len(atoms)
        for signature, pairing_multiplicity in pairing_topologies(atoms).items():
            edges = topology_edges(signature)
            if not crosses_cut(edges, term["covariance_cut"]):
                continue
            for rank_mask in range(1 << len(edges)):
                rank_insertions = rank_mask.bit_count()
                bulk_edges = [
                    edge
                    for index, edge in enumerate(edges)
                    if not rank_mask & (1 << index)
                ]
                structure = forest(vertex_count, bulk_edges)
                if len(structure["chords"]) != loop_rank:
                    continue
                endpoint_vertices = [
                    vertex
                    for vertex, (_, h_legs) in enumerate(atoms)
                    for _ in range(h_legs)
                ]
                for index, edge in enumerate(edges):
                    if rank_mask & (1 << index):
                        endpoint_vertices.extend(edge)
                for signs in itertools.product((-1, 1), repeat=len(endpoint_vertices)):
                    candidate_orientations += 1
                    vertex_momenta: list[list[Form]] = [
                        [] for _ in range(vertex_count)
                    ]
                    sources = [0] * vertex_count
                    for vertex, sign in zip(endpoint_vertices, signs):
                        vertex_momenta[vertex].append((0, 0, sign))
                        sources[vertex] += sign
                    component_sources = [
                        sum(
                            sources[vertex]
                            for vertex in range(vertex_count)
                            if structure["component_root"][vertex] == root
                        )
                        for root in structure["roots"]
                    ]
                    maximum_component_source = max(
                        maximum_component_source,
                        *(abs(source) for source in component_sources),
                    )
                    bulk_momenta = solve_flow(
                        vertex_count, bulk_edges, sources, loop_rank
                    )
                    if bulk_momenta is None:
                        continue
                    source_conserving_orientations += 1
                    if any(momentum == (0, 0, 0) for momentum in bulk_momenta):
                        identically_zero_flows += 1
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
                    for degree, arguments in kernels:
                        if len(arguments) != degree:
                            raise AssertionError("kernel arity mismatch")
                        if tuple(map(sum, zip(*arguments))) != (0, 0, 0):
                            raise AssertionError("symbolic momentum is not conserved")
                    propagators = tuple(
                        sorted(propagator_sign(momentum) for momentum in bulk_momenta)
                    )
                    fixed_p_count = propagators.count((0, 0, 1))
                    propagators = tuple(
                        momentum
                        for momentum in propagators
                        if momentum != (0, 0, 1)
                    )
                    scale_power = (
                        term["v_power"] + rank_insertions + fixed_p_count
                    )
                    key: Key = (loop_rank, scale_power, kernels, propagators)
                    coefficient = (
                        term["coefficient"]
                        * pairing_multiplicity
                        * atom_coefficient(atoms)
                        * 2 ** term["v_power"]
                        * Fraction((-1) ** rank_insertions, 2**rank_insertions)
                    )
                    grouped[key][(term["name"], rank_insertions)] += coefficient
                    contributing_orientations += 1
    stats = {
        "candidate_signed_orientations": candidate_orientations,
        "source_conserving_orientations": source_conserving_orientations,
        "identically_zero_orientations": identically_zero_flows,
        "contributing_orientations": contributing_orientations,
        "precombination_integrand_count": len(grouped),
        "exactly_canceled_integrand_count": sum(
            sum(origins.values(), Fraction()) == 0 for origins in grouped.values()
        ),
        "surviving_integrand_count": sum(
            sum(origins.values(), Fraction()) != 0 for origins in grouped.values()
        ),
        "maximum_component_source_absolute_value": maximum_component_source,
    }
    return grouped, stats


def encode_form(form: Form) -> list[int]:
    return list(form)


def encode_row(key: Key, origins: Counter) -> dict:
    loop_rank, scale_power, kernels, propagators = key
    return {
        "loop_rank": loop_rank,
        "omega_p_inverse_square_power": scale_power,
        "coefficient": enc(sum(origins.values(), Fraction())),
        "kernels": [
            {
                "degree": degree,
                "arguments": [encode_form(form) for form in arguments],
            }
            for degree, arguments in kernels
        ],
        "propagators": [encode_form(form) for form in propagators],
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


def build() -> dict:
    grouped_by_rank = {}
    statistics = {}
    for loop_rank in (0, 1):
        grouped, stats = generate_rank(loop_rank)
        grouped_by_rank[loop_rank] = grouped
        statistics[str(loop_rank)] = stats
    canceled = [
        encode_row(key, origins)
        for loop_rank in (0, 1)
        for key, origins in sorted(grouped_by_rank[loop_rank].items())
        if sum(origins.values(), Fraction()) == 0
    ]
    surviving = [
        encode_row(key, origins)
        for loop_rank in (0, 1)
        for key, origins in sorted(grouped_by_rank[loop_rank].items())
        if sum(origins.values(), Fraction()) != 0
    ]
    scale_counts = {
        str(loop_rank): {
            str(power): count
            for power, count in sorted(
                Counter(
                    row["omega_p_inverse_square_power"]
                    for row in surviving
                    if row["loop_rank"] == loop_rank
                ).items()
            )
        }
        for loop_rank in (0, 1)
    }
    checks = {
        "zero_loop_candidate_count_is_432256": statistics["0"]["candidate_signed_orientations"] == 432256,
        "zero_loop_4120_conserving_3272_zero_848_contributing": statistics["0"]["source_conserving_orientations"] == 4120 and statistics["0"]["identically_zero_orientations"] == 3272 and statistics["0"]["contributing_orientations"] == 848,
        "zero_loop_reduces_to_ten_survivors": statistics["0"]["precombination_integrand_count"] == 10 and statistics["0"]["exactly_canceled_integrand_count"] == 0 and statistics["0"]["surviving_integrand_count"] == 10,
        "zero_loop_maximum_component_source_is_six": statistics["0"]["maximum_component_source_absolute_value"] == 6,
        "one_loop_candidate_count_is_110112": statistics["1"]["candidate_signed_orientations"] == 110112,
        "one_loop_1104_conserving_750_zero_354_contributing": statistics["1"]["source_conserving_orientations"] == 1104 and statistics["1"]["identically_zero_orientations"] == 750 and statistics["1"]["contributing_orientations"] == 354,
        "one_loop_thirty_seven_rows_ten_cancel_twenty_seven_survive": statistics["1"]["precombination_integrand_count"] == 37 and statistics["1"]["exactly_canceled_integrand_count"] == 10 and statistics["1"]["surviving_integrand_count"] == 27,
        "one_loop_maximum_component_source_is_five": statistics["1"]["maximum_component_source_absolute_value"] == 5,
        "scale_power_splits_are_exact": scale_counts == {"0": {"2": 7, "3": 3}, "1": {"1": 24, "2": 3}},
        "all_kernel_arguments_conserve_symbolic_momentum": True,
        "all_propagator_constraints_are_explicit": True,
        "large_volume_lower_loop_bound_remains_open": True,
        "complete_M4_and_actual_H_minus_one_remain_open": True,
        "no_continuum_born_krein_or_lorentzian_promotion": True,
    }
    if not all(checks.values()):
        raise AssertionError([name for name, passed in checks.items() if not passed])
    return {
        "result_id": "REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_LOWER_LOOP_ATLAS_V1",
        "result_kind": "exact generic-volume affine momentum-flow atlas for the missing zero- and one-loop conditioned sectors of complete BT order g^4",
        "created": "2026-08-15",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "volume_scope": {
            "lengths": "every integer L>=7",
            "external_momentum": "p=(1,0,0,0) in Z_L^4",
            "reason": "The exhaustive audit gives maximum absolute component source six in rank zero and five in rank one, so integer and modular source conservation agree for L>=7.",
        },
        "affine_notation": {
            "form": "[a,b,c] denotes a*q+b*r+c*p; b is zero in the lower-loop rows",
            "formula": "M4_rank_ell(L)=N^(-1)*sum_rows coefficient*omega(p)^(-2*s)*sum_over_ell_loop_momenta product K_d(arguments)/product omega(k)^2, with every listed propagator required nonzero",
            "normalization": "The same K_d, conditioned covariance, fiber variance, and N=L^4 conventions as the certified two-loop atlas are used.",
        },
        "statistics": statistics,
        "surviving_by_loop_rank_and_scale_power": scale_counts,
        "exact_cancellations": canceled,
        "surviving_integrands": surviving,
        "checks": checks,
        "does_not_establish": [
            "that the ten zero-loop or twenty-seven one-loop rows are individually or jointly sub-power",
            "the sign or asymptotic coefficient of the complete lower-loop sector",
            "the sign or scaling of complete M4 after lower-loop recombination",
            "a nonperturbative score or actual interacting H^-1 estimate",
            "a continuum limit, Born rule, Krein reconstruction, or any Lorentzian claim",
        ],
        "next_gate": "Combine the ten zero-loop rows into their exact one-dimensional external-momentum rational function and prove its scaling. Then group the twenty-seven one-loop rows under q shifts and p reflection before applying soft-factor bounds; separate rowwise bounds are too weak and destroy observed cancellations.",
        "status": "EXACT_LOWER_LOOP_ATLAS_PROVED_ASYMPTOTIC_BOUND_OPEN",
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
