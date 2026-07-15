#!/usr/bin/env python3
"""Close the fixed-coupling delta-Q gate for the positive Berger clock.

The calculation keeps the lapse until after variation and uses conformal
gauge only for the common spatial scale.  On

    ds^2 = -N(t)^2 dt^2 + sigma_1^2 + sigma_2^2 + c(t)^2 sigma_3^2,
    (T_1,T_2) = rho(t) (cos(theta(t)), sin(theta(t))),

the exact reduced Weyl-plus-matter action gives a lapse equation.  Its
linearization on the positive Berger branch is

    delta E_N = -(alpha_B q^(3/2)/2) delta Q_R / Q_R.

Consequently every fixed-coupling constraint-satisfying homogeneous tangent
has delta Q_R=0.  Compact SU(2)_L x U(1)_R averaging upgrades this to all
smooth spatial perturbations: averaging preserves the linearized equations
and the invariant integrated charge variation.  Thus a hypothetical charged
tangent would produce a forbidden charged homogeneous tangent.

The result is a scoped classical charge theorem.  It does not construct the
support-local all-row BV contraction or prove nonlinear clock stability.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_PATH = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "BERGER_FIXED_COUPLING_DELTA_CHARGE.json"
)
REPORT_PATH = (
    ROOT
    / "d_quotient_classical"
    / "reports"
    / "berger-fixed-coupling-delta-charge.md"
)
SCHEMA_PATH = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "berger-fixed-coupling-delta-charge-v1.schema.json"
)


def _reduced_action_data() -> dict[str, Any]:
    """Derive the exact reduced action and its linearized lapse equation."""

    c0, c1, c2, c3, c4 = sp.symbols("c0:5", positive=True)
    n0, n1, n2, n3 = sp.symbols("n0:4", positive=True)
    r0, r1, r2, r3 = sp.symbols("r0:4", positive=True)
    theta0, theta1, theta2, theta3 = sp.symbols("theta0:4", real=True)
    alpha_b, quartic, q = sp.symbols("alpha_B lambda q", positive=True)

    variables = [
        c0, c1, c2, c3,
        n0, n1, n2,
        r0, r1, r2,
        theta0, theta1, theta2,
    ]
    successors = [
        c1, c2, c3, c4,
        n1, n2, n3,
        r1, r2, r3,
        theta1, theta2, theta3,
    ]

    def total_derivative(expression: sp.Expr) -> sp.Expr:
        return sp.expand(
            sum(
                sp.diff(expression, variable) * successor
                for variable, successor in zip(variables, successors)
            )
        )

    # These are obtained from the orthonormal non-holonomic frame with
    # [e_1,e_2]=c e_3, [e_2,e_3]=c^{-1}e_1,
    # [e_3,e_1]=c^{-1}e_2 and [e_0,e_3]=-(dot c/Nc)e_3.
    scalar_curvature = sp.factor(
        -(
            n0**3 * c0**3
            - 4 * n0**3 * c0
            - 4 * n0 * c2
            + 4 * n1 * c1
        )
        / (2 * n0**3 * c0)
    )
    left = (
        n0**3 * c0**3
        - n0**3 * c0
        - 3 * n0**2 * c0 * c1
        - n0 * c2
        + n1 * c1
    )
    right = (
        n0**3 * c0**3
        - n0**3 * c0
        + 3 * n0**2 * c0 * c1
        - n0 * c2
        + n1 * c1
    )
    weyl_squared = sp.factor(4 * left * right / (3 * n0**6 * c0**2))

    if sp.factor(
        scalar_curvature.subs({c1: 0, c2: 0, n0: 1, n1: 0})
        - (4 - c0**2) / 2
    ) != 0:
        raise AssertionError("time-dependent scalar curvature has wrong static limit")
    if sp.factor(
        weyl_squared.subs({c1: 0, c2: 0, n0: 1, n1: 0})
        - 4 * (1 - c0**2) ** 2 / 3
    ) != 0:
        raise AssertionError("time-dependent Weyl square has wrong static limit")

    reduced_lagrangian = sp.factor(
        n0
        * c0
        * (
            alpha_b * weyl_squared / 8
            + (r1**2 + r0**2 * theta1**2) / (2 * n0**2)
            - scalar_curvature * r0**2 / 12
            - quartic * r0**4 / 4
        )
    )

    e_c = sp.expand(
        sp.diff(reduced_lagrangian, c0)
        - total_derivative(sp.diff(reduced_lagrangian, c1))
        + total_derivative(total_derivative(sp.diff(reduced_lagrangian, c2)))
    )
    e_n = sp.expand(
        sp.diff(reduced_lagrangian, n0)
        - total_derivative(sp.diff(reduced_lagrangian, n1))
    )
    e_rho = sp.expand(
        sp.diff(reduced_lagrangian, r0)
        - total_derivative(sp.diff(reduced_lagrangian, r1))
    )
    e_theta = sp.expand(-total_derivative(sp.diff(reduced_lagrangian, theta1)))

    rho_bar = sp.sqrt(2 * alpha_b * (1 - 4 * q))
    omega_bar = sp.sqrt(q / (4 * (1 - 4 * q)))
    lambda_bar = -(
        q**2 - 5 * q + 1
    ) / (6 * alpha_b * (1 - 4 * q) ** 2)
    branch = {
        c0: sp.sqrt(q),
        c1: 0,
        c2: 0,
        c3: 0,
        c4: 0,
        n0: 1,
        n1: 0,
        n2: 0,
        n3: 0,
        r0: rho_bar,
        r1: 0,
        r2: 0,
        r3: 0,
        theta0: 0,
        theta1: omega_bar,
        theta2: 0,
        theta3: 0,
        quartic: lambda_bar,
    }
    if any(sp.simplify(equation.subs(branch)) != 0 for equation in (e_c, e_n, e_rho, e_theta)):
        raise AssertionError("positive Berger branch does not solve the reduced equations")

    delta_c, delta_n, delta_rho, delta_omega = sp.symbols(
        "delta_c delta_N delta_rho delta_omega", real=True
    )
    delta_e_n = sp.factor(
        sp.diff(e_n, c0).subs(branch) * delta_c
        + sp.diff(e_n, n0).subs(branch) * delta_n
        + sp.diff(e_n, r0).subs(branch) * delta_rho
        + sp.diff(e_n, theta1).subs(branch) * delta_omega
    )
    relative_delta_qr = sp.factor(
        delta_c / sp.sqrt(q)
        + 2 * delta_rho / rho_bar
        + delta_omega / omega_bar
        - delta_n
    )
    proportionality = sp.factor(alpha_b * q ** sp.Rational(3, 2) / 2)
    if sp.simplify(delta_e_n + proportionality * relative_delta_qr) != 0:
        raise AssertionError("lapse constraint is not the relative charge variation")

    fixture = {
        q: sp.Rational(9, 40),
        alpha_b: 5,
    }
    fixture_lambda = sp.simplify(lambda_bar.subs(fixture))
    fixture_rho = sp.simplify(rho_bar.subs(fixture))
    fixture_omega = sp.simplify(omega_bar.subs(fixture))
    fixture_coefficient = sp.simplify(proportionality.subs(fixture))
    if (
        fixture_lambda != sp.Rational(119, 480)
        or fixture_rho != 1
        or fixture_omega != sp.Rational(3, 4)
        or fixture_coefficient != 27 * sp.sqrt(10) / 320
    ):
        raise AssertionError("rational fixed-coupling fixture drifted")

    # At the fixture the coefficientwise lapse row is independently readable.
    lapse_coefficients = {
        "delta_c": sp.factor(sp.diff(e_n, c0).subs(branch).subs(fixture)),
        "delta_N": sp.factor(sp.diff(e_n, n0).subs(branch).subs(fixture)),
        "delta_rho": sp.factor(sp.diff(e_n, r0).subs(branch).subs(fixture)),
        "delta_omega": sp.factor(sp.diff(e_n, theta1).subs(branch).subs(fixture)),
    }
    expected_lapse_coefficients = {
        "delta_c": -sp.Rational(9, 16),
        "delta_N": 27 * sp.sqrt(10) / 320,
        "delta_rho": -27 * sp.sqrt(10) / 160,
        "delta_omega": -9 * sp.sqrt(10) / 80,
    }
    if lapse_coefficients != expected_lapse_coefficients:
        raise AssertionError("fixture lapse row drifted")

    return {
        "scalar_curvature": scalar_curvature,
        "weyl_squared": weyl_squared,
        "reduced_lagrangian": reduced_lagrangian,
        "delta_lapse_equation": delta_e_n,
        "relative_delta_charge": relative_delta_qr,
        "proportionality": proportionality,
        "fixture_coefficient": fixture_coefficient,
        "lapse_coefficients": lapse_coefficients,
    }


@dataclass(frozen=True)
class BergerFixedCouplingDeltaCharge:
    """Exact certificate for the fixed-coupling Berger delta-charge gate."""

    payload: dict[str, Any]

    @classmethod
    def build(cls) -> "BergerFixedCouplingDeltaCharge":
        data = _reduced_action_data()
        payload: dict[str, Any] = {
            "schema": "pure-weyl-berger-fixed-coupling-delta-charge-v1",
            "result_id": "BERGER_FIXED_COUPLING_DELTA_CHARGE",
            "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
            "generator_id": "D_compact",
            "phase_space_id": "positive_berger_fixed_coupling_linearized_solutions",
            "claim_status": "CERTIFIED",
            "scientific_verdict": "D_GAUGE",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            "conventions": {
                "metric_signature": "(-,+,+,+)",
                "conformal_gauge": "a(t)=1; the removed common scale is pure Weyl gauge and Q_R is scale independent",
                "metric": "ds^2=-N(t)^2 dt^2+sigma_1^2+sigma_2^2+c(t)^2 sigma_3^2",
                "matter": "(T_1,T_2)=rho(t)(cos(theta(t)),sin(theta(t)))",
                "action": "S/(16 pi^2)=int dt N c{alpha_B C^2/8+(dot rho^2+rho^2 dot theta^2)/(2N^2)-R rho^2/12-lambda rho^4/4}",
                "couplings_held_fixed": ["alpha_B", "lambda"],
                "charge": "Q_R=16 pi^2 c rho^2 dot(theta)/N in conformal gauge",
            },
            "time_dependent_geometry": {
                "scalar_curvature": str(data["scalar_curvature"]),
                "weyl_squared": str(data["weyl_squared"]),
                "static_limits_verified": True,
                "reduced_action_derived_before_lapse_gauge_fixing": True,
                "metric_derivative_order": 2,
            },
            "branch": {
                "interval": "(5-sqrt(21))/2 < q < 1/4",
                "c": "sqrt(q)",
                "rho": "sqrt(2 alpha_B (1-4q))",
                "omega": "sqrt(q/[4(1-4q)])",
                "lambda": "-(q^2-5q+1)/[6 alpha_B (1-4q)^2]",
                "background_reduced_equations_zero": True,
            },
            "linearized_lapse_constraint": {
                "relative_charge_variation": "delta Q_R/Q_R=delta c/sqrt(q)+2 delta rho/rho+delta omega/omega-delta N",
                "identity": "delta E_N=-(alpha_B q^(3/2)/2)(delta Q_R/Q_R)",
                "coefficient_nonzero_on_branch": True,
                "fixed_coupling_consequence": "delta Q_R=0 for every homogeneous constraint-satisfying tangent",
            },
            "rational_fixture": {
                "q": "9/40",
                "alpha_B": "5",
                "lambda": "119/480",
                "c": "3 sqrt(10)/20",
                "rho": "1",
                "omega": "3/4",
                "constraint_identity": "delta E_N=-(27 sqrt(10)/320)(delta Q_R/Q_R)",
                "lapse_row": {
                    key: str(value)
                    for key, value in data["lapse_coefficients"].items()
                },
            },
            "invariant_shift_audit": {
                "possible_shift": "N^3(t) along the U(1)_R Berger fibre",
                "status": "PURE_COORDINATE_GAUGE",
                "reason": "the background metric is U(1)_R invariant and the homogeneous scalars have zero spatial derivative; the shift is removed by a time-dependent U(1)_R coordinate change and does not alter the lapse row or Q_R",
            },
            "full_mode_upgrade": {
                "compact_group": "SU(2)_L x U(1)_R",
                "linearized_operator_equivariant": True,
                "group_average_preserves_fixed_coupling_solutions": True,
                "delta_Q_R_is_invariant_linear_functional": True,
                "argument": "if any smooth allowed tangent had delta Q_R nonzero, compact group averaging would give an allowed homogeneous tangent with the same delta Q_R, contradicting the lapse constraint",
                "conclusion": "delta Q_R=0 on the complete smooth fixed-coupling linearized solution space",
            },
            "presymplectic_conclusion": {
                "imported_identity": "Omega_total(delta,L_D)=omega delta Q_R",
                "result": "Omega_total(delta,L_D)=0 for every allowed fixed-coupling linearized tangent",
                "verdict": "D_GAUGE",
                "scope": "the smooth fixed-coupling linearized covariant phase space about the positive Berger clock background on closed S3",
            },
            "interpretation": {
                "background_charge_nonzero": True,
                "charge_variation_zero": True,
                "statement": "the rotating phase has nonzero clock momentum, but the compact lapse constraint fixes that momentum to first order; it is a relational clock coordinate, not a new freely variable D charge in this phase space",
                "not_a_contradiction": "Q_R itself is nonzero while its pullback differential vanishes on the allowed tangent space",
            },
            "flags": {
                "fixed_coupling_linearized_delta_Q_tangent_exists": False,
                "homogeneous_lapse_constraint_exact": True,
                "full_mode_average_argument_exact": True,
                "total_helical_presymplectic_contraction_zero": True,
                "scoped_D_verdict_promoted": True,
                "support_local_all_row_BV_retract_constructed": False,
                "nonlinear_stability_proved": False,
            },
            "next_gate": "FULL_BERGER_CLOCK_BV_AND_STABILITY_AUDIT",
            "not_established": [
                "a support-local all-row Diff x Weyl clock contraction",
                "causal Green homotopies for the matter-coupled Berger complex",
                "nonlinear stability or global deparametrization",
                "a verdict for different boundaries, couplings, or clock actions",
                "the parked CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT requested by the nonlinear team",
            ],
            "claim_boundary": "At fixed alpha_B and lambda, the exact lapse constraint and compact spatial averaging prove delta Q_R=0 for every smooth linearized solution about the positive Berger clock background. Together with the certified helical current identity this gives D_GAUGE on that declared linearized phase space. The theorem does not supply the all-row BV retract, causal propagation, nonlinear stability, or any boundary or quantum result.",
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        p = self.payload
        required = {
            "schema", "result_id", "setting_id", "generator_id",
            "phase_space_id", "claim_status", "scientific_verdict",
            "dependency_tags", "conventions", "time_dependent_geometry",
            "branch", "linearized_lapse_constraint", "rational_fixture",
            "invariant_shift_audit", "full_mode_upgrade",
            "presymplectic_conclusion", "interpretation", "flags",
            "next_gate", "not_established", "claim_boundary",
        }
        if set(p) != required:
            raise AssertionError("fixed-coupling delta-charge key set drifted")
        if p["scientific_verdict"] != "D_GAUGE":
            raise AssertionError("scoped Berger D verdict drifted")
        if p["linearized_lapse_constraint"]["coefficient_nonzero_on_branch"] is not True:
            raise AssertionError("lapse coefficient lost nondegeneracy")
        if p["flags"]["fixed_coupling_linearized_delta_Q_tangent_exists"] is not False:
            raise AssertionError("forbidden delta-Q tangent was promoted")
        if p["flags"]["support_local_all_row_BV_retract_constructed"] is not False:
            raise AssertionError("all-row BV gate was promoted")
        if p["next_gate"] != "FULL_BERGER_CLOCK_BV_AND_STABILITY_AUDIT":
            raise AssertionError("next gate drifted")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Fixed-coupling Berger delta-charge theorem

The positive Berger background has nonzero internal clock momentum, but that
momentum is not freely variable on its fixed-coupling linearized solution
space.

Keeping the lapse before variation and fixing only the common Weyl scale gives

\[
ds^2=-N(t)^2dt^2+\sigma_1^2+\sigma_2^2+c(t)^2\sigma_3^2,
\qquad
(T_1,T_2)=\rho(t)(\cos\theta,\sin\theta).
\]

The exact reduced action is

\[
\frac{S}{16\pi^2}=\int dt\,Nc\left\{
\frac{\alpha_B}{8}C^2+
\frac{\dot\rho^2+\rho^2\dot\theta^2}{2N^2}
-\frac{R\rho^2}{12}-\frac{\lambda\rho^4}{4}
\right\}.
\]

On the positive branch, with \(\alpha_B\) and \(\lambda\) held fixed, the
linearized lapse equation is

\[
\boxed{
\delta E_N=-\frac{\alpha_Bq^{3/2}}2\frac{\delta Q_R}{Q_R}.
}
\]

The coefficient is nonzero throughout
\((5-\sqrt{21})/2<q<1/4\). Therefore every homogeneous allowed tangent obeys
\(\delta Q_R=0\).

This also excludes an inhomogeneous charged tangent.  The compact spatial
isometry group \(SU(2)_L\times U(1)_R\) preserves the background and the
linearized equations, while \(\delta Q_R\) is an invariant linear functional.
If any smooth solution had nonzero \(\delta Q_R\), its compact group average
would be a homogeneous solution with the same nonzero value, contradicting
the lapse constraint.

Combining this with the previously certified identity

\[
\Omega_{\rm total}(\delta,\mathcal L_D)=\omega\,\delta Q_R
\]

gives

\[
\boxed{
\Omega_{\rm total}(\delta,\mathcal L_D)=0,
\qquad D_{\rm compact}=D_{\rm GAUGE}
}
\]

on the declared smooth fixed-coupling linearized phase space about the
positive Berger background.

There is no contradiction with \(Q_R>0\): the background charge is nonzero,
but its pullback differential vanishes on the allowed tangent space.  The
phase is therefore a genuine rotating clock coordinate whose momentum is
fixed by the compact Hamiltonian constraint, rather than an additional freely
variable residual charge.

This theorem does not construct the support-local all-row BV contraction,
causal Green homotopies, or nonlinear stability.  Those form the next gate,
`FULL_BERGER_CLOCK_BV_AND_STABILITY_AUDIT`.
"""


