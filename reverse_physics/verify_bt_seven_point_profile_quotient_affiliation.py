#!/usr/bin/env python3
"""Independent verifier for the seven-point BT signed-profile quotient."""
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
    "REVERSE_PHYSICS_BT_SEVEN_POINT_PROFILE_QUOTIENT_AFFILIATION_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-seven-point-profile-quotient-affiliation-v1.schema.json",
)
SEVEN = os.path.join(
    ROOT,
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_SEVEN_POINT_COX_SELECTION_V1.json",
)
INTERFERENCE = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PARENT_JET_INTERFERENCE_V1.json",
)
SIX_QUOTIENT = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1.json",
)
BRANCHING = os.path.join(
    ROOT,
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_CHANNEL_RESOLVED_BRANCHING_INSTRUMENT_V1.json",
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


def parse_matrix(rows, local):
    import sympy as sp

    return sp.Matrix(
        [[sp.factor(sp.sympify(value, locals=local)) for value in row] for row in rows]
    )


def rational_matrix(rows):
    import sympy as sp

    return sp.Matrix([[frac(value) for value in row] for row in rows])


def fixture_replay(row):
    import sympy as sp

    a0, a1, tau1, a2, tau2, a3, tau3 = map(frac, row["parameters"])
    A = (a0 - a1) ** 2 - 2 * tau1 * (a0 + a1) + 2 * tau1**2
    B = a2 * A + 2 * tau2 * (-A + 3 * tau1**2)
    C = a2 * B + 2 * tau2**2 * (A + tau1**2)
    u = -A / (2 * tau1**2)
    v = (
        C * tau3**2
        - A * tau2**2 * (a3**2 - 2 * a3 * tau3 + 2 * tau3**2)
    ) / (4 * tau1**2 * tau2**2 * (tau3 + a3))
    J = sp.Matrix([[0, 1], [1, 0]])
    K = 3 * J
    eta = sp.Matrix(
        [[0, 0, 0, 3], [0, 0, 3, 0], [0, 3, 0, 0], [3, 0, 0, 0]]
    )
    R = sp.Matrix([[1, 0, 1, 0], [0, 1, 0, 1]])
    D = sp.diag(u, u, v, v)
    raw = eta.inv() * D.T * R.T * K * R * D
    physical = -raw
    P = raw / (2 * u * v)
    X = sp.Matrix([frac(value) for value in row["coefficients"]])
    collapse = R * D * X
    signed = -(collapse.T * K * collapse)[0]
    projected = (-2 * u * v) * ((P * X).T * eta * (P * X))[0]
    return (
        frac(row["A"]) == A
        and frac(row["C"]) == C
        and frac(row["u"]) == u
        and frac(row["v"]) == v
        and frac(row["signed_quotient_eigenvalue"]) == -2 * u * v > 0
        and rational_matrix(row["physical_raised_pullback"]) == physical
        and rational_matrix(row["projector"]) == P
        and frac(row["signed_physical_contraction"]) == signed
        and frac(row["signed_projected_contraction"]) == projected
        and signed == projected
        and all(row["signs"].values())
        and row["contractions_agree"] is True
    )


def verify(certificate):
    import sympy as sp

    schema_errors = list(Draft202012Validator(load(SCHEMA)).iter_errors(certificate))
    disposition = certificate.get("disposition", {})
    affiliation = certificate.get("branching_affiliation", {})
    quotient = certificate.get("physical_quotient", {})
    preflight = (
        not schema_errors
        and certificate.get("certificate")
        == "REVERSE_PHYSICS_BT_SEVEN_POINT_PROFILE_QUOTIENT_AFFILIATION_V1"
        and certificate.get("dependency_tags") == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
        and disposition.get("complete_2485_tree_pretrace_components") == "COMPUTED"
        and disposition.get("third_positive_scalar_species_jump")
        == "AMPLITUDE_AFFILIATED_ON_QUOTIENT"
        and disposition.get("fourth_jump") == "NOT_COMPUTED"
        and disposition.get("complete_BT_probability") == "NOT_CONSTRUCTED"
        and disposition.get("Eq19_all_orders") == "NOT_PROVED"
        and quotient.get("seven_external_delta_prime_sign") == -1
        and affiliation.get("third_jump")
        == "AMPLITUDE_AFFILIATED_ON_SEVEN_POINT_SIGNED_PROFILE_QUOTIENT"
        and "anything LORENTZIAN-CAUSAL" in certificate.get("does_not_establish", [])
    )
    if not preflight:
        return {"serialized_claim_preflight": False}

    a0, a1, a2, a3, e1, e2, tau1, tau2, tau3 = sp.symbols(
        "a0 a1 a2 a3 e1 e2 tau1 tau2 tau3"
    )
    symbols7 = (a0, a1, a2, a3, e1, e2, tau1, tau2, tau3)
    local7 = {symbol.name: symbol for symbol in symbols7}
    components = certificate["amplitude_components"]
    finite = {
        int(mask): sp.cancel(sp.sympify(value, locals=local7))
        for mask, value in components["finite_hierarchy_components"].items()
    }
    strong = {
        int(mask): sp.factor(sp.sympify(value, locals=local7))
        for mask, value in components["strong_order_components"].items()
    }
    A = (a0 - a1) ** 2 - 2 * tau1 * (a0 + a1) + 2 * tau1**2
    B = a2 * A + 2 * tau2 * (-A + 3 * tau1**2)
    C = a2 * B + 2 * tau2**2 * (A + tau1**2)
    Drec = a3 * C + 2 * tau3 * (-C + 3 * tau2**2 * A)
    F1 = sp.factor(-a3**2 * C / (16 * tau1**2 * tau2**2 * tau3))
    F2 = sp.factor(-a3 * Drec / (16 * tau1**2 * tau2**2 * tau3**2))

    # Independent tree rail: explicit per-tree enumeration with invariant
    # triangle vertices, at a fixture not used by the producer.
    import verify_bt_seven_point_cox_selection as tree_verifier

    old_seven = load(SEVEN)
    point = tree_verifier.POINTS[0]
    hard_fixture = old_seven["correlated_boundary"][
        "independent_verifier_hard_fixture"
    ]
    order, tree_count, _, leading = tree_verifier.exact_tree_kernel(
        point, hard_fixture, return_leading=True
    )
    substitution7 = dict(zip(symbols7, point))
    expected_components = {
        mask: Fraction(sp.Rational(expression.subs(substitution7)))
        for mask, expression in finite.items()
    }

    # Rebuild the parent profiles from the pinned finite-e six-point tensor.
    interference = load(INTERFERENCE)
    sa0, sa1, sa2, se, st1, st2 = sp.symbols("a0 a1 a2 e tau1 tau2")
    local6 = {
        symbol.name: symbol for symbol in (sa0, sa1, sa2, se, st1, st2)
    }
    six_finite = interference["amplitude_components"]["finite_e_leading_components"]
    six_singleton = sp.cancel(sp.sympify(six_finite["1"], locals=local6))
    six_pair = sp.cancel(sp.sympify(six_finite["3"], locals=local6))
    p = sp.symbols("p")
    parent_substitution = {
        sa0: p,
        sa1: a2,
        sa2: a3,
        se: e2,
        st1: tau2,
        st2: tau3,
    }
    parent_singleton = sp.cancel(six_singleton.subs(parent_substitution))
    parent_pair = sp.cancel(six_pair.subs(parent_substitution))
    H0s = sp.factor(parent_singleton.subs({p: 0, e2: 0}))
    H1s = sp.factor(sp.diff(parent_singleton, p).subs({p: 0, e2: 0}))
    H0p = sp.factor(parent_pair.subs({p: 0, e2: 0}))
    H1p = sp.factor(sp.diff(parent_pair, p).subs({p: 0, e2: 0}))
    profile = sp.Matrix([[H0s, H1s], [H0p, H1p]])
    u, v = [sp.factor(value) for value in profile.inv() * sp.Matrix([F1, F2])]
    expected_u = sp.factor(-A / (2 * tau1**2))
    expected_v = sp.factor(
        (C * tau3**2 - A * tau2**2 * (a3**2 - 2 * a3 * tau3 + 2 * tau3**2))
        / (4 * tau1**2 * tau2**2 * (tau3 + a3))
    )
    parent_record = certificate["recombined_six_point_parent"]
    serialized_parent = {
        key: sp.factor(sp.sympify(value, locals=local7))
        for key, value in parent_record.items()
    }
    serialized_u = sp.factor(
        sp.sympify(certificate["unique_factorization"]["u"], locals=local7)
    )
    serialized_v = sp.factor(
        sp.sympify(certificate["unique_factorization"]["v"], locals=local7)
    )

    # Exact algebra behind the open-domain sign proof.
    x, y = sp.symbols("x y", positive=True)
    threshold = (x + y) ** 2
    threshold_A = sp.expand(A.subs({a0: x**2, a1: y**2, tau1: threshold}))
    upper_gap_at_threshold = sp.Poly(
        sp.expand((2 * tau1**2 - A).subs({a0: x**2, a1: y**2, tau1: threshold})),
        x,
        y,
    )
    r, s = sp.symbols("r s", positive=True)
    g = lambda value: value**2 - 2 * value + 2
    bracket = A * (g(r) - g(s)) + 2 * tau1**2 * (3 * r + 1)
    lower_bound_gap = sp.expand(bracket - (-A + 2 * tau1**2))
    ratio_form = sp.factor(
        tau3**2 * bracket / (4 * tau1**2 * (tau3 + a3))
    )

    ug, vg = sp.symbols("u v", real=True, nonzero=True)
    z = sp.symbols("z")
    local_uv = {"u": ug, "v": vg, "z": z}
    J = sp.Matrix([[0, 1], [1, 0]])
    K = 3 * J
    eta = sp.Matrix(
        [[0, 0, 0, 3], [0, 0, 3, 0], [0, 3, 0, 0], [3, 0, 0, 0]]
    )
    R = sp.Matrix([[1, 0, 1, 0], [0, 1, 0, 1]])
    D4 = sp.diag(ug, ug, vg, vg)
    raw = (eta.inv() * D4.T * R.T * K * R * D4).applyfunc(sp.factor)
    physical = -raw
    P = (raw / (2 * ug * vg)).applyfunc(sp.factor)
    Nminus = sp.Matrix([[vg, 0], [0, vg], [-ug, 0], [0, -ug]])
    Nplus = sp.Matrix([[vg, 0], [0, vg], [ug, 0], [0, ug]])
    X = sp.Matrix(sp.symbols("l0 q0 l1 q1", real=True))
    collapsed = R * D4 * X
    pointwise = sp.simplify(
        -(collapsed.T * K * collapsed)[0]
        - (-2 * ug * vg) * ((P * X).T * eta * (P * X))[0]
    )
    charpoly = sp.factor(physical.charpoly(z).as_expr())
    serialized_eta = parse_matrix(certificate["declared_carrier"]["tensor_metric_eta"], local_uv)
    serialized_R = parse_matrix(certificate["declared_carrier"]["physical_collapse_R"], local_uv)
    serialized_physical = parse_matrix(quotient["physical_raised_pullback_generic"], local_uv)
    serialized_P = parse_matrix(quotient["projector_generic"], local_uv)
    serialized_kernel = parse_matrix(quotient["kernel_basis_columns"], local_uv)
    serialized_image = parse_matrix(quotient["image_basis_columns"], local_uv)

    six_quotient = load(SIX_QUOTIENT)
    branching = load(BRANCHING)
    second = frac(six_quotient["branching_affiliation"]["second_selected_history"])
    third = frac(
        old_seven["threshold_analysis"]["normalization"]
        ["selected_nested_history_relative_to_Born"]
    )
    recorded_rates = list(map(frac, branching["rate_factorization"]["extension_rate_squares"]))
    inputs = certificate["provenance"]["inputs"]
    fixtures = quotient["exact_fixtures"]
    checks = {
        "schema_and_claim_boundary": not schema_errors,
        "dependency_tags_and_lifecycle": certificate["dependency_tags"]
        == ["LOCAL-ALGEBRAIC", "REDUCED-MODE"]
        and certificate["lifecycle_state"] == "COEFFICIENT_COMPUTED",
        "independent_explicit_tree_count_and_order": tree_count == 2485 and order == 2,
        "independent_all_mask_component_match": leading.coefficients == expected_components,
        "all_seven_masks_and_no_cubic_profile": sorted(finite) == list(range(7))
        and 7 not in finite,
        "finite_to_strong_limit": all(
            sp.simplify(finite[mask].subs({e1: 0, e2: 0}) - strong[mask]) == 0
            for mask in finite
        ),
        "singleton_and_pair_permutation_equalities": strong[1] == strong[2] == strong[4]
        and strong[3] == strong[5] == strong[6],
        "compact_F1_F2": sp.simplify(strong[1] - F1) == 0
        and sp.simplify(strong[3] - F2) == 0
        and sp.simplify(sp.sympify(components["F1_singleton"], locals=local7) - F1) == 0
        and sp.simplify(sp.sympify(components["F2_complementary_pair"], locals=local7) - F2) == 0,
        "scalar_square_reconstruction": sp.simplify(
            6 * F1 * F2
            - 3 * a3**3 * C * Drec / (128 * tau1**4 * tau2**4 * tau3**3)
        ) == 0,
        "parent_profiles_rebuilt": all(
            sp.simplify(serialized_parent[key] - value) == 0
            for key, value in {
                "H0_singleton": H0s,
                "H1_singleton": H1s,
                "H0_pair": H0p,
                "H1_pair": H1p,
                "determinant": profile.det(),
            }.items()
        ),
        "parent_matrix_invertible": sp.simplify(
            profile.det() - 3 * a3**3 * (a3 + tau3) / (16 * tau3**4)
        ) == 0,
        "unique_factorization": sp.simplify(u - expected_u) == 0
        and sp.simplify(v - expected_v) == 0
        and sp.simplify(serialized_u - u) == 0
        and sp.simplify(serialized_v - v) == 0
        and sp.simplify(profile * sp.Matrix([u, v]) - sp.Matrix([F1, F2]))
        == sp.zeros(2, 1),
        "inner_threshold_A_positive": sp.simplify(threshold_A - threshold**2) == 0,
        "A_below_two_tau1_squared": all(coefficient > 0 for coefficient in upper_gap_at_threshold.coeffs())
        and sp.diff(2 * tau1**2 - A, tau1) == 2 * (a0 + a1),
        "v_ratio_identity_and_positive_bound": sp.simplify(
            expected_v.subs({a2: r * tau2, a3: s * tau3})
            - ratio_form.subs(a3, s * tau3)
        ) == 0
        and sp.simplify(lower_bound_gap - (A * (g(r) - g(s) + 1) + 6 * tau1**2 * r)) == 0,
        "serialized_carrier": serialized_eta == eta and serialized_R == R and eta.det() == 81,
        "physical_pullback_spectrum": serialized_physical == physical
        and physical.rank() == 2
        and sp.simplify(charpoly - z**2 * (z + 2 * ug * vg) ** 2) == 0,
        "projector_exact_selfadjoint": serialized_P == P
        and sp.simplify(P * P - P) == sp.zeros(4)
        and sp.simplify(eta.inv() * P.T * eta - P) == sp.zeros(4),
        "kernel_exact_nondegenerate_invisible": serialized_kernel == Nminus
        and physical * Nminus == sp.zeros(4, 2)
        and R * D4 * Nminus == sp.zeros(2)
        and (Nminus.T * eta * Nminus).det() != 0,
        "image_exact_orthogonal": serialized_image == Nplus
        and P * Nplus == Nplus
        and Nminus.T * eta * Nplus == sp.zeros(2)
        and (Nplus.T * eta * Nplus).det() != 0,
        "negative_image_orientation_hilbertized": sp.simplify(
            Nplus.T * eta * Nplus - 6 * ug * vg * J
        ) == sp.zeros(2)
        and sp.simplify((Nplus.T * eta * Nplus) * (-J) + 6 * ug * vg * sp.eye(2))
        == sp.zeros(2),
        "signed_pointwise_identity": pointwise == 0,
        "three_exact_fraction_fixtures": len(fixtures) == 3
        and all(fixture_replay(row) for row in fixtures),
        "conditional_third_rate_imported": third == Fraction(9, 81920)
        and second == Fraction(5, 3072)
        and third / second == Fraction(27, 400)
        and frac(affiliation["conditional_third_rate"]) == Fraction(27, 400)
        and recorded_rates == [Fraction(1, 48), Fraction(5, 64), Fraction(27, 400)],
        "tree_phase_topology_independent": {
            (-sp.I) ** vertices * sp.I ** (vertices - 1) for vertices in range(1, 8)
        } == {-sp.I},
        "sixty_histories_permutation_carried": certificate["declared_carrier"]["history_count"] == 60
        and old_seven["threshold_analysis"]["normalization"]["labeled_nested_histories"] == 60,
        "provenance_hashes": len(inputs) == 5
        and all(row["sha256"] == sha256(row["path"]) for row in inputs),
        "producer_checks_intact": certificate["checks"]["passed"]
        == certificate["checks"]["total"]
        == 41
        and certificate["checks"]["failures"] == []
        and all(certificate["checks"]["details"].values()),
        "open_claims_remain_open": disposition["fourth_jump"] == "NOT_COMPUTED"
        and disposition["complete_BT_probability"] == "NOT_CONSTRUCTED"
        and disposition["Eq19_all_orders"] == "NOT_PROVED"
        and "anything LORENTZIAN-CAUSAL" in certificate["does_not_establish"],
    }
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    try:
        checks = verify(load(args.verify))
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        print("[FAIL] verifier exception:", exc)
        return 1
    failed = [name for name, ok in checks.items() if not ok]
    for name in failed:
        print("[FAIL]", name)
    print("checks %d/%d" % (len(checks) - len(failed), len(checks)))
    print("INDEPENDENT RESULT:", "PASS" if not failed else "FAIL")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
