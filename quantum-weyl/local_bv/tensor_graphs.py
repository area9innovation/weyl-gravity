"""Exact raw index-contraction graphs for AFN0 grading signatures."""

from __future__ import annotations

from itertools import combinations
from typing import Iterator, Sequence

from .algebra import canonical_sha256
from .basis_exhaustiveness import refine_top_form_signature


Pairing = tuple[tuple[str, str], ...]


def _perfect_matchings(labels: Sequence[str]) -> Iterator[Pairing]:
    if not labels:
        yield ()
        return
    first = labels[0]
    for partner_index in range(1, len(labels)):
        partner = labels[partner_index]
        remaining = labels[1:partner_index] + labels[partner_index + 1 :]
        for tail in _perfect_matchings(remaining):
            yield ((first, partner), *tail)


def signature_index_slots(signature: dict[str, object]) -> tuple[str, ...]:
    slots: list[str] = []
    curvature_count = int(signature["curvature_count"])
    for factor in range(curvature_count):
        slots.extend(f"R{factor}:{slot}" for slot in range(4))
    tensor_derivatives = int(signature["tensor_derivative_count"])
    if tensor_derivatives:
        if not curvature_count:
            raise ValueError("tensor derivatives have no curvature seed")
        slots.extend(f"DR0:{slot}" for slot in range(tensor_derivatives))
    species = str(signature["ghost_species"])
    ghost_derivatives = int(signature["ghost_derivative_order"])
    if species == "WEYL":
        slots.extend(f"Domega:{slot}" for slot in range(ghost_derivatives))
    elif species == "DIFF":
        slots.append("xi:upper")
        slots.extend(f"Dxi:{slot}" for slot in range(ghost_derivatives))
    elif species != "NONE":
        raise ValueError("unknown ghost species")
    if len(slots) != int(signature["total_index_slots"]):
        raise AssertionError("signature index-slot count drifted")
    return tuple(slots)


def contraction_graph_manifest(signature: dict[str, object]) -> dict[str, object]:
    """Enumerate raw scalar contraction graphs before symmetry quotienting."""

    realizable, reason = refine_top_form_signature(signature)
    if not realizable:
        return {
            "tensor_realizability": "NOT_REALIZABLE_AFTER_REFINED_GRADING",
            "reason": reason,
            "raw_contraction_graph_count": 0,
            "raw_graph_manifest_hash": canonical_sha256([]),
            "graph_enumeration_status": "NOT_APPLICABLE",
        }
    slots = signature_index_slots(signature)
    epsilon_count = int(signature["epsilon_count"])
    epsilon_choices = combinations(slots, 4) if epsilon_count else ((),)
    graphs: list[dict[str, object]] = []
    for epsilon_slots in epsilon_choices:
        epsilon_set = set(epsilon_slots)
        remainder = tuple(slot for slot in slots if slot not in epsilon_set)
        for pairs in _perfect_matchings(remainder):
            graphs.append(
                {
                    "epsilon_slots": list(epsilon_slots),
                    "metric_pairs": [list(pair) for pair in pairs],
                }
            )
    return {
        "tensor_realizability": "TENSOR_REALIZABLE",
        "reason": reason,
        "raw_contraction_graph_count": len(graphs),
        "raw_graph_manifest_hash": canonical_sha256(graphs),
        "graph_enumeration_status": "RAW_COMPLETE_CANONICAL_QUOTIENT_PENDING",
    }