def _write(result: BergerFixedCouplingDeltaCharge) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: BergerFixedCouplingDeltaCharge) -> None:
    result.verify()
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError("fixed-coupling delta-charge certificate drifted")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError("fixed-coupling delta-charge report drifted")


def _guards(result: BergerFixedCouplingDeltaCharge) -> None:
    mutations = [
        ("promote charged tangent", ("flags", "fixed_coupling_linearized_delta_Q_tangent_exists"), True),
        ("erase D verdict", ("scientific_verdict",), None),
        ("promote all-row BV", ("flags", "support_local_all_row_BV_retract_constructed"), True),
        ("drop lapse nondegeneracy", ("linearized_lapse_constraint", "coefficient_nonzero_on_branch"), False),
        ("skip next gate", ("next_gate",), "FINAL_CLOCK_THEOREM"),
    ]
    for name, path, value in mutations:
        payload = deepcopy(result.payload)
        target: Any = payload
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            BergerFixedCouplingDeltaCharge(payload).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard failed: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerFixedCouplingDeltaCharge.build()
    if args.check:
        _check(result)
    else:
        _write(result)
    if args.guards:
        _guards(result)
    print("BERGER_FIXED_COUPLING_DELTA_CHARGE: PASS")
    print("scientific verdict: D_GAUGE (scoped fixed-coupling linearized phase space)")
    print("next gate: FULL_BERGER_CLOCK_BV_AND_STABILITY_AUDIT")


if __name__ == "__main__":
    main()
