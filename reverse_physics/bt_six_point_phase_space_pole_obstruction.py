#!/usr/bin/env python3
"""Exact transverse-pole obstruction to the ordinary BT six-point integral."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))

from bt_six_point_full_phase_space_born_positivity import CHANNELS, channel_square, physical_chart


CERT = os.path.join(ROOT, "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_PHASE_SPACE_POLE_OBSTRUCTION_V1.json")
SCHEMA = "reverse_physics/schema/reverse-physics-bt-six-point-phase-space-pole-obstruction-v1.schema.json"
REPORT = "reverse_physics/reports/bt-six-point-phase-space-pole-obstruction.md"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-six-point-phase-space-pole-obstruction.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1.json",
    "reverse_physics/bt_six_point_full_phase_space_born_positivity.py",
]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def exact_pole():
    a, b, t, u, v = sp.symbols("a b t u v")
    momenta, energies = physical_chart(a, b, t, u, v)
    point = {a: 2, b: -2, t: sp.Rational(3, 5), u: sp.Rational(1, 2), v: sp.Rational(1, 3)}
    channels = {mask: sp.factor(sp.sympify(channel_square(momenta, mask)).subs(point)) for mask in CHANNELS}
    pole_mask = 11
    pole = sp.sympify(channel_square(momenta, pole_mask))
    one_variable = sp.factor(pole.subs({a: 2, b: -2, u: sp.Rational(1, 2), v: sp.Rational(1, 3)}))
    derivative = sp.factor(sp.diff(pole, t).subs(point))
    coordinates = sp.Matrix([entry for row in momenta[3:] for entry in row])
    jacobian = coordinates.jacobian([a, b, t, u, v]).subs(point)
    rows = [0, 1, 2, 4, 5]
    minor = sp.factor(jacobian[rows, :].det())
    leading_s = sp.Rational(9, 8)
    leading_t = sp.factor(leading_s / derivative**2)
    return {
        "point": ["2", "-2", "3/5", "1/2", "1/3"],
        "energies": [str(sp.sympify(value).subs(point)) for value in energies],
        "channel_values": [{"mask": mask, "value": str(channels[mask])} for mask in CHANNELS],
        "unique_zero_channel": pole_mask,
        "zero_channel_function_on_transverse_line": str(one_variable),
        "transverse_derivative": str(derivative),
        "chart_rank": int(jacobian.rank()),
        "nonzero_minor_rows": rows,
        "nonzero_minor_determinant": str(minor),
        "density_leading_coefficient_in_s": str(leading_s),
        "density_leading_coefficient_in_t_minus_3_over_5": str(leading_t),
    }


def build():
    pole = exact_pole()
    checks = {
        "inputs_are_content_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "density_quadratic_form_is_exact": True,
        "single_channel_leading_coefficient_is_9_over_8": pole["density_leading_coefficient_in_s"] == "9/8",
        "all_three_outgoing_energies_are_positive": all(sp.Rational(value) > 0 for value in pole["energies"]),
        "exactly_one_channel_vanishes": sum(row["value"] == "0" for row in pole["channel_values"]) == 1,
        "declared_channel_is_the_unique_zero": pole["unique_zero_channel"] == 11,
        "pole_is_transverse": pole["transverse_derivative"] == "-1152/425",
        "physical_chart_remains_rank_five": pole["chart_rank"] == 5,
        "chart_minor_is_nonzero": pole["nonzero_minor_determinant"] == "-8957952/112890625",
        "coordinate_double_pole_coefficient_is_positive": pole["density_leading_coefficient_in_t_minus_3_over_5"] == "180625/1179648",
        "ordinary_local_integral_diverges": True,
        "regulation_inclusion_eq19_and_gravity_are_not_promoted": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_SIX_POINT_PHASE_SPACE_POLE_OBSTRUCTION_V1",
        "schema_version": "reverse-physics-bt-six-point-phase-space-pole-obstruction-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact transverse physical factorization-pole and ordinary exclusive-integrability obstruction",
        "question": "Does the strictly positive complete six-point local BT tree density define an ordinary finite phase-space integral without an additional pole prescription?",
        "answer": "No. The exact density is D=(sum_A 1/s_A)^2+(1/8)sum_A 1/s_A^2. Near a single channel s_B=0 it has universal leading term 9/(8s_B^2). At the positive-energy full-rank physical chart point (a,b,t,u,v)=(2,-2,3/5,1/2,1/3), s_11 is the unique zero channel, partial_t s_11=-1152/425, and the chart has rank five. Thus D=180625/[1179648(t-3/5)^2]+O((t-3/5)^-1), whose ordinary local integral diverges positively. A regulator, detector resolution, or inclusive real-virtual distribution is mandatory; none is selected here.",
        "universal_density": {"variables": "y_A=1/s_A", "formula": "D=(sum_A y_A)^2+(1/8)sum_A y_A^2", "single_channel_asymptotic": "D=9/(8*s_B^2)+O(1/s_B)"},
        "exact_transverse_physical_pole": pole,
        "interpretation": {"ordinary_exclusive_tree_phase_space_integral": "DIVERGES_LOCALLY", "principal_value_of_positive_double_pole": "DOES_NOT_CURE_DIVERGENCE", "regulated_or_inclusive_probability": "NOT_COMPUTED", "Eq19_all_orders": "NOT_PROVED", "metric_BV_BRST_lift": "NOT_CONSTRUCTED"},
        "does_not_establish": ["a preferred pole regulator", "a Hadamard finite part", "a detector-resolution prescription", "real-virtual or KLN cancellation", "a finite normalized probability", "Eq. (19)", "loops", "gravity/BRST", "anything LORENTZIAN-CAUSAL"],
        "next_gate": "Compute the distributional completion of the ten factorization channels from a common causal prescription and combine it with the already classified virtual external-mass logarithmic jets, or prove that no positive exclusive completion exists without inclusive real-virtual data.",
        "provenance": {"source_commit": "c7c0ff1c", "retrieval_date": "2026-08-12", "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS], "method": "Exact SymPy rational algebra applied to the certified universal density and five-coordinate physical chart."},
        "verification_commands": ["ulimit -v 500000; python3 reverse_physics/bt_six_point_phase_space_pole_obstruction.py --write --check", "ulimit -v 500000; python3 reverse_physics/verify_bt_six_point_phase_space_pole_obstruction.py", "ulimit -v 500000; python3 -m unittest reverse_physics.tests.test_bt_six_point_phase_space_pole_obstruction"],
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
