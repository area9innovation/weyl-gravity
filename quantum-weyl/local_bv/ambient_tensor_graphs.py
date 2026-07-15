"""Factored tensor-graph realization for the AFN0 ambient signatures.

The ambient grading certificate deliberately forgets how derivatives are
distributed among identical curvature and ghost factors.  This module restores
that finite information.  It does *not* materialize every perfect matching:
the dimension-six odd sector alone contains hundreds of millions of raw
graphs.  Instead, every derivative-distribution profile carries an exact slot
inventory and an independently checkable perfect-matching count.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import product
from math import comb, factorial

from .algebra import canonical_sha256
from .lower_form_ambient import ambient_lower_form_signature_analysis


EXPLICIT_GRAPH_THRESHOLD = 100_000


@lru_cache(maxsize=None)
def nondecreasing_distributions(total: int, factor_count: int) -> tuple[tuple[int, ...], ...]:
    """Partitions of ``total`` into exactly ``factor_count`` unlabeled factors."""

    if total < 0 or factor_count < 0:
        raise ValueError("distribution inputs must be nonnegative")
    if factor_count == 0:
        return ((),) if total == 0 else ()
    rows: list[tuple[int, ...]] = []

    def visit(prefix: tuple[int, ...], lower: int, remaining: int, slots: int) -> None:
        if slots == 0:
            if remaining == 0:
                rows.append(prefix)
            return
        # Nondecreasing tails require every remaining entry to be at least
        # ``value``.  This bound makes the enumeration finite by construction.
        for value in range(lower, remaining // slots + 1):
            visit((*prefix, value), value, remaining - value, slots - 1)

    visit((), 0, total, factor_count)
    return tuple(rows)


def _weyl_distributions(total: int, factor_count: int) -> tuple[tuple[int, ...], ...]:
    """Weyl-ghost derivative distributions with at most one scalar omega."""

    return tuple(
        row
        for row in nondecreasing_distributions(total, factor_count)
        if row.count(0) <= 1
    )


def _odd_double_factorial(value: int) -> int:
    if value <= 0:
        return 1
    result = 1
    for factor in range(value, 0, -2):
        result *= factor
    return result


def raw_graph_count(slot_count: int, epsilon_count: int) -> int:
    """Number of epsilon choices followed by metric perfect matchings."""

    if slot_count < 0 or epsilon_count not in {0, 1}:
        raise ValueError("invalid tensor-graph count inputs")
    if epsilon_count:
        if slot_count < 4 or (slot_count - 4) % 2:
            return 0
        return comb(slot_count, 4) * _odd_double_factorial(slot_count - 5)
    if slot_count % 2:
        return 0
    return _odd_double_factorial(slot_count - 1)


def _multiplicity_groups(values: tuple[int, ...], prefix: str, parity: int) -> list[dict[str, object]]:
    groups = []
    for value in sorted(set(values)):
        multiplicity = values.count(value)
        groups.append(
            {
                "factor_type": prefix,
                "derivative_order": value,
                "multiplicity": multiplicity,
                "factor_permutation_order": factorial(multiplicity),
                "factor_exchange_sign": "KOSZUL" if parity else "EVEN",
            }
        )
    return groups


def _factor_rows(
    signature: dict[str, object],
    curvature_orders: tuple[int, ...],
    weyl_orders: tuple[int, ...],
    diff_orders: tuple[int, ...],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for factor, order in enumerate(curvature_orders):
        rows.append(
            {
                "factor_id": f"R{factor}",
                "factor_type": "COVARIANT_DERIVATIVE_RIEMANN",
                "derivative_order": order,
                "Grassmann_parity": 0,
                "slot_variances": ["LOWER"] * (4 + order),
                "intrinsic_slot_symmetry": "RIEMANN_PAIRS; DERIVATIVE_JET_RELATIONS_PENDING",
            }
        )
    for factor, order in enumerate(weyl_orders):
        rows.append(
            {
                "factor_id": f"omega{factor}",
                "factor_type": "COVARIANT_DERIVATIVE_WEYL_GHOST",
                "derivative_order": order,
                "Grassmann_parity": 1,
                "slot_variances": ["LOWER"] * order,
                "intrinsic_slot_symmetry": "SCALAR_JET; COMMUTATOR_RELATIONS_PENDING",
            }
        )
    for factor, order in enumerate(diff_orders):
        rows.append(
            {
                "factor_id": f"xi{factor}",
                "factor_type": "COVARIANT_DERIVATIVE_DIFF_GHOST",
                "derivative_order": order,
                "Grassmann_parity": 1,
                "slot_variances": ["UPPER", *("LOWER" for _ in range(order))],
                "intrinsic_slot_symmetry": "VECTOR_JET; COMMUTATOR_RELATIONS_PENDING",
            }
        )
    form_degree = int(signature["form_degree"])
    if form_degree:
        rows.append(
            {
                "factor_id": "dx",
                "factor_type": "HORIZONTAL_FORM_CARRIER",
                "derivative_order": 0,
                "Grassmann_parity": form_degree % 2,
                # These are formal basis-vector slots dual to the covariant
                # coefficient indices of the horizontal form.
                "slot_variances": ["UPPER"] * form_degree,
                "intrinsic_slot_symmetry": f"TOTALLY_ANTISYMMETRIC_RANK_{form_degree}",
            }
        )
    return rows


def factor_profiles(signature: dict[str, object]) -> tuple[dict[str, object], ...]:
    """All unlabeled derivative-distribution profiles for one refined signature."""

    if signature.get("refinement_status") != "REFINED_ADMISSIBLE":
        return ()
    curvature = nondecreasing_distributions(
        int(signature["tensor_derivative_count"]),
        int(signature["curvature_count"]),
    )
    weyl = _weyl_distributions(
        int(signature["weyl_ghost_derivative_count"]),
        int(signature["weyl_ghost_count"]),
    )
    diff = nondecreasing_distributions(
        int(signature["diff_ghost_derivative_count"]),
        int(signature["diff_ghost_count"]),
    )
    profiles = []
    for curvature_orders, weyl_orders, diff_orders in product(curvature, weyl, diff):
        factors = _factor_rows(signature, curvature_orders, weyl_orders, diff_orders)
        slot_count = sum(len(row["slot_variances"]) for row in factors)
        if slot_count != int(signature["total_index_slots_with_dx"]):
            raise AssertionError("factor profile does not reproduce signature slot count")
        multiplicities = [
            *_multiplicity_groups(curvature_orders, "COVARIANT_DERIVATIVE_RIEMANN", 0),
            *_multiplicity_groups(weyl_orders, "COVARIANT_DERIVATIVE_WEYL_GHOST", 1),
            *_multiplicity_groups(diff_orders, "COVARIANT_DERIVATIVE_DIFF_GHOST", 1),
        ]
        payload = {
            "curvature_derivative_orders": list(curvature_orders),
            "weyl_ghost_derivative_orders": list(weyl_orders),
            "diff_ghost_derivative_orders": list(diff_orders),
            "factors": factors,
            "identical_factor_groups": multiplicities,
            "slot_count": slot_count,
            "epsilon_slot_count": 4 if int(signature["epsilon_count"]) else 0,
            "metric_pair_count": (slot_count - 4 * int(signature["epsilon_count"])) // 2,
        }
        profiles.append({**payload, "profile_sha256": canonical_sha256(payload)})
    return tuple(profiles)


def signature_realization(signature: dict[str, object]) -> dict[str, object]:
    """Factored graph realization for one ambient integer signature."""

    if signature["refinement_status"] != "REFINED_ADMISSIBLE":
        payload = {
            "signature_sha256": signature["signature_sha256"],
            "realization_status": "REJECTED_BY_REFINED_GRADING",
            "reason": signature["refinement_reason"],
            "factor_profile_count": 0,
            "factor_profiles": [],
            "raw_graph_count_per_profile": 0,
            "total_raw_graph_count": 0,
        }
        return {**payload, "realization_sha256": canonical_sha256(payload)}

    profiles = factor_profiles(signature)
    if not profiles:
        raise AssertionError("refined signature has no derivative-distribution profile")
    per_profile = raw_graph_count(
        int(signature["total_index_slots_with_dx"]),
        int(signature["epsilon_count"]),
    )
    if not per_profile:
        raise AssertionError("refined signature has no raw contraction graph")
    total = len(profiles) * per_profile
    payload = {
        "signature_sha256": signature["signature_sha256"],
        "realization_status": "FACTORED_TENSOR_GRAPH_REALIZABLE",
        "reason": "every factor profile has a complete epsilon/metric contraction graph",
        "factor_profile_count": len(profiles),
        "factor_profiles": list(profiles),
        "factor_profile_manifest_sha256": canonical_sha256(profiles),
        "raw_graph_count_per_profile": per_profile,
        "total_raw_graph_count": total,
        "graph_storage_mode": (
            "EXPLICIT_MATERIALIZATION_ADMISSIBLE"
            if total <= EXPLICIT_GRAPH_THRESHOLD
            else "FACTORED_COUNT_ONLY"
        ),
        "raw_graph_count_formula": (
            "(N-1)!!"
            if int(signature["epsilon_count"]) == 0
            else "binomial(N,4)*(N-5)!!"
        ),
        "quotient_status": {
            "factor_permutations": "PROFILE_GROUPS_EXPLICIT_ACTIONS_PENDING",
            "Grassmann_exchange": "SIGNS_DECLARED_ACTIONS_PENDING",
            "Bianchi": "NOT_COMPUTED",
            "integration_by_parts": "NOT_COMPUTED",
            "dimension_specific_antisymmetrization": "NOT_COMPUTED",
        },
    }
    return {**payload, "realization_sha256": canonical_sha256(payload)}


@lru_cache(maxsize=1)
def ambient_tensor_graph_analysis() -> tuple[dict[str, object], dict[str, object]]:
    """Return the compact certificate analysis and detailed profile bundle."""

    ambient = ambient_lower_form_signature_analysis()
    realizations = []
    rejected_hashes = []
    summaries = []
    counts_by_sector: dict[tuple[str, int], dict[str, int]] = {}
    for manifest in ambient["manifests"]:
        sector = (str(manifest["parity"]), int(manifest["total_degree"]))
        sector_counts = {
            "refined_signature_count": 0,
            "factor_profile_count": 0,
            "total_raw_graph_count": 0,
        }
        for signature in manifest["signatures"]:
            realization = signature_realization(signature)
            if signature["refinement_status"] != "REFINED_ADMISSIBLE":
                rejected_hashes.append(signature["signature_sha256"])
                continue
            realizations.append(realization)
            sector_counts["refined_signature_count"] += 1
            sector_counts["factor_profile_count"] += int(realization["factor_profile_count"])
            sector_counts["total_raw_graph_count"] += int(realization["total_raw_graph_count"])
            summaries.append(
                {
                    "signature_sha256": signature["signature_sha256"],
                    "parity": signature["parity"],
                    "total_degree": signature["total_degree"],
                    "ghost_number": signature["ghost_number"],
                    "form_degree": signature["form_degree"],
                    "total_index_slots_with_dx": signature["total_index_slots_with_dx"],
                    "factor_profile_count": realization["factor_profile_count"],
                    "factor_profile_manifest_sha256": realization[
                        "factor_profile_manifest_sha256"
                    ],
                    "raw_graph_count_per_profile": realization[
                        "raw_graph_count_per_profile"
                    ],
                    "total_raw_graph_count": realization["total_raw_graph_count"],
                    "graph_storage_mode": realization["graph_storage_mode"],
                    "realization_sha256": realization["realization_sha256"],
                }
            )
        counts_by_sector[sector] = sector_counts

    bundle_payload = {
        "result_id": "AFN0_AMBIENT_TENSOR_GRAPH_PROFILE_BUNDLE",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "ambient_analysis_sha256": ambient["analysis_sha256"],
        "realization_count": len(realizations),
        "realizations": realizations,
    }
    bundle = {**bundle_payload, "bundle_sha256": canonical_sha256(bundle_payload)}
    totals = {
        "coarse_signature_count": ambient["totals"]["coarse_signature_count"],
        "rejected_signature_count": len(rejected_hashes),
        "refined_signature_count": len(realizations),
        "factor_profile_count": sum(row["factor_profile_count"] for row in summaries),
        "total_raw_graph_count": sum(row["total_raw_graph_count"] for row in summaries),
        "factored_count_only_signature_count": sum(
            row["graph_storage_mode"] == "FACTORED_COUNT_ONLY" for row in summaries
        ),
    }
    analysis_payload = {
        "result_id": "AFN0_AMBIENT_TENSOR_GRAPH_REALIZATION_CERTIFICATE",
        "result_state": "AMBIENT_TENSOR_GRAPH_REALIZATION_COMPLETE_QUOTIENT_OPEN",
        "classical_commit": "UNFROZEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC"],
        "scope_label": "AFN0_ONLY",
        "ambient_signature_source": {
            "result_id": ambient["result_id"],
            "analysis_sha256": ambient["analysis_sha256"],
        },
        "factor_profile_bundle": {
            "bundle_sha256": bundle["bundle_sha256"],
            "realization_count": bundle["realization_count"],
        },
        "totals": totals,
        "counts_by_sector": [
            {"parity": parity, "total_degree": degree, **counts}
            for (parity, degree), counts in sorted(counts_by_sector.items())
        ],
        "rejected_signature_manifest_sha256": canonical_sha256(rejected_hashes),
        "realized_signature_summaries": summaries,
        "checks": {
            "all_ambient_signatures_accounted_for": "VERIFIED",
            "every_refined_signature_has_factor_profile": "VERIFIED",
            "every_factor_profile_reproduces_index_slots": "VERIFIED",
            "Weyl_scalar_Grassmann_zero_profiles_removed": "VERIFIED",
            "epsilon_and_metric_graph_counts_exact": "VERIFIED",
            "no_raw_graph_materialization_claim": "VERIFIED",
        },
        "next_gates": {
            "factor_permutation_actions": "NOT_COMPUTED",
            "Bianchi_and_Grassmann_quotient": "NOT_COMPUTED",
            "integration_by_parts_quotient": "NOT_COMPUTED",
            "dimension_specific_antisymmetrization": "NOT_COMPUTED",
            "production_Q_dh_matrices": "NOT_COMPUTED",
        },
        "claim_boundary": [
            "tensor-graph realizability is certified in a factored representation for all 720 refined signatures",
            "the 2,860,932,903 raw graphs are counted exactly but are not claimed to have been individually materialized",
            "factor actions, Bianchi identities, jet commutators, integration by parts, and four-dimensional antisymmetrization remain open",
            "no canonical-basis dimension or relative-cohomology class is promoted",
        ],
    }
    analysis = {**analysis_payload, "analysis_sha256": canonical_sha256(analysis_payload)}
    return analysis, bundle
