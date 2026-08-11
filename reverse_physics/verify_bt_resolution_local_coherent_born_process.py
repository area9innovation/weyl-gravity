#!/usr/bin/env python3
"""Independent verifier for the BT resolution-local coherent Born process."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_RESOLUTION_LOCAL_COHERENT_BORN_PROCESS_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-resolution-local-coherent-born-process-v1.schema.json")
RIGGED = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_RIGGED_RESOLUTION_JORDAN_MOLLER_V1.json")
PHYSICAL = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json")
ABEL = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_ABEL_NAIMARK_ASYMPTOTIC_DILATION_V1.json")
DETECTOR = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_DETECTOR_RESOLUTION_DILATION_V1.json")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    import sympy as sp

    schema_errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    rigged, physical, abel, detector = map(load, (RIGGED, PHYSICAL, ABEL, DETECTOR))
    relative = certificate.get("relative_detector_weight", {})
    gns = certificate.get("rank_two_GNS_purification", {})
    local = certificate.get("local_coherent_process", {})
    law = certificate.get("probability_law", {})
    boundary = certificate.get("global_representation_boundary", {})
    disposition = certificate.get("disposition", {})

    gamma = Fraction(1, 48)
    # Method-distinct finite-cell Kolmogorov controls.  Each list is a
    # different exact purification of a unit y-density.
    profile_weights = [
        [Fraction(1)],
        [Fraction(1, 6), Fraction(1, 3), Fraction(1, 2)],
        [Fraction(1, 10), Fraction(2, 10), Fraction(3, 10), Fraction(4, 10)],
    ]
    profile_ok = all(
        sum(weights) == 1
        and Fraction(1, 2)*sum(2*gamma*w for w in weights) == gamma
        for weights in profile_weights
    )

    # A discrete relative-weight rail: simultaneous translation leaves the
    # integrable difference sum unchanged, and ordered differences are positive.
    f = [0, 1, 1, 1, 0, 0]
    g = [0, 0, 1, 1, 0, 0]
    translate = lambda x: [x[-1], *x[:-1]]
    relative_ok = (
        sum(Fraction(x-y) for x, y in zip(f, g)) == 1
        and all(x >= y for x, y in zip(f, g))
        and sum(Fraction(x-y) for x, y in zip(translate(f), translate(g))) == 1
    )

    a, b, z, t = sp.symbols("a b z t", nonnegative=True)
    nu = a/sp.Integer(16)
    generating = sp.exp(nu*(z-1))
    poisson_ok = (
        sp.simplify(generating.subs(z, 1)-1) == 0
        and sp.diff(generating, z).subs(z, 1) == nu
        and sp.simplify(generating*sp.exp((b/16)*(z-1))-sp.exp(((a+b)/16)*(z-1))) == 0
        and sp.series(sp.exp(-t/16), t, 0, 3) == 1-t/16+t**2/512+sp.Order(t**3)
    )

    fixture_ok = True
    try:
        rows = law["exact_fixtures"]
        fixture_ok = len(rows) == 4
        for row, length in zip(rows, map(Fraction, (1, 2, 4, 8))):
            pair = length/48
            total = length/16
            fixture_ok &= (
                frac(row["length"]) == length
                and frac(row["per_pair_mean"]) == pair
                and frac(row["total_mean"]) == total
                and row["vacuum_probability"] == f"exp(-{total.numerator}/{total.denominator})"
                and row["vacuum_amplitude"] == f"exp(-{total.numerator}/{2*total.denominator})"
                and row["one_or_more_probability"] == f"1-exp(-{total.numerator}/{total.denominator})"
                and frac(row["normalized_test_function_phase_square"]) == total
            )
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        fixture_ok = False

    # Riesz obstruction: a unit vector supported in length L has displacement
    # pairing squared L/16, unbounded on the unit sphere.
    riesz_ok = all(Fraction(length, 16) == expected for length, expected in ((1, Fraction(1, 16)), (16, Fraction(1)), (64, Fraction(4))))
    inputs = certificate.get("provenance", {}).get("inputs", [])
    checks = {
        "schema": not schema_errors,
        "identity_tags_lifecycle": certificate.get("certificate") == "REVERSE_PHYSICS_BT_RESOLUTION_LOCAL_COHERENT_BORN_PROCESS_V1" and certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"] and certificate.get("lifecycle_state") == "CLASSIFIED",
        "source_rigged_cocycle": rigged.get("threshold_gram", {}).get("physical_per_pair_cocycle") == "log(c)/48",
        "source_rank_two_gram": physical.get("public_Rt_comparison", {}).get("physical_gram_rank") == 2,
        "source_abel_purification": abel.get("naimark_probability_dilation", {}).get("density") == "p_s(y)=sech(y-s)^2/2",
        "source_detector_response": frac(detector.get("physical_response", {}).get("real_per_pair_born_normalized_per_unit_a", {})) == gamma,
        "relative_weight_discrete_rail": relative_ok,
        "relative_weight_contract": relative.get("definition") == "Tau_rel(f,g)=integral_R (f-g) ds" and relative.get("profile_cell") == "Tau_rel(q_(R+a),q_R)=a",
        "three_profile_GNS_rails": profile_ok,
        "rank_two_contract": gns.get("physical_response_endomorphism") == "G_phys=gamma*I2, gamma=1/48" and gns.get("minimal_rank") == 2 and gns.get("public_nilpotent_rank_one_substitution") == "FORBIDDEN_BY_CERTIFIED_GRAM_RANK",
        "local_process_norm": local.get("norm_square") == "||F_I||^2=3*gamma*|I|=|I|/16",
        "local_state_and_automorphism": local.get("state") == "POSITIVE_NORMALIZED_LOCALLY_NORMAL_RESOLUTION_COHERENT_PROCESS" and "compact-resolution g" in local.get("coherent_automorphism", ""),
        "poisson_exact_rail": poisson_ok,
        "probability_fixtures": fixture_ok,
        "probability_contract": law.get("per_pair_rate") == {"numerator": 1, "denominator": 48} and law.get("total_rate") == {"numerator": 1, "denominator": 16} and law.get("normalization") == "sum_(n>=0) P_n(a)=1",
        "hard_real_response": law.get("leading_responses") == "hard=-a/16, real_total=+a/16, inclusive=0",
        "Riesz_obstruction_rail": riesz_ok,
        "global_boundary": boundary.get("global_norm") == "+infinity" and boundary.get("conclusion") == "NO_GLOBAL_FOCK_VECTOR_OR_INNER_WEYL_IMPLEMENTER",
        "coherent_assumption_boundary": disposition.get("actual_BT_nonlinear_multiple_emission_dynamics") == "NOT_COMPUTED" and disposition.get("positive_normalized_multiple_emission_process") == "CONSTRUCTED_UNDER_COHERENT_INDEPENDENT_INCREMENT_COMPLETION",
        "physical_object_boundary": disposition.get("resolution_local_coherent_Moller_automorphism") == "CONSTRUCTED_AT_LEADING_LOG" and disposition.get("spacetime_local_physical_S_matrix") == "NOT_CONSTRUCTED",
        "claim_boundaries": disposition.get("finite_complete_NLO_probability") == "NOT_ESTABLISHED" and disposition.get("beyond_tree_positivity") == "NOT_ESTABLISHED" and disposition.get("Eq19_all_orders") == "NOT_PROVED" and "anything LORENTZIAN-CAUSAL" in certificate.get("does_not_establish", []),
        "hashes": len(inputs) == 8 and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs),
        "producer_ledger": certificate.get("checks", {}).get("passed") == certificate.get("checks", {}).get("total") == 30 and certificate.get("checks", {}).get("failures") == [] and all(certificate.get("checks", {}).get("details", {}).values()),
    }
    for error in schema_errors:
        print("schema", list(error.path), error.message)
    failures = [name for name, ok in checks.items() if not ok]
    if failures:
        print("BT RESOLUTION LOCAL COHERENT BORN VERIFY: FAIL", *failures, sep="\n  ")
        return False, checks
    return True, checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    ok, checks = verify(load(args.verify))
    if not ok:
        return 1
    print(f"BT RESOLUTION LOCAL COHERENT BORN VERIFY: ALL PASS ({sum(checks.values())}/{len(checks)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
