#!/usr/bin/env python3
"""Independent verifier for the object-typed BT inclusive NLO ledger."""
import argparse
import hashlib
import json
import os
from fractions import Fraction

from jsonschema import Draft202012Validator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_INCLUSIVE_NLO_OBJECT_LEDGER_V1.json")
SCHEMA = os.path.join(ROOT, "reverse_physics/schema/reverse-physics-bt-inclusive-nlo-object-ledger-v1.schema.json")


def load(path):
    with open(path) as handle:
        return json.load(handle)


def rational(value):
    return Fraction(value["numerator"], value["denominator"])


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(certificate):
    schema_errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    objects = certificate.get("object_types", {})
    physical = objects.get("physical_process", {})
    projector = objects.get("projector_pushforward", {})
    combined = certificate.get("combined_ledger", {})
    correction = certificate.get("correction", {})
    disposition = certificate.get("disposition", {})

    born = rational(combined.get("Born_coefficient_without_common_factors", {"numerator": 0, "denominator": 1}))
    pair = rational(physical.get("real_pair_absolute_response", {"numerator": 0, "denominator": 1}))
    total = rational(physical.get("real_three_pair_absolute_response", {"numerator": 0, "denominator": 1}))
    virtual = rational(combined.get("physical_virtual_ratio_response", {"numerator": 1, "denominator": 1}))
    rt_response = rational(combined.get("nonphysical_Rt_comparison_response", {"numerator": 1, "denominator": 1}))
    available = rational(combined.get("available_physical_real_plus_virtual_response", {"numerator": 0, "denominator": 1}))
    required = rational(combined.get("required_unconstructed_physical_matching_response", {"numerator": 0, "denominator": 1}))

    real_source = load(os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json"))
    closure_source = load(os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_FULL_SIGNED_QUADRATIC_CLOSURE_V1.json"))
    predecessor = load(os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_INCLUSIVE_PHYSICAL_COEFFICIENT_V1.json"))

    checks = {
        "schema": not schema_errors,
        "source_real_response": real_source.get("phase_and_combinatorics", {}).get("per_pair_finite_part_shift") == "+lambda^6*log(c_pair)/(512*pi^4*s)" and real_source.get("phase_and_combinatorics", {}).get("common_three_pair_shift") == "+3*lambda^6*log(c)/(512*pi^4*s)",
        "source_virtual_response": real_source.get("virtual_comparison", {}).get("axis_compatible_parent_response") == "lim_(r->0) log(G(x,c*r*x)/G(x,r*x))=0",
        "source_Rt_response": rational(closure_source.get("coefficient_disposition", {}).get("completed_public_quadratic_map_soft_log_per_pair", {"numerator": 1, "denominator": 1})) == 0,
        "exact_normalization": born == Fraction(3, 32) and pair == Fraction(1, 512) and total == 3 * pair == Fraction(3, 512) and pair / born == Fraction(1, 48) and total / born == Fraction(1, 16),
        "physical_sum_and_separate_Rt": virtual == 0 and rt_response == 0 and available == total + virtual == Fraction(3, 512) and required == -available and combined.get("typing_rule") == "THE_RT_PUSHFORWARD_RESPONSE_IS_NOT_ADDED_TO_THE_PHYSICAL_SMATRIX_LEDGER",
        "object_separation": projector.get("symbol") == "R_t P R_t^dagger" and physical.get("symbol") == "Pout(S-1)Pin" and projector.get("symbol") != physical.get("symbol"),
        "correction_boundary": predecessor.get("disposition", {}).get("physical_real_collinear_coefficient") == "ZERO" and correction.get("status") == "SUPERSEDED_OBJECT_IDENTIFICATION" and len(correction.get("retained_exact_results", [])) == 4,
        "claim_boundary": disposition.get("physical_real_emission_response") == "NONZERO" and disposition.get("public_Rt_compensating_response") == "ZERO_BUT_NOT_A_PHYSICAL_SUMMAND" and disposition.get("available_real_virtual_cancellation") == "EXACT_OBSTRUCTION" and disposition.get("physical_inclusive_NLO_probability") == "NOT_ESTABLISHED" and disposition.get("Eq19_all_orders") == "NOT_PROVED",
        "provenance_hashes": len(certificate.get("provenance", {}).get("inputs", [])) == 7 and all(row.get("sha256") == sha256(row.get("path", "")) for row in certificate.get("provenance", {}).get("inputs", [])),
        "producer_ledger": certificate.get("checks", {}).get("passed") == certificate.get("checks", {}).get("total") == 16 and certificate.get("checks", {}).get("failures") == [] and all(certificate.get("checks", {}).get("details", {}).values()),
    }
    for error in schema_errors:
        print("schema", list(error.path), error.message)
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        print("BT INCLUSIVE NLO OBJECT LEDGER VERIFY: FAIL", *failures, sep="\n  ")
        return False, checks
    return True, checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args()
    ok, checks = verify(load(args.verify))
    if not ok:
        return 1
    print(f"BT INCLUSIVE NLO OBJECT LEDGER VERIFY: ALL PASS ({sum(checks.values())}/{len(checks)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
