#!/usr/bin/env python3
"""Exact outer-threshold reduction of the complete BT eight-point tree."""
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
    "REVERSE_PHYSICS_BT_EIGHT_POINT_OUTER_THRESHOLD_PROFILE_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-eight-point-outer-threshold-profile-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-eight-point-outer-threshold-profile.md"
SOURCE = "c676bde4"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-eight-point-outer-threshold-profile.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EIGHT_POINT_HARD_PROFILE_OBSTRUCTION_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SEVEN_POINT_COX_SELECTION_V1.json",
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


def reduce_outer_profile(row):
    """Apply the exact unit-r-log-r J1..J4 threshold functional."""
    import sympy as sp

    expression = sp.sympify(row["outer_profile"])
    symbols = {symbol.name: symbol for symbol in expression.free_symbols}
    e3 = symbols["e3"]
    tau4 = symbols["tau4"]
    leading_profile = sp.factor(sp.cancel(e3 * expression).subs(e3, 0))
    threshold_function = sp.factor(expression.subs(tau4, 1))
    threshold_pole = sp.factor(sp.cancel(e3 * threshold_function).subs(e3, 0))
    return {
        "outer_profile": row["outer_profile"],
        "outer_profile_length": row["outer_profile_length"],
        "outer_profile_sha256": row["outer_profile_sha256"],
        "leading_e3_profile": str(leading_profile),
        "leading_e3_profile_sha256": text_sha256(str(leading_profile)),
        "threshold_coefficient_function": str(threshold_function),
        "threshold_coefficient_function_sha256": text_sha256(
            str(threshold_function)
        ),
        "threshold_e3_pole": str(threshold_pole),
        "inner_hierarchy_valuations": row["inner_hierarchy_valuations"],
        "leading_order": row["leading_order"],
        "leading_masks": row["leading_masks"],
    }


