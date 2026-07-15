#!/usr/bin/env python3
"""Classify homogeneous positive-sign conformal stealth clocks on the ESU.

For one real conformally coupled scalar with the only local Weyl-invariant
potential, ``V(T)=kappa*T**4/4``, the on-shell homogeneous stress tensor on
the unit Einstein cylinder is radiation-like:

    rho = (Tdot**2 + T**2)/2 + kappa*T**4/4,
    p = rho/3.

Consequently a homogeneous stealth field is a zero-energy trajectory.  For
``kappa >= 0`` only the zero field is possible.  For ``kappa < 0`` every
connected nonzero real solution is, up to sign and time translation,

    T(t) = sqrt(-2/kappa) * sec(t-t0).

It is locally stress-free and has positive kinetic sign, but it turns once
and reaches poles at finite cylinder time.  It therefore cannot supply a
globally regular homogeneous clock.  The result is deliberately scoped: it
does not rule out inhomogeneous stealth configurations or a clock on a
genuinely non-conformally-flat Bach-sourced background.
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
    / "HOMOGENEOUS_POSITIVE_CONFORMAL_STEALTH_CLOCK.json"
)
REPORT_PATH = (
    ROOT
    / "d_quotient_classical"
    / "reports"
    / "homogeneous-positive-conformal-stealth-clock.md"
)
SCHEMA_PATH = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "homogeneous-positive-conformal-stealth-clock-v1.schema.json"
)


@dataclass(frozen=True)
class HomogeneousPositiveConformalStealthClock:
    """Exact homogeneous stealth classification and clock obstruction."""

    payload: dict[str, Any]

    @classmethod
    def build(cls) -> "HomogeneousPositiveConformalStealthClock":
        field, velocity, acceleration, kappa = sp.symbols(
            "T Tdot Tddot kappa", real=True
        )

        potential = kappa * field**4 / 4
        rho = sp.expand((velocity**2 + field**2) / 2 + potential)

        # This is the exact spatial pressure before using the scalar EOM.
        pressure_off_shell = sp.expand(
            velocity**2 / 6
            - field**2 / 6
            - field * acceleration / 3
            - potential
        )
        eom_acceleration = -field - kappa * field**3
        pressure_on_shell = sp.expand(
            pressure_off_shell.subs(acceleration, eom_acceleration)
        )
        if sp.expand(3 * pressure_on_shell - rho) != 0:
            raise AssertionError("homogeneous conformal stress is not traceless")

        # The nonzero stealth branch requires kappa=-g<0.  Its complete
        # connected real solution family is the secant orbit below.
        g = sp.symbols("g", positive=True, real=True)
        tau = sp.symbols("tau", real=True)
        amplitude = sp.sqrt(sp.Rational(2, 1) / g)
        stealth_field = amplitude / sp.cos(tau)
        stealth_velocity = sp.diff(stealth_field, tau)
        stealth_acceleration = sp.diff(stealth_field, tau, 2)
        stealth_eom_defect = sp.trigsimp(
            stealth_acceleration + stealth_field - g * stealth_field**3
        )
        stealth_rho = sp.trigsimp(
            rho.subs(
                {
                    field: stealth_field,
                    velocity: stealth_velocity,
                    kappa: -g,
                }
            )
        )
        if sp.simplify(stealth_eom_defect) != 0:
            raise AssertionError("secant stealth branch fails the scalar equation")
        if sp.simplify(stealth_rho) != 0:
            raise AssertionError("secant stealth branch has nonzero stress")

        # Exhaustiveness is exposed by u=a/T.  The zero-energy equation
        # becomes udot^2=1-u^2, whose nonconstant connected solutions are
        # shifted cosines.  Inverting gives precisely the secant family.
        u, u_dot = sp.symbols("u udot", real=True)
        transformed_energy_defect = sp.factor(
            (
                rho.subs(
                    {
                        field: amplitude / u,
                        velocity: -amplitude * u_dot / u**2,
                        kappa: -g,
                    }
                )
                * (g * u**4)
            )
        )
        if sp.simplify(transformed_energy_defect - (u_dot**2 + u**2 - 1)) != 0:
            raise AssertionError("zero-energy equation did not reduce to a circle")

        turning_velocity = sp.simplify(stealth_velocity.subs(tau, 0))
        turning_acceleration = sp.simplify(stealth_acceleration.subs(tau, 0))
        if turning_velocity != 0 or sp.simplify(turning_acceleration - amplitude) != 0:
            raise AssertionError("secant turning-point data drifted")

        # A scalar clock fixes temporal diffeomorphisms only on charts where
        # Tdot is nonzero.  Raw T still gives one equation for the temporal
        # diffeomorphism and Weyl parameters, so a separate Weyl gauge is
        # required exactly as in the free one-scalar audit.
        epsilon, sigma = sp.symbols("epsilon_D sigma_W", real=True)
        raw_variation = sp.expand(epsilon * velocity - sigma * field)
        if raw_variation != epsilon * velocity - sigma * field:
            raise AssertionError("Diff x Weyl incidence drifted")

        payload: dict[str, Any] = {
            "schema": "pure-weyl-homogeneous-positive-conformal-stealth-clock-v1",
            "result_id": "HOMOGENEOUS_POSITIVE_CONFORMAL_STEALTH_CLOCK",
            "setting_id": "compact_positive_conformal_stealth_clock",
            "generator_id": "D_compact",
            "phase_space_id": "homogeneous_conformal_scalar_on_unit_cylinder",
            "claim_status": "CERTIFIED_SCOPED_OBSTRUCTION",
            "scientific_verdict": None,
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            "conventions": {
                "metric": "g=-dt^2+dOmega_3^2 on the unit conformal cylinder",
                "scalar_curvature": 6,
                "field": "one real conformal scalar T of Weyl weight -1",
                "kinetic_sign": "POSITIVE_STANDARD",
                "action": "S=-integral sqrt(-g)[(nabla T)^2/2+R*T^2/12+kappa*T^4/4]",
                "equation": "ddot(T)+T+kappa*T^3=0",
                "potential": "V(T)=kappa*T^4/4",
            },
            "stress_classification": {
                "energy_density": "rho=(dot(T)^2+T^2)/2+kappa*T^4/4",
                "pressure_off_shell": "p=dot(T)^2/6-T^2/6-T*ddot(T)/3-kappa*T^4/4",
                "pressure_on_shell": "p=rho/3",
                "stress_trace_on_shell": "ZERO",
                "stealth_condition": "rho=0",
                "kappa_nonnegative_nonzero_stealth_exists": False,
                "kappa_negative_required_for_nonzero_homogeneous_stealth": True,
            },
            "complete_nonzero_family": {
                "coupling": "kappa=-g with g>0",
                "solution": "T(t)=s*sqrt(2/g)*sec(t-t0), s in {+1,-1}",
                "first_integral": "dot(T)^2=T^2[(g/2)T^2-1]",
                "exhaustiveness_variable": "u=sqrt(2/g)/T",
                "reduced_first_integral": "dot(u)^2+u^2=1",
                "scalar_equation_exact": True,
                "stress_tensor_zero": True,
                "family_exhaustive_on_connected_nonzero_real_branches": True,
            },
            "clock_and_health": {
                "local_kinetic_sign": "POSITIVE",
                "potential_bounded_below": False,
                "turning_point": "t=t0, dot(T)=0",
                "nearest_poles": "t=t0+/-pi/2",
                "maximal_regular_interval_length": "pi",
                "finite_time_singularity": True,
                "globally_regular_on_R_times_S3": False,
                "globally_monotone_clock": False,
                "local_monotone_clock_charts": True,
                "raw_diff_weyl_incidence_rank": 1,
                "independent_weyl_gauge_required": True,
            },
            "gate_result": {
                "gate": "HOMOGENEOUS_POSITIVE_STEALTH_CLOCK",
                "status": "OBSTRUCTED_BY_TURNING_POINT_AND_FINITE_TIME_POLES",
                "parent_gate": "POSITIVE_ENERGY_NONCONFORMALLY_FLAT_OR_STEALTH_CLOCK",
                "parent_gate_status": "OPEN",
                "next_gate": "INHOMOGENEOUS_STEALTH_OR_NONCONFORMALLY_FLAT_CLOCK",
            },
            "flags": {
                "quartic_family_complete_for_local_weyl_invariant_potential": True,
                "homogeneous_stress_derived": True,
                "nonzero_local_stealth_branch_exists": True,
                "nonzero_global_regular_homogeneous_stealth_exists": False,
                "healthy_global_homogeneous_clock_exists": False,
                "inhomogeneous_stealth_clock_ruled_out": False,
                "nonconformally_flat_backreacted_clock_ruled_out": False,
            },
            "not_established": [
                "an inhomogeneous stress-free scalar with timelike nonvanishing gradient",
                "a globally regular positive clock on a Bach-sourced non-conformally-flat background",
                "a support-local BV contraction for either surviving alternative",
                "a Lorentzian-boundary, nonlinear, or quantum D verdict",
            ],
            "claim_boundary": "This certificate completely classifies real homogeneous stealth trajectories of one positive-sign conformal scalar with quartic Weyl-invariant potential on the unit cylinder. It proves that none is a globally regular homogeneous clock. It does not rule out inhomogeneous stealth fields or genuinely backreacted non-conformally-flat clocks.",
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
            "stress_classification",
            "complete_nonzero_family",
            "clock_and_health",
            "gate_result",
            "flags",
            "not_established",
            "claim_boundary",
        }
        if set(p) != required:
            raise AssertionError("homogeneous stealth certificate key set drifted")
        if p["schema"] != "pure-weyl-homogeneous-positive-conformal-stealth-clock-v1":
            raise AssertionError("wrong homogeneous stealth schema")
        if p["claim_status"] != "CERTIFIED_SCOPED_OBSTRUCTION":
            raise AssertionError("homogeneous stealth obstruction was promoted")
        if p["scientific_verdict"] is not None:
            raise AssertionError("obstructed clock received a D verdict")
        if p["gate_result"]["parent_gate_status"] != "OPEN":
            raise AssertionError("surviving parent clock gate was closed")
        flags = p["flags"]
        required_true = {
            "quartic_family_complete_for_local_weyl_invariant_potential",
            "homogeneous_stress_derived",
            "nonzero_local_stealth_branch_exists",
        }
        required_false = {
            "nonzero_global_regular_homogeneous_stealth_exists",
            "healthy_global_homogeneous_clock_exists",
            "inhomogeneous_stealth_clock_ruled_out",
            "nonconformally_flat_backreacted_clock_ruled_out",
        }
        if any(flags.get(key) is not True for key in required_true):
            raise AssertionError("a proved homogeneous stealth mechanism was dropped")
        if any(flags.get(key) is not False for key in required_false):
            raise AssertionError("an open or obstructed stealth gate was promoted")
        if p["clock_and_health"]["potential_bounded_below"] is not False:
            raise AssertionError("negative quartic instability was hidden")
        if p["clock_and_health"]["finite_time_singularity"] is not True:
            raise AssertionError("finite-time stealth pole was hidden")
        if p["complete_nonzero_family"]["family_exhaustive_on_connected_nonzero_real_branches"] is not True:
            raise AssertionError("stealth-family exhaustiveness was dropped")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Homogeneous positive-sign conformal stealth-clock audit

## Result

Consider one real conformal scalar with the standard positive kinetic sign
and the complete local Weyl-invariant potential,

\[
S=-\int\sqrt{-g}\left[
\frac12(\nabla T)^2+\frac1{12}RT^2+\frac\kappa4T^4
\right].
\]

For a homogeneous field on the unit conformal cylinder, the exact equation
and improved stress tensor are

\[
\ddot T+T+\kappa T^3=0,
\qquad
\rho=\frac12(\dot T^2+T^2)+\frac\kappa4T^4,
\qquad
p=\frac\rho3.
\]

Thus a homogeneous stealth configuration is precisely a zero-energy
trajectory.

## Complete nonzero stealth family

For \(\kappa\geq0\), positivity of the three terms in \(\rho\) leaves only
\(T=0\).  A nonzero branch therefore requires \(\kappa=-g<0\).  Its first
integral is

\[
\dot T^2=T^2\left(\frac g2T^2-1\right).
\]

On a connected nonzero branch set

\[
u=\frac{\sqrt{2/g}}{T}.
\]

The first integral becomes

\[
\dot u^2+u^2=1.
\]

Therefore every nonzero real homogeneous stealth solution is, up to sign and
time translation,

\[
T(t)=\pm\sqrt{\frac2g}\sec(t-t_0).
\]

Direct substitution verifies both the scalar equation and
\(T_{\mu\nu}=0\).

## Clock obstruction

The field has a positive local kinetic sign, unlike the neutral two-scalar
candidate.  But its stealth potential is unbounded below.  More decisively,
every secant branch has

\[
\dot T(t_0)=0
\]

and poles at \(t=t_0\pm\pi/2\).  Hence it is neither globally monotone nor
globally regular on \(\mathbb R\times S^3\).  It supplies only local clock
charts separated by a turning point and finite-time singularities.

The scoped conclusion is

```text
HOMOGENEOUS_POSITIVE_STEALTH_CLOCK
    = OBSTRUCTED_BY_TURNING_POINT_AND_FINITE_TIME_POLES
```

The parent gate remains open.  This calculation does not exclude an
inhomogeneous stealth field with everywhere timelike nonzero gradient, nor a
positive clock on a genuinely non-conformally-flat Bach-sourced background.
The next gate is
`INHOMOGENEOUS_STEALTH_OR_NONCONFORMALLY_FLAT_CLOCK`.
"""


