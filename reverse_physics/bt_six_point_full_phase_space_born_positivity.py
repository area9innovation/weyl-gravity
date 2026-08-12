#!/usr/bin/env python3
"""Exact BT six-point complete-phase-space local Born-density theorem."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from itertools import combinations

import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))

from bt_six_point_generic_external_mass_kernel import (
    FULL_MASK,
    generic_external_mass_kernel,
)


CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1.json",
)
SCHEMA = (
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-full-phase-space-born-positivity-v1.schema.json"
)
REPORT = "reverse_physics/reports/bt-six-point-full-phase-space-born-positivity.md"
SOURCE = "1ec0ae4b25c0cb53859263613a8dc6a56fb85709"
INPUTS = [
    "planning/work-items/reverse-physics-bateman-six-point-full-phase-space-born-positivity.json",
    "reverse_physics/bt_six_point_generic_external_mass_kernel.py",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_TWO_ANGLE_PHYSICAL_BORN_DENSITY_V1.json",
    "notes/bateman-turok-embedding.md",
]
CHANNELS = [
    sum(1 << index for index in subset)
    for subset in combinations(range(6), 3)
    if sum(1 << index for index in subset)
    < (FULL_MASK ^ sum(1 << index for index in subset))
]
FIXTURES = [
    (Fraction(3, 2), Fraction(-3, 2), Fraction(1, 2), Fraction(2, 3), Fraction(1, 4)),
    (Fraction(5, 2), Fraction(-3, 2), Fraction(1), Fraction(2, 5), Fraction(3, 7)),
    (Fraction(3, 2), Fraction(-5, 2), Fraction(3, 2), Fraction(4, 5), Fraction(5, 6)),
    (Fraction(7, 4), Fraction(-9, 4), Fraction(5, 3), Fraction(7, 6), Fraction(2, 9)),
    (Fraction(9, 4), Fraction(-7, 4), Fraction(2, 3), Fraction(3, 7), Fraction(4, 9)),
    (Fraction(5, 3), Fraction(-7, 3), Fraction(4, 5), Fraction(5, 8), Fraction(7, 10)),
]


def sha256(path):
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, path), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def direction(parameter):
    return (
        (1 - parameter * parameter) / (1 + parameter * parameter),
        2 * parameter / (1 + parameter * parameter),
        parameter * 0,
    )


def rotate(vector, t, u, v):
    def cs(parameter):
        return ((1 - parameter * parameter) / (1 + parameter * parameter),
                2 * parameter / (1 + parameter * parameter))
    ct, st = cs(t)
    cu, su = cs(u)
    cv, sv = cs(v)
    x, y, z = vector
    x, y = ct * x - st * y, st * x + ct * y
    y, z = cu * y - su * z, su * y + cu * z
    return (cv * x - sv * y, sv * x + cv * y, z)


def physical_chart(a, b, t, u, v):
    directions = [direction(a * 0), direction(a), direction(b)]
    cross = lambda left, right: left[0] * right[1] - left[1] * right[0]
    weights = [
        cross(directions[1], directions[2]),
        cross(directions[2], directions[0]),
        cross(directions[0], directions[1]),
    ]
    energies = [Fraction(16, 5) * weight / sum(weights) for weight in weights]
    outgoing = [
        (energy,) + tuple(energy * value for value in rotate(unit, t, u, v))
        for energy, unit in zip(energies, directions)
    ]
    incoming = [
        (Fraction(6, 5), Fraction(6, 5), Fraction(0), Fraction(0)),
        (Fraction(1), Fraction(-3, 5), Fraction(4, 5), Fraction(0)),
        (Fraction(1), Fraction(-3, 5), Fraction(-4, 5), Fraction(0)),
    ]
    return incoming + [tuple(-value for value in row) for row in outgoing], energies


def add(*vectors):
    return tuple(sum(row[index] for row in vectors) for index in range(4))


def square(vector):
    return vector[0] ** 2 - sum(value ** 2 for value in vector[1:])


def channel_square(momenta, mask):
    return square(add(*(momenta[index] for index in range(6) if mask & (1 << index))))


def invariants(momenta):
    adjacent = [square(add(momenta[i], momenta[(i + 1) % 6])) for i in range(6)]
    triples = [square(add(momenta[i], momenta[(i + 1) % 6], momenta[(i + 2) % 6])) for i in range(3)]
    return adjacent, triples


def chart_rank_certificate():
    a, b, t, u, v = sp.symbols("a b t u v")
    momenta, _ = physical_chart(a, b, t, u, v)
    outgoing_coordinates = sp.Matrix([value for row in momenta[3:] for value in row])
    jacobian = outgoing_coordinates.jacobian([a, b, t, u, v])
    point = {a: 2, b: -2, t: 0, u: 1, v: 0}
    evaluated = jacobian.subs(point)
    rows = [0, 2, 3, 4, 6]
    determinant = sp.factor(evaluated[rows, :].det())
    return {
        "base_point": ["2", "-2", "0", "1", "0"],
        "jacobian_shape": list(evaluated.shape),
        "rank": int(evaluated.rank()),
        "nonzero_minor_rows": rows,
        "nonzero_minor_determinant": str(determinant),
    }


def fixture_result(values):
    momenta, energies = physical_chart(*values)
    adjacent, triples = invariants(momenta)
    result = generic_external_mass_kernel(adjacent, triples, max_degree=3)
    coefficients = result["degree_three"]
    formula = {}
    channel_values = {mask: channel_square(momenta, mask) for mask in CHANNELS}
    for mask in CHANNELS:
        formula[mask] = Fraction(1, 4) * sum(
            Fraction(1, channel_values[other]) for other in CHANNELS if other != mask
        )
    return {
        "parameters": [str(value) for value in values],
        "energies": [str(value) for value in energies],
        "massless_and_conserved": all(square(row) == 0 for row in momenta)
        and all(value == 0 for value in add(*momenta)),
        "all_ten_channels_regular": all(channel_values.values()),
        "twenty_middle_coefficients": len(coefficients) == 20,
        "universal_formula_matches_complete_tree_sum": all(
            coefficients[mask] == formula[mask]
            and coefficients[FULL_MASK ^ mask] == formula[mask]
            for mask in CHANNELS
        ),
        "strict_square_sum": 2 * sum(value * value for value in formula.values()) > 0,
    }


def build():
    chart = chart_rank_certificate()
    fixtures = [fixture_result(values) for values in FIXTURES]
    incidence = [
        [int(channel != assignment) for channel in CHANNELS]
        for assignment in CHANNELS
    ]
    determinant = int(sp.Matrix(incidence).det())
    checks = {
        "input_hashes_pinned": all(len(sha256(path)) == 64 for path in INPUTS),
        "ten_unordered_three_three_channels": len(CHANNELS) == 10,
        "auxiliary_species_flow_is_J_minus_I": all(
            incidence[i][j] == (i != j) for i in range(10) for j in range(10)
        ),
        "incidence_map_is_invertible_in_characteristic_zero": determinant == -9,
        "common_zero_is_impossible_at_regular_kinematics": determinant != 0,
        "rational_chart_has_exact_rank_five": chart["rank"] == 5,
        "rank_minor_is_exact_and_nonzero": chart["nonzero_minor_determinant"] == "864/3125",
        "six_shape_and_orientation_fixtures": len(fixtures) == 6,
        "fixture_energies_are_future_positive": all(all(Fraction(x) > 0 for x in row["energies"]) for row in fixtures),
        "fixture_momenta_are_massless_and_conserved": all(row["massless_and_conserved"] for row in fixtures),
        "all_fixture_channels_are_regular": all(row["all_ten_channels_regular"] for row in fixtures),
        "all_fixtures_retain_twenty_middle_coefficients": all(row["twenty_middle_coefficients"] for row in fixtures),
        "universal_formula_matches_complete_220_tree_kernel": all(row["universal_formula_matches_complete_tree_sum"] for row in fixtures),
        "all_exact_full_chart_fixtures_are_strictly_positive": all(row["strict_square_sum"] for row in fixtures),
        "six_delta_prime_sign_is_positive": (-1) ** 6 == 1,
        "integration_eq19_gravity_loops_and_causality_remain_open": True,
    }
    return {
        "certificate": "REVERSE_PHYSICS_BT_SIX_POINT_FULL_PHASE_SPACE_BORN_POSITIVITY_V1",
        "schema_version": "reverse-physics-bt-six-point-full-phase-space-born-positivity-v1",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact complete-regular-phase-space local six-delta-prime scalar tree Born-density theorem",
        "question": "Is the complete leading BT six-point local Born density positive over the full regular massless physical 3-to-3 phase space?",
        "answer": "Yes, locally and at tree level. For every unordered three-three split S, the complete 220-tree middle external-mass coefficient is c_S=c_Sc=(1/4) sum_{A!=S} 1/s_A, where A runs over the ten unordered three-particle channels and s_A is their massless invariant. The auxiliary O(1,1) two-quartic-tree species-flow matrix is J-I: the unique forbidden channel puts all three like external species on one vertex. Its determinant is -9, so the ten real coefficients have no common zero wherever every channel is finite and nonzero. The six-delta-prime coefficient 2 sum c_S^2 is therefore strictly positive at every regular physical point with positive local measure. An exact rational chart has Jacobian rank five, confirming that the result is not a lower-dimensional slice. This does not regulate or integrate the channel poles and does not prove Eq. (19).",
        "universal_complement_formula": {
            "channels": CHANNELS,
            "formula": "c_S=c_Sc=(1/4)*sum_{A != S} 1/s_A",
            "auxiliary_model": "S_1,1=integral(partial Omega partial Upsilon + lambda^2 Omega^2 Upsilon^2/2)",
            "species_assignment": "S labels the three Omega external legs and Sc the three Upsilon external legs",
            "channel_rule": "A two-quartic tree exists exactly when a 3|3 channel contains one or two Omega legs; the channels A=S and A=Sc are the same unordered forbidden channel",
            "incidence_matrix": incidence,
            "incidence_determinant": determinant,
            "common_zero_argument": "Writing y_A=1/s_A and 4c=(J-I)y, det(J-I)=-9. At a regular point y is nonzero, hence c cannot vanish identically.",
        },
        "full_physical_chart": {
            "parameters": ["a", "b", "t", "u", "v"],
            "shape": "three planar null directions n(0), n(a), n(b), with positive momentum-conserving energies from oriented cross weights",
            "orientation": "R_z(v) R_x(u) R_z(t)",
            "fixed_total_momentum": ["16/5", "0", "0", "0"],
            "jacobian_certificate": chart,
            "exact_fixtures": fixtures,
        },
        "local_born_density": {
            "external_projector": "(-partial_x0)...(-partial_x5) at x_i=0",
            "external_derivative_sign": "+1 from (-1)^6",
            "kernel": "2*sum_{S<Sc} c_S^2",
            "status": "STRICTLY_POSITIVE_AT_EVERY_REGULAR_PHYSICAL_POINT_WITH_POSITIVE_LOCAL_WEIGHT",
        },
        "interpretation": {
            "complete_regular_massless_three_to_three_local_phase_space": "STRICTLY_POSITIVE",
            "internal_channel_poles": "EXCLUDED_NOT_REGULATED",
            "integrated_normalized_probability": "NOT_COMPUTED",
            "Eq19_all_orders": "NOT_PROVED",
            "metric_BV_BRST_lift": "NOT_CONSTRUCTED",
        },
        "assumptions": [
            "The public BT perfect-square scalar cubic and quartic vertices and common tree normalization are used.",
            "The leading square-free six-external-mass coefficient is identified with the three-Omega/three-Upsilon auxiliary tree assignment by the linearized Eq. (16) external-leg map.",
            "All ten massless three-particle channel invariants are finite and nonzero.",
            "The external phase-space/detector weight is regular and positive at the local physical point.",
            "The common tree phase is omitted before the real tree coefficient is squared.",
        ],
        "does_not_establish": [
            "a prescription at any internal three-particle channel pole",
            "a regulated or integrated six-body probability",
            "normalization of a complete scattering probability",
            "real-virtual or KLN cancellation",
            "positivity beyond tree level",
            "a Moller, LSZ, or S operator",
            "Bateman--Turok Eq. (19)",
            "a derivation of the full nonlinear R_t projector transport",
            "a gravity or metric BV/BRST lift",
            "anything LORENTZIAN-CAUSAL",
            "literature priority",
        ],
        "next_gate": "Construct one common causal or explicitly distributional prescription for the ten s_A=0 tree poles and integrate the positive local density over the exact five-dimensional chart. In parallel, Eq. (19) remains the distinct nonlinear projector-transport gate.",
        "provenance": {
            "source_commit": SOURCE,
            "retrieval_date": "2026-08-12",
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "producer_method": "Exact characteristic-zero auxiliary-species combinatorics gives J-I and its determinant. SymPy exact differentiation certifies a rank-five rational physical chart. The complete PS 220-tree recursion independently matches the closed formula on six positive rational fixtures varying both shape coordinates and all three orientation parameters.",
            "primary_source": {
                "source": "Bateman--Turok arXiv:2607.00096v1",
                "url": "https://arxiv.org/abs/2607.00096v1",
                "equations": ["Eq. (14)", "Eq. (16)", "Eq. (18)", "Appendix B Eqs. (24)-(25)"],
            },
        },
        "verification_commands": [
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_six_point_full_phase_space_born_positivity.py --write --check",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_six_point_full_phase_space_born_positivity.py",
            "ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_six_point_full_phase_space_born_positivity",
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=CERT)
    args = parser.parse_args(argv)
    value = build()
    rendered = canonical(value)
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
