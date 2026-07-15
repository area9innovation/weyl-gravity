#!/usr/bin/env python3
"""Audit the local BV/health extension of the neutral conformal clock pair.

The homogeneous neutral clock is exact, but its opposite-sign scalar must not
be declared harmless merely because the scalar gauge-incidence matrix is
invertible.  This module performs the next local calculation.

Writing the raw pair as

    T_1 = rho cos(theta),  T_2 = rho sin(theta),

the common Weyl rescaling acts on rho while theta is Weyl invariant.  In the
rho=constant Weyl frame, the reduced matter action contains a derivative term
whose target coefficient is -rho^2 cos(2 theta).  For every neutral winding
orbit with nonzero Wronskian, the invariant norm

    N = T_1^2 - T_2^2

is a nonzero sinusoid and crosses zero four times per compact D period.  The
remaining ratio mode therefore alternates kinetic sign and becomes degenerate
at the crossings.  Temporal diffeomorphism gauge can move this mode into the
metric (unitary gauge), but cannot turn the coupled physical degree into a BV
contractible auxiliary pair.

The conclusion is scoped: the homogeneous reference clock remains valid, but
this minimal (+,-) model does not provide a globally regular positive local
matter completion.  A complete all-row BV operator is not claimed here.
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
    / "NEUTRAL_CLOCK_BV_HEALTH_AUDIT.json"
)
REPORT_PATH = (
    ROOT
    / "d_quotient_classical"
    / "reports"
    / "neutral-clock-bv-health-audit.md"
)
SCHEMA_PATH = (
    ROOT
    / "d_quotient_classical"
    / "schema"
    / "neutral-clock-bv-health-audit-v1.schema.json"
)
INPUT_CLOCK_COMMIT = "a558ecf6eae7259ebd9dfef048602b83f9ccf9e4"
INPUT_CLOCK_SHA256 = "c68921ec717de842052350238cfb3cb65f950a05197dd213691b5b4bb1b14e03"


@dataclass(frozen=True)
class NeutralClockBVHealthAudit:
    """Exact polar-reduction and neutral-orbit health certificate."""

    payload: dict[str, Any]

    @classmethod
    def build(cls) -> "NeutralClockBVHealthAudit":
        rho, theta = sp.symbols("rho theta", positive=True, real=True)
        d_rho, d_theta = sp.symbols("d_rho d_theta", real=True)
        t, alpha, beta, amplitude = sp.symbols(
            "t alpha beta amplitude", real=True
        )

        t1 = rho * sp.cos(theta)
        t2 = rho * sp.sin(theta)
        dt1 = sp.diff(t1, rho) * d_rho + sp.diff(t1, theta) * d_theta
        dt2 = sp.diff(t2, rho) * d_rho + sp.diff(t2, theta) * d_theta
        target_line = sp.expand_trig(sp.expand(dt1**2 - dt2**2))
        expected_line = (
            sp.cos(2 * theta) * d_rho**2
            - 2 * rho * sp.sin(2 * theta) * d_rho * d_theta
            - rho**2 * sp.cos(2 * theta) * d_theta**2
        )
        if sp.trigsimp(target_line - expected_line) != 0:
            raise AssertionError("indefinite target metric polar form drifted")

        fixed_radius_line = sp.expand(expected_line.subs(d_rho, 0))
        if fixed_radius_line != -rho**2 * sp.cos(2 * theta) * d_theta**2:
            raise AssertionError("Weyl-reduced angle kinetic coefficient drifted")
        invariant_norm = sp.trigsimp(t1**2 - t2**2)
        if sp.trigsimp(invariant_norm - rho**2 * sp.cos(2 * theta)) != 0:
            raise AssertionError("internal norm drifted")

        # General equal-energy homogeneous pair.  Nonzero W is precisely the
        # clock transversality condition.
        phase_1 = t + alpha
        phase_2 = t + beta
        x1 = amplitude * sp.cos(phase_1)
        p1 = -amplitude * sp.sin(phase_1)
        x2 = amplitude * sp.cos(phase_2)
        p2 = -amplitude * sp.sin(phase_2)
        wronskian = sp.trigsimp(x1 * p2 - x2 * p1)
        norm_orbit = sp.trigsimp(x1**2 - x2**2)
        expected_w = amplitude**2 * sp.sin(alpha - beta)
        expected_norm = -expected_w * sp.sin(2 * t + alpha + beta)
        if sp.trigsimp(wronskian - expected_w) != 0:
            raise AssertionError("general neutral Wronskian drifted")
        if sp.trigsimp(norm_orbit - expected_norm) != 0:
            raise AssertionError("neutral internal norm identity drifted")

        # The four representatives in one 2*pi period solve
        # 2t+alpha+beta=k*pi.  Consecutive crossings are pi/2 apart.
        zero_representatives = [
            "-(alpha+beta)/2",
            "pi/2-(alpha+beta)/2",
            "pi-(alpha+beta)/2",
            "3*pi/2-(alpha+beta)/2",
        ]

        # Linearized scalar incidence.  Its inverse is algebraic on W!=0,
        # but this only changes gauge coordinates; it does not erase the
        # derivative ratio field from the reduced action.
        incidence = sp.Matrix([[p1, -x1], [p2, -x2]])
        if sp.trigsimp(incidence.det() - wronskian) != 0:
            raise AssertionError("clock incidence determinant drifted")

        payload: dict[str, Any] = {
            "schema": "pure-weyl-neutral-clock-bv-health-audit-v1",
            "result_id": "NEUTRAL_CLOCK_BV_HEALTH_AUDIT",
            "setting_id": "compact_neutral_clock_pair",
            "generator_id": "D_compact",
            "phase_space_id": "compact_neutral_clock_pair_local_extension",
            "claim_status": "CERTIFIED_SCOPED_OBSTRUCTION",
            "scientific_verdict": None,
            "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
            "inputs": {
                "homogeneous_clock_certificate": "d_quotient_classical/certificates/NEUTRAL_CONFORMAL_CLOCK_PAIR.json",
                "commit": INPUT_CLOCK_COMMIT,
                "sha256": INPUT_CLOCK_SHA256,
            },
            "local_field_reduction": {
                "polar_fields": ["T_1=rho*cos(theta)", "T_2=rho*sin(theta)"],
                "weyl_action": "rho -> exp(-sigma_W)*rho; theta -> theta",
                "invariant_metric": "g_hat=rho^2*g",
                "target_line_element": "cos(2 theta) d(rho)^2-2 rho sin(2 theta)d(rho)d(theta)-rho^2 cos(2 theta)d(theta)^2",
                "rho_constant_frame": "d(rho)=0",
                "remaining_angle_target_coefficient": "G_theta=-rho^2*cos(2 theta)",
                "remaining_angle_has_derivative_action": True,
                "ratio_mode_weyl_contractible": False,
            },
            "brst_incidence": {
                "scalar_rule": "s T_A=c^mu partial_mu T_A-c_W T_A",
                "polar_rules": [
                    "s theta=c^mu partial_mu theta",
                    "s log(rho)=c^mu partial_mu log(rho)-c_W",
                ],
                "background_temporal_weyl_matrix": [["dot(T_1)", "-T_1"], ["dot(T_2)", "-T_2"]],
                "determinant": "W",
                "field_ghost_incidence_invertible_on_W_nonzero": True,
                "inverse_type": "pointwise multiplication by 1/W",
                "inverse_support_local": True,
                "interpretation": "scalar gauge coordinates can be eliminated locally, but their dynamics transfers to the metric/constraint rows",
            },
            "neutral_orbit_obstruction": {
                "general_equal_energy_pair": [
                    "T_1=A*cos(t+alpha)",
                    "T_2=A*cos(t+beta)",
                ],
                "wronskian": "W=A^2*sin(alpha-beta)",
                "internal_norm": "N=T_1^2-T_2^2=-W*sin(2t+alpha+beta)",
                "clock_condition": "W!=0",
                "norm_zero_count_per_2pi": 4,
                "norm_zero_representatives": zero_representatives,
                "crossing_spacing": "pi/2",
                "reduced_kinetic_sign": "sign(G_theta)=sign(-N)",
                "kinetic_sign_definite_on_full_clock_orbit": False,
                "kinetic_degeneracy_crossed_by_every_regular_clock_orbit": True,
                "global_regular_einstein_or_scalar_frame_exists": False,
            },
            "degree_of_freedom_audit": {
                "gauge_group_changed_by_adding_pair": False,
                "new_second_order_scalar_fields": 2,
                "scalar_coordinates_can_fix_temporal_diff_and_weyl": True,
                "physical_effect": "unitary gauge transfers the scalar dynamics into metric and constraint rows rather than deleting it",
                "opposite_sign_reference_sector_entirely_contractible": False,
                "healthy_positive_local_completion_on_this_orbit": False,
            },
            "gate_result": {
                "gate": "FULL_NEUTRAL_CLOCK_PAIR_BV_COMPLETION",
                "status": "OBSTRUCTED_AS_GLOBALLY_REGULAR_HEALTHY_CLOCK",
                "homogeneous_clock_theorem_retained": True,
                "next_gate": "POSITIVE_ENERGY_NONCONFORMALLY_FLAT_OR_STEALTH_CLOCK",
            },
            "flags": {
                "polar_reduction_exact": True,
                "scalar_incidence_support_local": True,
                "homogeneous_clock_still_valid": True,
                "ratio_derivative_mode_survives_weyl_reduction": True,
                "neutral_orbit_crosses_internal_null_cone": True,
                "kinetic_sign_global_positive": False,
                "opposite_sign_sector_fully_contractible": False,
                "full_all_row_bv_operator_constructed": False,
            },
            "not_established": [
                "the complete coupled all-row BV differential and antifield transformation",
                "a causal Green complex across the kinetic-degeneracy hypersurfaces",
                "a healthy positive-energy matter interpretation",
                "a no-go theorem for backreacted non-conformally-flat or stealth clocks",
                "an interacting or quantum verdict",
            ],
            "claim_boundary": "The audit proves that the minimal opposite-sign neutral pair cannot be promoted from a working homogeneous reference clock to a globally regular positive local clock merely by Diff x Weyl contraction. It does not obstruct other clock actions, backreacted non-conformally-flat backgrounds, stealth matter, or larger BV extensions.",
        }
        result = cls(payload=payload)
        result.verify()
        return result

    def verify(self) -> None:
        p = self.payload
        required = {
            "schema", "result_id", "setting_id", "generator_id",
            "phase_space_id", "claim_status", "scientific_verdict",
            "dependency_tags", "inputs", "local_field_reduction",
            "brst_incidence", "neutral_orbit_obstruction",
            "degree_of_freedom_audit", "gate_result", "flags",
            "not_established", "claim_boundary",
        }
        if set(p) != required:
            raise AssertionError("neutral-clock health key set drifted")
        if p["claim_status"] != "CERTIFIED_SCOPED_OBSTRUCTION":
            raise AssertionError("neutral-clock health obstruction was promoted")
        if p["scientific_verdict"] is not None:
            raise AssertionError("local health audit received an unrelated D verdict")
        flags = p["flags"]
        for key in {
            "polar_reduction_exact",
            "scalar_incidence_support_local",
            "homogeneous_clock_still_valid",
            "ratio_derivative_mode_survives_weyl_reduction",
            "neutral_orbit_crosses_internal_null_cone",
        }:
            if flags.get(key) is not True:
                raise AssertionError(f"proved health-audit flag dropped: {key}")
        for key in {
            "kinetic_sign_global_positive",
            "opposite_sign_sector_fully_contractible",
            "full_all_row_bv_operator_constructed",
        }:
            if flags.get(key) is not False:
                raise AssertionError(f"open/false health-audit flag promoted: {key}")
        if p["gate_result"]["status"] != "OBSTRUCTED_AS_GLOBALLY_REGULAR_HEALTHY_CLOCK":
            raise AssertionError("wrong neutral-clock health gate")
        if not p["gate_result"]["homogeneous_clock_theorem_retained"]:
            raise AssertionError("health audit erased the valid homogeneous theorem")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return r"""# Neutral clock-pair BV health audit

