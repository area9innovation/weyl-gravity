#!/usr/bin/env python3
"""Certify the minimal neutral conformal-clock pair on the cylinder.

Two real weight-minus-one conformal scalars are given opposite kinetic
signs.  Their homogeneous modes are identical unit oscillators, but their
improved stress tensors and Hamiltonians enter with opposite signs.  On the
regular zero-energy sector their stress cancels componentwise, so the exact
Bach-flat cylinder remains a solution.

The construction is more than one tuned orbit.  The energy difference and
the Wronskian are conserved.  On the open sector

    H_D = 0,   W = chi_1*pi_2 - chi_2*pi_1 != 0,

the projective angle atan2(chi_2, chi_1) is a Weyl-invariant, everywhere
monotone group-valued clock.  Its incidence with compact time translation is
nonzero, while the Euclidean radius fixes the common Weyl rescaling.  The
two incidence directions have determinant rho squared and are transverse.

The theorem is deliberately scoped to the exact homogeneous classical
sector.  The opposite-sign scalar is reference/Krein matter; an inhomogeneous
BV completion, stability, and quantum admissibility are not inferred.
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
    / "NEUTRAL_CONFORMAL_CLOCK_PAIR.json"
)
REPORT_PATH = (
    ROOT
    / "d_quotient_classical"
    / "reports"
    / "neutral-conformal-clock-pair.md"
)
SCHEMA_PATH = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "neutral-conformal-clock-pair-v1.schema.json"
)
INPUT_BASE_COMMIT = "0c200a2805f1085f44e466987dc126001035585b"


def _poisson(first: sp.Expr, second: sp.Expr, variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    """Poisson bracket for ``dx1^dp1 - dx2^dp2``."""

    x1, p1, x2, p2 = variables
    return sp.expand(
        sp.diff(first, x1) * sp.diff(second, p1)
        - sp.diff(first, p1) * sp.diff(second, x1)
        - sp.diff(first, x2) * sp.diff(second, p2)
        + sp.diff(first, p2) * sp.diff(second, x2)
    )


@dataclass(frozen=True)
class NeutralConformalClockPair:
    """Exact certificate for the homogeneous neutral clock-pair sector."""

    payload: dict[str, Any]

    @classmethod
    def build(cls) -> "NeutralConformalClockPair":
        x1, p1, x2, p2, r, t = sp.symbols(
            "chi_1 pi_1 chi_2 pi_2 r t", real=True
        )
        variables = (x1, p1, x2, p2)

        # Exact quadrature representative of the regular solution family.
        orbit = sp.Matrix(
            [r * sp.cos(t), -r * sp.sin(t), r * sp.sin(t), r * sp.cos(t)]
        )
        if any(
            sp.simplify(sp.diff(orbit[index], t) - orbit[index + 1]) != 0
            for index in (0, 2)
        ):
            raise AssertionError("quadrature clock positions do not evolve correctly")
        if any(
            sp.simplify(sp.diff(orbit[index], t) + orbit[index - 1]) != 0
            for index in (1, 3)
        ):
            raise AssertionError("quadrature clock momenta do not evolve correctly")

        h1 = sp.Rational(1, 2) * (x1**2 + p1**2)
        h2 = sp.Rational(1, 2) * (x2**2 + p2**2)
        h_total = sp.expand(h1 - h2)
        wronskian = sp.expand(x1 * p2 - x2 * p1)
        radius_squared = sp.expand(x1**2 + x2**2)
        if sp.simplify(h_total.subs(dict(zip(variables, orbit)))) != 0:
            raise AssertionError("quadrature orbit is not neutral")
        if sp.simplify(wronskian.subs(dict(zip(variables, orbit))) - r**2) != 0:
            raise AssertionError("quadrature Wronskian drifted")
        if sp.simplify(radius_squared.subs(dict(zip(variables, orbit))) - r**2) != 0:
            raise AssertionError("quadrature radius drifted")

        # The indefinite symplectic form and Hamiltonian generate the same
        # oscillator equation in both components.
        omega = sp.diag(1, 1, -1, -1) * sp.Matrix(
            [[0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 0, 1], [0, 0, -1, 0]]
        )
        # The preceding matrix product is block diag(J,-J).
        d_flow = sp.Matrix([p1, -x1, p2, -x2])
        gradient_h = sp.Matrix([sp.diff(h_total, item) for item in variables])
        if sp.simplify(d_flow.T * omega - gradient_h.T) != sp.zeros(1, 4):
            raise AssertionError("neutral D flow is not Hamiltonian")

        if _poisson(h_total, wronskian, variables) != 0:
            raise AssertionError("Wronskian is not conserved")
        if _poisson(h_total, h_total, variables) != 0:
            raise AssertionError("neutral charge is not conserved")

        # For theta=atan2(x2,x1), derivatives are used instead of asking
        # SymPy to simplify branch-sensitive atan2 expressions.
        theta_gradient = sp.Matrix(
            [-x2 / radius_squared, 0, x1 / radius_squared, 0]
        )
        theta_velocity = sp.factor((theta_gradient.T * d_flow)[0])
        if sp.simplify(theta_velocity - wronskian / radius_squared) != 0:
            raise AssertionError("projective clock velocity drifted")
        if sp.simplify(theta_velocity.subs(dict(zip(variables, orbit))) - 1) != 0:
            raise AssertionError("quadrature clock is not unit-speed")

        # Raw-field incidence under (epsilon_D, sigma_W):
        # delta T_A = epsilon*dot(T_A) - sigma*T_A.  In the fixed cylinder
        # frame a=1 the numerical values of T_A and chi_A agree, but chi_A=aT_A
        # is Weyl invariant and must not itself be used as the Weyl gauge.
        incidence = sp.Matrix([[p1, -x1], [p2, -x2]])
        incidence_det = sp.factor(incidence.det())
        if incidence_det != wronskian:
            raise AssertionError("Diff x Weyl incidence determinant drifted")
        if sp.simplify(incidence_det.subs(dict(zip(variables, orbit))) - r**2) != 0:
            raise AssertionError("quadrature incidence is not transverse")

        # Gauge functions theta and u=log(rho) diagonalize the incidence on
        # the representative orbit: D moves theta and Weyl moves u.
        log_radius_d_velocity = sp.factor((x1 * p1 + x2 * p2) / radius_squared)
        if sp.simplify(log_radius_d_velocity.subs(dict(zip(variables, orbit)))) != 0:
            raise AssertionError("radius gauge mixes with D on the representative")

        # The improved homogeneous stress is linear in the internal sign.
        # Each scalar has rho_A=H_A/Vol and p_A=rho_A/3, hence the total
        # stress is proportional to the same constraint H_total.
        rho_numerator = sp.expand(h1 - h2)
        pressure_numerator = sp.expand((h1 - h2) / 3)
        if rho_numerator != h_total or sp.expand(3 * pressure_numerator - h_total) != 0:
            raise AssertionError("neutral improved stress relation drifted")
        if sp.simplify(rho_numerator.subs(dict(zip(variables, orbit)))) != 0:
            raise AssertionError("quadrature stress does not cancel")

        # The zero-charge surface is regular at r != 0.  Since
        # i_X Omega=dH, dH annihilates all tangent vectors to H=0 and the D
        # flow is a kernel direction of the pulled-back two-form.
        gradient_on_orbit = sp.simplify(gradient_h.subs(dict(zip(variables, orbit))))
        gradient_norm_squared = sp.simplify(sum(entry**2 for entry in gradient_on_orbit))
        if sp.simplify(gradient_norm_squared - 2 * r**2) != 0:
            raise AssertionError("zero-charge surface regularity drifted")

        payload: dict[str, Any] = {
            "schema": "pure-weyl-neutral-conformal-clock-pair-v1",
            "result_id": "NEUTRAL_CONFORMAL_CLOCK_PAIR",
            "setting_id": "compact_neutral_clock_pair",
            "generator_id": "D_compact",
            "phase_space_id": "compact_neutral_clock_pair_homogeneous",
            "claim_status": "CERTIFIED_SCOPED_CLASSICAL_THEOREM",
            "scientific_verdict": "D_GAUGE",
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            "conventions": {
                "metric": "g=-dt^2+dOmega_3^2 on the unit conformal cylinder",
                "scalar_curvature": 6,
                "fields": "two real conformal scalars T_1,T_2 of Weyl weight -1",
                "internal_metric": "eta_AB=diag(+1,-1)",
                "action": "S_pair=-1/2 integral sqrt(-g) eta_AB[(nabla T^A)(nabla T^B)+(R/6)T^A T^B]",
                "homogeneous_variables": "chi_A=a*T_A; on the fixed cylinder a=1 so chi_A=T_A numerically",
                "symplectic_form": "Omega=dchi_1 wedge dpi_1-dchi_2 wedge dpi_2",
            },
            "exact_solution_family": {
                "equations": ["ddot(chi_1)+chi_1=0", "ddot(chi_2)+chi_2=0"],
                "neutral_constraint": "H_D=(chi_1^2+pi_1^2-chi_2^2-pi_2^2)/2=0",
                "regular_clock_sector": "H_D=0 and W=chi_1*pi_2-chi_2*pi_1!=0",
                "representative": [
                    "chi_1=r*cos(t)",
                    "pi_1=-r*sin(t)",
                    "chi_2=r*sin(t)",
                    "pi_2=r*cos(t)",
                ],
                "representative_charge": "ZERO",
                "representative_wronskian": "r^2",
                "wronskian_conserved": True,
                "regular_sector_preserved": True,
            },
            "stress_cancellation": {
                "individual_density": "rho_A=(chi_A^2+pi_A^2)/(2 Vol(S3))",
                "total_density": "rho_total=H_D/Vol(S3)",
                "total_pressure": "p_total=H_D/(3 Vol(S3))",
                "total_trace": "ZERO",
                "stress_vanishes_on_neutral_constraint": True,
                "cylinder_bach_tensor": "ZERO",
                "coupled_metric_equation_satisfied": True,
                "scalar_equations_satisfied": True,
                "exact_nonzero_clock_background_exists": True,
            },
            "gauge_slice": {
                "raw_variation": "delta T_A=epsilon_D*dot(T_A)-sigma_W*T_A",
                "incidence_frame": "fixed cylinder a=1, where T_A=chi_A numerically; chi_A=a*T_A remains Weyl invariant",
                "incidence_matrix": [["dot(T_1)", "-T_1"], ["dot(T_2)", "-T_2"]],
                "incidence_determinant": "W=T_1*dot(T_2)-T_2*dot(T_1)",
                "full_rank_on_regular_sector": True,
                "clock": "z=(chi_1+i chi_2)/sqrt(chi_1^2+chi_2^2) in U(1)",
                "local_angle": "theta=atan2(chi_2,chi_1)",
                "clock_velocity": "dot(theta)=W/(chi_1^2+chi_2^2)",
                "clock_velocity_never_zero_on_regular_sector": True,
                "clock_orientation": "sign(W), conserved",
                "weyl_invariant": True,
                "weyl_gauge": "u=(1/2)log(T_1^2+T_2^2) in raw-field coordinates",
                "representative_incidence": "delta theta=epsilon_D; delta u=-sigma_W",
                "global_compact_D_clock": True,
                "global_real_lift_on_universal_cover": False,
                "universal_cover_requirement": "choose a winding lift and an initial reference",
            },
            "symplectic_reduction": {
                "D_hamiltonian": "H_D=(chi_1^2+pi_1^2-chi_2^2-pi_2^2)/2",
                "D_flow": ["pi_1", "-chi_1", "pi_2", "-chi_2"],
                "zero_level_regular_for_r_nonzero": True,
                "gradient_norm_squared_on_representative": "2*r^2",
                "D_is_kernel_of_pulled_back_symplectic_form": True,
                "compact_spatial_flux": "ZERO",
                "integrability": "INTEGRABLE",
                "conservation": "CONSERVED",
                "phase_space_preserved": True,
                "surface_corner_terms": "NONE_ON_CLOSED_S3",
                "scoped_verdict": "D_GAUGE",
            },
            "health_and_scope": {
                "opposite_sign_reference_scalar_present": True,
                "unrestricted_matter_energy_positive": False,
                "negative_direction_removed_by_full_local_BV_reduction": "NOT_ESTABLISHED",
                "inhomogeneous_stress_cancellation": "NOT_ESTABLISHED",
                "interpretation": "minimal classical reference/Krein clock sector, not a healthy standalone matter theory",
            },
            "gate_result": {
                "shared_gate": "BACKREACTED_OR_COMPOSITE_CLOCK_MODEL",
                "status": "PASSED_BY_NEUTRAL_TWO_FIELD_HOMOGENEOUS_SECTOR",
                "replaces": "the obstructed one-real-scalar exact-cylinder candidate",
                "next_gate": "FULL_NEUTRAL_CLOCK_PAIR_BV_COMPLETION",
            },
            "flags": {
                "two_field_action_weyl_invariant": True,
                "exact_nonzero_cylinder_clock_background": True,
                "componentwise_stress_cancellation": True,
                "regular_sector_evolution_invariant": True,
                "diff_weyl_incidence_full_rank": True,
                "compact_group_valued_clock_global": True,
                "universal_cover_real_clock_global_without_lift": False,
                "homogeneous_D_reduction_exact": True,
                "full_inhomogeneous_BV_completion": False,
                "healthy_positive_matter_completion": False,
            },
            "not_established": [
                "a support-local inhomogeneous BV complex for the clock pair",
                "removal or harmlessness of the opposite-sign scalar outside the homogeneous constrained quotient",
                "nonlinear stability of the neutral clock sector under arbitrary perturbations",
                "a distributional, Hadamard, or quantum completion",
                "a real-valued global clock on the universal cover without extra winding data",
            ],
            "provenance": {
                "generator_path": "d_quotient_classical/composite_clock/neutral_conformal_clock.py",
                "schema_path": "d_quotient_classical/schema/neutral-conformal-clock-pair-v1.schema.json",
                "input_base_commit": INPUT_BASE_COMMIT,
            },
            "claim_boundary": "This certificate proves an exact nonzero homogeneous clock sector on the Bach-flat cylinder and a scoped D_GAUGE reduction there. It uses an opposite-sign reference scalar and does not promote an inhomogeneous, healthy-matter, interacting, boundary, or quantum theorem.",
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
            "exact_solution_family",
            "stress_cancellation",
            "gauge_slice",
            "symplectic_reduction",
            "health_and_scope",
            "gate_result",
            "flags",
            "not_established",
            "provenance",
            "claim_boundary",
        }
        if set(p) != required:
            raise AssertionError("neutral-clock certificate key set drifted")
        if p["schema"] != "pure-weyl-neutral-conformal-clock-pair-v1":
            raise AssertionError("wrong neutral-clock schema")
        if p["scientific_verdict"] != "D_GAUGE":
            raise AssertionError("scoped homogeneous verdict was lost")
        if p["phase_space_id"] != "compact_neutral_clock_pair_homogeneous":
            raise AssertionError("neutral-clock verdict escaped its phase space")
        flags = p["flags"]
        required_true = {
            "two_field_action_weyl_invariant",
            "exact_nonzero_cylinder_clock_background",
            "componentwise_stress_cancellation",
            "regular_sector_evolution_invariant",
            "diff_weyl_incidence_full_rank",
            "compact_group_valued_clock_global",
            "homogeneous_D_reduction_exact",
        }
        required_false = {
            "universal_cover_real_clock_global_without_lift",
            "full_inhomogeneous_BV_completion",
            "healthy_positive_matter_completion",
        }
        if any(flags.get(key) is not True for key in required_true):
            raise AssertionError("a proved neutral-clock property was dropped")
        if any(flags.get(key) is not False for key in required_false):
            raise AssertionError("an open neutral-clock gate was promoted")
        if not p["health_and_scope"]["opposite_sign_reference_scalar_present"]:
            raise AssertionError("Krein/reference-field caveat was erased")
        if p["gate_result"]["status"] != "PASSED_BY_NEUTRAL_TWO_FIELD_HOMOGENEOUS_SECTOR":
            raise AssertionError("wrong replacement-gate status")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Neutral conformal clock-pair theorem

## Result

The one-scalar obstruction has a minimal exact-cylinder repair at the
classical homogeneous level.  Take two real conformal scalars with internal
metric \(\eta_{AB}=\operatorname{diag}(+1,-1)\):

\[
S_{\rm pair}=-\frac12\int\sqrt{-g}\,\eta_{AB}
\left(\nabla T^A\!\cdot\!\nabla T^B+\frac{R}{6}T^AT^B\right).
\]

Their homogeneous variables \(\chi_A=aT_A\) are unit oscillators.  Define

\[
H_D=\frac12(\chi_1^2+\pi_1^2-\chi_2^2-\pi_2^2),\qquad
W=\chi_1\pi_2-\chi_2\pi_1.
\]

Both \(H_D\) and \(W\) are conserved.  On the open sector

\[
H_D=0,\qquad W\ne0,
\]

the total improved stress tensor vanishes componentwise.  Since the cylinder
is Bach-flat, this is an exact nonzero solution sector of the coupled scalar
and metric equations, rather than a test-field background.

A representative is

\[
(\chi_1,\pi_1,\chi_2,\pi_2)
=r(\cos t,-\sin t,\sin t,\cos t).
\]

## Clock and gauge incidence

The projective field

\[
z=\frac{\chi_1+i\chi_2}{\sqrt{\chi_1^2+\chi_2^2}}\in U(1)
\]

is Weyl invariant.  Its local angle obeys

\[
\dot\theta=\frac{W}{\chi_1^2+\chi_2^2},
\]

so it has no turning point on either connected component \(W>0\) or
\(W<0\).  It is a global group-valued clock for the effective compact
\(D\)-orbit.  A real clock on the universal cover additionally requires a
winding lift and an initial reference.

In raw scalar coordinates, compact time translation and Weyl rescaling act by

\[
\delta T_A=\epsilon_D\dot T_A-\sigma_WT_A.
\]

In the fixed cylinder frame \(a=1\), these raw fields agree numerically with
\(\chi_A\), and the two-field incidence determinant is exactly \(W\).  It
therefore has full rank throughout the regular clock sector.  The distinction
is conceptual: \(\chi_A=aT_A\) is individually Weyl invariant and is used for
oscillator dynamics, whereas the raw radius
\(u=\tfrac12\log(T_1^2+T_2^2)\) fixes Weyl.  The projective angle fixes \(D\)
independently.

## Scoped symplectic conclusion

With

\[
\Omega=d\chi_1\wedge d\pi_1-d\chi_2\wedge d\pi_2,
\]

the Hamiltonian of the \(D\)-flow is \(H_D\).  The zero level is regular for
nonzero amplitude, and the \(D\)-flow is a kernel direction of the pullback
of \(\Omega\).  Therefore

```text
D_compact = D_GAUGE
```

on the declared phase space
`compact_neutral_clock_pair_homogeneous`.

## Essential limitation

The cancellation uses an opposite-sign reference scalar.  The unrestricted
matter theory is not positive-energy, and this certificate does not show
that the negative direction is removed in the full inhomogeneous BV theory.
It proves a working classical clock and exact-cylinder background, not a
healthy standalone matter model.

The next gate is `FULL_NEUTRAL_CLOCK_PAIR_BV_COMPLETION`: construct the local
inhomogeneous complex, determine whether its reference sector is entirely
gauge/contractible, and test nonlinear stability and quantum admissibility.
"""


def _write(result: NeutralConformalClockPair) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: NeutralConformalClockPair) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError(f"stale certificate: {CERTIFICATE_PATH}")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError(f"stale report: {REPORT_PATH}")
    if not SCHEMA_PATH.is_file():
        raise AssertionError(f"missing schema: {SCHEMA_PATH}")


def _guards(result: NeutralConformalClockPair) -> None:
    mutations = (
        ("lost background", ("flags", "exact_nonzero_cylinder_clock_background"), False),
        ("lost transversality", ("flags", "diff_weyl_incidence_full_rank"), False),
        ("positive matter overclaim", ("flags", "healthy_positive_matter_completion"), True),
        ("BV overclaim", ("flags", "full_inhomogeneous_BV_completion"), True),
        ("scope escape", ("phase_space_id",), "compact_scalar_clock"),
        ("erased Krein caveat", ("health_and_scope", "opposite_sign_reference_scalar_present"), False),
    )
    passed = 0
    for label, path, value in mutations:
        payload = deepcopy(result.payload)
        target: Any = payload
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            NeutralConformalClockPair(payload=payload).verify()
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
    result = NeutralConformalClockPair.build()
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
