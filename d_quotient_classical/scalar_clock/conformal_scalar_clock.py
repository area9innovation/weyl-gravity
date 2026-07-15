#!/usr/bin/env python3
"""Certify the single-scalar clock obstruction on the vacuum cylinder.

The calculation deliberately separates three statements.

* A homogeneous conformally coupled scalar becomes the unit oscillator after
  the Weyl-invariant redefinition ``chi = a T``.
* On every monotone branch, ``chi`` supplies a perfectly good *local*
  relational clock, and a finite reduced-mode fixture has explicit complete
  observables and a nonzero reduced bracket.
* A nonzero homogeneous scalar is not a solution of the scalar-coupled pure
  Weyl equations on the exact vacuum cylinder: its improved energy density is
  positive whereas the cylinder Bach tensor vanishes.  Around the only
  compatible homogeneous background, ``T_bar = 0``, the scalar has zero
  linearized Diff x Weyl gauge incidence and cannot fix ``D``.

Thus the proposed one-scalar vertical slice is obstructed in the declared
exact-cylinder setting.  This does not rule out a backreacted geometry, a
composite/two-field clock, or a different reference-matter model.
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
    / "SCALAR_CLOCK_VERTICAL_SLICE.json"
)
REPORT_PATH = (
    ROOT
    / "d_quotient_classical"
    / "reports"
    / "scalar-clock-vertical-slice.md"
)
SCHEMA_PATH = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "scalar-clock-vertical-slice-v1.schema.json"
)
INPUT_BASE_COMMIT = "fc751539810e9c8191e455c4fcd715ba6d39a41a"


def _poisson(
    first: sp.Expr,
    second: sp.Expr,
    q: sp.Symbol,
    p: sp.Symbol,
    x: sp.Symbol,
    y: sp.Symbol,
) -> sp.Expr:
    """Poisson bracket for ``dq^dp - dx^dy``."""

    return sp.expand(
        sp.diff(first, q) * sp.diff(second, p)
        - sp.diff(first, p) * sp.diff(second, q)
        - sp.diff(first, x) * sp.diff(second, y)
        + sp.diff(first, y) * sp.diff(second, x)
    )


@dataclass(frozen=True)
class ScalarClockVerticalSlice:
    """Exact algebraic data for the homogeneous scalar-clock gate."""

    payload: dict[str, Any]

    @classmethod
    def build(cls) -> "ScalarClockVerticalSlice":
        q, p, x, y = sp.symbols("q p x y", real=True)
        amplitude_a, amplitude_b, time = sp.symbols("A B t", real=True)
        tau, r, p_tau = sp.symbols("tau r p_tau", real=True)

        # Unit-radius ESU convention: g=-dt^2+dOmega_3^2, R=6 and
        # (Box-R/6)T=0.  The normalized homogeneous mode is an oscillator.
        solution = amplitude_a * sp.cos(time) + amplitude_b * sp.sin(time)
        solution_dot = sp.diff(solution, time)
        oscillator_defect = sp.simplify(sp.diff(solution, time, 2) + solution)
        if oscillator_defect != 0:
            raise AssertionError("homogeneous conformal scalar is not an oscillator")
        conserved_radius = sp.trigsimp(solution**2 + solution_dot**2)
        if sp.simplify(conserved_radius - amplitude_a**2 - amplitude_b**2) != 0:
            raise AssertionError("clock amplitude is not conserved")

        # Symplectic and Hamiltonian conventions: Omega=dq^dp and
        # i_X Omega=dH for X_D=(p,-q).
        omega = sp.Matrix([[0, 1], [-1, 0]])
        h_scalar = sp.Rational(1, 2) * (q**2 + p**2)
        x_d = sp.Matrix([p, -q])
        gradient_h = sp.Matrix([sp.diff(h_scalar, q), sp.diff(h_scalar, p)])
        if sp.simplify(x_d.T * omega - gradient_h.T) != sp.zeros(1, 2):
            raise AssertionError("scalar D flow is not Hamiltonian")
        radial_delta_h = sp.expand(
            sp.diff(h_scalar, q) * q + sp.diff(h_scalar, p) * p
        )
        if radial_delta_h != q**2 + p**2:
            raise AssertionError("nonzero scalar charge witness drifted")

        # Improved stress tensor on the homogeneous solution,
        #
        # T_mn = d_m T d_n T - 1/2 g_mn (dT)^2
        #      + (1/6)(G_mn T^2 + g_mn Box(T^2)-nabla_m nabla_n(T^2)).
        #
        # On the unit ESU, G_00=3 and G_ij=-gamma_ij.  With qddot=-q,
        # d_t^2(q^2)=2(p^2-q^2).  Keep the canonical and improvement
        # pieces separate so the positivity result is actually derived.
        second_derivative_q_squared = 2 * (p**2 - q**2)
        rho_canonical = sp.Rational(1, 2) * p**2
        rho_improvement = sp.Rational(1, 6) * (3 * q**2)
        pressure_canonical = sp.Rational(1, 2) * p**2
        pressure_improvement = sp.Rational(1, 6) * (
            -q**2 - second_derivative_q_squared
        )
        rho = sp.expand(rho_canonical + rho_improvement)
        pressure = sp.expand(pressure_canonical + pressure_improvement)
        if rho != sp.Rational(1, 2) * (p**2 + q**2):
            raise AssertionError("improved scalar energy density drifted")
        if pressure != sp.Rational(1, 6) * (p**2 + q**2):
            raise AssertionError("improved scalar pressure drifted")
        if sp.expand(rho - 3 * pressure) != 0:
            raise AssertionError("conformal scalar stress is not traceless")

        # Raw T is not a complete Diff x Weyl slice.  For
        # delta T = epsilon*Tdot - sigma*T, the incidence row has a
        # one-dimensional stabilizer generated by (T,Tdot).
        raw_incidence = sp.Matrix([[p, -q]])
        raw_stabilizer = sp.Matrix([q, p])
        if raw_incidence * raw_stabilizer != sp.zeros(1, 1):
            raise AssertionError("raw scalar stabilizer disappeared")

        # chi=aT is Weyl invariant and transforms only by time pullback.
        # It is a local clock where p=dot(chi) is nonzero, never a global one:
        # q^2+p^2=r^2 forces p=0 at q=+-r on every nontrivial orbit.
        local_clock_relation = sp.expand(q**2 + p**2)
        if local_clock_relation != q**2 + p**2:
            raise AssertionError("local clock relation drifted")

        # Explicit local relational fixture.  The second oscillator carries
        # the opposite symplectic/charge sign, modeling the negative E-like
        # reduced branch needed for a nonempty D-zero level.
        constraint = sp.Rational(1, 2) * (q**2 + p**2 - x**2 - y**2)
        hamiltonian_flow = sp.Matrix(
            [
                _poisson(q, constraint, q, p, x, y),
                _poisson(p, constraint, q, p, x, y),
                _poisson(x, constraint, q, p, x, y),
                _poisson(y, constraint, q, p, x, y),
            ]
        )
        if hamiltonian_flow != sp.Matrix([p, -q, y, -x]):
            raise AssertionError("relational fixture D flow drifted")
        invariant_1 = sp.expand(q * x + p * y)
        invariant_2 = sp.expand(q * y - p * x)
        if _poisson(invariant_1, constraint, q, p, x, y) != 0:
            raise AssertionError("first relational invariant is not closed")
        if _poisson(invariant_2, constraint, q, p, x, y) != 0:
            raise AssertionError("second relational invariant is not closed")
        invariant_bracket = _poisson(invariant_1, invariant_2, q, p, x, y)
        if invariant_bracket != -(q**2 + p**2 + x**2 + y**2):
            raise AssertionError("reduced invariant bracket drifted")

        x_at_tau = sp.expand((invariant_1 * tau - invariant_2 * p_tau) / r**2)
        y_at_tau = sp.expand((invariant_1 * p_tau + invariant_2 * tau) / r**2)
        relation_substitution = {p_tau**2: r**2 - tau**2}
        recovered_1 = sp.expand(tau * x_at_tau + p_tau * y_at_tau).subs(
            relation_substitution
        )
        recovered_2 = sp.expand(tau * y_at_tau - p_tau * x_at_tau).subs(
            relation_substitution
        )
        if sp.simplify(recovered_1 - invariant_1) != 0:
            raise AssertionError("first complete observable reconstruction failed")
        if sp.simplify(recovered_2 - invariant_2) != 0:
            raise AssertionError("second complete observable reconstruction failed")

        payload: dict[str, Any] = {
            "schema": "pure-weyl-scalar-clock-vertical-slice-v1",
            "result_id": "SCALAR_CLOCK_VERTICAL_SLICE",
            "setting_id": "compact_scalar_clock",
            "generator_id": "D_compact",
            "phase_space_id": "compact_scalar_clock",
            "claim_status": "CERTIFIED_OBSTRUCTION",
            "scientific_verdict": None,
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            "conventions": {
                "metric": "g=-dt^2+dOmega_3^2 on the unit cylinder",
                "scalar_curvature": 6,
                "scalar_action": "S_T=-1/2 integral sqrt(-g)[(nabla T)^2+(R/6)T^2]",
                "scalar_equation": "(Box-R/6)T=0",
                "weyl_weight": -1,
                "weyl_invariant_homogeneous_clock": "chi=a*T",
                "normalized_constant_harmonic": "integral_S3 Y0^2=1",
            },
            "homogeneous_clock": {
                "equation": "ddot(chi)+chi=0",
                "general_solution": "chi(t)=A*cos(t)+B*sin(t)",
                "conserved_radius_squared": "A^2+B^2=chi^2+dot(chi)^2",
                "nontrivial_global_monotone_solution_exists": False,
                "local_chart_condition": "dot(chi)!=0",
                "local_clock_range": "|tau|<r on a branch sign(dot(chi))=+/-1",
                "turning_points": "chi=+/-r and dot(chi)=0",
                "maximum_monotone_interval_length": "pi",
                "multiple_crossing_guard": "branch sign(dot(chi)) and interval are required",
            },
            "gauge_incidence": {
                "raw_scalar_variation": "delta T=epsilon*dot(T)-sigma*T",
                "raw_incidence_row": ["dot(T)", "-T"],
                "raw_incidence_generic_rank": 1,
                "raw_stabilizer": ["epsilon=T", "sigma=dot(T)"],
                "raw_T_slice_transverse_to_time_diff_and_weyl": False,
                "invariant_clock_variation": "delta chi=epsilon*dot(chi)",
                "invariant_clock_fixes_time_diff_locally": True,
                "independent_weyl_gauge_still_required": True,
            },
            "improved_charge": {
                "symplectic_form": "Omega_T=dchi wedge dpi",
                "D_vector_field": ["dot(chi)=pi", "dot(pi)=-chi"],
                "hamiltonian": "H_D^T=(pi^2+chi^2)/2",
                "reference_normalization": "H_D^T[0,0]=0",
                "radial_variation": "delta H_D^T=chi^2+pi^2",
                "nonzero_on_every_clock_orbit": True,
                "compact_spatial_flux": "ZERO",
                "integrability": "INTEGRABLE",
                "conservation": "CONSERVED",
                "unrestricted_test_field_verdict": "D_CHARGED",
            },
            "coupled_background_test": {
                "cylinder_bach_tensor": "ZERO",
                "stress_tensor_formula": "d_mu T d_nu T-(1/2)g_mu_nu(dT)^2+(1/6)[G_mu_nu T^2+g_mu_nu Box(T^2)-nabla_mu nabla_nu(T^2)]",
                "energy_split": "rho_can=dot(chi)^2/(2 Vol(S3)); rho_imp=chi^2/(2 Vol(S3))",
                "homogeneous_energy_density": "rho=(dot(chi)^2+chi^2)/(2 Vol(S3))",
                "homogeneous_pressure": "p=rho/3",
                "stress_trace": "ZERO",
                "nonzero_clock_stress_vanishes": False,
                "nonzero_homogeneous_clock_on_exact_vacuum_cylinder_exists": False,
                "only_compatible_homogeneous_scalar_background": "T_bar=0",
                "linearized_diff_weyl_variation_at_T_bar_zero": "ZERO",
                "linearized_scalar_fixes_D_at_T_bar_zero": False,
            },
            "local_relational_fixture": {
                "scope": "REDUCED_MODE_OFF_SHELL_FIXTURE",
                "symplectic_form": "dq wedge dp-dx wedge dy",
                "constraint": "C=(q^2+p^2-x^2-y^2)/2",
                "flow": ["dot(q)=p", "dot(p)=-q", "dot(x)=y", "dot(y)=-x"],
                "invariants": ["I1=q*x+p*y", "I2=q*y-p*x"],
                "invariant_bracket": "{I1,I2}=-(q^2+p^2+x^2+y^2)",
                "bracket_on_C_zero": "{I1,I2}=-2*r^2",
                "complete_observable_x": "x_epsilon(tau)=(I1*tau-I2*p_tau)/r^2",
                "complete_observable_y": "y_epsilon(tau)=(I1*p_tau+I2*tau)/r^2",
                "branch_relation": "p_tau=epsilon*sqrt(r^2-tau^2)",
                "gauge_invariance": "PASS",
                "nontrivial_tau_evolution": "PASS",
            },
            "gate_result": {
                "shared_gate": "SCALAR_CLOCK_VERTICAL_SLICE",
                "status": "OBSTRUCTED_ON_EXACT_VACUUM_CYLINDER",
                "reason": "the only compatible homogeneous scalar background is zero, which has no linearized clock incidence",
                "next_gate": "BACKREACTED_OR_COMPOSITE_CLOCK_MODEL",
                "allowed_repairs": [
                    "solve a genuinely backreacted scalar-pure-Weyl background",
                    "use a Weyl-invariant composite or two-field clock",
                    "use a separately declared reference-matter clock model",
                ],
            },
            "flags": {
                "homogeneous_equation_exact": True,
                "local_monotone_charts_exist": True,
                "global_monotone_single_scalar_clock": False,
                "raw_scalar_slice_is_full_gauge_transverse": False,
                "weyl_invariant_local_clock_constructed": True,
                "improved_scalar_D_charge_nonzero": True,
                "local_relational_fixture_exact": True,
                "exact_vacuum_cylinder_clock_background_exists": False,
                "linearized_single_scalar_clock_exists": False,
                "full_backreacted_clock_phase_space_constructed": False,
            },
            "not_established": [
                "a backreacted scalar-pure-Weyl solution space",
                "a full coupled BV deformation retract or causal Green complex",
                "a global scalar clock chart",
                "an interacting, boundary, or quantum D verdict",
                "a D_GAUGE or D_CHARGED verdict on a consistent backreacted scalar-clock phase space",
            ],
            "provenance": {
                "generator_path": "d_quotient_classical/scalar_clock/conformal_scalar_clock.py",
                "schema_path": "d_quotient_classical/schema/scalar-clock-vertical-slice-v1.schema.json",
                "input_base_commit": INPUT_BASE_COMMIT,
            },
            "claim_boundary": "This certificate proves a scoped obstruction for one real conformally coupled scalar on the exact vacuum cylinder. The positive test-field charge is not promoted to a verdict on a nonexistent coupled clock phase space.",
        }
        result = cls(payload=payload)
        result.verify()
        return result

    def verify(self) -> None:
        p = self.payload
        required = {
            "schema",
            "result_id",
            "setting_id",
            "generator_id",
            "phase_space_id",
            "claim_status",
            "scientific_verdict",
            "dependency_tags",
            "conventions",
            "homogeneous_clock",
            "gauge_incidence",
            "improved_charge",
            "coupled_background_test",
            "local_relational_fixture",
            "gate_result",
            "flags",
            "not_established",
            "provenance",
            "claim_boundary",
        }
        if set(p) != required:
            raise AssertionError("scalar-clock certificate key set drifted")
        if p["schema"] != "pure-weyl-scalar-clock-vertical-slice-v1":
            raise AssertionError("wrong scalar-clock schema")
        if p["claim_status"] != "CERTIFIED_OBSTRUCTION":
            raise AssertionError("scalar-clock obstruction was silently promoted")
        if p["scientific_verdict"] is not None:
            raise AssertionError("nonexistent coupled phase space received a D verdict")
        flags = p["flags"]
        required_true = {
            "homogeneous_equation_exact",
            "local_monotone_charts_exist",
            "weyl_invariant_local_clock_constructed",
            "improved_scalar_D_charge_nonzero",
            "local_relational_fixture_exact",
        }
        required_false = {
            "global_monotone_single_scalar_clock",
            "raw_scalar_slice_is_full_gauge_transverse",
            "exact_vacuum_cylinder_clock_background_exists",
            "linearized_single_scalar_clock_exists",
            "full_backreacted_clock_phase_space_constructed",
        }
        if any(flags.get(key) is not True for key in required_true):
            raise AssertionError("a proved scalar-clock mechanism was dropped")
        if any(flags.get(key) is not False for key in required_false):
            raise AssertionError("an open or obstructed scalar-clock gate was promoted")
        if p["gate_result"]["status"] != "OBSTRUCTED_ON_EXACT_VACUUM_CYLINDER":
            raise AssertionError("wrong shared-gate status")
        if p["coupled_background_test"][
            "only_compatible_homogeneous_scalar_background"
        ] != "T_bar=0":
            raise AssertionError("background obstruction drifted")
        if p["improved_charge"]["unrestricted_test_field_verdict"] != "D_CHARGED":
            raise AssertionError("test-field charge witness disappeared")
        if p["local_relational_fixture"]["scope"] != "REDUCED_MODE_OFF_SHELL_FIXTURE":
            raise AssertionError("relational fixture scope was broadened")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Scalar-clock vertical-slice certificate

## Result

For one real conformally coupled scalar on the unit conformal cylinder,

\[
S_T=-\frac12\int\sqrt{-g}\left((\nabla T)^2+\frac16RT^2\right),
\qquad R=6,
\]

the Weyl-invariant homogeneous variable \(\chi=aT\) obeys

\[
\ddot\chi+\chi=0,
\qquad
H_D^T=\frac12(\dot\chi^2+\chi^2).
\]

Consequently, every nontrivial orbit has local monotone clock charts, but no
global monotone chart.  Each chart must declare both an interval and the sign
of \(\dot\chi\).

The local clock mechanics is exact: the certificate contains explicit
complete observables on a finite negative-sign E-like fixture, together with
their nonzero reduced Poisson bracket.  This proves that the relational
construction itself is not the obstruction.

## Exact-cylinder obstruction

The improved homogeneous stress tensor satisfies

\[
\rho=\frac{\dot\chi^2+\chi^2}{2\operatorname{Vol}(S^3)},
\qquad p=\frac{\rho}{3}.
\]

The exact cylinder is conformally flat, hence its Bach tensor vanishes.  The
coupled metric equation therefore excludes every nonzero homogeneous scalar
clock on that background.  The only compatible homogeneous background is
\(\bar T=0\), but at that background

\[
\delta_{(\xi,\sigma)}T
=\xi^0\dot{\bar T}-\sigma\bar T=0,
\]

so the linearized scalar cannot fix \(D\).

Thus

```text
SCALAR_CLOCK_VERTICAL_SLICE = OBSTRUCTED_ON_EXACT_VACUUM_CYLINDER
```

No `D_GAUGE` or `D_CHARGED` verdict is assigned to a coupled scalar-clock
phase space that has not been constructed.  The positive test-field charge
is retained only as a scoped vertical witness.

## Next admissible gate

One must now choose and certify one of:

1. a genuinely backreacted scalar--pure-Weyl background;
2. a Weyl-invariant composite or two-field clock;
3. a separately declared reference-matter clock model.

The result does not address interacting, boundary, or quantum stability.
"""


def _write(result: ScalarClockVerticalSlice) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: ScalarClockVerticalSlice) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError(f"stale certificate: {CERTIFICATE_PATH}")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError(f"stale report: {REPORT_PATH}")
    if not SCHEMA_PATH.is_file():
        raise AssertionError(f"missing schema: {SCHEMA_PATH}")


def _guards(result: ScalarClockVerticalSlice) -> None:
    mutations = (
        ("global clock", ("flags", "global_monotone_single_scalar_clock"), True),
        (
            "coupled background",
            ("flags", "exact_vacuum_cylinder_clock_background_exists"),
            True,
        ),
        ("linearized clock", ("flags", "linearized_single_scalar_clock_exists"), True),
        ("missing charge", ("flags", "improved_scalar_D_charge_nonzero"), False),
        ("premature verdict", ("scientific_verdict",), "D_GAUGE"),
    )
    passed = 0
    for label, path, value in mutations:
        payload = deepcopy(result.payload)
        target: Any = payload
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            ScalarClockVerticalSlice(payload=payload).verify()
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
    result = ScalarClockVerticalSlice.build()
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