## Outcome

The neutral two-field model remains an exact homogeneous reference clock, but
it does **not** extend to a globally regular positive local matter clock by
simply declaring the opposite-sign direction gauge.

Write

\[
T_1=\rho\cos\theta,\qquad T_2=\rho\sin\theta.
\]

Weyl rescaling acts on \(\rho\), while \(\theta\) is Weyl invariant.  The
indefinite target line element is

\[
dT_1^2-dT_2^2
=\cos(2\theta)d\rho^2
-2\rho\sin(2\theta)d\rho,d\theta
-\rho^2\cos(2\theta)d\theta^2.
\]

After choosing the regular \(\rho=\text{constant}\) Weyl frame, the ratio
field retains a derivative action with target coefficient

\[
G_\theta=-\rho^2\cos(2\theta).
\]

It is therefore not a Weyl-contractible auxiliary field.

## Why every neutral winding clock crosses the problem

For the general equal-energy homogeneous pair,

\[
T_1=A\cos(t+\alpha),\qquad T_2=A\cos(t+\beta),
\]

one has

\[
W=A^2\sin(\alpha-\beta),
\qquad
N:=T_1^2-T_2^2=-W\sin(2t+\alpha+\beta).
\]

The clock condition is \(W\ne0\).  It forces \(N\) to cross zero four times
per compact \(D\) period.  Since \(G_\theta=-N\) in the fixed-radius frame,
the remaining local kinetic direction changes sign and becomes degenerate at
every crossing.  No regular neutral winding orbit stays inside one healthy
internal cone.

