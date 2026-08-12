#!/usr/bin/env python3
"""Independent verifier for the crossed six-point Kallen obstruction."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

from jsonschema import Draft202012Validator


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CROSSED_SIX_POINT_KALLEN_OBSTRUCTION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-crossed-six-point-kallen-obstruction-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


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
    first = load(os.path.join(ROOT, inputs[1]["path"]))
    quotient = load(os.path.join(ROOT, inputs[2]["path"]))
    nested = load(os.path.join(ROOT, inputs[3]["path"]))
    chambers = load(os.path.join(ROOT, inputs[4]["path"]))
    analytic = certificate["analytic_spacelike_crossing"]
    crossed = certificate["crossed_two_species_quotient"]
    resolution = certificate["bilateral_kallen_resolution"]
    histories = certificate["history_disposition"]
    disposition = certificate["disposition"]

    r, x, a2 = sp.symbols("r x a2", positive=True)
    m, z = sp.symbols("m z", positive=True)
    local = {"r": r, "x": x, "a2": a2, "m": m, "z": z}

    def expression(value):
        return sp.sympify(value, locals=local)

    def matrix(value):
        return sp.Matrix(
            [[expression(entry) for entry in row] for row in value]
        )

    kallen = x**2+2*(1+r)*x+(1-r)**2
    delta = sp.sqrt(kallen)
    qx = sp.factor((2*x*(1+r)+(1-r)**2)/(2*x**2))
    q = -qx
    v = a2/2
    J = sp.Matrix([[0, 1], [1, 0]])
    eta = sp.kronecker_product(J, 3*J)
    Np = sp.Matrix([[v, 0], [0, v], [q, 0], [0, q]])
    Nm = sp.Matrix([[v, 0], [0, v], [-q, 0], [0, -q]])
    raw_image = sp.simplify(Np.T*eta*Np)
    raw_kernel = sp.simplify(Nm.T*eta*Nm)
    fixed = sp.simplify(raw_image*J)
    flipped = sp.simplify(raw_image*(-J))
    R = sp.Matrix.hstack(sp.eye(2), sp.eye(2))
    D = sp.diag(q, q, v, v)
    collapsed = sp.simplify(R*D*Np)

    density = sp.factor(qx*delta/((1+r)*x))
    infinity_limit = sp.simplify(sp.limit(x*density, x, sp.oo))
    unequal_zero = sp.simplify(
        sp.limit(x**3*density, x, 0, dir="+")
    )
    equal_zero = sp.simplify(
        sp.limit(x**sp.Rational(3, 2)*density.subs(r, 1), x, 0, dir="+")
    )
    rp, xp = 1/r, x/r
    kallen_pull = sp.factor(
        kallen.subs({r: rp, x: xp}, simultaneous=True)/kallen
    )
    q_pull = sp.factor(
        qx.subs({r: rp, x: xp}, simultaneous=True)/qx
    )
    density_pull = sp.simplify(
        density.subs({r: rp, x: xp}, simultaneous=True)
        * sp.diff(xp, x)/density
    )

    # Independently differentiate the producer's displayed primitive after
    # reconstructing the crossed rationalizing substitution.
    primitive = expression(resolution["primitive"])
    A = 1+m**2
    xz = m*(z+1/z)-A
    deltaz = m*(1/z-z)
    qxz = sp.factor((2*xz*A+(1-m**2)**2)/(2*xz**2))
    densityz = sp.factor(qxz*deltaz/(A*xz)*sp.diff(xz, z))

    expected_marks = list(range(3, 15))
    expected_missing = chambers["order_chamber_completion"][
        "missing_crossed_sheets"
    ][2]
    first_rho = sp.factor(
        (1-r)**2*(2*x*(1+r)+(1-r)**2)/(4*x**3)
    )

    checks = {
        "schema_validation": True,
        "all_input_hashes_match": all(
            row["sha256"] == sha256(row["path"]) for row in inputs
        ),
        "predecessors_pass": all(
            value["checks"]["ok"]
            for value in (first, quotient, nested, chambers)
        ),
        "crossed_kallen_reconstructs": sp.simplify(
            expression(analytic["kallen_polynomial"])-kallen
        ) == 0,
        "crossed_root_reconstructs": sp.simplify(
            expression(analytic["kallen_root"])**2-kallen
        ) == 0,
        "continued_q_reconstructs": sp.simplify(
            expression(analytic["continued_q"])+qx
        ) == 0,
        "positive_qx_reconstructs": sp.simplify(
            expression(analytic["positive_q_cross"])-qx
        ) == 0,
        "continued_eigenvalue_reconstructs": sp.simplify(
            expression(analytic["continued_nonzero_quotient_eigenvalue"])
            + a2*qx
        ) == 0,
        "external_sign_is_even_and_unflipped": (
            analytic["external_delta_prime_sign"] == 1
            and "six external" in analytic["sign_reason"]
        ),
        "first_crossed_pair_remains_positive_formula": sp.simplify(
            expression(analytic["first_crossed_pair_rho"])-first_rho
        ) == 0,
        "parent_profile_metric_reconstructs": matrix(
            crossed["parent_profile_metric"]
        ) == eta,
        "image_basis_reconstructs": sp.simplify(
            matrix(crossed["image_basis"])-Np
        ) == sp.zeros(4, 2),
        "kernel_basis_reconstructs": sp.simplify(
            matrix(crossed["kernel_basis"])-Nm
        ) == sp.zeros(4, 2),
        "raw_image_gram_reconstructs": sp.simplify(
            matrix(crossed["image_raw_gram"])-raw_image
        ) == sp.zeros(2),
        "raw_kernel_gram_reconstructs": sp.simplify(
            matrix(crossed["kernel_raw_gram"])-raw_kernel
        ) == sp.zeros(2),
        "kernel_image_is_orthogonal": sp.simplify(Nm.T*eta*Np)
        == sp.zeros(2),
        "fixed_hilbertization_is_negative": sp.simplify(matrix(
            crossed["fixed_profile_swap_hilbertized_gram"]
        )-fixed) == sp.zeros(2) and sp.simplify(
            fixed+3*a2*qx*sp.eye(2)
        ) == sp.zeros(2),
        "flipped_hilbertization_is_positive": sp.simplify(matrix(
            crossed["branch_flipped_hilbertized_gram"]
        )-flipped) == sp.zeros(2) and sp.simplify(
            flipped-3*a2*qx*sp.eye(2)
        ) == sp.zeros(2),
        "inertias_are_exact": (
            crossed["inertia_with_certified_sharp"] == [0, 2, 0]
            and crossed["inertia_after_branch_flip"] == [2, 0, 0]
        ),
        "collapse_reconstructs_negative_scalar": sp.simplify(matrix(
            crossed["collapse_on_image"]
        )-collapsed) == sp.zeros(2) and sp.simplify(
            collapsed+a2*qx*sp.eye(2)
        ) == sp.zeros(2),
        "positive_source_no_isometry_statement_retained": (
            "no solution" in crossed["no_isometry_theorem"]
            and "<0" in crossed["no_isometry_theorem"]
        ),
        "absolute_density_reconstructs": sp.simplify(
            expression(resolution["density"])-density
        ) == 0,
        "bilateral_endpoint_limits_reconstruct": (
            infinity_limit == 1
            and sp.simplify(
                unequal_zero
                - (r**2-2*r+1)**sp.Rational(3, 2)/(2*(r+1))
            ) == 0
            and equal_zero == 2
        ),
        "daughter_exchange_reconstructs": (
            kallen_pull == r**-2 and q_pull == 1 and density_pull == 1
        ),
        "geometric_reference_is_exchange_fixed": sp.simplify(
            sp.sqrt(1/r)-sp.sqrt(r)/r
        ) == 0 and resolution["exchange_fixed_reference"] == "x0=sqrt(r)",
        "primitive_differentiates_exactly": sp.factor(
            sp.diff(primitive, z)-densityz
        ) == 0,
        "resolution_range_is_bilateral": (
            "whole real line" in resolution["range"]
            and "L2(R" in resolution["direct_integral_unitary_after_branch_flip"]
        ),
        "unilateral_is_only_a_dilation_subspace": (
            "Zero extension" in resolution["unilateral_embedding"]
            and "only after" in resolution["dilation_boundary"]
        ),
        "all_twelve_history_marks_match": (
            histories["edge_marks"] == expected_marks
            and histories["reversed_history_count"] == expected_missing == 12
            and nested["ordered_two_noise_intertwiner"]["edge_marks"]
            == expected_marks
        ),
        "history_status_is_obstruction_not_affiliation": (
            histories["status"]
            == "ALL_TWELVE_ONE_BRANCH_CROSSED_INTERTWINERS_OBSTRUCTED_BY_THE_SAME_RANK_TWO_SIGN"
        ),
        "claim_boundary_remains_fail_closed": (
            disposition["positive_isometry_with_certified_sharp"]
            == "EXACTLY_OBSTRUCTED"
            and disposition["branch_flipped_bilateral_dilation"]
            == "CONSTRUCTED_CONDITIONALLY"
            and disposition["crossed_branch_sign_from_BT_dynamics"]
            == "NOT_DERIVED"
            and disposition["Eq19_all_orders"] == "NOT_PROVED"
            and disposition["spacetime_Moller_LSZ_S_operator"]
            == "NOT_CONSTRUCTED"
        ),
        "next_gate_requires_complete_crossed_detector": (
            "complete crossed 3->3 detector block" in certificate["next_gate"]
            and "both orientations" in certificate["next_gate"]
        ),
    }
    return {name: bool(value) for name, value in checks.items()}


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
