"""Exact raw and symmetry-canonical index graphs for AFN0 signatures."""

from __future__ import annotations

from itertools import combinations, product
from math import comb
from typing import Iterator, Sequence

from .algebra import canonical_sha256
from .basis_exhaustiveness import refine_top_form_signature


Pairing = tuple[tuple[str, str], ...]
RawGraph = tuple[tuple[str, ...], Pairing]


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


def _odd_double_factorial(value: int) -> int:
    if value <= 0:
        return 1
    result = 1
    for factor in range(value, 0, -2):
        result *= factor
    return result


def slot_metadata(signature: dict[str, object]) -> tuple[dict[str, object], ...]:
    slots: list[dict[str, object]] = []
    curvature_count = int(signature["curvature_count"])
    for factor in range(curvature_count):
        for position in range(4):
            slots.append(
                {
                    "slot_id": f"R{factor}:{position}",
                    "factor_id": f"R{factor}",
                    "factor_type": "RIEMANN_COVARIANT",
                    "slot_kind": "TENSOR",
                    "variance": "LOWER",
                    "riemann_pair": position // 2,
                    "riemann_pair_position": position % 2,
                }
            )
    tensor_derivatives = int(signature["tensor_derivative_count"])
    if tensor_derivatives:
        if not curvature_count:
            raise ValueError("tensor derivatives have no curvature seed")
        for position in range(tensor_derivatives):
            slots.append(
                {
                    "slot_id": f"DR0:{position}",
                    "factor_id": "R0",
                    "factor_type": "CURVATURE_DERIVATIVE",
                    "slot_kind": "DERIVATIVE",
                    "variance": "LOWER",
                    "derivative_order_position": position,
                    "derivative_order_convention": "ZERO_IS_OUTERMOST",
                }
            )
    species = str(signature["ghost_species"])
    ghost_derivatives = int(signature["ghost_derivative_order"])
    if species == "WEYL":
        for position in range(ghost_derivatives):
            slots.append(
                {
                    "slot_id": f"Domega:{position}",
                    "factor_id": "omega",
                    "factor_type": "WEYL_GHOST_DERIVATIVE",
                    "slot_kind": "DERIVATIVE",
                    "variance": "LOWER",
                    "derivative_order_position": position,
                    "derivative_order_convention": "ZERO_IS_OUTERMOST",
                }
            )
    elif species == "DIFF":
        slots.append(
            {
                "slot_id": "xi:upper",
                "factor_id": "xi",
                "factor_type": "DIFF_GHOST",
                "slot_kind": "TENSOR",
                "variance": "UPPER",
            }
        )
        for position in range(ghost_derivatives):
            slots.append(
                {
                    "slot_id": f"Dxi:{position}",
                    "factor_id": "xi",
                    "factor_type": "DIFF_GHOST_DERIVATIVE",
                    "slot_kind": "DERIVATIVE",
                    "variance": "LOWER",
                    "derivative_order_position": position,
                    "derivative_order_convention": "ZERO_IS_OUTERMOST",
                }
            )
    elif species != "NONE":
        raise ValueError("unknown ghost species")
    if len(slots) != int(signature["total_index_slots"]):
        raise AssertionError("signature index-slot count drifted")
    return tuple(slots)


def signature_index_slots(signature: dict[str, object]) -> tuple[str, ...]:
    return tuple(str(row["slot_id"]) for row in slot_metadata(signature))


def _raw_graphs(signature: dict[str, object]) -> tuple[RawGraph, ...]:
    slots = signature_index_slots(signature)
    epsilon_count = int(signature["epsilon_count"])
    epsilon_choices = combinations(slots, 4) if epsilon_count else ((),)
    graphs = []
    for epsilon_slots in epsilon_choices:
        epsilon_set = set(epsilon_slots)
        remainder = tuple(slot for slot in slots if slot not in epsilon_set)
        for pairs in _perfect_matchings(remainder):
            graphs.append(
                (
                    tuple(epsilon_slots),
                    tuple(sorted(_canonical_pair(*pair) for pair in pairs)),
                )
            )
    return tuple(graphs)


def _expected_raw_count(signature: dict[str, object]) -> int:
    slot_count = int(signature["total_index_slots"])
    if signature["epsilon_count"]:
        return comb(slot_count, 4) * _odd_double_factorial(slot_count - 5)
    return _odd_double_factorial(slot_count - 1)