## What the gauge incidence does—and does not—prove

The scalar block of the linearized temporal-diffeomorphism/Weyl incidence has
determinant \(W\).  Its inverse is pointwise multiplication by \(1/W\), so
the scalar coordinates are excellent local gauge-fixing variables.  This is
why the homogeneous clock works.

But using those coordinates as unitary gauge transfers their derivative
dynamics into the metric and constraint rows.  It does not delete the coupled
physical degree of freedom.  Adding the scalar pair introduces no new gauge
symmetry, and the Weyl-reduced action still contains the ratio derivative
term explicitly.

Thus

```text
FULL_NEUTRAL_CLOCK_PAIR_BV_COMPLETION
    = OBSTRUCTED_AS_GLOBALLY_REGULAR_HEALTHY_CLOCK
```

while

```text
NEUTRAL_CONFORMAL_CLOCK_PAIR
    = VALID_HOMOGENEOUS_REFERENCE_CLOCK
```

remains unchanged.

## Next admissible model

The next search should avoid cancellation by a freely propagating opposite-
sign scalar.  The gate is
`POSITIVE_ENERGY_NONCONFORMALLY_FLAT_OR_STEALTH_CLOCK`: either construct a
positive-energy clock on a genuinely Bach-sourced non-conformally-flat
background, or find a stress-free conformal/stealth clock whose local kinetic
sector remains regular.

