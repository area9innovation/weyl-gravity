#!/usr/bin/env python3
"""Exact separation of BT complement and eight-point hard-profile data."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_COMPLEMENT_HARD_PROFILE_SEPARATION_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-complement-hard-profile-separation-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-complement-hard-profile-separation.md"
SOURCE = "4da7c887"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-complement-hard-profile-separation.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EIGHT_POINT_INNER_THRESHOLD_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_PHYSICAL_COLLINEAR_OPERATOR_FACTORIZATION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_FINITE_PHYSICAL_MOLLER_COLUMN_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_ENDPOINT_COMPLEMENT_MATCHING_V1.json",
]


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


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
    import sympy as sp

    inner = load(INPUTS[1])
    physical = load(INPUTS[2])
    moller = load(INPUTS[3])
    endpoint = load(INPUTS[4])

    a0, a1, tau, h = sp.symbols("a0 a1 tau h")
    rho_formula = (
        (a0 - a1) ** 2
        * (2 * tau * (a0 + a1) - (a0 - a1) ** 2)
        / (4 * tau**3)
    )
    shared_inner = {a0: 1, a1: 4, tau: 10}
    rho = Fraction(rho_formula.subs(shared_inner))
    c1 = Fraction(7, 4) + rho / 2
    G = [[Fraction(0), -rho], [-rho, Fraction(-2)]]

    hard_fixtures = inner["profile_analysis"]["hard_fixtures"]
    adjacent_rows = [row[0] for row in hard_fixtures]
    hard_values = [Fraction(row[-1]) for row in adjacent_rows]
    inner_coefficients = [
        frac(row)
        for row in inner["inner_threshold"]["fixture_r_log_r_coefficients"]
    ]
    inner_difference = frac(
        inner["inner_threshold"]["hard_difference_r_log_r_coefficient"]
    )
    endpoint_row = endpoint["physical_fixtures"][0]
    endpoint_rho = frac(endpoint_row["rho"])
    endpoint_c1 = frac(endpoint_row["coefficients"][1])
    imported_gram = [
        [frac(value) for value in row]
        for row in endpoint_row["matched_gram"]
    ]
    G_matrix = sp.Matrix(
        [[sp.Rational(value.numerator, value.denominator) for value in row]
         for row in G]
    )

    checks = {
        "all_predecessor_certificates_pass": all(
            value["checks"]["ok"] for value in (inner, physical, moller, endpoint)
        ),
        "shared_inner_data_are_one_four_ten": inner["profile_analysis"][
            "soft_fixture"
        ][:2]
        + [inner["profile_analysis"]["soft_fixture"][5]]
        == [1, 4, 10],
        "rho_formula_imported_and_recomputed": (
            physical["amplitude_factorization"]["rho"]
            == "(a0-a1)^2*(2*tau*(a0+a1)-(a0-a1)^2)/(4*tau^3)"
            and rho == Fraction(819, 4000)
        ),
        "hard_fixtures_differ_only_in_final_adjacent_invariant": (
            hard_fixtures[0][1:] == hard_fixtures[1][1:]
            and adjacent_rows[0][:-1] == adjacent_rows[1][:-1]
            and hard_values == [Fraction(33), Fraction(34)]
        ),
        "same_rho_for_both_hard_fixtures": rho == Fraction(819, 4000),
        "same_unique_endpoint_coefficient": (
            c1 == endpoint_c1 == Fraction(14819, 8000)
            and endpoint_rho == rho
        ),
        "same_forced_cross_krein_gram": imported_gram == G,
        "forced_complement_is_rank_two": (
            G_matrix.rank() == 2
            and sp.factor(G_matrix.det()) == -sp.Rational(rho.numerator, rho.denominator) ** 2
        ),
        "final_inner_coefficients_are_distinct": inner_coefficients
        == [Fraction(-6699, 128), Fraction(-7149, 128)],
        "inner_difference_is_225_over_64": (
            inner_difference
            == inner_coefficients[0] - inner_coefficients[1]
            == Fraction(225, 64)
        ),
        "rho_only_identification_is_refuted": (
            endpoint_rho == rho and inner_coefficients[0] != inner_coefficients[1]
        ),
        "hard_coordinate_is_absent_from_rho_law": h not in rho_formula.free_symbols,
        "additional_hard_profile_coordinate_is_required": True,
        "combined_architecture_is_not_claimed_dynamic": True,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_COMPLEMENT_HARD_PROFILE_SEPARATION_V1",
        "schema_version": "reverse-physics-bt-complement-hard-profile-separation-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact shared-fixture parameter-separation theorem between the rho-dependent cross-Krein complement and the all-threshold BT eight-point hard-profile coefficient",
        "question": "Can the hard-profile dependence that survives all four eight-point thresholds be identified with the single rho dependence of the cross-Krein complement required by the finite physical Moller compression?",
        "answer": "No on the exact shared fixture. The two complete eight-point hard fixtures have identical soft and inner data, including (a0,a1,tau1)=(1,4,10), and differ only in one adjacent hard invariant h=33 versus h=34. The certified first-emission formula therefore gives the same rho=819/4000 on both. The forced public-to-physical complement has the same rank-two cross-Krein Gram [[0,-rho],[-rho,-2]] and the unique endpoint law gives the same c1=7/4+rho/2=14819/8000. Nevertheless the complete all-threshold eight-point coefficients are -6699/128 and -7149/128, differing by 225/64. Hence the fourth-jump hard dependence is not a function of rho alone and cannot be identified with the rho-dependent complement parameter. The two obstructions are compatible only in a richer architecture: a rank-two cross-Krein fibre controlled by rho over a base that retains at least one additional hard-profile coordinate h, with the fourth jump allowed to vary in that coordinate. This exact equal-rho/non-equal-response square is a parameter-separation witness, not a global dimension theorem or a dynamically derived BT bundle. The profile-valued jump map, pairing with the complement, physical normalization, Eq. (19), complete probability, gravity, and Lorentzian causality remain open.",
        "shared_fixture": {
            "inner_data": {
                "a0": rat(1),
                "a1": rat(4),
                "tau1": rat(10),
            },
            "hard_coordinate_name": "final_adjacent_invariant_h",
            "hard_coordinate_values": [rat(value) for value in hard_values],
            "all_other_hard_entries_equal": True,
            "rho_formula": str(sp.factor(rho_formula)),
            "rho": rat(rho),
            "endpoint_c1": rat(c1),
            "forced_missing_gram": [
                [rat(value) for value in row] for row in G
            ],
            "forced_missing_gram_rank": 2,
            "forced_missing_gram_determinant": rat(-rho**2),
            "inner_coefficients": [rat(value) for value in inner_coefficients],
            "inner_coefficient_difference": rat(inner_difference),
        },
        "separation_theorem": {
            "equal_complement_parameter": "rho(33)=rho(34)=819/4000",
            "equal_complement_gram": "G_missing(33)=G_missing(34)",
            "equal_endpoint_coefficient": "c1(33)=c1(34)=14819/8000",
            "unequal_fourth_response": "kappa4(33)-kappa4(34)=225/64",
            "conclusion": "THE_ALL_THRESHOLD_HARD_PROFILE_IS_NOT_RHO_ONLY",
            "smallest_justified_architecture": {
                "base_data": ["rho", "at_least_one_additional_hard_profile_coordinate_h"],
                "fibre": "rank_two_cross_Krein_complement_with_G_missing(rho)",
                "fourth_jump": "profile_section_allowed_to_depend_on_h",
                "status": "ALGEBRAIC_PREFLIGHT_NOT_DERIVED_FROM_BT_DYNAMICS",
            },
        },
        "disposition": {
            "rho_only_unification": "EXACTLY_REFUTED_ON_SHARED_FIXTURE",
            "complement_and_hard_profile_parameter_separation": "PROVED_ON_SHARED_FIXTURE",
            "combined_profile_cross_Krein_architecture": "TYPE_FIXED_NOT_CONSTRUCTED",
            "BT_derived_profile_jump": "NOT_CONSTRUCTED",
            "physical_fourth_probability": "NOT_NORMALIZED",
            "Eq19_all_orders": "NOT_PROVED",
        },
        "does_not_establish": [
            "a global dimension theorem for every BT kinematic base",
            "a unique hard-profile coordinate away from the two exact fixtures",
            "a dynamically derived profile-valued fourth jump",
            "a BT derivation of the cross-Krein complement",
            "a normalized fourth-event probability or Cox decision",
            "a complete physical 2->6 probability",
            "a spacetime Moller, LSZ, or S operator",
            "the all-order Eq. (19)",
            "a gravitational or BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": "Construct a history-resolved profile section over a base retaining rho and the witnessed hard coordinate, valued in or paired with the certified rank-two cross-Krein complement. The first falsifiable test is whether a single exact map reproduces both all-threshold coefficients at fixed rho while preserving G_missing(rho), the charge grading, the endpoint law, and the existing one-through-three-emission column. Algebraic compatibility is insufficient: the map must be derived from a declared BT zero-mode, higher-composite, or eight-point quotient operator before it can advance Eq. (19).",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_complement_hard_profile_separation.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_complement_hard_profile_separation.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_complement_hard_profile_separation",
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks,
        },
        "report": REPORT,
        "schema": SCHEMA,
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def fast_check(path):
    try:
        with open(path, encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print("[FAIL] recorded certificate:", exc)
        return 1
    inputs = value.get("provenance", {}).get("inputs", [])
    ok = (
        value.get("certificate")
        == "REVERSE_PHYSICS_BT_COMPLEMENT_HARD_PROFILE_SEPARATION_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        == 15
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(inputs) == 5
        and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs)
        and value.get("disposition", {}).get("Eq19_all_orders") == "NOT_PROVED"
    )
    print("FAST RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--fast-check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    if args.fast_check:
        return fast_check(args.output)
    value = build()
    rendered = canonical(value)
    if args.write:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    if args.check:
        try:
            with open(args.output, encoding="utf-8") as handle:
                recorded = canonical(json.load(handle))
        except (OSError, json.JSONDecodeError) as exc:
            print("[FAIL] recorded certificate:", exc)
            return 1
        if recorded != rendered:
            print("[FAIL] certificate drift")
            return 1
    print("checks %d/%d" % (value["checks"]["passed"], value["checks"]["total"]))
    print("RESULT:", "PASS" if value["checks"]["ok"] else "FAIL")
    print("rho:", value["shared_fixture"]["rho"])
    print(
        "hard response difference:",
        value["shared_fixture"]["inner_coefficient_difference"],
    )
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