def _permutation_parity(values: Sequence[str]) -> int:
    inversions = sum(
        values[left] > values[right]
        for left in range(len(values))
        for right in range(left + 1, len(values))
    )
    return -1 if inversions % 2 else 1


def _riemann_symmetries(factor: int) -> tuple[tuple[dict[str, str], int], ...]:
    prefix = f"R{factor}:"
    rows = []
    for swap_first, swap_second, exchange_pairs in product((False, True), repeat=3):
        image = [0, 1, 2, 3]
        sign = 1
        if swap_first:
            image[0], image[1] = image[1], image[0]
            sign *= -1
        if swap_second:
            image[2], image[3] = image[3], image[2]
            sign *= -1
        if exchange_pairs:
            image = [image[2], image[3], image[0], image[1]]
        rows.append(
            (
                {f"{prefix}{source}": f"{prefix}{target}" for source, target in enumerate(image)},
                sign,
            )
        )
    return tuple(rows)


def _compose_maps(left: dict[str, str], right: dict[str, str]) -> dict[str, str]:
    keys = set(left) | set(right)
    return {key: left.get(right.get(key, key), right.get(key, key)) for key in keys}


def _symmetry_actions(
    signature: dict[str, object],
) -> tuple[tuple[dict[str, str], int], ...]:
    curvature_count = int(signature["curvature_count"])
    actions: tuple[tuple[dict[str, str], int], ...] = (({}, 1),)
    for factor in range(curvature_count):
        actions = tuple(
            (_compose_maps(left_map, right_map), left_sign * right_sign)
            for left_map, left_sign in actions
            for right_map, right_sign in _riemann_symmetries(factor)
        )
    if curvature_count == 2 and not signature["tensor_derivative_count"]:
        swap = {
            **{f"R0:{slot}": f"R1:{slot}" for slot in range(4)},
            **{f"R1:{slot}": f"R0:{slot}" for slot in range(4)},
        }
        actions = actions + tuple(
            (_compose_maps(swap, mapping), sign) for mapping, sign in actions
        )
    return actions


def _canonical_pair(left: str, right: str) -> tuple[str, str]:
    return (left, right) if left < right else (right, left)


def _transform_graph(
    graph: RawGraph, mapping: dict[str, str], tensor_sign: int
) -> tuple[tuple[tuple[str, ...], Pairing], int]:
    epsilon, pairs = graph
    mapped_epsilon = tuple(mapping.get(slot, slot) for slot in epsilon)
    epsilon_sign = _permutation_parity(mapped_epsilon)
    canonical_epsilon = tuple(sorted(mapped_epsilon))
    canonical_pairs = tuple(
        sorted(
            _canonical_pair(mapping.get(left, left), mapping.get(right, right))
            for left, right in pairs
        )
    )
    return (canonical_epsilon, canonical_pairs), tensor_sign * epsilon_sign


def _symmetry_quotient(
    signature: dict[str, object], graphs: Sequence[RawGraph]
) -> dict[str, object]:
    actions = _symmetry_actions(signature)
    orbit_representatives: set[tuple[tuple[str, ...], Pairing]] = set()
    zero_graph_count = 0
    for graph in graphs:
        images: dict[tuple[tuple[str, ...], Pairing], set[int]] = {}
        for mapping, tensor_sign in actions:
            key, sign = _transform_graph(graph, mapping, tensor_sign)
            images.setdefault(key, set()).add(sign)
        if any(signs == {-1, 1} for signs in images.values()):
            zero_graph_count += 1
            continue
        orbit_representatives.add(min(images))
    representatives = [
        {
            "epsilon_slots": list(epsilon),
            "metric_pairs": [list(pair) for pair in pairs],
        }
        for epsilon, pairs in sorted(orbit_representatives)
    ]
    return {
        "implemented_symmetry_action_count": len(actions),
        "signed_symmetry_zero_raw_graph_count": zero_graph_count,
        "symmetry_canonical_orbit_count": len(representatives),
        "symmetry_canonical_orbit_representatives": representatives,
        "factor_permutation_status": (
            "IMPLEMENTED"
            if int(signature["curvature_count"]) < 2
            or not signature["tensor_derivative_count"]
            else "PENDING_DERIVATIVE_DISTRIBUTION"
        ),
        "riemann_pair_symmetries_status": "IMPLEMENTED_WITH_SIGNS",
        "bianchi_quotient_status": "NOT_COMPUTED",
        "dimension_specific_antisymmetrization_status": "NOT_COMPUTED",
    }


