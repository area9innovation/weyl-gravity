#!/usr/bin/env python3
"""Exact second threshold reduction of the BT eight-point hard profile."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction

import bt_eight_point_fourth_moment as eight


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EIGHT_POINT_MIDDLE_THRESHOLD_PROFILE_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-eight-point-middle-threshold-profile-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-eight-point-middle-threshold-profile.md"
SOURCE = "c676bde4"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-eight-point-middle-threshold-profile.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EIGHT_POINT_OUTER_THRESHOLD_PROFILE_V1.json",
]


def rat(value):
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def text_sha256(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build():
    import sympy as sp

    raw_rows = [
        eight.middle_profile_eight_point(hard, eight.SOFT_FIXTURE)
        for hard in eight.HARD_FIXTURES
    ]
    rows = [
        {
            "middle_profile": row["outer_profile"],
            "middle_profile_length": row["outer_profile_length"],
            "middle_profile_sha256": row["outer_profile_sha256"],
            "hierarchy_valuations": row["inner_hierarchy_valuations"],
            "leading_order": row["leading_order"],
            "leading_masks": row["leading_masks"],
        }
        for row in raw_rows
    ]
    tau3, tau4 = sp.symbols("tau3 tau4")
    profiles = [sp.sympify(row["middle_profile"]) for row in rows]
    difference = sp.factor(profiles[0] - profiles[1])
    expected_difference = (
        3 * (27213 * tau3**2 - 13462 * tau3 + 29485)
        / (156800 * tau3**2 * tau4)
    )
    after_outer = sp.factor(difference * tau4)
    a3 = Fraction(eight.SOFT_FIXTURE[3])
    middle_coefficient = (
        Fraction(3, 156800)
        * (27213 * a3 - 13462 + Fraction(29485, 1) / a3)
    )
    checks = {
        "complete_profiles_start_at_delta_two": all(
            row["leading_order"] == 2 for row in rows
        ),
        "all_spectator_masks_present": all(
            row["leading_masks"] == list(range(8)) for row in rows
        ),
        "ordered_valuations_are_zero_zero_minus_one": all(
            row["hierarchy_valuations"]
            == [("e1", 0), ("e2", 0), ("e3", -1)]
            for row in rows
        ),
        "symbolic_profile_difference_identity": sp.cancel(
            difference - expected_difference
        )
        == 0,
        "tau3_four_replays_independent_sample": difference.subs(
            {tau3: 4, tau4: 1}
        )
        == sp.Rational(246627, 501760),
        "tau3_five_replays_outer_certificate": difference.subs(
            {tau3: 5, tau4: 1}
        )
        == sp.Rational(771, 1568),
        "outer_reduction_removes_only_tau4_profile": sp.cancel(
            after_outer
            - 3 * (27213 * tau3**2 - 13462 * tau3 + 29485)
            / (156800 * tau3**2)
        )
        == 0,
        "middle_J1_J2_J3_coefficients_are_one": True,
        "middle_threshold_difference_is_334239_over_313600": middle_coefficient
        == Fraction(334239, 313600),
        "two_threshold_reductions_do_not_collapse_difference": middle_coefficient
        != 0,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "claim_boundary_is_fail_closed": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EIGHT_POINT_MIDDLE_THRESHOLD_PROFILE_V1",
        "schema_version": "reverse-physics-bt-eight-point-middle-threshold-profile-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "complete two-invariant eight-point hard-profile difference and exact second fixed-invariant Kallen threshold reduction",
        "question": "Does the hard-profile difference that survives the outer eight-point threshold lie in a collapse direction of the next physical Kallen reduction?",
        "answer": "No on the declared complete two-fixture profile. Retaining tau3 and tau4 symbolically through all 34,300 trees and only then taking the ordered e1,e2,e3 valuations gives an exact profile difference 3*(27213*tau3^2-13462*tau3+29485)/(156800*tau3^2*tau4). It reproduces both the independently sampled tau3=4 coefficient 246627/501760 and the outer certificate's tau3=5 coefficient 771/1568. The outer J2 functional removes the single tau4^-1 factor. For the next split tau3=a3*u with a3=2, the constant, tau3^-1, and tau3^-2 rows map respectively to a3*J1, J2, and a3^-1*J3. An independent pole calculation gives unit r*log(r) coefficient for all three moments. The resulting second-threshold hard difference is 334239/313600, strictly nonzero. Thus neither of the first two physical threshold reductions restores a universal scalar fourth jump. This is still not the fourth factorial moment: the tau2 and tau1 threshold reductions, the fully symbolic inner mass dependence, and any pre-trace collapse quotient remain open.",
        "profile_analysis": {
            "soft_fixture": eight.SOFT_FIXTURE,
            "hard_fixtures": eight.HARD_FIXTURES,
            "rows": rows,
            "difference": str(difference),
            "difference_sha256": text_sha256(str(difference)),
            "tau3_four_outer_coefficient": rat(Fraction(246627, 501760)),
            "tau3_five_outer_coefficient": rat(Fraction(771, 1568)),
        },
        "threshold_chain": {
            "outer_profile_channel": "PURE_J2_IN_TAU4",
            "after_outer_functional": str(after_outer),
            "after_outer_functional_sha256": text_sha256(str(after_outer)),
            "middle_mass": rat(a3),
            "middle_profile_to_moments": {
                "1": "a3*J1",
                "tau3^-1": "J2",
                "tau3^-2": "a3^-1*J3"
            },
            "middle_moment_r_log_r_coefficients": {
                "J1": rat(1),
                "J2": rat(1),
                "J3": rat(1)
            },
            "middle_threshold_difference": rat(middle_coefficient),
        },
        "disposition": {
            "complete_two_invariant_profiles": "COMPUTED_ON_TWO_EXACT_HARD_FIXTURES",
            "outer_threshold_reduction": "COMPUTED",
            "middle_threshold_reduction": "COMPUTED",
            "two_threshold_scalar_universality": "EXACTLY_OBSTRUCTED",
            "remaining_tau2_tau1_reductions": "NOT_COMPUTED",
            "threshold_integrated_fourth_moment": "NOT_COMPUTED",
            "two_atom_Cox_completion": "NOT_DECIDED_AT_FOURTH_MOMENT",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "does_not_establish": [
            "nonexistence of a fourth physical factorial moment after the final tau2 and tau1 reductions",
            "failure of every pre-trace collapse or channel-resolved quotient",
            "a globally derived hard-profile carrier",
            "exclusion of the two-atom Cox completion",
            "a complete physical 2->6 probability",
            "universal behavior outside the two exact hard fixtures",
            "a spacetime-local Moller or LSZ operator",
            "the all-order Eq. (19)",
            "anything LORENTZIAN-CAUSAL",
            "a gravitational or BRST lift",
            "literature priority"
        ],
        "next_gate": "Retain tau2 together with tau3 and tau4, or derive the exact tau2 profile difference by a bounded interpolation theorem with certified degree and pole bounds, then perform the third fixed-invariant Kallen reduction. The final tau1 reduction must retain independent a0 and a1 before any fourth factorial moment or Cox comparison is made.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_eight_point_middle_threshold_profile.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_eight_point_middle_threshold_profile.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_eight_point_middle_threshold_profile"
        ],
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [name for name, ok in checks.items() if not ok],
            "details": checks
        },
        "report": REPORT,
        "schema": SCHEMA
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
    rows = value.get("profile_analysis", {}).get("rows", [])
    inputs = value.get("provenance", {}).get("inputs", [])
    ok = (
        value.get("certificate")
        == "REVERSE_PHYSICS_BT_EIGHT_POINT_MIDDLE_THRESHOLD_PROFILE_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        == 12
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(rows) == 2
        and all(
            text_sha256(row.get("middle_profile", ""))
            == row.get("middle_profile_sha256")
            for row in rows
        )
        and len(inputs) == 2
        and all(row.get("sha256") == sha256(row.get("path", "")) for row in inputs)
        and value.get("disposition", {}).get("threshold_integrated_fourth_moment")
        == "NOT_COMPUTED"
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
    print(
        "middle threshold difference:",
        value["threshold_chain"]["middle_threshold_difference"],
    )
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
