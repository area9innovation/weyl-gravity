#!/usr/bin/env python3
"""Independent verifier for the BT residual-tilt Jacobian cancellation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CERT = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "certificates",
    "REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_TILT_JACOBIAN_CANCELLATION_V1.json",
)
SCHEMA_PATH = os.path.join(
    REPO_ROOT,
    "reverse_physics",
    "schema",
    "reverse-physics-bt-euclidean-residual-tilt-jacobian-cancellation-v1.schema.json",
)


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def file_hash(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(REPO_ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def cycle_fixture(omega: list[Fraction]) -> dict[str, object]:
    """Reconstruct the C4 residual, action, tree sum, and coarea factor."""
    residual = [
        (omega[(site - 1) % 4] + omega[(site + 1) % 4]) / omega[site] - 2
        for site in range(4)
    ]
    action = sum((entry * entry for entry in residual), Fraction(0)) / 2
    edges = [omega[site] * omega[(site + 1) % 4] for site in range(4)]
    edge_product = edges[0] * edges[1] * edges[2] * edges[3]
    tree_terms = [edge_product / edge for edge in edges]
    tree_sum = sum(tree_terms, Fraction(0))
    norm_square = sum((entry**4 for entry in omega), Fraction(0))
    # The two declared fixtures have the same rational norm 17/4.
    norm = Fraction(17, 4)
    if norm * norm != norm_square:
        raise ValueError("independent fixture no longer has rational Omega^2 norm")
    return {
        "omega": omega,
        "residual": residual,
        "action": action,
        "tree_terms": tree_terms,
        "tree_sum": tree_sum,
        "coarea": 2 * norm * tree_sum,
    }


def verify(path: str = DEFAULT_CERT) -> bool:
    checks: dict[str, bool] = {}
    errors = []
    try:
        with open(path, encoding="utf-8") as handle:
            certificate = json.load(handle)
        with open(SCHEMA_PATH, encoding="utf-8") as handle:
            schema = json.load(handle)
        errors = sorted(
            Draft202012Validator(schema).iter_errors(certificate),
            key=lambda error: list(error.path),
        )
        checks["strict_schema"] = not errors

        public = certificate["exact_cycle_tilt"]
        base = cycle_fixture(
            [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
        )
        shifted = cycle_fixture(
            [Fraction(2), Fraction(1), Fraction(1), Fraction(1, 2)]
        )
        checks["unit_product_tilt_fixture_rederived"] = (
            __import__("math").prod(base["omega"]) == 1
            and __import__("math").prod(shifted["omega"]) == 1
            and base["omega"] == [decode(value) for value in public["base_omega"]]
            and shifted["omega"]
            == [decode(value) for value in public["shifted_omega"]]
        )
        checks["residuals_and_actions_rederived"] = (
            base["residual"]
            == [decode(value) for value in public["base_residual"]]
            == [Fraction(1, 2), Fraction(-1), Fraction(1, 2), Fraction(2)]
            and shifted["residual"]
            == [decode(value) for value in public["shifted_residual"]]
            == [Fraction(-5, 4), Fraction(1), Fraction(-1, 2), Fraction(4)]
            and base["action"] == decode(public["base_action"]) == Fraction(11, 4)
            and shifted["action"]
            == decode(public["shifted_action"])
            == Fraction(301, 32)
        )
        checks["tree_terms_rederived"] = (
            base["tree_terms"]
            == [decode(value) for value in public["base_tree_terms"]]
            == [Fraction(1, 2), Fraction(1, 2), Fraction(2), Fraction(2)]
            and shifted["tree_terms"]
            == [decode(value) for value in public["shifted_tree_terms"]]
            == [Fraction(1, 2), Fraction(1), Fraction(2), Fraction(1)]
            and base["tree_sum"]
            == decode(public["base_tree_density"])
            == Fraction(5)
            and shifted["tree_sum"]
            == decode(public["shifted_tree_density"])
            == Fraction(9, 2)
        )
        checks["coarea_factors_rederived"] = (
            base["coarea"]
            == decode(public["base_coarea_jacobian"])
            == Fraction(85, 2)
            and shifted["coarea"]
            == decode(public["shifted_coarea_jacobian"])
            == Fraction(153, 4)
        )

        surface_ratio = shifted["coarea"] / base["coarea"]
        inverse_ratio = base["coarea"] / shifted["coarea"]
        checks["surface_and_density_ratios_rederived"] = (
            surface_ratio
            == decode(public["surface_jacobian_ratio"])
            == Fraction(9, 10)
            and inverse_ratio
            == decode(public["inverse_density_jacobian_ratio"])
            == Fraction(10, 9)
        )
        checks["jacobian_cancellation_rederived"] = (
            surface_ratio * inverse_ratio
            == decode(public["cancellation_product"])
            == 1
        )
        action_gap = shifted["action"] - base["action"]
        coupling = decode(public["coupling"])
        checks["action_and_boltzmann_gaps_rederived"] = (
            coupling == Fraction(2, 5)
            and action_gap == decode(public["action_gap"]) == Fraction(213, 32)
            and action_gap / (coupling * coupling)
            == decode(public["boltzmann_exponent_gap"])
            == Fraction(5325, 128)
            and public["weighted_pullback_ratio"] == "exp(-5325/128)"
        )

        theorem = certificate["general_tilt_theorem"]
        checks["general_chain_rule_theorem_is_typed"] = (
            theorem["status"] == "PROVED"
            and "Jac_H(psi+t h)/Jac_H(psi)" in theorem["surface_jacobian"]
            and "exp[-S(psi+t h)+S(psi)]" in theorem["pullback_ratio"]
            and "determinant one" in theorem["proof"]
        )
        marginal = certificate["conditional_marginal_reduction"]
        checks["flat_fiber_marginal_is_typed"] = (
            marginal["tree_factor"] == "CANCELLED_EXACTLY"
            and marginal["status"] == "EXACT_ACTION_FIBER_REDUCTION_ONLY"
            and "exp[-S(eta+s h)]" in marginal["marginal"]
            and "uniformly in lattice volume" in marginal["remaining_problem"]
        )
        disposition = certificate["method_disposition"]
        checks["method_boundary_is_fail_closed"] = (
            disposition["inverse_tree_jacobian_cancellation"] == "PROVED"
            and disposition["tree_log_convexity_as_extra_tilt_confinement"]
            == "OBSTRUCTED"
            and disposition["direct_action_difference_or_fiber_ratio_bound"]
            == "OPEN"
            and disposition["normalized_lowest_mode_marginal_bound"] == "OPEN"
            and disposition[
                "actual_interacting_h_minus_one_second_moment_bound"
            ]
            == "OPEN"
            and disposition["interacting_tightness"] == "NOT_ESTABLISHED"
            and disposition["continuum_limit"] == "NOT_ESTABLISHED"
            and disposition["born_rule"] == "NOT_ESTABLISHED"
            and disposition["krein_reconstruction"] == "NOT_ASSESSED"
            and disposition["lorentzian_transfer"] == "NOT_ESTABLISHED"
        )
        foundation = certificate["foundational_dependency_cut"]
        checks["foundational_boundary_is_fail_closed"] = (
            foundation["classification"] == "USED_BY_DISPLAYED_PROOF"
            and foundation["weakest_base_or_reversal"] == "NOT_ESTABLISHED"
            and "all-volume" in foundation["uniform_limit_layer"]
        )
        checks["missing_objects_name_the_actual_gate"] = all(
            any(token in item for item in certificate["missing_object_ledger"])
            for token in ("conditional-fiber", "one-mode", "dyadic-shell", "tightness")
        )
        nonclaims = certificate["does_not_establish"]
        checks["required_nonclaims_are_explicit"] = all(
            any(token in statement for statement in nonclaims)
            for token in (
                "action-difference",
                "lowest-mode",
                "H^-1",
                "continuum",
                "Born",
                "Krein",
                "LORENTZIAN-CAUSAL",
                "literature-priority",
            )
        )
        provenance = certificate["provenance"]
        checks["input_hash_matches"] = (
            len(provenance["inputs"]) == 1
            and provenance["inputs"][0]["sha256"]
            == file_hash(provenance["inputs"][0]["path"])
            and "Exact Fraction arithmetic" in provenance["arithmetic"]
        )
        checks["dependency_tags_are_exact"] = certificate["dependency_tags"] == [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
        ]
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"[FAIL] verifier exception: {exc}")
        return False

    if not all(checks.values()):
        for error in errors[:3]:
            print(f"[FAIL] schema: {error.message}")
        for name, ok in checks.items():
            if not ok:
                print(f"[FAIL] {name}")
        return False
    print(
        "[PASS] independent BT residual-tilt Jacobian cancellation verifier "
        f"({sum(checks.values())}/{len(checks)})"
    )
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", default=DEFAULT_CERT)
    args = parser.parse_args(argv)
    return 0 if verify(args.certificate) else 1


if __name__ == "__main__":
    sys.exit(main())
