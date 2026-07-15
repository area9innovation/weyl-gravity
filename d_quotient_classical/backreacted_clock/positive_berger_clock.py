#!/usr/bin/env python3
"""Certify a positive rotating conformal clock on a Berger cylinder.

The metric is the static product of time with a biaxially squashed three-
sphere,

    g = -dt^2 + a^2(sigma_1^2+sigma_2^2) + c^2 sigma_3^2,

where the left-invariant one-forms obey the SU(2) Maurer--Cartan equations.
Two standard-sign conformal scalars form a complex field of constant modulus
and rotating phase.  The phase is an everywhere-timelike compact clock, while
its stationary stress sources the nonzero Bach tensor.

For q=c^2/a^2 in

    (5-sqrt(21))/2 < q < 1/4,

the exact source equations admit positive Weyl coupling, positive scalar
amplitude, real nonzero frequency, and positive quartic coupling.  The scalar
stress satisfies the dominant energy inequalities.  This is an exact healthy
clock *background* theorem; a covariant phase-space charge verdict and the
all-row BV contraction remain separate gates.
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
    / "POSITIVE_BERGER_CLOCK_BACKGROUND.json"
)
REPORT_PATH = (
    ROOT
    / "d_quotient_classical"
    / "reports"
    / "positive-berger-clock-background.md"
)
SCHEMA_PATH = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "positive-berger-clock-background-v1.schema.json"
)


def _berger_geometry(a: sp.Symbol, c: sp.Symbol) -> tuple[sp.Matrix, sp.Expr, sp.Matrix]:
    """Derive Ricci, scalar curvature, and Bach tensors in an orthonormal frame."""

    n = 4
    eta = sp.diag(-1, 1, 1, 1)
    structure = [
        [[sp.S(0) for _ in range(n)] for _ in range(n)] for _ in range(n)
    ]
    # [e1,e2]=(c/a^2)e3, [e2,e3]=(1/c)e1, [e3,e1]=(1/c)e2.
    for first, second, target, value in (
        (1, 2, 3, c / a**2),
        (2, 3, 1, 1 / c),
        (3, 1, 2, 1 / c),
    ):
        structure[first][second][target] = value
        structure[second][first][target] = -value

    connection = [
        [[sp.S(0) for _ in range(n)] for _ in range(n)] for _ in range(n)
    ]
    for derivative in range(n):
        for vector in range(n):
            for lowered_target in range(n):
                gamma_lower = sp.Rational(1, 2) * (
                    sum(
                        eta[lowered_target, m]
                        * structure[derivative][vector][m]
                        for m in range(n)
                    )
                    - sum(
                        eta[derivative, m]
                        * structure[vector][lowered_target][m]
                        for m in range(n)
                    )
                    + sum(
                        eta[vector, m]
                        * structure[lowered_target][derivative][m]
                        for m in range(n)
                    )
                )
                for target in range(n):
                    connection[target][derivative][vector] += (
                        eta[target, lowered_target] * gamma_lower
                    )

    riemann = [
        [
            [[sp.S(0) for _ in range(n)] for _ in range(n)]
            for _ in range(n)
        ]
        for _ in range(n)
    ]
    for target in range(n):
        for vector in range(n):
            for first in range(n):
                for second in range(n):
                    riemann[target][vector][first][second] = sp.simplify(
                        sum(
                            connection[mid][second][vector]
                            * connection[target][first][mid]
                            - connection[mid][first][vector]
                            * connection[target][second][mid]
                            - structure[first][second][mid]
                            * connection[target][mid][vector]
                            for mid in range(n)
                        )
                    )

    ricci = sp.zeros(n)
    for first in range(n):
        for second in range(n):
            ricci[first, second] = sp.simplify(
                sum(riemann[index][first][index][second] for index in range(n))
            )
    scalar = sp.simplify(
        sum(eta[i, j] * ricci[i, j] for i in range(n) for j in range(n))
    )
    schouten = sp.simplify((ricci - scalar * eta / 6) / 2)

    weyl = [
        [
            [[sp.S(0) for _ in range(n)] for _ in range(n)]
            for _ in range(n)
        ]
        for _ in range(n)
    ]
    for first in range(n):
        for second in range(n):
            for third in range(n):
                for fourth in range(n):
                    riemann_lower = sum(
                        eta[first, target]
                        * riemann[target][second][third][fourth]
                        for target in range(n)
                    )
                    weyl[first][second][third][fourth] = sp.simplify(
                        riemann_lower
                        - (
                            eta[first, third] * schouten[fourth, second]
                            - eta[first, fourth] * schouten[third, second]
                            - eta[second, third] * schouten[fourth, first]
                            + eta[second, fourth] * schouten[third, first]
                        )
                    )

    derivative_schouten = [
        [[sp.S(0) for _ in range(n)] for _ in range(n)] for _ in range(n)
    ]
    for derivative in range(n):
        for first in range(n):
            for second in range(n):
                derivative_schouten[derivative][first][second] = sp.simplify(
                    -sum(
                        connection[index][derivative][first]
                        * schouten[index, second]
                        + connection[index][derivative][second]
                        * schouten[first, index]
                        for index in range(n)
                    )
                )

    second_schouten = [
        [
            [[sp.S(0) for _ in range(n)] for _ in range(n)]
            for _ in range(n)
        ]
        for _ in range(n)
    ]
    for outer in range(n):
        for inner in range(n):
            for first in range(n):
                for second in range(n):
                    second_schouten[outer][inner][first][second] = sp.simplify(
                        -sum(
                            connection[index][outer][inner]
                            * derivative_schouten[index][first][second]
                            + connection[index][outer][first]
                            * derivative_schouten[inner][index][second]
                            + connection[index][outer][second]
                            * derivative_schouten[inner][first][index]
                            for index in range(n)
                        )
                    )

    schouten_up = sp.simplify(eta * schouten * eta)
    bach = sp.zeros(n)
    for first in range(n):
        for second in range(n):
            laplacian = sum(
                eta[outer, inner]
                * second_schouten[outer][inner][first][second]
                for outer in range(n)
                for inner in range(n)
            )
            mixed = sum(
                eta[outer, inner]
                * second_schouten[outer][first][second][inner]
                for outer in range(n)
                for inner in range(n)
            )
            curvature = sum(
                schouten_up[inner, outer]
                * weyl[first][inner][second][outer]
                for inner in range(n)
                for outer in range(n)
            )
            bach[first, second] = sp.factor(laplacian - mixed + curvature)

    if sp.simplify(sum(eta[i, j] * bach[i, j] for i in range(n) for j in range(n))) != 0:
        raise AssertionError("derived Berger Bach tensor is not traceless")
    if bach != bach.T:
        raise AssertionError("derived Berger Bach tensor is not symmetric")
    return ricci, sp.factor(scalar), bach


@dataclass(frozen=True)
class PositiveBergerClockBackground:
    """Exact Bach-sourced positive-clock background certificate."""

    payload: dict[str, Any]

    @classmethod
    def build(cls) -> "PositiveBergerClockBackground":
        a, c = sp.symbols("a c", positive=True, real=True)
        q, alpha_b = sp.symbols("q alpha_B", positive=True, real=True)
        ricci, scalar, bach = _berger_geometry(a, c)

        expected_ricci = sp.diag(
            0,
            (2 * a**2 - c**2) / (2 * a**4),
            (2 * a**2 - c**2) / (2 * a**4),
            c**2 / (2 * a**4),
        )
        expected_scalar = (4 * a**2 - c**2) / (2 * a**4)
        expected_bach = sp.diag(
            (a**2 - c**2) ** 2 / (6 * a**8),
            (a**2 - c**2) * (a**2 - 3 * c**2) / (6 * a**8),
            (a**2 - c**2) * (a**2 - 3 * c**2) / (6 * a**8),
            (a**2 - c**2) * (5 * c**2 - a**2) / (6 * a**8),
        )
        if sp.simplify(ricci - expected_ricci) != sp.zeros(4):
            raise AssertionError("Berger Ricci tensor drifted")
        if sp.simplify(scalar - expected_scalar) != 0:
            raise AssertionError("Berger scalar curvature drifted")
        if sp.simplify(bach - expected_bach) != sp.zeros(4):
            raise AssertionError("Berger Bach tensor drifted")

        # Dimensionless matter solve.  x=lambda*rho^2*a^2 and q=c^2/a^2.
        x = sp.symbols("x", real=True)
        bach_dimensionless = sp.Matrix(
            [
                (1 - q) ** 2 / 6,
                (1 - q) * (1 - 3 * q) / 6,
                (1 - q) * (5 * q - 1) / 6,
            ]
        )
        stress_dimensionless = sp.Matrix(
            [
                (4 - q + 9 * x) / 12,
                (2 - q + 3 * x) / 12,
                (q + 3 * x) / 12,
            ]
        )
        first_defect = sp.factor(
            bach_dimensionless[1] * stress_dimensionless[0]
            - bach_dimensionless[0] * stress_dimensionless[1]
        )
        second_defect = sp.factor(
            bach_dimensionless[2] * stress_dimensionless[0]
            - bach_dimensionless[0] * stress_dimensionless[2]
        )
        expected_defect = (q - 1) * (
            -q**2 + 12 * q * x + 5 * q - 3 * x - 1
        ) / 36
        if sp.expand(first_defect - expected_defect) != 0:
            raise AssertionError("horizontal Bach-source defect drifted")
        if sp.expand(second_defect + 2 * expected_defect) != 0:
            raise AssertionError("vertical Bach-source defect drifted")

        x_solution = sp.factor((q**2 - 5 * q + 1) / (3 * (4 * q - 1)))
        if sp.simplify(first_defect.subs(x, x_solution)) != 0:
            raise AssertionError("horizontal source matching failed")
        if sp.simplify(second_defect.subs(x, x_solution)) != 0:
            raise AssertionError("vertical source matching failed")
        omega_squared_dimensionless = sp.factor((4 - q) / 12 + x_solution)
        if sp.simplify(
            omega_squared_dimensionless + q / (4 * (4 * q - 1))
        ) != 0:
            raise AssertionError("clock frequency drifted")

        # Put back the scale and solve alpha_B B=T.
        rho_squared = sp.factor(2 * alpha_b * (1 - 4 * q) / a**2)
        quartic = sp.factor(
            -(q**2 - 5 * q + 1)
            / (6 * alpha_b * (1 - 4 * q) ** 2)
        )
        omega_squared = sp.factor(q / (4 * a**2 * (1 - 4 * q)))

        # A rational human-auditable point in the positive interval.
        fixture = {
            q: sp.Rational(9, 40),
            a: 1,
            alpha_b: 5,
        }
        fixture_rho_squared = sp.simplify(rho_squared.subs(fixture))
        fixture_quartic = sp.simplify(quartic.subs(fixture))
        fixture_omega_squared = sp.simplify(omega_squared.subs(fixture))
        if fixture_rho_squared != 1:
            raise AssertionError("rational fixture amplitude drifted")
        if fixture_quartic != sp.Rational(119, 480):
            raise AssertionError("rational fixture quartic drifted")
        if fixture_omega_squared != sp.Rational(9, 16):
            raise AssertionError("rational fixture frequency drifted")

        # The three principal tensors match coefficientwise at the fixture.
        q_value = fixture[q]
        bach_fixture = sp.Matrix(
            [entry.subs(q, q_value) for entry in bach_dimensionless]
        )
        stress_fixture = sp.Matrix(
            [entry.subs({q: q_value, x: fixture_quartic}) for entry in stress_dimensionless]
        )
        if sp.simplify(5 * bach_fixture - stress_fixture) != sp.zeros(3, 1):
            raise AssertionError("rational Bach-source fixture failed")

        # Raw Diff x Weyl incidence for T1=rho cos(omega t),
        # T2=rho sin(omega t) has determinant rho^2 omega.
        rho, omega, time = sp.symbols("rho omega t", positive=True, real=True)
        t1 = rho * sp.cos(omega * time)
        t2 = rho * sp.sin(omega * time)
        incidence = sp.Matrix(
            [
                [sp.diff(t1, time), -t1],
                [sp.diff(t2, time), -t2],
            ]
        )
        if sp.trigsimp(incidence.det() - rho**2 * omega) != 0:
            raise AssertionError("positive clock incidence determinant drifted")

        lower_bound = sp.Rational(5, 2) - sp.sqrt(21) / 2
        if sp.ask(sp.Q.positive(lower_bound - sp.Rational(1, 5))) is not True:
            raise AssertionError("positive-pressure lower bound was not proved")
        if sp.ask(sp.Q.positive(sp.Rational(1, 4) - lower_bound)) is not True:
            raise AssertionError("positive Berger interval was not proved nonempty")

        # All energy inequalities have the same positive factor
        # rho^2/[12 a^2(1-4q)] on the certified interval.  The remaining
        # numerator factorizations make positivity and the dominant-energy
        # inequalities transparent and exact.
        energy_numerator = sp.factor((1 - q) ** 2)
        horizontal_pressure_numerator = sp.factor((1 - q) * (1 - 3 * q))
        vertical_pressure_numerator = sp.factor((1 - q) * (5 * q - 1))
        energy_minus_horizontal = sp.factor(
            energy_numerator - horizontal_pressure_numerator
        )
        energy_minus_vertical = sp.factor(
            energy_numerator - vertical_pressure_numerator
        )
        if sp.simplify(energy_minus_horizontal - 2 * q * (1 - q)) != 0:
            raise AssertionError("horizontal dominant-energy factor drifted")
        if sp.simplify(
            energy_minus_vertical - 2 * (1 - q) * (1 - 3 * q)
        ) != 0:
            raise AssertionError("vertical dominant-energy factor drifted")
        payload: dict[str, Any] = {
            "schema": "pure-weyl-positive-berger-clock-background-v1",
            "result_id": "POSITIVE_BERGER_CLOCK_BACKGROUND",
            "setting_id": "compact_positive_berger_clock",
            "generator_id": "D_compact",
            "phase_space_id": "positive_rotating_scalar_berger_background",
            "claim_status": "CERTIFIED_EXACT_BACKGROUND",
            "scientific_verdict": None,
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            "conventions": {
                "metric_signature": "(-,+,+,+)",
                "metric": "g=-dt^2+a^2(sigma_1^2+sigma_2^2)+c^2 sigma_3^2",
                "maurer_cartan": "[e1,e2]=(c/a^2)e3, [e2,e3]=(1/c)e1, [e3,e1]=(1/c)e2",
                "squashing": "q=c^2/a^2",
                "matter": "two real standard-sign conformal scalars with O(2)-invariant potential lambda(T_1^2+T_2^2)^2/4",
                "metric_equation": "alpha_B B_mn=T_mn with alpha_B>0",
                "common_action_convention": "alpha_B=4 alpha_g for S_W=-alpha_g integral C^2, subject to the repository's overall Bach sign convention",
            },
            "berger_geometry": {
                "scalar_curvature": "R=(4a^2-c^2)/(2a^4)",
                "ricci_orthonormal": [
                    "0",
                    "(2a^2-c^2)/(2a^4)",
                    "(2a^2-c^2)/(2a^4)",
                    "c^2/(2a^4)",
                ],
                "bach_orthonormal": [
                    "(a^2-c^2)^2/(6a^8)",
                    "(a^2-c^2)(a^2-3c^2)/(6a^8)",
                    "(a^2-c^2)(a^2-3c^2)/(6a^8)",
                    "(a^2-c^2)(5c^2-a^2)/(6a^8)",
                ],
                "bach_trace": "ZERO",
                "bach_symmetric": True,
                "nonconformally_flat_on_solution_interval": True,
            },
            "clock_ansatz": {
                "fields": ["T_1=rho*cos(omega*t)", "T_2=rho*sin(omega*t)"],
                "modulus": "T_1^2+T_2^2=rho^2>0",
                "phase": "theta=atan2(T_2,T_1)=omega*t mod 2pi",
                "phase_gradient_norm": "(nabla theta)^2=-omega^2<0",
                "target_metric": "d rho^2+rho^2 d theta^2",
                "phase_kinetic_coefficient": "+rho^2",
                "diff_weyl_incidence_determinant": "rho^2*omega",
                "incidence_full_rank": True,
                "separate_weyl_gauge": "log rho",
            },
            "exact_solution_family": {
                "parameter_interval": "(5-sqrt(21))/2 < q < 1/4",
                "interval_lower_approx": float(lower_bound.evalf()),
                "interval_exact_checks": [
                    "(5-sqrt(21))/2 > 1/5",
                    "1/4-(5-sqrt(21))/2 > 0",
                ],
                "rho_squared": "2 alpha_B(1-4q)/a^2",
                "omega_squared": "q/[4a^2(1-4q)]",
                "lambda": "-(q^2-5q+1)/[6 alpha_B(1-4q)^2]",
                "scalar_equations": "PASS",
                "metric_equations": "alpha_B B=T componentwise PASS",
                "solution_interval_nonempty": True,
                "rho_squared_positive": True,
                "omega_squared_positive": True,
                "lambda_positive": True,
            },
            "energy_health": {
                "energy_density": "rho^2(1-q)^2/[12a^2(1-4q)]",
                "horizontal_pressure": "rho^2(1-q)(1-3q)/[12a^2(1-4q)]",
                "vertical_pressure": "rho^2(1-q)(5q-1)/[12a^2(1-4q)]",
                "energy_minus_horizontal_pressure": "rho^2*2q(1-q)/[12a^2(1-4q)]",
                "energy_minus_vertical_pressure": "rho^2*2(1-q)(1-3q)/[12a^2(1-4q)]",
                "positivity_factors": [
                    "q>q_0>1/5",
                    "q<1/4<1/3<1",
                    "rho^2>0",
                    "a^2>0",
                    "1-4q>0",
                ],
                "energy_density_positive": True,
                "all_principal_pressures_positive": True,
                "dominant_energy_condition": True,
                "quartic_potential_bounded_below": True,
                "scalar_target_positive_definite": True,
            },
            "rational_fixture": {
                "a": "1",
                "q": "9/40",
                "c_squared": "9/40",
                "alpha_B": "5",
                "rho_squared": "1",
                "omega": "3/4",
                "lambda": "119/480",
                "scalar_equation": "PASS",
                "three_independent_metric_equations": "PASS",
            },
            "gate_result": {
                "gate": "POSITIVE_ENERGY_NONCONFORMALLY_FLAT_BACH_SOURCED_CLOCK",
                "status": "PASSED_BY_EXACT_BERGER_BACKGROUND",
                "next_gate": "FULL_BERGER_CLOCK_CHARGE_AND_BV_AUDIT",
                "next_gate_status": "OPEN",
            },
            "flags": {
                "exact_backreacted_background_exists": True,
                "positive_standard_scalar_kinetic": True,
                "bounded_below_quartic": True,
                "everywhere_timelike_phase_clock": True,
                "full_diff_weyl_incidence": True,
                "covariant_phase_space_D_charge_computed": False,
                "support_local_all_row_bv_retract_constructed": False,
                "linear_and_nonlinear_stability_proved": False,
                "quantum_admissibility_proved": False,
            },
            "not_established": [
                "the normalized covariant D charge and presymplectic reduction on perturbations of the Berger branch",
                "a support-local all-row BV deformation retract using the clock",
                "causal Green homotopies for the matter-coupled squashed background",
                "linear, nonlinear, or quantum stability",
                "a universal D_GAUGE verdict",
            ],
            "claim_boundary": "This certificate proves an exact open family of smooth non-conformally-flat Bach-sourced backgrounds with a positive-energy rotating conformal-scalar phase clock and a positive quartic potential. It does not yet prove that D is gauge on the full perturbative covariant phase space; that requires the separate charge and all-row BV audit.",
        }
        result = cls(payload=payload)
        result.verify()
        return result

    def verify(self) -> None:
        p = self.payload
        required = {
            "schema", "result_id", "setting_id", "generator_id",
            "phase_space_id", "claim_status", "scientific_verdict",
            "dependency_tags", "conventions", "berger_geometry",
            "clock_ansatz", "exact_solution_family", "energy_health",
            "rational_fixture", "gate_result", "flags", "not_established",
            "claim_boundary",
        }
        if set(p) != required:
            raise AssertionError("positive Berger certificate key set drifted")
        if p["claim_status"] != "CERTIFIED_EXACT_BACKGROUND":
            raise AssertionError("Berger background theorem was weakened")
        if p["scientific_verdict"] is not None:
            raise AssertionError("background existence was promoted to a D verdict")
        if p["gate_result"]["status"] != "PASSED_BY_EXACT_BERGER_BACKGROUND":
            raise AssertionError("positive backreaction gate was lost")
        if p["gate_result"]["next_gate_status"] != "OPEN":
            raise AssertionError("charge/BV audit was silently promoted")
        flags = p["flags"]
        for key in (
            "exact_backreacted_background_exists",
            "positive_standard_scalar_kinetic",
            "bounded_below_quartic",
            "everywhere_timelike_phase_clock",
            "full_diff_weyl_incidence",
        ):
            if flags.get(key) is not True:
                raise AssertionError(f"proved Berger flag dropped: {key}")
        for key in (
            "covariant_phase_space_D_charge_computed",
            "support_local_all_row_bv_retract_constructed",
            "linear_and_nonlinear_stability_proved",
            "quantum_admissibility_proved",
        ):
            if flags.get(key) is not False:
                raise AssertionError(f"open Berger flag promoted: {key}")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Positive Berger-sphere clock background

## Outcome

There is an exact open family of smooth, compact, non-conformally-flat
backgrounds carrying a positive rotating conformal-scalar clock.

Take

\[
g=-dt^2+a^2(\sigma_1^2+\sigma_2^2)+c^2\sigma_3^2,
\qquad q=\frac{c^2}{a^2},
\]

on \(\mathbb R\times S^3\), and two standard-sign real conformal scalars

\[
T_1=\rho\cos(\omega t),
\qquad
T_2=\rho\sin(\omega t).
\]

Their target metric is positive,

\[
dT_1^2+dT_2^2=d\rho^2+\rho^2d\theta^2,
\]

and the phase \(\theta=\omega t\) has everywhere timelike gradient.  The raw
temporal-diffeomorphism/Weyl incidence determinant is

\[
\det M=\rho^2\omega\ne0.
\]

## Exact Bach-source match

In the orthonormal Berger frame the nonzero independent Bach components are

\[
\begin{aligned}
B_{00}&=\frac{(a^2-c^2)^2}{6a^8},\\
B_{11}=B_{22}&=\frac{(a^2-c^2)(a^2-3c^2)}{6a^8},\\
B_{33}&=\frac{(a^2-c^2)(5c^2-a^2)}{6a^8}.
\end{aligned}
\]

For the field equation \(\alpha_BB_{\mu\nu}=T_{\mu\nu}\), the complete
positive branch is

\[
\frac{5-\sqrt{21}}2<q<\frac14,
\]

\[
\rho^2=\frac{2\alpha_B(1-4q)}{a^2},
\qquad
\omega^2=\frac{q}{4a^2(1-4q)},
\]

\[
\lambda=-\frac{q^2-5q+1}{6\alpha_B(1-4q)^2}>0.
\]

The scalar equations and all three independent metric equations vanish
coefficientwise.

## Health of the clock matter

Throughout the interval, the scalar kinetic metric is positive and the
quartic potential is bounded below.  The energy density and principal
pressures are

\[
\varepsilon=\frac{\rho^2(1-q)^2}{12a^2(1-4q)},
\]

\[
p_h=\frac{\rho^2(1-q)(1-3q)}{12a^2(1-4q)},
\qquad
p_v=\frac{\rho^2(1-q)(5q-1)}{12a^2(1-4q)}.
\]

They are positive and obey \(\varepsilon\geq p_h,p_v\).

## Rational fixture

A compact exact representative is

\[
a=1,\quad q=\frac9{40},\quad \alpha_B=5,\quad \rho=1,
\quad \omega=\frac34,\quad \lambda=\frac{119}{480}.
\]

It satisfies the scalar equation and all independent Bach-source equations
over the rationals.

## Remaining gate

This is the first standard-sign, bounded-potential clock background to pass
the coupled field equations.  It is not yet a charge theorem.  The next gate
is

```text
FULL_BERGER_CLOCK_CHARGE_AND_BV_AUDIT
```

which must derive the normalized covariant \(D\) charge, the perturbative
phase space, the support-local all-row BV contraction, and causal propagation.
No `D_GAUGE` verdict is assigned before that audit.
"""