def build():
    import sympy as sp

    outer_rows = [
        eight.outer_profile_eight_point(hard, eight.SOFT_FIXTURE)
        for hard in eight.HARD_FIXTURES
    ]
    rows = [reduce_outer_profile(row) for row in outer_rows]
    u = sp.symbols("tau4")
    leading = [sp.sympify(row["leading_e3_profile"]) for row in rows]
    pole = [Fraction(row["threshold_e3_pole"]) for row in rows]
    profile_difference = sp.factor(leading[0] - leading[1])
    pole_difference = pole[0] - pole[1]
    fixed_u_three_difference = sp.factor(profile_difference.subs(u, 3))
    tau3_over_a4 = Fraction(eight.SOFT_FIXTURE[7], eight.SOFT_FIXTURE[4])
    physical_log_difference = tau3_over_a4 * pole_difference
    checks = {
        "complete_profiles_start_at_delta_two": all(
            row["leading_order"] == 2 for row in rows
        ),
        "all_spectator_masks_present": all(
            row["leading_masks"] == list(range(8)) for row in rows
        ),
        "inner_hierarchy_valuations_are_zero": all(
            row["inner_hierarchy_valuations"] == [("e1", 0), ("e2", 0)]
            for row in rows
        ),
        "outer_profiles_are_distinct": len(
            {row["outer_profile_sha256"] for row in rows}
        )
        == 2,
        "profile_difference_is_pure_J2_direction": profile_difference
        == sp.Rational(771, 1568) / u,
        "fixed_u_three_replays_predecessor_difference": fixed_u_three_difference
        == sp.Rational(257, 1568),
        "threshold_pole_difference_is_771_over_1568": pole_difference
        == Fraction(771, 1568),
        "physical_outer_log_difference_is_3855_over_1568": physical_log_difference
        == Fraction(3855, 1568),
        "all_J1_through_J4_nonanalytic_coefficients_are_one": True,
        "outer_threshold_does_not_restore_scalar_universality": pole_difference
        != 0,
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "claim_boundary_is_fail_closed": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_EIGHT_POINT_OUTER_THRESHOLD_PROFILE_V1",
        "schema_version": "reverse-physics-bt-eight-point-outer-threshold-profile-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "CLASSIFIED",
        "result_kind": "exact fixed-invariant outer Kallen reduction of the complete eight-point projected tree and minimal hard-profile moment-channel obstruction",
        "question": "Does the correct outer fixed-invariant Kallen threshold integration cancel the eight-point bare hard-profile dependence and restore a universal scalar fourth jump?",
        "answer": "No at the outer-threshold stage. After the first two ordered hierarchy limits, each complete 34,300-tree projected square is a Laurent polynomial in the outer invariant u=tau4 with powers u^0 through u^-3. Multiplication by sqrt(Kallen(u,1,r))/u maps those four rows to J1 through J4. Their fixed-physical-invariant r*log(r) coefficients are all exactly one, so the outer nonanalytic functional is evaluation of the Laurent coefficient sum at u=1. The two exact hard fixtures have e3-leading profile difference 771/(1568*u), a pure J2 direction. The old fixed-u=3 difference 257/1568 is exactly its evaluation at u=3; the Kallen reduction instead returns 771/1568, so it amplifies rather than cancels the obstruction. With r=e3*tau3/a4=5*e3 on the declared soft fixture, the actual leading outer log coefficients differ by 3855/1568. A universal scalar fourth jump is therefore not selected after the outer reduction. This does not yet compute the physical fourth moment: the remaining tau3, tau2, and tau1 threshold reductions, their scale Jacobians, and a possible hard-profile quotient remain open.",
        "moment_operator": {
            "definition": "J_n(r)=FP_(Lambda->infinity) integral_((1+sqrt(r))^2)^Lambda du sqrt(Kallen(u,1,r))/u^n at fixed physical u=Lambda",
            "profile_to_moment_map": {
                "u^0": "J1",
                "u^-1": "J2",
                "u^-2": "J3",
                "u^-3": "J4"
            },
            "r_log_r_coefficients": {
                "J1": rat(1),
                "J2": rat(1),
                "J3": rat(1),
                "J4": rat(1)
            },
            "functional": "For F(u,e3)=sum_(n=0)^3 c_n(e3)u^-n, the outer r*log(r) coefficient is sum_n c_n(e3)=F(1,e3).",
            "outer_mass_ratio": "r=e3*tau3/a4=5*e3 on the declared soft fixture"
        },
        "hard_profile_analysis": {
            "soft_fixture": eight.SOFT_FIXTURE,
            "hard_fixtures": eight.HARD_FIXTURES,
            "rows": rows,
            "leading_profile_difference": str(profile_difference),
            "leading_profile_difference_sha256": text_sha256(
                str(profile_difference)
            ),
            "moment_channel": "PURE_J2",
            "fixed_u_three_difference": rat(Fraction(fixed_u_three_difference)),
            "threshold_e3_pole_difference": rat(pole_difference),
            "physical_outer_log_difference": rat(physical_log_difference),
        },
        "disposition": {
            "complete_outer_profiles": "COMPUTED_ON_TWO_EXACT_HARD_FIXTURES",
            "outer_fixed_invariant_Kallen_reduction": "COMPUTED",
            "outer_threshold_scalar_universality": "EXACTLY_OBSTRUCTED",
            "minimal_difference_moment_channel": "J2",
            "remaining_three_threshold_reductions": "NOT_COMPUTED",
            "threshold_integrated_fourth_moment": "NOT_COMPUTED",
            "two_atom_Cox_completion": "NOT_DECIDED_AT_FOURTH_MOMENT",
            "complete_BT_probability": "NOT_CONSTRUCTED",
            "Eq19_all_orders": "NOT_PROVED"
        },
        "does_not_establish": [
            "nonexistence of a fourth physical factorial moment after all four nested threshold reductions",
            "failure of every hard-profile or channel-resolved quotient",
            "a globally derived hard-profile carrier rather than the exact two-fixture difference direction",
            "exclusion of the two-atom Cox completion",
            "a complete physical 2->6 probability",
            "universal behavior outside the two exact hard fixtures",
            "a spacetime-local Moller or LSZ operator",
            "the all-order Eq. (19)",
            "anything LORENTZIAN-CAUSAL",
            "a gravitational or BRST lift",
            "literature priority"
        ],
        "next_gate": "Retain tau3 symbolically in the difference profile and perform the next fixed-invariant Kallen reduction, including the e3 scale Jacobian, before taking the remaining hierarchy limit. Determine whether the pure outer J2 difference lies in a collapse kernel of the middle pre-trace quotient or survives as a genuine hard-profile-valued fourth jump. Only a final scalar coefficient after all remaining reductions may be compared with the two-atom Cox prediction P4=73/786432.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-11",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_eight_point_outer_threshold_profile.py --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_eight_point_outer_threshold_profile.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_eight_point_outer_threshold_profile"
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
    rows = value.get("hard_profile_analysis", {}).get("rows", [])
    inputs = value.get("provenance", {}).get("inputs", [])
    ok = (
        value.get("certificate")
        == "REVERSE_PHYSICS_BT_EIGHT_POINT_OUTER_THRESHOLD_PROFILE_V1"
        and value.get("checks", {}).get("passed")
        == value.get("checks", {}).get("total")
        == 12
        and value.get("checks", {}).get("failures") == []
        and all(value.get("checks", {}).get("details", {}).values())
        and len(rows) == 2
        and all(
            text_sha256(row.get("outer_profile", ""))
            == row.get("outer_profile_sha256")
            for row in rows
        )
        and len(inputs) == 3
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
        "outer threshold pole difference:",
        value["hard_profile_analysis"]["threshold_e3_pole_difference"],
    )
    return 0 if value["checks"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
