"""Signed identical-factor orbits for the small AFN0 ambient sectors.

The ambient tensor-graph certificate counts more than 2.8 billion raw graphs.
This module deliberately restricts explicit orbit reduction to total degrees
three and four, where the factored realization contains fewer than 400,000
graphs.  It quotients only by permutations of genuinely identical tensor
factors, including the Koszul sign for odd factors.  Intrinsic tensor
identities, horizontal-form antisymmetry, integration by parts, and the
four-dimensional quotient remain separate fail-closed gates.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
from math import factorial
from typing import Iterator, Sequence

from .algebra import canonical_sha256
from .ambient_tensor_graphs import factor_profiles, raw_graph_count
from .lower_form_ambient import ambient_lower_form_signature_analysis


SMALL_TOTAL_DEGREES = (3, 4)
Pairing = tuple[tuple[str, str], ...]
Graph = tuple[tuple[str, ...], Pairing]
Action = tuple[dict[str, str], int]


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


def _canonical_pair(left: str, right: str) -> tuple[str, str]:
    return (left, right) if left < right else (right, left)


def _profile_slots(profile: dict[str, object]) -> tuple[str, ...]:
    return tuple(
        f"{factor['factor_id']}:{position}"
        for factor in profile["factors"]
        for position in range(len(factor["slot_variances"]))
    )


def raw_graphs(profile: dict[str, object]) -> Iterator[Graph]:
    """Yield every epsilon choice and metric matching for one small profile."""

    slots = _profile_slots(profile)
    epsilon_choices = combinations(slots, 4) if profile["epsilon_slot_count"] else ((),)
    for epsilon_slots in epsilon_choices:
        epsilon = tuple(epsilon_slots)
        epsilon_set = set(epsilon)
        remainder = tuple(slot for slot in slots if slot not in epsilon_set)
        for pairs in _perfect_matchings(remainder):
            yield epsilon, tuple(sorted(_canonical_pair(*pair) for pair in pairs))


def _permutation_sign(values: Sequence[int] | Sequence[str]) -> int:
    inversions = sum(
        values[left] > values[right]
        for left in range(len(values))
        for right in range(left + 1, len(values))
    )
    return -1 if inversions % 2 else 1


def _group_actions(factors: Sequence[dict[str, object]]) -> tuple[Action, ...]:
    """Return the signed symmetric-group action for one identical-factor group."""

    factor_ids = tuple(str(factor["factor_id"]) for factor in factors)
    slot_counts = {len(factor["slot_variances"]) for factor in factors}
    parities = {int(factor["Grassmann_parity"]) for factor in factors}
    if len(slot_counts) != 1 or len(parities) != 1:
        raise AssertionError("identical-factor group has incompatible slot data")
    slot_count = next(iter(slot_counts))
    parity = next(iter(parities))
    rows = []
    for permutation in permutations(range(len(factor_ids))):
        mapping = {
            f"{source_id}:{slot}": f"{factor_ids[permutation[source]]}:{slot}"
            for source, source_id in enumerate(factor_ids)
            for slot in range(slot_count)
        }
        rows.append((mapping, _permutation_sign(permutation) if parity else 1))
    return tuple(rows)


def factor_permutation_actions(profile: dict[str, object]) -> tuple[Action, ...]:
    """Construct the direct product of all signed identical-factor actions."""

    grouped: dict[tuple[str, int], list[dict[str, object]]] = {}
    for factor in profile["factors"]:
        if factor["factor_type"] == "HORIZONTAL_FORM_CARRIER":
            continue
        key = (str(factor["factor_type"]), int(factor["derivative_order"]))
        grouped.setdefault(key, []).append(factor)
    nontrivial = [rows for rows in grouped.values() if len(rows) > 1]
    group_actions = [_group_actions(rows) for rows in nontrivial]
    if not group_actions:
        return (({}, 1),)
    actions = []
    for choices in product(*group_actions):
        mapping: dict[str, str] = {}
        sign = 1
        for group_mapping, group_sign in choices:
            if set(mapping).intersection(group_mapping):
                raise AssertionError("identical-factor groups overlap")
            mapping.update(group_mapping)
            sign *= group_sign
        actions.append((mapping, sign))
    expected = 1
    for rows in nontrivial:
        expected *= factorial(len(rows))
    if len(actions) != expected:
        raise AssertionError("factor action order drifted")
    return tuple(actions)


def _transform(graph: Graph, action: Action) -> tuple[Graph, int]:
    mapping, factor_sign = action
    epsilon, pairs = graph
    mapped_epsilon = tuple(mapping.get(slot, slot) for slot in epsilon)
    epsilon_sign = _permutation_sign(mapped_epsilon)
    transformed = (
        tuple(sorted(mapped_epsilon)),
        tuple(
            sorted(
                _canonical_pair(mapping.get(left, left), mapping.get(right, right))
                for left, right in pairs
            )
        ),
    )
    return transformed, factor_sign * epsilon_sign


def _orbit_key(graph: Graph, actions: Sequence[Action]) -> tuple[Graph, bool]:
    images: dict[Graph, set[int]] = {}
    for action in actions:
        image, sign = _transform(graph, action)
        images.setdefault(image, set()).add(sign)
    killed = any(signs == {-1, 1} for signs in images.values())
    return min(images), killed


def profile_orbit_reduction(
    signature: dict[str, object], profile: dict[str, object]
) -> dict[str, object]:
    """Reduce one profile and retain exact raw-to-orbit coverage receipts."""

    actions = factor_permutation_actions(profile)
    orbit_multiplicities: Counter[Graph] = Counter()
    killed: dict[Graph, bool] = {}
    seen = 0
    for graph in raw_graphs(profile):
        representative, is_killed = _orbit_key(graph, actions)
        orbit_multiplicities[representative] += 1
        killed.setdefault(representative, is_killed)
        if killed[representative] != is_killed:
            raise AssertionError("signed stabilizer status is not orbit-invariant")
        seen += 1
    expected = raw_graph_count(
        int(signature["total_index_slots_with_dx"]),
        int(signature["epsilon_count"]),
    )
    if seen != expected or sum(orbit_multiplicities.values()) != expected:
        raise AssertionError("raw-to-orbit coverage drifted")
    action_order = len(actions)
    if any(action_order % size for size in orbit_multiplicities.values()):
        raise AssertionError("orbit size does not divide the factor action order")
    killed_representatives = tuple(sorted(key for key, value in killed.items() if value))
    surviving_representatives = tuple(sorted(key for key, value in killed.items() if not value))
    payload = {
        "profile_sha256": profile["profile_sha256"],
        "signature_sha256": signature["signature_sha256"],
        "factor_action_order": action_order,
        "factor_action_manifest_sha256": canonical_sha256(
            [
                {"mapping": mapping, "sign": sign}
                for mapping, sign in actions
            ]
        ),
        "raw_graph_count": seen,
        "signed_orbit_count": len(orbit_multiplicities),
        "surviving_orbit_count": len(surviving_representatives),
        "Grassmann_zero_orbit_count": len(killed_representatives),
        "Grassmann_zero_raw_graph_count": sum(
            orbit_multiplicities[key] for key in killed_representatives
        ),
        "orbit_size_histogram": [
            {"orbit_size": size, "orbit_count": count}
            for size, count in sorted(Counter(orbit_multiplicities.values()).items())
        ],
        "surviving_representative_manifest_sha256": canonical_sha256(
            surviving_representatives
        ),
        "Grassmann_zero_representative_manifest_sha256": canonical_sha256(
            killed_representatives
        ),
        "coverage_status": "EXACT_RAW_GRAPH_PARTITION_VERIFIED",
        "identity_seams": {
            "intrinsic_Riemann_symmetries": "NOT_COMPUTED",
            "algebraic_and_differential_Bianchi": "NOT_COMPUTED",
            "covariant_jet_commutators": "NOT_COMPUTED",
            "horizontal_form_antisymmetry": "NOT_COMPUTED",
            "integration_by_parts": "NOT_COMPUTED",
            "four_dimensional_antisymmetrization": "NOT_COMPUTED",
        },
    }
    return {**payload, "reduction_sha256": canonical_sha256(payload)}


@lru_cache(maxsize=1)
def ambient_factor_orbit_analysis() -> tuple[dict[str, object], dict[str, object]]:
    """Build the compact certificate and detailed degrees-three/four bundle."""

    ambient = ambient_lower_form_signature_analysis()
    reductions = []
    summaries = []
    sector_counts: dict[tuple[str, int], dict[str, int]] = {}
    for manifest in ambient["manifests"]:
        degree = int(manifest["total_degree"])
        if degree not in SMALL_TOTAL_DEGREES:
            continue
        parity = str(manifest["parity"])
        counts = {
            "refined_signature_count": 0,
            "factor_profile_count": 0,
            "raw_graph_count": 0,
            "signed_orbit_count": 0,
            "surviving_orbit_count": 0,
            "Grassmann_zero_orbit_count": 0,
        }
        for signature in manifest["signatures"]:
            if signature["refinement_status"] != "REFINED_ADMISSIBLE":
                continue
            profiles = factor_profiles(signature)
            profile_reductions = [
                profile_orbit_reduction(signature, profile) for profile in profiles
            ]
            reductions.extend(profile_reductions)
            counts["refined_signature_count"] += 1
            counts["factor_profile_count"] += len(profile_reductions)
            for key in (
                "raw_graph_count",
                "signed_orbit_count",
                "surviving_orbit_count",
                "Grassmann_zero_orbit_count",
            ):
                counts[key] += sum(int(row[key]) for row in profile_reductions)
            summaries.append(
                {
                    "signature_sha256": signature["signature_sha256"],
                    "parity": parity,
                    "total_degree": degree,
                    "ghost_number": signature["ghost_number"],
                    "form_degree": signature["form_degree"],
                    "factor_profile_count": len(profile_reductions),
                    "raw_graph_count": sum(row["raw_graph_count"] for row in profile_reductions),
                    "signed_orbit_count": sum(row["signed_orbit_count"] for row in profile_reductions),
                    "surviving_orbit_count": sum(row["surviving_orbit_count"] for row in profile_reductions),
                    "Grassmann_zero_orbit_count": sum(row["Grassmann_zero_orbit_count"] for row in profile_reductions),
                    "profile_reduction_manifest_sha256": canonical_sha256(
                        [row["reduction_sha256"] for row in profile_reductions]
                    ),
                }
            )
        sector_counts[(parity, degree)] = counts

    bundle_payload = {
        "result_id": "AFN0_AMBIENT_FACTOR_ORBIT_BUNDLE_DEGREES_THREE_FOUR",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "ambient_analysis_sha256": ambient["analysis_sha256"],
        "profile_reduction_count": len(reductions),
        "profile_reductions": reductions,
    }
    bundle = {**bundle_payload, "bundle_sha256": canonical_sha256(bundle_payload)}
    totals = {
        key: sum(row[key] for row in sector_counts.values())
        for key in (
            "refined_signature_count",
            "factor_profile_count",
            "raw_graph_count",
            "signed_orbit_count",
            "surviving_orbit_count",
            "Grassmann_zero_orbit_count",
        )
    }
    analysis_payload = {
        "result_id": "AFN0_AMBIENT_FACTOR_ORBIT_CERTIFICATE_DEGREES_THREE_FOUR",
        "result_state": "SIGNED_FACTOR_ORBITS_COMPLETE_IDENTITY_QUOTIENT_OPEN",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope_label": "AFN0_ONLY_TOTAL_DEGREES_THREE_FOUR",
        "ambient_signature_source": {
            "result_id": ambient["result_id"],
            "analysis_sha256": ambient["analysis_sha256"],
        },
        "declared_quotient": {
            "implemented": [
                "permutations of identical factors at fixed derivative order",
                "Koszul signs for exchanges of identical Grassmann-odd factors",
                "epsilon orientation sign induced by factor permutations",
            ],
            "explicitly_excluded": [
                "intrinsic Riemann symmetries and Bianchi identities",
                "covariant-jet commutators",
                "horizontal-form antisymmetry",
                "integration by parts",
                "four-dimensional antisymmetrization identities",
                "Q and d_h matrix assembly",
            ],
        },
        "factor_orbit_bundle": {
            "bundle_sha256": bundle["bundle_sha256"],
            "profile_reduction_count": bundle["profile_reduction_count"],
        },
        "totals": totals,
        "counts_by_sector": [
            {"parity": parity, "total_degree": degree, **counts}
            for (parity, degree), counts in sorted(sector_counts.items())
        ],
        "signature_summaries": summaries,
        "checks": {
            "all_refined_degree_three_four_signatures_accounted_for": "VERIFIED",
            "all_factor_profiles_accounted_for": "VERIFIED",
            "signed_factor_actions_exact": "VERIFIED",
            "every_raw_graph_assigned_to_exactly_one_orbit": "VERIFIED",
            "every_orbit_size_divides_action_order": "VERIFIED",
            "Grassmann_odd_stabilizer_zeros_detected": "VERIFIED",
            "ambient_billion_graph_sectors_not_materialized": "VERIFIED",
        },
        "next_gates": {
            "intrinsic_tensor_and_Bianchi_quotient": "NOT_COMPUTED",
            "covariant_jet_commutators": "NOT_COMPUTED",
            "horizontal_form_antisymmetry": "NOT_COMPUTED",
            "integration_by_parts_quotient": "NOT_COMPUTED",
            "dimension_specific_antisymmetrization": "NOT_COMPUTED",
            "production_Q_dh_matrices": "NOT_COMPUTED",
            "total_degrees_five_six_factor_orbits": "NOT_COMPUTED_FACTORED_ONLY",
        },
        "claim_boundary": [
            "the signed identical-factor quotient is complete only for total degrees three and four",
            "the certificate partitions raw graphs into signed factor orbits but does not yet compute the canonical local-form quotient",
            "no lower-form basis exhaustiveness, relative-cohomology dimension, anomaly class, coefficient, QME, or Lorentzian claim is promoted",
            "total degrees five and six remain factored and their raw graphs are not materialized",
        ],
    }
    analysis = {**analysis_payload, "analysis_sha256": canonical_sha256(analysis_payload)}
    return analysis, bundle