def _pair_contraction_tensor(
    pair: tuple[str, str], metadata: dict[str, dict[str, object]]
) -> str:
    variances = tuple(metadata[slot]["variance"] for slot in pair)
    if variances == ("LOWER", "LOWER"):
        return "INVERSE_METRIC"
    if variances == ("UPPER", "UPPER"):
        return "METRIC"
    return "KRONECKER_DELTA"


def _graph_payload(
    graph: RawGraph, metadata: dict[str, dict[str, object]]
) -> dict[str, object]:
    epsilon, pairs = graph
    return {
        "epsilon_slots": list(epsilon),
        "epsilon_slot_variances": [metadata[slot]["variance"] for slot in epsilon],
        "metric_edges": [
            {
                "slots": list(pair),
                "contraction_tensor": _pair_contraction_tensor(pair, metadata),
            }
            for pair in pairs
        ],
    }


def _outer_derivative_slot(signature: dict[str, object]) -> str | None:
    if signature["tensor_derivative_count"]:
        return "DR0:0"
    if signature["ghost_derivative_order"]:
        species = str(signature["ghost_species"])
        return "Domega:0" if species == "WEYL" else "Dxi:0"
    return None


def _single_differentiated_factor(signature: dict[str, object]) -> bool:
    if (
        signature["curvature_count"] == 0
        and signature["tensor_derivative_count"] == 0
        and signature["ghost_derivative_order"]
    ):
        return True
    return bool(
        signature["ghost_species"] == "NONE"
        and signature["curvature_count"] == 1
        and signature["tensor_derivative_count"]
    )


def _current_witness(graph: RawGraph, outer_slot: str) -> dict[str, object]:
    epsilon, pairs = graph
    if outer_slot in epsilon:
        position = epsilon.index(outer_slot)
        current_epsilon = list(epsilon)
        current_epsilon[position] = "CURRENT_FREE_INDEX"
        witness = {
            "mode": "EPSILON_CURRENT",
            "outer_derivative_slot": outer_slot,
            "current_epsilon_slots": current_epsilon,
            "remaining_metric_pairs": [list(pair) for pair in pairs],
        }
    else:
        pair = next(pair for pair in pairs if outer_slot in pair)
        partner = pair[1] if pair[0] == outer_slot else pair[0]
        witness = {
            "mode": "METRIC_CURRENT",
            "outer_derivative_slot": outer_slot,
            "current_free_index_partner": partner,
            "remaining_metric_pairs": [list(row) for row in pairs if row != pair],
            "epsilon_slots": list(epsilon),
        }
    if not _verify_current_witness(graph, witness):
        raise AssertionError("graphwise divergence witness does not reconstruct")
    return witness


def _verify_current_witness(graph: RawGraph, witness: dict[str, object]) -> bool:
    outer_slot = str(witness["outer_derivative_slot"])
    if witness["mode"] == "EPSILON_CURRENT":
        epsilon = tuple(
            outer_slot if slot == "CURRENT_FREE_INDEX" else str(slot)
            for slot in witness["current_epsilon_slots"]
        )
        pairs = tuple(tuple(pair) for pair in witness["remaining_metric_pairs"])
    else:
        epsilon = tuple(str(slot) for slot in witness["epsilon_slots"])
        reconstructed = tuple(
            tuple(pair) for pair in witness["remaining_metric_pairs"]
        ) + ((outer_slot, str(witness["current_free_index_partner"])),)
        pairs = tuple(sorted(_canonical_pair(*pair) for pair in reconstructed))
    expected_epsilon, expected_pairs = graph
    return epsilon == expected_epsilon and pairs == expected_pairs


def _divergence_witness_manifest(
    signature: dict[str, object], graphs: Sequence[RawGraph]
) -> dict[str, object]:
    if not _single_differentiated_factor(signature):
        return {
            "status": "NOT_APPLICABLE",
            "graphwise_current_count": 0,
            "graphwise_current_manifest_hash": canonical_sha256([]),
            "current_witnesses": [],
        }
    outer_slot = _outer_derivative_slot(signature)
    if outer_slot is None:
        raise AssertionError("single differentiated factor lacks an outer derivative")
    witnesses = [_current_witness(graph, outer_slot) for graph in graphs]
    return {
        "status": "VERIFIED_EVERY_RAW_GRAPH",
        "outer_derivative_convention": "DERIVATIVE_POSITION_ZERO_IS_OUTERMOST",
        "covariant_constancy_inputs": ["nabla_metric=0", "nabla_epsilon=0"],
        "graphwise_current_count": len(witnesses),
        "graphwise_current_manifest_hash": canonical_sha256(witnesses),
        "current_witnesses": witnesses,
    }


