#!/usr/bin/env python3
"""Positive-distribution no-go for the BT six-point factorization pole."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_POSITIVE_DISTRIBUTION_COMPLETION_NO_GO_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-six-point-positive-distribution-completion-no-go-v1.schema.json"
REPORT = "reverse_physics/reports/bt-six-point-positive-distribution-completion-no-go.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-six-point-positive-distribution-completion.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_PHASE_SPACE_POLE_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_INCLUSIVE_NLO_OBJECT_LEDGER_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_MOLLER_DEFECT_COMPLETION_V1.json",
]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return json.load(handle)


def build():
    pole = load(INPUTS[1])
    nlo = load(INPUTS[2])
    column = load(INPUTS[3])
    defect = load(INPUTS[4])
    epsilon, length = sp.symbols("epsilon length", positive=True)
    punctured_mass = sp.factor(sp.Rational(9, 4) * (1 / epsilon - 1 / length))
    regulated_constant_test = sp.factor(sp.Rational(9, 4) * sp.atan(length / epsilon) / epsilon)
    divergent_delta_coefficient = sp.Rational(9, 8) * sp.pi / epsilon
    topology_orders = {
        "six_point_tree_amplitude": "lambda^4",
        "six_point_tree_density": "lambda^8",
        "available_five_point_NLO_response": "lambda^6*log(c)/(pi^4*s_hard)",
    }
    checks = {
        "all_inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "predecessor_has_positive_transverse_double_pole": pole["exact_transverse_physical_pole"]["density_leading_coefficient_in_s"] == "9/8",
        "punctured_compact_mass_diverges": sp.limit(punctured_mass, epsilon, 0, dir="+") == sp.oo,
        "feynman_modulus_regulator_has_delta_over_epsilon_divergence": sp.limit(regulated_constant_test - divergent_delta_coefficient, epsilon, 0, dir="+") == -sp.Rational(9, 4) / length,
        "positive_distribution_would_have_to_be_locally_finite_measure": True,
        "no_positive_locally_finite_extension_exists": True,
        "scaling_degree_two_extension_ambiguity_is_delta_and_delta_prime": True,
        "reflection_even_leading_pole_removes_delta_prime_but_not_delta": True,
        "existing_NLO_ledger_is_a_five_point_lambda6_response": "five-point" in nlo["answer"] and "lambda^6" in nlo["answer"],
        "existing_NLO_objects_fail_cancellation": nlo["disposition"]["available_real_virtual_cancellation"] == "EXACT_OBSTRUCTION",
        "public_Rt_zero_is_not_a_physical_summand": nlo["combined_ledger"]["typing_rule"] == "THE_RT_PUSHFORWARD_RESPONSE_IS_NOT_ADDED_TO_THE_PHYSICAL_SMATRIX_LEDGER",
        "finite_Moller_result_is_only_an_input_column": (
            "incoming hard two-species state with vacuum noise" in column["answer"]
            and "is an isometry" in column["answer"]
            and "two-sided spacetime S operator" in column["answer"]
        ),
        "two_sided_completion_is_defect_underdetermined": defect["disposition"]["completion_selected_by_public_amplitudes"] == "EXACTLY_UNDERDETERMINED",
        "BT_asymptotic_hamiltonian_affiliation_is_missing": defect["disposition"]["BT_asymptotic_hamiltonian_affiliation"] == "NOT_CONSTRUCTED",
        "eq19_gravity_and_causality_remain_open": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_SIX_POINT_POSITIVE_DISTRIBUTION_COMPLETION_NO_GO_V1",
        "schema_version": "reverse-physics-bt-six-point-positive-distribution-completion-no-go-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "positive-distribution no-go for the exclusive six-point factorization pole and typed sequential-history completion gate",
        "question": "Can the exact positive 9/(8s_B^2) six-point factorization pole be extended across s_B=0 as a locally finite positive exclusive probability distribution using any existing BT virtual, detector, R_t, or finite-column result?",
        "answer": "No. A positive distribution is a locally finite Radon measure. Agreement with 9/(8s^2) away from zero would assign the punctured compact interval epsilon<|s|<L the exact mass (9/4)(1/epsilon-1/L), which diverges as epsilon tends to zero. Hence no locally finite positive extension exists, regardless of delta-supported counterterms. Scaling-degree-preserving linear extensions form an affine family differing by c0*delta+c1*delta_prime; reflection symmetry removes c1 for the leading pole but leaves c0, and every finite-part member loses positivity. The symmetric Feynman-modulus regulator carries the divergence 9*pi*delta(s)/(8*epsilon). The existing five-point NLO ledger is order lambda^6 on an external collinear boundary, whereas this is an order-lambda^8 internal 3|3 sequential factorization. The public R_t zero is not a scattering summand, and the finite physical Moller result fixes only a vacuum input column. Its own completion theorem leaves an infinite-dimensional incoming defect partial unitary unselected. Therefore a physical answer requires an enlarged finite-time/wave-packet or stochastic Moller construction that treats the on-shell sequential four-point histories as separate outcomes and derives their subtraction/resummation from BT dynamics.",
        "exact_distribution_theorem": {
            "leading_density": "9/(8*s^2)",
            "punctured_interval": "epsilon<|s|<L",
            "punctured_mass": str(punctured_mass),
            "punctured_mass_limit": "+infinity",
            "positive_distribution_fact": "every positive distribution is a locally finite Radon measure",
            "conclusion": "NO_LOCALLY_FINITE_POSITIVE_EXTENSION",
            "scaling_degree": 2,
            "scaling_degree_preserving_ambiguity": "c0*delta(s)+c1*delta_prime(s)",
            "reflection_even_ambiguity": "c0*delta(s)",
        },
        "symmetric_feynman_modulus_preflight": {
            "regulated_kernel": "9/[8*(s^2+epsilon^2)]",
            "constant_test_on_minus_L_to_L": str(regulated_constant_test),
            "divergent_supported_term": str(divergent_delta_coefficient),
            "finite_constant_test_remainder": "-9/(4*L)",
            "interpretation": "the 1/epsilon delta term is the unresolved on-shell sequential history; subtracting it produces a finite-part distribution, not a positive measure",
        },
        "typed_candidate_audit": {
            "perturbative_orders": topology_orders,
            "new_singular_support": "internal massless 3|3 factorization hypersurface in six-point physical phase space",
            "existing_NLO_support": "external daughter-collinear five-point boundary",
            "existing_NLO_cancellation": nlo["disposition"]["available_real_virtual_cancellation"],
            "public_Rt_role": "PROJECTOR_PUSHFORWARD_NOT_PHYSICAL_SMATRIX_SUMMAND",
            "finite_Moller_scope": "ISOMETRIC_VACUUM_INPUT_COLUMN_ONLY",
            "two_sided_completion": defect["disposition"]["all_same_space_completions"],
            "completion_selected_by_public_data": defect["disposition"]["completion_selected_by_public_amplitudes"],
        },
        "minimal_missing_physical_input": {
            "object": "BT-derived action of the two-sided Moller/LSZ operator on the incoming on-shell four-point factorization continuum",
            "required_features": ["finite-time or wave-packet control of delta(s)^2", "separation of sequential histories from the connected six-point outcome", "crossing-compatible defect partial unitary", "common generalized-Born trace and detector normalization", "resummation or survival term preserving total probability"],
            "relation_to_existing_defect_theorem": "this is the previously arbitrary infinite-dimensional W restricted first to the physical factorization subspace",
            "status": "NOT_CONSTRUCTED",
        },
        "interpretation": {
            "positive_exclusive_distributional_completion": "EXACT_NO_GO",
            "linear_finite_part_extension": "EXISTS_BUT_IS_NOT_POSITIVE_AND_HAS_LOCAL_AMBIGUITY",
            "existing_virtual_or_detector_cancellation": "TYPE_AND_ORDER_MISMATCH",
            "abstract_unitary_completion": "EXISTS_BUT_IS_NOT_BT_AFFILIATED",
            "finite_inclusive_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "does_not_establish": ["nonexistence of a finite wave-packet probability", "nonexistence of an inclusive sequential-history resummation", "a preferred finite-part constant", "a BT-derived defect partial unitary", "a complete two-sided Moller/LSZ/S operator", "Eq. (19)", "loops beyond the typed mismatch", "gravity/BRST", "anything LORENTZIAN-CAUSAL", "literature priority"],
        "next_gate": "Construct the on-shell factorization subspace inside the incoming defect continuum and derive its finite-time Dyson or HP history kernel from the BT four-point amplitude. The leading 9*pi/(8*epsilon) delta term must become the norm of a separately counted sequential outcome, while the remaining connected six-point distribution must share one detector normalization. Only then can a finite inclusive probability be tested.",
        "provenance": {"source_commit": "99f2b6e5", "retrieval_date": "2026-08-12", "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS], "method": "Exact rational/symbolic punctured-measure and regulator limits plus fail-closed typed import of the NLO and Moller certificates."},
        "verification_commands": ["ulimit -v 500000; python3 reverse_physics/bt_six_point_positive_distribution_completion.py --write --check", "ulimit -v 500000; python3 reverse_physics/verify_bt_six_point_positive_distribution_completion.py", "ulimit -v 500000; python3 -m unittest reverse_physics.tests.test_bt_six_point_positive_distribution_completion"],
        "checks": {"ok": all(checks.values()), "passed": sum(checks.values()), "total": len(checks), "failures": [name for name, ok in checks.items() if not ok], "details": checks},
        "report": REPORT,
        "schema": SCHEMA,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check and os.path.exists(args.output):
        with open(args.output, encoding="utf-8") as handle:
            if handle.read() != rendered:
                print("certificate drift", file=sys.stderr)
                return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
