"""Intrinsic signed tensor orbits for AFN0 total degrees three and four.

The full symmetry group can be much larger than its generator set.  We avoid
expanding it by applying adjacent identical-factor exchanges, the three
standard Riemann pair generators, and adjacent horizontal-form exchanges to
each raw graph.  A signed disjoint-set structure computes the resulting
orbits and detects components killed by an odd stabilizer.

This is an orbit quotient only.  Bianchi identities, covariant-jet
commutators, integration by parts, and dimension-specific identities are
linear relations between the surviving orbits and remain separate gates.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache

from .algebra import canonical_sha256
from .ambient_factor_orbits import Graph, raw_graphs
from .ambient_tensor_graphs import factor_profiles, raw_graph_count
from .lower_form_ambient import ambient_lower_form_signature_analysis


SMALL_TOTAL_DEGREES = (3, 4)


class SignedDisjointSet:
    """Disjoint sets with relations ``value_x = sign * value_y``."""

    def __init__(self, size: int):
        self.parent = list(range(size))
        self.weight = [1] * size
        self.component_zero = [False] * size

    def find(self, node: int) -> tuple[int, int]:
        parent = self.parent[node]
        if parent == node:
            return node, 1
        root, parent_weight = self.find(parent)
        self.weight[node] *= parent_weight
        self.parent[node] = root
        return root, self.weight[node]

    def relate(self, left: int, right: int, sign: int) -> None:
        if sign not in {-1, 1}:
            raise ValueError("a signed relation must have sign plus or minus one")
        left_root, left_weight = self.find(left)
        right_root, right_weight = self.find(right)
        if left_root == right_root:
            if left_weight != sign * right_weight:
                self.component_zero[left_root] = True
            return
        # value_left_root = left_weight * sign * right_weight * value_right_root
        self.parent[left_root] = right_root
        self.weight[left_root] = left_weight * sign * right_weight
        self.component_zero[right_root] = (
            self.component_zero[right_root] or self.component_zero[left_root]
        )

    def components(self) -> tuple[dict[int, list[int]], set[int]]:
        components: dict[int, list[int]] = {}
        for node in range(len(self.parent)):
            root, _ = self.find(node)
            components.setdefault(root, []).append(node)
        zero_roots = {root for root in components if self.component_zero[root]}
        return components, zero_roots


def _swap_mapping(left: dict[str, object], right: dict[str, object]) -> dict[str, str]:
    left_count = len(left["slot_variances"])
    right_count = len(right["slot_variances"])
    if left_count != right_count:
        raise AssertionError("identical factors have unequal slot counts")
    left_id = str(left["factor_id"])
    right_id = str(right["factor_id"])
    return {
        **{f"{left_id}:{slot}": f"{right_id}:{slot}" for slot in range(left_count)},
        **{f"{right_id}:{slot}": f"{left_id}:{slot}" for slot in range(left_count)},
    }


def symmetry_generators(profile: dict[str, object]) -> tuple[dict[str, object], ...]:
    """Minimal signed generators for the implemented orbit quotient."""

    factors = list(profile["factors"])
    generators: list[dict[str, object]] = []

    grouped: dict[tuple[str, int], list[dict[str, object]]] = {}
    for factor in factors:
        if factor["factor_type"] == "HORIZONTAL_FORM_CARRIER":
            continue
        key = (str(factor["factor_type"]), int(factor["derivative_order"]))
        grouped.setdefault(key, []).append(factor)
    for group in grouped.values():
        for left, right in zip(group, group[1:]):
            generators.append(
                {
                    "generator_type": "IDENTICAL_FACTOR_ADJACENT_TRANSPOSITION",
                    "mapping": _swap_mapping(left, right),
                    "sign": -1 if int(left["Grassmann_parity"]) else 1,
                }
            )

    for factor in factors:
        if factor["factor_type"] != "COVARIANT_DERIVATIVE_RIEMANN":
            continue
        factor_id = str(factor["factor_id"])
        generators.extend(
            (
                {
                    "generator_type": "RIEMANN_FIRST_PAIR_SWAP",
                    "mapping": {
                        f"{factor_id}:0": f"{factor_id}:1",
                        f"{factor_id}:1": f"{factor_id}:0",
                    },
                    "sign": -1,
                },
                {
                    "generator_type": "RIEMANN_SECOND_PAIR_SWAP",
                    "mapping": {
                        f"{factor_id}:2": f"{factor_id}:3",
                        f"{factor_id}:3": f"{factor_id}:2",
                    },
                    "sign": -1,
                },
                {
                    "generator_type": "RIEMANN_PAIR_EXCHANGE",
                    "mapping": {
                        f"{factor_id}:0": f"{factor_id}:2",
                        f"{factor_id}:1": f"{factor_id}:3",
                        f"{factor_id}:2": f"{factor_id}:0",
                        f"{factor_id}:3": f"{factor_id}:1",
                    },
                    "sign": 1,
                },
            )
        )

    horizontal = next(
        (
            factor
            for factor in factors
            if factor["factor_type"] == "HORIZONTAL_FORM_CARRIER"
        ),
        None,
    )
    if horizontal is not None:
        factor_id = str(horizontal["factor_id"])
        for slot in range(len(horizontal["slot_variances"]) - 1):
            generators.append(
                {
                    "generator_type": "HORIZONTAL_FORM_ADJACENT_TRANSPOSITION",
                    "mapping": {
                        f"{factor_id}:{slot}": f"{factor_id}:{slot + 1}",
                        f"{factor_id}:{slot + 1}": f"{factor_id}:{slot}",
                    },
                    "sign": -1,
                }
            )

    unique: dict[str, dict[str, object]] = {}
    for generator in generators:
        unique.setdefault(canonical_sha256(generator), generator)
    return tuple(unique[key] for key in sorted(unique))


def _permutation_sign(values: tuple[str, ...]) -> int:
    inversions = sum(
        values[left] > values[right]
        for left in range(len(values))
        for right in range(left + 1, len(values))
    )
    return -1 if inversions % 2 else 1


def _canonical_pair(left: str, right: str) -> tuple[str, str]:
    return (left, right) if left < right else (right, left)


def transform_graph(graph: Graph, generator: dict[str, object]) -> tuple[Graph, int]:
    mapping = generator["mapping"]
    epsilon, pairs = graph
    mapped_epsilon = tuple(mapping.get(slot, slot) for slot in epsilon)
    transformed = (
        tuple(sorted(mapped_epsilon)),
        tuple(
            sorted(
                _canonical_pair(mapping.get(left, left), mapping.get(right, right))
                for left, right in pairs
            )
        ),
    )
    return transformed, int(generator["sign"]) * _permutation_sign(mapped_epsilon)


def profile_intrinsic_orbit_reduction(
    signature: dict[str, object], profile: dict[str, object]
) -> dict[str, object]:
    """Compute the generator orbit quotient for one derivative profile."""

    # The factored enumerator orders epsilon slots by factor inventory.  The
    # symmetry action uses lexical slot order to expose its orientation sign,
    # so normalize the stored node keys once before constructing the graph.
    graphs = tuple(
        (tuple(sorted(epsilon)), pairs) for epsilon, pairs in raw_graphs(profile)
    )
    expected = raw_graph_count(
        int(signature["total_index_slots_with_dx"]),
        int(signature["epsilon_count"]),
    )
    if len(graphs) != expected or len(set(graphs)) != expected:
        raise AssertionError("raw graph enumeration is not exact and duplicate-free")
    graph_index = {graph: index for index, graph in enumerate(graphs)}
    generators = symmetry_generators(profile)
    disjoint = SignedDisjointSet(len(graphs))
    edge_count = 0
    for generator in generators:
        for source, graph in enumerate(graphs):
            image, sign = transform_graph(graph, generator)
            target = graph_index.get(image)
            if target is None:
                raise AssertionError("symmetry generator does not preserve the raw graph set")
            disjoint.relate(source, target, sign)
            edge_count += 1
    components, zero_roots = disjoint.components()
    representatives = {
        root: min(graphs[node] for node in nodes)
        for root, nodes in components.items()
    }
    surviving = tuple(sorted(value for root, value in representatives.items() if root not in zero_roots))
    killed = tuple(sorted(value for root, value in representatives.items() if root in zero_roots))
    histogram = Counter(len(nodes) for nodes in components.values())
    if sum(size * count for size, count in histogram.items()) != expected:
        raise AssertionError("intrinsic orbit coverage drifted")
    generator_type_counts = Counter(
        str(generator["generator_type"]) for generator in generators
    )
    payload = {
        "profile_sha256": profile["profile_sha256"],
        "signature_sha256": signature["signature_sha256"],
        "raw_graph_count": expected,
        "generator_count": len(generators),
        "generator_edge_count": edge_count,
        "generator_type_counts": [
            {"generator_type": key, "count": count}
            for key, count in sorted(generator_type_counts.items())
        ],
        "generator_manifest_sha256": canonical_sha256(generators),
        "signed_orbit_count": len(components),
        "surviving_orbit_count": len(surviving),
        "odd_stabilizer_zero_orbit_count": len(killed),
        "odd_stabilizer_zero_raw_graph_count": sum(
            len(components[root]) for root in zero_roots
        ),
        "orbit_size_histogram": [
            {"orbit_size": size, "orbit_count": count}
            for size, count in sorted(histogram.items())
        ],
        "surviving_representative_manifest_sha256": canonical_sha256(surviving),
        "zero_representative_manifest_sha256": canonical_sha256(killed),
        "coverage_status": "EXACT_SIGNED_GENERATOR_ORBIT_PARTITION_VERIFIED",
        "implemented_quotients": {
            "identical_factor_permutations": "COMPLETE_BY_ADJACENT_GENERATORS",
            "Grassmann_exchange_signs": "COMPLETE",
            "Riemann_pair_antisymmetry": "COMPLETE_BY_GENERATORS",
            "Riemann_pair_exchange": "COMPLETE_BY_GENERATOR",
            "horizontal_form_antisymmetry": "COMPLETE_BY_ADJACENT_GENERATORS",
        },
        "open_linear_relations": {
            "algebraic_and_differential_Bianchi": "NOT_COMPUTED",
            "covariant_jet_commutators": "NOT_COMPUTED",
            "integration_by_parts": "NOT_COMPUTED",
            "four_dimensional_antisymmetrization": "NOT_COMPUTED",
        },
    }
    return {**payload, "reduction_sha256": canonical_sha256(payload)}


@lru_cache(maxsize=1)
def ambient_intrinsic_orbit_analysis() -> tuple[dict[str, object], dict[str, object]]:
    """Build the compact intrinsic-orbit analysis and detailed profile bundle."""

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
            "generator_edge_count": 0,
            "signed_orbit_count": 0,
            "surviving_orbit_count": 0,
            "odd_stabilizer_zero_orbit_count": 0,
        }
        for signature in manifest["signatures"]:
            if signature["refinement_status"] != "REFINED_ADMISSIBLE":
                continue
            profile_reductions = [
                profile_intrinsic_orbit_reduction(signature, profile)
                for profile in factor_profiles(signature)
            ]
            reductions.extend(profile_reductions)
            counts["refined_signature_count"] += 1
            counts["factor_profile_count"] += len(profile_reductions)
            for key in (
                "raw_graph_count",
                "generator_edge_count",
                "signed_orbit_count",
                "surviving_orbit_count",
                "odd_stabilizer_zero_orbit_count",
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
                    "odd_stabilizer_zero_orbit_count": sum(row["odd_stabilizer_zero_orbit_count"] for row in profile_reductions),
                    "profile_reduction_manifest_sha256": canonical_sha256(
                        [row["reduction_sha256"] for row in profile_reductions]
                    ),
                }
            )
        sector_counts[(parity, degree)] = counts

    bundle_payload = {
        "result_id": "AFN0_AMBIENT_INTRINSIC_ORBIT_BUNDLE_DEGREES_THREE_FOUR",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "ambient_analysis_sha256": ambient["analysis_sha256"],
        "profile_reduction_count": len(reductions),
        "profile_reductions": reductions,
    }
    bundle = {**bundle_payload, "bundle_sha256": canonical_sha256(bundle_payload)}
    total_keys = (
        "refined_signature_count",
        "factor_profile_count",
        "raw_graph_count",
        "generator_edge_count",
        "signed_orbit_count",
        "surviving_orbit_count",
        "odd_stabilizer_zero_orbit_count",
    )
    totals = {
        key: sum(row[key] for row in sector_counts.values()) for key in total_keys
    }
    analysis_payload = {
        "result_id": "AFN0_AMBIENT_INTRINSIC_ORBIT_CERTIFICATE_DEGREES_THREE_FOUR",
        "result_state": "INTRINSIC_SIGNED_ORBITS_COMPLETE_LINEAR_RELATIONS_OPEN",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope_label": "AFN0_ONLY_TOTAL_DEGREES_THREE_FOUR",
        "ambient_signature_source": {
            "result_id": ambient["result_id"],
            "analysis_sha256": ambient["analysis_sha256"],
        },
        "intrinsic_orbit_bundle": {
            "bundle_sha256": bundle["bundle_sha256"],
            "profile_reduction_count": bundle["profile_reduction_count"],
        },
        "algorithm": {
            "mode": "SIGNED_DISJOINT_SET_ON_SYMMETRY_GENERATORS",
            "implemented_generators": [
                "adjacent identical-factor transpositions with Koszul signs",
                "Riemann first-pair and second-pair antisymmetry",
                "Riemann pair exchange",
                "adjacent horizontal-form transpositions",
                "induced epsilon orientation signs",
            ],
            "raw_graph_materialization_scope": "TOTAL_DEGREES_THREE_FOUR_ONLY",
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
            "every_generator_preserves_raw_graph_space": "VERIFIED",
            "every_raw_graph_assigned_to_exactly_one_signed_orbit": "VERIFIED",
            "orbit_histograms_reconstruct_raw_counts": "VERIFIED",
            "odd_stabilizer_zero_components_detected": "VERIFIED",
            "ambient_degree_five_six_graphs_not_materialized": "VERIFIED",
        },
        "next_gates": {
            "algebraic_and_differential_Bianchi": "NOT_COMPUTED",
            "covariant_jet_commutators": "NOT_COMPUTED",
            "integration_by_parts_quotient": "NOT_COMPUTED",
            "dimension_specific_antisymmetrization": "NOT_COMPUTED",
            "production_Q_dh_matrices": "NOT_COMPUTED",
            "total_degrees_five_six_intrinsic_orbits": "NOT_COMPUTED_FACTORED_ONLY",
        },
        "claim_boundary": [
            "the intrinsic signed orbit quotient is complete only for total degrees three and four",
            "Bianchi, jet-commutator, integration-by-parts, and four-dimensional relations are not group actions and remain open",
            "the surviving orbit count is not a canonical local-form basis dimension",
            "no relative-cohomology class, anomaly coefficient, QME, residual transfer, or Lorentzian claim is promoted",
        ],
    }
    analysis = {**analysis_payload, "analysis_sha256": canonical_sha256(analysis_payload)}
    return analysis, bundle