def _write(result: PositiveBergerClockBackground) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: PositiveBergerClockBackground) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError(f"stale certificate: {CERTIFICATE_PATH}")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError(f"stale report: {REPORT_PATH}")
    if not SCHEMA_PATH.is_file():
        raise AssertionError(f"missing schema: {SCHEMA_PATH}")


def _guards(result: PositiveBergerClockBackground) -> None:
    mutations = (
        ("premature D verdict", ("scientific_verdict",), "D_GAUGE"),
        ("erase background", ("flags", "exact_backreacted_background_exists"), False),
        ("erase positivity", ("flags", "bounded_below_quartic"), False),
        ("erase clock", ("flags", "everywhere_timelike_phase_clock"), False),
        ("promote charge", ("flags", "covariant_phase_space_D_charge_computed"), True),
        ("promote BV", ("flags", "support_local_all_row_bv_retract_constructed"), True),
        ("promote stability", ("flags", "linear_and_nonlinear_stability_proved"), True),
        ("promote next gate", ("gate_result", "next_gate_status"), "PASSED"),
    )
    passed = 0
    for label, path, value in mutations:
        payload = deepcopy(result.payload)
        target: Any = payload
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            PositiveBergerClockBackground(payload=payload).verify()
        except AssertionError:
            passed += 1
        else:
            raise AssertionError(f"mutation guard failed: {label}")
    print(f"mutation guards: {passed}/{len(mutations)} PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = PositiveBergerClockBackground.build()
    if args.write:
        _write(result)
    if args.check:
        _check(result)
    if args.guards:
        _guards(result)
    if not (args.write or args.check or args.guards):
        print(result.certificate_text(), end="")
    else:
        print(f"{CERTIFICATE_PATH} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
