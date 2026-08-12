#!/usr/bin/env python3
"""Independent verification of the BT six-point positive-distribution no-go."""
import hashlib
import json
import os
import sys

import sympy as sp
from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_POSITIVE_DISTRIBUTION_COMPLETION_NO_GO_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-six-point-positive-distribution-completion-no-go-v1.schema.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def file_hash(relative_path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative_path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    epsilon, length, s = sp.symbols("epsilon length s", positive=True)
    punctured_mass = 2 * sp.integrate(sp.Rational(9, 8) / s**2, (s, epsilon, length))
    regulated_mass = sp.integrate(
        sp.Rational(9, 8) / (s**2 + epsilon**2),
        (s, -length, length),
    )
    leading_delta = sp.Rational(9, 8) * sp.pi / epsilon
    theorem = certificate["exact_distribution_theorem"]
    preflight = certificate["symmetric_feynman_modulus_preflight"]
    typed = certificate["typed_candidate_audit"]
    interpretation = certificate["interpretation"]
    checks = {
        "schema_validation": not list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate)),
        "all_input_hashes_match": all(row["sha256"] == file_hash(row["path"]) for row in certificate["provenance"]["inputs"]),
        "punctured_mass_recomputed": sp.simplify(
            punctured_mass
            - sp.sympify(theorem["punctured_mass"], locals={"epsilon": epsilon, "length": length})
        ) == 0,
        "punctured_mass_diverges": sp.limit(punctured_mass, epsilon, 0, dir="+") == sp.oo,
        "regulated_mass_recomputed": sp.simplify(
            regulated_mass
            - sp.sympify(
                preflight["constant_test_on_minus_L_to_L"],
                locals={"epsilon": epsilon, "length": length},
            )
        ) == 0,
        "regulated_remainder_recomputed": sp.limit(regulated_mass - leading_delta, epsilon, 0, dir="+") == -sp.Rational(9, 4) / length,
        "positive_extension_is_refused": theorem["conclusion"] == "NO_LOCALLY_FINITE_POSITIVE_EXTENSION",
        "extension_ambiguity_is_explicit": theorem["scaling_degree"] == 2 and theorem["reflection_even_ambiguity"] == "c0*delta(s)",
        "candidate_orders_are_distinct": typed["perturbative_orders"]["six_point_tree_density"] == "lambda^8" and "lambda^6" in typed["perturbative_orders"]["available_five_point_NLO_response"],
        "candidate_supports_are_distinct": typed["new_singular_support"] != typed["existing_NLO_support"],
        "projector_is_not_misused": typed["public_Rt_role"] == "PROJECTOR_PUSHFORWARD_NOT_PHYSICAL_SMATRIX_SUMMAND",
        "abstract_completion_is_not_promoted": interpretation["abstract_unitary_completion"] == "EXISTS_BUT_IS_NOT_BT_AFFILIATED",
        "physical_probability_remains_open": interpretation["finite_inclusive_probability"] == "NOT_CONSTRUCTED",
        "minimal_gate_is_concrete": certificate["minimal_missing_physical_input"]["status"] == "NOT_CONSTRUCTED" and len(certificate["minimal_missing_physical_input"]["required_features"]) == 5,
        "claim_boundary_is_preserved": "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"] and interpretation["Eq19_all_orders"] == "NOT_PROVED",
    }
    return {name: bool(value) for name, value in checks.items()}


def main():
    checks = verify(load(CERT))
    failures = [name for name, ok in checks.items() if not ok]
    print("checks %d/%d" % (sum(checks.values()), len(checks)))
    print("RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
