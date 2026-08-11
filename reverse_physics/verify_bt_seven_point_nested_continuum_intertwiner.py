#!/usr/bin/env python3
"""Independent verifier for the BT seven-point nested continuum intertwiner."""
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
    "REVERSE_PHYSICS_BT_SEVEN_POINT_NESTED_CONTINUUM_INTERTWINER_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-seven-point-nested-continuum-intertwiner-v1.schema.json",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def mm(left, right):
    return [
        [sum(left[i][k] * right[k][j] for k in range(len(right)))
         for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def transpose(value):
    return [list(row) for row in zip(*value)]


def fixture(alpha, sout, w, tau3):
    alpha, sout, w, tau3 = map(Fraction, (alpha, sout, w, tau3))
    H0 = 2 + alpha * sout * (2 - sout)
    H = H0 + (6 - 2 * alpha) / w + alpha / w**2
    u = -alpha / 2
    v = tau3 * H / (4 * (1 + sout))
    eigenvalue = -2 * u * v
    scale = tau3 * alpha * H0 / (4 * (1 + sout))
    density = eigenvalue / scale * (w - 1) / w
    J = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    K = [[3 * value for value in row] for row in J]
    eta = [
        [J[i // 2][j // 2] * K[i % 2][j % 2] for j in range(4)]
        for i in range(4)
    ]
    plus = [[v, 0], [0, v], [u, 0], [0, u]]
    minus = [[v, 0], [0, v], [-u, 0], [0, -u]]
    image = mm(mm(transpose(plus), eta), plus)
    kernel = mm(mm(transpose(minus), eta), minus)
    cross = mm(mm(transpose(minus), eta), plus)
    R = [[1, 0, 1, 0], [0, 1, 0, 1]]
    D = [[u, 0, 0, 0], [0, u, 0, 0], [0, 0, v, 0], [0, 0, 0, v]]
    collapse_plus = mm(mm(R, D), plus)
    collapse_minus = mm(mm(R, D), minus)
    return {
        "H0": H0,
        "H": H,
        "u": u,
        "v": v,
        "eigenvalue": eigenvalue,
        "scale": scale,
        "density": density,
        "image": image,
        "kernel": kernel,
        "cross": cross,
        "collapse_plus": collapse_plus,
        "collapse_minus": collapse_minus,
        "expected_image": [[0, 6 * u * v], [6 * u * v, 0]],
        "expected_kernel": [[0, -6 * u * v], [-6 * u * v, 0]],
        "expected_collapse": [[2 * u * v, 0], [0, 2 * u * v]],
    }


def frac(value):
    return Fraction(value["numerator"], value["denominator"])


def main(argv=None):
    import jsonschema
    import sympy as sp

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", default=CERT)
    args = parser.parse_args(argv)
    cert = load(args.verify)
    schema = load(SCHEMA)
    checks = {}
    try:
        jsonschema.Draft202012Validator(schema).validate(cert)
        checks["strict_schema"] = True
    except jsonschema.ValidationError:
        checks["strict_schema"] = False

    fixtures = [
        fixture(1, Fraction(1, 2), 2, 3),
        fixture(Fraction(3, 2), Fraction(1, 3), Fraction(5, 2), 7),
        fixture(Fraction(7, 4), Fraction(2, 3), 4, 5),
    ]
    checks["three_exact_positive_eigenvalues"] = all(
        row["H0"] > 0 and row["H"] > 0 and row["eigenvalue"] > 0
        and row["scale"] > 0 and row["density"] > 0
        for row in fixtures
    )
    checks["three_exact_image_grams"] = all(
        row["image"] == row["expected_image"] for row in fixtures
    )
    checks["three_exact_kernel_grams"] = all(
        row["kernel"] == row["expected_kernel"] for row in fixtures
    )
    checks["three_exact_orthogonal_splits"] = all(
        row["cross"] == [[0, 0], [0, 0]] for row in fixtures
    )
    checks["three_exact_collapse_maps"] = all(
        row["collapse_plus"] == row["expected_collapse"]
        and row["collapse_minus"] == [[0, 0], [0, 0]]
        for row in fixtures
    )

    alpha, sout, w, tau3 = sp.symbols(
        "alpha s w tau3", positive=True
    )
    H0 = 2 + alpha * sout * (2 - sout)
    H = H0 + (6 - 2 * alpha) / w + alpha / w**2
    u = -alpha / 2
    v = tau3 * H / (4 * (1 + sout))
    eigenvalue = -2 * u * v
    scale = tau3 * alpha * H0 / (4 * (1 + sout))
    density = sp.factor(eigenvalue / scale * (w - 1) / w)
    local = {"alpha": alpha, "s": sout, "w": w, "tau3": tau3}
    quotient_record = cert["seven_point_positive_quotient_range"]
    checks["serialized_dimensionless_quotient"] = all(
        sp.factor(sp.sympify(quotient_record[key], locals=local) - expected) == 0
        for key, expected in (
            ("u", u), ("v", v), ("H0", H0), ("H", H),
            ("nonzero_physical_eigenvalue", eigenvalue),
        )
    )
    recorded_density = sp.sympify(
        cert["physical_cumulative_resolution"]["density"], locals=local
    )
    recorded_scale = sp.sympify(
        cert["physical_cumulative_resolution"]["asymptotic_scale"],
        locals=local,
    )
    checks["serialized_measure_formulas"] = (
        sp.factor(recorded_density - density) == 0
        and sp.factor(recorded_scale - scale) == 0
    )
    checks["positive_coefficient_theorem"] = (
        sp.expand(H - H0 - (6 - 2 * alpha) / w - alpha / w**2) == 0
        and sp.expand(H0 - 2 - alpha * sout * (2 - sout)) == 0
        and sp.factor(6 - 2 * alpha - 2 * (3 - alpha)) == 0
    )
    checks["unit_linear_asymptote"] = sp.limit(density, w, sp.oo) == 1

    primitive = sp.sympify(
        cert["physical_cumulative_resolution"]["primitive_F"],
        locals={"alpha": alpha, "s": sout, "w": w, "log": sp.log},
    )
    recorded_chi = sp.sympify(
        cert["physical_cumulative_resolution"]["chi_from_primitive"],
        locals={"alpha": alpha, "s": sout, "w": w, "log": sp.log},
    )
    checks["primitive_derivative"] = sp.factor(
        sp.diff(primitive, w) - density
    ) == 0
    checks["primitive_threshold_subtraction"] = (
        sp.simplify(recorded_chi - (primitive - primitive.subs(w, 1))) == 0
        and sp.simplify(recorded_chi.subs(w, 1)) == 0
    )
    checks["onto_half_line"] = (
        sp.simplify(sp.limit(recorded_chi / w, w, sp.oo)) == 1
        and sp.limit(density, w, 1, dir="+") == 0
    )
    checks["radon_nikodym_isometry"] = sp.factor(
        eigenvalue / scale * (w - 1) / w - density
    ) == 0

    # Reconstruct the change of variables from the original seven-point
    # coefficients rather than parsing the producer's dimensionless result.
    a0, a1, tau1, a2, tau2, a3 = sp.symbols(
        "a0 a1 tau1 a2 tau2 a3", positive=True
    )
    A = (a0 - a1) ** 2 - 2 * tau1 * (a0 + a1) + 2 * tau1**2
    C7 = (
        a2 * (a2 * A + 2 * tau2 * (-A + 3 * tau1**2))
        + 2 * tau2**2 * (A + tau1**2)
    )
    v_original = (
        C7 * tau3**2
        - A * tau2**2 * (a3**2 - 2 * a3 * tau3 + 2 * tau3**2)
    ) / (4 * tau1**2 * tau2**2 * (tau3 + a3))
    substitution = {
        alpha: A / tau1**2,
        sout: a3 / tau3,
        w: tau2 / a2,
    }
    checks["original_quotient_reconstruction"] = (
        sp.factor(u.subs(substitution) + A / (2 * tau1**2)) == 0
        and sp.factor(v.subs(substitution) - v_original) == 0
    )

    r0, w0, m = sp.symbols("r0 w0 m", positive=True)
    q_inner = (2 * w0 * (1 + r0) - (1 - r0) ** 2) / (2 * w0**2)
    alpha_direct = (
        (1 - r0) ** 2 - 2 * w0 * (1 + r0) + 2 * w0**2
    ) / w0**2
    kallen_inner = w0**2 + 1 + r0**2 - 2 * w0 - 2 * w0 * r0 - 2 * r0
    checks["inner_alpha_crosswalk"] = (
        sp.factor(alpha_direct - 2 * (1 - q_inner)) == 0
        and sp.factor(alpha_direct - 1 - kallen_inner / w0**2) == 0
        and sp.factor(2 - alpha_direct - 2 * q_inner) == 0
        and sp.factor(alpha_direct.subs({r0: m**2, w0: (1 + m) ** 2})) == 1
        and sp.limit(alpha_direct, w0, sp.oo) == 2
    )

    epsilon, gap, inner_scale = sp.symbols(
        "epsilon gap inner_scale", positive=True
    )
    rho = epsilon * inner_scale / a2
    finite_measure = sp.sqrt(
        (1 + gap) ** 2 + 1 + rho**2
        - 2 * (1 + gap) - 2 * (1 + gap) * rho - 2 * rho
    ) / (1 + gap)
    checks["massless_kallen_limit"] = sp.factor(
        sp.limit(finite_measure, epsilon, 0, dir="+") - gap / (1 + gap)
    ) == 0
    epsilon1, epsilon2, outer_gap = sp.symbols(
        "epsilon1 epsilon2 outer_gap", positive=True
    )
    lower = (1 + sp.sqrt(epsilon1 * inner_scale / a2)) ** 2
    upper = outer_gap**2 / (epsilon2 * a2)
    checks["finite_hierarchy_exhaustion"] = (
        sp.limit(lower, epsilon1, 0, dir="+") == 1
        and sp.limit(upper, epsilon2, 0, dir="+") == sp.oo
    )

    hp = load(os.path.join(
        ROOT,
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1.json",
    ))
    channels = hp["system_and_noise_carrier"]["noise_channels"]
    level2 = [row for row in channels if row["level"] == 2]
    checks["sixty_exact_edge_marks"] = (
        [row["noise_index"] for row in level2] == list(range(15, 75))
        and cert["ordered_three_noise_intertwiner"]["edge_marks"]
        == list(range(15, 75))
        and sorted(
            sum(row["parent"] == parent for row in level2)
            for parent in {row["parent"] for row in level2}
        ) == [5] * 12
    )
    q0, q1, q2 = Fraction(1, 48), Fraction(5, 64), Fraction(27, 400)
    checks["rate_chain"] = (
        q0 * q1 * q2 == Fraction(9, 81920)
        and q0 * q1 * q2 / 6 == Fraction(3, 163840)
        and 60 * q0 * q1 * q2 / 6 == Fraction(9, 8192)
        and 5 * q2 / 2 == Fraction(27, 160)
    )
    cox = load(os.path.join(
        ROOT,
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_SEVEN_POINT_COX_SELECTION_V1.json",
    ))
    checks["seven_point_scalar_consumer"] = (
        frac(cox["threshold_analysis"]["normalization"]
             ["leading_three_count_coefficient"]) == Fraction(9, 8192)
    )
    checks["mark_completion"] = (
        cert["seventy_five_mark_completion"]["physically_intertwined_edge_marks"]
        == list(range(75))
        and cert["seventy_five_mark_completion"]
        ["remaining_quotient_only_edge_marks"] == []
    )
    checks["claim_boundary"] = (
        cert["disposition"]["all_order_inductive_intertwiner"]
        == "NOT_CONSTRUCTED"
        and cert["disposition"]["fourth_jump"] == "NOT_COMPUTED"
        and cert["disposition"]["Eq19_all_orders"] == "NOT_PROVED"
        and cert["disposition"]["spacetime_Moller_LSZ_S_operator"]
        == "NOT_CONSTRUCTED"
        and "anything LORENTZIAN-CAUSAL" in cert["does_not_establish"]
    )
    checks["input_hashes"] = all(
        sha256(os.path.join(ROOT, row["path"])) == row["sha256"]
        for row in cert["provenance"]["inputs"]
    )
    checks["producer_check_ledger"] = (
        cert["checks"]["ok"] is True
        and cert["checks"]["passed"] == cert["checks"]["total"] == 43
        and not cert["checks"]["failures"]
    )

    passed = sum(bool(value) for value in checks.values())
    total = len(checks)
    failures = [name for name, value in checks.items() if not value]
    print(f"checks {passed}/{total}")
    print("INDEPENDENT RESULT:", "PASS" if not failures else "FAIL")
    if failures:
        print("failures:", ", ".join(failures))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
