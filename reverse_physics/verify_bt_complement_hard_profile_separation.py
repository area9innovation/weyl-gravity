#!/usr/bin/env python3
"""Independent verifier for BT complement/hard-profile parameter separation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COMPLEMENT_HARD_PROFILE_SEPARATION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-complement-hard-profile-separation-v1.schema.json",
)


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

    errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    if errors:
        return {"schema_validation": False}
    inputs = certificate["provenance"]["inputs"]
    inner = load(os.path.join(ROOT, inputs[1]["path"]))
    physical = load(os.path.join(ROOT, inputs[2]["path"]))
    moller = load(os.path.join(ROOT, inputs[3]["path"]))
    endpoint = load(os.path.join(ROOT, inputs[4]["path"]))
    shared = certificate["shared_fixture"]

    a0, a1, tau, h = sp.symbols("a0 a1 tau h")
    rho_formula = (
        (a0 - a1) ** 2
        * (2 * tau * (a0 + a1) - (a0 - a1) ** 2)
        / (4 * tau**3)
    )
    rho = Fraction(rho_formula.subs({a0: 1, a1: 4, tau: 10}))
    c1 = Fraction(7, 4) + rho / 2
    G = sp.Matrix(
        [
            [0, -sp.Rational(rho.numerator, rho.denominator)],
            [-sp.Rational(rho.numerator, rho.denominator), -2],
        ]
    )
    hard = inner["profile_analysis"]["hard_fixtures"]
    hard_values = [Fraction(row[0][-1]) for row in hard]
    coefficients = [
        frac(row)
        for row in inner["inner_threshold"]["fixture_r_log_r_coefficients"]
    ]
    difference = frac(
        inner["inner_threshold"]["hard_difference_r_log_r_coefficient"]
    )
    endpoint_row = endpoint["physical_fixtures"][0]
    imported_gram = sp.Matrix(
        [[sp.Rational(frac(value).numerator, frac(value).denominator)
          for value in row]
         for row in endpoint_row["matched_gram"]]
    )
    checks = {
        "schema_validation": True,
        "all_input_hashes_match": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "all_predecessor_checks_pass": all(
            value["checks"]["ok"] for value in (inner, physical, moller, endpoint)
        ),
        "rho_formula_reconstruction": (
            rho == Fraction(819, 4000)
            and h not in rho_formula.free_symbols
            and shared["rho_formula"] == str(sp.factor(rho_formula))
        ),
        "hard_fixture_difference_is_only_33_to_34": (
            hard[0][1:] == hard[1][1:]
            and hard[0][0][:-1] == hard[1][0][:-1]
            and hard_values == [Fraction(33), Fraction(34)]
        ),
        "shared_inner_data_reconstruct_rho": (
            frac(shared["inner_data"]["a0"]) == 1
            and frac(shared["inner_data"]["a1"]) == 4
            and frac(shared["inner_data"]["tau1"]) == 10
            and frac(shared["rho"]) == rho
        ),
        "unique_endpoint_law_reconstruction": (
            c1 == Fraction(14819, 8000)
            == frac(shared["endpoint_c1"])
            == frac(endpoint_row["coefficients"][1])
        ),
        "forced_gram_reconstruction": imported_gram == G,
        "forced_gram_rank_and_determinant": (
            G.rank() == shared["forced_missing_gram_rank"] == 2
            and Fraction(G.det()) == frac(shared["forced_missing_gram_determinant"])
            == -rho**2
        ),
        "individual_inner_coefficients_replay": coefficients
        == [Fraction(-6699, 128), Fraction(-7149, 128)]
        == [frac(row) for row in shared["inner_coefficients"]],
        "inner_difference_replay": difference
        == coefficients[0] - coefficients[1]
        == frac(shared["inner_coefficient_difference"])
        == Fraction(225, 64),
        "equal_rho_unequal_response_witness": (
            rho == frac(endpoint_row["rho"]) and coefficients[0] != coefficients[1]
        ),
        "rho_only_conclusion_recorded": certificate["separation_theorem"][
            "conclusion"
        ]
        == "THE_ALL_THRESHOLD_HARD_PROFILE_IS_NOT_RHO_ONLY",
        "combined_architecture_remains_preflight": certificate[
            "separation_theorem"
        ]["smallest_justified_architecture"]["status"]
        == "ALGEBRAIC_PREFLIGHT_NOT_DERIVED_FROM_BT_DYNAMICS",
        "Eq19_probability_gravity_and_Lorentzian_claims_stay_open": (
            certificate["disposition"]["Eq19_all_orders"] == "NOT_PROVED"
            and certificate["disposition"]["physical_fourth_probability"]
            == "NOT_NORMALIZED"
            and any("gravitational" in row for row in certificate["does_not_establish"])
            and any("LORENTZIAN-CAUSAL" in row for row in certificate["does_not_establish"])
        ),
    }
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    checks = verify(load(args.verify))
    for name, ok in checks.items():
        print(("PASS" if ok else "FAIL") + ": " + name)
    print("RESULT:", "PASS" if all(checks.values()) else "FAIL")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