def _write(result: HomogeneousPositiveConformalStealthClock) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: HomogeneousPositiveConformalStealthClock) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError(f"stale certificate: {CERTIFICATE_PATH}")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError(f"stale report: {REPORT_PATH}")
    if not SCHEMA_PATH.is_file():
        raise AssertionError(f"missing schema: {SCHEMA_PATH}")


def _guards(result: HomogeneousPositiveConformalStealthClock) -> None:
    mutations = (
        ("premature D verdict", ("scientific_verdict",), "D_GAUGE"),
        ("hide local branch", ("flags", "nonzero_local_stealth_branch_exists"), False),
        ("promote global branch", ("flags", "healthy_global_homogeneous_clock_exists"), True),
        ("close inhomogeneous gate", ("flags", "inhomogeneous_stealth_clock_ruled_out"), True),
        ("close backreaction gate", ("flags", "nonconformally_flat_backreacted_clock_ruled_out"), True),
        ("hide unstable potential", ("clock_and_health", "potential_bounded_below"), True),
        ("hide finite pole", ("clock_and_health", "finite_time_singularity"), False),
        ("promote parent", ("gate_result", "parent_gate_status"), "PASSED"),
    )
    passed = 0
    for label, path, value in mutations:
        payload = deepcopy(result.payload)
        target: Any = payload
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            HomogeneousPositiveConformalStealthClock(payload=payload).verify()
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
    result = HomogeneousPositiveConformalStealthClock.build()
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