def contraction_graph_artifact(signature: dict[str, object]) -> dict[str, object]:
    """Return the content-addressable graph artifact for one signature."""

    realizable, reason = refine_top_form_signature(signature)
    if not realizable:
        payload = {
            "signature": signature,
            "refined_grading_status": "REJECTED_BY_REFINED_GRADING",
            "reason": reason,
            "slot_metadata": [],
            "raw_generation": {
                "status": "NOT_APPLICABLE",
                "raw_contraction_graph_count": 0,
                "independent_combinatorial_count": 0,
                "count_agreement": "VERIFIED",
            },
            "symmetry_quotient": "NOT_APPLICABLE",
            "divergence_witness": "NOT_APPLICABLE",
        }
        return {**payload, "artifact_hash": canonical_sha256(payload)}
    metadata_rows = slot_metadata(signature)
    metadata = {str(row["slot_id"]): row for row in metadata_rows}
    graphs = _raw_graphs(signature)
    expected_count = _expected_raw_count(signature)
    if len(graphs) != expected_count:
        raise AssertionError("raw graph enumeration disagrees with combinatorics")
    graph_payloads = [_graph_payload(graph, metadata) for graph in graphs]
    payload = {
        "signature": signature,
        "refined_grading_status": "REFINED_ADMISSIBLE",
        "reason": reason,
        "slot_metadata": list(metadata_rows),
        "raw_generation": {
            "status": "RAW_CONTRACTION_EXISTS",
            "raw_contraction_graph_count": len(graphs),
            "independent_combinatorial_count": expected_count,
            "count_agreement": "VERIFIED",
            "raw_graph_manifest_hash": canonical_sha256(graph_payloads),
        },
        "symmetry_quotient": _symmetry_quotient(signature, graphs),
        "divergence_witness": _divergence_witness_manifest(signature, graphs),
    }
    return {**payload, "artifact_hash": canonical_sha256(payload)}


def contraction_graph_manifest(signature: dict[str, object]) -> dict[str, object]:
    """Return a compact fail-closed summary of one graph artifact."""

    artifact = contraction_graph_artifact(signature)
    raw = artifact["raw_generation"]
    if raw["status"] == "NOT_APPLICABLE":
        return {
            "raw_contraction_status": "NOT_APPLICABLE",
            "tensor_realizability": "NOT_REALIZABLE_AFTER_REFINED_GRADING",
            "reason": artifact["reason"],
            "raw_contraction_graph_count": 0,
            "raw_graph_manifest_hash": canonical_sha256([]),
            "graph_enumeration_status": "NOT_APPLICABLE",
            "graph_artifact_hash": artifact["artifact_hash"],
            "symmetry_canonical_orbit_count": 0,
            "graphwise_divergence_status": "NOT_APPLICABLE",
            "graphwise_current_manifest_hash": canonical_sha256([]),
        }
    symmetry = artifact["symmetry_quotient"]
    divergence = artifact["divergence_witness"]
    return {
        "raw_contraction_status": "RAW_CONTRACTION_EXISTS",
        "tensor_realizability": "UNDECIDED_PENDING_BIANCHI_AND_DIMENSION_IDENTITIES",
        "reason": artifact["reason"],
        "raw_contraction_graph_count": raw["raw_contraction_graph_count"],
        "raw_graph_manifest_hash": raw["raw_graph_manifest_hash"],
        "graph_enumeration_status": "SYMMETRY_CANONICALIZED_BIANCHI_PENDING",
        "graph_artifact_hash": artifact["artifact_hash"],
        "symmetry_canonical_orbit_count": symmetry[
            "symmetry_canonical_orbit_count"
        ],
        "graphwise_divergence_status": divergence["status"],
        "graphwise_current_manifest_hash": divergence[
            "graphwise_current_manifest_hash"
        ],
    }


def contraction_graph_bundle(
    signatures: Sequence[dict[str, object]],
) -> dict[str, object]:
    """Bundle unique signature artifacts under one content address."""

    artifacts = {
        artifact["artifact_hash"]: artifact
        for artifact in map(contraction_graph_artifact, signatures)
    }
    payload = {
        "result_id": "AFN0_CONTRACTION_GRAPH_BUNDLE",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "artifact_count": len(artifacts),
        "artifacts": [artifacts[key] for key in sorted(artifacts)],
    }
    return {**payload, "bundle_hash": canonical_sha256(payload)}
