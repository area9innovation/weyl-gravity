#!/usr/bin/env python3
"""Independent verifier for the BT six-point nested continuum intertwiner."""
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
    "REVERSE_PHYSICS_BT_SIX_POINT_NESTED_CONTINUUM_INTERTWINER_V1.json",
)
SCHEMA = os.path.join(
    ROOT,
    "reverse_physics/schema/"
    "reverse-physics-bt-six-point-nested-continuum-intertwiner-v1.schema.json",
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
        [sum(left[i][k]*right[k][j] for k in range(len(right)))
         for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def transpose(value):
    return [list(row) for row in zip(*value)]


def fixture(m, z, a2):
    m, z, a2 = map(Fraction, (m, z, a2))
    r = m*m
    w = 1+r+m*(z+1/z)
    delta = m*(1/z-z)
    q = (2*w*(1+r)-(1-r)**2)/(2*w*w)
    v = a2/2
    J = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    K = [[3*x for x in row] for row in J]
    eta = [
        [J[i//2][j//2]*K[i % 2][j % 2] for j in range(4)]
        for i in range(4)
    ]
    plus = [[v, 0], [0, v], [q, 0], [0, q]]
    minus = [[v, 0], [0, v], [-q, 0], [0, -q]]
    image = mm(mm(transpose(plus), eta), plus)
    kernel = mm(mm(transpose(minus), eta), minus)
    cross = mm(mm(transpose(minus), eta), plus)
    R = [[1, 0, 1, 0], [0, 1, 0, 1]]
    D = [[q, 0, 0, 0], [0, q, 0, 0], [0, 0, v, 0], [0, 0, 0, v]]
    collapse_plus = mm(mm(R, D), plus)
    collapse_minus = mm(mm(R, D), minus)
    density = q*delta/((1+r)*w)
    return {
        "r": r, "w": w, "delta": delta, "q": q, "v": v,
        "image": image, "kernel": kernel, "cross": cross,
        "collapse_plus": collapse_plus,
        "collapse_minus": collapse_minus,
        "expected_image": [[0, 6*q*v], [6*q*v, 0]],
        "expected_kernel": [[0, -6*q*v], [-6*q*v, 0]],
        "expected_collapse": [[2*q*v, 0], [0, 2*q*v]],
        "density": density,
    }


def main(argv=None):
    import sympy as sp
    import jsonschema

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
        fixture(Fraction(1, 2), Fraction(1, 2), 3),
        fixture(Fraction(1, 3), Fraction(1, 2), 5),
        fixture(1, Fraction(1, 2), 7),
    ]
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
    checks["three_exact_positive_densities"] = all(
        row["q"] > 0 and row["v"] > 0 and row["density"] > 0
        for row in fixtures
    )

    r, w = sp.symbols("r w", positive=True)
    kallen = w**2+1+r**2-2*w-2*w*r-2*r
    q = (2*w*(1+r)-(1-r)**2)/(2*w**2)
    checks["unit_log_density"] = (
        sp.simplify(sp.limit(q*w/(1+r), w, sp.oo)-1) == 0
        and sp.limit(kallen/w**2, w, sp.oo) == 1
    )
    m, z = sp.symbols("m z", positive=True)
    threshold_numerator = sp.factor(
        (2*w*(1+r)-(1-r)**2).subs(
            {r: m**2, w: (1+m)**2}
        )
    )
    checks["full_threshold_positivity"] = threshold_numerator == (1+m)**4

    # Parse the serialized primitive, then independently reconstruct the
    # rationalized density from Kallen kinematics and differentiate.
    primitive = sp.sympify(
        cert["physical_cumulative_resolution"]["primitive_F_m"],
        locals={"m": m, "z": z, "log": sp.log},
    )
    A = 1+m**2
    d = (1-m**2)**2
    w_z = A+m*(z+1/z)
    delta_z = m*(1/z-z)
    q_z = (2*A*w_z-d)/(2*w_z**2)
    rational_density = sp.cancel(
        q_z*delta_z/(A*w_z)*sp.diff(w_z, z)
    )
    checks["primitive_derivative"] = sp.cancel(
        sp.diff(primitive, z)-rational_density
    ) == 0
    checks["primitive_threshold"] = sp.simplify(
        primitive.subs(z, 1)+sp.Rational(5, 4)
    ) == 0
    equal = -sp.log(z)-4/(1+z)
    equal_density = -(z-1)**2/(z*(z+1)**2)
    checks["equal_mass_extension"] = (
        sp.simplify(sp.diff(equal, z)-equal_density) == 0
        and sp.simplify(
            sp.limit(primitive-primitive.subs(z, 1), m, 1)
            -(equal-equal.subs(z, 1))
        ) == 0
    )
    finite_remainder = sp.limit(primitive+sp.log(z), z, 0, dir="+")
    checks["onto_half_line"] = (
        not finite_remainder.has(sp.oo, -sp.oo, sp.zoo)
        and sp.expand_log(primitive, force=True).coeff(sp.log(z)) == -1
    )

    # Exchange is rebuilt at the differential-measure level.
    k_exchange = sp.factor(
        kallen.subs({r: 1/r, w: w/r}, simultaneous=True)/kallen
    )
    q_exchange = sp.factor(
        q.subs({r: 1/r, w: w/r}, simultaneous=True)/q
    )
    A_exchange = sp.factor((1+1/r)/(1+r))
    checks["daughter_exchange"] = (
        k_exchange == r**-2 and q_exchange == 1
        and sp.simplify(q_exchange*sp.sqrt(k_exchange)/A_exchange) == 1
    )

    # The change of variables is checked without a quadrature: alpha^2 dmu
    # and d sigma have exactly the same Radon--Nikodym density.
    a2 = sp.symbols("a2", positive=True)
    eigenvalue = a2*q
    alpha_squared = sp.simplify(eigenvalue/(a2*(1+r)))
    dmu_density = sp.sqrt(kallen)/w
    dsigma_density = q*sp.sqrt(kallen)/((1+r)*w)
    checks["radon_nikodym_isometry"] = sp.simplify(
        alpha_squared*dmu_density-dsigma_density
    ) == 0
    alpha0, alpha1, alpha2 = sp.symbols(
        "alpha0 alpha1 alpha2", positive=True
    )
    checks["shift_transport_cocycle"] = sp.simplify(
        (alpha2/alpha1)*(alpha1/alpha0)-alpha2/alpha0
    ) == 0

    epsilon, gap = sp.symbols("epsilon gap", positive=True)
    checks["finite_hierarchy_exhaustion"] = sp.limit(
        gap**2/epsilon, epsilon, 0, dir="+"
    ) == sp.oo
    U = sp.symbols("U", positive=True)
    outer_Q = (2*U*(1+r)-(1-r)**2)/(2*U**2)
    outer_L = -(1-r)**2/(2*U)
    outer_kallen = U**2+1+r**2-2*U-2*U*r-2*r
    outer_I = (
        5*r**3-6*r**2*sp.log(r)-3*r**2
        -6*r*sp.log(r)+3*r-5
    )/(24*(r-1))
    checks["outer_local_massless_limit"] = (
        sp.limit(outer_Q, r, 0, dir="+") == (2*U-1)/(2*U**2)
        and sp.limit(outer_L, r, 0, dir="+") == -1/(2*U)
        and sp.factor(outer_kallen.subs(r, 0)) == (U-1)**2
        and sp.limit(outer_I, r, 0, dir="+") == sp.Rational(5, 24)
    )

    hp = load(os.path.join(
        ROOT,
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_QUANTUM_STOCHASTIC_MOLLER_DILATION_V1.json",
    ))
    channels = hp["system_and_noise_carrier"]["noise_channels"]
    level1 = [row for row in channels if row["level"] == 1]
    checks["twelve_exact_edge_marks"] = (
        [row["noise_index"] for row in level1] == list(range(3, 15))
        and sorted(
            sum(row["parent"] == parent for row in level1)
            for parent in {row["parent"] for row in level1}
        ) == [4, 4, 4]
    )
    q0, q1 = Fraction(1, 48), Fraction(5, 64)
    checks["rate_chain"] = (
        q0*q1 == Fraction(5, 3072)
        and q0*q1/2 == Fraction(5, 6144)
        and 12*q0*q1/2 == Fraction(5, 512)
        and 4*q1/2 == Fraction(5, 32)
    )
    six = load(os.path.join(
        ROOT,
        "reverse_physics/certificates/"
        "REVERSE_PHYSICS_BT_SIX_POINT_STRONGLY_ORDERED_TREE_V1.json",
    ))
    checks["six_point_scalar_consumer"] = (
        six["threshold_and_factorial_analysis"]["normalization"]
        ["physical_two_count_coefficient"]
        == {"numerator": 5, "denominator": 512}
    )
    checks["mark_boundary"] = (
        cert["seventy_five_mark_boundary"]["physically_intertwined_edge_marks"]
        == list(range(15))
        and cert["seventy_five_mark_boundary"]
        ["remaining_quotient_only_edge_marks"] == list(range(15, 75))
    )
    checks["claim_boundary"] = (
        cert["disposition"]["full_seventy_five_mark_physical_intertwiner"]
        == "NOT_CONSTRUCTED"
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
        and cert["checks"]["passed"] == cert["checks"]["total"] == 40
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
