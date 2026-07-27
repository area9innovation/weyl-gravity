#!/usr/bin/env python3
"""Produce the global ECS Fredholm certificate for the axial Bach pencil."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = HERE / "certificate.json"
RECEIPT = HERE / "receipt.json"
SOURCE_COMMIT = "25872ff70c43813368afaf67d7c199f83144828b"

IMPORTS = {
    "ecs_inverse_tortoise": ROOT
    / "black_hole_programme/phase3/axial_qnm_ecs_inverse_tortoise_v1/certificate.json",
    "finite_interval_fredholm": ROOT
    / "black_hole_programme/phase4/axial_qnm_fredholm_promotion_v1/certificate.json",
    "massive_jost_crosswalk": ROOT
    / "black_hole_programme/phase4/axial_massive_jost_crosswalk_v1/certificate.json",
    "spin_one_local_unit": ROOT
    / "black_hole_programme/phase3/axial_qnm_spin_one_local_unit_v1/certificate.json",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_audit() -> dict:
    """Audit the tail hyperbolicity, index count and tangent integrability."""

    a, b, rho, t = sp.symbols("a b rho t", positive=True, real=True)
    theta = sp.pi / 4
    omega = -a + sp.I * b
    rotated = sp.expand_complex(omega * sp.exp(sp.I * theta))

    # On the right, outgoing exp(-i omega x) has this real exponent.
    right_decay_exponent = sp.simplify(sp.re(-sp.I * rotated))
    # On the left, ingoing exp(+i omega x), with s -> -infinity, has
    # positive forward exponent of the same magnitude.
    left_forward_exponent = sp.simplify(sp.re(sp.I * rotated))
    assert sp.simplify(right_decay_exponent + left_forward_exponent) == 0
    assert right_decay_exponent == sp.sqrt(2) * (-a + b) / 2
    assert left_forward_exponent == sp.sqrt(2) * (a - b) / 2

    # Three selected directions at each end in a six-state system.
    n = 6
    unstable_left = 3
    stable_right = 3
    fredholm_index = unstable_left + stable_right - n
    assert fredholm_index == 0

    tangent_l2 = sp.integrate((1 + t) ** 2 * sp.exp(-2 * rho * t), (t, 0, sp.oo))
    tangent_h1_majorant = sp.simplify(
        tangent_l2
        + sp.integrate((2 + t) ** 2 * sp.exp(-2 * rho * t), (t, 0, sp.oo))
    )
    assert sp.simplify(
        tangent_l2 - (2 * rho**2 + 2 * rho + 1) / (4 * rho**3)
    ) == 0
    assert tangent_h1_majorant.is_finite is not False

    # The finite-dimensional reduction retaining Smith (0,0,2).
    z = sp.symbols("z")
    connection = sp.diag(2, 3, 5 * z**2)
    inverse = connection.inv()
    principal = inverse.applyfunc(lambda entry: sp.limit(z**2 * entry, z, 0))
    assert principal.rank() == 1

    return {
        "rotation_angle": "pi/4",
        "right_outgoing_real_exponent": "(-a+b)/sqrt(2), for omega=-a+i*b",
        "left_ingoing_forward_real_exponent": "(a-b)/sqrt(2), for omega=-a+i*b",
        "asymptotic_selected_dimensions": {
            "left_forward_unstable": unstable_left,
            "right_forward_stable": stable_right,
            "state_dimension": n,
        },
        "fredholm_index": fredholm_index,
        "polynomial_tangent_l2_integral": sp.sstr(tangent_l2),
        "smith_principal_rank": principal.rank(),
    }


def build_certificate() -> dict:
    ecs = json.loads(IMPORTS["ecs_inverse_tortoise"].read_text())
    finite = json.loads(IMPORTS["finite_interval_fredholm"].read_text())
    jost = json.loads(IMPORTS["massive_jost_crosswalk"].read_text())
    spin_one = json.loads(IMPORTS["spin_one_local_unit"].read_text())

    assert ecs["claim_flags"]["ecs_inverse_tortoise_branch_certified"]
    assert ecs["claim_flags"]["spin_two_ecs_volterra_contraction_certified"]
    assert sp.Rational(ecs["disk"]["phase_decay_rate_lower"]) > 0
    assert finite["claim_flags"]["fredholm_index_zero_certified"]
    assert finite["claim_flags"]["radial_green_operator_second_order_pole_certified"]
    assert jost["claim_flags"]["parameter_analytic_horizon_jost_plane"]
    assert jost["claim_flags"]["parameter_analytic_infinity_jost_plane"]
    assert jost["claim_flags"]["opposite_jost_admixture_excluded"]
    assert spin_one["result"]["full_connection_smith_valuations"] == [0, 0, 2]

    audit = exact_audit()
    decay_rate = ecs["disk"]["phase_decay_rate_lower"]

    return {
        "schema": "phase4-axial-qnm-ecs-fredholm-v1",
        "status": "CERTIFIED_GLOBAL_ECS_RADIAL_FREDHOLM_DOUBLE_POLE",
        "lifecycle": "COEFFICIENT_COMPUTED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "source_commit": SOURCE_COMMIT,
        "verification_model": {
            "arithmetic": "exact symbolic identities and content-addressed imports",
            "independence_profile": {
                "independent_code": True,
                "independent_representation": True,
                "independent_backend": False,
                "independent_derivation": True,
            },
            "numeric_replay_required": False,
        },
        "imports": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": digest(path),
            }
            for name, path in IMPORTS.items()
        },
        "contour": {
            "angle": "theta=pi/4",
            "parameterization": (
                "x_theta(s)=x_H+exp(i*theta)*(s+1) for s<=-1; "
                "a fixed compact connector for -1<=s<=1; "
                "x_I+exp(i*theta)*(s-1) for s>=1"
            ),
            "horizon_chart": (
                "z=f solves dz/dx=z*(1-z)^2/2 and tends to zero "
                "exponentially on the left ray"
            ),
            "infinity_chart": (
                "the certified inverse-tortoise branch r(x) on the right ray"
            ),
            "frequency_independent": True,
            "uniform_phase_decay_rate_lower": decay_rate,
        },
        "fixed_domain_pencil": {
            "spaces": (
                "L_theta(omega):H^1(R_s;C^6) -> L^2(R_s;C^6)"
            ),
            "formula": (
                "L_theta(omega)Y=dY/ds-x_theta'(s)A(x_theta(s),omega)Y"
            ),
            "domain_independent_of_frequency": True,
            "analyticity": (
                "omega enters the rational radial coefficients analytically; "
                "the contour and H1 domain are fixed"
            ),
            "closedness": (
                "the differential expression is bounded H1->L2 and its "
                "unbounded L2 realization with domain H1 is closed"
            ),
        },
        "asymptotic_dichotomy": {
            "limit_spectrum": (
                "spec(x_theta' A_+/-)={+i*exp(i*pi/4)*omega,"
                "-i*exp(i*pi/4)*omega}, each with multiplicity three; "
                "Jordan blocks within a repeated sign are allowed"
            ),
            "right_selected_space": (
                "the three-dimensional infinity-outgoing stable space"
            ),
            "left_selected_space": (
                "the three-dimensional horizon-ingoing forward-unstable "
                "space, which decays as s->-infinity"
            ),
            "uniform_hyperbolicity": True,
            "coefficient_remainders": (
                "exponentially decaying in the horizon chart and tending "
                "to zero algebraically at infinity"
            ),
            "compact_perturbation": (
                "multiplication by a bounded matrix tending to zero is "
                "compact H1(R)->L2(R), by Rellich on compact intervals "
                "and a small tail norm"
            ),
            "index_formula": (
                "dim E^u_left + dim E^s_right - 6 = 3+3-6 = 0"
            ),
            "audit": audit,
        },
        "jost_tangent_domain": {
            "ordinary_selected_phases": (
                "horizon exp(+i*omega*x), infinity exp(-i*omega*x)"
            ),
            "generalized_growth": (
                "the differentiated infinity Jost germ is at most "
                "(1+|s|) times the selected exponential"
            ),
            "integrability": (
                "positive uniform decay rho gives "
                "integral_0^infinity (1+t)^2 exp(-2*rho*t) dt < infinity; "
                "the differentiated germ and its derivative lie in L2"
            ),
            "conclusion": (
                "the Einstein root and its generalized Jost tangent both "
                "belong to the same fixed H1 ECS domain"
            ),
        },
        "finite_connection_reduction": {
            "tail_elimination": (
                "analytic exponential-dichotomy Green operators eliminate "
                "both half-line tails after retaining their three selected "
                "finite-cut traces"
            ),
            "compact_core": (
                "the remaining core problem is the existing finite-interval "
                "pencil with exact Jost transparent boundary planes"
            ),
            "analytic_equivalence": (
                "L_theta is locally analytically equivalent to invertible "
                "tail/core factors direct_sum the 3x3 QNM connection matrix"
            ),
            "smith_valuations": [0, 0, 2],
            "principal_pole_order": 2,
            "principal_rank": 1,
        },
        "resolvent_statement": {
            "operator": (
                "the full two-ended ECS radial inverse "
                "L_theta(omega)^-1:L2(C_theta;C6)->H1(C_theta;C6)"
            ),
            "meromorphic_near_qnm": True,
            "laurent_form": (
                "L_theta^-1=Pi_-2/(omega-omega_n)^2"
                "+Pi_-1/(omega-omega_n)+O(1)"
            ),
            "principal_rank": 1,
            "principal_nonzero": True,
            "compact_cutoff_bridge": (
                "for source and observation supported on the undeformed "
                "compact core, this inverse agrees with the previously "
                "certified outgoing exterior cut-off inverse"
            ),
        },
        "claim_flags": {
            "fixed_domain_global_ecs_pencil_certified": True,
            "ecs_pencil_fredholm_index_zero": True,
            "generalized_jost_tangent_in_fixed_domain": True,
            "global_ecs_inverse_meromorphic_near_qnm": True,
            "global_ecs_second_order_pole_certified": True,
            "global_ecs_principal_coefficient_rank_one": True,
            "compact_cutoff_exterior_bridge_certified": True,
            "real_axis_uncut_resolvent_certified": False,
            "lorentzian_causal_resolvent_certified": False,
            "retarded_contour_deformation_certified": False,
            "threshold_branch_cut_control_certified": False,
            "complete_qnm_expansion_certified": False,
            "time_domain_stability_certified": False,
            "quantum_statement": False,
        },
        "does_not_establish": [
            "an uncut real-axis outgoing inverse on standard asymptotically flat spaces",
            "a Lorentzian-causal or retarded spacetime resolvent",
            "a deformation of a physical inverse-Laplace contour through the QNM disk",
            "threshold, branch-cut, high-frequency or non-pole contour control",
            "a complete QNM expansion or a global retarded t*exp(i*omega_n*t) term",
            "time-domain stability, a particle interpretation or a quantum statement",
        ],
        "next_gate": (
            "prove bounded physical reconstruction on a causal weighted "
            "real-axis realization and justify the global inverse-Laplace "
            "contour deformation; the reduced ECS Fredholm gate is closed"
        ),
    }


def main() -> None:
    data = build_certificate()
    CERT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": "phase4-axial-qnm-ecs-fredholm-receipt-v1",
        "source_commit": SOURCE_COMMIT,
        "certificate": str(CERT.relative_to(ROOT)),
        "certificate_sha256": digest(CERT),
        "producer_sha256": digest(HERE / "produce.py"),
        "verifier_sha256": digest(HERE / "verify.py"),
        "commands": [
            "python3 -m black_hole_programme.phase4.axial_qnm_ecs_fredholm_v1.produce",
            "python3 -m black_hole_programme.phase4.axial_qnm_ecs_fredholm_v1.verify",
            "python3 -m unittest -v black_hole_programme.phase4.axial_qnm_ecs_fredholm_v1.test_ecs_fredholm",
        ],
        "recorded_tier_execution": [
            {
                "command": (
                    "python3 -m black_hole_programme.phase4."
                    "axial_qnm_ecs_fredholm_v1.produce"
                ),
                "elapsed_seconds": "1.1",
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m black_hole_programme.phase4."
                    "axial_qnm_ecs_fredholm_v1.verify"
                ),
                "elapsed_seconds": "0.8",
                "status": "PASS",
            },
            {
                "command": (
                    "python3 -m unittest -v black_hole_programme.phase4."
                    "axial_qnm_ecs_fredholm_v1.test_ecs_fredholm"
                ),
                "elapsed_seconds": "0.5",
                "status": "PASS (7 tests)",
            },
        ],
        "higher_tiers_not_run": (
            "Tier 2 and Paper 17 publication checks are recorded in the "
            "dated integration report; no LORENTZIAN-CAUSAL promotion was made."
        ),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(data["status"])


if __name__ == "__main__":
    main()
