#!/usr/bin/env python3
"""Independent verifier for RW/Maxwell simplicity and endomorphisms."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_data(data: dict, check_imports: bool = True) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    require(
        data.get("status") == "EXACT_RW_MAXWELL_SIMPLICITY_ENDOMORPHISMS_PASS",
        "status mismatch",
    )
    flags = data.get("claim_flags", {})
    expected_true = [
        "spin2_simple_all_ell_positive_real",
        "maxwell_simple_all_ell_positive_real",
        "spin2_endomorphism_ring_scalar_positive_real",
        "maxwell_endomorphism_ring_scalar_positive_real",
        "spin2_algebraically_special_controls_exact",
        "axial_ell2_nonsplit_all_positive_real",
        "only_plus_minus_identity_axial_ell2_positive_real",
    ]
    expected_false = [
        "spin2_simple_at_algebraically_special_points",
        "local_rational_positive_c_axial_ell2_exists",
        "nonlocal_c_excluded",
        "all_ell_bach_nonsplitting_established",
        "physical_qnm_smith_case_selected",
        "green_resolvent_double_pole_established",
        "quantum_statement",
    ]
    for key in expected_true:
        require(flags.get(key) is True, f"required true flag changed: {key}")
    for key in expected_false:
        require(flags.get(key) is False, f"required false flag changed: {key}")

    r, w, ll = sp.symbols("r w ll", nonzero=True)
    sig = sp.symbols("sig")
    a, b = sp.symbols("a b")
    f = 1 - 2 / r

    def dx(expr: sp.Expr) -> sp.Expr:
        return sp.factor(f * sp.diff(expr, r))

    # Re-derive the conjugated spin-two residual independently.
    potential2 = f * (ll / r**2 - 6 / r**3)
    trial = a + b / r
    residual = sp.factor(
        dx(dx(trial)) + 2 * sp.I * sig * w * dx(trial) - potential2 * trial
    )
    numerator = sp.Poly(sp.together(residual).as_numer_denom()[0], r)
    require(numerator.degree() == 2, "unexpected spin-two residual degree")
    as_frequency = sig * sp.I * ll * (ll - 2) / 12
    as_prefactor = 1 + 6 / ((ll - 2) * r)
    as_check = sp.factor(
        (
            dx(dx(as_prefactor))
            + 2 * sp.I * sig * as_frequency * dx(as_prefactor)
            - potential2 * as_prefactor
        ).subs(sig**2, 1)
    )
    require(as_check == 0, "algebraically-special control failed")

    declared = data.get("spin2_simplicity", {})
    require(
        declared.get("algebraically_special_frequency")
        == "omega=sigma*I*Lambda*(Lambda-2)/12",
        "algebraically-special frequency mutated",
    )
    require(
        declared.get("algebraically_special_prefactor")
        == "F=1+6/((Lambda-2)*r)",
        "algebraically-special prefactor mutated",
    )
    require(
        declared.get("ell2_control") == "omega=2*sigma*I, F=1+3/(2*r)",
        "ell=2 algebraically-special control mutated",
    )

    # Independently admit the opposite Jost sign at the three imaginary frame
    # events and solve the complete bounded rational ansatz.
    frame_results = data.get("ell2_frame_event_audit", {}).get("results", {})
    for event in (sp.Rational(1, 4), sp.Rational(1, 2), sp.Integer(1)):
        event_omega = sp.I * event
        require(str(event_omega) in frame_results, "missing frame-event audit")
        for sign in (1, -1):
            horizon_order = sp.simplify(-4 * sign * sp.I * event_omega)
            if horizon_order > 0:
                variables = sp.symbols(f"v{event}_{sign}_0:2")
                event_trial = variables[0] + variables[1] / r
            else:
                pole_order = int(-horizon_order)
                variables = sp.symbols(
                    f"v{event}_{sign}_0:{pole_order + 2}"
                )
                event_trial = sum(
                    value * r**power
                    for power, value in enumerate(variables)
                ) / (r * (r - 2) ** pole_order)
            event_residual = sp.together(
                dx(dx(event_trial))
                + 2 * sp.I * sign * event_omega * dx(event_trial)
                - potential2.subs(ll, 6) * event_trial
            )
            event_equations = sp.Poly(
                event_residual.as_numer_denom()[0], r
            ).all_coeffs()
            zero_tuple = tuple(sp.Integer(0) for _ in variables)
            require(
                sp.linsolve(event_equations, variables)
                == sp.FiniteSet(zero_tuple),
                f"frame-event rational kernel {event_omega}, sign {sign}",
            )
            require(
                frame_results.get(str(event_omega), {})
                .get(str(sign), {})
                .get("solution")
                == "ZERO_ONLY",
                "stored frame-event result mutated",
            )

    # Independent local-exponent checks.
    local = data.get("local_exhaustion", {})
    require(local.get("spin2_exponents", {}).get("r0") == [-1, 3], "spin2 exponents")
    require(local.get("maxwell_exponents", {}).get("r0") == [0, 2], "Maxwell exponents")
    require(
        local.get("spin2_symmetric_square_exponents", {}).get("r0")
        == [-2, 2, 6],
        "spin2 symmetric-square exponents",
    )
    require(
        local.get("maxwell_symmetric_square_exponents", {}).get("r0")
        == [0, 2, 4],
        "Maxwell symmetric-square exponents",
    )
    require(
        local.get("spin2_endomorphism_ansatz") == "q=q0+q1/r+q2/r^2",
        "spin2 terminal ansatz mutated",
    )

    # Re-derive the symmetric-square rational kernels independently.
    q0, q1, q2 = sp.symbols("q0 q1 q2")

    def third(u: sp.Expr, q: sp.Expr) -> sp.Expr:
        return sp.factor(dx(dx(dx(q))) + 4 * u * dx(q) + 2 * dx(u) * q)

    u2 = w**2 - potential2
    q = q0 + q1 / r + q2 / r**2
    poly = sp.Poly(sp.together(third(u2, q)).as_numer_denom()[0], r)
    equations = list(poly.all_coeffs())
    solution = sp.solve(equations, [q0, q1, q2], dict=True)
    require(solution == [{q0: 0, q1: 0, q2: 0}], "spin2 K_U rational kernel")

    potential1 = f * ll / r**2
    maxwell_k = sp.factor(third(w**2 - potential1, q0))
    require(
        maxwell_k == 4 * ll * q0 * (r - 3) * (r - 2) / r**5,
        "Maxwell K_U constant kernel",
    )

    # Recompute the specialization-safe nonsplitting minors.
    m = sp.Matrix(
        [
            [0, -4 * w**4, 0],
            [-8 * w**4, 8 * w**4, 24 * w**2],
            [16 * w**4, 42 * w**2, -156 * w**2],
            [48 * w**2, -224 * w**2, 312 * w**2],
            [-208 * w**2, 364 * w**2, -192 * w**2],
            [224 * w**2, -168 * w**2, 0],
        ]
    )
    rhs = sp.Matrix(
        [
            0,
            -2 * sp.I * (5 * w - 6 * sp.I),
            sp.I * (35 * w - 78 * sp.I),
            -6 * sp.I * (5 * w - 26 * sp.I),
            96,
            0,
        ]
    )
    coefficient_minor = sp.factor(m.extract((0, 1, 2), range(3)).det())
    augmented_minor = sp.factor(
        m.row_join(rhs).extract((0, 1, 2, 5), range(4)).det()
    )
    require(coefficient_minor == 3456 * w**10, "coefficient rank minor")
    require(augmented_minor == -645120 * sp.I * w**9, "augmented rank minor")
    refinement = data.get("positive_real_nonsplitting_refinement", {})
    try:
        stored_coefficient_minor = sp.sympify(
            refinement.get("coefficient_minor_rows_0_1_2", ""),
            locals={"omega": w},
        )
        stored_augmented_minor = sp.sympify(
            refinement.get("augmented_minor_rows_0_1_2_5", ""),
            locals={"omega": w},
        )
    except (sp.SympifyError, TypeError):
        stored_coefficient_minor = sp.nan
        stored_augmented_minor = sp.nan
    require(
        sp.simplify(stored_coefficient_minor - coefficient_minor) == 0,
        "stored coefficient minor mutated",
    )
    require(
        sp.simplify(stored_augmented_minor - augmented_minor) == 0,
        "stored augmented minor mutated",
    )

    # Direct involution terminal algebra.
    scalar, nilpotent = sp.symbols("scalar nilpotent")
    nmat = sp.Matrix([[0, nilpotent], [0, 0]])
    cmat = scalar * sp.eye(2) + nmat
    involutions = sp.solve(list(cmat**2 - sp.eye(2)), [scalar, nilpotent], dict=True)
    require(
        involutions == [
            {nilpotent: 0, scalar: -1},
            {nilpotent: 0, scalar: 1},
        ],
        "involution terminal algebra",
    )

    if check_imports:
        for item in data.get("imports", {}).values():
            path = ROOT / item["path"]
            require(path.exists(), f"missing import: {path}")
            if path.exists():
                require(digest(path) == item["sha256"], f"import hash: {path}")
        cocycle = json.loads(
            (
                ROOT
                / data["imports"]["generic_projective_cocycle"]["path"]
            ).read_text()
        )
        require(
            cocycle["claim_flags"]["generic_rational_cocycle_nontrivial"],
            "imported cocycle premise",
        )
        require(
            cocycle["finite_specialization_corollary"][
                "maximal_minor_gcd_exactness"
            ]
            == "384*omega**6",
            "imported coefficient-minor audit changed",
        )

    return errors


def main() -> None:
    data = json.loads((HERE / "certificate.json").read_text())
    errors = verify_data(data)
    if errors:
        raise SystemExit("\n".join(errors))
    print("EXACT_RW_MAXWELL_SIMPLICITY_ENDOMORPHISMS_VERIFIED")


if __name__ == "__main__":
    main()