This audit is not a no-go theorem for those alternatives or for larger
contractible reference-matter extensions.
"""


def _write(result: NeutralClockBVHealthAudit) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check(result: NeutralClockBVHealthAudit) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError(f"stale certificate: {CERTIFICATE_PATH}")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError(f"stale report: {REPORT_PATH}")
    if not SCHEMA_PATH.is_file():
        raise AssertionError(f"missing schema: {SCHEMA_PATH}")


def _guards(result: NeutralClockBVHealthAudit) -> None:
    mutations = (
        ("positive kinetic", ("flags", "kinetic_sign_global_positive"), True),
        ("contractible ghost", ("flags", "opposite_sign_sector_fully_contractible"), True),
        ("all-row overclaim", ("flags", "full_all_row_bv_operator_constructed"), True),
        ("erase incidence", ("flags", "scalar_incidence_support_local"), False),
        ("erase homogeneous theorem", ("gate_result", "homogeneous_clock_theorem_retained"), False),
        ("premature D verdict", ("scientific_verdict",), "D_GAUGE"),
    )
    passed = 0
    for label, path, value in mutations:
        payload = deepcopy(result.payload)
        target: Any = payload
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            NeutralClockBVHealthAudit(payload=payload).verify()
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
    result = NeutralClockBVHealthAudit.build()
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
